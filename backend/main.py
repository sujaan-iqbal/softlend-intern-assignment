from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import math
import sys
import os

# Allow importing the rule_engine from the parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import get_db, engine
from models import Base, Customer, CreditGap, Offer
from models import ImpactEnum, GapStatusEnum, OfferStatusEnum
import schemas
import engine_bridge

app = FastAPI(title="Softlend Backend API")

# Helper for consistent error JSON responses
def raise_error(status_code: int, detail: str, code: str):
    raise HTTPException(
        status_code=status_code,
        detail={"error": detail, "code": code}
    )

# Create DB tables on startup
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


# ==========================
# 1. CREATE CUSTOMER
# ==========================
@app.post("/customers", response_model=schemas.Customer_Response, status_code=201)
def create_customer(customer: schemas.Create_Customer, db: Session = Depends(get_db)):
    existing = db.query(Customer).filter(Customer.mobile == customer.mobile).first()
    if existing:
        raise_error(409, "Mobile already exists", "MOBILE_DUPLICATE")
    
    new_customer = Customer(
        name=customer.name,
        mobile=customer.mobile,
        pan=customer.pan
    )
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


# ==========================
# 2. UPDATE CREDIT SCORE
# ==========================
@app.post("/customers/{customer_id}/credit-score", status_code=200)
def update_credit_score(customer_id: int, score_data: schemas.Update_Credit_Score, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise_error(404, "Customer not found", "CUSTOMER_NOT_FOUND")
    
    # Update score
    customer.cibil_score = score_data.cibil_score
    customer.score_fetched_at = datetime.now()
    db.commit()
    
    # Dummy credit report for the rule engine
    dummy_report = {
        "customer_id": f"C00{customer_id}",
        "credit_utilisation_pct": 87,
        "missed_payments_12m": 2,
        "written_off_accounts": 0,
        "credit_age_months": 14,
        "hard_enquiries_6m": 2
    }
    
    # Call the rule engine via bridge
    gap_result = engine_bridge.analyze_gaps(dummy_report)
    
    # Save detected gaps into DB
    for gap in gap_result['gaps']:
        impact_map = {
            'high': ImpactEnum.HIGH,
            'medium': ImpactEnum.MEDIUM,
            'low': ImpactEnum.LOW
        }
        impact_enum = impact_map.get(gap['impact'].lower(), ImpactEnum.MEDIUM)
        
        new_gap = CreditGap(
            customer_id=customer_id,
            factor=gap['id'],
            current_value=str(dummy_report.get(gap['id'], "N/A")),
            ideal_value="<30% / 0",
            impact=impact_enum,
            estimated_score_gain=gap['estimated_score_gain'],
            action_description=gap['action'],
            status=GapStatusEnum.OPEN
        )
        db.add(new_gap)
    
    db.commit()
    
    return {
        "customer_id": customer_id,
        "cibil_score": score_data.cibil_score,
        "score_fetched_at": customer.score_fetched_at
    }


# ==========================
# 3. MANUAL ADD CREDIT GAP
# ==========================
@app.post("/customers/{customer_id}/credit-gaps", status_code=201)
def add_credit_gap(customer_id: int, gap_data: schemas.Create_Credit_Gap, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise_error(404, "Customer not found", "CUSTOMER_NOT_FOUND")
    
    impact_map = {
        'high': ImpactEnum.HIGH,
        'medium': ImpactEnum.MEDIUM,
        'low': ImpactEnum.LOW
    }
    impact_enum = impact_map.get(gap_data.impact.lower(), ImpactEnum.MEDIUM)
    
    new_gap = CreditGap(
        customer_id=customer_id,
        factor=gap_data.factor,
        current_value=gap_data.current_value,
        ideal_value=gap_data.ideal_value,
        impact=impact_enum,
        estimated_score_gain=gap_data.estimated_score_gain,
        action_description=gap_data.action_description,
        status=GapStatusEnum.OPEN
    )
    db.add(new_gap)
    db.commit()
    db.refresh(new_gap)
    
    return {
        "id": new_gap.id,
        "factor": new_gap.factor,
        "status": new_gap.status.value
    }


# ==========================
# 4. RESOLVE A GAP
# ==========================
@app.patch("/credit-gaps/{gap_id}/resolve", status_code=200)
def resolve_credit_gap(gap_id: int, db: Session = Depends(get_db)):
    gap = db.query(CreditGap).filter(CreditGap.id == gap_id).first()
    if not gap:
        raise_error(404, "Gap not found", "GAP_NOT_FOUND")
    
    gap.status = GapStatusEnum.RESOLVED
    gap.resolved_at = datetime.now()
    db.commit()
    db.refresh(gap)
    
    return {
        "id": gap.id,
        "factor": gap.factor,
        "status": gap.status.value,
        "resolved_at": gap.resolved_at
    }


# ==========================
# 5. GET FULL CREDIT PROFILE
# ==========================
@app.get("/customers/{customer_id}/credit-profile", status_code=200)
def get_credit_profile(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise_error(404, "Customer not found", "CUSTOMER_NOT_FOUND")
    
    gaps = db.query(CreditGap).filter(CreditGap.customer_id == customer_id).all()
    
    total_open_gain = 0
    open_gaps_count = 0
    resolved_gaps_count = 0
    gap_list = []
    
    for gap in gaps:
        gap_list.append({
            "id": gap.id,
            "factor": gap.factor,
            "impact": gap.impact.value,
            "estimated_score_gain": gap.estimated_score_gain,
            "action_description": gap.action_description,
            "status": gap.status.value
        })
        
        if gap.status == GapStatusEnum.OPEN:
            open_gaps_count += 1
            total_open_gain += gap.estimated_score_gain
        else:
            resolved_gaps_count += 1
    
    potential_score = (customer.cibil_score or 0) + total_open_gain
    
    return {
        "customer_id": customer.id,
        "name": customer.name,
        "cibil_score": customer.cibil_score,
        "score_fetched_at": customer.score_fetched_at,
        "potential_score": potential_score,
        "gaps": gap_list,
        "open_gaps": open_gaps_count,
        "resolved_gaps": resolved_gaps_count
    }


# ==========================
# 6. CREATE OFFER
# ==========================
@app.post("/customers/{customer_id}/offers", status_code=201)
def create_offer(customer_id: int, offer: schemas.Offer_Create, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise_error(404, "Customer not found", "CUSTOMER_NOT_FOUND")
    
    new_offer = Offer(
        customer_id=customer_id,
        lender=offer.lender,
        amount=offer.amount,
        interest_rate=offer.interest_rate,
        tenure_months=offer.tenure_months,
        min_score_required=offer.min_score_required,
        status=OfferStatusEnum.PENDING
    )
    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)
    return new_offer


# ==========================
# 7. LIST OFFERS
# ==========================
@app.get("/customers/{customer_id}/offers", response_model=List[schemas.Offer_Response_Data])
def list_offers(customer_id: int, locked: Optional[str] = Query(None), db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise_error(404, "Customer not found", "CUSTOMER_NOT_FOUND")
    
    offers = db.query(Offer).filter(Offer.customer_id == customer_id).all()
    response = []
    
    for offer in offers:
        is_locked = customer.cibil_score is None or customer.cibil_score < offer.min_score_required
        
        if locked is not None:
            if locked.lower() == "true" and not is_locked:
                continue
            if locked.lower() == "false" and is_locked:
                continue
        
        score_gap = max(0, offer.min_score_required - (customer.cibil_score or 0))
        
        response.append({
            "id": offer.id,
            "lender": offer.lender,
            "amount": float(offer.amount),
            "interest_rate": float(offer.interest_rate),
            "tenure_months": offer.tenure_months,
            "min_score_required": offer.min_score_required,
            "status": offer.status.value,
            "locked": is_locked,
            "score_gap": 0 if not is_locked else score_gap
        })
    
    return response


# ==========================
# 8. UPDATE OFFER STATUS
# ==========================
@app.patch("/offers/{offer_id}/status", status_code=200)
def update_offer_status(offer_id: int, status_data: dict, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise_error(404, "Offer not found", "OFFER_NOT_FOUND")
    
    new_status_str = status_data.get("status")
    if new_status_str not in ["pending", "active", "disbursed"]:
        raise_error(422, "Invalid status transition", "INVALID_STATUS")
    
    # Validate transition path
    if offer.status == OfferStatusEnum.PENDING and new_status_str != "active":
        raise_error(422, "Pending offers can only transition to active", "INVALID_STATUS_TRANSITION")
    if offer.status == OfferStatusEnum.ACTIVE and new_status_str != "disbursed":
        raise_error(422, "Active offers can only transition to disbursed", "INVALID_STATUS_TRANSITION")
    
    # Check if offer is still locked before activation
    if new_status_str == "active":
        customer = db.query(Customer).filter(Customer.id == offer.customer_id).first()
        if customer.cibil_score is None or customer.cibil_score < offer.min_score_required:
            raise_error(
                422,
                f"Offer is locked. Customer score {customer.cibil_score} is below required {offer.min_score_required}.",
                "OFFER_LOCKED"
            )
    
    status_map = {
        "pending": OfferStatusEnum.PENDING,
        "active": OfferStatusEnum.ACTIVE,
        "disbursed": OfferStatusEnum.DISBURSED
    }
    offer.status = status_map[new_status_str]
    db.commit()
    
    return {"id": offer.id, "status": offer.status.value}


# ==========================
# 9. CALCULATE EMI
# ==========================
@app.get("/offers/{offer_id}/emi")
def calculate_emi(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(Offer).filter(Offer.id == offer_id).first()
    if not offer:
        raise_error(404, "Offer not found", "OFFER_NOT_FOUND")
    
    P = float(offer.amount)
    r = float(offer.interest_rate) / 12 / 100
    n = offer.tenure_months
    
    if r == 0:
        emi = P / n
    else:
        emi = (P * r * (1 + r) ** n) / ((1 + r) ** n - 1)
    
    return {
        "offer_id": offer_id,
        "principal": P,
        "interest_rate": float(offer.interest_rate),
        "tenure_months": n,
        "monthly_emi": round(emi, 2)
    }


# ==========================
# 10. IMPROVEMENT SUMMARY
# ==========================
@app.get("/customers/{customer_id}/improvement-summary")
def improvement_summary(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise_error(404, "Customer not found", "CUSTOMER_NOT_FOUND")
    
    gaps = db.query(CreditGap).filter(CreditGap.customer_id == customer_id).all()
    
    total_resolved_gain = 0
    total_potential_gain = 0
    
    for gap in gaps:
        if gap.status == GapStatusEnum.RESOLVED:
            total_resolved_gain += gap.estimated_score_gain
        else:
            total_potential_gain += gap.estimated_score_gain
    
    return {
        "customer_id": customer_id,
        "resolved_gaps_count": sum(1 for g in gaps if g.status == GapStatusEnum.RESOLVED),
        "total_score_points_recovered": total_resolved_gain,
        "remaining_potential_score_gain": total_potential_gain
    }
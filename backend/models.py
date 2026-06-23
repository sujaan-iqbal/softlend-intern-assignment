from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, DECIMAL
from sqlalchemy.sql import func
import enum
from database import Base

# ==========================================
# Enums (Lowercase to match SQLite constraints)
# ==========================================

class ImpactEnum(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class GapStatusEnum(str, enum.Enum):
    OPEN = "open"
    RESOLVED = "resolved"

class OfferStatusEnum(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DISBURSED = "disbursed"

# ==========================================
# Customer Table
# ==========================================

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    mobile = Column(String, unique=True, nullable=False)
    pan = Column(String, nullable=False)
    cibil_score = Column(Integer, nullable=True)
    score_fetched_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

# ==========================================
# Credit Gaps Table
# ==========================================

class CreditGap(Base):
    __tablename__ = "credit_gaps"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    factor = Column(String, nullable=False)
    current_value = Column(String, nullable=False)
    ideal_value = Column(String, nullable=False)
    
    # Force Enum to store lowercase strings in SQLite
    impact = Column(
        Enum(
            ImpactEnum,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        nullable=False
    )
    
    estimated_score_gain = Column(Integer, nullable=False)
    action_description = Column(String, nullable=False)
    
    status = Column(
        Enum(
            GapStatusEnum,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=GapStatusEnum.OPEN
    )
    
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

# ==========================================
# Offers Table
# ==========================================

class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    lender = Column(String, nullable=False)
    amount = Column(DECIMAL(12, 2), nullable=False)
    interest_rate = Column(DECIMAL(5, 2), nullable=False)
    tenure_months = Column(Integer, nullable=False)
    min_score_required = Column(Integer, default=650)
    
    status = Column(
        Enum(
            OfferStatusEnum,
            values_callable=lambda obj: [e.value for e in obj]
        ),
        default=OfferStatusEnum.PENDING
    )
    
    created_at = Column(DateTime, server_default=func.now())
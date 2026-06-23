from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import re

class CustomerCreate(BaseModel):
    name: str
    mobile: str
    pan: str

    @validator('mobile')
    def validate_mobile(cls, v):
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Mobile must be exactly 10 digits')
        return v

    @validator('pan')
    def validate_pan(cls, v):
        if not re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$', v):
            raise ValueError('PAN format invalid')
        return v

class CustomerResponse(BaseModel):
    id: int
    name: str
    mobile: str

class CreditScoreUpdate(BaseModel):
    cibil_score: int

class CreditGapCreate(BaseModel):
    factor: str
    current_value: str
    ideal_value: str
    impact: str
    estimated_score_gain: int
    action_description: str

class OfferCreate(BaseModel):
    lender: str
    amount: float
    interest_rate: float
    tenure_months: int
    min_score_required: int = 650

class OfferResponse(BaseModel):
    id: int
    lender: str
    amount: float
    interest_rate: float
    tenure_months: int
    min_score_required: int
    locked: bool
    score_gap: int
    status: str

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..services.payment_service import PaymentService
from ..database import get_db
from ..models import Payment
from ..models.payment import PaymentStatus, PaymentMethod
from pydantic import BaseModel

router = APIRouter()

class PaymentIntentRequest(BaseModel):
    job_id: int
    amount: float
    user_id: str

class PaymentWebhookRequest(BaseModel):
    event: str
    payload: dict

@router.post("/intent")
async def create_payment_intent(
    request: PaymentIntentRequest,
    db: Session = Depends(get_db)
):
    """Create a payment intent"""
    service = PaymentService(db)
    return service.create_payment_intent(
        request.job_id,
        request.amount,
        request.user_id
    )

@router.post("/webhook")
async def process_payment_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Process Stripe webhook events"""
    payload = await request.json()
    service = PaymentService(db)
    service.process_payment_webhook(payload)
    return {"status": "success"}

@router.get("/{payment_id}")
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Get payment details"""
    service = PaymentService(db)
    return service.get_payment(payment_id)

@router.get("/user/{user_id}")
async def get_payments_for_user(
    user_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get user's payment history"""
    service = PaymentService(db)
    return service.get_payments_for_user(user_id, limit, offset)

@router.post("/{payment_id}/refund")
async def refund_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    """Refund a payment"""
    service = PaymentService(db)
    return service.refund_payment(payment_id)

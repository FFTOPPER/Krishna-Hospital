from fastapi import APIRouter
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Patient
from schemas import SignupData, LoginData
from auth import hash_password, verify_password

router = APIRouter()


# =====================================================
# Patient Signup
# =====================================================

@router.post("/signup")
def signup(data: SignupData):

    db: Session = SessionLocal()

    try:

        existing = db.query(Patient).filter(
            Patient.email_or_phone == data.email_or_phone
        ).first()

        if existing:
            return {
                "success": False,
                "message": "Account already exists."
            }

        patient = Patient(
            email_or_phone=data.email_or_phone,
            password=hash_password(data.password)
        )

        db.add(patient)
        db.commit()
        db.refresh(patient)

        return {
            "success": True,
            "message": "Account created successfully."
        }

    finally:
        db.close()


# =====================================================
# Patient Login
# =====================================================

@router.post("/login")
def login(data: LoginData):

    db: Session = SessionLocal()

    try:

        patient = db.query(Patient).filter(
            Patient.email_or_phone == data.email_or_phone
        ).first()

        if not patient:
            return {
                "success": False,
                "message": "Incorrect credentials."
            }

        if not verify_password(
            data.password,
            patient.password
        ):
            return {
                "success": False,
                "message": "Incorrect credentials."
            }

        return {
            "success": True,
            "message": "Login successful.",
            "patient_id": patient.id,
            "email_or_phone": patient.email_or_phone
        }

    finally:
        db.close()
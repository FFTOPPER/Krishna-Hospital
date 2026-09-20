from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import date

from database import SessionLocal
from models import Patient, PatientRegistration

router = APIRouter()


class RegistrationData(BaseModel):

    email_or_phone: str
    phone_number: str

    consultation_date: date
    referred_by: str
    child_name: str
    dob: date
    age: str
    gender: str
    parent_name: str
    parent_education_occupation: str
    address: str
    consultation_complaints: str


@router.post("/patient-registration")
def patient_registration(data: RegistrationData):

    db: Session = SessionLocal()

    try:
        # Check if patient exists
        patient = db.query(Patient).filter(
            Patient.email_or_phone == data.email_or_phone
        ).first()

        if not patient:
            return {
                "success": False,
                "message": "Patient not found."
            }

        # Prevent duplicate registration
        existing_registration = db.query(PatientRegistration).filter(
            PatientRegistration.patient_id == patient.id
        ).first()

        if existing_registration:
            return {
                "success": False,
                "message": "You have already submitted the registration form."
            }

        # Create new registration
        registration = PatientRegistration(

            patient_id=patient.id,

            phone_number=data.phone_number,

            consultation_date=data.consultation_date,

            referred_by=data.referred_by,

            child_name=data.child_name,

            dob=data.dob,

            age=data.age,

            gender=data.gender,

            parent_name=data.parent_name,

            parent_education_occupation=data.parent_education_occupation,

            address=data.address,

            consultation_complaints=data.consultation_complaints

        )

        db.add(registration)
        db.commit()
        db.refresh(registration)

        return {
            "success": True,
            "message": "Registration submitted successfully."
        }

    finally:
        db.close()
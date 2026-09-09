from fastapi import APIRouter
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Patient
from schemas import ProfilePhotoData,RemovePhotoData,ChangePasswordData
from auth import hash_password

router=APIRouter()

@router.get("/patient-profile/{email_or_phone}")
def patient_profile(email_or_phone: str):

    db: Session = SessionLocal()

    patient = db.query(Patient).filter(
        Patient.email_or_phone == email_or_phone
    ).first()

    if not patient:
        db.close()
        return {
            "success": False,
            "message": "Patient not found."
        }

    data = {
        "id": patient.id,
        "email_or_phone": patient.email_or_phone,
        "profile_picture": patient.profile_picture
    }

    db.close()

    return {
        "success": True,
        "patient": data
    }

@router.post("/upload-profile-photo")
def upload_photo(data: ProfilePhotoData):

    db: Session = SessionLocal()

    patient = db.query(Patient).filter(
        Patient.email_or_phone == data.email_or_phone
    ).first()

    if not patient:
        db.close()
        return {
            "success": False,
            "message": "Patient not found."
        }

    patient.profile_picture = data.profile_picture

    db.commit()
    db.close()

    return {
        "success": True,
        "message": "Profile picture updated."
    }

@router.post("/remove-profile-photo")
def remove_photo(data: RemovePhotoData):

    db: Session = SessionLocal()

    patient = db.query(Patient).filter(
        Patient.email_or_phone == data.email_or_phone
    ).first()

    if not patient:
        db.close()
        return {
            "success": False,
            "message": "Patient not found."
        }

    patient.profile_picture = None

    db.commit()
    db.close()

    return {
        "success": True,
        "message": "Photo removed."
    }

@router.post("/change-password")
def change_password(data: ChangePasswordData):

    db: Session = SessionLocal()

    patient = db.query(Patient).filter(
        Patient.email_or_phone == data.email_or_phone
    ).first()

    if not patient:
        db.close()
        return {
            "success": False,
            "message": "Patient not found."
        }

    patient.password = hash_password(data.new_password)

    db.commit()
    db.close()

    return {
        "success": True,
        "message": "Password updated successfully."
    }
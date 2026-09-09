from fastapi import APIRouter
from sqlalchemy.orm import Session

from database import SessionLocal
from models import (
    AppointmentUpdate,
    Patient,
    PatientRegistration,
    FollowUpStatus
)

router = APIRouter()


# =====================================================
# My Activities
# =====================================================

@router.get("/my-activities/{email_or_phone}")
def my_activities(email_or_phone: str):

    db: Session = SessionLocal()

    try:

        patient = db.query(Patient).filter(
            Patient.email_or_phone == email_or_phone
        ).first()

        if not patient:
            return {
                "success": False,
                "message": "Patient not found."
            }

        registrations = (
            db.query(PatientRegistration)
            .filter(PatientRegistration.patient_id == patient.id)
            .order_by(PatientRegistration.consultation_date.desc())
            .all()
        )

        data = []

        for registration in registrations:

            data.append({

                "id": registration.id,

                "date": str(registration.consultation_date),

                "child_name": registration.child_name,

                "referred_by": registration.referred_by,

                "age": registration.age,

                "gender": registration.gender,

                "status": registration.status

            })

        return {

            "success": True,

            "activities": data

        }

    finally:
        db.close()


# =====================================================
# Registration Status
# =====================================================

@router.get("/patient/registration-status/{patient_id}")
def patient_registration_status(patient_id: int):

    db: Session = SessionLocal()

    try:

        registrations = (
            db.query(PatientRegistration)
            .filter(PatientRegistration.patient_id == patient_id)
            .order_by(PatientRegistration.id.desc())
            .all()
        )

        result = []

        for registration in registrations:

            appointment = (
                db.query(AppointmentUpdate)
                .filter(
                    AppointmentUpdate.registration_id == registration.id
                )
                .first()
            )

            result.append({

                "registration_id": registration.id,

                "child_name": registration.child_name,

                "consultation_date": str(registration.consultation_date),

                "parent_name": registration.parent_name,

                "status": registration.status,

                "visit_date":
                    str(appointment.visit_date)
                    if appointment else None,

                "visit_time":
                    appointment.visit_time.strftime("%H:%M")
                    if appointment else None,

                "rejection_reason":
                    registration.rejection_reason

            })

        return {

            "success": True,

            "registrations": result

        }

    finally:
        db.close()


# =====================================================
# Patient Follow-up Schedule
# =====================================================

@router.get("/patient/followups/{email_or_phone}")
def patient_followups(email_or_phone: str):

    db: Session = SessionLocal()

    try:

        patient = db.query(Patient).filter(
            Patient.email_or_phone == email_or_phone
        ).first()

        if not patient:
            return {
                "success": False,
                "message": "Patient not found."
            }

        registrations = (
            db.query(PatientRegistration)
            .filter(PatientRegistration.patient_id == patient.id)
            .all()
        )

        meetings = []

        for registration in registrations:

            followup = (
                db.query(FollowUpStatus)
                .filter(
                    FollowUpStatus.registration_id == registration.id,
                    FollowUpStatus.attendance_status == "Attended"
                )
                .order_by(FollowUpStatus.id.desc())
                .first()
            )

            if followup and followup.followup_date:

                meetings.append({

                    "registration_id": registration.id,

                    "patient_id": patient.id,

                    "child_name": registration.child_name,

                    "parent_name": registration.parent_name,

                    "doctor_name": followup.doctor_name,

                    "followup_date": str(followup.followup_date),

                    "followup_time":
                        followup.followup_time.strftime("%H:%M")
                        if followup.followup_time else None,

                    "attendance_status": followup.attendance_status

                })

        meetings.sort(key=lambda x: x["followup_date"])

        return {

            "success": True,

            "meetings": meetings

        }

    finally:
        db.close()
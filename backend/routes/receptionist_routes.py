from sqlalchemy.orm import Session
from fastapi import APIRouter
import os
from dotenv import load_dotenv

from database import SessionLocal

from models import (
    FollowUpStatus,
    Receptionist,
    PatientRegistration,
    AppointmentUpdate,
    PatientNotification
)

from schemas import (
    FollowUpData,
    ReceptionistChangePasswordData,
    ReceptionistSignupData,
    ReceptionistLoginData,
    ConfirmRegistrationData,
    RejectRegistrationData
)

from auth import hash_password, verify_password

# Load .env variables
load_dotenv()

router = APIRouter()

# Secret key from .env
SECRET_RECEPTION_KEY = os.getenv("SECRET_RECEPTION_KEY")


# =====================================================
# Receptionist Signup
# =====================================================

@router.post("/receptionist/signup")
def receptionist_signup(data: ReceptionistSignupData):

    db: Session = SessionLocal()

    try:

        if data.secret_key != SECRET_RECEPTION_KEY:
            return {
                "success": False,
                "message": "Invalid registration key."
            }

        existing = db.query(Receptionist).filter(
            Receptionist.email == data.email
        ).first()

        if existing:
            return {
                "success": False,
                "message": "Receptionist already exists."
            }

        receptionist = Receptionist(
            name=data.name,
            email=data.email,
            password=hash_password(data.password)
        )

        db.add(receptionist)
        db.commit()
        db.refresh(receptionist)

        return {
            "success": True,
            "message": "Receptionist account created."
        }

    finally:
        db.close()


# =====================================================
# Receptionist Login
# =====================================================

@router.post("/receptionist/login")
def receptionist_login(data: ReceptionistLoginData):

    db: Session = SessionLocal()

    try:

        receptionist = db.query(Receptionist).filter(
            Receptionist.email == data.email
        ).first()

        if not receptionist:
            return {
                "success": False,
                "message": "Invalid credentials."
            }

        if not verify_password(data.password, receptionist.password):
            return {
                "success": False,
                "message": "Invalid credentials."
            }

        return {
            "success": True,
            "receptionist_id": receptionist.id,
            "name": receptionist.name
        }

    finally:
        db.close()


# =====================================================
# Receptionist Profile
# =====================================================

@router.get("/receptionist/profile/{receptionist_id}")
def receptionist_profile(receptionist_id: int):

    db: Session = SessionLocal()

    try:

        receptionist = db.query(Receptionist).filter(
            Receptionist.id == receptionist_id
        ).first()

        if not receptionist:
            return {
                "success": False,
                "message": "Receptionist not found."
            }

        return {
            "success": True,
            "receptionist": {
                "id": receptionist.id,
                "name": receptionist.name,
                "email": receptionist.email
            }
        }

    finally:
        db.close()


# =====================================================
# Change Password
# =====================================================

@router.post("/receptionist/change-password")
def receptionist_change_password(data: ReceptionistChangePasswordData):

    db: Session = SessionLocal()

    try:

        receptionist = db.query(Receptionist).filter(
            Receptionist.id == data.receptionist_id
        ).first()

        if not receptionist:
            return {
                "success": False,
                "message": "Receptionist not found."
            }

        receptionist.password = hash_password(data.new_password)

        db.commit()

        return {
            "success": True,
            "message": "Password updated successfully."
        }

    finally:
        db.close()


# =====================================================
# Patient Queue
# =====================================================

@router.get("/receptionist/queue")
def receptionist_queue():

    db: Session = SessionLocal()

    try:

        registrations = (
            db.query(PatientRegistration)
            .order_by(PatientRegistration.id.desc())
            .all()
        )

        queue = []

        for registration in registrations:

            latest_appointment = (
                db.query(AppointmentUpdate)
                .filter(
                    AppointmentUpdate.registration_id == registration.id
                )
                .order_by(AppointmentUpdate.updated_at.desc())
                .first()
            )

            queue.append({

                "id": registration.id,
                "patient_id": registration.patient_id,
                "consultation_date": str(registration.consultation_date),
                "referred_by": registration.referred_by,
                "child_name": registration.child_name,
                "age": registration.age,
                "gender": registration.gender,
                "parent_name": registration.parent_name,
                "parent_education_occupation": registration.parent_education_occupation,
                "address": registration.address,
                "consultation_complaints": registration.consultation_complaints,
                "status": registration.status,
                "rejection_reason": registration.rejection_reason,

                "visit_date": (
                    str(latest_appointment.visit_date)
                    if latest_appointment else None
                ),

                "visit_time": (
                    latest_appointment.visit_time.strftime("%H:%M")
                    if latest_appointment else None
                ),

                "doctor_name": (
                    latest_appointment.doctor_name
                    if latest_appointment else None
                )

            })

        return {
            "success": True,
            "registrations": queue
        }

    finally:
        db.close()


# =====================================================
# Confirm Registration
# =====================================================

@router.post("/receptionist/confirm-registration")
def confirm_registration(data: ConfirmRegistrationData):

    db: Session = SessionLocal()

    try:

        registration = db.query(PatientRegistration).filter(
            PatientRegistration.id == data.registration_id
        ).first()

        if not registration:
            return {
                "success": False,
                "message": "Registration not found."
            }

        receptionist = db.query(Receptionist).filter(
            Receptionist.id == data.receptionist_id
        ).first()

        if not receptionist:
            return {
                "success": False,
                "message": "Receptionist not found."
            }

        # Update registration status
        registration.status = "Confirmed"
        registration.rejection_reason = None

        # Create or update appointment
        appointment = db.query(AppointmentUpdate).filter(
            AppointmentUpdate.registration_id == data.registration_id
        ).first()

        if appointment:

            appointment.visit_date = data.visit_date
            appointment.visit_time = data.visit_time
            appointment.doctor_name = data.doctor_name
            appointment.receptionist_id = data.receptionist_id

        else:

            appointment = AppointmentUpdate(
                registration_id=data.registration_id,
                receptionist_id=data.receptionist_id,
                visit_date=data.visit_date,
                visit_time=data.visit_time,
                doctor_name=data.doctor_name
            )

            db.add(appointment)

        # Send notification to patient
        notification = PatientNotification(
            patient_id=registration.patient_id,
            title="Appointment Confirmed",
            message=(
                f"Your consultation has been confirmed with "
                f"{data.doctor_name}. Visit on {data.visit_date} "
                f"at {data.visit_time.strftime('%H:%M')}."
            )
        )

        db.add(notification)

        db.commit()

        return {
            "success": True,
            "message": "Appointment confirmed successfully."
        }

    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": str(e)
        }

    finally:
        db.close()
# =====================================================
# Reject Registration
# =====================================================

@router.post("/receptionist/reject-registration")
def reject_registration(data: RejectRegistrationData):

    db: Session = SessionLocal()

    try:

        registration = db.query(PatientRegistration).filter(
            PatientRegistration.id == data.registration_id
        ).first()

        if not registration:
            return {
                "success": False,
                "message": "Registration not found."
            }

        registration.status = "Rejected"
        registration.rejection_reason = data.rejection_reason

        appointment = db.query(AppointmentUpdate).filter(
            AppointmentUpdate.registration_id == data.registration_id
        ).first()

        if appointment:
            db.delete(appointment)

        notification = PatientNotification(
            patient_id=registration.patient_id,
            title="Registration Rejected",
            message=f"Reason: {data.rejection_reason}"
        )

        db.add(notification)

        db.commit()

        return {
            "success": True,
            "message": "Registration rejected successfully."
        }

    finally:
        db.close()


# =====================================================
# Confirmed Registrations
# =====================================================

@router.get("/receptionist/confirmed")
def confirmed_registrations():

    db: Session = SessionLocal()

    try:

        registrations = (
            db.query(PatientRegistration)
            .filter(PatientRegistration.status == "Confirmed")
            .order_by(PatientRegistration.id.desc())
            .all()
        )

        confirmed = []

        for registration in registrations:

            appointment = (
                db.query(AppointmentUpdate)
                .filter(
                    AppointmentUpdate.registration_id == registration.id
                )
                .order_by(AppointmentUpdate.updated_at.desc())
                .first()
            )

            confirmed.append({

                "id": registration.id,
                "patient_id": registration.patient_id,
                "child_name": registration.child_name,
                "parent_name": registration.parent_name,
                "age": registration.age,
                "gender": registration.gender,
                "referred_by": registration.referred_by,
                "address": registration.address,
                "consultation_complaints": registration.consultation_complaints,
                "visit_date": str(appointment.visit_date) if appointment else None,
                "visit_time": appointment.visit_time.strftime("%H:%M") if appointment else None
                "doctor_name": appointment.doctor_name if appointment else None
            })

        return {
            "success": True,
            "registrations": confirmed
        }

    finally:
        db.close()


# =====================================================
# Follow-up List
# =====================================================

@router.get("/receptionist/followup-list")
def followup_list():

    db = SessionLocal()

    try:

        registrations = db.query(PatientRegistration).filter(
            PatientRegistration.status == "Confirmed"
        ).order_by(PatientRegistration.id.desc()).all()

        data = []

        for registration in registrations:

            appointment = db.query(AppointmentUpdate).filter(
                AppointmentUpdate.registration_id == registration.id
            ).order_by(
                AppointmentUpdate.updated_at.desc()
            ).first()

            followup = db.query(FollowUpStatus).filter(
                FollowUpStatus.registration_id == registration.id
            ).first()

            data.append({

                "registration_id": registration.id,
                "patient_id": registration.patient_id,
                "child_name": registration.child_name,
                "parent_name": registration.parent_name,
                "visit_date": str(appointment.visit_date) if appointment else None,
                "visit_time": appointment.visit_time.strftime("%H:%M") if appointment else None,
                "attendance_status": followup.attendance_status if followup else None,
                "followup_date": str(followup.followup_date) if followup and followup.followup_date else None,
                "followup_time": followup.followup_time.strftime("%H:%M") if followup and followup.followup_time else None,
                "doctor_name": followup.doctor_name if followup else None

            })

        return {
            "success": True,
            "patients": data
        }

    finally:
        db.close()


# =====================================================
# Save Follow-up
# =====================================================

@router.post("/receptionist/followup")
def save_followup(data: FollowUpData):

    db = SessionLocal()

    try:

        existing = db.query(FollowUpStatus).filter(
            FollowUpStatus.registration_id == data.registration_id
        ).first()

        if existing:

            existing.attendance_status = data.attendance_status
            existing.followup_date = data.followup_date
            existing.followup_time = data.followup_time
            existing.doctor_name = data.doctor_name
            existing.receptionist_id = data.receptionist_id

        else:

            db.add(
                FollowUpStatus(
                    registration_id=data.registration_id,
                    receptionist_id=data.receptionist_id,
                    attendance_status=data.attendance_status,
                    followup_date=data.followup_date,
                    followup_time=data.followup_time,
                    doctor_name=data.doctor_name
                )
            )

        db.commit()

        return {
            "success": True,
            "message": "Follow-up saved successfully."
        }

    finally:
        db.close()
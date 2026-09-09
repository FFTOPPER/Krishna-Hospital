import os
from datetime import date

from fastapi import APIRouter
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import SessionLocal
from models import (
    Doctor,
    PatientRegistration,
    AppointmentUpdate
)
from schemas import (
    DoctorSignupData,
    DoctorLoginData,
    DoctorChangePasswordData
)
from auth import hash_password, verify_password

# Load .env variables
load_dotenv()

router = APIRouter()

# Secret key from .env
SECRET_DOCTOR_KEY = os.getenv("SECRET_DOCTOR_KEY")


# =====================================================
# Doctor Signup
# =====================================================

@router.post("/doctor/signup")
def doctor_signup(data: DoctorSignupData):

    db: Session = SessionLocal()

    try:

        if data.secret_key != SECRET_DOCTOR_KEY:
            return {
                "success": False,
                "message": "Invalid doctor registration key."
            }

        existing = db.query(Doctor).filter(
            Doctor.email == data.email
        ).first()

        if existing:
            return {
                "success": False,
                "message": "Doctor account already exists."
            }

        doctor = Doctor(
            name=data.name,
            email=data.email,
            password=hash_password(data.password)
        )

        db.add(doctor)
        db.commit()
        db.refresh(doctor)

        return {
            "success": True,
            "message": "Doctor account created successfully."
        }

    finally:
        db.close()


# =====================================================
# Doctor Login
# =====================================================

@router.post("/doctor/login")
def doctor_login(data: DoctorLoginData):

    db: Session = SessionLocal()

    try:

        doctor = db.query(Doctor).filter(
            Doctor.email == data.email
        ).first()

        if not doctor:
            return {
                "success": False,
                "message": "Invalid credentials."
            }

        if not verify_password(data.password, doctor.password):
            return {
                "success": False,
                "message": "Invalid credentials."
            }

        return {
            "success": True,
            "doctor_id": doctor.id,
            "name": doctor.name,
            "email": doctor.email
        }

    finally:
        db.close()


# =====================================================
# Doctor Profile
# =====================================================

@router.get("/doctor/profile/{doctor_id}")
def doctor_profile(doctor_id: int):

    db: Session = SessionLocal()

    try:

        doctor = db.query(Doctor).filter(
            Doctor.id == doctor_id
        ).first()

        if not doctor:
            return {
                "success": False,
                "message": "Doctor not found."
            }

        return {
            "success": True,
            "doctor": {
                "id": doctor.id,
                "name": doctor.name,
                "email": doctor.email
            }
        }

    finally:
        db.close()


# =====================================================
# Change Password
# =====================================================

@router.post("/doctor/change-password")
def doctor_change_password(data: DoctorChangePasswordData):

    db: Session = SessionLocal()

    try:

        doctor = db.query(Doctor).filter(
            Doctor.id == data.doctor_id
        ).first()

        if not doctor:
            return {
                "success": False,
                "message": "Doctor not found."
            }

        doctor.password = hash_password(data.new_password)

        db.commit()

        return {
            "success": True,
            "message": "Password updated successfully."
        }

    finally:
        db.close()


# =====================================================
# Helper Function
# =====================================================

def build_patient_data(registration, appointment):

    return {

        "registration_id": registration.id,

        "patient_id": registration.patient_id,

        "consultation_date": str(registration.consultation_date),

        "referred_by": registration.referred_by,

        "child_name": registration.child_name,

        "dob": str(registration.dob),

        "age": registration.age,

        "gender": registration.gender,

        "parent_name": registration.parent_name,

        "parent_education_occupation":
            registration.parent_education_occupation,

        "address": registration.address,

        "consultation_complaints":
            registration.consultation_complaints,

        "visit_date": str(appointment.visit_date),

        "visit_time":
            appointment.visit_time.strftime("%H:%M")
            if appointment.visit_time else None

    }


# =====================================================
# Doctor Dashboard (Today + Upcoming)
# =====================================================

@router.get("/doctor/patients")
def doctor_patients():

    db: Session = SessionLocal()

    try:

        today = date.today()

        appointments = (
            db.query(AppointmentUpdate)
            .join(
                PatientRegistration,
                AppointmentUpdate.registration_id == PatientRegistration.id
            )
            .filter(PatientRegistration.status == "Confirmed")
            .order_by(AppointmentUpdate.visit_date.asc())
            .all()
        )

        print("TODAY:", today)
        print("Appointments Found:", len(appointments))

        today_patients = []
        upcoming_patients = []

        for appointment in appointments:

            print(
                "Registration:",
                appointment.registration_id,
                "Date:",
                appointment.visit_date,
                "Time:",
                appointment.visit_time
            )

            registration = db.query(PatientRegistration).filter(
                PatientRegistration.id == appointment.registration_id
            ).first()

            if not registration:
                continue

            patient = build_patient_data(registration, appointment)

            if appointment.visit_date == today:
                today_patients.append(patient)

            elif appointment.visit_date > today:
                upcoming_patients.append(patient)

        return {
            "success": True,
            "today": today_patients,
            "upcoming": upcoming_patients
        }

    finally:
        db.close()


# =====================================================
# Today's Patients Only
# =====================================================

@router.get("/doctor/today")
def today_patients():

    db: Session = SessionLocal()

    try:

        today = date.today()

        appointments = (
            db.query(AppointmentUpdate)
            .filter(AppointmentUpdate.visit_date == today)
            .all()
        )

        patients = []

        for appointment in appointments:

            registration = db.query(PatientRegistration).filter(
                PatientRegistration.id == appointment.registration_id,
                PatientRegistration.status == "Confirmed"
            ).first()

            if registration:
                patients.append(
                    build_patient_data(registration, appointment)
                )

        return {
            "success": True,
            "patients": patients
        }

    finally:
        db.close()


# =====================================================
# Upcoming Patients Only
# =====================================================

@router.get("/doctor/upcoming")
def upcoming_patients():

    db: Session = SessionLocal()

    try:

        today = date.today()

        appointments = (
            db.query(AppointmentUpdate)
            .filter(AppointmentUpdate.visit_date > today)
            .order_by(AppointmentUpdate.visit_date.asc())
            .all()
        )

        patients = []

        for appointment in appointments:

            registration = db.query(PatientRegistration).filter(
                PatientRegistration.id == appointment.registration_id,
                PatientRegistration.status == "Confirmed"
            ).first()

            if registration:
                patients.append(
                    build_patient_data(registration, appointment)
                )

        return {
            "success": True,
            "patients": patients
        }

    finally:
        db.close()
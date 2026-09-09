from datetime import date, time
from pydantic import BaseModel


# =====================================================
# Patient Authentication Schemas
# =====================================================

class SignupData(BaseModel):
    email_or_phone: str
    password: str


class LoginData(BaseModel):
    email_or_phone: str
    password: str


# =====================================================
# Patient Registration Schema
# =====================================================

class PatientRegistrationData(BaseModel):
    email_or_phone: str

    consultation_date: date

    referred_by: str | None = None

    child_name: str

    dob: date

    age: str

    gender: str

    parent_name: str

    parent_education_occupation: str | None = None

    address: str | None = None

    consultation_complaints: str | None = None


# =====================================================
# Patient Profile Schemas
# =====================================================

class ProfilePhotoData(BaseModel):
    email_or_phone: str
    profile_picture: str


class RemovePhotoData(BaseModel):
    email_or_phone: str


class ChangePasswordData(BaseModel):
    email_or_phone: str
    new_password: str


# =====================================================
# Patient Notification Schemas
# =====================================================

class MarkNotificationReadData(BaseModel):
    patient_id: int


# =====================================================
# Receptionist Authentication Schemas
# =====================================================

class ReceptionistSignupData(BaseModel):
    name: str
    email: str
    password: str
    secret_key: str


class ReceptionistLoginData(BaseModel):
    email: str
    password: str


# =====================================================
# Receptionist Queue Management Schemas
# =====================================================

class ConfirmRegistrationData(BaseModel):
    registration_id: int
    receptionist_id: int
    visit_date: date
    visit_time: time


class RejectRegistrationData(BaseModel):
    registration_id: int
    rejection_reason: str


# =====================================================
# Receptionist Profile Management Schemas
# =====================================================

class ReceptionistChangePasswordData(BaseModel):
    receptionist_id: int
    new_password: str


# =====================================================
# Follow-Up Management Schemas
# =====================================================

class FollowUpData(BaseModel):
    registration_id: int
    receptionist_id: int

    # Expected values:
    # "Attended" or "Missed"
    attendance_status: str

    followup_date: date | None = None
    followup_time: time | None = None
    doctor_name: str | None = None

# =====================================================
# Doctor Authentication Schemas
# =====================================================

class DoctorSignupData(BaseModel):

    name: str

    email: str

    password: str

    secret_key: str


class DoctorLoginData(BaseModel):

    email: str

    password: str


class DoctorChangePasswordData(BaseModel):

    doctor_id: int

    new_password: str       
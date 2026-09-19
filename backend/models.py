from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship

from database import Base

from sqlalchemy import Column, Integer, String

# =========================
# Patient Table
# =========================
class Patient(Base):

    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    email_or_phone = Column(String, unique=True, index=True, nullable=False)

    password = Column(String, nullable=False)

    # Permanent profile picture (Base64 string)
    profile_picture = Column(Text, nullable=True)

    # One patient can have multiple registrations
    registrations = relationship(
        "PatientRegistration",
        back_populates="patient",
        cascade="all, delete-orphan"
    )


# =========================
# Patient Registration Table
# =========================
class PatientRegistration(Base):

    __tablename__ = "patient_registrations"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False
    )

    consultation_date = Column(Date, nullable=False)

    referred_by = Column(String)

    child_name = Column(String, nullable=False)

    dob = Column(Date, nullable=False)

    age = Column(String)

    gender = Column(String)

    parent_name = Column(String, nullable=False)

    parent_education_occupation = Column(String)

    address = Column(Text)

    consultation_complaints = Column(Text)

    # Workflow status
    status = Column(String, default="Pending", nullable=False)

    # Reason for rejection (if rejected)
    rejection_reason = Column(Text, nullable=True)

    # Relationship to Patient
    patient = relationship(
        "Patient",
        back_populates="registrations"
    )

    # Appointment history
    appointments = relationship(
        "AppointmentUpdate",
        back_populates="registration",
        cascade="all, delete-orphan"
    )


# =========================
# Receptionist Table
# =========================
class Receptionist(Base):

    __tablename__ = "receptionists"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)

    password = Column(String, nullable=False)

    # Appointments confirmed by this receptionist
    appointments = relationship(
        "AppointmentUpdate",
        back_populates="receptionist"
    )


# =========================
# Appointment Updates Table
# =========================
class AppointmentUpdate(Base):

    __tablename__ = "appointment_updates"

    id = Column(Integer, primary_key=True, index=True)

    registration_id = Column(
        Integer,
        ForeignKey("patient_registrations.id", ondelete="CASCADE"),
        nullable=False
    )

    receptionist_id = Column(
        Integer,
        ForeignKey("receptionists.id", ondelete="CASCADE"),
        nullable=False
    )

    visit_date = Column(Date, nullable=False)

    visit_time = Column(Time, nullable=False)

    doctor_name = Column(String(100), nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow)

    registration = relationship(
        "PatientRegistration",
        back_populates="appointments"
    )

    receptionist = relationship(
        "Receptionist",
        back_populates="appointments"
    )


# =========================
# Patient Notifications Table
# =========================
class PatientNotification(Base):

    __tablename__ = "patient_notifications"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(
        Integer,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(String, nullable=False)

    message = Column(Text, nullable=False)

    is_read = Column(String, default="No")

    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient")

# =========================
# Follow-up Status Table
# =========================

class FollowUpStatus(Base):

    __tablename__="followup_status"

    id=Column(Integer,primary_key=True,index=True)

    registration_id=Column(
        Integer,
        ForeignKey("patient_registrations.id",ondelete="CASCADE"),
        nullable=False
    )

    receptionist_id=Column(
        Integer,
        ForeignKey("receptionists.id",ondelete="CASCADE"),
        nullable=False
    )

    attendance_status=Column(String,nullable=False)

    followup_date=Column(Date,nullable=True)

    followup_time=Column(Time,nullable=True)

    doctor_name=Column(String,nullable=True)

    updated_at=Column(DateTime,default=datetime.utcnow)

    registration=relationship("PatientRegistration")

    receptionist=relationship("Receptionist")



# =====================================================
# Doctor Model
# =====================================================

class Doctor(Base):

    __tablename__ = "doctor"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    email = Column(String, unique=True, nullable=False, index=True)

    password = Column(String, nullable=False)
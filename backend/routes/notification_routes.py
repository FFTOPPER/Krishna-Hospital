from fastapi import APIRouter
from sqlalchemy.orm import Session

from database import SessionLocal
from models import PatientNotification
from schemas import MarkNotificationReadData

router=APIRouter()

@router.get("/notifications/{patient_id}")
def get_notifications(patient_id:int):

    db:Session=SessionLocal()

    try:

        notifications=db.query(PatientNotification).filter(
            PatientNotification.patient_id==patient_id
        ).order_by(PatientNotification.created_at.desc()).all()

        return{

            "success":True,

            "notifications":[

                {

                    "id":n.id,
                    "title":n.title,
                    "message":n.message,
                    "is_read":n.is_read

                }

                for n in notifications

            ]

        }

    finally:
        db.close()


@router.post("/notifications/mark-read")
def mark_read(data:MarkNotificationReadData):

    db:Session=SessionLocal()

    try:

        db.query(PatientNotification).filter(
            PatientNotification.patient_id==data.patient_id,
            PatientNotification.is_read=="No"
        ).update({"is_read":"Yes"})

        db.commit()

        return{

            "success":True

        }

    finally:
        db.close()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

from routes.auth_routes import router as auth_router
from routes.registration_routes import router as registration_router
from routes.activity_routes import router as activity_router
from routes.profile_routes import router as profile_router
from routes.receptionist_routes import router as receptionist_router
from routes.notification_routes import router as notification_router
from routes.doctor_routes import router as doctor_router

app = FastAPI(
    title="Krishna Hospital Digital Patient Registration API",
    version="1.0.0"
)

# =====================================================
# CORS Configuration
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # Local Development
        "http://127.0.0.1:5500",
        "http://localhost:5500",

        # Production (Replace with your actual Vercel URLs)
        "https://krishna-patient.vercel.app",
        "https://krishna-reception.vercel.app",
        "https://krishna-doctor.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# =====================================================
# Create Database Tables
# =====================================================

Base.metadata.create_all(bind=engine)

# =====================================================
# Patient Routes
# =====================================================

app.include_router(auth_router)
app.include_router(registration_router)
app.include_router(activity_router)
app.include_router(profile_router)

# =====================================================
# Receptionist Routes
# =====================================================

app.include_router(receptionist_router)
app.include_router(notification_router)

# =====================================================
# Doctor Routes
# =====================================================

app.include_router(doctor_router)

# =====================================================
# Health Check
# =====================================================

@app.get("/")
def home():
    return {
        "success": True,
        "message": "Krishna Hospital Digital Patient Registration API Running"
    }
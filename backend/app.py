from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import fault_solutions, payments, notifications, reviews, dashboard
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="OBD2 Platform API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(fault_solutions.router, prefix="/api")
app.include_router(payments.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(reviews.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to OBD2 Platform API"}

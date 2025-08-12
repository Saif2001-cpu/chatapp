from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import db, client  # <-- Import db and client
from controllers.auth import router as auth_router
from controllers.contacts import router as contacts_router

app = FastAPI()

# CORS middleware to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection check
try:
    client.admin.command("ping")
    print("You are successfully connected to MongoDB!")
except Exception as e:
    print("MongoDB connection error:", e)


@app.get("/")
async def root():
    return {"message": "Welcome to the Chat App API"}


app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(contacts_router, prefix="/api/contacts", tags=["Contacts"])

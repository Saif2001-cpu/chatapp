from fastapi import APIRouter, HTTPException, Depends
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
import jwt
import os
import dotenv

# Load env variables
dotenv.load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
JWT_ALGORITHM = "HS256"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB setup
password = os.getenv("password")
uri = f"mongodb+srv://maif95689:{password}@cluster0.y0ibdhj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri)
db = client["chatapp"]
users_collection = db["users"]

# FastAPI Router
router = APIRouter()


# Custom ObjectId validator for Pydantic
# Models
class RegisterModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    profile_image: str = None


class LoginModel(BaseModel):
    email: EmailStr
    password: str


# Utils
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)


def create_jwt_token(user_id: str) -> str:
    payload = {
        "user_id": str(user_id),
        "exp": datetime.utcnow() + timedelta(days=1),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


# Routes
@router.post("/register")
def register(user: RegisterModel):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")

    hashed_pw = hash_password(user.password)
    user_data = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pw,
        "phone": user.phone,
        "profile_image": user.profile_image,
        "created_at": datetime.utcnow(),
    }
    result = users_collection.insert_one(user_data)

    token = create_jwt_token(result.inserted_id)
    return {"message": "Registration successful", "token": token}


@router.post("/login")
def login(user: LoginModel):
    db_user = users_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_jwt_token(db_user["_id"])
    return {"message": "Login successful", "token": token}

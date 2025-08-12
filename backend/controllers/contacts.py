from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from typing import List
from pydantic import BaseModel
from database.db import db

router = APIRouter()


# Pydantic models
class Contact(BaseModel):
    name: str
    email: str
    phone: str


class ContactOut(Contact):
    id: str


# Add new contact
@router.post("/contacts", response_model=dict)
def create_contact(contact: Contact, user_id: str):

    # Check if the contact exists in the users collection
    user_exists = db.users.find_one({"email": contact.email})
    if not user_exists:
        raise HTTPException(
            status_code=400, detail="Contact does not exist in the system"
        )
    contact_data = contact.dict()
    contact_data["user_id"] = user_id
    result = db.contacts.insert_one(contact_data)
    return {"message": "Contact created successfully", "id": str(result.inserted_id)}


# Fetch all contacts for a user
@router.get("/contacts", response_model=List[ContactOut])
def get_contacts(user_id: str):
    contacts = list(db.contacts.find({"user_id": user_id}))
    if not contacts:
        raise HTTPException(status_code=404, detail="No contacts found")
    return [
        ContactOut(
            id=str(contact["_id"]),
            name=contact["name"],
            email=contact["email"],
            phone=contact["phone"],
        )
        for contact in contacts
    ]

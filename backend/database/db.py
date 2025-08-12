import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import dotenv

dotenv.load_dotenv()

password = os.getenv("password")
uri = f"mongodb+srv://maif95689:{password}@cluster0.y0ibdhj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi("1"))
db = client["chatapp"]

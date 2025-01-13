import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MONGO_URI = os.getenv("MONGODB_API_KEY")
    COSMOS_URI = os.getenv("AZURE_URL")
    COSMOS_KEY = os.getenv("AZURE_KEY")

# from flask_pymongo import PyMongo
import os
from config import Config
from azure.cosmos import CosmosClient, PartitionKey


client = CosmosClient(os.getenv('AZURE_URL'), os.getenv('AZURE_KEY'))

# def init_db(app):
#     try:
#         # app.config["MONGO_URI"] = Config.MONGO_URI
        
#         app.config["COSMOS_URI"] = Config.COSMOS_URI
#         app.config["COSMOS_KEY"] = Config.COSMOS_KEY
#         # client.init_app(app)
#     except Exception as e:
#         print(e)



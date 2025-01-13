from database import client
from uuid import uuid4
from flask import Blueprint, request, jsonify
from azure.cosmos import CosmosClient, PartitionKey
from schemas import UserSchema
from datetime import datetime
from pydantic import ValidationError
import bcrypt
import os

# current_time = datetime.now()
# formatted_time = current_time.strftime("%I:%M:%S %p")
# user_routes = Blueprint('user_routes', __name__)
# @user_routes.route('/', methods=['POST'])
# def create_user():
#     print(request.json,"from users")
#     try:
#         data = UserSchema(**request.json)
#         combined = (data.password + os.getenv("SECRET_KEY")).encode()
#         salt = bcrypt.gensalt()
#         hashed = bcrypt.hashpw(combined, salt)
#         user = {
#            "userId":str(uuid4()),
#             "username": data.username,
#             "password": hashed.decode(),
#             "created_at":  formatted_time,
#             # "updated_at":  formatted_time
#         }
#         user_id = mongo.db.users.insert_one(user).inserted_id
#         return jsonify({"userId": str(user_id),"username":data.username}), 201
#     except ValidationError as e:
#         return jsonify({"error": e.errors()}), 400

# @user_routes.route('/', methods=['GET'])
# def get_users():
#     users = list(mongo.db.users.find({}, {"password": 0}))
#     for user in users:
#         user["_id"] = str(user["_id"])
#     return jsonify(users), 200



DATABASE_NAME = "UserDetails"
CONTAINER_NAME = "Users"

database = client.create_database_if_not_exists(DATABASE_NAME)
container = database.create_container_if_not_exists(
    id = CONTAINER_NAME,
    partition_key = PartitionKey(path="/userId")
    )

current_time = datetime.now()
formatted_time = current_time.strftime("%I:%M:%S %p")

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/', methods=['POST'])
def create_user():
    print(request.json, "from users")
    try:
        data = UserSchema(**request.json)
        combined = (data.password + os.getenv("SECRET_KEY")).encode()
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(combined, salt)

        user = {
            "id": str(uuid4()),  # Cosmos DB uses "id" as the primary key
            "userId": str(uuid4()),
            "username": data.username,
            "password": hashed.decode(),
            "created_at": formatted_time,
            # "updated_at": formatted_time
        }
        print(user)

        container.create_item(body=user)
        return jsonify({"userId": user["userId"], "username": data.username}), 201

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400

@user_routes.route('/', methods=['GET'])
def get_users():
    query = "SELECT c.id, c.userId, c.username, c.created_at FROM c"
    users = list(container.query_items(query=query, enable_cross_partition_query=True))
    return jsonify(users), 200



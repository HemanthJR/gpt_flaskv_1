from uuid import uuid4
from flask import Blueprint, request, jsonify
from database import client
from azure.cosmos import CosmosClient, PartitionKey
from schemas import ChatroomSchema
from datetime import datetime
from pydantic import ValidationError


chatroom_routes = Blueprint('chatroom_routes', __name__)



DATABASE_NAME = "UserDetails"
CONTAINER_NAME = "chatrooms"

database = client.create_database_if_not_exists(DATABASE_NAME)
container = database.create_container_if_not_exists(
    id = CONTAINER_NAME,
    partition_key = PartitionKey(path="/userId")
    )


chatroom_routes = Blueprint('chatroom_routes', __name__)

@chatroom_routes.route('/', methods=['POST'])
def create_chatroom():
    try:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%I:%M:%S %p")

        data = request.json
        userId = data["userId"]
        chatroomId = data["chatroomId"]
        prompt_data = data["prompt"]
        response_data = data["response"]

        # Prepare prompts and responses with IDs
        prompt_data = [
            {"promptId": str(uuid4()), "prompt": prompt["prompt"]}
            for prompt in prompt_data
        ]

        response_data = [
            {
                "responseId": str(uuid4()),
                "response": response["response"],
                "promptId": prompt_data[index]["promptId"]
            }
            for index, response in enumerate(response_data)
        ]

        print(f"User ID: {userId}, Chatroom ID: {chatroomId}")

        # Check if the chatroom exists
        query = f"SELECT * FROM c WHERE c.userId = '{userId}' AND c.chatroomId = '{chatroomId}'"
        existing_chatrooms = list(container.query_items(query=query, enable_cross_partition_query=True))
        existing_chatroom = existing_chatrooms[0] if existing_chatrooms else None

        if existing_chatroom:
            # Check if the specific chat exists
            existing_chat = next(
                (chat for chat in existing_chatroom['chats'] if chat['chatId'] == data.get('chatId')), None
            )

            if existing_chat:
                # Update existing chat with new prompts and responses
                for prompt, response in zip(prompt_data, response_data):
                    existing_chat["prompts_responses"].append({"prompt": prompt, "response": response})

                # Update chatroom in Cosmos DB
                existing_chatroom["updated_at"] = formatted_time
                container.upsert_item(existing_chatroom)

                return jsonify({
                    "message": "New prompts and responses added to existing chat",
                    "chatroomId": chatroomId,
                    "chatId": existing_chat["chatId"],
                    "created_at": formatted_time
                }), 200
            else:
                # Create a new chat in the existing chatroom
                new_chat_id = str(uuid4())
                new_chat = {
                    "chatId": new_chat_id,
                    "prompts_responses": [{"prompt": prompt, "response": response} for prompt, response in zip(prompt_data, response_data)]
                }
                existing_chatroom["chats"].append(new_chat)
                existing_chatroom["updated_at"] = formatted_time

                # Update chatroom in Cosmos DB
                container.upsert_item(existing_chatroom)

                return jsonify({
                    "message": "New chat created in existing chatroom",
                    "chatroomId": chatroomId,
                    "chatId": new_chat_id,
                    "created_at": formatted_time
                }), 201
        else:
            # Create a new chatroom
            new_chat_id = str(uuid4())
            new_chatroom = {
                "id": str(uuid4()),  # Cosmos DB requires a unique 'id' field
                "userId": userId,
                "chatroomId": chatroomId,
                "chats": [
                    {
                        "chatId": new_chat_id,
                        "prompts_responses": [{"prompt": prompt, "response": response} for prompt, response in zip(prompt_data, response_data)]
                    }
                ],
                "created_at": formatted_time,
                "updated_at": formatted_time
            }

            container.create_item(new_chatroom)

            return jsonify({
                "message": "New chatroom created",
                "chatroomId": chatroomId,
                "chatId": new_chat_id,
                "created_at": formatted_time
            }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# @chatroom_routes.route('/', methods=['POST'])
# def create_chatroom():
#     try:
#         current_time = datetime.now()
#         formatted_time = current_time.strftime("%I:%M:%S %p")

#         data = request.json
#         userId = data["userId"]
#         chatroomId = data["chatroomId"]
#         prompt_data = data["prompt"]
#         response_data = data["response"]

#         prompt_data = [
#             {
#                 "promptId": str(uuid4()), 
#                 "prompt": prompt["prompt"]
#             }
#             for prompt in prompt_data
#         ]

#         response_data = [
#             {
#                 "responseId": str(uuid4()), 
#                 "response": response["response"],
#                 "promptId": prompt_data[index]["promptId"]  
#             }
#             for index, response in enumerate(response_data)
#         ]
        
#         print(f"User ID: {userId}, Chatroom ID: {chatroomId}")

#         existing_chatroom = mongo.db.chatrooms.find_one({"userId": userId, "chatroomId": chatroomId})
#         print(f"Existing Chatroom: {existing_chatroom}")

#         if existing_chatroom:
#             existing_chat = next((chat for chat in existing_chatroom['chats'] if chat['chatId'] == data.get('chatId')), None)

#             if existing_chat:
#                 mongo.db.chatrooms.update_one(
#                     {"userId": userId, "chatroomId": chatroomId, "chats.chatId": existing_chat["chatId"]},
#                     {
#                         "$push": {
#                             "chats.$.prompts_responses": {"$each": list(zip(prompt_data, response_data))}  
#                         },
#                         "$set": {"updated_at": formatted_time} 
#                     }
#                 )

#                 return jsonify({
#                     "message": "New prompts and responses added to existing chat",
#                     "chatroomId": chatroomId,
#                     "chatId": existing_chat["chatId"],
#                     "created_at": formatted_time
#                 }), 200
            
#             else:
#                 new_chat_id = str(uuid4())
#                 mongo.db.chatrooms.update_one(
#                     {"userId": userId, "chatroomId": chatroomId},
#                     {
#                         "$push": {
#                             "chats": {
#                                 "chatId": new_chat_id,
#                                 "prompts_responses": list(zip(prompt_data, response_data))
#                             }
#                         },
#                         "$set": {"updated_at": formatted_time}
#                     }
#                 )

#                 return jsonify({
#                     "message": "New chat created in existing chatroom",
#                     "chatroomId": chatroomId,
#                     "chatId": new_chat_id,
#                     "created_at": formatted_time
#                 }), 201

#         else:
#             new_chat_id = str(uuid4())
#             new_chatroom = {
#                 "userId": userId,
#                 "chatroomId": str(uuid4()), 
#                 "chats": [{
#                     "chatId": new_chat_id, 
#                     "prompts_responses": list(zip(prompt_data, response_data))
#                 }],
#                 "created_at": formatted_time,
#                 "updated_at": formatted_time
#             }

#             mongo.db.chatrooms.insert_one(new_chatroom)

#             return jsonify({
#                 "message": "New chatroom created",
#                 "chatroomId": new_chatroom["chatroomId"],
#                 "chatId": new_chat_id,
#                 "created_at": formatted_time
#             }), 201

#     except ValidationError as e:
#         return jsonify({"error": e.errors()}), 400

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@chatroom_routes.route('/<userid>', methods=['GET'])
def get_chatrooms_by_user(userid):
    try:
        query = f"SELECT c.chatroomId, c.chats, c.created_at, c.updated_at FROM c WHERE c.userId = '{userid}'"
        chatrooms = list(container.query_items(query=query, enable_cross_partition_query=True))

        if chatrooms:
            return jsonify(chatrooms), 200

        return jsonify("No chatrooms found"), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# @chatroom_routes.route('/update', methods=['PUT'])
# def update_chatroom():
#     try:
#         current_time = datetime.now()
#         formatted_time = current_time.strftime("%I:%M:%S %p")

#         data = request.json
#         userId = data["userId"]
#         chatroomId = data["chatroomId"]
#         chatId = data["chatId"]
#         prompt_data = data["prompt"]
#         response_data = data["response"]

#         prompt_data = [
#             {
#                 "promptId": prompt["promptId"],
#                 "prompt": prompt["prompt"]
#             }
#             for prompt in prompt_data
#         ]

#         response_data = [
#             {
#                 "responseId": response["responseId"],
#                 "response": response["response"],
#                 "promptId": prompt_data[index]["promptId"]
#             }
#             for index, response in enumerate(response_data)
#         ]

#         query = f"SELECT * FROM c WHERE c.userId = '{userId}' AND c.chatroomId = '{chatroomId}'"
#         chatrooms = list(container.query_items(query=query, enable_cross_partition_query=True))

#         if not chatrooms:
#             return jsonify({"error": "Chatroom not found"}), 404

#         existing_chatroom = chatrooms[0]
#         chat = next((chat for chat in existing_chatroom["chats"] if chat["chatId"] == chatId), None)

#         if not chat:
#             return jsonify({"error": "ChatId not found in the chatroom"}), 404

#         for prompt, response in zip(prompt_data, response_data):
#             promptId = prompt["promptId"]

#             if not isinstance(chat["prompts_responses"], list):
#                 return jsonify({"error": f"prompts_responses is not a list. Found type: {type(chat['prompts_responses'])}"}), 500

#             existing_prompt = next(
#                 (item for sublist in chat["prompts_responses"] if isinstance(sublist, dict) for item in [sublist] if item.get("promptId") == promptId),
#                 None
#             )

#             if existing_prompt:
#                 # Update existing prompt
#                 for sublist in chat["prompts_responses"]:
#                     if isinstance(sublist, dict) and sublist.get("promptId") == promptId:
#                         sublist["response"] = response["response"]
#                         sublist["updated_at"] = formatted_time
#                         break
#             else:
#                 # Append new prompt and response
#                 chat["prompts_responses"].append({
#                     "promptId": promptId,
#                     "prompt": prompt["prompt"],
#                     "responseId": response["responseId"],
#                     "response": response["response"],
#                     "created_at": formatted_time,
#                     "updated_at": formatted_time
#                 })

#         # Replace the updated chatroom in Cosmos DB
#         container.replace_item(item=existing_chatroom["id"], body=existing_chatroom)

#         return jsonify({
#             "message": "Prompt and response updated or appended successfully",
#             "chatroomId": chatroomId,
#             "chatId": chatId,
#             "updated_at": formatted_time
#         }), 200

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


@chatroom_routes.route('/update', methods=['PUT'])
def update_chatroom():
    try:
        current_time = datetime.now()
        formatted_time = current_time.strftime("%I:%M:%S %p")

        data = request.json
        userId = data["userId"]
        chatroomId = data["chatroomId"]
        chatId = data["chatId"]
        prompt_data = data["prompt"]
        response_data = data["response"]

        # Prepare prompt and response data
        prompt_response_pairs = [
            {
                "prompt": {
                    "promptId": prompt["promptId"],
                    "prompt": prompt["prompt"]
                },
                "response": {
                    "responseId": response["responseId"],
                    "response": response["response"],
                    "promptId": prompt["promptId"],
                    "created_at": formatted_time,
                    "updated_at": formatted_time
                }
            }
            for prompt, response in zip(prompt_data, response_data)
        ]

        # Fetch the existing chatroom
        query = f"SELECT * FROM c WHERE c.userId = '{userId}' AND c.chatroomId = '{chatroomId}'"
        chatrooms = list(container.query_items(query=query, enable_cross_partition_query=True))

        if not chatrooms:
            return jsonify({"error": "Chatroom not found"}), 404

        existing_chatroom = chatrooms[0]
        chat = next((chat for chat in existing_chatroom["chats"] if chat["chatId"] == chatId), None)

        if not chat:
            return jsonify({"error": "ChatId not found in the chatroom"}), 404

        # Update or append prompts_responses
        for pair in prompt_response_pairs:
            existing_entry = next(
                (entry for entry in chat["prompts_responses"] if entry["prompt"]["promptId"] == pair["prompt"]["promptId"]),
                None
            )

            if existing_entry:
                # Update the response of the existing entry
                existing_entry["response"].update(pair["response"])
            else:
                # Append the new prompt-response pair
                chat["prompts_responses"].append(pair)

        # Replace the updated chatroom in Cosmos DB
        container.replace_item(item=existing_chatroom["id"], body=existing_chatroom)

        return jsonify({
            "message": "Prompt and response updated or appended successfully",
            "chatroomId": chatroomId,
            "chatId": chatId,
            "updated_at": formatted_time
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# @chatroom_routes.route('/update', methods=['PUT'])
# def update_chatroom():
#     try:
#         current_time = datetime.now()
#         formatted_time = current_time.strftime("%I:%M:%S %p")

#         data = request.json
#         userId = data["userId"]
#         chatroomId = data["chatroomId"]
#         chatId = data["chatId"]  
#         prompt_data = data["prompt"]
#         response_data = data["response"]

       
#         prompt_data = [
#             {
#                 "promptId": prompt["promptId"],  
#                 "prompt": prompt["prompt"]
#             }
#             for prompt in prompt_data
#         ]

#         response_data = [
#             {
#                 "responseId": response["responseId"],  
#                 "response": response["response"],
#                 "promptId": prompt_data[index]["promptId"]  
#             }
#             for index, response in enumerate(response_data)
#         ]

#         existing_chatroom = mongo.db.chatrooms.find_one({
#             "userId": userId,
#             "chatroomId": chatroomId
#         })

#         if existing_chatroom:
#             chat = next((chat for chat in existing_chatroom["chats"] if chat["chatId"] == chatId), None)

#             if chat:
#                 for prompt, response in zip(prompt_data, response_data):
#                     promptId = prompt["promptId"]
#                     print(promptId,"<-prompt_id")
#                     print(type(promptId),"<-prompt_id")
#                     existing_prompt = next(
#                         # (item for item in chat["prompts_responses"] if item["promptId"] == promptId),
#                         (item for sublist in chat["prompts_responses"] for item in sublist if item["promptId"] == promptId), 
#                         None
#                     )

#                     if existing_prompt:
#                         mongo.db.chatrooms.update_one(
#                             {"userId": userId, "chatroomId": chatroomId, "chats.chatId": chatId, "chats.prompts_responses.promptId": promptId},
#                             {
#                                 "$set": {
#                                     "chats.$.prompts_responses.$[elem].response": response["response"],
#                                     "chats.$.prompts_responses.$[elem].updated_at": formatted_time
#                                 }
#                             },
#                             array_filters=[{"elem.promptId": promptId}]
#                         )
#                     else:
#                         mongo.db.chatrooms.update_one(
#                             {"userId": userId, "chatroomId": chatroomId, "chats.chatId": chatId},
#                             {
#                                 "$push": {
#                                     "chats.$.prompts_responses": {
#                                         "promptId": promptId,
#                                         "prompt": prompt["prompt"],
#                                         "responseId": response["responseId"],
#                                         "response": response["response"],
#                                         "created_at": formatted_time,
#                                         "updated_at": formatted_time
#                                     }
#                                 },
#                                 "$set": {"updated_at": formatted_time}
#                             }
#                         )

#                 return jsonify({
#                     "message": "Prompt and response updated or appended successfully",
#                     "chatroomId": chatroomId,
#                     "chatId": chatId,
#                     "updated_at": formatted_time
#                 }), 200
#             else:
#                 return jsonify({"error": "ChatId not found in the chatroom"}), 404
#         else:
#             return jsonify({"error": "Chatroom not found"}), 404

#     except ValidationError as e:
#         return jsonify({"error": e.errors()}), 400


@chatroom_routes.route('roomid/<userid>', methods=['GET'])
def get_chatrooms_id(userid):
    try:
        result = []
        promt = []
        final_out = []
        
        query = f"SELECT c.id, c.userId, c.chatroomId, c.chats, c.created_at, c.updated_at FROM c WHERE c.userId = '{userid}'"
        chatrooms = list(container.query_items(query=query, enable_cross_partition_query=True))

        if not chatrooms:
            return jsonify("No chatrooms found"), 404

        for chatroom in chatrooms:
            result.append(chatroom["chatroomId"])
            for chat in chatroom.get("chats", []):  
                for res in chat.get("prompts_responses", []):  
                    prompt_entry = res.get("prompt")
                    if prompt_entry and isinstance(prompt_entry, dict):
                        promt.append(prompt_entry["prompt"])

        
        for chatroom_id, prompt in zip(result, promt):
            final_out.append({
                "chatroomid": chatroom_id,
                "prompt": prompt
            })

        return jsonify(final_out), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@chatroom_routes.route('/history/<userid>', methods=['GET'])
def get_history(userid):
    try:
        query = f"SELECT * FROM c WHERE c.userId = '{userid}'"
        chatrooms = list(container.query_items(query=query, enable_cross_partition_query=True))

        
        if not chatrooms:
            return jsonify("No chatrooms found"), 404

        
        sorted_records = sorted(
            chatrooms,
            key=lambda x: datetime.strptime(x.get("updated_at", "12:00:00 AM"), "%I:%M:%S %p"),
            reverse=True
        )

        
        latest_records = sorted_records[:5]

        
        prompts = []
        for record in latest_records:
            for chat in record.get("chats", []):
                for prompts_responses in chat.get("prompts_responses", []):
                    prompt_entry = prompts_responses.get("prompt")
                    if prompt_entry and isinstance(prompt_entry, dict) and "prompt" in prompt_entry:
                        prompts.append(prompt_entry["prompt"])

        return jsonify(prompts), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


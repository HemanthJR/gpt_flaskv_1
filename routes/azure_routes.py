from flask import Blueprint, jsonify,request
from pydantic import ValidationError
from openai import AzureOpenAI

import os
from dotenv import load_dotenv

import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT" )
api_key = os.getenv("AZURE_OPENAI_API_KEY")
api_version = "2023-03-15-preview"  

openai_client = AzureOpenAI(api_version=api_version,azure_endpoint=endpoint, api_key=api_key)
azure_routes = Blueprint('azure_routes', __name__)

#CLOUDINARY SECRETS
cloudinary.config(
    cloud_name = os.getenv("CLOUD_NAME"),
    api_key = os.getenv("CLOUD_API_KEY"),
    api_secret = os.getenv("CLOUD_API_SECRET"),
    secure = True
)


# @azure_routes.route('/generate_text', methods=['POST'])
# def generate_text():
#     try:
#         data = request.get_json()
#         user_input = data.get('user_input', '')
#         conversation = data.get('conversation', [{'role': 'system', 'content': 'You are a helpful assistant.'}])
#         conversation.append({'role': 'user', 'content': user_input})

#         if not user_input:
#             return jsonify({'error': 'Prompt is required'}), 400
        

#         image_url = None
#         if 'image' in request.files:
#             image_file = request.files['image'] 
#             image_url = upload_image_to_cloudinary(image_file)
#             print(image_url)
#             conversation.append({'role': 'user', 'content': f"Image URL: {image_url}"})




#         response = openai_client.chat.completions.create(
#                 model="gpt4-o",
#                 temperature=0.3,
#                 stream = True,
#                 messages=conversation,
#             )

#         generated_text = ""

#         for resp in response:
#             content = resp.choices[0].delta.content 
#             if content:
#                 generated_text += content

#         return jsonify({'generated_text': generated_text}) 

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
    

# def upload_image_to_cloudinary(image_file):
#     try:
#         # Upload the image to Cloudinary
#         response = cloudinary.uploader.upload(image_file)
        
#         # Extract and return the secure URL
#         return response.get('secure_url', '')
#     except Exception as e:
#         print(f"Error uploading image to Cloudinary: {e}")
#         raise e

@azure_routes.route('/hrgenerate_text', methods=['POST'])
def generate_text():
    try:
        # Check if form-data includes a file
        user_input = request.form.get('user_input', '')
        conversation = request.form.get('conversation', '[{"role": "system", "content": "You are a helpful assistant."}]')
        image_file = request.files.get('image')
        # print(image_file,"<-img")
        if not user_input and not image_file:
            return jsonify({'error': 'Prompt or image is required'}), 400

        # Convert conversation to list of dicts
        import json
        conversation = json.loads(conversation)
        conversation.append({'role': 'user', 'content': user_input})
        # print(conversation)
        
        image_url = None
        if image_file:
            upload_result = cloudinary.uploader.upload(image_file)
            image_url = upload_result.get('url')
            # print(image_url)
            
            conversation.append({'role': 'user', 'content': [
                # {"type":"text", "text":f"{user_input}"},
                {"type":"image_url","image_url": {"url": image_url}}
            ]})
            # f"Attached image: {image_url}. {user_input}"}
            # print(conversation,"<-image update")
        
        response = openai_client.chat.completions.create(
            model="gpt4-o",
            temperature=0.3,
            stream=True,
            messages=conversation,
        )

        generated_text = ""
        for resp in response:
            content = resp.choices[0].delta.content
            if content:
                generated_text += content

        return jsonify({'generated_text': generated_text, 'image_url': image_url})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


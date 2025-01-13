import uuid
from pydantic import BaseModel, Field,root_validator
from typing import List, Optional
from datetime import datetime
from bson.objectid import ObjectId
current_time = datetime.now()
formatted_time = current_time.strftime("%I:%M:%S %p")
class UserSchema(BaseModel):
    userId:str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password: str
    created_at: str = Field(default_factory=lambda:str(formatted_time))  


# class ChatroomSchema(BaseModel):
#     userId: str 
#     chatroomId: str = Field(default_factory=lambda: str(uuid.uuid4())) 
#     chatId: str = Field(default_factory=lambda: str(uuid.uuid4())) 
#     prompt: List[str] 
#     response: List[str]  
#     created_at: datetime = Field(default_factory=datetime.utcnow)  
#     updated_at: datetime = Field(default_factory=datetime.utcnow) 

# class ChatroomSchema(BaseModel):
#     userId: str
#     chatroomId: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     chatId: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     prompt: List[str]  
#     response: List[str]  
#     created_at: str = Field(default_factory=lambda:str(formatted_time))
#     updated_at: str = Field(default_factory=lambda:str(formatted_time))

   
#     @root_validator(pre=True)
#     def ensure_prompt_response_are_lists(cls, values):
       
#         if isinstance(values.get('prompt'), str):
#             values['prompt'] = [values['prompt']]
#         if isinstance(values.get('response'), str):
#             values['response'] = [values['response']]
#         return values
    


class PromptSchema(BaseModel):
    promptId: str 
    prompt: str 
    response_promptId: str  


class ResponseSchema(BaseModel):
    promptId:str
    responseId: str  
    response: str  

class ChatSchema(BaseModel):
    chatId: str 
    prompts_responses: List[dict]  

class ChatroomSchema(BaseModel):
    userId: str 
    chatroomId: str  
    chatId: str  
    prompt: List[str]  
    response: List[str]  
    created_at: datetime  
    updated_at: datetime  

    class Config:
     
        json_encoders = {
            uuid.UUID: lambda v: str(v)
        }

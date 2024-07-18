from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import pymongo
from bson.objectid import ObjectId
import requests
import json
import os

# Assuming FIREWORKAI_API_KEY is stored in environment variables
FIREWORKAI_API_KEY = os.getenv('FIREWORKAI_API_KEY')

app = FastAPI()

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chat_app"]
users_collection = db["users"]
messages_collection = db["messages"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    username: str
    password: str

class Message(BaseModel):
    username: str
    message: str

def authenticate_user(username: str, password: str):
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return True
    return False

def create_user(username: str, password: str):
    if users_collection.find_one({"username": username}):
        return False
    users_collection.insert_one({"username": username, "password": password})
    return True

def save_message(username: str, message: str):
    messages_collection.insert_one({"username": username, "message": message})

def get_fireworks_response(user_message: str):
    url = "https://api.fireworks.ai/inference/v1/chat/completions"
    payload = {
        "model": "accounts/fireworks/models/llama-v3-70b-instruct",
        "max_tokens": 1024,
        "top_p": 1,
        "top_k": 40,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "temperature": 0.6,
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ]
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {FIREWORKAI_API_KEY}"
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No response from Fireworks AI')
    else:
        return 'Error: Unable to get response from Fireworks AI'

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if not authenticate_user(form_data.username, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": form_data.username, "token_type": "bearer"}

@app.post("/register")
async def register(user: User):
    if create_user(user.username, user.password):
        return {"message": "Registration successful! You can now log in."}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists. Please choose a different username.",
        )

@app.post("/chat")
async def chat(message: Message):
    
    bot_response = get_fireworks_response(message.message)
    save_message(message.username, message.message)
    save_message('bot', bot_response)
    return {"response": bot_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

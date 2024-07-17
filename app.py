import json
import streamlit as st
import requests
import streamlit as st
import pymongo
from bson.objectid import ObjectId

# MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["chat_app"] 
users_collection = db["users"]
messages_collection = db["messages"]


# Set page configuration
st.set_page_config(page_title='Login/Register and Chatbot Page')

# In-memory storage for user credentials (for demo purposes)
# In a real application, use a secure database to store credentials
if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        "admin": "password"
    }

# Function to authenticate user
def authenticate(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    return True if user else False

# Function to register user
def register(username, password):
    if users_collection.find_one({"username": username}):
        return False
    users_collection.insert_one({"username": username, "password": password})
    return True

# Function to save chat message to MongoDB
def save_message(username, message):
    messages_collection.insert_one({"username": username, "message": message})

# Function to get chat response from Fireworks AI
def get_fireworks_response(user_message):
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
    "Authorization": "Bearer JqHGWbAlvB24DRxSrzfRMAerqWDCgcYmeGPwTSbdAvRAnC11"
    }
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
        return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No response from Fireworks AI')
    else:
        return 'Error: Unable to get response from Fireworks AI'

# Page selection
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Login", "Register"])

if page == "Login":
    st.title('Login Page')

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    login_button = st.button("Login")

    if login_button:
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.write("Welcome to the application!")
            st.balloons()  # This triggers the balloon effect
        else:
            st.error("Invalid username or password")

elif page == "Register":
    st.title('Register Page')

    new_username = st.text_input("Choose a Username")
    new_password = st.text_input("Choose a Password", type='password')
    register_button = st.button("Register")

    if register_button:
        if register(new_username, new_password):
            st.success("Registration successful! You can now log in.")
        else:
            st.error("Username already exists. Please choose a different username.")

# Check if the user is logged in
if 'logged_in' in st.session_state and st.session_state.logged_in:
    st.title("Chatbot")
    st.write("You are logged in! Start chatting below:")

    # Chatbot functionality
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    user_message = st.text_input("You: ")
    if st.button("Send"):
        if user_message:
            st.session_state.messages.append(f"You: {user_message}")
            bot_response = get_fireworks_response(user_message)
            st.session_state.messages.append(f"Bot: {bot_response}")
            save_message('you', bot_response)  # Save message to MongoDB

    # Display chat history
    for message in st.session_state.messages:
        st.write(message)

import streamlit as st
import requests

# Set page configuration
st.set_page_config(page_title='Login/Register and Chatbot Page')

# Backend API URLs
backend_url = "http://127.0.0.1:8000"

# Function to login user
def login(username, password):
    response = requests.post(f"{backend_url}/token", data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        return None
# Function to register user
def register(username, password):
    response = requests.post(f"{backend_url}/register", json={"username": username, "password": password})
    return response.status_code == 200

# Function to chat with the bot
def chat_with_bot(username, message, token):
    response = requests.post(
        f"{backend_url}/chat",
        json={"username": username, "message": message},
        headers={"Authorization": f"Bearer {token}"}
    )
    if response.status_code == 200:
        return response.json().get("response")
    else:
        return None

# Page selection
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Login", "Register", "Chat"])

if page == "Login":
    st.title('Login Page')
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    login_button = st.button("Login")

    if login_button:
        token = login(username, password)
        if token:
            st.session_state.logged_in = True
            st.session_state.token = token['access_token']
            st.session_state.username = username
            st.success("Login successful!")
            st.balloons()
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

# Chat functionality
if page == "Chat":
    if 'logged_in' in st.session_state and st.session_state.logged_in:
        st.title("Chatbot")
        st.write("You are logged in! Start chatting below:")

        if 'messages' not in st.session_state:
            st.session_state.messages = []

        user_message = st.text_input("You: ")
        if st.button("Send"):
            if user_message:
                st.session_state.messages.append(f"You: {user_message}")
                bot_response = chat_with_bot(st.session_state.username, user_message, st.session_state.token)
                if bot_response:
                    st.session_state.messages.append(f"Bot: {bot_response}")

        # Display chat history
        for message in st.session_state.messages:
            st.write(message)
    else:
        st.warning("Please log in first.")
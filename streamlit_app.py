import streamlit as st
import requests

# Set page configuration
st.set_page_config(page_title='CHAT_BOT', layout='wide')

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

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]

# Main content area
if not st.session_state.logged_in:
    page = st.sidebar.radio("Navigation", ["Login", "Register"])

    if page == "Login":
        st.title('Login')
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
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

    elif page == "Register":
        st.title('Register')
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type='password')
        register_button = st.button("Register")

        if register_button:
            if register(new_username, new_password):
                st.success("Registration successful! You can now log in.")
            else:
                st.error("Username already exists. Please choose a different username.")
else:
    st.title("💬 Chat-Bot")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.token = None
        st.session_state.username = None
        st.session_state.messages = [{"role": "assistant", "content": "How can I help you?"}]
        st.experimental_rerun()
    
    # Display chat messages
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    # Chat input
    if user_message := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": user_message})
        st.chat_message("user").write(user_message)
        
        bot_response = chat_with_bot(st.session_state.username, user_message, st.session_state.token)
        if bot_response:
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            st.chat_message("assistant").write(bot_response)

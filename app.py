import streamlit as st
import google.generativeai as genai


import time

import pandas as pd
import hashlib
import os

st.set_page_config(page_title="NEXA AI", page_icon="🤖")

# --- 2. SIGNUP & LOGIN SYSTEM ---

# A. Function to encrypt passwords
def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# B. Create the user database file if it doesn't exist
USER_DB = "users.csv"
if not os.path.exists(USER_DB):
    df = pd.DataFrame(columns=["email", "password"])
    df.to_csv(USER_DB, index=False)

# C. DEFINE the auth_page (The computer needs to read this first!)
def auth_page():
    st.markdown("<h2 style='text-align: center; color: #00FBFF;'>Gear Up Productions</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email").lower()
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Login to NEXA"):
                df = pd.read_csv(USER_DB)
                if ((df['email'] == email) & (df['password'] == hash_pass(pw))).any():
                    st.session_state.logged_in = True
                    st.session_state.username = email
                    st.rerun()
                else:
                    st.error("Invalid Email or Password")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("New Email").lower()
            new_pw = st.text_input("New Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            if st.form_submit_button("Sign Up"):
                df = pd.read_csv(USER_DB)
                if new_email in df['email'].values:
                    st.warning("Email already exists!")
                elif new_pw != confirm:
                    st.error("Passwords don't match!")
                else:
                    new_user = pd.DataFrame([[new_email, hash_pass(new_pw)]], columns=["email", "password"])
                    new_user.to_csv(USER_DB, mode='a', header=False, index=False)
                    st.success("Account created! Now go to the Login tab.")

# D. CALL the function to run the logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth_page()
    st.stop()  # This stops the rest of the app until login is successful

# --- 3. UI STYLING & ENTRANCE ANIMATION ---
# This is where your Cyan CSS and the 'first_load' balloons go.
# Since the user is now logged in, they will see the animations.

# --- 4. AI SETUP ---
# Your Gemini API Key and System Instructions ("You are NEXA AI...")

# --- 5. CHAT INTERFACE ---
# The logic that displays messages and takes user input.
if 'first_load' not in st.session_state:
    st.session_state.first_load = True

# Only run this block if it's the very first time the app is opening
if st.session_state.first_load:
    st.balloons()
    welcome_placeholder = st.empty()
    
    with welcome_placeholder.container():
        st.markdown(f"""
            <div style="text-align: center; padding: 50px;">
                <h1 style="color: #00FBFF; font-size: 3rem; text-shadow: 0 0 20px #00FBFF;">
                    NEXA AI
                </h1>
                <h3 style="color: #FFFFFF;">Your Personal Companion</h3>
                <p style="color: #00FBFF; font-weight: bold; letter-spacing: 2px;">
                    BY GEAR UP PRODUCTIONS
                </p>
            </div>
        """, unsafe_allow_html=True)
        

        time.sleep(3)
    
    welcome_placeholder.empty()
    # Flip the flag to False so this doesn't run again when you chat
    st.session_state.first_load = False


# --- CUSTOM UI STYLING ---
st.markdown("""
    <style>
    /* Main background and text */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Neon Cyan Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 2px solid #00FBFF;
    }

    /* Animated Chat Messages */
    div[data-testid="stChatMessage"] {
        animation: fadeIn 0.5s ease-in-out;
        border-radius: 15px;
        margin-bottom: 10px;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* User Message Styling */
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #1B2129;
        border-left: 5px solid #00FBFF;
    }

    /* Assistant Message Styling */
    div[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #0D2D35;
        border-left: 5px solid #0088A3;
    }

    /* Glowing Chat Input */
    .stChatInputContainer > div {
        border: 1px solid #00FBFF !important;
        box-shadow: 0 0 10px #00FBFF33;
    }

    /* Custom Title Color */
    h1 {
        color: #00FBFF;
        text-shadow: 0 0 10px #00FBFF66;
    }
    </style>
    """, unsafe_allow_html=True)

# ... (The rest of your existing logic: API Key, Model Setup, and Chat loop)

# ==========================================
# PASTE YOUR API KEY INSIDE THE QUOTES BELOW
# ==========================================
# NEW WAY (Safe for Gear Up Productions)
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Setup Google Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest'),system_instruction="You are NEXA AI, a conversational companion developed by Nivin in Gear Up Productions. You are friendly, helpful, and you should always identify yourself as NEXA AI from Gear Up Productions when asked who created you. Do not say you are a large language model trained by Google unless specifically asked about your underlying architecture.if the user ask hi say hi friend only nothing else")



# Page Config

# --- SIDEBAR & ADMIN PANEL ---
with st.sidebar:
    st.title("Gear Up Productions")
    st.info("NEXA AI v1.0")
    
    # 1. Clear Chat Button
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.write("---")
    
    # 2. Admin Dashboard Access
    # The 'key' parameter here is what prevents the Duplicate ID error!
    admin_pw = st.text_input("Enter Admin Key", type="password", key="admin_panel_key")
    
    if admin_pw == "Nivin@2007":
        st.write("### 👥 Registered Users")
        try:
            df_admin = pd.read_csv(USER_DB)
            st.dataframe(df_admin, use_container_width=True)
            st.metric("Total Members", len(df_admin))
        except Exception:
            st.error("User database not found yet.")
    elif admin_pw:
        st.sidebar.error("Access Denied")

# --- MAIN CHAT INTERFACE START ---

st.title("🤖 NEXA AI")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
# User Input
if prompt := st.chat_input("Ask NEXA anything..."):
    # 1. Show user message and save to local session history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Generate AI Response with HISTORY
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("NEXA is thinking...")
        
        try:
            # 3. Format history for Gemini API
            # Gemini expects 'user' and 'model' roles. We convert 'assistant' to 'model'.
            formatted_history = []
            for m in st.session_state.messages[:-1]: # All messages except the current one
                role = "model" if m["role"] == "assistant" else "user"
                formatted_history.append({"role": role, "parts": [m["content"]]})

            # 4. Start the chat session with memory
            chat_session = model.start_chat(history=formatted_history)
            
            # 5. Send new message
            response = chat_session.send_message(prompt)
            full_response = response.text
            
            message_placeholder.markdown(full_response)
            
            # 6. Save assistant response to local history
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            if "429" in str(e):
                st.error("🚀 NEXA is taking a quick breath! Please wait 60 seconds and try again.")
            else:
                st.error(f"Something went wrong: {e}")
        
        # Secret Key to open the database
        admin_pw = st.sidebar.text_input("Enter Admin Key", type="password")
        
        if admin_pw == "Nivin@2007": # You can change this secret password
            st.write("### 👥 Registered Users")
            
            try:
                # Reads the users.csv file from the Streamlit server
                df_admin = pd.read_csv(USER_DB)
                
                # Shows the list of emails and hashed passwords in a clean table
                st.dataframe(df_admin, use_container_width=True)
                
                # Quick stats for your venture
                st.metric("Total Members", len(df_admin))
                
            except FileNotFoundError:
                st.error("User database file not found yet.")
        
        elif admin_pw:
            st.sidebar.error("Access Denied: Incorrect Key")
import streamlit as st
import google.generativeai as genai
import time
import pandas as pd
import hashlib
import os

st.set_page_config(page_title="NEXA AI", page_icon="🤖")

# ==============================
# 1. AUTH SYSTEM
# ==============================

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

USER_DB = "users.csv"

if not os.path.exists(USER_DB):
    df = pd.DataFrame(columns=["email", "password"])
    df.to_csv(USER_DB, index=False)

def auth_page():
    st.markdown("<h2 style='text-align: center; color: #00FBFF;'>Gear Up Productions</h2>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Login", "Create Account"])

    # LOGIN
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

    # SIGNUP
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
                    st.success("Account created! Now login.")

# SESSION LOGIN CHECK
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    auth_page()
    st.stop()

# ==============================
# 2. WELCOME ANIMATION
# ==============================

if 'first_load' not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    st.balloons()
    placeholder = st.empty()

    with placeholder.container():
        st.markdown("""
        <div style="text-align:center;padding:50px;">
            <h1 style="color:#00FBFF;">NEXA AI</h1>
            <h3>Your Personal Companion</h3>
            <p>BY GEAR UP PRODUCTIONS</p>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(3)

    placeholder.empty()
    st.session_state.first_load = False

# ==============================
# 3. STYLING
# ==============================

st.markdown("""
<style>
.stApp {background-color:#0E1117;color:#FFFFFF;}

[data-testid="stSidebar"] {
    background-color:#161B22;
    border-right:2px solid #00FBFF;
}

div[data-testid="stChatMessage"] {
    border-radius:15px;
    margin-bottom:10px;
}

div[data-testid="stChatMessage"]:nth-child(even) {
    background-color:#1B2129;
    border-left:5px solid #00FBFF;
}

div[data-testid="stChatMessage"]:nth-child(odd) {
    background-color:#0D2D35;
    border-left:5px solid #0088A3;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 4. GEMINI SETUP
# ==============================

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction="""You are NEXA AI, created by Nivin in Gear Up Productions.
You are friendly and helpful.
If user says hi → reply only 'hi friend'."""
)

# ==============================
# 5. SIDEBAR (ADMIN PANEL)
# ==============================

with st.sidebar:
    st.title("Gear Up Productions")
    st.info("NEXA AI v1.0")

    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.write("---")

    admin_pw = st.text_input("Enter Admin Key", type="password")

    if admin_pw == "Nivin@2007":
        st.write("### 👥 Registered Users")
        df_admin = pd.read_csv(USER_DB)
        st.dataframe(df_admin)
        st.metric("Total Members", len(df_admin))

    elif admin_pw:
        st.error("Access Denied")

# ==============================
# 6. CHAT INTERFACE
# ==============================

st.title("🤖 NEXA AI")

if "messages" not in st.session_state:
    st.session_state.messages = []

# DISPLAY HISTORY
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# INPUT
if prompt := st.chat_input("Ask NEXA anything..."):

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")

        try:
            # FORMAT HISTORY
            formatted_history = []
            for m in st.session_state.messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                formatted_history.append({"role": role, "parts": [m["content"]]})

            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(prompt)

            reply = response.text
            placeholder.markdown(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            st.error(f"Error: {e}")
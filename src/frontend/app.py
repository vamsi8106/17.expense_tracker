#src/frontend/app.py
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import streamlit as st
import uuid
import requests
from src.config.settings import settings


API_URL = settings.API_URL


st.title("💬 Expense Assistant")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

msg = st.chat_input("Ask something...")

if msg:
    resp = requests.post(API_URL, json={
        "session_id": st.session_state.session_id,
        "message": msg
    }).json()["response"]

    st.session_state.history.append(("user", msg))
    st.session_state.history.append(("bot", resp))

for sender, txt in st.session_state.history:
    st.chat_message(sender).write(txt)

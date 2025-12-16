##BD_TK_FRONT/app_streamlit.py
import streamlit as st
import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app_utils.api import api_get, api_post, api_put, auth_headers, show_http_error, safe_json

st.set_page_config(page_title="Personas - Home", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None

st.title("🏠 Personas — Inicio")

if not st.session_state.get("token"):
    st.info("Iniciá sesión para habilitar las páginas.")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        data = api_post("/login", json={"username": username, "password": password}, timeout=15)
        if data and data.get("token"):
            st.session_state["token"] = data["token"]
            st.success("Login OK")
            st.rerun()
else:
    st.success("✅ Logueado. Usá el menú de la izquierda (Pages).")

##BD_TK_FRONT/app_streamlit.py
import streamlit as st
from utils.api import api_post, show_http_error

st.set_page_config(page_title="Personas - Home", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None

st.title("🏠 Personas — Inicio")

if not st.session_state.get("token"):
    st.info("Iniciá sesión para habilitar las páginas: Listado / Crear-Editar / Importar.")

    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        username = (username or "").strip()
        password = (password or "").strip()

        if not username or not password:
            st.error("Ingrese usuario y contraseña.")
            st.stop()

        r = api_post("/login", json={"username": username, "password": password}, timeout=15)
        if r is None:
            st.stop()

        if r.status_code == 200:
            data = r.json() or {}
            token = data.get("token")
            if not token:
                st.error("Login OK pero no llegó token. Revisá el backend.")
                st.stop()
            st.session_state["token"] = token
            st.success("Login OK ✅")
            st.rerun()
        else:
            show_http_error(r, "Login fallido")
else:
    st.success("✅ Logueado. Usá el menú de la izquierda (Pages).")

    if st.button("Cerrar sesión"):
        st.session_state["token"] = None
        st.rerun()

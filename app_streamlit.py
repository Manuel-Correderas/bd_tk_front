import os
import requests
import streamlit as st

# 🔐 DEFINICIÓN BLINDADA
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8001").rstrip("/")

st.set_page_config(page_title="Personas - Home", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None  # <- correcto

def auth_headers():
    t = st.session_state.get("token")
    return {"x-token": t} if t else {}

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return None

def show_http_error(resp, default="Error"):
    data = safe_json(resp)
    detail = data.get("detail") if isinstance(data, dict) else None
    st.error(detail or f"{default}: {resp.status_code} - {resp.text}")

def request_post(url, **kwargs):
    try:
        return requests.post(url, **kwargs)
    except Exception as e:
        st.error(f"Error conexión (POST): {e}")
        return None

def request_get(url, **kwargs):
    try:
        return requests.get(url, **kwargs)
    except Exception as e:
        st.error(f"Error conexión (GET): {e}")
        return None

st.title("🏠 Personas — Inicio")

# LOGIN
if not st.session_state.get("token"):
    st.info("Iniciá sesión para habilitar las páginas: Listado / Crear-Editar / Importar.")

    username = st.text_input("Usuario", key="login_user")
    password = st.text_input("Contraseña", type="password", key="login_pass")

    if st.button("Ingresar", key="btn_login"):
        if not username or not password:
            st.error("Ingrese usuario y contraseña.")
        else:
            r = request_post(
                f"{BACKEND_URL}/login",
                json={"username": username, "password": password},
                timeout=15,
            )
            if r is None:
                pass
            elif r.status_code == 200:
                data = safe_json(r) or {}
                st.session_state["token"] = data.get("token")
                st.success("Login OK")
                st.rerun()
            else:
                show_http_error(r, "Login fallido")
else:
    st.success("✅ Logueado. Usá el menú de la izquierda (Pages).")
    st.write("➡️ Andá a **📋 Listado**, **👤 Crear/Editar** o **📥 Importar** desde el menú.")

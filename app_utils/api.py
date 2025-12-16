# BD_TK_FRONT/utils/api.py
import requests
import streamlit as st

def backend_url() -> str:
    return st.secrets.get("BACKEND_URL", "http://127.0.0.1:10000").rstrip("/")

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

def api_get(path: str, **kwargs):
    try:
        return requests.get(f"{backend_url()}{path}", timeout=20, **kwargs)
    except Exception as e:
        st.error(f"Error conexión (GET): {e}")
        return None

def api_post(path: str, **kwargs):
    try:
        return requests.post(f"{backend_url()}{path}", timeout=30, **kwargs)
    except Exception as e:
        st.error(f"Error conexión (POST): {e}")
        return None

def api_put(path: str, **kwargs):
    try:
        return requests.put(f"{backend_url()}{path}", timeout=30, **kwargs)
    except Exception as e:
        st.error(f"Error conexión (PUT): {e}")
        return None
def handle_unauthorized(resp) -> bool:
    """
    Devuelve True si fue 401/403 y ya manejó el caso (logout + mensaje).
    """
    if resp is None:
        return False

    if resp.status_code in (401, 403):
        st.session_state["token"] = None
        st.warning("Tu sesión expiró o no tenés permisos. Volvé a iniciar sesión.")
        try:
            st.switch_page("app_streamlit.py")  # Streamlit >= 1.22
        except Exception:
            st.rerun()
        return True

    return False
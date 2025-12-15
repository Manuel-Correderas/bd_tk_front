##BD_TK_FRONT/utils/api.py
import requests
import streamlit as st

DEFAULT_BACKEND = "http://127.0.0.1:8001"

def get_backend_url() -> str:
    return st.secrets.get("BACKEND_URL", DEFAULT_BACKEND).rstrip("/")

def auth_headers() -> dict:
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

def handle_unauthorized(resp) -> bool:
    if resp is not None and resp.status_code == 401:
        st.session_state["token"] = None
        st.error("Token inválido / sesión expirada. Volvé a Home y logueate de nuevo.")
        return True
    return False

def api_request(method: str, path: str, **kwargs):
    url = f"{get_backend_url()}{path}"
    headers = kwargs.pop("headers", {})
    headers = {**headers, **auth_headers()}
    timeout = kwargs.pop("timeout", 30)

    try:
        return requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
    except Exception as e:
        st.error(f"Error conexión ({method}): {e}")
        return None

def api_get(path: str, **kwargs):
    return api_request("GET", path, **kwargs)

def api_post(path: str, **kwargs):
    return api_request("POST", path, **kwargs)

def api_put(path: str, **kwargs):
    return api_request("PUT", path, **kwargs)

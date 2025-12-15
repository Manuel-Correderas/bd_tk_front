import requests
import streamlit as st

DEFAULT_BACKEND = "http://127.0.0.1:8001"

def get_backend_url() -> str:
    # usa BACKEND_URL en secrets (Streamlit Cloud) o cae al default
    return st.secrets.get("BACKEND_URL", DEFAULT_BACKEND).rstrip("/")

def auth_headers() -> dict:
    t = st.session_state.get("token")
    return {"x-token": t} if t else {}

def safe_json(resp: requests.Response):
    try:
        return resp.json()
    except Exception:
        return None

def show_http_error(resp: requests.Response, default="Error"):
    data = safe_json(resp)
    detail = data.get("detail") if isinstance(data, dict) else None
    st.error(detail or f"{default}: {resp.status_code} - {resp.text}")

def api_get(path: str, *, params=None, timeout=20):
    url = f"{get_backend_url()}{path}"
    try:
        r = requests.get(url, headers=auth_headers(), params=params, timeout=timeout)
        return r
    except Exception as e:
        st.error(f"Error conexión (GET): {e}")
        return None

def api_post(path: str, *, json=None, files=None, timeout=30):
    url = f"{get_backend_url()}{path}"
    try:
        r = requests.post(url, headers=auth_headers(), json=json, files=files, timeout=timeout)
        return r
    except Exception as e:
        st.error(f"Error conexión (POST): {e}")
        return None

def api_put(path: str, *, json=None, timeout=30):
    url = f"{get_backend_url()}{path}"
    try:
        r = requests.put(url, headers=auth_headers(), json=json, timeout=timeout)
        return r
    except Exception as e:
        st.error(f"Error conexión (PUT): {e}")
        return None

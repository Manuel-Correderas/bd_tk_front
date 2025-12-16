# BD_TK_FRONT/utils/api.py
import requests
import streamlit as st

def backend_url() -> str:
    return st.secrets.get("BACKEND_URL", "http://127.0.0.1:8001").rstrip("/")

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

def _request(method: str, path: str, timeout: int = 20, **kwargs):
    url = f"{backend_url()}{path}"

    # headers default + merge
    hdrs = auth_headers()
    if "headers" in kwargs and isinstance(kwargs["headers"], dict):
        hdrs.update(kwargs["headers"])
    kwargs["headers"] = hdrs

    if "timeout" in kwargs:
        timeout = kwargs.pop("timeout")

    try:
        return requests.request(method, url, timeout=timeout, **kwargs)
    except Exception as e:
        st.error(f"Error conexión ({method}): {e}")
        return None


def api_get(path: str, **kwargs):
    return _request("GET", path, **kwargs)

def api_post(path: str, **kwargs):
    return _request("POST", path, **kwargs)

def api_put(path: str, **kwargs):
    return _request("PUT", path, **kwargs)

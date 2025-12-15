import requests
import streamlit as st

def backend_url() -> str:
    return st.secrets.get("BACKEND_URL", "http://127.0.0.1:8001").rstrip("/")

def auth_headers() -> dict:
    t = st.session_state.get("token")
    return {"x-token": t} if t else {}

def safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return None

def raise_or_show(resp, default_msg="Error"):
    if resp is None:
        st.error(f"{default_msg}: no se pudo conectar al backend.")
        st.stop()
    if resp.status_code >= 400:
        data = safe_json(resp)
        detail = data.get("detail") if isinstance(data, dict) else None
        st.error(detail or f"{default_msg}: {resp.status_code} - {resp.text}")
        st.stop()
    return resp

def api_get(path: str, *, params=None, timeout=20):
    url = f"{backend_url()}{path}"
    try:
        r = requests.get(url, headers=auth_headers(), params=params, timeout=timeout)
        raise_or_show(r, f"GET {path}")
        return safe_json(r)
    except Exception as e:
        st.error(f"Error conexión GET {path}: {e}")
        return None

def api_post(path: str, *, json=None, files=None, timeout=30):
    url = f"{backend_url()}{path}"
    try:
        r = requests.post(url, headers=auth_headers(), json=json, files=files, timeout=timeout)
        raise_or_show(r, f"POST {path}")
        return safe_json(r)
    except Exception as e:
        st.error(f"Error conexión POST {path}: {e}")
        return None

def api_put(path: str, *, json=None, timeout=30):
    url = f"{backend_url()}{path}"
    try:
        r = requests.put(url, headers=auth_headers(), json=json, timeout=timeout)
        raise_or_show(r, f"PUT {path}")
        return safe_json(r)
    except Exception as e:
        st.error(f"Error conexión PUT {path}: {e}")
        return None

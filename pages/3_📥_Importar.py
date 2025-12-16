# pages/3_📥_Importar.py
import streamlit as st
from utils.api import api_get, api_post, api_put, auth_headers, show_http_error, safe_json

st.set_page_config(page_title="Importar", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None

st.title("📥 Importar personas (CSV o Excel)")

if not st.session_state.get("token"):
    st.warning("No estás logueado. Volvé a Home y hacé login.")
    st.stop()

st.info(
    "Subí el archivo y el backend se encarga de: crear nuevas por DNI y "
    "actualizar existentes completando datos/meses sin duplicar."
)

up = st.file_uploader("Cargar archivo", type=["csv", "xls", "xlsx"])

if st.button("Importar archivo"):
    if up is None:
        st.warning("Primero cargá un archivo.")
    else:
        files = {"file": (up.name, up.getvalue(), up.type or "application/octet-stream")}
        r = api_post("/import-personas", files=files, timeout=300)
        if r is None:
            st.stop()
        if handle_unauthorized(r):
            st.stop()
        if r.status_code == 200:
            data = r.json() if r.headers.get("content-type","").startswith("application/json") else {}
            st.success((data or {}).get("detail", "Importación OK"))
            st.rerun()
        else:
            show_http_error(r, "Importación fallida")

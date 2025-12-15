# pages/2_👤_Crear_Editar.py
import streamlit as st
from utils.api import api_post, api_put, show_http_error, handle_unauthorized

st.set_page_config(page_title="Crear/Editar", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None

st.title("👤 Crear / Editar Persona")

if not st.session_state.get("token"):
    st.warning("No estás logueado. Volvé a Home y hacé login.")
    st.stop()

modo = st.radio("Modo", ["Crear nueva", "Editar por ID"], horizontal=True)

nombre = st.text_input("Nombre")
apellido = st.text_input("Apellido")
telefono = st.text_input("Teléfono")
dnis_text = st.text_input("DNIs (separados por coma)", placeholder="12345678, 23456789")
dnis_list = [{"dni": d.strip()} for d in (dnis_text or "").split(",") if d.strip()]

payload = {
    "nombre": (nombre or "").strip(),
    "apellido": (apellido or "").strip(),
    "telefono": (telefono or "").strip(),
    "dnis": dnis_list,
}

if modo == "Crear nueva":
    if st.button("Crear persona"):
        if not payload["nombre"] or not payload["apellido"]:
            st.error("Nombre y apellido son obligatorios")
        elif not payload["dnis"]:
            st.error("Debe ingresar al menos un DNI")
        else:
            r = api_post("/persons", json=payload, timeout=30)
            if r is None:
                st.stop()
            if handle_unauthorized(r):
                st.stop()
            if r.status_code in (200, 201):
                st.success("OK (creada o actualizada por DNI)")
                st.rerun()
            else:
                show_http_error(r, "No se pudo crear")
else:
    person_id = st.number_input("ID de la persona", min_value=1, step=1)
    if st.button("Actualizar persona"):
        if not payload["nombre"] or not payload["apellido"]:
            st.error("Nombre y apellido son obligatorios")
        elif not payload["dnis"]:
            st.error("Debe ingresar al menos un DNI")
        else:
            r = api_put(f"/persons/{int(person_id)}", json=payload, timeout=30)
            if r is None:
                st.stop()
            if handle_unauthorized(r):
                st.stop()
            if r.status_code == 200:
                st.success("Persona actualizada")
                st.rerun()
            else:
                show_http_error(r, "No se pudo actualizar")

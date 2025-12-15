# pages/1_📋_Listado.py
import pandas as pd
import requests
import streamlit as st

BACKEND_URL = st.secrets.get("BACKEND_URL", "http://127.0.0.1:8001").rstrip("/")
PAGE_SIZE = 50

st.set_page_config(page_title="Listado", layout="wide")

if "token" not in st.session_state:
    st.session_state["token"] = None
if "page" not in st.session_state:
    st.session_state["page"] = 0

def auth_headers():
    t = st.session_state.get("token")
    return {"x-token": t} if t else {}

def safe_json(resp: requests.Response):
    try:
        return resp.json()
    except Exception:
        return None

def handle_unauthorized(resp: requests.Response) -> bool:
    if resp.status_code == 401:
        st.session_state["token"] = None
        st.error("Token inválido / sesión expirada. Volvé a Home y logueate de nuevo.")
        return True
    return False

def show_http_error(resp: requests.Response, default="Error"):
    data = safe_json(resp)
    detail = data.get("detail") if isinstance(data, dict) else None
    st.error(detail or f"{default}: {resp.status_code} - {resp.text}")

def request_get(url: str, **kwargs):
    try:
        return requests.get(url, **kwargs)
    except Exception as e:
        st.error(f"Error conexión (GET): {e}")
        return None

def request_put(url: str, **kwargs):
    try:
        return requests.put(url, **kwargs)
    except Exception as e:
        st.error(f"Error conexión (PUT): {e}")
        return None

st.title("📋 Listado de Personas")

if not st.session_state.get("token"):
    st.warning("No estás logueado. Volvé a Home y hacé login.")
    st.stop()

q = (st.text_input(
    "Buscar por nombre, apellido o DNI",
    placeholder="Ej: Juan, Pérez, 30111222",
    key="list_search",
) or "").strip()

persons = []

if q:
    r = request_get(
        f"{BACKEND_URL}/persons/search",
        headers=auth_headers(),
        params={"q": q, "limit": 50},
        timeout=20,
    )
    if r is None:
        st.stop()
    if handle_unauthorized(r):
        st.stop()
    if r.status_code != 200:
        show_http_error(r, "No se pudo buscar")
        st.stop()
    persons = r.json() or []
    st.caption(f"Resultados: {len(persons)} (máx 50)")
else:
    skip = st.session_state["page"] * PAGE_SIZE
    r = request_get(
        f"{BACKEND_URL}/persons",
        headers=auth_headers(),
        params={"skip": skip, "limit": PAGE_SIZE},
        timeout=20,
    )
    if r is None:
        st.stop()
    if handle_unauthorized(r):
        st.stop()
    if r.status_code != 200:
        show_http_error(r, "No se pudo obtener listado")
        st.stop()
    persons = r.json() or []

    col_prev, col_mid, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅ Anterior", disabled=(st.session_state["page"] == 0), key="prev_page"):
            st.session_state["page"] -= 1
            st.rerun()
    with col_mid:
        st.caption(f"Página {st.session_state['page'] + 1} — mostrando {len(persons)} registros")
    with col_next:
        if st.button("Siguiente ➡", disabled=(len(persons) < PAGE_SIZE), key="next_page"):
            st.session_state["page"] += 1
            st.rerun()

if not persons:
    st.info("No hay resultados.")
    st.stop()

rows = [{
    "ID": p.get("id"),
    "Nombre": p.get("nombre", ""),
    "Apellido": p.get("apellido", ""),
    "Teléfono": p.get("telefono", "") or "",
    "DNIs": ", ".join(d.get("dni", "") for d in (p.get("dnis") or []) if d.get("dni")),
} for p in persons]

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

st.divider()
st.subheader("🗓 Observaciones por mes (abrí una persona)")

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

for p in persons:
    pid = p.get("id")
    titulo = f"{p.get('nombre','')} {p.get('apellido','')} (ID {pid})"

    with st.expander(titulo):
        st.write("**DNIs:**", ", ".join(d.get("dni","") for d in (p.get("dnis") or [])))
        st.write("**Teléfono:**", p.get("telefono", "") or "")

        obs = p.get("observations") or []
        obs_by_month = {o.get("month"): (o.get("text") or "") for o in obs if o.get("month")}

        edited = []
        for m in range(1, 13):
            existing_text = (obs_by_month.get(m) or "").strip()
            default_checked = bool(existing_text)

            c1, c2 = st.columns([1, 3])
            with c1:
                chk = st.checkbox(f"{MESES[m]} ✔", value=default_checked, key=f"chk_{pid}_{m}")
            with c2:
                txt = st.text_area(f"Detalle {MESES[m]}", value=existing_text, key=f"txt_{pid}_{m}")

            final_text = "" if (not chk and not (txt or "").strip()) else (txt or "")
            edited.append({"month": m, "text": final_text})

        if st.button("Guardar observaciones", key=f"save_obs_{pid}"):
            r = request_put(
                f"{BACKEND_URL}/persons/{pid}/observations",
                json=edited,
                headers=auth_headers(),
                timeout=30,
            )
            if r is None:
                st.stop()
            if handle_unauthorized(r):
                st.stop()
            if r.status_code == 200:
                st.success("Observaciones actualizadas")
                st.rerun()
            else:
                show_http_error(r, "No se pudo guardar observaciones")

import streamlit as st
import requests

st.set_page_config(page_title="Cobertura OneDrive", page_icon="📁")

st.title("📁 Archivos en Carpeta 'Cobertura' – OneDrive Personal (Siempre actualizado)")

# ---------------- CONFIG ----------------
cfg = st.secrets["onedrive"]
CLIENT_ID = cfg["client_id"]
CLIENT_SECRET = cfg["client_secret"]
REFRESH_TOKEN = cfg["refresh_token"]
REDIRECT_URI = cfg["redirect_uri"]

def get_access_token():
    url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token",
        "redirect_uri": REDIRECT_URI,
        "scope": "Files.ReadWrite Files.Read.All User.Read offline_access"
    }
    r = requests.post(url, data=data)
    return r.json()

def list_files(access_token):
    url = "https://graph.microsoft.com/v1.0/me/drive/root:/Cobertura:/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers)
    return r.json()

# ---------------- CONSULTA AUTOMÁTICA ----------------

token = get_access_token()

if "access_token" not in token:
    st.error("❌ Error obteniendo access_token")
    st.code(token)
else:
    st.success("Archivos actualizados ✔️")
    files = list_files(token["access_token"])

    if "value" in files:
        for item in files["value"]:
            st.write(f"📄 **{item['name']}** — `{item['lastModifiedDateTime']}`")
    else:
        st.error("No se pudieron leer los archivos")
        st.code(files)


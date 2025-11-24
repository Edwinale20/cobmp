import streamlit as st
import requests

st.set_page_config(page_title="Cobertura OneDrive", page_icon="📁")

st.title("📁 Archivos en Carpeta 'Cobertura' – OneDrive Personal")

CLIENT_ID = st.secrets["client_id"]
CLIENT_SECRET = st.secrets["client_secret"]
REFRESH_TOKEN = st.secrets["refresh_token"]
REDIRECT_URI = st.secrets["redirect_uri"]

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

if st.button("🔄 Actualizar lista"):
    token_data = get_access_token()
    if "access_token" not in token_data:
        st.error("❌ Error al obtener access_token")
        st.code(token_data)
    else:
        files = list_files(token_data["access_token"])
        st.success("Lista actualizada ✔️")
        st.write(files)

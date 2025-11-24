import streamlit as st
import requests
          
# ==========================
# 1. Cargar secretos
# ==========================
CLIENT_ID = st.secrets["onedrive"]["client_id"]
CLIENT_SECRET = st.secrets["onedrive"]["client_secret"]
REFRESH_TOKEN = st.secrets["onedrive"]["refresh_token"]
REDIRECT_URI = st.secrets["onedrive"]["redirect_uri"]
      
# ==========================
# 2. Función – obtener access_token desde refresh_token
# ==========================
def get_access_token():

    token_url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"

    data = {
        "client_id": CLIENT_ID,
        "scope": "Files.ReadWrite.All offline_access",
        "refresh_token": REFRESH_TOKEN,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "refresh_token",
        "client_secret": CLIENT_SECRET,
    }

    r = requests.post(token_url, data=data)

    if r.status_code != 200:
        st.error("❌ Error al obtener access_token")
        st.write(r.text)
        return None
    
    return r.json()["access_token"]
  
# ==========================
# 3. Listar archivos de carpeta "Cobertura"
# ==========================
def listar_archivos():
    access_token = get_access_token()
    if not access_token:
        return
    
    # IMPORTANTE: la URL usa /drive/root:/NOMBRECARPETA:/
    url = "https://graph.microsoft.com/v1.0/me/drive/root:/Cobertura:/children"

    headers = {"Authorization": f"Bearer {access_token}"}

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        st.error("❌ Error al listar archivos")
        st.write(r.text)
        return

    items = r.json().get("value", [])

    st.success("Archivos encontrados en la carpeta 'Cobertura':")
    for item in items:
        st.write("- ", item["name"])
  
# ==========================
# UI
# ==========================
st.title("📂 Archivos en Carpeta 'Cobertura' – OneDrive Personal")

if st.button("🔄 Actualizar lista"):
    listar_archivos()

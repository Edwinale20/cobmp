import streamlit as st
import requests

st.set_page_config(page_title="Coberturas Marca Propia", page_icon="🏪")

st.title("🏪 Cobertura de marca propia")
st.markdown("✅ Datos en tiempo real", unsafe_allow_html=True)
st.markdown("🧮 KPI´s principales", unsafe_allow_html=True)

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
#---------------------------------------------------------------------

def list_excel_files(access_token):
    url = "https://graph.microsoft.com/v1.0/me/drive/root:/Cobertura:/children"
    headers = {"Authorization": f"Bearer {access_token}"}
    r = requests.get(url, headers=headers).json()

    excel_files = [
        f for f in r.get("value", [])
        if f["name"].lower().endswith(".xlsx")
    ]
    return excel_files


def download_excel_df(access_token, file_id):
    """Descarga un Excel de OneDrive y lo devuelve como DataFrame."""
    url = f"https://graph.microsoft.com/v1.0/me/drive/items/{file_id}/content"
    headers = {"Authorization": f"Bearer {access_token}"}
    content = requests.get(url, headers=headers).content
    return pd.read_excel(io.BytesIO(content))


def venta(venta_semanal):
    concat_venta = pd.DataFrame()

    for df2 in venta_semanal:   # ⬅️ antes era xlsx_file
        try:
            # Ya NO se hace pd.read_excel(xlsx_file) aquí
            # Porque df2 YA ES el DataFrame descargado de OneDrive

            if 'Semana Contable' not in df2.columns:
                print(f"Advertencia: La columna 'Semana Contable' no existe en un archivo.")
                continue
            
            df2['Semana Contable'] = df2['Semana Contable'].astype(str)

            concat_venta = pd.concat([concat_venta, df2], ignore_index=True)

        except Exception as e:
            print(f"Error procesando archivo: {e}")
    
    if 'Semana Contable' in concat_venta.columns:
        cols2 = ['Semana Contable'] + [c for c in concat_venta.columns if c not in ['Semana Contable']]
        concat_venta = concat_venta[cols2]

    columnas_a_eliminar = [col for col in concat_venta.columns if 'Unnamed' in col] + ['Metrics']
    concat_venta = concat_venta.drop(columns=columnas_a_eliminar, errors='ignore')

    concat_venta['Mercado'] = concat_venta['Mercado'].astype(float).astype(int).astype(str)
    concat_venta['Artículo'] = concat_venta['Artículo'].astype(float).astype(int).astype(str)
    concat_venta['Semana Contable'] = concat_venta['Semana Contable'].astype(str)
    concat_venta['Unidades inventario'] = concat_venta['Unidades inventario'].astype('int64')

    concat_venta = concat_venta.rename(columns={
        'Artículo': 'ARTICULO',
        'División': 'DIVISION',
        'Plaza': 'PLAZA',
        'Mercado': 'MERCADO',
    })

    return concat_venta

access_token = get_access_token()
files = list_excel_files(access_token)

venta_semanal = []   # ahora es una lista de DataFrames, no rutas

for f in files:
    df = download_excel_df(access_token, f["id"])
    venta_semanal.append(df)


VENTA = venta(venta_semanal)
st.dataframe(VENTA, use_container_width=True)

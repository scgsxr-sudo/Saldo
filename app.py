import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="Il Mio Saldo Sicuro", page_icon="💰", layout="wide")

# --- CONFIGURAZIONE GOOGLE SHEETS ---
SHEET_ID = "1nWcJ6rwNGRDGLzYItDvXF7Evn5rRMckjavU6uMD2HcQ"
url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"

def carica_dati():
    try:
        # Leggiamo il CSV dal link pubblico di Google
        df_sheet = pd.read_csv(url)
        # Pulizia colonne e date
        df_sheet.columns = [c.strip() for c in df_sheet.columns]
        df_sheet['Data'] = pd.to_datetime(df_sheet['Data'], dayfirst=True, errors='coerce')
        return df_sheet.dropna(subset=['Data'])
    except Exception as e:
        return pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Importo', 'Nota'])

df = carica_dati()

st.title("💰 Saldo Permanente (Google Sheets)")

# --- CALCOLO SALDO ---
if not df.empty:
    # Convertiamo Importo in numero se non lo è
    df['Importo'] = pd.to_numeric(df['Importo'], errors='coerce').fillna(0)
    
    entrate = df[df['Tipo'].str.contains('Entrata', case=False, na=False)]['Importo'].sum()
    uscite = df[df['Tipo'].str.contains('Uscita', case=False, na=False)]['Importo'].sum()
    saldo_totale = entrate - uscite

    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate Totali", f"{entrate:.2f} €")
    c2.metric("Uscite Totali", f"-{uscite:.2f} €")
    c3.metric("SALDO ATTUALE", f"{saldo_totale:.2f} €", delta=f"{saldo_totale:.2f} €")
else:
    st.warning("Il foglio Google sembra vuoto o non accessibile. Verifica le intestazioni!")

# --- CALENDARIO ---
st.subheader("📅 Vista Mensile")
events = []
for i, row in df.iterrows():
    tipo = str(row['Tipo']).strip()
    color = "#5cb85c" if "Entrata" in tipo else "#d9534f"
    prefix = "+" if "Entrata" in tipo else "-"
    
    events.append({
        "title": f"{prefix}{row['Importo']}€ ({row['Categoria']})",
        "start": row['Data'].strftime("%Y-%m-%d"),
        "backgroundColor": color,
        "borderColor": color
    })

calendar(events=events, options={"initialView": "dayGridMonth"})

# --- ISTRUZIONI PER SALVARE ---
st.divider()
with st.expander("ℹ️ Come aggiungere nuovi dati senza perderli"):
    st.write("""
    Per far sì che i dati rimangano salvati per sempre, inseriscili direttamente nel tuo **Google Sheets**:
    1. Apri il tuo link di Google Sheets.
    2. Aggiungi una riga con: **Data** (es. 25/12/2023), **Tipo** (Entrata o Uscita), **Categoria**, **Importo** e **Nota**.
    3. Torna qui e ricarica la pagina dell'app: il saldo e il calendario si aggiorneranno da soli!
    """)






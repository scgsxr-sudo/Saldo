import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="Mio Saldo Calendar", page_icon="📅", layout="wide")

# --- DATABASE ---
DB_FILE = "dati_portafoglio.csv"
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Data'])
else:
    df = pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Importo', 'Nota'])

st.title("📅 Calendario Finanziario")

# --- COLONNA SINISTRA: INSERIMENTO | COLONNA DESTRA: CALENDARIO ---
col_input, col_cal = st.columns([1, 2])

with col_input:
    st.subheader("➕ Nuovo Movimento")
    with st.form("form_inserimento", clear_on_submit=True):
        importo = st.number_input("Importo (€)", min_value=0.0, step=1.0)
        tipo = st.selectbox("Tipo", ["Entrata", "Uscita"])
        data_scelta = st.date_input("Data", datetime.now())
        cat = st.selectbox("Categoria", ["Spesa", "Stipendio", "Casa", "Svago", "Altro"])
        nota = st.text_input("Nota")
        if st.form_submit_button("Registra"):
            nuova_riga = pd.DataFrame([[data_scelta.strftime('%d/%m/%Y'), tipo, cat, importo, nota]], 
                                      columns=['Data', 'Tipo', 'Categoria', 'Importo', 'Nota'])
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.success("Salvato!")
            st.rerun()

with col_cal:
    # Trasformiamo i dati in eventi per il calendario
    calendar_events = []
    for i, row in df.iterrows():
        colore = "#28a745" if row['Tipo'] == "Entrata" else "#dc3545"
        prefix = "+" if row['Tipo'] == "Entrata" else "-"
        calendar_events.append({
            "title": f"{prefix}{row['Importo']}€ ({row['Categoria']})",
            "start": row['Data'].strftime("%Y-%m-%d"),
            "backgroundColor": colore,
            "borderColor": colore
        })

    # Visualizzazione Calendario
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,dayGridWeek"
        },
        "initialView": "dayGridMonth",
    }
    
    calendar(events=calendar_events, options=calendar_options)

# --- RIEPILOGO IN BASSO ---
st.divider()
saldo = df[df['Tipo'] == 'Entrata']['Importo'].sum() - df[df['Tipo'] == 'Uscita']['Importo'].sum()
st.metric("SALDO TOTALE", f"{saldo:.2f} €")


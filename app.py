import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="Saldo Calendar", page_icon="📅", layout="wide")

DB_FILE = "dati_portafoglio.csv"

# --- CARICAMENTO DATI ---
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['Data'])
else:
    df = pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Importo', 'Nota'])

st.title("📅 Mio Calendario Spese")

# --- INSERIMENTO ---
with st.expander("➕ Aggiungi Movimento"):
    with st.form("nuovo", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        d = col1.date_input("Data", datetime.now())
        t = col2.selectbox("Tipo", ["Uscita", "Entrata"])
        i = col3.number_input("Euro €", min_value=0.0)
        c = st.selectbox("Categoria", ["Spesa", "Stipendio", "Casa", "Svago", "Altro"])
        n = st.text_input("Nota")
        if st.form_submit_button("Salva"):
            nuova_riga = pd.DataFrame([[d.strftime('%d/%m/%Y'), t, c, i, n]], 
                                      columns=['Data', 'Tipo', 'Categoria', 'Importo', 'Nota'])
            df = pd.concat([df, nuova_riga], ignore_index=True)
            df.to_csv(DB_FILE, index=False)
            st.rerun()

# --- PREPARA EVENTI ---
events = []
for index, row in df.iterrows():
    color = "#d9534f" if row['Tipo'] == "Uscita" else "#5cb85c"
    events.append({
        "id": str(index),
        "title": f"{row['Importo']}€ {row['Categoria']}",
        "start": row['Data'].strftime("%Y-%m-%d"),
        "backgroundColor": color,
    })

# --- VISUALIZZA CALENDARIO ---
cal = calendar(events=events, options={"initialView": "dayGridMonth"}, key="cal")

# --- CANCELLAZIONE ---
if cal.get("eventClick"):
    idx = int(cal["eventClick"]["event"]["id"])
    mov = df.iloc[idx]
    st.error(f"Vuoi eliminare: {mov['Importo']}€ per {mov['Categoria']}?")
    if st.button("SÌ, ELIMINA"):
        df = df.drop(df.index[idx])
        df.to_csv(DB_FILE, index=False)
        st.rerun()

# --- SALDO ---
st.divider()
saldo = df[df['Tipo'] == 'Entrata']['Importo'].sum() - df[df['Tipo'] == 'Uscita']['Importo'].sum()
st.sidebar.metric("SALDO TOTALE", f"{saldo:.2f} €")
if not df.empty:
    st.sidebar.write("### Ultimi Movimenti")
    st.sidebar.dataframe(df.tail(5), hide_index=True)




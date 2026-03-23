import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configurazione pagina
st.set_page_config(page_title="Mio Saldo", page_icon="💰")

DB_FILE = "dati_portafoglio.csv"

# Caricamento dati
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True).dt.date
else:
    df = pd.DataFrame(columns=['Data', 'Tipo', 'Importo', 'Nota'])

st.title("💰 Gestore Saldo")

# --- INSERIMENTO ---
with st.expander("➕ Aggiungi Movimento"):
    with st.form("form_inserimento", clear_on_submit=True):
        importo = st.number_input("Importo (€)", min_value=0.0, step=1.0)
        tipo = st.selectbox("Tipo", ["Entrata", "Uscita"])
        nota = st.text_input("Nota")
        data_scelta = st.date_input("Data", datetime.now())
        submit = st.form_submit_button("Registra")

if submit:
    nuova_riga = pd.DataFrame([[data_scelta.strftime('%d/%m/%Y'), tipo, importo, nota]], 
                              columns=['Data', 'Tipo', 'Importo', 'Nota'])
    df = pd.concat([df, nuova_riga], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.success("Registrato!")
    st.rerun()

# --- VISUALIZZAZIONE ---
st.subheader("Filtra per Giorno")
giorno_filtro = st.date_input("Scegli una data", datetime.now())
dati_giorno = df[df['Data'] == giorno_filtro] if not df.empty else df

if not dati_giorno.empty:
    st.table(dati_giorno)

st.divider()
entrate_tot = df[df['Tipo'] == 'Entrata']['Importo'].sum()
uscite_tot = df[df['Tipo'] == 'Uscita']['Importo'].sum()
st.metric("SALDO TOTALE", f"{entrate_tot - uscite_tot:.2f} €")

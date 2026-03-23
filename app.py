import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Il Mio Saldo", page_icon="💰")

DB_FILE = "dati_portafoglio.csv"

# Carica dati
if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
else:
    df = pd.DataFrame(columns=['Data', 'Tipo', 'Importo', 'Nota'])

st.title("💰 Gestore Saldo")

# Inserimento
with st.form("form_inserimento", clear_on_submit=True):
    importo = st.number_input("Importo (€)", min_value=0.0, step=1.0)
    tipo = st.selectbox("Tipo", ["Entrata", "Uscita"])
    nota = st.text_input("Nota")
    submit = st.form_submit_button("Registra")

if submit:
    nuova_riga = pd.DataFrame([[datetime.now().strftime("%d/%m/%Y"), tipo, importo, nota]], 
                              columns=['Data', 'Tipo', 'Importo', 'Nota'])
    df = pd.concat([df, nuova_riga], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.success("Registrato!")
    st.rerun()

# Saldo e Tabella
entrate = df[df['Tipo'] == 'Entrata']['Importo'].sum()
uscite = df[df['Tipo'] == 'Uscita']['Importo'].sum()
st.metric("SALDO ATTUALE", f"{entrate - uscite:.2f} €")
st.dataframe(df.iloc[::-1], use_container_width=True) # Mostra gli ultimi sopra

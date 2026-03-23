import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

st.set_page_config(page_title="Il Mio Saldo", page_icon="💰", layout="wide")

# Connessione al foglio usando i Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# CARICAMENTO DATI (ttl=0 serve per non avere ritardi nel vedere i dati nuovi)
df = conn.read(ttl=0)
df.columns = [c.strip().lower() for c in df.columns]

st.title("💰 Gestione Saldo Smart")

# --- MASCHERA DI INSERIMENTO ---
with st.expander("➕ Aggiungi una spesa o un'entrata"):
    with st.form("nuovo_inserimento"):
        col1, col2 = st.columns(2)
        data_ins = col1.date_input("Data", datetime.now())
        tipo_ins = col2.selectbox("Tipo", ["Entrata", "Uscita"])
        cat_ins = st.selectbox("Categoria", ["Stipendio", "Spesa", "Casa", "Svago", "Altro"])
        imp_ins = st.number_input("Importo (€)", min_value=0.0, step=0.01)
        nota_ins = st.text_input("Nota")
        
        if st.form_submit_button("REGISTRA"):
            # Creiamo la nuova riga con i nomi colonne corretti
            nuova_riga = pd.DataFrame([{
                "data": data_ins.strftime('%d/%m/%Y'),
                "tipo": tipo_ins,
                "categoria": cat_ins,
                "importo": imp_ins,
                "nota": nota_ins
            }])
            
            # Aggiungiamo la riga al database esistente
            df_finale = pd.concat([df, nuova_riga], ignore_index=True)
            
            # AGGIORNIAMO IL FOGLIO GOOGLE
            conn.update(data=df_finale)
            st.success("Dato salvato correttamente!")
            st.rerun()

# --- CALCOLO SALDO ---
if not df.empty:
    df['importo'] = pd.to_numeric(df['importo'], errors='coerce').fillna(0)
    entrate = df[df['tipo'].str.lower() == 'entrata']['importo'].sum()
    uscite = df[df['tipo'].str.lower() == 'uscita']['importo'].sum()
    saldo = entrate - uscite

    c1, c2, c3 = st.columns(3)
    c1.metric("Entrate", f"{entrate:.2f} €")
    c2.metric("Uscite", f"-{uscite:.2f} €")
    c3.metric("SALDO ATTUALE", f"{saldo:.2f} €")

    # CALENDARIO
    st.subheader("📅 Storico Movimenti")
    events = []
    for _, row in df.iterrows():
        try:
            color = "#5cb85c" if row['tipo'].lower() == "entrata" else "#d9534f"
            events.append({
                "title": f"{row['importo']}€ ({row['categoria']})",
                "start": pd.to_datetime(row['data'], dayfirst=True).strftime("%Y-%m-%d"),
                "backgroundColor": color,
                "borderColor": color
            })
        except:
            continue
    
    calendar(events=events, options={"initialView": "dayGridMonth"})
else:
    st.warning("Nessun dato trovato nel foglio Google.")









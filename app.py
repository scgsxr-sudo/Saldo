import streamlit as st
import pandas as pd
import os
from datetime import datetime
from streamlit_calendar import calendar
from st_annotated_text import annotated_text

st.set_page_config(page_title="Gestione Saldo Pro", page_icon="📅", layout="wide")

DB_FILE = "dati_portafoglio.csv"

# --- FUNZIONI DATI ---
def carica_dati():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        df['Data'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        return df.dropna(subset=['Data'])
    return pd.DataFrame(columns=['Data', 'Tipo', 'Categoria', 'Importo', 'Nota'])

def salva_dati(df):
    df.to_csv(DB_FILE, index=False)

df = carica_dati()

st.title("📅 Calendario Finanziario Interattivo")

# --- LAYOUT: NUOVO INSERIMENTO ---
with st.expander("➕ Inserisci una nuova Entrata o Uscita", expanded=False):
    with st.form("nuovo_movimento", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        data_m = c1.date_input("Data", datetime.now())
        tipo_m = c2.selectbox("Tipo", ["Uscita", "Entrata"])
        importo_m = c3.number_input("Importo (€)", min_value=0.0, step=1.0)
        
        c4, c5 = st.columns(2)
        cat_m = c4.selectbox("Categoria", ["Spesa", "Affitto/Casa", "Stipendio", "Svago", "Trasporti", "Salute", "Altro"])
        nota_m = c5.text_input("Nota (opzionale)")
        
        if st.form_submit_button("Salva nel Calendario"):
            nuova_riga = pd.DataFrame([[data_m.strftime('%d/%m/%Y'), tipo_m, cat_m, importo_m, nota_m]], 
                                      columns=['Data', 'Tipo', 'Categoria', 'Importo', 'Nota'])
            df = pd.concat([df, nuova_riga], ignore_index=True)
            salva_dati(df)
            st.success("Registrato!")
            st.rerun()

# --- PREPARAZIONE EVENTI CALENDARIO ---
calendar_events = []
for i, row in df.iterrows():
    color = "#d9534f" if row['Tipo'] == "Uscita" else "#5cb85c"
    calendar_events.append({
        "id": i,
        "title": f"{'-' if row['Tipo']=='Uscita' else '+'}{row['Importo']}€ {row['Categoria']}",
        "start": row['Data'].strftime("%Y-%m-%d"),
        "color": color,
        "nota": row['Nota']
    })

# --- CALENDARIO ---
st.subheader("I tuoi movimenti")
cal_output = calendar(events=calendar_events, options={
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,dayGridWeek"},
    "initialView": "dayGridMonth",
    "selectable": True,
}, key="financial_cal")

# --- LOGICA DI ELIMINAZIONE ---
# Se clicchi su un evento nel calendario
if cal_output.get("eventClick"):
    event_id = int(cal_output["eventClick"]["event"]["id"])
    movimento = df.iloc[event_id]
    
    st.warning(f"Vuoi eliminare questo movimento? **{movimento['Tipo']} di {movimento['Importo']}€ ({movimento['Categoria']})**")
    if st.button("Sì, elimina definitivamente"):
        df = df.drop(df.index[event_id])
        salva_dati(df)
        st.success("Eliminato!")
        st.rerun()

# --- RIEPILOGO E TABELLA ---
st.divider()
entrate = df[df['Tipo'] == 'Entrata']['Importo'].sum()
uscite = df[df['Tipo'] == 'Uscita']['Importo'].sum()

col_s1, col_s2, col_s3 = st.columns(3)
col_s1.metric("Totale Entrate", f"{entrate} €")
col_s2.metric("Totale Uscite", f"{uscite} €", delta=f"-{uscite}", delta_color="inverse")
col_s3.metric("SALDO ATTUALE", f"{entrate - uscite:.2f} €")

if not df.empty:
    with st.expander("📂 Lista completa movimenti (Tabella)"):
        st.dataframe(df.sort_values(by='Data', ascending=False), use_container_width=True)



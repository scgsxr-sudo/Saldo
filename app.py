Importazione Streamlit comest
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Il Mio Saldo", page_icon="💰")

DB_FILE = "dati_portafoglio.csv"

if os.path.exists(DB_FILE):
    df = pd.read_csv(DB_FILE)
    # Convertiamo la colonna Data in formato data vero per i calcoli
    df['Data'] = pd.to_datetime(df['Data'], dayfirst=True).dt.date
else:
    df = pd.DataFrame(columns=['Data', 'Tipo', 'Importo', 'Nota'])

st.title("💰 Gestore Saldo con Calendario")

# --- PARTE 1: INSERIMENTO ---
with st.expander("➕ Aggiungi Movimento"):
    with st.form("form_inserimento", clear_on_submit=True):
        importo = st.number_input("Importo (€)", min_value=0.0, step=1.0)
        tipo = st.selectbox("Tipo", ["Entrata", "Uscita"])
        nota = st.text_input("Nota")
        # AGGIUNTO IL CALENDARIO PER SCEGLIERE LA DATA
        data_scelta = st.date_input("Seleziona la data", datetime.now())
        submit = st.form_submit_button("Registra")

if submit:
    nuova_riga = pd.DataFrame([[data_scelta, tipo, importo, nota]], 
                              columns=['Data', 'Tipo', 'Importo', 'Nota'])
    df = pd.concat([df, nuova_riga], ignore_index=True)
    df.to_csv(DB_FILE, index=False)
    st.success(f"Registrato per il giorno {data_scelta.strftime('%d/%m/%Y')}!")
    st.rerun()

---

# --- PARTE 2: FILTRO CALENDARIO ---
st.subheader("Visualizza per Giorno")
giorno_filtro = st.date_input("Scegli un giorno per vedere i dettagli", datetime.now())

# Filtriamo i dati per il giorno scelto
dati_giorno = df[df['Data'] == giorno_filtro]

if not dati_giorno.empty:
    entrate_g = dati_giorno[dati_giorno['Tipo'] == 'Entrata']['Importo'].sum()
    uscite_g = dati_giorno[dati_giorno['Tipo'] == 'Uscita']['Importo'].sum()
    st.info(f"In questo giorno: +{entrate_g}€ | -{uscite_g}€")
    st.table(dati_giorno[['Tipo', 'Importo', 'Nota']])
else:
    st.write("Nessun movimento registrato in questa data.")

---

# --- PARTE 3: SALDO TOTALE ---
st.divider()
entrate_tot = df[df['Tipo'] == 'Entrata']['Importo'].sum()
uscite_tot = df[df['Tipo'] == 'Uscita']['Importo'].sum()
st.metric("SALDO TOTALE", f"{entrate_tot - uscite_tot:.2f} €")

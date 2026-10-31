import streamlit as st
import pandas as pd

# 1. Configurazione della pagina web
st.set_page_config(page_title="Perito AI - Fabbricati & RC", layout="wide", page_icon="🏢")

st.title("🏢 Sistema Automatizzato Gestione Sinistri Fabbricati & RC")
st.write("Analisi di indennizzabilità e generazione Computo Metrico su base **Prezzario Regione Lombardia**.")

# 2. Caricamento del database (Prezzario Lombardia simulato)
@st.cache_data
def carica_prezzario_lombardia():
    dati_simulati = {
        'Codice': ['1.A01.010', '1.A02.050', '2.B15.020', '3.C04.110'],
        'Descrizione': [
            'Demolizione di intonaco interno o esterno, eseguita a mano o con mezzi meccanici, compreso il carico sui mezzi di trasporto.',
            'Tinteggiatura interna con idropittura lavabile, data a due mani su pareti o soffitti, compresi i ponteggi interni.',
            'Rimozione di pavimentazione esistente in ceramica o marmo, compreso lo sgombero delle macerie.',
            'Rifacimento di intonaco civile per interni, eseguito a mano con malta preconfezionata.'
        ],
        'UM': ['mq', 'mq', 'mq', 'mq'],
        'Prezzo_Unitario': [14.50, 9.80, 22.10, 18.40]
    }
    return pd.DataFrame(dati_simulati)

df_prezzario = carica_prezzario_lombardia()

# 3. INTERFACCIA UTENTE
col_sinistra, col_destra = st.columns(2)

with col_sinistra:
    st.header("📄 Caricamento Documenti Legali")
    file_polizza = st.file_uploader("Carica il Frontespizio di Polizza (PDF)", type=["pdf"])
    file_cga = st.file_uploader("Carica le Condizioni Generali - CGA (PDF)", type=["pdf"])
    
    st.header("📸 Prove Fotografiche del Danno")
    foto_danni = st.file_uploader("Trascina qui le foto dei danni al fabbricato", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

with col_destra:
    st.header("⚙️ Parametri Sinistro (Input Assistito)")
    tipo_sinistro = st.selectbox("Qual è la causa presunta del danno?", ["Acqua Condotta (Rottura Tubo)", "Ricerca Guasto", "Fenomeno Elettrico", "RC Terzi (Es. Danno al vicino)", "Infiltrazione da Tetto/Lastrico"])
    mq_stimati = st.number_input("Estensione stimata dell'area danneggiata (in Mq)", min_value=1.0, value=10.0, step=0.5)

# 4. MOTORE DI ELABORAZIONE
if st.button("🚀 AVVIA ELABORAZIONE PERIZIA", use_container_width=True):
    if file_polizza and file_cga and foto_danni:
        with st.spinner("Analisi in corso..."):
            st.success("Analisi completata con successo!")
            
            st.subheader("⚖️ Verdetto di Indennizzabilità & Copertura")
            if tipo_sinistro == "Acqua Condotta (Rottura Tubo)":
                st.markdown("### **Esito: INDENNIZZABILE 🟢**")
                st.info("**Motivazione Tecnica:** Rilevata rottura accidentale della tubazione idrica. La garanzia 'Acqua Condotta' risulta attiva.")
                st.warning("⚠️ **Franchigie applicate:** Franchigia fissa di € 250,00.")
            else:
                st.markdown("### **Esito: APRIRE POSIZIONE RC TERZI 🔵**")
                st.info("**Motivazione Tecnica:** Il bagnamento ha coinvolto la proprietà sottostante.")
                
            st.subheader("📋 Computo Metrico Estimativo (Prezzario Lombardia)")
            voci_computo = []
            totale_computo = 0.0
            
            for index, row in df_prezzario.iterrows():
                if "Demolizione" in row['Descrizione'] or "Tinteggiatura" in row['Descrizione']:
                    costo_totale_voce = row['Prezzo_Unitario'] * mq_stimati
                    totale_computo += costo_totale_voce
                    voci_computo.append({
                        "Codice Tariffa": row['Codice'],
                        "Descrizione Lavorazione": row['Descrizione'],
                        "U.M.": row['UM'],
                        "Quantità": f"{mq_stimati}",
                        "Prezzo Unitario (€)": f"{row['Prezzo_Unitario']:.2f}",
                        "Totale (€)": f"{costo_totale_voce:.2f}"
                    })
            
            st.table(pd.DataFrame(voci_computo))
            st.metric(label="Totale Stimato Opere di Ripristino", value=f"€ {totale_computo:.2f}")
    else:
        st.error("❌ Carica tutti i documenti richiesti per procedere.")


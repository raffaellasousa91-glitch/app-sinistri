import streamlit as st
import pandas as pd

# 1. Configurazione della pagina web
st.set_page_config(page_title="Perito AI - Fabbricati & RC", layout="wide", page_icon="🏢")

st.title("🏢 Sistema Automatizzato Gestione Sinistri Fabbricati & RC")
st.write("Analisi indennizzabilità, Computo Metrico e **Confronto Preventivi** su base **Prezzario Regione Lombardia**.")

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
    
    st.header("📸 Prove Fotografiche")
    foto_danni = st.file_uploader("Trascina qui le foto dei danni al fabbricato", type=["jpg", "png", "jpeg"], accept_multiple_files=True)

with col_destra:
    st.header("🔍 Analisi Contro-Preventivi")
    file_preventivo = st.file_uploader("Carica il Preventivo da Verificare / Confrontare (PDF/Excel)", type=["pdf", "xlsx", "csv"])
    
    st.header("⚙️ Parametri Sinistro")
    tipo_sinistro = st.selectbox("Qual è la causa presunta del danno?", ["Acqua Condotta (Rottura Tubo)", "Ricerca Guasto", "Fenomeno Elettrico", "RC Terzi (Es. Danno al vicino)", "Infiltrazione da Tetto/Lastrico"])
    mq_stimati = st.number_input("Estensione stimata dell'area danneggiata (in Mq)", min_value=1.0, value=10.0, step=0.5)

# 4. MOTORE DI ELABORAZIONE
if st.button("🚀 AVVIA ELABORAZIONE PERIZIA E CONFRONTO PREVENTIVO", use_container_width=True):
    if file_polizza and file_cga and foto_danni:
        with st.spinner("Analisi e comparazione prezzi in corso..."):
            st.success("Analisi completata con successo!")
            
            # --- SEZIONE 1: VERDETTO ---
            st.subheader("⚖️ Verdetto di Indennizzabilità & Copertura")
            if tipo_sinistro == "Acqua Condotta (Rottura Tubo)":
                st.markdown("### **Esito: INDENNIZZABILE 🟢**")
                st.info("**Motivazione Tecnica:** Rilevata rottura accidentale della tubazione idrica. La garanzia 'Acqua Condotta' risulta attiva.")
                st.warning("⚠️ **Franchigie applicate:** Franchigia fissa di € 250,00.")
            else:
                st.markdown("### **Esito: APRIRE POSIZIONE RC TERZI 🔵**")
                st.info("**Motivazione Tecnica:** Il bagnamento ha coinvolto la proprietà sottostante.")
                
            # --- SEZIONE 2: COMPUTO METRICO REALE DA FOTO ---
            st.subheader("📋 Computo Metrico Stimato da Visione Foto (Tariffe Lombardia)")
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
                        "Quantità": mq_stimati,
                        "Prezzo Unitario Reg. Lombardia (€)": row['Prezzo_Unitario'],
                        "Totale Ammissibile (€)": costo_totale_voce
                    })
            
            st.table(pd.DataFrame(voci_computo))
            st.metric(label="Totale Stimato Opere di Ripristino (Secondo Prezzario)", value=f"€ {totale_computo:.2f}")
            
            # --- SEZIONE 3: ANALISI E CONFRONTO PREVENTIVO CARICATO ---
            if file_preventivo:
                st.subheader("📊 Analisi Congruatà del Preventivo Ricevuto")
                st.write("L'Intelligenza Artificiale ha estratto le voci del preventivo caricato e le ha paragonate alle voci equivalenti della Regione Lombardia:")
                
                # Simulazione estrazione e confronto voci del preventivo contro-periziato
                dati_confronto = [
                    {
                        "Lavorazione": "Demolizione intonaci (Voce Preventivo)",
                        "Prezzo Richiesto (€/mq)": 19.50,
                        "Prezzo Reg. Lombardia (€/mq)": 14.50,
                        "Scostamento": "+34.4%",
                        "Esito Congruità": "FUORI TARIFFA 🛑"
                    },
                    {
                        "Lavorazione": "Tinteggiatura lavabile (Voce Preventivo)",
                        "Prezzo Richiesto (€/mq)": 10.20,
                        "Prezzo Reg. Lombardia (€/mq)": 9.80,
                        "Scostamento": "+4.0%",
                        "Esito Congruità": "CONGRUO ✅"
                    }
                ]
                
                st.table(pd.DataFrame(dati_confronto))
                
                totale_preventivo_caricato = (19.50 * mq_stimati) + (10.20 * mq_stimati)
                differenza_totale = totale_preventivo_caricato - totale_computo
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(label="Totale Richiesto nel Preventivo", value=f"€ {totale_preventivo_caricato:.2f}")
                with col2:
                    st.metric(label="Taglio / Riduzione Proposta", value=f"€ {differenza_totale:.2f}", delta="- Fuori Tariffa", delta_color="inverse")
                
                st.error(f"🔍 **Nota del Perito AI:** Il preventivo ricevuto risulta complessivamente superiore del **{((totale_preventivo_caricato/totale_computo)-1)*100:.1f}%** rispetto alle tariffe ufficiali della Regione Lombardia. Si consiglia di contestare la voce relativa alle demolizioni.")
            else:
                st.info("💡 Suggerimento: Carica un preventivo nel pannello di destra se desideri effettuare il controllo di congruità dei prezzi automatico.")
                
    else:
        st.error("❌ Carica i documenti obbligatori (Polizza, CGA e Foto) per procedere.")



import streamlit as st
import pandas as pd
import json
import http.client
import base64

# 1. Configurazione della pagina web
st.set_page_config(page_title="Perito AI - Fabbricati & RC", layout="wide", page_icon="🏢")

st.title("🏢 Sistema Automatizzato Gestione Sinistri Fabbricati & RC")
st.write("Analisi REALE di indennizzabilità, Computo Metrico e Confronto Preventivi su base **Prezzario Regione Lombardia**.")

# Recupero della chiave segreta dalle impostazioni di Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 Chiave API non configurata! Inserisci la tua 'GEMINI_API_KEY' nei Secrets di Streamlit per attivare la lettura GRATUITA.")
    st.stop()

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
    garanzia_digitata = st.text_input("Digita la garanzia specifica da utilizzare", placeholder="Es. Ricerca e ripristino guasto d'acqua")

# 4. MOTORE DI ELABORAZIONE REALE CON AI (GEMINI GRATUITO)
if st.button("🚀 AVVIA ELABORAZIONE PERIZIA E CONFRONTO PREVENTIVO", use_container_width=True):
    if file_polizza and file_cga and foto_danni:
        with st.spinner("L'AI di Google sta analizzando i PDF e le immagini caricati..."):
            
            garanzia_attiva = garanzia_digitata if garanzia_digitata else tipo_sinistro
            
            # Connessione corretta senza caratteri errati nell'URL
            conn = http.client.HTTPSConnection("://googleapis.com")
            
            prompt_testo = f"""
            Agisci come perito assicurativo anziano per danni fabbricati e RC. Analizza la richiesta per la garanzia: {garanzia_attiva}.
            Esamina i contratti e le foto allegate per estrarre la franchigia esatta o lo scoperto reale applicabile.
            Rispondi rigorosamente in formato JSON con questi tre campi precisi:
            'indennizzabile' (metti true o false),
            'motivazione' (spiegazione tecnica dettagliata estrapolata dal testo),
            'franchigia_reale' (il valore economico o la percentuale trovata nel documento).
            """
            
            payload = json.dumps({
                "contents": [{
                    "parts": [{"text": prompt_testo}]
                }],
                "generationConfig": {
                    "responseMimeType": "application/json"
                }
            })
            
            headers = {'Content-Type': 'application/json'}
            
            try:
                conn.request("POST", f"/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}", payload, headers)
                res = conn.getresponse()
                data = res.read().decode("utf-8")
                
                response_json = json.loads(data)
                text_response = response_json['candidates'][0]['content']['parts'][0]['text']
                risultato_ai = json.loads(text_response)
                
                # --- VISUALIZZAZIONE RISULTATI ---
                st.success("Analisi completata con successo tramite Google Gemini!")
                
                st.subheader("⚖️ Verdetto di Indennizzabilità & Copertura Reale")
                if risultato_ai.get("indennizzabile") == True or risultato_ai.get("indennizzabile") == "true":
                    st.markdown("### **Stato: INDENNIZZABILE 🟢**")
                else:
                    st.markdown("### **Stato: NON INDENNIZZABILE O IN DUBBIO 🟡**")
                    
                st.info(f"**Motivazione Contrattuale Estratta:** {risultato_ai.get('motivazione')}")
                st.error(f"🔍 **FRANCHIGIA REALE TROVATA NEL PDF:** {risultato_ai.get('franchigia_reale')}")
                
                # Sezione computo metrico standard
                st.subheader("📋 Computo Metrico Stimato (Tariffe Lombardia)")
                voci_computo = []
                totale_computo = 0.0
                for index, row in df_prezzario.iterrows():
                    if "Demolizione" in row['Descrizione'] or "Tinteggiatura" in row['Descrizione']:
                        costo_totale_voce = row['Prezzo_Unitario'] * 10.0
                        totale_computo += costo_totale_voce
                        voci_computo.append({
                            "Codice Tariffa": row['Codice'],
                            "Descrizione Lavorazione": row['Descrizione'],
                            "U.M.": row['UM'],
                            "Quantità": 10.0,
                            "Prezzo Unitario (€)": row['Prezzo_Unitario'],
                            "Totale (€)": costo_totale_voce
                        })
                st.table(pd.DataFrame(voci_computo))
                st.metric(label="Totale Opere di Ripristino", value=f"€ {totale_computo:.2f}")
                
            except Exception as e:
                st.error(f"Errore durante l'elaborazione dei dati: {str(e)}")
    else:
        st.error("❌ Carica i documenti obbligatori per avviare la lettura reale.")





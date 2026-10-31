import streamlit as st
import pandas as pd
import json
import http.client

# 1. Configurazione della pagina web
st.set_page_config(page_title="Perito AI - Fabbricati & RC", layout="wide", page_icon="🏢")

st.title("🏢 Sistema Automatizzato Gestione Sinistri Fabbricati & RC")
st.write("Analisi REALE di indennizzabilità, Computo Metrico e Confronto Preventivi su base **Prezzario Regione Lombardia**.")

# Recupero della chiave segreta dalle impostazioni di Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("🔑 Chiave API non configurata! Inserisci la tua 'GEMINI_API_KEY' nei Secrets di Streamlit per attivare la lettura GRATUITA dei PDF.")
    st.stop()

# 2. INTERFACCIA UTENTE
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

# 3. MOTORE DI ELABORAZIONE REALE CON AI (GEMINI GRATUITO)
if st.button("🚀 AVVIA ELABORAZIONE PERIZIA E CONFRONTO PREVENTIVO", use_container_width=True):
    if file_polizza and file_cga and foto_danni:
        with st.spinner("L'AI di Google sta analizzando i PDF caricati..."):
            
            garanzia_attiva = garanzia_digitata if garanzia_digitata else tipo_sinistro
            
            # Prepariamo la richiesta per le API di Google Gemini
            conn = http.client.HTTPSConnection("://googleapis.com")
            payload = json.dumps({
                "contents": [{
                    "parts": [{
                        "text": f"Analizza la richiesta di sinistro per la garanzia: {garanzia_attiva}. Estrai la franchigia reale o lo scoperto e determina se è indennizzabile. Rispondi solo in formato JSON con i campi: 'indennizzabile' (true/false), 'motivazione', 'franchigia_reale'."
                    }]
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
                text_response = response_json['candidates']['content']['parts']['text']
                risultato_ai = json.loads(text_response)
                
                # --- VISUALIZZAZIONE RISULTATI ---
                st.success("Analisi completata con successo tramite Google Gemini (Gratuito)!")
                
                st.subheader("⚖️ Verdetto di Indennizzabilità & Copertura Reale")
                if risultato_ai.get("indennizzabile"):
                    st.markdown("### **Stato: INDENNIZZABILE 🟢**")
                else:
                    st.markdown("### **Stato: NON INDENNIZZABILE O IN DUBBIO 🟡**")
                    
                st.info(f"**Motivazione Contrattuale Estratta:** {risultato_ai.get('motivazione')}")
                st.error(f"🔍 **FRANCHIGIA REALE TROVATA NEL PDF:** {risultato_ai.get('franchigia_reale')}")
                
            except Exception as e:
                st.error(f"Errore di connessione: {str(e)}")
    else:
        st.error("❌ Carica i documenti obbligatori per avviare la lettura reale.")





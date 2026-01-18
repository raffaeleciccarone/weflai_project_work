#!/usr/bin/env python
import sys
import os

# Aggiungo la directory corrente al path per importare i moduli locali se necessario
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Optional
from pydantic import BaseModel, Field
from crewai.flow.flow import Flow, listen, start, router # <--- Aggiunto router

# IMPORTIAMO LE TUE CREW REALI (Assicurati che i file esistano)
# Se sono nella stessa cartella:
try:
    from booking_crew import BookingCrew
    from cancellation_crew import CancellationCrew
except ImportError:
    # Fallback per mostrare l'errore se i file non sono pronti
    print("ERRORE CRITICO: Assicurati di avere 'booking_crew.py' e 'cancellation_crew.py' nella stessa cartella.")
    BookingCrew = None
    CancellationCrew = None

# --- DEFINIZIONE DELLO STATO ---

class TicketOutput(BaseModel):
    # Ho reso i campi Optional per evitare crash se il LLM fallisce una estrazione parziale
    partenza_iata: Optional[str] = Field(None, description="Codice IATA aeroporto partenza")
    partenza_citta: Optional[str] = Field(None, description="Città di partenza")
    arrivo_iata: Optional[str] = Field(None, description="Codice IATA aeroporto arrivo")
    arrivo_citta: Optional[str] = Field(None, description="Città di arrivo")
    nome_compagnia: Optional[str] = Field(None, description="Nome della compagnia aerea")
    data_volo: Optional[str] = Field(None, description="Data del volo YYYY-MM-DD")
    orario_partenza: Optional[str] = Field(None, description="HH:MM")
    orario_arrivo: Optional[str] = Field(None, description="HH:MM")
    nome_passeggero: Optional[str] = Field(None, description="Nome del passeggero")
    cognome_passeggero: Optional[str] = Field(None, description="Cognome del passeggero")
    qr_code_path: Optional[str] = Field(None, description="Path locale del file QR code generato")

class AirportState(BaseModel):
    # Ho rinominato user_input in 'query' per matchare l'input del kickoff
    query: str = "" 
    operation_type: str = "" # "booking", "cancellation"
    final_output: Optional[str] = None

# --- DEFINIZIONE DEL FLOW ---

# Passiamo AirportState come type parameter al Flow
class AirportFlow(Flow[AirportState]):

    @start()
    def determine_intent(self):
        # Accediamo allo stato tipizzato
        user_query = self.state.query.lower()
        
        print(f"🔄 [ROUTER] Analisi Intento per: '{user_query}'")
        
        # Logica di routing semplice
        if any(word in user_query for word in ["cancell", "elimina", "rimuovi", "disdici"]):
            self.state.operation_type = "cancellation"
        else:
            self.state.operation_type = "booking"
            
        return self.state.operation_type

    @router(determine_intent)
    def route_request(self):
        # Il router legge il return value della funzione precedente (determine_intent)
        # o controlla lo stato. Qui usiamo il return value.
        op_type = self.state.operation_type
        
        if op_type == "booking":
            return "run_booking_crew"
        elif op_type == "cancellation":
            return "run_cancellation_crew"
        
        # Fallback
        return "run_booking_crew"

    @listen("run_booking_crew")
    def run_booking_crew(self):
        print("✈️  [FLOW] Avvio Booking Crew...")
        
        if not BookingCrew: return "Errore: Classe BookingCrew non trovata"

        # Prepariamo l'input per la Crew
        inputs = {"query": self.state.query}
        
        # KICKOFF
        # Nota: La crew restituisce un oggetto CrewOutput, prendiamo .raw
        result = BookingCrew().crew().kickoff(inputs=inputs)
        
        # Salviamo il risultato nello stato
        self.state.final_output = result.raw
        return result.raw

    @listen("run_cancellation_crew")
    def run_cancellation_crew(self):
        print("🗑️  [FLOW] Avvio Cancellation Crew...")
        
        if not CancellationCrew: return "Errore: Classe CancellationCrew non trovata"

        inputs = {"query": self.state.query}
        
        # KICKOFF
        result = CancellationCrew().crew().kickoff(inputs=inputs)
        
        self.state.final_output = result.raw
        return result.raw

# --- ESECUZIONE ---

if __name__ == "__main__":
    import asyncio
    
    # Esempio 1: Prenotazione
    print("\n--- TEST FLOW: PRENOTAZIONE ---")
    flow_booking = AirportFlow()
    # Passiamo 'query' che matcha il campo nel modello Pydantic AirportState
    final_response = flow_booking.kickoff(inputs={"query": "Vorrei prenotare un volo da Roma a Milano per domani per Mario Rossi"})
    
    print("\n✅ RISULTATO FINALE FLOW:")
    print(final_response)

    # Esempio 2: Cancellazione (Decommentare per testare)
    # print("\n--- TEST FLOW: CANCELLAZIONE ---")
    # flow_cancel = AirportFlow()
    # final_response_cancel = flow_cancel.kickoff(inputs={"query": "Voglio cancellare la prenotazione di Mario Rossi"})
    # print("\n✅ RISULTATO FINALE FLOW:")
    # print(final_response_cancel)
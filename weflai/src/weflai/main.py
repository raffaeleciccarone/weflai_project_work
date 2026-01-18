# weflai/main.py
import sys
import os

# CrewAI Flow Imports
from crewai.flow.flow import Flow, listen, start, router

# Project Imports
from weflai.models import WeFlaiState
from weflai.crews.booking_crew.booking_crew import BookingCrew
from weflai.crews.cancellation_crew.cancellation_crew import CancellationCrew

class WeFlaiFlow(Flow[WeFlaiState]):

    @start()
    def get_user_intent(self):
        print("\n" + "="*40)
        print("✈️  WEFLAI SYSTEM v1.0 - DATABASE AGENT ✈️")
        print("="*40)
        print("1. Nuova Prenotazione")
        print("2. Cancellazione Prenotazione")
        print("3. Esci")
        
        choice = input("\nSeleziona operazione (1-3): ").strip()
        
        if choice == "1":
            self.state.user_intent = "booking"
            print("\n📝 Esempio: 'Volo Roma Milano domani mattina per Mario Rossi'")
            self.state.user_query = input("La tua richiesta: ")
        elif choice == "2":
            self.state.user_intent = "cancellation"
            print("\n🗑️  Esempio: 'Cancella la prenotazione di Mario Rossi per Milano'")
            self.state.user_query = input("La tua richiesta: ")
        else:
            self.state.user_intent = "exit"

    @router(get_user_intent)
    def route_request(self):
        return self.state.user_intent

    @listen("booking")
    def handle_booking(self):
        print(f"\n🚀 Avvio Booking Crew per: '{self.state.user_query}'")
        try:
            # Kickoff della Crew
            result = BookingCrew().crew().kickoff(inputs={"query": self.state.user_query})
            
            # Controllo se abbiamo un oggetto Pydantic (successo)
            if result.pydantic:
                self.state.final_ticket = result.pydantic
                print("\n" + "✅"*20)
                print(" BIGLIETTO EMESSO CON SUCCESSO ")
                print("✅"*20)
                print(self.state.final_ticket.model_dump_json(indent=4))
                
                # Opzionale: salvataggio manuale se non gestito dal task
                with open("ticket_finale.json", "w") as f:
                    f.write(self.state.final_ticket.model_dump_json(indent=4))
                    
            else:
                # Caso in cui la Crew restituisce testo (es. "Volo non trovato")
                print("\n⚠️  RISULTATO:", result.raw)
                
        except Exception as e:
            print(f"\n❌ ERRORE CRITICO DURANTE LA PRENOTAZIONE: {e}")

    @listen("cancellation")
    def handle_cancellation(self):
        print(f"\n🗑️  Avvio Cancellation Crew per: '{self.state.user_query}'")
        try:
            result = CancellationCrew().crew().kickoff(inputs={"query": self.state.user_query})
            print("\n✅ ESITO OPERAZIONE:")
            print(result.raw)
        except Exception as e:
            print(f"\n❌ ERRORE CANCELLAZIONE: {e}")

    @listen("exit")
    def handle_exit(self):
        print("\n👋 Arrivederci!")

def kickoff():
    """Entry point per l'esecuzione"""
    flow = WeFlaiFlow()
    flow.kickoff()

if __name__ == "__main__":
    kickoff()
#!/usr/bin/env python
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
from weflai.src.weflai.crews.flight_crew.Weflai_crew import PoemCrew
from pydantic import BaseModel, Field
from typing import Optional

class TicketOutput(BaseModel):
    partenza_iata: str = Field(..., description="Codice IATA aeroporto partenza")
    partenza_citta: str = Field(..., description="Città di partenza")
    arrivo_iata: str = Field(..., description="Codice IATA aeroporto arrivo")
    arrivo_citta: str = Field(..., description="Città di arrivo")
    nome_compagnia: str = Field(..., description="Nome della compagnia aerea")
    data_volo: str = Field(..., description="Data del volo YYYY-MM-DD")
    orario_partenza: str = Field(..., description="HH:MM")
    orario_arrivo: str = Field(..., description="HH:MM")
    nome_passeggero: str = Field(..., description="Nome del passeggero")
    cognome_passeggero: str = Field(..., description="Cognome del passeggero")
    qr_code_path: Optional[str] = Field(None, description="Path locale del file QR code generato")

class BookingState(BaseModel):
    user_input: str = ""
    operation_type: str = "" # "BOOK", "CANCEL", "INFO"
    sql_query_result: Optional[str] = None
    ticket_details: Optional[TicketOutput] = None
    is_success: bool = False

#lele

class FlightCrew(Flow[TicketOutput]):




def kickoff():
    poem_flow = FlightCrew()
    poem_flow.kickoff()


def plot():
    poem_flow = FlightCrew()
    poem_flow.plot()





if __name__ == "__main__":
    kickoff()

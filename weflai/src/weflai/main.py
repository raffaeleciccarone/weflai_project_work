#!/usr/bin/env python
from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
from weflai.src.weflai.crews.flight_crew.Weflai_crew import flight_crew
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


class FlightCrew(Flow[TicketOutput]):

    @start()
    def generate_sentence_count(self, crewai_trigger_payload: dict = None):
        print("Generating sentence count")

        # Use trigger payload if available
        if crewai_trigger_payload:
            # Example: use trigger data to influence sentence count
            self.state.sentence_count = crewai_trigger_payload.get('sentence_count', randint(1, 5))
            print(f"Using trigger payload: {crewai_trigger_payload}")
        else:
            self.state.sentence_count = randint(1, 5)

    @listen(generate_sentence_count)
    def generate_poem(self):
        print("Generating poem")
        result = (
            PoemCrew()
            .crew()
            .kickoff(inputs={"sentence_count": self.state.sentence_count})
        )

        print("Poem generated", result.raw)
        self.state.poem = result.raw

    @listen(generate_poem)
    def save_poem(self):
        print("Saving poem")
        with open("poem.txt", "w") as f:
            f.write(self.state.poem)


def kickoff():
    poem_flow = FlightCrew()
    poem_flow.kickoff()


def plot():
    poem_flow = FlightCrew()
    poem_flow.plot()


def run_with_trigger():
    """
    Run the flow with trigger payload.
    """
    import json
    import sys

    # Get trigger payload from command line argument
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    # Create flow and kickoff with trigger payload
    # The @start() methods will automatically receive crewai_trigger_payload parameter
    flight_flow = FlightCrew()

    try:
        result = flight_flow.kickoff({"crewai_trigger_payload": trigger_payload})
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the flow with trigger: {e}")


if __name__ == "__main__":
    kickoff()

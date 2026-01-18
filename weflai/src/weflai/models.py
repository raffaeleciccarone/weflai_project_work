# weflai/models.py
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
import re
from datetime import datetime

class TicketOutput(BaseModel):
    """
    Modello Pydantic per il biglietto di volo.
    Contiene validazioni rigorose per garantire coerenza dei dati.
    """
    
    id_prenotazione: str = Field(
        ..., 
        description="ID della prenotazione (convertito a stringa)",
        examples=["123", "456"]
    )
    
    id_volo: int = Field(
        ..., 
        description="ID del volo (intero positivo)",
        gt=0
    )
    
    passeggero: str = Field(
        ..., 
        description="Nome e Cognome completo del passeggero",
        min_length=3
    )
    
    compagnia: str = Field(
        ..., 
        description="Nome della compagnia aerea",
        examples=["ITA Airways", "Ryanair", "easyJet"]
    )
    
    partenza_iata: str = Field(
        ..., 
        description="Codice IATA aeroporto di partenza (3 lettere maiuscole)",
        pattern=r"^[A-Z]{3}$"
    )
    
    arrivo_iata: str = Field(
        ..., 
        description="Codice IATA aeroporto di arrivo (3 lettere maiuscole)",
        pattern=r"^[A-Z]{3}$"
    )
    
    tratta: str = Field(
        ..., 
        description="Città Partenza - Città Arrivo",
        pattern=r"^.+ - .+$"
    )
    
    data: str = Field(
        ..., 
        description="Data del volo (formato YYYY-MM-DD)",
        pattern=r"^\d{4}-\d{2}-\d{2}$"
    )
    
    orario_partenza: str = Field(
        ..., 
        description="Orario di partenza (formato HH:MM)",
        pattern=r"^\d{2}:\d{2}(:\d{2})?$"
    )
    
    orario_arrivo: str = Field(
        ..., 
        description="Orario di arrivo (formato HH:MM)",
        pattern=r"^\d{2}:\d{2}(:\d{2})?$"
    )
    
    note: str = Field(
        default="Prenotazione confermata", 
        description="Note o stato della prenotazione"
    )
    
    # --- VALIDATORI ---
    
    @field_validator('id_prenotazione', mode='before')
    @classmethod
    def coerce_id_to_str(cls, v):
        if v is None: return ""
        return str(v)
    
    @field_validator('partenza_iata', 'arrivo_iata', mode='before')
    @classmethod
    def uppercase_iata(cls, v):
        if isinstance(v, str):
            return v.upper().strip()
        return v
    
    @field_validator('passeggero')
    @classmethod
    def validate_passeggero(cls, v):
        if not v or len(v.strip().split()) < 2:
            raise ValueError(f"Il passeggero deve avere 'Nome Cognome'. Ricevuto: {v}")
        return v.strip()
    
    @field_validator('data')
    @classmethod
    def validate_data_format(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
            return v
        except ValueError:
            raise ValueError(f"Data non valida: '{v}'. Richiesto YYYY-MM-DD.")
    
    @field_validator('orario_partenza', 'orario_arrivo')
    @classmethod
    def validate_orario_format(cls, v):
        # Supporta HH:MM:SS tagliando i secondi, o HH:MM
        if re.match(r"^\d{2}:\d{2}:\d{2}$", v):
            v = v[:5]
        
        if not re.match(r"^\d{2}:\d{2}$", v):
            raise ValueError(f"Orario non valido: '{v}'. Richiesto HH:MM.")
        return v
    
    @model_validator(mode='after')
    def validate_consistency(self):
        if self.partenza_iata == self.arrivo_iata:
            raise ValueError(f"Partenza e Arrivo coincidono ({self.partenza_iata}).")
        return self

class WeFlaiState(BaseModel):
    user_intent: str = ""
    user_query: str = ""
    final_ticket: Optional[TicketOutput] = None
# services/api_moteur/settings.py
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    rules_url: str = Field(default="http://rules-service:8081", alias="RULES_URL")
    kafka_bootstrap: str = Field(default="kafka:9092", alias="KAFKA_BOOTSTRAP")
    apicurio_url: str = Field(default="http://apicurio:8080", alias="APICURIO_URL")
    topic_evenements: str = Field(default="jeu-cabinet.evenements", alias="TOPIC_EVENEMENTS")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()


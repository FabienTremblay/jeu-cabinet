from pydantic_settings import BaseSettings


class CabinetCLISettings(BaseSettings):
    lobby_base_url: str = "http://lobby.cabinet.localhost"

    class Config:
        env_prefix = "CABINET_"


settings = CabinetCLISettings()

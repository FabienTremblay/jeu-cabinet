import httpx
from .settings import settings

async def evaluer_decision(table: str, contexte: dict) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.post(f"{settings.rules_url}/decisions/{table}", json={"contexte": contexte})
        r.raise_for_status()
        return r.json()

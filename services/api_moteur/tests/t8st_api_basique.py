from fastapi.testclient import TestClient
from services.api_moteur.app import app

client = TestClient(app)

def test_cycle_minimal():
    r = client.post("/moteur/v1/parties", json={"nom": "demo", "options": {}})
    assert r.status_code == 200
    partie_id = r.json()["partie_id"]

    r = client.post(f"/moteur/v1/parties/{partie_id}/joueurs", json={"joueur_id": "j1", "pseudo": "Alice"})
    assert r.status_code == 200

    r = client.get(f"/moteur/v1/parties/{partie_id}/etat")
    assert r.status_code == 200
    assert r.json()["etat"]

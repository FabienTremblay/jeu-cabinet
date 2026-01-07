import pytest
from services.cabinet.moteur.etat import ProgrammeTour


def _fake_entree(uid, carte_id, auteur_id="J1", type_="mesure"):
    # petit helper pour créer un objet ressemblant à EntreeProgramme
    return type(
        "E",
        (),
        {
            "uid": uid,
            "carte_id": carte_id,
            "auteur_id": auteur_id,
            "type": type_,
            "params": {},
            "tags": [],
        },
    )()


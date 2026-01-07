# services/cabinet/tests/conftest.py
import pytest
from services.cabinet.moteur.manager import PartieManager

@pytest.fixture
def pm():
    return PartieManager()

@pytest.fixture
def etat_minimal(pm):
    return pm.creer(
        skin="minimal",
        partie_id="T-001",
        joueurs={
            "J1": {"nom": "Alice"},
            "J2": {"nom": "Bob"},
        },
        seed=42,
    )

@pytest.fixture
def goto():
    """
    Petit utilitaire pour exécuter une sous-phase par son libellé de skin.
    Usage côté test: goto(pm, etat, "monde")
    """
    def _go(pm, etat, sp: str):
        etat._run_subphase(sp)
        return etat
    return _go

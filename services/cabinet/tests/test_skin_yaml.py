from pathlib import Path

import pytest

from services.cabinet.bre.skin_yaml import (
    charger_skin_yaml,
    diagnostic_heritage_minimal,
)


CHEMIN_OVERLAY = (
    Path(__file__).parents[3]
    / "donnees"
    / "cabinet"
    / "skins"
    / "exemples"
    / "exemple_mandat_austerite_overlay"
    / "skin.yaml"
)


def test_lit_un_skin_yaml_overlay_valide():
    skin = charger_skin_yaml(CHEMIN_OVERLAY)

    assert skin.skin_id == "exemple_mandat_austerite_overlay"
    assert skin.herite_de == "debut_mandat_bre"
    assert skin.nom == "Mandat d’austérité — overlay exemple"
    assert skin.version == "v1"
    assert skin.difficulte == "intermediaire"


def test_erreur_claire_si_skin_id_manque(tmp_path):
    chemin = tmp_path / "skin.yaml"
    chemin.write_text(
        """
skin:
  herite_de: debut_mandat_bre
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="skin.id"):
        charger_skin_yaml(chemin)


def test_erreur_claire_si_herite_de_manque_pour_overlay(tmp_path):
    chemin = tmp_path / "skin.yaml"
    chemin.write_text(
        """
skin:
  id: mandat_sans_parent
""",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="skin.herite_de"):
        charger_skin_yaml(chemin)


def test_diagnostic_heritage_minimal():
    diagnostic = diagnostic_heritage_minimal(charger_skin_yaml(CHEMIN_OVERLAY))

    assert diagnostic["skin_id"] == "exemple_mandat_austerite_overlay"
    assert diagnostic["herite_de"] == "debut_mandat_bre"
    assert diagnostic["declares"] == [
        "skin.id",
        "skin.herite_de",
        "skin.nom",
        "skin.version",
        "skin.difficulte",
        "presentation.pitch",
        "parametres.capital_politique_initial",
    ]
    assert diagnostic["herite"] == [
        "cartes",
        "evenements",
        "regles",
        "phases",
        "procedures",
    ]

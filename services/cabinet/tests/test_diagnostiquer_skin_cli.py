from pathlib import Path

from services.cabinet.outils.diagnostiquer_skin import (
    chemin_skin_yaml,
    formater_diagnostic_skin,
    main,
)
from services.cabinet.bre.skin_yaml import charger_skin_yaml


CHEMIN_OVERLAY = (
    Path(__file__).parents[1]
    / "skins"
    / "uat_mandat_austerite_overlay"
    / "skin.yaml"
)


def test_formate_un_diagnostic_lisible():
    sortie = formater_diagnostic_skin(charger_skin_yaml(CHEMIN_OVERLAY))

    assert "Skin : uat_mandat_austerite_overlay" in sortie
    assert "Nom : Mandat d’austérité — overlay UAT" in sortie
    assert "Version : v1" in sortie
    assert "Difficulté : intermediaire" in sortie
    assert "Hérite de : debut_mandat_bre" in sortie
    assert "- skin.id" in sortie
    assert "- parametres.capital_politique_initial" in sortie
    assert "- règles" in sortie
    assert "La fusion complète des familles héritées n’est pas encore implémentée." in sortie


def test_cli_fonctionne_avec_exemple_overlay(capsys):
    code = main(["--skin-yaml", str(CHEMIN_OVERLAY)])

    assert code == 0
    sortie = capsys.readouterr().out
    assert "Skin : uat_mandat_austerite_overlay" in sortie
    assert "Champs déclarés :" in sortie
    assert "Familles héritées :" in sortie


def test_cli_fonctionne_avec_identifiant_de_skin(capsys):
    assert chemin_skin_yaml("uat_mandat_austerite_overlay") == CHEMIN_OVERLAY

    code = main(["uat_mandat_austerite_overlay"])

    assert code == 0
    sortie = capsys.readouterr().out
    assert "Hérite de : debut_mandat_bre" in sortie


def test_cli_signale_un_skin_yaml_absent(capsys):
    code = main(["skin_introuvable"])

    assert code == 2
    erreur = capsys.readouterr().err
    assert "Erreur : skin.yaml introuvable:" in erreur


def test_cli_signale_un_skin_yaml_invalide(tmp_path, capsys):
    chemin = tmp_path / "skin.yaml"
    chemin.write_text("presentation:\n  pitch: Sans bloc skin\n", encoding="utf-8")

    code = main(["--skin-yaml", str(chemin)])

    assert code == 2
    erreur = capsys.readouterr().err
    assert "Le fichier skin.yaml doit contenir un bloc skin" in erreur

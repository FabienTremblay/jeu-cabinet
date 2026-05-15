from pathlib import Path

from services.cabinet.outils.diagnostiquer_skin import (
    chemin_skin_yaml,
    formater_diagnostic_skin,
    main,
    resumer_contenus_declaratifs,
)
from services.cabinet.bre.skin_yaml import charger_skin_yaml


CHEMIN_OVERLAY = (
    Path(__file__).parents[3]
    / "donnees"
    / "cabinet"
    / "skins"
    / "exemples"
    / "exemple_mandat_austerite_overlay"
    / "skin.yaml"
)
CHEMIN_OVERLAY_COUCHE_2 = (
    Path(__file__).parents[3]
    / "donnees"
    / "cabinet"
    / "skins"
    / "exemples"
    / "exemple_mandat_climat_overlay"
    / "skin.yaml"
)


def test_formate_un_diagnostic_lisible():
    sortie = formater_diagnostic_skin(charger_skin_yaml(CHEMIN_OVERLAY))

    assert "Skin : exemple_mandat_austerite_overlay" in sortie
    assert "Nom : Mandat d’austérité — overlay exemple" in sortie
    assert "Version : v1" in sortie
    assert "Difficulté : intermediaire" in sortie
    assert "Hérite de : debut_mandat_bre" in sortie
    assert "- skin.id" in sortie
    assert "- parametres.capital_politique_initial" in sortie
    assert "- règles" in sortie
    assert "- cartes.yaml : absent" in sortie
    assert "- evenements.yaml : absent" in sortie
    assert "- messages.yaml : absent" in sortie
    assert "La fusion complète des familles héritées n’est pas encore implémentée." in sortie
    assert "La publication résolue de la skin n’est pas encore implémentée." in sortie


def test_diagnostique_les_trois_fichiers_de_couche_2():
    sortie = formater_diagnostic_skin(charger_skin_yaml(CHEMIN_OVERLAY_COUCHE_2))

    assert "Skin : exemple_mandat_climat_overlay" in sortie
    assert "- cartes.yaml : présent" in sortie
    assert "  - hériter : true" in sortie
    assert "  - ajoutés : 1 (MES_TRANSITION_CLIMATIQUE)" in sortie
    assert "  - remplacés : 1 (MES_PLAN_SOCIAL)" in sortie
    assert "  - retirés : 1 (MES_BAISSE_IMPOTS)" in sortie
    assert "- evenements.yaml : présent" in sortie
    assert "  - ajoutés : 1 (EVT_CANICULE_HISTORIQUE)" in sortie
    assert "  - remplacés : 1 (EVT_CRITIQUE_OPPOSITION)" in sortie
    assert "  - retirés : 1 (EVT_SONDAGE_FAVORABLE)" in sortie
    assert "- messages.yaml : présent" in sortie
    assert "  - messages personnalisés : 2" in sortie
    assert "programme_ouvert" in sortie
    assert "capital_politique_insuffisant" in sortie


def test_diagnostique_cartes_yaml_seul(tmp_path):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "cartes.yaml").write_text(
        """
cartes:
  heriter: false
  ajouter:
    - id: MES_NOUVELLE
  remplacer:
    - id: MES_EXISTANTE
  retirer:
    - MES_RETIREE
""",
        encoding="utf-8",
    )

    resumes = resumer_contenus_declaratifs(tmp_path)

    cartes = resumes[0]
    assert cartes.present is True
    assert cartes.heriter is False
    assert cartes.ajoutes == ("MES_NOUVELLE",)
    assert cartes.remplaces == ("MES_EXISTANTE",)
    assert cartes.retires == ("MES_RETIREE",)
    assert resumes[1].present is False
    assert resumes[2].present is False


def test_diagnostique_evenements_yaml_seul(tmp_path):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "evenements.yaml").write_text(
        """
evenements:
  heriter: true
  ajouter:
    - id: EVT_NOUVEAU
  remplacer:
    - id: EVT_EXISTANT
  retirer:
    - EVT_RETIRE
""",
        encoding="utf-8",
    )

    resumes = resumer_contenus_declaratifs(tmp_path)

    evenements = resumes[1]
    assert evenements.present is True
    assert evenements.heriter is True
    assert evenements.ajoutes == ("EVT_NOUVEAU",)
    assert evenements.remplaces == ("EVT_EXISTANT",)
    assert evenements.retires == ("EVT_RETIRE",)
    assert resumes[0].present is False
    assert resumes[2].present is False


def test_diagnostique_messages_yaml_seul(tmp_path):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "messages.yaml").write_text(
        """
messages:
  accueil: Bienvenue.
  refus: Action refusée.
""",
        encoding="utf-8",
    )

    resumes = resumer_contenus_declaratifs(tmp_path)

    messages = resumes[2]
    assert messages.present is True
    assert messages.cles == ("accueil", "refus")
    assert resumes[0].present is False
    assert resumes[1].present is False


def test_cli_fonctionne_avec_exemple_overlay(capsys):
    code = main(["--skin-yaml", str(CHEMIN_OVERLAY)])

    assert code == 0
    sortie = capsys.readouterr().out
    assert "Skin : exemple_mandat_austerite_overlay" in sortie
    assert "Champs déclarés :" in sortie
    assert "Familles héritées :" in sortie


def test_cli_fonctionne_avec_exemple_couche_2(capsys):
    code = main(["exemple_mandat_climat_overlay"])

    assert code == 0
    sortie = capsys.readouterr().out
    assert "Skin : exemple_mandat_climat_overlay" in sortie
    assert "Contenus déclaratifs de couche 2 :" in sortie
    assert "- cartes.yaml : présent" in sortie
    assert "- evenements.yaml : présent" in sortie
    assert "- messages.yaml : présent" in sortie


def test_cli_fonctionne_avec_identifiant_de_skin(capsys):
    assert chemin_skin_yaml("exemple_mandat_austerite_overlay") == CHEMIN_OVERLAY

    code = main(["exemple_mandat_austerite_overlay"])

    assert code == 0
    sortie = capsys.readouterr().out
    assert "Hérite de : debut_mandat_bre" in sortie


def test_cli_resout_l_overlay_couche_2_via_catalogue(capsys):
    assert chemin_skin_yaml("exemple_mandat_climat_overlay") == CHEMIN_OVERLAY_COUCHE_2

    code = main(["exemple_mandat_climat_overlay"])

    assert code == 0
    sortie = capsys.readouterr().out
    assert "Skin : exemple_mandat_climat_overlay" in sortie
    assert "- cartes.yaml : présent" in sortie


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


def test_cli_signale_un_fichier_couche_2_invalide(tmp_path, capsys):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "cartes.yaml").write_text("cartes:\n  ajouter: MES_NOUVELLE\n", encoding="utf-8")

    code = main(["--skin-yaml", str(tmp_path / "skin.yaml")])

    assert code == 2
    erreur = capsys.readouterr().err
    assert "Les blocs ajouter, remplacer et retirer doivent contenir des listes" in erreur


def _ecrire_skin_yaml(dossier: Path) -> None:
    (dossier / "skin.yaml").write_text(
        """
skin:
  id: skin_test
  herite_de: debut_mandat_bre
  nom: Skin test
  version: v1
  difficulte: debutant
""",
        encoding="utf-8",
    )

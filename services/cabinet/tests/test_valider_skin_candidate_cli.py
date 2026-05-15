from pathlib import Path

from services.cabinet.outils.valider_skin_candidate import (
    OptionsValidation,
    chemin_skin_dir,
    formater_validation,
    main,
    valider_skin_candidate,
)


CHEMIN_OVERLAY_COUCHE_2 = (
    Path(__file__).parents[1]
    / "skins"
    / "exemple_mandat_climat_overlay"
)


def test_candidate_valide_minimale(capsys):
    code = main(["--skin-dir", str(CHEMIN_OVERLAY_COUCHE_2)])

    assert code == 0
    sortie = capsys.readouterr().out
    assert "Validation skin candidate : exemple_mandat_climat_overlay" in sortie
    assert "Statut : valide" in sortie
    assert "- aucune" in sortie
    assert "Cette commande valide la candidate sans publier la skin." in sortie


def test_cli_fonctionne_avec_identifiant_de_skin(capsys):
    assert chemin_skin_dir("exemple_mandat_climat_overlay") == CHEMIN_OVERLAY_COUCHE_2

    code = main(["exemple_mandat_climat_overlay"])

    assert code == 0
    sortie = capsys.readouterr().out
    assert "Statut : valide" in sortie


def test_marqueur_a_remplacer_detecte(tmp_path):
    _ecrire_skin_yaml(tmp_path, nom="A_REMPLACER_NOM_SKIN")

    validation = valider_skin_candidate(tmp_path)

    assert validation.valide is False
    assert "skin.yaml contient un marqueur A_REMPLACER_*" in validation.erreurs


def test_id_duplique_dans_ajouter(tmp_path):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "cartes.yaml").write_text(
        """
cartes:
  ajouter:
    - id: MES_DOUBLON
    - id: MES_DOUBLON
""",
        encoding="utf-8",
    )

    validation = valider_skin_candidate(tmp_path)

    assert validation.valide is False
    assert "cartes.yaml: id dupliqué dans ajouter: MES_DOUBLON" in validation.erreurs


def test_id_present_dans_ajouter_et_retirer(tmp_path):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "cartes.yaml").write_text(
        """
cartes:
  ajouter:
    - id: MES_CONFLIT
  retirer:
    - MES_CONFLIT
""",
        encoding="utf-8",
    )

    validation = valider_skin_candidate(tmp_path)

    assert validation.valide is False
    assert (
        "cartes.yaml: id présent dans ajouter et retirer: MES_CONFLIT"
        in validation.erreurs
    )


def test_section_inconnue_produit_un_avertissement(tmp_path):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "evenements.yaml").write_text(
        """
evenements:
  heriter: true
  autre_section:
    - id: EVT_INCONNU
""",
        encoding="utf-8",
    )

    validation = valider_skin_candidate(tmp_path)

    assert validation.valide is True
    assert (
        "evenements.yaml contient une section inconnue dans evenements: autre_section"
        in validation.avertissements
    )


def test_version_absente_produit_un_avertissement(tmp_path):
    (tmp_path / "skin.yaml").write_text(
        """
skin:
  id: skin_test
  herite_de: debut_mandat_bre
  nom: Skin test
  difficulte: debutant
""",
        encoding="utf-8",
    )

    validation = valider_skin_candidate(tmp_path)

    assert validation.valide is True
    assert "skin.version n’est pas déclarée" in validation.avertissements


def test_message_avec_cle_vide(tmp_path):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "messages.yaml").write_text(
        """
messages:
  "": Message sans clé.
""",
        encoding="utf-8",
    )

    validation = valider_skin_candidate(tmp_path)

    assert validation.valide is False
    assert "messages.yaml contient une clé de message vide" in validation.erreurs


def test_marqueur_a_remplacer_dans_messages_detecte(tmp_path):
    _ecrire_skin_yaml(tmp_path)
    (tmp_path / "messages.yaml").write_text(
        """
messages:
  accueil: A_REMPLACER_MESSAGE
""",
        encoding="utf-8",
    )

    validation = valider_skin_candidate(tmp_path)

    assert validation.valide is False
    assert "messages.yaml contient un marqueur A_REMPLACER_*" in validation.erreurs


def test_skin_id_incoherent_avec_le_dossier_si_verifie(tmp_path):
    dossier = tmp_path / "mauvais_dossier"
    dossier.mkdir()
    _ecrire_skin_yaml(dossier, skin_id="autre_id")

    validation = valider_skin_candidate(
        dossier,
        options=OptionsValidation(verifier_nom_dossier=True),
    )

    assert validation.valide is False
    assert "skin.id (autre_id) ne correspond pas au dossier (mauvais_dossier)" in validation.erreurs


def test_validation_par_montage_ne_force_pas_le_nom_du_dossier(tmp_path):
    dossier = tmp_path / "skin-a-tester"
    dossier.mkdir()
    _ecrire_skin_yaml(dossier, skin_id="mon_overlay")

    validation = valider_skin_candidate(dossier)

    assert validation.valide is True


def test_formate_les_validations_futures(tmp_path):
    _ecrire_skin_yaml(tmp_path)

    sortie = formater_validation(valider_skin_candidate(tmp_path))

    assert "Validations futures dépendantes du parent :" in sortie
    assert "- remplacer doit viser un id existant dans le parent" in sortie
    assert "Elle ne résout pas encore l’héritage avec la skin parente." in sortie


def _ecrire_skin_yaml(
    dossier: Path,
    *,
    skin_id: str = "skin_test",
    nom: str = "Skin test",
) -> None:
    (dossier / "skin.yaml").write_text(
        f"""
skin:
  id: {skin_id}
  herite_de: debut_mandat_bre
  nom: {nom}
  version: v1
  difficulte: debutant
""",
        encoding="utf-8",
    )

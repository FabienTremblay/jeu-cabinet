from services.cabinet.bre.catalogue_skins import (
    chemin_dossier_catalogue,
    lister_entrees_chargeables,
    skin_est_chargeable,
    trouver_entree_catalogue,
)


def test_catalogue_resout_un_overlay_declaratif():
    entree = trouver_entree_catalogue("exemple_mandat_climat_overlay")

    assert entree is not None
    assert entree.type == "declarative_overlay"
    assert entree.statut == "exemple_controle"
    assert entree.chargeable is False
    assert entree.source["type"] == "dossier"


def test_catalogue_liste_les_skins_chargeables():
    ids = {entree.skin_id for entree in lister_entrees_chargeables()}

    assert {"minimal", "debut_mandat", "debut_mandat_bre"} <= ids
    assert "mandat_fragile" not in ids
    assert "exemple_mandat_climat_overlay" not in ids


def test_catalogue_identifie_une_skin_chargeable():
    assert skin_est_chargeable("debut_mandat_bre") is True
    assert skin_est_chargeable("exemple_mandat_climat_overlay") is False
    assert skin_est_chargeable("skin_absente") is False


def test_catalogue_resout_le_dossier_depuis_la_racine_du_depot():
    chemin = chemin_dossier_catalogue("exemple_mandat_climat_overlay")

    assert chemin is not None
    assert chemin.name == "exemple_mandat_climat_overlay"
    assert (chemin / "skin.yaml").exists()


def test_catalogue_ignore_les_sources_module_python_pour_les_dossiers():
    assert chemin_dossier_catalogue("debut_mandat_bre") is None

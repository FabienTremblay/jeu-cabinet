from services.cabinet.bre.catalogue_skins import (
    chemin_dossier_catalogue,
    trouver_entree_catalogue,
)


def test_catalogue_resout_un_overlay_declaratif():
    entree = trouver_entree_catalogue("exemple_mandat_climat_overlay")

    assert entree is not None
    assert entree.type == "declarative_overlay"
    assert entree.statut == "exemple_controle"
    assert entree.chargeable is False
    assert entree.source["type"] == "dossier"


def test_catalogue_resout_le_dossier_depuis_la_racine_du_depot():
    chemin = chemin_dossier_catalogue("exemple_mandat_climat_overlay")

    assert chemin is not None
    assert chemin.name == "exemple_mandat_climat_overlay"
    assert (chemin / "skin.yaml").exists()


def test_catalogue_ignore_les_sources_module_python_pour_les_dossiers():
    assert chemin_dossier_catalogue("debut_mandat_bre") is None

import responses
import pytest
from services.cabinet.bre.regles_bre_proxy import ReglesBreProxy, BreIndisponible

@responses.activate
def test_regle_sous_phase_appelle_bre():
    # Mock de la réponse du BRE
    responses.add(
        responses.POST,
        "http://rules-service:8081/rules/eval/sous-phase",
        json={"commands": [{"op": "signal.programme_ouvert"}]},
        status=200,
    )

    # Création du proxy
    proxy = ReglesBreProxy(
        rules_url="http://rules-service:8081",
        skin="debut_mandat_bre",
        version_regles="v1",
        timeout_s=1.0,
    )

    # Appel de la méthode
    etat = object()  # Mock ou objet Etat minimal
    commandes = proxy.regle_sous_phase(etat, "signal.init_tour")

    # Validation
    assert commandes == [{"op": "signal.programme_ouvert"}]
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == "http://rules-service:8081/rules/eval/sous-phase"

@responses.activate
def test_bre_indisponible():
    # Simule une indisponibilité du BRE
    responses.add(
        responses.POST,
        "http://rules-service:8081/rules/eval/sous-phase",
        body=Exception("Timeout"),
    )

    proxy = ReglesBreProxy(
        rules_url="http://rules-service:8081",
        skin="debut_mandat_bre",
        version_regles="v1",
        timeout_s=0.1,  # Timeout court pour déclencher l'erreur
    )

    with pytest.raises(BreIndisponible):
        proxy.regle_sous_phase(object(), "signal.init_tour")


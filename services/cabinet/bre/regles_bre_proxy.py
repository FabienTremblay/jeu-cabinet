# services/cabinet/bre/regles_bre_proxy.py
from __future__ import annotations

import json
import logging
import ssl
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .etat_bre_adapter import EtatBreAdapter

from ..moteur.regles_interfaces import ReglesInterface, Command

log = logging.getLogger(__name__)


class BreErreur(Exception):
    """erreur générique d'accès ou de contrat avec le rules-service."""


class BreIndisponible(BreErreur):
    """rules-service injoignable / timeout / DNS / etc."""


class BreReponseInvalide(BreErreur):
    """réponse non-JSON ou structure inattendue."""


class BreRefus(BreErreur):
    """erreur 4xx/5xx explicite du rules-service (contrat violé, règle absente, etc.)."""


def _jsonable(x: Any) -> Any:
    """convertit récursivement un objet Python vers une structure JSON-safe."""
    if x is None or isinstance(x, (str, int, float, bool)):
        return x
    if isinstance(x, dict):
        return {str(k): _jsonable(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [_jsonable(v) for v in x]
    if hasattr(x, "__dict__"):
        return _jsonable(vars(x))
    return str(x)


@dataclass(frozen=True)
class BreConfig:
    rules_url: str
    skin: str
    version_regles: str
    timeout_s: float = 2.0
    verify_tls: bool = True
    trace_enabled: bool = False


class ReglesBreProxy(ReglesInterface):
    """
    Proxy strict vers rules-service.

    - aucune règle locale (pas de fallback) si fallback is None
    - si fallback est fourni, on peut choisir de retomber dessus en cas d'erreur (mode migration)
    """

    def __init__(
        self,
        *,
        rules_url: str,
        skin: str,
        version_regles: str,
        timeout_s: float = 2.0,
        verify_tls: bool = True,
        trace_enabled: bool = False,
        fallback: Optional[ReglesInterface] = None,
        fallback_sur_erreur: bool = False,
    ) -> None:
        self.cfg = BreConfig(
            rules_url=rules_url.rstrip("/"),
            skin=skin,
            version_regles=version_regles,
            timeout_s=float(timeout_s),
            verify_tls=verify_tls,
            trace_enabled=trace_enabled,
        )
        self.fallback = fallback
        self.fallback_sur_erreur = bool(fallback_sur_erreur)

    # -----------------------------
    # API ReglesInterface
    # -----------------------------
    def regle_sous_phase(self, etat: Any, signal: str) -> List[Command]:
        payload = self._payload_base(etat)
        payload["signal"] = signal
        try:
            return self._eval_commands("/rules/eval/sous-phase", payload)
        except BreErreur as e:
            if self.fallback and self.fallback_sur_erreur:
                log.warning("BRE erreur (%s) -> fallback regle_sous_phase", e)
                return self.fallback.regle_sous_phase(etat, signal)
            raise

    def regle_attente_terminee(self, etat: Any, type_attente: str) -> List[Command]:
        payload = self._payload_base(etat)
        payload["type_attente"] = type_attente
        try:
            log.info(
                "BRE-> regle_attente_terminee skin=%s version=%s type_attente=%s",
                self.cfg.skin,
                self.cfg.version_regles,
                type_attente,
            )
            return self._eval_commands("/rules/eval/attente-terminee", payload)
        except BreErreur as e:
            if self.fallback and self.fallback_sur_erreur:
                log.warning("BRE erreur (%s) -> fallback regle_attente_terminee", e)
                return self.fallback.regle_attente_terminee(etat, type_attente)
            raise

    def valider_usage_carte(self, etat: Any, cmd: Command) -> Tuple[bool, List[Command]]:
        payload = self._payload_base(etat)
        payload["cmd"] = _jsonable(cmd)
        try:
            rep = self._post_json("/rules/eval/valider-usage-carte", payload)
        except BreErreur as e:
            if self.fallback and self.fallback_sur_erreur:
                log.warning("BRE erreur (%s) -> fallback valider_usage_carte", e)
                return self.fallback.valider_usage_carte(etat, cmd)
            raise

        if not isinstance(rep, dict):
            raise BreReponseInvalide("BRE: réponse non-dict sur valider-usage-carte")

        if "ok" not in rep:
            raise BreReponseInvalide("BRE: champ 'ok' manquant sur valider-usage-carte")

        ok = bool(rep.get("ok"))
        cmd_cout = rep.get("cmd_cout")
        if cmd_cout is None:
            cmd_cout = []
        if not isinstance(cmd_cout, list):
            raise BreReponseInvalide("BRE: 'cmd_cout' doit être une liste")
        return ok, cmd_cout

    # -----------------------------
    # internes
    # -----------------------------
    def _payload_base(self, etat: Any) -> Dict[str, Any]:
        # base stable, extensible (facts minimaux + état complet jsonable pour itérer vite)
        return {
            "source_fichier": "services/cabinet/bre/regles_bre_proxy.py",
            # contrat commun facts_envelope.schema.json
            "analyse_skin": {"skin": self.cfg.skin, "version": self.cfg.version_regles},
            "joueurs": {},  # requis par le schéma commun (shape libre)
            "etat_min": EtatBreAdapter.to_facts(etat),
            "axes": {},
            "trace": {},
        }

    def _eval_commands(self, path: str, payload: Dict[str, Any]) -> List[Command]:
        rep = self._post_json(path, payload)
        if not isinstance(rep, dict):
            raise BreReponseInvalide("BRE: réponse non-dict sur eval")

        cmds = rep.get("commands", [])
        if cmds is None:
            cmds = []
        if not isinstance(cmds, list):
            raise BreReponseInvalide("BRE: champ 'commands' doit être une liste")
        return cmds

    def _post_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.cfg.rules_url}{path}"
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        req = Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )

        try:
            ctx = None
            if not self.cfg.verify_tls:
                ctx = ssl._create_unverified_context()
            with urlopen(req, timeout=self.cfg.timeout_s, context=ctx) as resp:
                raw = resp.read().decode("utf-8") or "{}"
        except HTTPError as e:
            # 4xx/5xx explicite: pas un timeout, c'est une réponse d'erreur
            raise BreRefus(f"BRE HTTPError: {e.code} sur {path}") from e
        except (URLError, TimeoutError) as e:
            raise BreIndisponible(f"BRE indisponible sur {path}: {e}") from e
        except Exception as e:
            raise BreIndisponible(f"BRE erreur inattendue sur {path}: {e}") from e

        try:
            data = json.loads(raw)
        except Exception as e:
            raise BreReponseInvalide("BRE: réponse non-JSON") from e

        if not isinstance(data, dict):
            raise BreReponseInvalide("BRE: JSON doit être un objet")

        return data

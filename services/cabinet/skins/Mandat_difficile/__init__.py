# services/cabinet/skins/debut_mandat/__init__.py

from .config import SKIN_CONFIG
from .regles import get_regles


def get_config():
    """API attendue par config_loader.charger_config_et_regles."""
    return SKIN_CONFIG


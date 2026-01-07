from ..cabinet.moteur.manager import PartieManager

# NOTE: si Manager a besoin de config_loader, instancie-le ici.
moteur_manager = PartieManager()

def get_manager() -> PartieManager:
    return moteur_manager

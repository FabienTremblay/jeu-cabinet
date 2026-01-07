# services/cabinet/bre/__init__.py
"""
Package dédié au BRE (Business Rules Engine).

On y place les adaptateurs/proxies et utilitaires permettant de brancher un
moteur de règles externe (rules-service) sans casser les skins Python existants.
"""

from .regles_bre_proxy import ReglesBreProxy


#!/usr/bin/env python3
import argparse, requests, sys, json

BASE = "http://api.cabinet.localhost/moteur/v1"

def post(url, data):
    r = requests.post(url, json=data)
    r.raise_for_status()
    return r.json()

def get(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["creer", "join", "etat", "action", "cloture"])
    ap.add_argument("--partie")
    ap.add_argument("--joueur")
    ap.add_argument("--pseudo")
    ap.add_argument("--type")
    ap.add_argument("--data", default="{}")
    args = ap.parse_args()

    if args.cmd == "creer":
        print(post(f"{BASE}/parties", {"nom": "demo", "options": {}}))
    elif args.cmd == "join":
        print(post(f"{BASE}/parties/{args.partie}/joueurs", {"joueur_id": args.joueur, "pseudo": args.pseudo}))
    elif args.cmd == "etat":
        print(get(f"{BASE}/parties/{args.partie}/etat"))
    elif args.cmd == "action":
        print(post(f"{BASE}/parties/{args.partie}/actions", {
            "acteur": args.joueur, "type_action": args.type, "donnees": json.loads(args.data)
        }))
    elif args.cmd == "cloture":
        print(post(f"{BASE}/parties/{args.partie}/cloture-tour", {}))

if __name__ == "__main__":
    sys.exit(main())

# Step22 — enregistrement de vrais essais (aucun essai réel présent)

Un dossier de préparation pré-T0 est scellé par son SHA-256 et son horodatage explicite avant le gel ; les observations après T0 sont conservées **séparément**. Les 14 rubriques de sortie peuvent être `NOT_MEASURED` (valeur `null`) mais jamais un zéro inventé. Un dossier de démonstration est refusé si déclaré `REAL_OBSERVATION`.

L'outil `trial_registry.py` fournit `preflight`, `outcome_draft`, `append_envelope`, `verify_chain`, avec verrou exclusif pour un écrivain et chaînage SHA-256 des reçus. Ceci n'est **ni un tiers de confiance temporel ni une signature numérique**. Aucune cuisson réelle n'a été importée ni observée. L'outil n'exécute aucune cuisson, aucune surveillance continue.

Commande : `python -m unittest discover -s step22 -p 'test_*.py' -q`. Le protocole détaillé est `PROTOCOLE_COLLECTE.json`. L'utilisateur doit encore mesurer et renseigner les paramètres et résultats réels pour un essai.

# RIZ-112 → MATRICE | Preuve temporelle exécutable (prototype de transfert)

**Objectif** : concrétiser P1–P3 et P6 du contrat `TRANSFERT_METHODE_MATRICE_PREMATCH.md` sans remplacer l’ADN R8, sans démarrer un autre moteur, et sans modifier les 62 familles sportives.

Cet outil indépendant vérifie les **cinq instantanés strictement antérieurs au coup d'envoi**, dans l’ordre J-6, J-4, J-3, H-9, H-0. Il refuse un fait dont la première disponibilité ou l’ingestion est postérieure à son propre gel, les dates sans fuseau horaire, un `UNKNOWN` falsifié en zéro, les doublons de champ et la contamination par un label post-match. Les champs modifiés exigent une source disponible après le gel précédent. Les noms d’horizons décrivent des fenêtres ordonnées ; le prototype ne certifie pas leur tolérance horaire métier, qui devra être définie dans l’ADN MATRICE.

Un exemple **entièrement synthétique** montre l'évolution d'une composition d’équipe inconnue J-6, provisoire J-4, révisée H-9, confirmée avant le coup d'envoi. Aucune équipe, aucun match ni résultat réel ne figure dans le paquet. Une empreinte SHA-256 déterministe permet de comparer les cinq instantanés gelés, **sans** faire d'un fichier un horodatage d'un tiers de confiance.

Le validateur ne peut pas certifier qu'une source a véritablement été publiée à l'heure déclarée : cette authentification exige un relevé d'acquisition indépendant. Il ne calcule **aucune probabilité de match** ; il n'importe pas les 112 rubriques riz dans les 62 familles sportives.

À partir du répertoire contenant ce module :

```bash
python -m unittest discover -s . -p 'test_*.py' -q
python prematch_timeline_gate.py --infile EXEMPLE_SYNTHETIQUE_5_FENETRES.json --output RECU_5_FENETRES.json
```

**Transfert requis** : sur la branche du dépôt MATRICE qui fait autorité, réutiliser/adapter le validateur existant s’il couvre déjà ces règles. Ne produire une nouvelle implémentation que sur écart documenté. Réaliser ensuite des essais sur snapshots historiques authentiques : une vérification de temps et de provenance ne prouve pas la justesse d'un pronostic.

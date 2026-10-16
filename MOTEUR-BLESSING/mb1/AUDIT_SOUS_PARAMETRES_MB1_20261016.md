# MOTEUR BLESSING — MB-1 : sous-paramètres, preuve vérifiée le 16 octobre 2026

## Reprise à partir du vrai ZIP
Le fichier ajouté au projet est exactement le ZIP du reçu `R-9YPJ87CMENDW`. Taille **12 241 975 octets**, SHA-256 `5ef731d6ee4b5edb8a741c59a565d4f7363be84eb9225e814345cb0a04fe89e0`. Inventaire 100 membres, CRC conforme, 8 fichiers obligatoires présents. Le ZIP n'est **pas encore installé sur Windows**.

Sur le code réel, toutes les 169 batteries historiques ont été relancées localement : **46 + 45 + 30 + 48 = 169 tests réussis**. Ils n'établissent aucune performance sportive.

## Nouvelle cartographie MB-1 (372/372)
Revue éditoriale de la correspondance des sous-paramètres (6 par monde, 62 mondes) :
- **25** liens de conception directs aux champs existants, sans collecteur ni preuve PIT.
- **50** liens uniquement partiels ou contextuels, impropres à une mesure complète.
- **297** fiches sans représentation numérique adéquate dans V1.1.2.
- **13 des 24 liens préexistants** ont été rétrogradés en raison de confusions sémantiques. Exemples : ratio cartons/fautes ≠ cartons/matches; présence d'un nombre de jours depuis nomination ≠ communiqué; distance estimée ≠ coordonnées; dispersion de pluie ≠ incertitude des rafales.

Nouveaux modules créés et exécutés dans le paquet de livraison **`MOTEUR_BLESSING_V1_1_2_MB1_AMELIORE_2026-10-16.zip`** (original maintenu intact dans ses 100 fichiers) :
- `mb1/manual_crosswalk_v2.py` (**SHA** `be5ea01d6c2de93d89f27c2ff559694f1c968b4314eb83cb851097ba62abd2dd`)
- `mb1/crosswalk_audit_v2.py` (**SHA** `2aeda30cc1bc0fc66a8d8cb1993820219272ffc10629915c6c21361f6df4e458`)
- `mb1/SUBPARAMETERS_MB1_AUDIT_20261016.json` (**SHA** `7a643c4cec0a8f49898e2f26be7013b66704242d5952248332c7fbcfe0a4332a`)
- `mb1/pit_gate_v1.py` (**SHA** `f6e3d61a8bea41a513879fd140b2eae5e03eb6c9bc60cc5470b5465dda203493`)
- `mb1/test_mb1.py` (**SHA** `cd0a00d238f3c31716f283ec3430343c144f026df52cdd328a348ab32fdaa608`)
- `mb1/README_MB1.md`, `mb1/AUDIT_5_CYCLES_20261016.md`, `mb1/VERIFIER_MB1_WINDOWS.bat`.

**18/18 nouveaux tests PASS** sur les données structurées du ZIP + scénarios synthétiques d'attaque. Contrôles du référentiel, ré-audit des rapprochements, publication/capture après gel, données manquantes, SHA, fuseau horaire et gel strictement avant match. Les données PIT réelles ne sont **pas** certifiées par un JSON déclaratif.

## Livraisons conservées
- ZIP enrichi (MB-1 + original intact) : **12 271 620 octets**, SHA-256 `192cdae0a2d551b550abb4a6821f75bf2eef9a5d1d0e2d48cb80bc08252deed6`.
- ZIP incrémental MB-1 seulement : SHA-256 `e801039186cea972e3f1cc64781258a9ddf4730a58063fc2beeb3099af50c91c`.

Les fichiers réels nouvellement produits sont accessibles dans **la sortie de cette conversation**, pas automatiquement depuis GitHub/Delivery/PC. Ces sommes de contrôle permettent la reprise et la détection d'une version différente.

**Statut : `MB1_PARTIAL_DESIGN_RECONCILIATION_DONE`; `MB2_PIT_DATA_NOT_DONE`; `MB3_MODEL_VALIDATION_NOT_DONE`; `MB4_PRODUCT_NOT_DONE`.** Pas de nouveau score IC activé, l'essai synthétique V1.1.2 restant inférieur à sa baseline. Prochaine priorité : obtenir et authentifier des sources temporelles pré-match réelles; confirmer les jointures, éliminer doublons et tester sur dates indépendantes.

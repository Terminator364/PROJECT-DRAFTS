# RIZ112 → MATRICE R8 — comparaison en lecture seule (2026-10-17)

**Portée :** validation documentaire du prototype de preuve temporelle RIZ112 contre la feuille directrice ADN R8 et son pointeur `ACTIVE_WORK_HEAD.json` dans `Terminator364/ChatGPT-PC`. Aucun fichier MATRICE n'a été modifié ni fusionné. Ceci ne remplace pas un audit de tous les contrôles existants dans l'arbre de travail R8.

## Sources vérifiées

- Source MATLAB? **Non** : RIZ112, `simulations/EXPERIENCE_1000/TRANSFERT_PREMATCH/prematch_timeline_gate.py`, GitHub blob `MOTEUR-BLESSING/labs/RIZ112` (programme de 5 fenêtres).
- Autorité MATRICE : `MATRICE/GOUVERNANCE/FEUILLE_DE_ROUTE_DIRECTRICE_MATRICE_ADN_2026_10_14_R8.md`, branche `research/matrice-r4-universal-2026-10-10`, blob `7b77578da413c47a278f3fdd0ad4ab434e4cccc8`.
- `MATRICE/UNIVERSAL/ACTIVE_WORK_HEAD.json` même branche, blob `b700352f7b773a25d263ed2c3313712f0540d31c` : déclaration `LOT13` dernier vérifié, G3 encore ouvert, G4/G5 non démarrées; la déclaration de `next_lot` n'est pas une preuve d'exécution.
- Banc RIZ112 : checkpoint `CHECKPOINT_TRANSFERT_TEMPOREL_20261017.json`, 24 tests Linux + 24 Windows, sur un exemple purement synthétique; archive E136 et reçu cloud E137.

## Compatibilités déjà prouvées sur le prototype

| Invariant de méthode | Prototype RIZ112 | Limite |
| --- | --- | --- |
| Pas de donnée de match après T0 | Toutes les cinq coupes doivent précéder le coup d'envoi | Pas d'attestation externe des heures |
| Gel des vues `J-6,J-4,J-3,H-9,H-0` | Ordre vérifié; hash stable de chaque instantané | **Ne vérifie PAS** que l'étiquette correspond au délai réel par rapport au coup d'envoi |
| Données temporalisées | `observed_at_utc <= available_at_utc <= ingested_at_utc <= cutoff` | **N'a pas `published_at_utc`** séparé, demandé dans l'ontologie R8 |
| Statut d'incertitude | `UNKNOWN -> value=null`, pas de zéro silencieux | Ne modélise pas encore la politique complète d'abstention sportive R8 |
| Anti-double comptage | Clé `field` unique par snapshot | Pas d'arbitrage de deux sources différentes pour le même fait, ni `entity_id` /`fixture_id` sur chaque observation |
| Reproductibilité | SHA-256 du paquet et des cinq vues | Hash local seulement, aucune signature/horodatage tiers |
| Calibration | Pas de calcul d'IC sportif | Aucun match réel évalué, aucun Brier/reliability/calibration |

## Écarts à confronter AUX contrôles MATRICE existants avant tout ajout

1. L'ADN R8 décrit un schéma d'observation avec `field_id`, `fixture_id`, `entity_id`, `asof_utc`, `observed_at_utc`, `published_at_utc`, `available_at_utc`, `source_id`. Le prototype n'implémente qu'un sous-ensemble : **adapter au contrat existant, ne pas créer un second schéma canonique**.
2. Valider les seuils calendaires réels et le fuseau : le prototype vérifie l'ordre, **pas** le respect exact du « J-6 / H-9 » affiché. `H-0` demeure strictement avant le kickoff ; jamais une observation live.
3. Acquisitions publiées à T : exiger publication prouvée et première disponibilité à la coupure; éviter les reconstructions rétrospectives contaminées par des sources tardives.
4. `UNKNOWN`, provisoire, confirmé, sources concurrentes, versions et corrections : relier aux politiques de preuves et d'abstention des 62 familles, sans injection de nouvelles valeurs de probabilité.
5. Évaluer REUSE/ADAPT/BUILD ONLY IF GAP dans l'arbre `research/matrice-r8-g3-depth-audit-2026-10-14` et ses checkpoints les plus récents; **ne pas supposer qu'un besoin logiciel est encore absent parce qu'il manque au prototype riz**.

## Verdict

**TRANSFERT METHODOLOGIQUE POSSIBLE, INTEGRATION MATRICE NON APPROUVEE.** Le prototype atteste la reproductibilité de *cinq exemples synthétiques prématch*, et rien de plus. Ne pas modifier le catalogue des 62 familles ni l'IC de MATRICE; ne pas importer Q* du riz. Prochaine opération conditionnée par l'audit de réutilisation des contrôles temporels R8 existants et de la feuille de route. Le Cahier mère RIZ112 et le journal E137 demeurent la base de cette étude.

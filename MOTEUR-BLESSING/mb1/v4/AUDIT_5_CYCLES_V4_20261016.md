# MOTEUR BLESSING — MB-1 V4 — les cinq cycles (2026-10-16)

## 1 — Construction

Source réelle: ZIP MB-1 V3 SHA-256 `3c1bd3369309101ffdb11f41b4e62270c65f028ff138935b4058e35cf3042baa` (114 fichiers). Conserver sans altération les 114 membres existants.

Ajouts V4:
- `contract_gate_v4.py` : définition explicite et vérifiable de **24** obligations de gouvernance dans 4 mondes, chacune munie d'un type, d'un champ, d'une exigence de preuve et d'un effet de modèle `null`.
- `temporal_primitives_v4.py` : deux familles de prototypes mathématiques déterministes, hors modèle (moyennes de buts passés et temps depuis dernier match terminé) ; garde `match_end <= source_publication <= source_capture <= freeze < target_kickoff`, exclusions post-cutoff, refus des buts de prolongation.
- `backlog_297_v4.py` : couverture explicite **297/297** items encore non mappés, répartis par priorités de travail **24 / 55 / 206 / 12** ; les 50 liens partiels et 25 de conception directs ne sont pas artificiellement reclassés.
- `SOURCES_PIT_RESEARCH_V4_20261016.json` : recherche contrôlée de sources candidates (archives météo d'exécutions, événements historiques, CSV) avec réserves temporelles et conditions d'usage.

## 2 — Audit

Contrats 24/24, 297/297, 62 mondes conservés, 372 propositions conservées. Aucune formule historique V1.1.2 supprimée, aucun coefficient arbitraire ajouté. Sources candidates ≠ ingestion, aucun match réel ni horodatage indépendant disponible dans V4.

## 3 — Contre-audit

Essais adversariaux : même match dans son propre historique, dates sans fuseau, données capturées après T, erreurs d'heure de début/fin, scores négatifs/booléens, prolongation au lieu des 90 minutes + arrêts, doublons d'identité, fausses preuves de gouvernance complètes, données absentes, source hash mal formé, faux gel égal au coup d'envoi, horaires divergents pour un même match, coffre altéré.

**Point de vigilance** : les SHA déclarés dans les exemples de résultats historiques sont contrôlés sur leur *forme* seulement dans `temporal_primitives_v4.py`; il faut un coffre V3 qui lie réellement le hash aux octets avant toute décision scientifique. Les objectifs de source correspondent à un cahier des charges, pas à 297 collecteurs existants.

## 4 — Corrections

Refus explicite des entrées historiques appartenant au match cible et des versions hors périmètre 90 minutes, distinction NULL de zéro, isolation des deux calculs hors scoring, décision bloquée même lorsque les 24 pièces sont remplies par des déclarations arbitraires.

## 5 — Ré-audit

Test suite V4 **42/42 PASS** sous Python 3.13 Linux local. Les 169 tests historiques, 18 tests V2, 28 tests V3 et 42 V4 donnent **257 tests PASS** dans l'environnement ChatGPT. Aucun de ces tests ne constitue une validation sur des matchs réels ni une reproduction Windows globale.

## Blocages ouverts

- Authenticité historique indépendante des timestamps/source: **NOT PROVEN**.
- Données réelles réellement capturées avant T: **NOT INGESTED**.
- Calibration/évaluation OOS chronologique: **NOT RUN**.
- ZIP intégral V4 sur PC Windows: **NOT CONFIRMED**.
- **STATUT SCIENTIFIQUE `EXPERIMENTAL_NOT_APPROVED`**. Aucun IC réel certifié et aucune modification des 140 recettes candidates originales.

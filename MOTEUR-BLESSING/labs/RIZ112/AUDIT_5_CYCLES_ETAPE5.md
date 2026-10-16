# Audit contradictoire — RIZ-112, cahier mère et étape 5

## Cycle 1 — Construction

Inventaire des consignes explicites/réponses utilisateur, antérieures identifiables ou reconstituées ; création du cahier consolidé, journal JSONL append-only lié par SHA256, décisions et règles de transfert. À partir de l'archive authentifiée étape 4, construction d'un protocole **DRAFT** de mesure de qualité à 6 dimensions avec `weights=null` et d'un outil `study_design.py` séparant X pré-T₀, mécanismes et y post-T₀. Programme `interaction_2x2.py` pour étudier l'interaction de deux variables **au sein du noyau simplifié** sans émettre un IC.

## Cycle 2 — Audit

Reprise exacte de l'étape 4, test SHA256 29 039 octets et ZIP CRC, 22/22 tests précédents relancés. Le modèle n'utilise que 15/112 cases ; aucune donnée réelle Q mesurée, `IC=null`. Contrôle qu'aucune étiquette de qualité finale ne figure dans `prestart_feature_record`.

## Cycle 3 — Contre-audit

Tests hostiles : injection du résultat dans le paquet d'entrée, label prétendument approuvé sans protocole, score Q numérique malgré absence de barème, dates de capture tardives, score poststart daté avant début, défaut de version du protocole, NaN, doublon d'essai/source, ligne de journal modifiée ou réordonnée, et confusion d'une attestation déclarée avec une attestation tierce.

## Cycle 4 — Corrections

- Statut de protocole fixé à `DRAFT_NOT_APPROVED` et registre indépendant requis avant toute activation.
- `quality_score_100` refusé tant que le barème n'est pas approuvé ; aucune pondération cachée dans les scripts.
- `provenance_status=INDEPENDENT_VERIFIED` refusé dans les enregistrements auto-déclarés.
- `prestart_capture <= freeze < start < outcome_observed <= poststart_capture` et séparation JSON de X/y.
- Journal SHA256 chaîné, mais explicitation de sa limite : **sans ancrage externe, le hash local ne certifie pas l'heure historique**.

## Cycle 5 — Ré-audit

- Étape 4 : **22/22 tests PASS**.
- Étape 5 : **31/31 tests PASS**.
- Journal : **10/10 tests PASS**.
- **Total : 63/63 tests logiciels** dans le conteneur ChatGPT.
- Contraste 2×2 illustratif `lid_multiplier × power_W → W_shortfall` : **10,367227 g** de différence des différences. Ce résultat démontre une **non-additivité calculée**, non une relation scientifique validée ni un IC.
- **Zéro** préparation réelle étiquetée, **zéro** apprentissage effectif, **zéro** IC calibré, **zéro** intégration dans MATRICE. Test Windows **non effectué** pour cette étape.

## Éléments encore ouverts

1. Validation par l'utilisateur des critères de qualité, des méthodes de mesure et de l'agrégation Q (sans poids arbitraires).
2. Collecte réellement datée des conditions préstart puis des qualités observées, séparées.
3. Version du protocole figée avant la collecte ; double notation inter-observateurs et conservation des écarts.
4. Apprentissage de la relation des mécanismes vers la probabilité d'atteindre Q≥85 ; calibration et test chronologique indépendant.
5. Portage **des principes génériques** seulement vers MATRICE, avec test de non-régression de la baseline Poisson présentée comme multimonde.

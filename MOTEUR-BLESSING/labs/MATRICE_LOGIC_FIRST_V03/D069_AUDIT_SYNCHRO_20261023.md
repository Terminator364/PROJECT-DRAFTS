# MOTEUR D069 — Vérification et limites, 23 octobre 2026

## Résultats effectivement relus

1. GitHub Actions, branche publique PROJECT-DRAFTS, reçu `CI_READBACK_D066.json` : **58/58 tests PASS** du baseline chronologique, anti-fuite de provenance, analyse de l'archive V12, 355 contrats synthétiques de test et modèle source. Ces tests **ne constituent pas** une exécution des 355 contrats R8 privés d'origine.
2. GitHub Actions, branche R8 privée : D062 **55/55** tests intégrés PASS et D063 **67/67** PASS (calculs IC sous hypothèses et symboles 355). Le nouveau workflow D069 a été ajouté au workflow R8 connu, mais **`CI_READBACK_D069.json` reste absent** ; aucun succès de ce test de bout en bout n'est déclaré.
3. L'archive fournie `MOTEUR_BLESSING_V1_1_2_MOTEUR_ACTUEL_2026-10-16.zip` a été **extraite et testée localement** dans le contexte de cette conversation : suites **46 + 45 + 30 + 48 = 169/169 PASS**. Le module de démonstration a produit les trois IC **49,736825 %, 57,251863 % et 87,751713 %** entièrement synthétiques.
4. Le test d'entraînement V1.1.2 synthétique a été relancé : **230 train / 20 test**, Brier du candidat **0,385073164**, référence **0,376083642**, différence **+0,008989521** (candidat moins bon). Refus de promotion.
5. Ancien classeur V12 du Drive : 313 résultats (181 train, 72 validation, 55 test, 5 replay), 49/55 Over1.5 sur le test ; score de Brier V12 **0,1146655**, rigoureusement identique à sa référence du classeur. Avec la fréquence Over de l'entraînement seule, Brier sur test **0,1182304**, soit un gain exploratoire **0,003565** du V12. Bootstrap par paires exploratoire 15 000 réplications : intervalle d'amélioration **[-0,004858 ; +0,010683]**, incluant zéro. Ce test n'est **ni PIT certifié ni indépendamment validé**.

## Modifications logicielles D069

- Extension de la preuve de test GitHub R8 privée : `.github/workflows/moteur-logic-d060-sourcegraph.yml` avec nouvelle étape exhaustive D069 et reçu privé automatique, déclenchement demandé mais succès non attesté.
- `source_mechanism_dossiers_v11.py` : une propriété d'anti-double-compte absente dans les **anciens contrats sources** demeure explicitement UNKNOWN. Aucun faux auteur/effet causal n'est créé. Tests correspondants.
- `audit_legacy_v12_v13.py` : ajout d'un bootstrap par paires reproductible, limité à l'analyse rétrospective, sans allégation de généralisation ni publication avant T0.
- Suite GitHub publique étendue : **58/58 tests** désormais confirmés par un reçu GitHub actualisé.

## Frontière de finition

**Moteur ancien V1.1.2 : logiciel local vérifié.** **Moteur nouveau : modules mathématiques et historiques passés sur jeux de test, fusion des 355 contrats privés toujours en attente d'une preuve d'intégration.** **IC sportif réel calibré : aucun.**

Restent : succès reçu D069 sur la vraie source R8, données historiques de source originale datée avec résultats réglementaires à 90 min, étude d'impact R8 hors échantillon sur référence simple, et travail scientifique sur les 324 effets non signés. Aucune précision sportive de 85 % n'a été établie.

**Reprise `Moteur/continue` :** vérifier d'abord `MATRICE/R8_G3_DEEP_20261014/MOTEUR_LOGIC_FIRST_D057/CI_READBACK_D069.json` sur branche privée `research/moteur-logic-first-d057-2026-10-23`. Si absent, traiter les blocages de lancement GitHub Actions, sans inventer un reçu. Ne pas réinitialiser les travaux RIZ112, D062/D063, D066 ou les archives V12.
# Cahier mère — CONTEXTE INTÉGRAL DES CONVERSATIONS (rubrique permanente)

**Directive utilisateur D030 (17/10/2026) :** conserver continuellement *tout le contexte utile de chaque conversation* lié au RIZ-112 et à MATRICE : demandes et réponses, hypothèses, désaccords, corrections, choix abandonnés, code, expériences, problèmes, liens, versions, états de synchronisation. **Les faits archivés doivent être sourcés et qualifiés.**

## Transparence sur la complétude
Le registre ci-joint conserve les **passages textuels disponibles** et les **résumés signalés comme reconstitutions**. Des portions anciennes des échanges ne sont pas disponibles en transcription littérale : nous **ne prétendons pas** posséder l'intégralité verbatim des conversations antérieures. Chaque future conversation doit enregistrer au minimum toutes les instructions utilisateur et les réponses décisives accessibles, avec un ID, une date, un état et un ancrage vérifiable.

## Codes et comportement obligatoire à la reprise
- `MOTEUR|CONTINUE`, `Moteur/continue` et `MOTEUR BLESSING|CONTINUE` : **ouvrir d'abord** `MOTEUR-BLESSING/MANIFEST.json`, `CONTINUITE.md`, la feuille de route, les preuves MB-1, **puis** le pointeur `riz112_lab` et le Cahier mère.
- `RIZ112|CONTINUE` : ouvrir `labs/RIZ112/CAHIER_MERE.md` → `CONTEXTE_CONVERSATIONS.md` → `CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl` → `CHECKPOINT.json` → `journal/JOURNAL_EVENEMENTS.jsonl` → scripts réellement présents et tests → actions.
- Éviter de redémarrer les projets, de recopier de vieilles versions, de feindre des validations ou de perdre les réactions de l'utilisateur. Le lab RIZ demeure **méthodologique**, distinct du moteur prématch.
- **Avant clôture de chaque tour de travail :** relire les messages accessibles; journaliser toute instruction/feedback important, les actions et échecs; mettre à jour le contexte, les décisions, les tests, le checkpoint et les empreintes, puis vérifier GitHub et les copies distantes. Signaler séparément ce qui n'a pas été synchronisé.
- La synchronisation n'est **pas autonome entre conversations inactives** : les fichiers doivent être relus et actualisés à chaque reprise. Ni l'historique intégral inconnu ni une écriture distante impossible ne sont présentés comme faits.

## Évolution du moteur et des attentes utilisateur

| Cycle | Stade | Décision/avancement réel |
|---|---|---|
| Analogie | 01–03 | 112 cases, pré-cuisson, riz moelleux, grains séparés, Q>=85/100; IC conditionnel non-additif. |
| Équations initiales | 04 | 15 cases numériques, bilan eau/chaleur, 22 tests; pas de prédiction réaliste. |
| Cahier mère | 05 | Constitution des décisions et journal append-only; séparation pré/post-T0, Q non pondéré. |
| Couverture de rôles | 06 | 112/112 traitées en contrats, 17 liées aux valeurs simplifiées, sans 112 effets quantifiés. |
| DAG/temps | 07 | 19 arcs invalides exclus, 150 relations candidates, 62 sans chemin déclaré vers Q. |
| D014 | 08 | 62 raccordements fonctionnels, distinction calcul/contrôle/effet Q; valeur future non injectée. |
| IC démo | 09 | IC simulés A/B/C 62.40/36.83/0.10%, proxy Q* inventé, science null. |
| Contrefactuels | 10 | 11 cases modifient localement l’IC démo; contrôle de cohérence de 14 cibles. |
| Générateur | 11 | 60 situations dont 18 calculables, matériaux non modélisés transparents. |
| Population | 12 | 100 situations, 44 entrées diversifiées, 224 perturbations, 26 effets non démontrés. |
| Hiérarchie H1 | 13-H1 | 112 sous-arbres, propriétés marmite/fer/céramique/bois et transfert fictif. |
| Anticipations H2 | 13-H2 | Deux trajectoires sans/avec correction pré-déclarée, RNG comparables; 282/282 tests. |
| Mécanismes H3 | 14-H3 | 4 sous-chemins numériques hypothétiques supplémentaires (006/025/039/069), 22 lacunes restantes; 309/309 tests; PC non testé. |
| Reprise unifiée | 14-CONTEXT | Contexte des échanges et alias MOTEUR|CONTINUE / Moteur/continue / RIZ112|CONTINUE documentés ; H3 avant synchronisation distante. |

## Invariants exigés par l'utilisateur

1. 112 rubriques canoniques, non 112 variables toutes indépendantes ; éventuelles « 119 » à clarifier sans ajouter arbitrairement 7 champs. Paramètre → sous-paramètres → sous-sous-paramètres → mécanismes → anticipations → IC, avec interactions, saturation, contraintes et chemins conditionnels ; une variation peut légitimement ne rien changer localement.
2. Plusieurs situations A/B/C ou 100 dossiers à rubriques comparables, avec des valeurs initiales différentes et une sortie individualisée ; les catégories de marmite doivent passer par leurs propriétés pertinentes, les incompatibilités doivent être traitées sans abstention par défaut, mais le modèle doit marquer les limites de sécurité/validité.
3. Analogie de préparation du riz **pour MATRICE uniquement**, moteur prédictif et non manuel de cuisine ; prématch/précuisson uniquement, aucune donnée future. Distinguer le seuil **Q>=85/100** du seuil opérationnel **IC>0,25** proposé ultérieurement.
4. `IC_DEMO` de Q* = estimation simulée sous hypothèses non validées, **pas** IC scientifique ou probabilité réelle. Pas de constantes inventées dissimulées, pas d'addition mécanique de bonus/malus, aucune promotion sans observations et calibration indépendantes.
5. Processus de construction/audit/contre-audit/correction/ré-audit; tests et preuve de la version réellement exécutée; budget zéro, PC Windows 4 Go faible, GitHub et Drive disponibles, PC hors ligne non considéré synchronisé.
6. Le Cahier mère doit préserver les idées initiales **et** toutes les objections, retours, corrections, échecs, résultats, fichiers, liens de livraison; ne jamais remplacer silencieusement une décision contredite.

## Historique utilisateur et provenance
Voir `CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl`. Pour chaque entrée, `VERBATIM_EXCERPT` est un fragment disponible (non toute la transcription) et `SOURCE_RECONSTRUCTED` une synthèse non littérale. Les anciennes décisions détaillées et les événements d'exécution restent dans `DECISIONS.md` et `journal/JOURNAL_EVENEMENTS.jsonl`.

## État technique observé au moment de création de cette rubrique
- Source locale H3 : `step14/anticipatory_physics_h3.py` ; 100 simulations H3 et ablations; quatre chemins numériques **hypothétiques**, 22 lacunes encore sans chemin chiffré, 0 effet empirique validé.
- Suite H3 reroulée ici : 22 + 31 + 10 + 42 + 36 + 19 + 25 + 20 + 13 + 23 + 41 + 27 = **309/309 tests logiciels**.
- Github **avant** mise à jour : manifest du projet pointait encore vers la V13 H1, checkpoint à 67 événements, alors que la source H3 locale contenait déjà 79 événements. Ceci est un **incident de décalage réel** et doit rester archivé.
- L'accès au PC ne constitue pas un test Windows; garder statut réel.

## Procédure de collecte continue à chaque nouvelle conversation
Ajouter une nouvelle entrée `CTX-xxxx` pour chaque nouvelle directive et chaque réponse d'architecture significative. Pour chaque action, conserver l'ID de l'exécution, les empreintes du code et les tests, l'état des supports, les hypothèses associées et la référence `E###` du journal hash-chaîné. Ajouter une section `Contexte de la conversation en cours` au Cahier mère (ou un fichier de contexte versionné lié) sans effacer les précédents. **Vérifier** les fichiers distants; leur existence ne prouve pas à elle seule le contenu identique.

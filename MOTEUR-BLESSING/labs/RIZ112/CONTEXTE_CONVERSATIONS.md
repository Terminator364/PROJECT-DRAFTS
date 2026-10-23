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


## Vérification de la synchronisation (E084)
GitHub : 9/9 blobs critiques identiques, manifeste parent actualisé ; Drive privé : archive source initiale 568443 octets retrouvée ; Bibliothèque : copie retrouvée ; PC MBMPC : hors ligne, pas de copie ni tests Windows. Les éventuelles variantes finales du ZIP ont leur propre reçu séparé pour éviter une empreinte SHA-256 auto-référente.

## Vérification de continuité des messages actuels — CTX-0018 à CTX-0020, E085–E088

L’utilisateur demande **mot pour mot** que le contexte soit continuellement écrit et que la suite soit planifiée. Les messages exacts figurent dans `CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl`; l’état H3 et les limitations sont dans le journal. **Règle de fonctionnement** : conserver le contexte à chaque séance de travail et à chaque checkpoint, ne pas promettre d’écriture en arrière-plan lorsque ChatGPT est inactif.

**Statut scientifique** : 309 tests logiciels historiques H3 ; 22 mécanismes n’ont pas encore de chemin numérique même fictif ; aucune préparation réelle observée ni IC calibré. Le plan de continuation est `PLAN_SUITE_RIZ112_MATRICE.md`. H3 Drive confirmé par existence et taille, SHA non relu directement sur Drive. PC non synchronisé.

## Clôture vérifiée E089
GitHub : fichiers critiques relus ; Google Doc privé contenant les deux demandes et le plan relu ; Bibliothèque : copie de reprise enregistrée, ZIP précédent H3 sur Drive confirmé ; **nouvel archive de reprise complète non déposée sur Drive**; MBMPC non synchronisé. Contexte 21 entrées, journal 89 événements. Source faisant foi : chemins GitHub du manifeste et du checkpoint.


## §23 — Session U1 : un seul code, contexte complet disponible, reprise active (17 octobre 2026)

**[DIRECTIVES UTILISATEUR, TEXTE EXACT]** Voir `CTX-0022` à `CTX-0025` : demande de continuité, exigence d'enregistrement permanent du contexte, rejet des codes multiples, et attente qu'un simple `Moteur/continue` **lance le prochain travail selon le Cahier mère**. Ces formulations ne doivent pas être réduites à un simple alias.

**[CONSTAT VÉRIFIÉ]** Le ZIP H2 disponible était plus ancien que GitHub H3 (étape 14); le ZIP H3 de 192 fichiers avait un checkpoint identique aux blobs GitHub. Reprise sur H3/309 tests/89 événements/21 entrées de contexte plutôt que régression vers H2. Les 309 tests historiques et la chaîne du journal à E089 passent à nouveau. `CTX-0026` enregistre la synthèse de ces vérifications.

**[RÈGLE U1]** Code unique et sensible à la graphie documentaire : `Moteur/continue`. Tous les alias antérieurs restent uniquement en historique, **désactivés dans les nouveaux points d'entrée**. Lire ce contexte et les sources avant de démarrer H4 sans nouvelle confirmation. Récolter toutes les nouvelles directives verbatim accessibles et les actions sous des résumés vérifiables, tout au long de la séance; éviter de prétendre à une transcription de messages antérieurs inaccessibles ou à une tâche en arrière-plan.

**[PROCHAINE EXÉCUTION]** H4 — inspecter `step14/H3_26_CASES_LEDGER.json`, puis réduire les 22 manques de mécanismes avec preuves mathématiques explicites et tests, sans ajouter 22 malus artificiels, sans promouvoir l'IC fictif. Fichier exécutable d'instructions : `continuity/NEXT_ACTION.json`.

### Reçu final de synchronisation U1 — CTX-0027 / E094
Relecture GitHub 7/7 références critiques conforme à la commande unique; Google Drive privé 794 856 octets et Bibliothèque confirment le paquet initial. MBMPC hors ligne. Contexte porté à 27 entrées et journal à 94 événements. H4 sera exécuté au déclencheur `Moteur/continue`, pas exécuté en arrière-plan.


## Session H4A — 17 octobre 2026 (CTX-0028/0029)

L'utilisateur déclenche explicitement `Moteur/continue` (verbatim dans CTX-0028). L'assistant confronte le ZIP V1.1.2 à l'autorité GitHub H3, relance 169/169 tests V1.1.2, exécute H4A (7 rubriques, 3 diagnostics) puis 29/29 tests adversariaux après correction fraction nombre/masse. Les deux blobs Python GitHub correspondent aux fichiers testés. CTX-0029 est un résumé de travail, **pas** une transcription inventée. Le journal chaîné est passé à 96 événements; checkpoint H4A partiel et action suivante H4B. Aucun IC Q réel, ni aucun test Windows H4A, ni aucune nouvelle livraison Drive/Delivery attestée.
\n\n## Session finale du moteur unifié — CTX-0032/0033\n\nDirective utilisateur verbatim conservée dans CTX-0032 : « D'accord go le pc aussi est reconnecter oft ». Le laboratoire RIZ-112 a été effectivement unifié avec ses 108 fiches JSON et quatre rôles dérivés. 309 tests anciens + 106 nouveaux ont été relancés et réussis **sur Linux et sur Windows MBMPC**, avec 3 scénarios IC_DEMO 60.25/19.25/0.25 et `scientific_ic_percent=null`. Installation versionnée Windows avec raccourci, archive complète dans la bibliothèque et copie Drive G: SHA concordant ; fichier cloud confirmé par identité et taille, SHA cloud non encore relu indépendamment. Le journal E097/E098 invalide a été réparé, sa copie forensique a été conservée et l'historique E001–E102 correctement chaîné. La prochaine étape ne consiste pas à refaire H4 : ce sont des données réelles et la calibration du critère Q.\n

## 17 octobre 2026 — Simulation méthodologique 1000 configurations

Directive utilisateur CTX-0049/E126 : conserver le contexte, utiliser riz comme banc d'essai pour MATRICE, faire des hypothèses contrôlées plutôt que cuisiner réellement. Résultat CTX-0050/E127 : 1000 scénarios simulés (9 variables physiques), 200 tirages Q* par scénario, 690 H3 calculés, 310 abstentions, 20 IC_DEMO>=85%, 664 bilans idéalisés favorables; 18 perturbations additionnelles. `scientific_ic_percent=null`. Source : simulations/EXPERIENCE_1000/.


## Session D057–D058 — 23 octobre 2026 (CTX-0079 à CTX-0082)

**Messages utilisateur verbatim accessibles** : CTX-0079 `Moteur/continue` ; CTX-0080 `👀` ; CTX-0081 `D'accord continue et fini le travail`. Le registre CTX-0082 est **une synthèse de l'exécution de l'assistant**, pas un message utilisateur inventé.

**Travaux vérifiés** : vraie intégration V0.1/V0.2/V0.3 sur branche de laboratoire privée R8 non canonique; compilation `compile_v22.current()` 62 mondes/355 enfants; 710 emplacements pré-T0 pour deux équipes; premier run CI 27/28 puis seconde exécution 28/28 PASS; approfondissement D058 343 contrats JSON source originaux + 12 archives vérifiées par compilateur; troisième exécution CI **31/31 PASS**. Fichiers sources enrichis demeurent **privés**. Le code générique est dans PROJECT-DRAFTS public. Les règles causales non justifiées D056 restent bloquées et les 324 sans liaison ne sont pas déguisées en prédicteurs.

**Limitations** : IC Over1.5 numérique théorique/calibré **`null`** ; 0 validation sportive hors échantillon; moteur MATRICE 2.0 inchangé; pas de test Windows MBMPC dans cette séance; archivage ZIP complet sur Drive non confirmé. Miroir Google Docs du Cahier mère **actualisé et relu** après D058 (revision `AHj4eMSuJr92S2IoR0DJ9j5yZyMoWqtBYiUv-11dUSA-J9PJzcptLvO3VMoDD6f9jqPA3BtNJuqfks0n6fht6RfitEQecT5IH9XRvBNCA2oX`). Prochaine étape contractuelle : revue sémantique individuelle et graphe de mécanismes des 324 avec preuve, puis lois statistiques et calibration, sans promettre de précision de 85 %.

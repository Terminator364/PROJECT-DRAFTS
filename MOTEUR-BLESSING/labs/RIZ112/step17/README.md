# STEP17 — Audit des influences des 112 rubriques et traçabilité durable

## Règle fondatrice (CTX-0034, D035)
Le modèle ne doit pas prétendre que la présence d'une rubrique dans le JSON prouve son influence. Pour chaque variable causale admissible, établir une chaîne **donnée pré-T0 → sous-paramètres → mécanisme → contrainte/interactions → sortie Q**. La variation peut avoir un effet direct, indirect, conditionnel ou nul sous certaines conditions ; **ne jamais forcer un petit coefficient arbitraire** pour afficher une différence de 0,01 %.

Les 112 rôles comprennent 44 entrées, 37 actions, 13 politiques, 14 cibles et 4 prévisions dérivées. Une cible doit rester hors des prédicteurs ; une prévision dérivée n'est pas une nouvelle cause mesurée. Une variable inconnue ne devient jamais zéro ou une valeur supposée.

## Première preuve de perturbation, avant calibrage
Commande (à partir du répertoire `labs/RIZ112` avec sources H3+H4 présentes) :

```shell
python step17/audit_influences_112.py --output step17/RAPPORT_112_INFLUENCES_DEMO_20261017.json
python -m unittest discover -s step17 -p 'test_*.py' -q
python continuity/audit_trail.py verify
```

Pour les 112 rubriques, `REGISTRE_112_CELLULES.jsonl` conserve chaque intervention ou refus motivé. Le scanner distingue la variation **de la seule fiche** de celle **de la fiche et de la grandeur physique pré-T0 associée**, quand cette correspondance est exacte et documentée. Il ne modifie pas la source et garde un générateur déterministe pour éviter de confondre la variance de simulations et une influence des données.

**Constat initial sur scénario A** : 9 changements de l'IC_DEMO ; 6 changements d'intermédiaires sans modification de l'IC ; 35 contre-épreuves sans effet en aval observé ; 62 autres rubriques sans contre-épreuve numérique admissible, refusées ou jouant le rôle de cible/sortie/politique. Les **9 ne sont PAS des effets réels sur Q** et les 35 ne démontrent PAS une nullité physique générale ; c'est un audit du logiciel dans ces circonstances. `scientific_ic_percent=null` pour les 112.

## Clôture exigeante, pas inventée
Une rubrique d'entrée n'est vraiment reliée que si sa relation causale ou conditionnelle est exécutée, ses sources/preuves et unités sont indiquées, les interventions locales ont une traçabilité, des paramètres d'interaction ont été audités et les règles d'abstention sont respectées. Le moteur de démonstration Step16 garde son statut validé techniquement 415/415, mais la porte **influence de chaque paramètre sur la décision** reste ouverte. Un IC empirique exige encore une définition préenregistrée de Q et des essais réels contrôlés.

## Cahier mère : autorité durable, pas mémoire ChatGPT
- `CAHIER_MERE.md` : état narratif consolidé et verbatims nouvellement capturés.
- `CONTEXTE_INTEGRAL/REGISTRE_MESSAGES.jsonl` : intégralité des messages effectivement fournis au système de capture, sans résumés substitutifs.
- `journal/JOURNAL_EVENEMENTS.jsonl` : événements avec chaîne SHA-256 vérifiable ; chaque recalage doit être daté et préserver les versions antérieures.
- `step17/REGISTRE_112_CELLULES.jsonl` : les 112 cellules d'analyse et décisions d'intervention par cas.
- `continuity/audit_trail.py` : append explicite d'un message disponible + vérification du journal et du Cahier.
- `continuity/NEXT_ACTION.json` : reprise et première action, code unique `Moteur/continue`.

**Limite technique réelle** : aucun script de ce dépôt ne peut accéder automatiquement aux messages d'autres conversations ni enregistrer une session lorsque ChatGPT n'est pas en cours d'exécution. À chaque reprise, lire/contrôler le Cahier mère, puis y verser le contexte effectivement disponible. Ne pas promettre une collecte invisible continue ou une transcription historique exhaustive reconstruite. Les calculs, essais et exceptions doivent produire des artefacts d'audit plutôt que de n'exister que dans la discussion.

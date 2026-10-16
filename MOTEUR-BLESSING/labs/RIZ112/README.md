# RIZ-112 — Cahier mère + étape 5

## À lire pour une nouvelle conversation

1. **`CHECKPOINT.json`** : version, statut et prochain acte.
2. **`CAHIER_MERE.md`** : contexte, mandat, réflexions de conception, hypothèses, limites, décisions.
3. **`DECISIONS.md`** et **`journal/JOURNAL_EVENEMENTS.jsonl`** : historique des directives, réactions utilisateur et actes vérifiables.
4. **`TRANSFERT_MATRICE.md`** : critères pour réutiliser ce laboratoire dans MATRICE.
5. **`AUDIT_5_CYCLES_ETAPE5.md`** : preuves et limites de l'avancée présente.

**Code de reprise : `RIZ112|CONTINUE`**. GitHub est la source canonique de cet état : dossier `MOTEUR-BLESSING/labs/RIZ112` sur `Terminator364/PROJECT-DRAFTS/main`. Le code `MOTEUR|CONTINUE` reste pour le moteur sportif.

Le dossier `step5` contient deux nouveaux scripts exécutables et le protocole de qualité **DRAFT**. Le dossier `reference/step4` contient une copie du code et des cas JSON nécessaires ; l'archive étape 4 originale y reste conservée, sans modification. Les autres fichiers documentent et auditent les actions, sans livrer une recette.

## Exécuter

```bash
python step5/study_design.py --packet reference/step4/exemples/A_couvercle_ajuste.json
python step5/interaction_2x2.py
python -m unittest discover -s step5 -p 'test_*.py' -v
python -m unittest discover -s journal -p 'test_*.py' -v
python journal/journal_tool.py journal/JOURNAL_EVENEMENTS.jsonl
```

Test original étape 4 : consulter `reference/ORIGINAL_ETAPE4.zip` et relancer les 22 tests sous `RIZ112_ETAPE4/tests` depuis l'extraction.

Lancement sur les JSON est **en mode démonstration** : aucun IC chiffré ni Q mesuré réel ne doit être inventé. `quality_score_100` reste `null`, les résultats fictifs sont en quarantaine. Le résumé du cahier est une **reconstruction documentée de ce que l'on peut retrouver**, pas une transcription exhaustive et verbatim de toutes les conversations historiques.

**Ne pas relancer** `journal/seed_events.py` : il sert uniquement à initialiser l'historique. Pour créer une nouvelle entrée, utiliser `journal/journal_tool.py JOURNAL --event-json NOUVEL_EVENEMENT.json` puis mettre à jour le checkpoint et GitHub. Éviter les écritures concurrentes et utiliser la vérification de hash.

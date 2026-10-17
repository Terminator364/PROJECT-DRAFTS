# RIZ-112 Step19 — audit de 30 chaînes restantes (17/10/2026)

**Objectif : contrôler les routes d'influence pré-T0, pas forcer un effet sur l'IC réel.**

Source : Step18 a identifié 35 rubriques sans réponse lors des petites variations. Deux sont détectées dans d'autres régimes (036/038), trois ont maintenant des bilans de faisabilité (002/005/008). Ce lot examine les **30 autres** : 022, 023, 035, 23 actions projetées, quatre politiques conditionnelles.

## Corrections exécutables

- **035 eau planifiée / H3** : la même quantité figure dans `case_inputs['035']` et `prestart.inputs.water_added_g`. Le moteur de comparaison rejette toute divergence, refuse UNKNOWN et ne modifie les deux chemins qu'ensemble. L'ancien comportement Step16, qui ignorait une modification isolée de la fiche 035, n'est plus silencieusement accepté par `run_step19`. Le noyau H3 original reste inchangé.
- **022 ustensile** → possibilité planifiée d'égrainer (action 077); **023 récipient de service** → transfert prévu (action 081); si la ressource est explicitement absente, le **plan** indique blocage et les dépendants suivent. « Prévu » n'est pas « réellement exécuté ».
- **23 actions** : graphe de préconditions conservatif et acyclique. Variation du statut PLANNED/NOT_PLANNED peut modifier l'état d'une action ou celui de ses successeurs; aucune magnitude sur la qualité réelle n'est inférée.
- **4 politiques de correction** (086, 087, 090, 098) : prises en compte comme règles déclarées mais **non déclenchées**. Ne jamais utiliser les observations après démarrage comme prédicteurs.

## Exécution et preuves

Depuis le dossier racine de `labs/RIZ112` :

```sh
python -m unittest discover -s step19 -p 'test_*.py' -q
python step19/counterfactual_matrix.py --lab-root . --packet step6/examples/A_couvercle_ajuste_112.json --draws 100 --output step19/REPORT_30_ROUTES_20261017.json
```

**31 tests nouveaux réussis en environnement local** avant publication. Leur équivalence sur Windows doit être vérifiée séparément. Le rapport contient 30 contre-épreuves de route, **pas 30 effets sur Q**; le changement de statut d'une action est en partie tautologique mais utile pour vérifier les connexions vers ses dépendants. Les changements IC_DEMO liés à 035 relèvent uniquement de Q* synthétique du modèle H3. La mesure réelle de Q reste absente, `scientific_ic_percent=null`, et il n'est pas permis d'en déduire une réussite du riz à X %.

## Continuation

Ne pas mettre une case en « validée causalement » sans mécanisme fondé et essai observé. Prochaine porte : audit des routes physiques encore non chiffrées, statut des actions dans l'anticipation (pas dans les observations), protocole Q>=85 préenregistré et calibration sur véritables cuissons. Le **Cahier mère GitHub reste l'autorité**, avec le registre de contexte et le journal chaîné; aucune capture autonome de messages entre conversations n'est possible sans mécanisme planifié externe.

**Lancement Windows intégré** : `step19/LANCER_RIZ112_STEP19.cmd` génère A/B/C Step16, marges Step18, matrice de routes Step19 et exécute 31 tests Step19. Il quitte avec code différent de zéro en cas d’échec. Ce lanceur n’assimile pas le résultat synthétique à un IC réel.

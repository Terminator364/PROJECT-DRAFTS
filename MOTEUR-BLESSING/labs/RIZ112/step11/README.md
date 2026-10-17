# RIZ-112 : générateur de situations pré-T0 (prototype)

Objectif : générer des dossiers synthétiques **avec 112 rôles**, à comparer **avant la cuisson**, sans se faire passer pour un modèle culinaire validé.

```bash
cd RIZ112_CAHIER_MERE
python step11/scenario_factory.py --seed 20261017 --count 60 --draws 300 --out step11/SCENARIOS_60_JSON.json
python step11/test_scenario_factory.py -q
```

Les 14 objectifs post-cuisson sont **fixes** ; les quatre dérivées sont **calculées**, non tirées comme si elles étaient observées. Les 44 données initiales peuvent être observées, hypothétiques ou inconnues ; leurs rôles sont toujours tracés. Trente-sept actions et treize politiques sont conditionnelles. Les distributions de matériel et des valeurs sont **fictives**, pas tirées de données empiriques.

Les issues sont `DEMONSTRATION_ASSUMPTIONS_ONLY_NOT_REAL_Q`, `ABSTAIN_PRESTART_CONTRADICTION`, `ABSTAIN_CONTRADICTION`, `ABSTAIN_UNSUPPORTED_VESSEL`. `scientific_ic_percent` reste `null`. Le pourcentage simulé est uniquement `P(Q*_DEMO >=85 | hypothèses)`. Des variations de matériau sans équation ne modifient pas le pourcentage, sauf le refus de cas non modélisable.

**Le chiffre 119** cité par l'utilisateur ne doit pas produire des cases 113–119 sans nouvelles définitions. Les contrats actuels restent 112.

# RIZ-112 — Pré-préparation 44/44 : raccordement logiciel (23 octobre 2026)

## Résultat opérationnel

Le catalogue historique `R001…R042,R045,R047` contient **44 rubriques pré-T0**. Elles passent désormais toutes par `bridge44.evaluate44` : 44 sorties explicites typées PHYSICAL (25), PLAN (10), FEASIBILITY (2), MEASUREMENT (2), PROVENANCE (3), SAFETY (1), UNCERTAINTY (1). Chaque sortie est déterministe, documentée par une hypothèse ou une contrainte, et détecte la mutation individuelle de son entrée dans le jeu de test entièrement renseigné. **Ne pas assimiler 44 routes à 44 coefficients ou 44 effets sur Q réel.** Plusieurs facteurs décrivent l'identité d'un lot, la disponibilité d'un ustensile ou une condition de planification : ils ne reçoivent pas de bonus de qualité sans preuve.

L'entrée unifiée `pipeline44.run44` appelle d'abord `evaluate44`, contrôle les ressources et incohérences du protocole, **s'abstient** si une condition connue est impossible, puis appelle le modèle historique `step9/ic_simulation_v1.py` pour son *IC Q* exploratoire*. Aucun ancien score ni source n'a été réécrit. Les 14 sorties après T0 restent interdites en entrée; les absences restent `UNKNOWN`/null (pas 0).

## Preuves vérifiées

- GitHub Actions Python Ubuntu : [run 39938601745](https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/39938601745) — 16/16 tests unitaires, compilation et test sur vrai dossier Step6, **PASS**.
- Contrefactuels sur scénario synthétique de test : 44/44 sorties de route modifiées lors de leur mutation individuelle; cela prouve un *raccordement informatique*, pas l'effet sur la qualité du riz.
- Dossier canonique `step6/examples/A_couvercle_ajuste_112.json` : 44 routes visitées, 19 évaluables avec les informations présentes, 25 indéterminées ou inactives ; IC Q* 58 % pour 100 tirages dans cet essai d'intégration. **Ce n'est pas un IC réel, encore moins un modèle recalibré.**
- Ancienne expérience `simulations/EXPERIENCE_1000_112/` : 1000 × 112 déjà archivée et **inchangée**. Aucune campagne 1000 strict-44 n'a encore été lancée.

## Exécution reproductible

Depuis la racine `MOTEUR-BLESSING/labs/RIZ112` :

```sh
python -m unittest discover -s pret0_focus -p "test_*.py" -v
python pret0_focus/pipeline44.py step6/examples/A_couvercle_ajuste_112.json --draws 100 --seed 20261023 --output pret0_focus/RESULTAT_EXEMPLE_44.json
```

Le résultat JSON contient un reçu pour les 44 routes, les abstentions des contrôles pré-T0, l'IC exploratoire historique lorsqu'il est calculable et `scientific_ic_percent: null`.

## Limites et porte suivante

La transposition à MATRICE implique la **méthode** (gel temporel, provenance, dépendances, interactions, contrôles, abstentions, contrefactuels) mais **jamais** les coefficients culinaires. Les 44 chemins possèdent maintenant un calcul ou contrôle explicite ; ils ne possèdent pas tous un effet quantifié sur Q. Certains proxys thermiques (densité apparente, conductivité, altitude) reposent sur hypothèses explicites non calibrées. L'échelle Q réelle et les mesures de cuisine indépendantes sont toujours absentes.

**Prochaine phase attendue à la demande de l'utilisateur :** lancer une nouvelle campagne de 1 000 dossiers pré-T0 via `pipeline44`, avec audit des absences, veto de faisabilité, contrefactuels par famille, classement d'effets sur les sorties physiques versus Q* et comparaison avec les 1 000 anciens scénarios. Conserver chaque run dans un dossier versionné sans écraser l'historique.

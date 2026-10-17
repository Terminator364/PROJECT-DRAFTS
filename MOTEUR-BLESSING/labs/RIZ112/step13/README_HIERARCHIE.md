# RIZ-112 — Extension H1 : paramètres, sous-paramètres, sous-sous-paramètres et anticipations

## Mandat utilisateur D025

Une des 112 **rubriques** n'est pas une donnée atomique. Elle peut contenir plusieurs sous-paramètres, chacun avec ses sous-sous-paramètres, et de multiples anticipations conditionnelles. L'IC ne résulte pas d'une somme de 112 bonus/malus, mais de mécanismes interdépendants, avec interactions, incertitudes et contraintes. Quand deux contextes changent, la conséquence peut être différente, identique ou devenir inestimable; une absence de variation de l'IC n'autorise pas à supprimer la rubrique.

## Statut d'exécution (ne pas confondre)

- **112 / 112 rubriques** disposent d'une représentation hiérarchique initiale dans `H1_HIERARCHIE_112.json`, mais une partie reste au stade **schéma**, non de calcul physique.
- Les sous-paramètres **vraiment reliés numériquement à Q*_DEMO dans H1** portent d'abord sur `009 diamètre`, `010 matériau`, `011 épaisseur`, `013 couvercle`, `014 coefficient de fuite`, `035 eau`, `041 puissance`, `042 transfert thermique` et leurs ramifications via le noyau thermique V9.
- Les autres sous-paramètres de la structure sont des **emplacements d'observation, d'hypothèse, de plan, de politique ou de sortie**, à compléter avec des lois et preuves. Ne jamais annoncer 112 effets quantifiés.
- Aucun essai réel, aucune calibration du score réel Q, aucun IC de vraie réussite ni aucun effet sportif validé. `scientific_ic_percent=null`.

## Premier sous-modèle effectivement codé : marmite

`010 matériau -> conductivité k [W/(m K)]`; `009 diamètre d -> aire A=π(d/2)^2`; `011 épaisseur e -> résistance R_paroi=e/(kA)` ; `042 interface (R_contact, ΔT) -> P_transfert_max=ΔT/(R_paroi+R_contact)` ; `041 foyer P -> η_effectif = min(η_de_base, P_transfert_max/P)` ; le **même** moteur thermique V9 calcule ensuite eau, évaporation, température et Q*_DEMO. Les grandeurs de l'interface sont **hypothèses de démonstration**, sans mesures.

La condition `sans couvercle` déclenche une anticipation qui désactive uniquement les **actions futures incompatibles avec l'absence réelle** du couvercle, propage un multiplicateur de fuite de vapeur explicitement supposé, et recalcule Q*_DEMO. Une situation incohérente mais résoluble n'est plus bloquée par un simple nom de catégorie.

Le cas **bois non homologué exposé directement à la chauffe** est identifié comme trajectoire non sûre. La sortie 0 % est **une convention de faisabilité du modèle sûr**, pas une probabilité empirique de mauvais riz. Un **récipient bois avec insert métallique distinct** est un autre montage et passe dans le calcul thermique de l'insert, sans garantie de sécurité ou de qualité alimentaire. **Ne pas essayer de chauffer une marmite en bois non homologuée directement.**

## Hypothèses et limites

- Conductivités `k` d'ordre de grandeur, variables selon alliage, humidité, cuisson et température : cuivre 401, fer 83,5, céramique assimilée à une argile réfractaire 1,4, bois assimilé au chêne 0,16 W/(m K). Ce ne sont pas des propriétés mesurées des quatre ustensiles réels.
- Sources de données sur conductivité : https://www.engineeringtoolbox.com/thermal-conductivity-metals-d_858.html ; https://www.engineeringtoolbox.com/thermal-conductivity-d_429.html
- Hypothèses **non calibrées** de montage : résistance d'interface 0,065 K/W, température motrice 24 K, diamètre 18 cm, épaisseur 2 mm, taux de transmission de base 0,6.
- Ce calcul de conduction en régime permanent est un **prototype**. Il ne constitue ni une équation complète de casserole avec convection, radiation, chaleur spécifique, géométrie réelle, ni un conseil de sécurité alimentaire.
- `Q*_DEMO = 100×min(4 critères fictifs)` **n'est pas** `Q_réel` ni une probabilité de réussite réellement observée.
- Une rubrique peut avoir de nombreux sous-paramètres sans devoir modifier l'IC dans chaque scénario : saturation, effet conditionnel nul, obstacle limitant ou incertitude insuffisante.

## Reproduire

À la racine `RIZ112_CAHIER_MERE` :

```bash
python step13/build_hierarchy.py
python -m unittest discover -s step13 -p 'test_*.py' -v
python step13/hierarchical_engine.py --material ceramic_rated --diameter-cm 18 --wall-mm 2 --draws 500
```

L'archive complète inclut le code V12 et toutes les dépendances Python V9/V10. Sans ce corpus antérieur, le fichier H1 ne doit pas être présenté comme autonome.

## Transfert méthodologique MATRICE

La règle est transférable : **paramètre / sous-paramètre / sous-sous-paramètre / anticipation / modèle causal pré-match / trace de contribution / IC**. Ni les constantes du riz ni les probabilités de démonstration ne doivent passer dans la MATRICE sportive. Le monde sportif doit disposer de son propre graphe temporel et de calibrations indépendantes.

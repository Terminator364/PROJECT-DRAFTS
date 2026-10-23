# RIZ112 — 10 simulations PRE-T0 (440 valeurs) — 23/10/2026

**Mandat utilisateur :** réaliser d'abord 10 simulations A..J en générant 44 valeurs synthétiques pré-préparation par scénario, puis produire et conserver tous les résultats. L'expérience est un laboratoire pour la méthode pré-match de MATRICE.

## Contrat technique
- Identifiants canoniques : R001..R042, R045, R047, **44 variables**.
- Scénarios A..J : **10 situations, 440 cellules d'entrée**. Les valeurs complètes avec unités sont dans `MATRICE_44x10.csv`.
- Génération pseudo-aléatoire déterministe de graine **20261023**, tirages contraints et corrélés lorsque nécessaire : puissance/source, masse/eau, taille des grains/variété. Certains domaines ont été orientés pour étudier des situations contrastées. Aucun résultat post-T0 n'est une entrée.
- Le protocole d'actions est celui du jeu test complet `pret0_focus/test_bridge44.py`, gelé avant T0. Il est stocké dans la version locale complète des 10 paquets. Les 37 plans ne sont pas comptés dans les 440 valeurs, lesquelles représentent strictement les 44 rubriques.
- Déroulement scientifique **entièrement hypothétique**, aucun riz réellement préparé, aucun résultat sensoriel observé, aucune calibration réelle.

## Résultats calculés par le vrai moteur canonique IC44 V2

| Cas | Contraste exploré | IC_DEMO_PCT (%) |
|---|---|---:|
| A | Équilibré | 0.7268531182 |
| B | Eau insuffisante | 0.3153417356 |
| C | Chauffe faible | 0.0754995897 |
| D | Riz amidonné | 1.8853456931 |
| E | Casserole peu volumineuse | 0.1120223208 |
| F | Forte évaporation | 0.9816381081 |
| G | Énergie instable | 0.0604030525 |
| H | Conditions favorables | 2.4735166649 |
| I | Grains fragiles | 0.1643630843 |
| J | Conditions mixtes | 1.4813796447 |

**Moyenne exploratoire : 0.82763630119 %.** Le modèle multiplie sept canaux d'adéquation hypothétiques avec contraintes de faisabilité, ce qui compresse les indices. Ce n'est PAS la probabilité de réussir une cuisson ni un pari sportif. **IC_SCIENTIFIQUE_PCT = null** pour les dix.

## Audit indépendant et contre-épreuves

- Exécution locale de dix paquets complets + répétition déterministe.
- **440 contre-épreuves individuelles** de paramètres : 392 effets IC_DEMO détectés et 48 neutralités conditionnelles. La sensibilité 44/44 prouvée sur un monde complet n'implique pas 44/44 effets non nuls dans chaque monde.
- Rejeu du CSV original à partir du code canonique `ic44_v2.py` sur GitHub Actions : les 10 IC correspondent **à 10 décimales** aux sorties locales, et les 440 valeurs ont été reconnues. [Run PASS 39945875371](https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/39945875371).
- Des essais intermédiaires 39945546527 et 39945699901 avaient échoué à **publier le reçu par git rebase**, sans échouer au calcul. Le flux a été corrigé (publication du reçu via connecteur GitHub, CI readback sans push) ; l'essai final est entièrement PASS.
- La version locale téléchargable contient les paquets JSON de chaque cas, le classeur 44x10, les résultats physiques, les 440 mutations, un manifeste de SHA256 et le code local reproduisible. Le dépôt contient la matrice canonique, le script de rejeu, le reçu et ce rapport.

## Interprétation

Un champ « disponible avant préparation » peut être une propriété, une ressource ou un choix planifié. Un effet nul dans certaines conditions est légitime (stock déjà suffisant, saturation, protocole non applicable). **Ne jamais contraindre une variation artificielle de l'IC**. Les profils fictifs de lot et variété et les coefficients d'agrégation sont non calibrés. Ce laboratoire apprend des méthodes temporelles et de sensibilité pour MATRICE ; **les coefficients culinaires ne se transfèrent pas**.

## Continuité

Le Cahier mère suit **tout le projet MOTEUR**, ses demandes verbatim accessibles, changements, exécutions, preuves, échecs, limites, corrections et reprises. Le code `Moteur/continue` doit d'abord charger ce Cahier mère, `CHECKPOINT.json`, le registre d'événements et la dernière campagne, plutôt que de reconstruire de mémoire.

Le contrôle planifié ChatGPT de synchronisation a été **désactivé sur demande**. À chaque intervention active, écriture directe durable dans le projet ; les événements GitHub peuvent créer un journal de commits, mais ne contiennent pas automatiquement les messages privés ChatGPT. Cette limite est explicitement conservée.

# Audit V13 — construction / audit / contre-audit / correction / réaudit

1. **Construction.** Décomposition 112 rubriques en paramètres, sous-paramètres et sous-sous-paramètres. Ajout de propriétés du récipient et d'une chaîne de calcul physique hypothétique. Réconciliation des projets d'action avec la disponibilité effective et suppression du veto systématique « matériau non pris en charge » pour les cinq catégories déclarées.
2. **Audit initial.** Les entrées de la V12 peuvent être `null`. Le noyau V13 les interprétait initialement avec `float(None)` et plantait : **échec vérifié**. Un test de texte mal formulé a également échoué.
3. **Contre-audit.** Ajout de `ASSUMED_DEFAULTS` avec toutes les imputations de scénario publiées (`assumed_missing_inputs`). Vérification du verrou SHA des 14 cibles ; bois direct vs bois indirect ; disponibilité d'eau vs dose réelle ; débordement anticipé ; épaisseur, diamètre et conductivité ; 100 profils sans abstention automatique. Aucun événement futur n'a été injecté comme observation.
4. **Corrections.** Valeurs implicites devenues explicites, températures et rendement bornés dans le noyau pédagogique ; fer différencié du métal générique par propriété thermique, sans forcer une probabilité différente après arrondi ; scénario bois indirect séparé ; modèle de risque bois direct explicitement fictif. Ajout de la hiérarchie à trois niveaux et de la trace détaillée des 112 rôles.
5. **Réaduit final.** 241 tests antérieurs + 32 nouveaux = **273/273 PASS en Python/Linux**, y compris 100 scénarios synthétiques, contre-épreuves sur conditions initiales et cibles verrouillées. Comparaison contrôlée de 6 configurations avec 1 000 tirages par configuration, population de 100 avec 300 tirages par situation. Validation expérimentale réelle : **0 essai, 0 calibration**, IC réel absent. Ne pas promouvoir ce modèle au domaine sportif MATRICE.

## Constats adversariaux maintenus

- Le caractère générique du modèle implique plusieurs effets non quantifiés : plans ou politiques sans formulation spécifique ; certaines influences peuvent être nulles selon le contexte ; aucune preuve de 112 effets numériques indépendants.
- Le modèle ne prédit pas la qualité gustative observée. Les dimensions Q* (amidon, hydration, grain cassé, impuretés) sont des proxies inventés pour la démonstration.
- Les propriétés de conductivité seules ne valident pas le comportement réel des matériaux ni le risque de chauffe directe du bois ; la résistance thermique totale du récipient réel est bien plus complexe.
- Le registre des 998 sous-sous-paramètres est un **schéma**, pas une base de données ni un modèle entraîné.
- Les sorties numériques s'interprètent exclusivement comme `IC_DEMO_ASSUMPTIONS_ONLY`; seuil 25 % de la règle de décision ≠ qualité 85/100.

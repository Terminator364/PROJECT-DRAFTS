# H2 — Cinq passes de vérification

1. **Construction** — extension de l'interface H1 par `return_prepared_packet` strictement optionnelle ; intégration du profil du riz et de la politique 087 sous une simulation commune, sans nouvelle addition de 112 coefficients.
2. **Audit** — identification de la confusion entre simulation d'un déficit futur et observation future : tous les déclencheurs sont nommés `modeled_shortfall_not_observed`, et `post_T0_measured_values_used=0`.
3. **Contre-audit** — détection d'une consommation désynchronisée du générateur aléatoire par la branche conditionnelle, rendant la comparaison légèrement biaisée. **Correction : générateur séparé pour l'hypothèse d'exécution**, conservant les mêmes aléas physiques dans les deux trajectoires.
4. **Correction** — plafonnement dose par stock pré-T₀ (002), validation des sous-paramètres, refus de changer le rinçage sans plan (054), protection du paquet source, respect du cas non sûr bois/direct ; correction du contrôle d'exhaustivité `44+37+13+14+4=112` (les quatre dérivés ne sont pas des champs d'entrée).
5. **Réaduit** — 282/282 tests logiciels PASS, 100 scénarios synthétiques H2 exécutés et sérialisés, provenance et modèle de qualité fictive clairement libellés. Ne pas interpréter les sorties comme des taux de réussite réels.

## Règles de clôture non satisfaites

Aucune donnée de réussite du riz collectée, pas de barème Q approuvé, pas de validation thermique indépendante, ni de chemins numériques justifiés pour l'ensemble des 112 rôles. Le mandat D014 reste ouvert ; ce lot apporte **des interactions chiffrées réelles dans le programme**, pas une validation scientifique du monde physique.

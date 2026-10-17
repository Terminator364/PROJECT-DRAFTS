# H1 — Audit, contre-audit, correction et ré-audit

1. **Construction** : reprise V12 intégrale, définition de la décision D025, création de 112 entrées hiérarchiques, prototype thermique sous-paramétrique inter-rubriques.
2. **Audit** : premier test échoué parce que diamètre/épaisseur étaient `UNKNOWN` dans le JSON historique (010/009/011). Correction : ces données doivent être explicitement fournies et ne sont plus inventées silencieusement.
3. **Contre-audit** : matériaux cuivre/fer peuvent se retrouver avec le même IC sous saturation de puissance, alors que la céramique modifie la limite thermique; ceci montre l'absence de poids fixe et le rôle des autres sous-paramètres.
4. **Correction** : anticipation pour l'absence réelle de couvercle; compatibilité bois/direct traitée séparément du cas hypothétique d'un insert métal ; le 0 % pour chauffe directe non homologuée est une **convention de sécurité du modèle**, non une statistique réelle.
5. **Réaduit** : 20 tests H1 PASS, 23 tests V12 PASS. Le test de sensibilité couvre k, épaisseur, géométrie requise, eau, couvercle, déterminisme, source inchangée, et temporalité. Aucune nouvelle validation réelle de Q.

## Lacunes non résolues

- Les 112 entrées possèdent des enfants **structurels**, pas 112 lois de réponse physique ou 112 effets sur le score.
- Les anticipations des 13 politiques conditionnelles restent des contrats, leur probabilité de déclenchement et leur efficacité ne sont pas apprises.
- Le modèle de matériau nécessite les propriétés et le type d'interface de la vraie marmite ; label cuivre/fer/céramique seul est insuffisant.
- Pas de calibration, pas de données physiques mesurées, pas de validation hors échantillon ni de méthode approuvée pour Q réel.

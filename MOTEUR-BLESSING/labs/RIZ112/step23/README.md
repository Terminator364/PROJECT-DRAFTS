# Step23 — porte d'éligibilité scientifique stricte

Le validateur inspecte les preuves avant/après T0, la cohérence des empreintes et la complétude des 14 mesures. Tant que la **formule Q n'est pas préenregistrée et approuvée**, qu'il n'existe pas suffisamment de vrais essais indépendants, et qu'une calibration puis une validation hors-échantillon ne sont pas exécutées, il refuse de produire une probabilité réelle.

**Aucun score inventé**. Le seuil opérationnel d'illustration de 12 essais est **une suggestion pour amorcer un pilote, pas une taille d'échantillon statistiquement suffisante** ; une taille appropriée nécessitera une analyse de puissance adaptée à la variabilité observée.

Résultat attendu : `eligible_real_paired_trials=0`, `calibration_allowed_now=false`, `scientific_ic_percent=null`.

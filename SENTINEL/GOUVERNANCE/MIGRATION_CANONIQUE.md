# Migration canonique — décision du 26 novembre 2026

Le propriétaire demande une migration intégrale vers GitHub, puis la préparation de la correction d'autonomie, sans installation de la nouvelle version avant GO explicite.

## Autorité
- GitHub : sources, versions, documentation, tests, décisions et historique vérifié.
- PROJECT-DRAFTS est public : seulement contenu déclassifié et non sensible. Les archives privées nécessitent un dépôt GitHub privé, distinct ou zone privée de transit explicitement identifiée.
- HP : installation active, télémétrie nécessaire au fonctionnement, validations matérielles et éventuel espace de travail temporaire. Ne pas confondre ces éléments avec les anciennes copies de développement.
- Drive et ChatGPT : aucun référentiel concurrent; inventorier les copies effectivement accessibles. Ne pas supprimer les documents mixtes d'autres projets.

## Portes de migration
1. Inventorier les fichiers, versions et dépendances par origine. Ne pas fabriquer d'historique Git ancien.
2. Examiner confidentialité et intégrité; transférer vers la destination adaptée. Les secrets d'accès ne doivent jamais entrer dans Git, même privé.
3. Vérifier les empreintes SHA-256, nombres de fichiers et restauration depuis GitHub; identifier les lacunes et exclusions.
4. Supprimer seulement les copies obsolètes précisément identifiées et dont la restauration est prouvée. Préserver l'installation active, ses données utiles et une restauration exploitable.
5. Préparer la correction d'autonomie sur la base exacte B13; déploiement bloqué avant GO.

## Recette autonomie
- Réserve effective = max(seuil Windows, seuil matériel valide); 5 % observés sur le HP, sans modification du firmware ni du pourcentage Windows.
- Temps avant hibernation = max(0, énergie restante - réserve effective) / puissance estimée; unités cohérentes, seuil exact en énergie si disponible. Le pourcentage arrondi seul n'est pas suffisant.
- Adapter la puissance aux décharges récentes et à l'historique; rejeter mesures invalides, charge secteur, interruptions, variations de capacité; séparer apprentissage et validation par session chronologique.
- Comparer erreurs du modèle installé et candidat, surtout en dessous de 15 %. Confirmer hibernations via événements Windows; ne pas assimiler chaque arrêt de journal à une hibernation.
- Maintenir l'affichage existant en heures/minutes et secondes près du seuil, indiquer les estimations indisponibles et conserver un chemin de restauration.
- Cadence cible 30 s au-dessus de 15 %, 15 s entre 7 et 15 %, 5 s près du seuil, à valider selon actualisation réelle du capteur et coût.
- Pas de CI automatique ni de consommation GitHub Actions par défaut.

## État
Migration binaire/source non attestée. L'inventaire des neuf candidats n'est pas une sauvegarde. Aucun nettoyage ni déploiement autorisé par ce seul document.

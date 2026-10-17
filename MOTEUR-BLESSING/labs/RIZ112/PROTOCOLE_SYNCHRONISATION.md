# Synchronisation vérifiable — RIZ-112

Source canonique : `Terminator364/PROJECT-DRAFTS/main/MOTEUR-BLESSING/labs/RIZ112`.

**Début de chaque conversation de reprise** : lire `CHECKPOINT.json`, ce cahier, les derniers événements du journal, la liste des décisions et les preuves de tests. Vérifier le commit GitHub et la somme SHA de l'archive avant d'ouvrir les travaux. **Le code unique de continuité est `Moteur/continue`**, valable pour le moteur parent et le laboratoire; ouvrir `continuity/NEXT_ACTION.json` et commencer immédiatement le prochain travail.

**Pendant la conversation** : enregistrer dans les fichiers les hypothèses, options, comparaisons, décisions, corrections et résultats observables. Une entrée par événement ; inclure `status` (`USER_DIRECTIVE`, `HYPOTHESIS`, `IMPLEMENTED`, `TESTED`, `FAILED`, `CORRECTED`, `PENDING`, `DEFERRED`), l'origine, la preuve, et éventuellement `supersedes`. Ne pas rapporter des pensées privées : documenter **raisons, hypothèses et conclusions vérifiables**.

**Clôture** : mise à jour des checkpoints et journal sur GitHub, archive de reprise sur Drive/Bibliothèque ChatGPT quand possible, vérification de la présence et de l'intégrité, et statut PC distinct. Ne pas prétendre synchronisation permanente hors des exécutions effectives, et ne jamais bloquer le travail faute d'un miroir.

**Préservation des sources** : anciennes archives et manifests conservés en dossiers versionnés. Ne pas intégrer silencieusement RIZ-112 au dépôt MATRICE ; un lien explicite dans la matrice suffit jusqu'au gate de transfert.

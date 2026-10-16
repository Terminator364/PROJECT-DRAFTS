# Décisions et objections — RIZ-112 (suivi révisable, append-only)

| ID | Origine/date | Décision/exigence | Conséquence vérifiable | État |
|---|---|---|---|---|
| D001 | Utilisateur, 2026-10-15 (contexte antérieur) | Analogie 112 cases → 62 mondes, calculs mathématiques propres, ordre, dépendances, compensations, incompatibilités | Test d'interaction et lignée des équations, pas simple checklist | ACCEPTÉ |
| D002 | Utilisateur, 2026-10-15 | Analyse précuisson/prématch ; comparer états initiaux variables plutôt que valeurs idéales universelles | Rejeter observation post-T₀, vérifier dates | ACCEPTÉ |
| D003 | Utilisateur, 2026-10-16 | Objectif : deux portions de riz blanc moelleux à grains séparés | Cible qualité et évaluation stable | ACCEPTÉ |
| D004 | Utilisateur, 2026-10-16 | Le moteur prédit un IC depuis JSON ; ne fournit pas une recette | Pas de conseil de cuisson comme résultat primaire | ACCEPTÉ |
| D005 | Utilisateur, 2026-10-16 | Seuil de réussite 85/100, pas de score de « bonus/malus » | Probabilité conditionnelle à un Q observé et préspécifié ; IC null sinon | ACCEPTÉ |
| D006 | Retour sur MATRICE, 2026-10-16 | Une baseline Poisson présentée comme moteur intégral est une erreur | Reçu explicitant les mondes effectivement calculés ; baseline séparée | ACCEPTÉ |
| D007 | Audit étape 4, 2026-10-16 | Physique simplifiée, 15/112 cas mobilisés, amidon proxy non causal validé | Non promotion, ABSTAIN_IC_NON_CALIBRE | TESTÉ TECHNIQUE |
| D008 | Utilisateur, 2026-10-16 | Cahier mère exhaustif des décisions, feedbacks, actions, hypothèses et checkpoints inter-conversations | Fichiers canoniques GitHub + copies, journal JSONL, hash de chaque livraison | EN EXÉCUTION |
| D009 | Travail étape 5, 2026-10-16 | Pas de poids arbitraires pour Q, pas de barème approuvé présumé | Protocole qualité DRAFT avec critères observables mais coefficients non définis | PROPOSÉ / NON APPROUVÉ |

### Principe des corrections
Une correction ne remplace pas une décision antérieure dans le journal : créer une nouvelle entrée citant son ID et les éléments qui la contredisent. Conserver comme distinction principale *la demande de l'utilisateur*, *notre interprétation*, *l'implémentation testée* et *la preuve de réussite réelle*.
| D010 | Utilisateur, 2026-10-16 | Les **112 cases doivent contribuer réellement**, pas seulement les 15 du noyau initial ; synchronisation continue entre reprises | Test d'exhaustivité 112/112, trace d'opération + chemin/limite, refus de feindre 112 effets causaux | EXÉCUTÉ COMME CONTRAT / PHYSIQUE PARTIELLE |
| D011 | Contre-audit, 2026-10-16 | Contribution au protocole/gouvernance/étiquette ≠ contribution numérique au mécanisme ≠ effet prédictif validé | Reporter les trois couvertures séparément ; ne jamais promouvoir à « modèle intégral validé » | CORRECTION DE PORTÉE |
| D012 | Audit du graphe, 2026-10-16 | Les dépendances ne sont pas toutes des arcs causaux calculables : 17 labels poststart pointés à rebours, deux arcs rinçage circulaires | Exclure ces 19 arcs du DAG préstart ; ne pas cacher la nature hypothétique des 150 liens restants | TESTÉ LOGICIEL |
| D013 | Étape 7, 2026-10-16 | Une case peut être un contrôle d'admissibilité chiffré sans avoir un effet Q chiffré validé | 10 contraintes de faisabilité sans bonus/malus ; 62 cases sans chemin à Q conservées comme lacunes à résoudre | TESTÉ LOGICIEL / EFFETS SPORTIFS OU RIZ NON VALIDÉS |

| D014 | **Utilisateur — 16 octobre 2026 (correction de méthode)** | « C'est si compliqué que ça pour les faire ? Parce que là on y va par paliers. Et d'ailleurs faudrait écrire dans le cahier [mère]. » L'utilisateur conteste la progression par paliers qui ne clôt jamais l'exigence d'une contribution réelle des 112 cases. | **NE PAS** annoncer « moteur 112 complet » sur la seule couverture JSON ou le nombre de tests. Avant toute prochaine promotion de palier : tableau nominatif 112/112, effet fonctionnel réel et vérifiable (mécanisme calculé, contrainte exécutée, scénario conditionnel, cible mesurable) ; aucune case orpheline masquée. Conserver une liste explicite des lacunes non résolues, puis les traiter dans un lot cohérent, sans refaire éternellement des inventaires. La validation de l'IC scientifique reste séparée et exige des données réelles et calibration. | **DIRECTIVE ACTIVE / CLOTURE FONCTIONNELLE NON DEMONTREE** |

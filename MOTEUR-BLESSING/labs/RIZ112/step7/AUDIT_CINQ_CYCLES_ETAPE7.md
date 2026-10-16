# Étape 7 — audit, contradiction, correction, ré-audit (2026-10-16)

**Construction (cycle 1)** : réutilisation du moteur étape 6 ; couche `graph_governor.py`, gouvernance d'arcs, topologie et contraintes de faisabilité. Pas de réécriture du cœur étape 4 ni du protocole Q.

**Audit (cycle 2)** : 112 cases, 169 arcs déclarés, vérification de chaque extrémité, orientation des flux, des relations aux sorties et des cycles. Découverte : 17 arcs `PRESTART_ACTION/BRANCH_POLICY <- POSTSTART_TARGET`, 2 retours 054<-055/056.

**Contre-audit (cycle 3)** : insertion d'un arc créant une boucle → erreur ; injection d'une étiquette future → refus ; modification d'une quantité d'eau ou d'une présence de matériel → état de faisabilité mis à jour ; inconnue ≠ zéro ; ne pas transformer un `CONSISTENT` en réussite prédictive.

**Correction (cycle 4)** : les 19 arcs sont EXCLUS de la chaîne de calcul pré-T0, sans effacer les références historiques du registre V6 ; 150 arcs candidats acycliques conservés. Ajout de 10 contrôles de nécessité sur les ressources, y compris conversion eau 1g≈1mL **approximation didactique**, et capacité du récipient **condition nécessaire uniquement**.

**Ré-audit (cycle 5)** : 36 tests étape 7 PASS, et 22+31+10+42 tests précédents PASS, total 141/141 sous Python 3.13. Ancienne tentative avec mauvaise racine de découverte des tests étape 4 : échec de chargement **dû au chemin**, résolu en exécutant depuis l'arborescence source historique extraite ; aucun test d'origine modifié.

**Résultats et limites** : 112 cases décrites ; 50 avec chemin structurel hypothétique jusqu'à Q112, 62 sans chemin ; 17 chemins numériques simplifiés, dont 4 actuellement orphelins du graphe de Q ; 0 effet validé sur Q ; barème Q DRAFT ; 0 expérience de riz réelle ; IC null ; aucun test Windows V7. Test logiciel et couverture documentaire ne signifient pas compétence prédictive ou causalité validée.

**Prochaines portes** : proposer des hypothèses justifiées et mesurables pour les 62 cas orphelins, conserver les cases de sortie hors des entrées ; approuver et préenregistrer le protocole Q, produire des essais répétés avant de calibrer l'IC. Ne pas transposer les coefficients de ce prototype physique vers MATRICE.

# MOTEUR RIZ112 — Audit de rejeu intégral 1 000 × 44, V3.1 (2026-10-23)

## Demande utilisateur

L'utilisateur exige de prouver que **1 000 scénarios différents**, chacun doté de **44 paramètres pré-préparation générés selon un protocole aléatoire cohérent**, ont **chacun effectivement fait fonctionner le moteur**, obtenu **un IC**, et ne sont pas seulement des lignes préremplies. L'audit approfondit le moteur existant **sans le reconstruire**. Cette demande fait suite à D046, qui annonçait une campagne 1 000 × 44, 128 tirages par scénario.

## Vérification indépendante (source sauvegardée)

Le nouveau vérificateur complet, `VERIFICATEUR_1000x44_INTEGRAL.py`, est inclus dans la preuve du tour. Il lit les CSV d'origine `output/combined/INPUTS_1000x44.csv` et `RESULTATS_1000_IC_V3.csv` **sans les réécrire**. Pour chaque identifiant S0001…S1000 :

1. il compare les 44 valeurs enregistrées avec les valeurs régénérées **uniquement depuis la graine 20261023 et les règles antérieures** ;
2. il reconstruit son paquet avant T0 selon `generate_v3._apply` ;
3. il exécute de nouveau le vrai `ic44_v3.simulate` avec **128 tirages Monte Carlo et la graine historique propre au scénario** ;
4. il compare **à l'identique** le nombre de réussites simulées, `Qstar_nominal`, l'IC et le statut ;
5. il vérifie les SHA-256 des deux fichiers et les 29 empreintes du package initial.

**Résultat final : 1 000/1 000 rejeux, 44 000/44 000 paramètres régénérés à l'identique, 128 000 tirages refaits, 0 écart de sortie, 0 écart de génération, 1 000/1 000 combinaisons uniques, 44/44 paramètres variant dans la campagne, 29/29 fichiers de manifeste valides, 15/15 tests V3 réussis.** Le rejeu local complet dure environ 103 secondes (à ne pas confondre avec une mesure sur le PC personnel de l'utilisateur).

[Reçu JSON](PREUVE_REJEU_EXACT_1000x44_20261023.json) — sources du moteur et fichier complet d'entrées dans le package V3.1 disponible depuis le checkpoint Drive `1RnLc0cQNfRtwSznlyq77vNyI0LE5cbHY` (aucune modification).

## Important : 1 000 calculs ne signifient pas 1 000 nombres d'IC différents

- **1 000 combinaisons de paramètres uniques** ;
- **1 000 calculs du moteur exécutés** et **1 000 IC renseignés** ;
- **95 valeurs numériques distinctes** de l'IC, car chaque scénario comporte 128 essais : la fréquence varie par incréments d'environ 0,78125 point ;
- **798 IC affichés à 0 %**, soit zéro succès sur 128 essais, non la preuve d'une impossibilité réelle ;
- **202 IC strictement positifs**, **33 ≥80 %**, **21 ≥85 %** et un maximum de **95,312 %** ;
- les cinq types de contextes **200 chacun** étaient définis avant le calcul, sans refléter la distribution réelle des préparations.

## Architecture et conservation

Le contrat stable est **1 cas = 44 entrées avant T0 + 1 paquets de plans déterministes + mécanismes physiques + 128 tirages d'incertitude → Q*/100 et IC* du modèle**. Les 44 champs varient dans la campagne, mais certaines combinaisons sont corrélées pour préserver la cohérence (eau prévue vs masse, foyer vs source énergétique) ; ne pas les qualifier de 44 tirages indépendants. Chaque entrée peut avoir un effet **conditionnel** sur l'IC ; le fichier témoin V3.1 donne 44 exemples, pas une obligation de variation de tous les IC de toutes les situations.

La **porte logicielle de reproductibilité de la campagne 1 000×44 est close (PASS)**. Restent à auditer séparément : la justesse du modèle physique, la pertinence des lois aléatoires, la sensibilité au choix de 128 tirages, la calibration réelle et le transfert des **méthodes** à MATRICE. Aucun coefficient du riz ne doit être copié pour prédire les Over 1,5. **IC scientifique = null**.

## Protocole de reprise

Le Cahier mère de **tout MOTEUR** et `CHECKPOINT.json` doivent pointer vers le présent rapport, conserver le message utilisateur, cette vérification, le statut de chaque gate et les limites, puis utiliser `Moteur/continue` pour relire les artefacts au lieu de regénérer les 1 000 dossiers. Le code original et les anciens résultats V1/V2/1000×112 restent inchangés.

**Travaux ultérieurs proposés (non déclarés exécutés) :** qualification Monte Carlo adaptative/augmentation des tirages pour les IC rares ou proches d'un seuil ; tests de défaillance du générateur et lecture de chaque entrée ; confrontation aux données physiques expérimentales si elles deviennent disponibles.

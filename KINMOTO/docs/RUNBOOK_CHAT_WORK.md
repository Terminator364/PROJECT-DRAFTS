# KIN MOTO | MANUEL OPÉRATIONNEL CHATGPT - WORK - GITHUB

**Édition :** FACTORY 3.0 — 4 novembre 2026  
**Objet :** rendre la délégation prévisible, mesurable, peu coûteuse en quota et reproductible entre conversations.  
**Statut :** méthode proposée ; aucune automatisation persistante ni dépôt nouveau n'est créée par ce fichier.

## 1. Principe fondamental : le commanditaire parle, l'atelier exécute

L'utilisateur conserve une **conversation principale de pilotage** dans son Projet ChatGPT. Il y parle naturellement. Le pilote doit comprendre les objectifs, décomposer les demandes, identifier les contradictions et conserver les arbitrages. Le commanditaire n'a pas à connaître la structure du code pour demander « la moto flotte », « le trafic ne réagit pas », « on dégrade les graphismes » ou « améliore les missions ».

L'atelier **ne prétend pas** que le chat de pilotage et une session Work partagent automatiquement l'état de toutes leurs opérations. Le transfert est explicite : issues GitHub, branche, commit, rapport, fichier d'état et lien de prévisualisation. Work n'agit pas en arrière-plan sur une autre discussion par simple instruction prononcée ici. L'utilisateur peut entrer en Work depuis son Projet lorsque la mission exige navigateur, ordinateur ou code, puis les résultats sont récupérés depuis les outils connectés ou les fichiers réellement présents.

### Chemin d'une nouvelle idée

| Étape | Action | Artefact |
|---|---|---|
| 1 | L'utilisateur exprime librement l'idée ou la critique | Message de pilotage |
| 2 | Le pilote reformule le changement et classe son impact | Note courte de décision |
| 3 | Il cherche s'il existe déjà un module libre réutilisable | Note de sourcing |
| 4 | Il prépare un ticket borné avec risques/tests | Issue ou ticket Markdown |
| 5 | Work exécute dans une branche dédiée | Commit/PR et captures |
| 6 | Audit contradictoire, automatique puis visuel | Verdict QA avec preuves |
| 7 | L'utilisateur joue en PREVIEW et décide | Acceptation ou refus |
| 8 | L'état et le backlog sont mis à jour | `PROJECT_STATE.json`, `DECISIONS.md` |

## 2. Huit corps de travail sans agents fantômes

| Corps | Responsable fonctionnel | Livrables | Contrôle contradictoire |
|---|---|---|---|
| Direction produit | Conversation pilote | Vision, critères, priorités, arbitrages | Utilisateur |
| Architecture | Work/Codex, mission isolée | Diagrammes, APIs, dépendances, POC | QA architecture |
| Conduite/physique | Work/Codex, mission isolée | Contrôleur moto, paramètres, pistes tests | Tests + joueur |
| Art/3D/animations | Work/Codex, mission isolée | Assets intégrés, atlas, captures | Audit licences + visuel |
| Monde/traffic/missions | Work/Codex, lots distincts | Routes, agents, interactions, missions | Tests scénarios adverses |
| Performance/compatibilité | Work + essais matériels | FPS, RAM, profils, captures, logs | Contre-benchmark indépendant |
| QA/sécurité/licences | Pilote/outil d'audit | Matrices, vérifications, avis GO/NO-GO | Relecture non identique à l'implémentation |
| Intégration/livraison | Work ou outil GitHub | PR, tag, build, source ZIP, preview | Utilisateur pour STABLE |

« Corps » désigne un rôle et un type de ticket ; **ce n'est pas une promesse de huit IA actives simultanément**. Pour éviter les conflits, un seul corps modifie une zone de code partagée au même moment, ou des branches indépendantes sont fusionnées de manière ordonnée après revue.

## 3. Mandat Work : contrat standard de mission

Un ticket doit avoir au maximum un objectif principal, une zone de code ou d'assets clairement visée, des préconditions, des tests et un arrêt sûr. Les grandes missions sont découpées avant l'exécution ; l'opérateur ne s'arrête pas à chaque erreur de compilation, il la corrige dans le périmètre autorisé.

**Modèle prêt à transmettre :**

```text
KINMOTO | WORK | TICKET <ID>
MISSION : <un résultat concret>.
SOURCE CANONIQUE : dépôt <URL>, branche <nom>, commit de référence <SHA>.
LIRE D'ABORD : README.md ; PROJECT_STATE.json ; docs/CHARTER.md ; ticket ; tests pertinents.
CONTRAINTES : 0 FC ; aucune API facturée ; pas de modifications sur STABLE ; conserver Android/PC ; pas de régression graphique ; pas de secrets dans commits.
PÉRIMÈTRE MODIFIABLE : <répertoires/fichiers/modules>.
HORS PÉRIMÈTRE : <liste>.
ACCEPTATION : <3-8 conditions objectivement vérifiables>.
TESTS : <commandes locales/CI + capture vraie 3D si changement visuel>.
PREUVES : commit, diff, logs, screenshots, mesures, liste des licences.
GESTION BLOCAGE : contourner les difficultés techniques gratuites dans le mandat ; s'arrêter si coût, secret, suppression permanente ou modification de publication requise.
SORTIE : statut PASS/FAIL/BLOCKED/NOT_TESTED, rapport, prochain ticket possible.
N'ANNONCE PAS « TERMINÉ » SANS PREUVES. Ne travaille pas hors du présent mandat.
```

### Contrat d'autonomie

| Action | Règle |
|---|---|
| Lire fichiers et tester en local | Autorisé dans le ticket |
| Éditer fichiers du périmètre | Autorisé sur branche de développement |
| Installer dépendances gratuites documentées | Autorisé après contrôle licences/risques |
| Réparer compilation/tests | Autorisé, re-tester et documenter |
| Changer de moteur ou de base libre | Proposition, pas substitution silencieuse |
| Supprimer le code historique | Interdit sans archivage et autorisation |
| Ajouter un service facturé | Interdit |
| Publier sur URL STABLE | Approbation explicite du commanditaire |
| Pousser des secrets dans GitHub | Interdit |
| Lancer 10 tâches parallèles coûteuses en quota | Interdit par défaut |

## 4. Le pilote : politique de conversation

**Entrées acceptées :** idées imprécises, critiques, courtes phrases vocales transcrites, captures, vidéos de gameplay, questions, demandes explicites de lancement, codes de reprise. Le pilote ne doit pas exiger un formulaire avant de répondre. Il recherche les éléments déjà connus avant de demander une précision.

**Les réponses du pilote doivent contenir quand utile :** ce qui est constaté, la cause possible versus démontrée, l'impact, la décision recommandée et la prochaine action réalisable. Pas de statut « professionnel » ou « prêt » sans mesure. Il ne prétend pas avoir une mission Work terminée s'il n'a pas consulté sa livraison.

**À la fin d'une discussion de conception**, le pilote peut produire un ticket et une note de décision. **À la fin d'une mission de code**, l'opérateur doit produire un résultat exécutable, pas seulement une description. **Au passage en STABLE**, seul l'accord de l'utilisateur transforme la candidate en version officielle.

### Exemple de prise en charge d'une critique

« La moto glisse sur l'eau » devient : ticket PHYS-004, reproduire sur piste canonique, capturer position/contact roue/sol, contrôler latence entrée→yaw, relier inclinaison et courbe, benchmarke à 30 FPS, comparer avant/après ; le ticket est clos seulement quand la sensation s'améliore à l'essai réel. Ne pas corriger uniquement l'accélération pour masquer le bug.

« Le graphisme a baissé » devient : ticket ART-007, captures identiques avant/après, données de zoom/lumière/LOD/rendu, vérifier éventuel fallback Canvas, mesurer FPS ; refus si l'image perd en qualité sans raison clairement approuvée.

## 5. Gouvernance du quota et de la batterie

### Faits actualisés au 4 nov. 2026

- La documentation OpenAI décrit un quota inclus **partagé par Work et Codex**, modulé par les modèles, la complexité et le type d'exécution.
- Le solde réel se vérifie dans **Paramètres > Utilisation** ; un plafond de cinq heures et/ou hebdomadaire peut s'appliquer.
- Les tâches cloud peuvent consommer plus d'allocation qu'une tâche locale. Les appels API externes sont une dépense distincte.
- OpenAI annonce une évolution du mode de décompte à partir de décembre 2026 ; recontrôler les règles avant grosses sessions.
- Il est impossible de garantir un nombre de tâches disponibles à partir du seul libellé « Plus ».

### Protocole d'économie

1. Le pilote prépare le ticket, lit les docs existantes et joint uniquement les fichiers utiles.
2. L'opérateur choisit l'approche la moins coûteuse **qui préserve la fiabilité** : correction ciblée avant reconstruction, tests locaux avant sessions cloud répétées.
3. Les opérations déterministes sont exécutées par scripts : lint, tests, génération de captures, analyse statique, vérification hashes.
4. Un lot doit finir sur un état commité même si l'objectif complet reste partiel ; on évite de perdre des heures d'exécution.
5. Avant mission longue, consulter le quota réel. Si inconnu, limiter la mission au premier résultat mesurable et documenter l'arrêt.
6. Le pilote n'invente pas des pourcentages de quota et ne promet pas de continuité autonome après la fin d'une session.
7. Aucun achat de crédits, upgrade ou API facturée n'est accepté ; un blocage de quota est géré par planification ou changement de méthode gratuite.

**Échelle indicative interne** : grosse tâche = architecture/compilation/intégration complète ; moyenne = un module avec tests ; petite = revue PR, corrections UI, audit licences. Cette échelle n'est pas une tarification officielle.

## 6. Branches, CI et flux d'intégration

**Proposition :** `main` = dernière version acceptée et stable ; `develop` = intégration ; `feature/<ticket>` = modifications ; `release/v1-rcN` = candidate. Les noms sont modifiables mais les rôles restent distincts.

**Étapes :** branche → modification → tests → PR → QA indépendant → PREVIEW → essai utilisateur → décision GO/NO-GO → tag immuable → STABLE. Interdiction de publier la branche `develop` en tant que lien public officiel par défaut.

**Contenu minimal d'une PR :** description, raison, liens source/issue, captures avant/après si visuel, liste licences, tests PASS/FAIL/BLOCKED, benchmark si impact GPU/CPU, notes de migration de sauvegarde.

**CI gratuite minimale :** installation reproductible, typecheck/lint, tests unitaires moteur et sauvegarde, tests de licence/inventaire, génération de build statique, contrôle taille des bundles. Les tests WebGL physiques Android/iPhone nécessitent un vrai appareil ; ne pas les compter comme passés en CI.

**Coût GitHub Actions :** runners standards publics gratuits selon les conditions actuelles ; dépôts privés sous quota inclus et possibilité de coûts au-delà selon configuration. Contrôler les réglages de facturation/limites avant activation ; pas d'usage sur des runners payants.

## 7. État de projet obligatoire après chaque session

`PROJECT_STATE.json` doit conserver l'état unique **machine-readable**. Ne pas remplir les champs manquants avec des conjectures.

```json
{
  "schema_version": "1.0",
  "project": "KINMOTO",
  "state_date_utc": null,
  "current_major_release": null,
  "canonical_repo_url": null,
  "stable_commit": null,
  "develop_commit": null,
  "active_ticket": null,
  "active_branch": null,
  "work_session_id": null,
  "quota_snapshot": {"known": false, "source": "Settings > Usage", "recorded_at": null},
  "completed_tickets": [],
  "pending_tickets": [],
  "qa_latest": {"report_path": null, "logic": "NOT_TESTED", "visual": "NOT_TESTED", "performance": "NOT_TESTED", "physical": "NOT_TESTED"},
  "known_blockers": [],
  "release_candidate": null,
  "next_action": "Désigner le dépôt et lancer l'audit comparatif des bases libres"
}
```

Les statuts `NOT_TESTED`, `BLOCKED`, `FAIL`, `PASS` sont en majuscules sans interprétation. **Un champ nul signifie inconnu ou non encore établi**, pas une tâche oubliée.

### `NEXT_ACTION.md` obligatoire

Le fichier doit contenir : objectif unique, raison, point de départ commit, fichiers de contexte, dépendances, commande de test, preuve attendue, condition d'arrêt. Il sert de relais au nouveau chat même si tous les anciens échanges sont indisponibles.

### `SESSION_LOGS/YYYYMMDD-ID.md`

- Début : ticket, branche/commit, décisions et risques.
- Opérations réalisées : commandes ou modifications majeures, sans secrets.
- Tests et captures : versions et liens de preuve.
- État final : ce qui marche et ce qui échoue ; non-testé explicitement.
- Next : reprise exacte, aucun travail futur prétendument déjà effectué.

## 8. Révisions contradictoires (« audit / contre-audit »)

Les audits ne doivent pas être une répétition de la même liste avec de nouvelles formules. Un audit indépendant examine les **hypothèses adverses** : « Si la moto flotte encore ? », « si la capture de QA est en 2D ? », « si la mémoire monte après 20 minutes ? », « si les licences d'assets diffèrent de la licence du dépôt ? ».

### Exemples de preuves indépendantes

- Le test moteur passe en Node ; le contre-test vérifie la scène WebGL réelle sur PC.
- Une image est plus jolie ; le contre-test compare FPS et visibilité des commandes en mode Eco.
- Un projet Github déclare MIT ; le contre-test lit aussi `ATTRIBUTION.md`, dossier assets, dépendances et notices.
- Un build se charge en HTTPS ; le contre-test coupe le réseau, recharge et termine une mission hors ligne.
- La mission est marquée terminée ; le contre-test tente de déclencher une seconde fois le paiement.
- L'émulation Android passe ; le contre-test exige de jouer sur le Galaxy A21s réel.

Pour chaque tâche importante, conserver au moins une preuve **qui aurait pu invalider l'implémentation**.

## 9. Échanges entre pilote et Work : format de rapport de retour

```text
KINMOTO | RAPPORT DE MISSION
Ticket / branche / commit :
Mandat reçu :
Fichiers modifiés :
Code réutilisé / licences :
Tests exécutés avec commandes exactes :
Preuves graphiques (image, capture, vidéo) :
Appareils réellement testés :
Résultat G1 logique : PASS / FAIL / BLOCKED / NOT_TESTED
Résultat G2 visuel : PASS / FAIL / BLOCKED / NOT_TESTED
Résultat G3 performance : PASS / FAIL / BLOCKED / NOT_TESTED
Résultat G4 matériel : PASS / FAIL / BLOCKED / NOT_TESTED
Risques ou erreurs résiduels :
Lien PREVIEW (pas STABLE) :
Décisions à faire approuver :
Next action reproductible :
```

Le pilote vérifie ce rapport contre le commit et les fichiers quand l'accès le permet. S'il ne peut pas accéder à un livrable, il écrit **non vérifié** et indique la source manquante ; il ne simule pas une inspection.

## 10. Préparation de l'atelier A0 : ticket initial borné

```text
KINMOTO | A0 | FACTORY-SETUP
Objet : installer l'architecture de travail, PAS reconstruire le jeu.
- Désigner ou créer le dépôt canonique sans écraser les versions anciennes.
- Archiver les ZIP historiques avec empreintes SHA-256 et statuts « prototype non validé ».
- Installer docs/CHARTER.md, RUNBOOK, QA, PROJECT_STATE.json, NEXT_ACTION.md.
- Configurer une CI minimale gratuite, sans dépenses éventuelles, sur branche d'essai.
- Ouvrir un registre de sources libres, lire licences et attribution.
- Créer les tickets A1 benchmark comparatif, A2 sensation moto, A3 vertical slice.
- Exécuter une simulation de reprise : nouvelle session lit le repo et retrouve le prochain ticket.
Interdictions : toucher à l'URL STABLE, refaire le jeu, facturer, supprimer des prototypes.
Livrable : dépôt/commit vérifié, arbre de fichiers, rapport CI, notes sur accès/quota, compte rendu A0.
```

**Important :** la création de ce manuel n'exécute pas A0. Les actions de GitHub / Work nécessitent réellement un contexte d'exécution, des outils et parfois une approbation de l'utilisateur.

## 11. Réunions de version et validation du commanditaire

Pas de calendrier artificiel. Une revue de jalon exige un lien PREVIEW, un diff visuel, une vidéo courte de la conduite, les tests, les limites restantes et une fiche de notes joueur. L'utilisateur peut répondre **ACCEPTER**, **REFUSER**, **ACCEPTER AVEC RÉSERVES**, ou **DEMANDER CORRECTION**. Par défaut : un silence n'est pas une approbation. Les critiques deviennent des tickets reliés à la release candidate.

## 12. Questions qui ne doivent plus être reposées

- « Veux-tu dépenser un peu ? » → Non, 0 FC supplémentaires obligatoires.
- « Faut-il publier chaque jour ? » → Non, trois versions majeures, previews internes.
- « Faut-il reconstruire d'une page blanche ? » → Non, auditer les sources libres d'abord.
- « L'ancienne V1 est-elle satisfaisante ? » → Non, livraison technique ≠ acceptation produit.
- « Faut-il que tu codes personnellement ? » → Non, l'assistant et ses outils portent la technique.
- « Le jeu cible-t-il uniquement Android ? » → Non, Android/PC en priorité, iPhone dans la cible commune.
- « Le lancement d'une mission Work implique-t-il que ChatGPT ici voit tous les résultats ? » → Non, relire les artefacts via outils/sources.

## 13. Sources de méthode (revues le 4 nov. 2026)

- https://help.openai.com/fr-fr/articles/20001275-chatgpt-work-and-codex
- https://help.openai.com/fr-fr/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex
- https://help.openai.com/en/articles/20001625-understanding-chatgpt-and-codex-usage-limits
- https://docs.github.com/fr/actions/concepts/billing-and-usage
- https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Offline_and_background_operation

**Fin du manuel opérationnel.**

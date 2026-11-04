# KIN MOTO | ANNEXE DE CONTRE-AUDIT TECHNIQUE ET QUALITÉ

**Édition :** FACTORY 3.0 — 4 novembre 2026  
**Objet :** distinguer les faits démontrés, les hypothèses, les risques de licences et le véritable critère de réussite d'une V1.  
**Statut :** référentiel de vérification ; aucun benchmark physique nouveau n'a été effectué pour ce document.

## 1. Verdict contradictoire de la stratégie initiale

**Fausse assurance n°1 :** « 20 ou 42 tests réussis = jeu fini ». En réalité, les tests précités privilégiaient les règles de simulation et des profils graphiques simulés. Ils ne prouvaient pas la qualité de l'image ou les sensations sur Android.

**Fausse assurance n°2 :** « On peut créer une ville énorme en JSON gratuitement ». Les données peuvent être nombreuses, mais chaque modèle 3D, texture, transformation, IA et collision coûte CPU/GPU/RAM ; ce coût doit être mesuré. La génération procédurale aide seulement si les règles, assets et niveaux de détail sont contrôlés.

**Fausse assurance n°3 :** « Une licence MIT du dépôt couvre tous les fichiers ». Le code, les textures, les modèles, les sons, les polices et les données externes peuvent relever de licences différentes. Le droit de redistribution doit être documenté fichier par fichier.

**Fausse assurance n°4 :** « Un clone open source est une base automatiquement meilleure ». Une base lourde, inadaptée au tactile ou avec 270 Mo d'assets peut être moins appropriée qu'un noyau léger. Elle doit gagner un benchmark comparatif.

**Fausse assurance n°5 :** « Zéro coût hébergeur aujourd'hui = gratuit à jamais ». Les offres et les conditions changent. Le jeu doit être construit en fichiers statiques portables, migrables sans dépendre d'une plateforme.

**Fausse assurance n°6 :** « Une PWA est une application native ». Elle peut être installable et fonctionner hors ligne, mais dépend de Safari/Chrome/Opera et des politiques de stockage. Aucune promesse sur toutes les versions d'iOS sans essai.

## 2. Inventaire des preuves historiques

| Fait | Source matérielle | Statut exact |
|---|---|---|
| Ancien jeu V0.4, base WebGL + Canvas | Archive V0.4 et audit directeur | Projet existant, ressenti non validé |
| 42/42 contrôles de V0.4 | Rapport tests v0.4 | Réussite logique/2D simulée, pas certificat WebGL mobile |
| V1 livrée le 4 novembre | `KIN_MOTO_V1_FINAL_ANDROID_PC_20261104.zip` | Build publié, code présent |
| Tests V1 | `docs/QA_REPORT.json` | 17 unitaires, 3 SW, profils UI avec rendu simulé |
| 3D sur HP | Rapport V1 / capture mentionnée | Observation déclarée ; benchmark RAM long non inclus |
| Android physique | Rapport V1 | `NOT_TESTED` |
| iPhone physique | Rapport V1 | `NOT_TESTED` |
| Offline physique | Rapport V1 | `NOT_TESTED` |
| Acceptation produit | Retours explicites utilisateur | **REFUSÉE** : visuels, moto flottante, progression décevante |

**Une « preuve déclarée dans le rapport » n'est pas une mesure reproduite dans la préparation de cette annexe.** Elle reste étiquetée selon sa source.

## 3. Matrice de benchmark source avant réemploi

| Mesure | Méthode standard | Seuil/condition provisoire |
|---|---|---|
| Pilotage | Piste : ligne droite, slalom, freinage, virage | Pas de flottement visible, commandes prévisibles |
| Latence entrée | Test touch/keyboard en séquence | Perceptuellement acceptable, consignée |
| Contact roue/sol | Capture ralentie virage + arrêt | Alignement crédible et stable |
| Rendu WebGL | Capture avec indicateur de mode réel | Aucun fallback silencieux déclaré « 3D » |
| FPS | 10 min de jeu sur même parcours | Cible initiale 24–30 FPS sur téléphone modeste, à confirmer |
| Variabilité FPS | Étude des baisses, pauses et entrées | Pas de gel qui empêche une collision évitable |
| RAM | Moniteur OS/navigateur quand accessible | Pas d'accroissement continu, crash ou rechargement |
| Batterie | Session chronométrée équivalente | Pas de chauffe ou décharge déraisonnable |
| Taille bundle | Somme des fichiers de première charge | Minimal pour accès par forfait mobile |
| Offline | Télécharger, mode avion, relancer, mission | Jeu complet sans dépendance réseau après cache |
| Sauvegarde | Export → fermeture → import → reprise | Pas de perte d'argent, mission ni upgrades |
| Licence | `LICENCES.md` / `ASSET_LICENSES.csv` | Aucune source essentielle inconnue |

**Valeurs chiffrées :** ne pas figer 200 Mio ou 60 FPS comme engagements absolus sans benchmark réel. Le navigateur peut ne pas fournir une métrique CPU/GPU mémoire homogène sur toutes les plateformes. Privilégier trace d'éviction, FPS, fluidité ressentie, hausse mémoire et contexte de mesure.

## 4. Sources libres examinées et réserves

### 4.1 Costa Vista — fastrouter/experiments-costa-vista

Page : https://github.com/fastrouter/experiments-costa-vista

- README : moteur Three.js + Rapier, TypeScript/Vite, ville ouverte, moto, taxi, garage, météo, PWA.
- Le dépôt indique environ 270 Mo d'assets ; les commandes mobiles existent mais des fonctions restent clavier uniquement.
- Mention explicite : **MIT pour le code** ; assets crédités dans `ATTRIBUTION.md` et packs externes. L'importation de toute la bibliothèque exige audit distinct.
- **Verdict : CANDIDAT**, non sélectionné. Piste : moteur moto/physique, mission taxi et carte, à tester séparément.

### 4.2 Neon Mayhem — pranshuparmar/neon-mayhem

Page : https://github.com/pranshuparmar/neon-mayhem

- README : Three.js vanilla, navigateur, jouable hors ligne, activités taxi/livraison, motos, contrôles touch/clavier.
- Licence Apache-2.0 publiée au dépôt. Vérifier les ressources et mentions individuelles avant extraction.
- Il décrit un compteur anonyme de visites sur la version publique, désactivé pour localhost/offline selon son README : **KIN MOTO ne doit pas importer cette télémétrie par défaut**.
- **Verdict : CANDIDAT**, non sélectionné. Piste : architecture statique, tactile, missions et système de navigation.

### 4.3 Packs Kenney vérifiés sur pages officielles

- https://kenney.nl/assets/car-kit — 45 fichiers, **CC0** affiché par le site ; pas une garantie de bonne direction artistique sans conversion et harmonisation.
- https://kenney.nl/assets/city-kit-roads — 90 fichiers, **CC0** affiché par le site ; utile pour intersections/routes.
- https://kenney.nl/assets/city-kit-suburban — pack résidentiel, **CC0** affiché par le site.
- Autres sources éventuelles : **ne pas inférer** une licence à partir du nom du site ou du format du fichier.

### 4.4 Inventaire obligatoire pour chaque asset retenu

```text
asset_id;chemin;type;nom;url_source;commit_ou_version;auteur;licence;preuve_licence;
modifications;attribution_requise;poids_octets;usage;statut_legal;statut_performance
```

**Statuts :** `CANDIDATE`, `APPROVED`, `REJECTED`, `MISSING_EVIDENCE`. Aucune asset indispensable ne doit être `MISSING_EVIDENCE` à la release.

## 5. Comparaison des bases : ne pas élire le vainqueur sur description

### Phase zéro — Données à relever

- Date et commit du dépôt ; versions dépendances ; possibilité de build offline ; ressources externes chargées au démarrage ; licences sources et assets ; taille du premier téléchargement ; complexité du code.
- Contrôle de la confidentialité : vérifier s'il y a analytics, publicités, paiements, appels HTTP non indispensables ou collecte des événements.
- Taille effective de l'application **après** extraction des fonctionnalités pertinentes, pas seulement la taille du dépôt.

### Phase un — Protocole sur appareils

**HP Windows :** Opera et au moins un autre navigateur ; graphique intégré ; même parcours ; mesurer FPS, CPU/RAM système si accessible, rendu et latence commandes.

**Android modeste :** Galaxy A21s, profil Eco ; vrai Chrome ; 15–20 min, trafic et collision, mise en veille/reprise, hors ligne après cache.

**Android plus puissant :** profil Balanced, mêmes scènes, comparer gains sans changer la physique.

**iPhone :** avant de déclarer la cible officielle atteinte, Safari réel, test touch, WebGL et cache ; modèle/version connus seulement après relevé, jamais devinés.

### Phase deux — Score 100 points

| Critère | Max | Résultat à saisir |
|---|---:|---|
| Pilotage et contact au sol | 30 | `NOT_TESTED` |
| Qualité visuelle et animation | 20 | `NOT_TESTED` |
| Performance, RAM et taille | 20 | `NOT_TESTED` |
| Modularité et réutilisation | 15 | `NOT_TESTED` |
| Licence / absence de coût | 10 | `NOT_TESTED` |
| Missions / sauvegarde | 5 | `NOT_TESTED` |

Les critères juridiques, financiers et de compatibilité sont **éliminatoires**, même en cas de score élevé.

## 6. Moteur moto : scénarios et conditions de non-régression

| Scénario | Erreur historique | Exigence de résultat |
|---|---|---|
| Appui gauche | Virage à droite observé anciennement | Trajectoire visible vers gauche, toutes caméras |
| Démarrage | Moto qui « patine » ou glisse | Accélération progressive, roues tournent, ombre ancrée |
| Virage lent | Rotation brusque sur l'axe | Courbure contrôlée, vitesse/angle cohérents |
| Virage rapide | Léger pivot latéral sans dynamique | Inclinaison raccordée à trajectoire, récupération stable |
| Freinage | Diminution de compteur sans réaction | Décélération et transfert visuel/son appropriés |
| Collision voiture | Objets se traversent ou flottent | Contact, séparation, dégâts/ralentissement, réaction IA |
| Caméra | Influence la physique ou inverse commandes | Caméra indépendante, direction universelle |
| FPS variable | Moto change de vitesse à 20 FPS | Simulation fixe ou indépendante du rendu |

**Test subjectif minimum :** le commanditaire joue 15 minutes sur son HP et Android, commente à voix libre. Les anomalies sont transformées en tickets avec vidéo/séquence si possible. Une bonne note technique ne compense pas une mauvaise sensation.

## 7. Ville, circulation et missions : simulation sous budget

La V1 ne doit pas afficher des milliers de personnages. Utiliser quelques véhicules proches détaillés, agrégation des circulations distantes, graphes routiers, caméras stables, et les meilleures ressources gratuites disponibles. Une route stylisée mais cohérente et bien texturée vaut mieux que des dizaines de kilomètres vides.

**Voitures :** perception d'obstacle, distance de sécurité, respect des intersections, freinage, reprise, réaction aux chocs. **Missions :** client et destination accessibles, transitions d'états, argent payé une seule fois, pas de mission bloquée par collision ou par itinéraire inexistant. **Animations :** conducteur posture, guidon, roues, ressort, interaction client visuellement plausible.

## 8. Tests de mise à jour et sécurité PWA

1. Précharger les ressources nécessaires, couper le réseau, fermer/réouvrir, jouer une mission.
2. Déclencher une mise à jour PREVIEW pendant une mission ; vérifier qu'elle n'interrompt pas la partie.
3. Sauvegarder et exporter, passer d'un schéma de sauvegarde à un autre ; tester migration, rollback et refus explicite.
4. Simuler quota stockage navigateur insuffisant ; jeu doit proposer reprise ou restauration, sans fausse garantie d'archivage permanent.
5. Faire un audit réseau : pas de télémétrie, SDK ou appel API externe obligatoire.
6. Vérifier manifest, HTTPS, navigation mobile, clavier, commandes tactiles, orientation et fullscreen si disponible.

**PWA n'est pas synonyme de garantie hors ligne** : elle le devient seulement après contrôle du service worker, du cache complet, des assets et de la politique de mise à jour sur vrai appareil.

## 9. Portes de release et pouvoir de veto

| Gate | Tests | Verdict |
|---|---|---|
| G1 Fonctionnalité | Build, logique, mission entière, sauvegarde, collisions | `NOT_TESTED` avant exécution réelle |
| G2 Graphismes | Vraie 3D, captures de référence, review de modèles/assets | `NOT_TESTED` avant rendu réel |
| G3 Performance | Bench sur Android/PC, RAM et FPS, batterie si utile | `NOT_TESTED` avant appareils |
| G4 Jouabilité | Essai humain, retours et note qualité | `NOT_TESTED` avant essai |
| G5 Juridique/0 FC | Licences, dépendances, hébergement et absence paiement | `NOT_TESTED` avant audit |

Un échec G2/G4 bloque la publication même si G1/G3 passent. L'utilisateur a le **veto final** sur la qualité. La V1 livrée historiquement reste **techniquement publiée mais non approuvée comme produit**.

## 10. Contraintes des services gratuits (à revalider au lancement)

- **OpenAI Plus / Work/Codex :** quota partagé variable ; aucun nombre fixe de tâches garanti ; consulter Paramètres > Utilisation.
- **GitHub Actions :** standard public gratuit ; privé sous allocation incluse, risque de facturation selon paramètres. Bloquer toute dépense inattendue.
- **Cloudflare Pages Free :** limites actuelles documentées : 500 builds mensuels, 25 Mio par fichier, 20 000 fichiers, 1 build parallèle. Un jeu avec gros assets doit être découpé/optimisé.
- **Vercel Hobby :** personnel non commercial ; le jeu actuel privé de démonstration peut rester, commercialisation éventuelle exige une relecture des conditions.
- **GitHub Pages :** site statique possible ; vérifier limites de distribution et adéquation aux politiques avant choix définitif.

## 11. Sources publiques et preuves du 4 novembre 2026

- https://github.com/fastrouter/experiments-costa-vista
- https://github.com/pranshuparmar/neon-mayhem
- https://kenney.nl/assets/car-kit
- https://kenney.nl/assets/city-kit-roads
- https://kenney.nl/assets/city-kit-suburban
- https://developers.cloudflare.com/pages/platform/limits/
- https://docs.github.com/fr/actions/concepts/billing-and-usage
- https://vercel.com/docs/plans/hobby
- https://vercel.com/legal/terms
- https://help.openai.com/fr-fr/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex
- https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Guides/Offline_and_background_operation

**Fin de l'annexe.** Aucun projet libre ou moteur n'a été définitivement sélectionné, installé ou benchmarké dans cette étape documentaire.

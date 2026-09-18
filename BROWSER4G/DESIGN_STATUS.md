# BROWSER4G — DESIGN STATUS

Date : 2026-09-18

## Baseline canonique

- Statut global : `DESIGN_HARDENED / RUNTIME_UNVERIFIED / FIELD_UNVERIFIED`.
- Architecture cible : Win32/C++ x64 + WebView2 Evergreen.
- Maximum logique futur : 3 onglets.
- Pool stable futur : SLOT A HOT toujours ; SLOT B optionnel/PROTECTED seulement.
- Aucun cycle create/close à chaque changement d’onglet.
- COLD = URL + métadonnées + état applicatif explicitement stocké ; **aucune promesse de restauration complète du DOM, des formulaires ou du travel log WebView2**.
- PROTECTED n’est cold-discardé qu’en vraie pression mémoire.
- Historique, favoris et recovery seront natifs SQLite ; aucune dépendance à `edge://`.
- Runtime Health Guard obligatoire ; aucun downgrade automatique d’un UDF vers un runtime ancien.
- Les seuils mémoire futurs doivent être adaptatifs et fondés sur RAM disponible + commit, pas sur un seuil absolu unique.
- Budget logiciel : 0 USD ; GitHub-hosted Actions = 0 par défaut.

## Étape courante

`P0.1_SOURCE_READY`

Le code source du P0 minimal est maintenant matérialisé. Il vise à fournir la première preuve terrain :

1. fenêtre Win32 stable ;
2. création d’un unique WebView2 ;
3. version runtime exacte journalisée ;
4. micro-probe local après changement **runtime ou signature build/SDK** ;
5. télémétrie RAM/commit réelle, incluant les processus WebView2 et non seulement l’hôte ;
6. navigation manuelle seulement après probe PASS ;
7. artefact mono-EXE grâce au WebView2Loader statique.

## Gates de sortie P0

P0 ne devient `P0_FIELD_PASS` qu’après exécution réelle sur le PC cible avec au minimum :

- démarrage sans crash ;
- `RUNTIME_PROBE_PASS` dans le journal ;
- rendu visible du WebView2 ;
- navigation externe réussie ;
- 10 minutes de télémétrie hôte + processus WebView2 exposés par `GetProcessInfos` sans fuite monotone évidente à page stable ;
- un redémarrage de l’app avec runtime inchangé ;
- vérification qu’un runtime différent déclenche à nouveau le probe lors d’une future mise à jour réelle.

Jusqu’à ces preuves : ne pas déclarer le navigateur opérationnel et ne pas activer le multi-onglet.

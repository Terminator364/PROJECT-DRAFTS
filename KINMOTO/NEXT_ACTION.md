# BLOCAGE DE SÉCURITÉ — résolution prioritaire

GitHub `get_repo` et `list_repositories` signalent `PROJECT-DRAFTS` en visibilité **public**, contrairement à son README qui l'annonce privé. **Ne pas exécuter A1 ni publier d'autres sources** avant vérification et décision du propriétaire : mettre ce dépôt en privé OU autoriser expressément un autre dépôt privé et y migrer les sources après audit.

Ce blocage ne touche ni le jeu public ni les archives privées sur Google Drive. Aucun secret détecté par le balayage local simple des 27 fichiers du paquet A0, mais cela ne constitue pas un audit de confidentialité exhaustif.

---

# Prochaine action — KINMOTO FACTORY

**Ticket suivant après clôture A0 :** `A1-SOURCES-BENCHMARK` (voir `tasks/A1-SOURCES-BENCHMARK.md`).

## Objectif unique
Mesurer et comparer, sans modifier les jeux publiés, les candidats libres `neon-mayhem` et `experiments-costa-vista` et les anciens prototypes ; justifier le choix de l'architecture de V1.

## Préconditions
- Dépôt et SHA A0 vérifiés ; charte et registre accessibles.
- Licence du **code ET des assets** relevée et pièces originales conservées.
- Projet V1 non publié ; aucun paiement ni CI hébergée.

## Essais
- Build et premier lancement PC ; piste de conduite, contact roue/sol, direction, caméra, freinage, collision.
- Essai Android physique lorsque possible ; FPS, RAM système, taille téléchargement.
- Grille 100 points (moto 30, graphismes 20, ressources 20, architecture 15, licences 10, missions 5), statut NOT_TESTED explicite si absence de test.

## Arrêt / livrable
Rapport reproductible avec commits source, licences, captures, résultats, décision recommandée et ticket A2 prêt. Ne pas choisir un vainqueur à partir d'un README.

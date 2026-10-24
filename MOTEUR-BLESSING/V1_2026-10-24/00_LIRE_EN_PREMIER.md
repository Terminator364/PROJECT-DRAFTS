# MOTEUR BLESSING — V1.0 conversationnelle / première édition archivée

**Ce ZIP est prévu pour être joint à une conversation ChatGPT disposant de la lecture de fichiers, de la recherche web et d'un environnement Python.** Le ZIP n'est pas une IA autonome qui utilise Internet depuis Windows.

## Ce que contient cette version

- Un **cahier mère complet** : raison d'être, chronologie RIZ112 → MATRICE R8 → D079 → V1, décisions, calculs, interactions, limites et code de reprise.
- **62 fiches famille**, **355 fiches sous-paramètre** et **12 fiches d'interaction**, chacune avec mécanisme, question, stratégie d'acquisition, repli, valeurs du match témoin et points d'audit.
- Le **noyau mathématique D079 figé** (82,609048 % IC théorique) et le **runner V1 durci** (81,993295 % sur le même match exemple après ré-audit final selon de nouvelles conventions explicites).
- Le **registre 710 lignes**, les contre-audits, sources datées, scénarios et 40 tests pour prévenir les régressions.
- Un **protocole exact pour fournir seulement le match à ChatGPT**, et faire rechercher/déduire les valeurs avant tout IC.
- Les **62 recettes historiques V1.1.2** et **372 propositions d'acquisition** en références (elles ne sont pas synonymes des 355 IDs).

## Utilisation voulue par l'utilisateur

1. Joindre ce ZIP à une nouvelle conversation ChatGPT.
2. Dire par exemple : `Moteur/continue — analyse Gamba Osaka vs Kyoto Sanga à J−3`, ou simplement `MOTEUR/ANALYSER — [match, date, compétition]`.
3. ChatGPT extrait la procédure et collecte les informations **antérieures au cutoff**, construit les **710 états de sous-paramètre**, contextualise les **12 interactions de référence** ou les remplace par les bonnes, vérifie, puis calcule un **IC théorique expliqué**.
4. L'utilisateur **ne remplit aucune fiche**. Si une information n'est pas publiée, ChatGPT construit des proxies/scénarios **dont la méthodologie et l'incertitude sont visibles**. Les vrais hors domaines ont N/A+réactivation. Si l'identité même du match ne peut être vérifiée, pas de faux IC.

**Attention :** la complétude d'un dictionnaire de valeurs ne valide ni leur exactitude ni l'anticipation. Cette V1 documente un moteur calculatoire avec garde-fous; la collecte universelle autonome d'un nouveau match reste à éprouver.

## Fichiers clés

- `01_CAHIER_MERE/CAHIER_MERE_MOTEUR_BLESSING_V1.md`
- `00_DEMARRAGE/PROMPT_DE_DEMARRAGE_CHATGPT.md`
- `00_DEMARRAGE/PROTOCOLE_DE_RECHERCHE_ET_REPLI.md`
- `03_FICHES/INDEX_INTERACTIF.html`
- `02_AUDITS/AUDIT_CONTRADICTOIRE_V1.md`
- `04_MOTEUR/moteur_v1_conversation.py`
- `04_MOTEUR/DEMO_DOSSIER_ENTREE_GAMBA_KYOTO.json`
- `08_SYNCHRONISATION/CHECKPOINT_V1.md`

## Reproduction sans Internet (uniquement l'exemple)

```bash
python 04_MOTEUR/moteur_v1_conversation.py --dossier 04_MOTEUR/DEMO_DOSSIER_ENTREE_GAMBA_KYOTO.json --sortie 05_PREUVES_GAMBA_KYOTO/RESULTAT_V1_RECALCULE.json
python -m unittest discover -s 07_TESTS -p test_moteur_v1.py -v
```

La V1 ne crée jamais automatiquement le dossier de l'adversaire à partir du dossier Gamba/Kyoto. **Le travail de recherche du nouvel adversaire incombe à ChatGPT**, à partir des 62 plans et des 355 fiches.

## Navigation rapide

- `03_FICHES/INDEX_429_FICHES.md` : 62 + 355 + 12 fiches cliquables.
- `03_FICHES/12_INTERACTIONS/INDEX_INTERACTIONS.md` : équation et influences par interaction.
- `08_SYNCHRONISATION/CHECKPOINT_V1.md` : reprise avec `Moteur/continue`.
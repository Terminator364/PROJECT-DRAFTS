# D067 — Contre-audit du corpus historique MATRICE V12

**Date : 23 octobre 2026.** Source : classeur V12 de 313 matchs retrouvé dans les archives Drive de l'utilisateur. Les résultats ci-dessous sont un recalcul du tableau de score rétrospectif, **pas un nouvel historique PIT certifié**.

Le corpus compte **181 entraînement / 72 validation / 55 test d'octobre / 5 replay post-match**, soit 313 entrées; seuls 308 sont antérieurs aux 5 replays. Le modèle C1_LEAGUE_POISSON est noté comme sélectionné, le poids des paramètres R8 enrichis étant nul.

- Test gelé : **49/55 Over1.5 observés, 89,09 %**, moyenne des prévisions **76,733 %**, Brier **0,1146655**.
- La colonne de référence a exactement la même probabilité sur les 55 matchs : **aucun gain de Brier sur la référence**.
- Référence simple supplémentaire calculable *sans regarder les 55 issues*: fréquence Over1.5 de l'entraînement **135/181 = 74,59 %**. Son Brier sur test est **0,1182304**. Gain apparent du modèle C1 : seulement **0,003565 point de Brier**; aucune robustesse statistique déterminée.
- Écart probabilité moyenne vs fréquence du test : **-12,36 points**, compatible avec un défaut de calibration ou une sélection de matchs très atypique.
- Dans les **19 406 positions paramètre×match**, **16 555 = 85,31 %** sont marquées `UNOBSERVED`. Aucune affirmation selon laquelle les 62 paramètres avaient été mesurés exhaustivement n'est soutenue.
- Le classeur répertorie 21 URLs de scores pour 313 matchs, et reconnaît que les horodatages de publication **avant le match** sont incomplets. Les scores de 90 minutes restent également à certifier dans certains cas.

**Verdict :** cet ancien moteur constitue une référence à réutiliser et à reproduire mais pas une preuve de capacité prédictive certifiée. Les 355 sous-paramètres R8 du nouveau modèle doivent démontrer une amélioration hors échantillon par rapport au C1 simple, avec une traçabilité éditeur/horodatages pré-T0 et des résultats à 90 minutes prouvés.

Pour refaire l'audit à partir du fichier XLSX d'origine (sans cloud), utiliser `audit_legacy_v12_v13.py --legacy-xlsx <fichier.xlsx> --out <rapport.json>`. L'outil produit des métriques de vérification; il ne crée pas d'IC fictif.

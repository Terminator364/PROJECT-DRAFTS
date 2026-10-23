# RIZ112 — Contre-audit mathématique de l'IC_DEMO V2 (23 octobre 2026)

## Conclusion prioritaire

**Le moteur numérique 44/44 est raccordé, mais la fonction d'agrégation IC_DEMO V2 n'est PAS conforme à la cible utilisateur de notes/IC atteignant 80–85.** Il est mathématiquement impossible à ce calcul d'atteindre 80 même dans le meilleur cas théorique permissif, donc ce n'est pas seulement un problème de génération aléatoire.

## Preuve analytique (source ic44_v2.py / ic44.py version reproductible)

```
IC_DEMO_PCT = 100 × Π(sigmoid(margin_i), i=1..7) × F × exp(-0.8*dose_sigma)
margin_hydration = (hydration_ratio - 1) / 0.4
hydration_progress = min(1.2, max(0, thermal_progress))
hydration_ratio <= 1.2
=> sigmoid(margin_hydration) <= sigmoid(0.5) = 0.6224593312018546
dose_sigma = (0.015 or 0.07) + (0.015 or 0.07) >= 0.03
=> uncertainty_factor <= exp(-0.8 × 0.03) = 0.9762857097579093
other six sigmoid channels <= 1; feasibility F <= 1
=> IC_DEMO_PCT <= 100 × sigmoid(0.5) × exp(-0.024)
                  = 60.76981499578361%
```

Il s'agit d'une **borne supérieure non nécessairement atteignable**, mais suffisante pour démontrer l'impossibilité d'un IC V2 de 80 ou 85. Une condition exactement atteinte donne sigmoid(0)=50%, pas une note de qualité 85/100. La multiplication des sept domaines est une hypothèse non validée d'indépendance et compresse radicalement l'échelle. L'IC n'est ni une vraie probabilité ni un grade Q/100.

## Vérification exhaustive des dix sorties enregistrées

Tous les dix résultats de RESULTATS_DETAIL_10.json ont été recalculés avec le produit des sept scores × faisabilité × pénalité ; écart < 5e-7 point pour chaque scénario.

| Monde | Ancien IC_DEMO_V2 % | Moyenne des sept canaux en % **(illustration, pas nouvel IC)** | Domaine minimal | Rapport d'hydratation pour illustration |
|---|---:|---:|---|---:|
| A | 0.7268531182 | 59.5 | hydratation 18.2% | 0.398 |
| B | 0.3153417356 | 58.7 | hydratation 16.2% | — |
| C | 0.0754995897 | 48.8 | hydratation 7.6% | — |
| D | 1.8853456931 | 59.7 | hydratation 32.9% | — |
| E | 0.1120223208 | 50.8 | hydratation 7.6% | — |
| F | 0.9816381081 | 59.4 | hydratation 23.1% | — |
| G | 0.0604030525 | 50.1 | hydratation 7.6% | — |
| H | 2.4735166649 | 61.4 | hydratation 35.8% | 0.767 |
| I | 0.1643630843 | 47.9 | hygiène 18.0% | — |
| J | 1.4813796447 | 58.7 | hydratation 32.2% | — |

Sur l'ensemble : moyenne des canaux d'hydratation ~20.3%, thermique ~51.9%, séparation ~71.6%, intégrité ~50.0%, goût ~58.4%, service ~87.0%, hygiène ~49.2%. 
Exemple A : eau effectivement dosée par le modèle ~223.56 g, eau évaporée ~125.84 g, eau restante ~114.29 g pour cible ~287.36 g ; le modèle lui-même n'évalue donc pas cette situation comme correctement hydratée. Exemple H annoncé favorable : ratio d'hydratation ~0.767, inférieur à la cible. Les noms descriptifs ne constituent pas des verdicts de réussite.

## Implications et décision d'ingénierie

- **NE PAS** déformer les scores existants, les multiplier par 100 ou inventer artificiellement 80–85. Conserver les 10 et les 1000 historiques comme témoins immuables.
- Séparer **Q*_simulation**, *note de qualité synthétique sur 100* définie par une rubrique auditable, et **IC_DEMO** = fraction de réalisations Monte Carlo où **Q* >= 85**, selon les incertitudes pré-T0 gelées. On peut alors vérifier si des mondes favorables atteignent 80+ sous les hypothèses déclarées ; ne jamais garantir ce résultat.
- Donner une distinction explicite entre contraintes critiques non compensatoires (p.ex. salubrité/sous-cuisson) et critères préférentiels, sans faire passer la moyenne des sept sigmoïdes pour un nouvel IC validé.
- Tests V3 indispensables : zéro fuite temporelle, 44 routes effectives et effets conditionnels, distributions paramétriques cohérentes, prévisions de bonnes/ mauvaises situations, P(Q*>=85) pouvant varier sur 0..100, convergence MC, incertitude, cas impossibles → abstention, conservation des données/commits.
- La fiabilité scientifique nécessite résultats réels indépendants et calibration : **IC_SCIENTIFIQUE = null**. MATRICE récupère seulement la méthode, aucun coefficient culinaire.
- **Porte V2 : BLOQUÉE pour expansion IC 80–85**; 44/44 raccordement technique conservé. **Suite : REFONTE_IC44_V3 → 10 contre-tests → campagne 1000**, pas directement 1000 IC V2 comprimés.

## Traçabilité

Source canonique moteur : `pret0_focus/ic44_v2.py`. Les 10 scénarios et IC identiques au moteur ont été réexécutés sur GitHub Actions : https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/39945875371 . Archive locale utilisateur `RIZ112_10_SIMULATIONS_440_PARAMETRES_V2_20261023.zip` contient `RESULTATS_DETAIL_10.json` et `ic44.py`.

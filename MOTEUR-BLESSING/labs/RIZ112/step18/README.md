# Step18 — Trois vrais chemins de **faisabilité intermédiaire**, aucun coefficient Q inventé

L'audit Step17 des 112 rubriques a signalé notamment les rubriques **002** (eau potable disponible), **005** (eau de rinçage disponible) et **008** (capacité de casserole), jusqu'ici sans réponse calculatoire détectée dans le moteur Step16 lorsque leur seule fiche est perturbée.

`resource_feasibility.py` construit trois bilans distincts, sous hypothèses **précises et datées avant le gel** :

- `002` avec `035` : stock d'eau potable (ml) moins eau de cuisson prévue (g), convertie avec `water_density_g_per_ml` explicitement déclarée.
- `005` avec l'action de rinçage `054` : eau de rinçage disponible (ml) moins volume planifié explicite `rinse_volume_planned_ml`.
- `008`, `001`, `035` : volume nominal du récipient moins somme approximative du volume du riz sec et de l'eau. **Seulement un proxy de charge initiale**, pas une vraie prévision de remplissage final ou de sécurité alimentaire. Les densités sont obligatoires et sourcées.

Le calcul refuse `UNKNOWN` et les hypothèses non documentées, après T0, les unités incompatibles et les nombres invalides. Il distingue faisabilité matérielle et **qualité de cuisson**. Aucun chemin n'est déclaré causal vers Q sans données réelles.

Sous les hypothèses SYNTHÉTIQUES du fichier fourni (rho eau=1 g/ml; densité apparente riz sec=0,8 g/ml; rinçage prévu=120 ml), modifier chaque ressource de +1 % modifie les marges calculées de **+3,5 ml (002)**, **+10 ml (005)**, **+17 ml (008)**. C'est une conséquence mathématique des bilans, pas une variation d'IC en pourcentage. L'IC_DEMO original du scénario A reste **60,25 %**, IC scientifique `null`.

```shell
python -m unittest discover -s step18 -p 'test_*.py' -q
python step18/riz112_with_resources.py \
 --packet step6/examples/A_couvercle_ajuste_112.json --lab-root . \
 --assumptions step18/ASSUMPTIONS_EXEMPLE_SYNTHETIQUE.json \
 --output step18/RESULTAT_EXEMPLE_SYNTHETIQUE.json
```

Le point d'entrée `riz112_with_resources.py` appelle **sans altération** le Step16 validé, puis annexe les nouveaux diagnostics. La prochaine étape est d'élargir ces raccordements aux rubriques encore non réactives selon leur rôle, leurs conditions d'activation et les dépendances réellement démontrables. **Pas de transfert à MATRICE**.

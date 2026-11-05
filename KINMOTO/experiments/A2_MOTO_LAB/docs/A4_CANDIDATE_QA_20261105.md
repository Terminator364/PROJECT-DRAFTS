# KIN MOTO FACTORY 3.0 — Laboratoire A2/A3 → candidate de revue A4
**05/11/2026 · A2A3-A4-0.5.7-CANDIDATE-REVIEW · NO GO STABLE**

## Conformité au cahier maître V3
- A1-D §9.4 : audit de sources et sous-moteurs Neon/Costa dans PR #42, cinq scènes KINMOTO CPU, **aucun moteur officiellement choisi**. HP + Galaxy A21s + comparaison des trois jeux entiers toujours NOT_TESTED.
- A2 §16 : collision profondément chevauchée réparée sans téléportation d'un mètre en un seul tick, résolution plafonnée à 0,32m / 1/60s, odomètre et roues non contaminés (PR #43, 3 nouveaux tests).
- A3 §16 : deux courses rédigées quartier Bandal → École des Arts → Place Victoire, nouvelle station moto 3D dans mesh statique existant, garage, 16 véhicules, carrière et sauvegarde conservés (PR #44, 5 nouveaux tests).
- A4 §12-13 : assemblage HTML autonome et outil GO/NO-GO exécuté ; **G1 PASS, G2/G3/G4 bloqués** ; pas de sortie STABLE.
  
## Tests réellement exécutés sur code exact
| Séquence | Résultat |
|---|---|
| A2 seul (sur diagnostic 165) | **168/168 Node PASS** |
| A3 après A2 | **173/173 Node PASS** |
| A4 final | **173/173 Node, 26/26 Python PASS** |
| npm run check / build / test HTTP 5 ressources | **PASS** |
| 12 modules → HTML autonome | **105315 octets**, SHA256 `b761f5f0f70ffbd6f0c10408abbf89ccb251bc062a68cbb880f0257acd65ee55` |
| WebGL2 logiciel Chromium Xvfb ANGLE/Vulkan SwiftShader | Desktop 1280×800 PASS ; mobile émulé 393×852 PASS, pause/reprise, commandes, aucun JS error |
| WebGL2 mesures d'accélération | Desktop +2,537m, mobile émulé +0,604m ; 6 et 3 FPS **logiciels** uniquement |
| Vrai GPU HP, Galaxy A21s, Safari iOS, session 15-20min | **NOT_TESTED** |
| Extraction d'un ZIP neuf, rebuild HTML byte-identique, 173/26 tests et HTTP | **PASS** |

## Capture et distribution
- Les deux captures PNG du vrai moteur WebGL2 **logiciel** ont été enregistrées dans le paquet privé, avec le rapport JSON ; pas de preuve GPU physique.
- Fichier autonome `KINMOTO_A2A3_A4_CANDIDATE_PRIVEE.html` (105315 octets), ouverture depuis navigateur exécutable ; les aperçus de ChatGPT/Telegram/Quick Look peuvent bloquer le JS. iPhone réel non certifié.
- Paquet privé `KINMOTO_A2_A3_A4_CANDIDATE_PRIVEE_QA_20261105.zip` **1 038 580 octets**, SHA256 `da54a89b61b2c69cc42337e5e747421ee1227c872a1ff521bb20f9962dc6423f`, **88 entrées, 87/87 empreintes vérifiées**.
- Le paquet est dans la conversation, non publié sur Vercel/Drive par ce lot.

## Portes A4 : verdict exact
La commande `python tools/a4_release_gate.py` lit `docs/A4_ACCEPTANCE_EVIDENCE.json`.
`python tools/a4_release_gate.py --strict` renvoie **exit 2** en présence d'un veto.

- **G1_FUNCTIONAL = PASS**, tests et missions complètes.
- **G2_VISUAL = BLOCKED**, approbation visuelle et benchmark de référence humain absents.
- **G3_TARGET_PERFORMANCE = BLOCKED**, aucun FPS/RAM/chauffe mesuré sur HP et Galaxy A21s.
- **G4_REAL_PLAYABILITY = BLOCKED**, aucune session humaine 15–20min sur appareils.
- **A1_ENGINE_DECISION = BLOCKED**, scorecard et élection du moteur non terminés.
- **ASSETS_AND_LEGAL = BLOCKED**, audit juridique final des ressources encore ouvert.
- **OWNER_PUBLICATION_GO = BLOCKED**, aucun accord public.
- **GLOBAL = NO_GO STABLE**.

## Principaux écarts
Style low-poly visible dans les captures. PNJ et rues simplifiés, expérience de conduite non évaluée par l'utilisateur. Aucun modèle moto de Costa (assets créés avec outils commerciaux) ni GLB tiers non vérifié importé. La simulation fonctionne mais sa qualité V1 ne peut pas être déduite du nombre de tests.

**Gouvernance :** aucun merge main, aucun changement URL STABLE, zéro Vercel/GitHub Actions hébergées, zéro Remote et zéro nouveau coût.

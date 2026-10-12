# R1 App / Windows Rescue — état contrôlé au 12 octobre 2026

## Livrables exécutés
- Projet Android natif Java : applicationId `com.blessing.rescuebridge`, quatre classes (`MainActivity`, `BridgeClient`, `BridgeProtocol`, `SecurePairingStore`), Gradle/Android manifest.
- Agent Windows local Python `bridge_agent.py`, protocole HMAC SHA-256, anti-rejeu SQLite, fichiers limités à un workspace, sauvegarde et journal.
- Superviseur PowerShell détectant adaptateur USB RNDIS/NCM, attente du téléphone débranché, redémarrage sans dépendre de Desktop Commander.
- Test de compatibilité Java vers serveur Python réel sur HTTP loopback, tests d'intégrité et de permission, simulation de pannes.
- Trois cycles de validation **24/24 chacun**, suivis de la même vérification **24/24 × 3** après extraction du ZIP de livraison.

## Artefact produit pendant la session
Nom: `BCP-USB-Rescue-R1-Source-et-Tests.zip`
SHA-256: `2c213523517a63cf6d3861f7dc9aec1c2b22665d368df800de0fab50d0277d44`
Taille: 38 730 octets.
Windows-only ZIP: `BCP-USB-Rescue-R1-Windows.zip`
SHA-256: `6d01d117a8286266cfb6b22655a6be84757c6b7bc46fb663c4522a2fbc73661a`

Ces fichiers sont livrés dans les artefacts de la conversation actuelle, **non déposés dans ce dépôt GitHub** ; le présent fichier est seulement le registre de preuve et continuité. Ne prétendez jamais qu'un ZIP ChatGPT est durablement hébergé sur GitHub.

## Gates NON franchis
- Pas d'APK : Android SDK / Gradle absents de l'environnement de test.
- Pas de véritable Android Emulator démarré, pas de signature d'APK, pas d'installation sur Samsung.
- MBMPC hors ligne au dernier test Desktop Commander ; pas de test USB physique ou Windows réel.
- Pas de TLS : prototype HTTP + HMAC, réservé à un réseau USB privé non hostile.
- Pas de canal ChatGPT natif vers cette application, ni de shell arbitraire ni de bureau à distance graphique.
- Scripts PowerShell non exécutés sur Windows.
- Aucune minute GitHub Actions consommée pour ce R1.

## Passage requis avant la diffusion
1. Ajouter les sources vérifiées au dépôt pérenne sans duplicata de classes Android.
2. Compiler Android SDK 35 avec Gradle 8.9 en CI *manuelle* (aucun trigger automatique), récupérer APK, inspecter logs et SHA-256.
3. Exécuter tests sur Android virtuel, puis sur le Samsung réel branché à MBMPC ; enregistrer la preuve de liaison.
4. Corriger chaque échec matériel, répéter débranchement/rebranchement, redémarrage de Windows et permissions locales.
5. Ajouter TLS, gestion/révocation de clés et une intégration ChatGPT officiellement supportée avant de parler de remplacement de Desktop Commander.

Ceci n'est pas une certification de produit fini.
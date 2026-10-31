# ORIGIN 12 cycles de contre-audit

### R01 — Hypothèse modèle non vérifiée
**Contredit :** La mémoire de conversation ne prouve pas l'état actuel du téléphone.
**Réparé :** Exiger A signé, référence exacte, détails des partitions physiques avant toute décision.
**Paquets :** A, C
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R02 — Flash prématuré
**Contredit :** Un bootloader déverrouillé/Knox et une sauvegarde imparfaite rendent le retour difficile.
**Réparé :** Introduire B/S comme double porte indépendante; aucune action risquée si restauration non démontrée.
**Paquets :** B, S
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R03 — 3 Go DT vs appareil 4 Go
**Contredit :** Le device tree mainline a une mémoire 3 Go par défaut; risque de masquer les 4 Go.
**Réparé :** Test RAM physique, noeuds mémoire, réservations et vrai /proc/meminfo sous Linux.
**Paquets :** A, Q, W
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R04 — Wi-Fi absent
**Contredit :** Un Linux bootable sans radio réseau est inutilisable comme machine autonome locale.
**Réparé :** Wi-Fi+USB comme P0; chaîne firmware/antenne/power-domain, aucun G3 sans test.
**Paquets :** R, W
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R05 — Batterie et charge
**Contredit :** Serveur permanent peut devenir dangereux sans charge sûre, thermiques et capacité réelle.
**Réparé :** Contrôle D et W; STOP automatique d'essai si batterie douteuse; aucun travail lourd sur charge douteuse.
**Paquets :** D, W, Y
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R06 — Noyau vendor piégé
**Contredit :** Le noyau 4.19 peut reposer sur des composants Android non portables.
**Réparé :** Documenter dépendances HAL/firmware, deux voies V/M et critère mesuré de sélection.
**Paquets :** P, Q, U
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R07 — Modèle Apollo mal transposé
**Contredit :** Quelques ko ne suffisent pas à Linux; RAM 4 Go n'autorise pas une exécution anarchique.
**Réparé :** Budget RSS/PSS mesuré, modules S4 froids, ordre de priorités S0-S4.
**Paquets :** G, H, J
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R08 — Fausse exactement-une-fois
**Contredit :** SQLite ne garantit pas l'absence de double effet externe en cas de crash.
**Réparé :** Outbox et idempotence; tests de stale completion et crash-points; aucun effet externe non compensable.
**Paquets :** I, M
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R09 — Test labo confondu avec test appareil
**Contredit :** Une réussite x86 ne prouve ni Android Doze ni thermiques.
**Réparé :** Étiquetage obligatoire LAB/ANDROID/MAINLINE_HW; gates réels exigent preuve DEVICE.
**Paquets :** M, N, U
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R10 — Récupération insuffisante
**Contredit :** Réinitialisation peut détruire données et laisser le matériel inaccessible.
**Réparé :** Cartographier partitionnement réel, secours, sauvegarde externe et consignes opérateur.
**Paquets :** B, C, S
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R11 — Budget/Réseau RDC
**Contredit :** PC 4Go, data limitée et coupures rendent builds et CI répétitifs non viables.
**Réparé :** Build incrémental, caches, quota Actions 0/min par défaut, binaire petit, connexion optionnelle.
**Paquets :** O, J, Y
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

### R12 — Fin fictive / dérive de périmètre
**Contredit :** Un prototype ou un boot incomplet serait annoncé comme niveau 3.
**Réparé :** Gates stricts, statuts et preuves, replanification après chaque échec, audit indépendant de Z.
**Paquets :** Z, Y
**Test du graphe :** PASS (26 lots, 59 dépendances, 5 gates, 26 non validés)

**Bilan :** 12/12 contrôles structurels PASS, aucun test matériel prétendu.

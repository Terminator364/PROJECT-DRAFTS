#!/usr/bin/env python3
"""Build V4.1 from frozen R3.3 + V4 transport; additive, reversible."""
import pathlib,re,runpy,sys
root=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "r33").resolve()
sys.argv=["BCP_REMOTE_V4/patch_v4_android.py",str(root)]
runpy.run_path("BCP_REMOTE_V4/patch_v4_android.py",run_name="__main__")
java=root/"android/app/src/main/java/com/blessing/rescuebridge"
p=java/"MainActivity.java"
s=p.read_text(encoding="utf8")
anchor="    @Override protected void onResume() {\n        super.onResume();\n        visible=true;\n"
assert s.count(anchor)==1
s=s.replace(anchor,anchor+"        enrollTrustedUsbOnce();\n",1)
anchor2="        mainHandler.postDelayed(foregroundCheck,1000);\n    }\n"
assert s.count(anchor2)==1
s=s.replace(anchor2,"""        mainHandler.postDelayed(foregroundCheck,1000);
        if ("HOME".equals(activeScreen))
            mainHandler.postDelayed(()->{if(visible && !busy)connectOneTap(false);},900);
    }
""",1)
method=r'''    /** First-run provisioning by a *previously authorised* physical USB ADB PC.
     * ADB writes a short lived file into this app's external private directory;
     * Android Keystore retains it; file is removed immediately. No network enrollment.
     * A mismatched existing identity is never silently replaced.
     */
    private void enrollTrustedUsbOnce() {
        java.io.File folder=getExternalFilesDir(null);
        if(folder==null)return;
        java.io.File ticket=new java.io.File(folder,"bcp-usb-enroll.once");
        if(!ticket.isFile())return;
        try {
            if(ticket.length()<64 || ticket.length()>67)throw new SecurityException("Taille refusée");
            byte[] bytes=java.nio.file.Files.readAllBytes(ticket.toPath());
            String candidate=new String(bytes,java.nio.charset.StandardCharsets.US_ASCII).trim();
            if(!candidate.matches("[0-9a-fA-F]{64}"))throw new SecurityException("Format refusé");
            String previous=SecurePairingStore.load(this);
            if(!previous.isEmpty()&&!java.security.MessageDigest.isEqual(
                 previous.getBytes(java.nio.charset.StandardCharsets.US_ASCII),
                 candidate.getBytes(java.nio.charset.StandardCharsets.US_ASCII)))
                throw new SecurityException("Identité existante conservée");
            SecurePairingStore.save(this,candidate);
            if(secret!=null)secret.setText(candidate);
            status.setText("Appairage local prêt");
            explanation.setText("Clé enregistrée dans Android Keystore par câble USB autorisé.");
            lastAction.setText("Premier appairage protégé terminé");
        } catch(Exception error) {
            status.setText("Appairage à vérifier");
            explanation.setText("Appairage automatique refusé : "+error.getClass().getSimpleName());
        } finally {
            if(!ticket.delete())ticket.deleteOnExit();
        }
    }

'''
anchor3="    private void openUsbSettings() {\n"
assert s.count(anchor3)==1
s=s.replace(anchor3,method+anchor3,1)
s=s.replace('"/status",6500)', '"/status",19000)')
s=s.replace('detailed?"/diagnostics":"/status",6500)', 'detailed?"/diagnostics":"/status",19000)')
# Adapt the guidance without claiming that USB tethering is required.
s=s.replace("Si Android a désactivé le modem USB, ouvre les réglages système.", "La connexion ADB fonctionne sans modem USB après une autorisation initiale.")
s=s.replace("Le téléphone ne présente pas de réseau USB utilisable. Le câble peut être branché, mais Android doit autoriser Modem USB. Utilise Ouvrir les réglages réseau Android si nécessaire.", "Le tunnel USB ADB n'a pas répondu. Garde le câble branché, autorise le PC dans Android et réessaie. Aucun modem USB requis.")
s=s.replace("Adresse du PC absente. Ouvre Réglages, puis utilise l'adresse indiquée par DIAGNOSTIC.cmd sur Windows.","Le pont USB ADB recherche ton ordinateur. Aucun adressage IP manuel n'est requis.")
p.write_text(s,encoding="utf8")
# V4's versionCode 6 -> V4.1 code 7. Keep legacy test expectations in sync.
g=root/"android/app/build.gradle"
s=g.read_text(encoding="utf8")
assert s.count("versionCode 6")==1
s=s.replace("versionCode 6","versionCode 7").replace("0.4.0-adb-usb-preview","0.4.1-adb-oneclick")
g.write_text(s,encoding="utf8")
for name in ("test_pc_port_isolation.py","test_usb_readiness.py","test_user_experience.py"):
 p=root/"tests"/name
 s=p.read_text(encoding="utf8")
 s=s.replace("versionCode 6","versionCode 7").replace(r"versionCode\s+6\b",r"versionCode\s+7\b")
 p.write_text(s,encoding="utf8")
assert "enrollTrustedUsbOnce();" in (java/"MainActivity.java").read_text()
assert "versionCode 7" in g.read_text()
print("V4_1_ONECLICK_PATCH_OK")
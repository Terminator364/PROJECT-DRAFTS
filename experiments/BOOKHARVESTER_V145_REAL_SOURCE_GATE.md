# Blessing BookHarvester V1.4.5 — Gate de qualification Ranovel (2026-10-12)

## Preuves techniques

- Windows GitHub Actions: https://github.com/Terminator364/PROJECT-DRAFTS/actions/runs/38203125632 — **SUCCESS**, 57 tests, PyInstaller, probe Tkinter, installation isolée `app-v1.4.5`, raccourci.
- Diagnostic réel sur 3 chapitres aléatoires de `I Am the Demon Lord`: **22, 142 et 201**, chacun HTTP **403 Cloudflare**, extraction **0/3**, `SAMPLE_FAIL`, code de sortie **5**. Un succès du workflow signifie que le diagnostic est fiable, **pas** que Ranovel est accessible.
- Essais antérieurs sur MBMPC: chapitre 23 HTTP 403 avec `Server: cloudflare` et `CF-Ray`. Page de présentation HTTP 200; aucun lien chapitre reconnu dans son HTML statique (contenu éventuellement dynamique).
- L’indexation par les moteurs de recherche n’est pas la preuve d’un accès en lecture en temps réel.

## Sources open source examinées

- `lncrawl/lightnovel-crawler`: diagnostics de couche d'accès, challenge/HTTP non valide, adaptateurs par site.
- `dteviot/WebToEpub`: parser dans navigateur; plusieurs issues relatent des 403 exigeant connexion/autorisation.
- Ces projets ne prouvent pas la compatibilité réelle de Ranovel et n’autorisent aucun contournement de ses contrôles d’accès.

## Restrictions de la source

Les conditions accessibles de Ranovel réservent les droits et interdisent reproduction, duplication et copie sans permission: https://ranovel.com/terms-and-conditions/ . En conséquence, **ne pas proposer d’extraction intégrale de Ranovel ni de contournement Cloudflare** sans autorisation explicite du détenteur des droits et du site.

## Correctifs V1.4.5

- Classer 403 Cloudflare vs refus ordinaire, 404, erreur HTML, fausse page HTTP 200.
- Tirer au sort trois chapitres, vérifier les empreintes distinctes; rapport JSON sans texte reproduit.
- Sortir avec code !=0 si le site est inaccessible; pas de boucle de retries sur 403.
- Conserver les versions précédentes lors de l'installation Windows.
- Workflow redevenu manuel après le checkpoint; budget GitHub protégé.

## Release et état

- Artifact GitHub: `BookHarvester-V1.4.5-Windows-and-QA`, run `38203125632`.
- Archive interne Windows SHA-256: `7e461b569b754a56e238745ac3361afae3135225547c5902cdf88b948ed0cb1a`.
- **Ranovel: NON CERTIFIÉ.** Ne pas dire 236/236 ni 3/3.
- **MBMPC**: installation V1.4.5 non confirmée; la V1.4 précédente n’a pas été modifiée par ce checkpoint. Ne pas inventer de preuve locale.
- Solutions acceptables: lecture sur plateformes officielles; application de lecture dans navigateur; import de fichiers que l’utilisateur est autorisé à conserver; demander à la plateforme l’autorisation de sauvegarde/lecture hors ligne.

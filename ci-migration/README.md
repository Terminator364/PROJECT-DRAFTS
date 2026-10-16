# Public GitHub Actions migration (16 October 2026)

The Terminator364 account received 90% GitHub Actions billing alerts for 1,800/2,000 private minutes and 0.45/0.5 GB storage. The private ChatGPT-PC repository has repeated Windows CI jobs. This public PROJECT-DRAFTS branch isolates 20 reviewed G1/G4/G5/G6 synthetic test and Win32 source files; it NEVER checks out the private repository.

Security: the allowlist under public-source-manifest.json pins every Git blob; the public-source policy refuses any added file, changed blob or obvious secret marker. No tokens, Telegram deliveries, runtime truth, network identities, user-specific configurations or credentialed private tests are copied. The private branch may change; public results cover only the listed SHA1 blobs, NOT future private commits.

Workflow: standard public Windows 2022/2025 runners; read-only token; scoped triggers; cancellation of superseded CI; artifact retention 1 day. This validates synthetic scenarios, NOT field-PC reconnection. Before disabling any private auto-Windows workflow, require a passing public matrix, then remove or convert redundant private triggers to deliberate manual gate. Keep secret-bearing delivery work private.

Historical artifact storage is not reclaimed by lowering future retention. Old artifacts must be deleted separately via GitHub Actions management. Configure an account Actions $0 stop-use budget via https://github.com/settings/billing/budgets to prevent spending beyond included free usage.

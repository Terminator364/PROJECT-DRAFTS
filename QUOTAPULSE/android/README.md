# QuotaPulse — Android beta (8 Nov 2026)

A small, native Android quota dashboard for **Desktop Commander Remote MCP**. No Windows resident process, no Cloudflare, no ChatGPT runtime, no background polling, no calls to MCP tools.

## Function
On user refresh, an **ephemeral WebView** visits the original https://mcp.desktopcommander.app/usage and reads the **displayed, logged-in page text** using Android's JavaScript evaluation API. Parsing occurs entirely locally on device, with a strict used/limit/remaining consistency check. Only numeric quota and reset date are cached in local app preferences. The native dashboard shows usage, remaining, reset date, daily average and age of measurement. It never silently represents stale data as live. All calls are direct HTTPS page requests to the provider dashboard; the application never calls `/mcp` or `who_am_i`.

## Account setup
The provider supports **Continue with email** and **Continue with Google**. Google's OAuth does not allow sign-in within embedded Android WebViews, so **use the provider's email login method for initial authentication** if available on your account. The app does **not** bypass this limitation. Login is completed only against the provider's domain in the temporary view, then the view is destroyed after a confirmed quota reading. The app itself does not request, store or upload credentials. Cookie storage is maintained locally by Android WebView.

## Important: honest QA boundary
- Java parser and consistency unit tests can run in CI.
- APK compilation can be attested by GitHub Actions.
- **Live account authentication and actual Android UI cannot be verified by CI**. This build is a functional beta pending actual on-device account sign-in and usage read. If authentication fails or provider changes its dashboard, the application shows an error and the last verified reading, not invented data.
- The first login may require manual email confirmation. Android's WebView Google OAuth limitation is known and documented.

## Privacy / performance
- No new server or Cloudflare; no Windows process.
- No Android background services or WorkManager.
- In-memory WebView is created on demand and released after refresh.
- No analytics or third-party SDKs. No INTERNET use except provider site and authentication.
- APK uses only Android SDK and no extra library runtime.

## Build
`gradle -p apps/quota-pulse --no-daemon :app:testDebugUnitTest :app:assembleDebug`

## Source
This project is a separate Android app under `apps/quota-pulse` and is not a PCRC Core change.


## v0.2.0 Android fix (Nov 8 2026)
- Strict numeric tokenization prevents absorbing trailing 78% into the limit.
- 9 regression tests include the Samsung screenshot layout (7 811 / 10 000, 78% used, average 976).
- Timeout now terminates stalled reads; authentication is displayed only when required.
- Android 16 system insets keep the UI below status bar.
- Stable application identity for the replacement build is com.quotapulse.monitor.stable to coexist with original debug beta; future APKs require persistent signing key and same package id.
- Live authentication/read still requires explicit on-device acceptance testing; Java unit tests alone cannot prove it.

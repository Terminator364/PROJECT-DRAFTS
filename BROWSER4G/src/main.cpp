#include <windows.h>
#include <psapi.h>
#include <shlobj.h>
#include <wrl.h>
#include <WebView2.h>

#include <cwchar>
#include <cwctype>
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iterator>
#include <sstream>
#include <string>

#pragma comment(lib, "Psapi.lib")
#pragma comment(lib, "Shell32.lib")

using Microsoft::WRL::Callback;
using Microsoft::WRL::ComPtr;

namespace {
constexpr wchar_t kWindowClass[] = L"BROWSER4G_P0_WINDOW";
constexpr wchar_t kAppName[] = L"BROWSER4G P0";
constexpr wchar_t kSdkVersion[] = L"1.0.4191.47";
constexpr UINT_PTR kTelemetryTimer = 1;
constexpr UINT kTelemetryIntervalMs = 15000;
constexpr int kAddressId = 1001;
constexpr int kGoId = 1002;
constexpr int kStatusId = 1003;
constexpr int kTopBarHeight = 36;
constexpr int kStatusHeight = 22;

HWND g_mainWindow = nullptr;
HWND g_address = nullptr;
HWND g_go = nullptr;
HWND g_status = nullptr;

ComPtr<ICoreWebView2Environment> g_environment;
ComPtr<ICoreWebView2Controller> g_controller;
ComPtr<ICoreWebView2> g_webView;

std::filesystem::path g_appRoot;
std::wstring g_runtimeVersion;
std::wstring g_lastGoodRuntime;
bool g_probeRequired = true;
bool g_probeRunning = false;
bool g_probePassed = false;
bool g_runtimeReady = false;

std::wstring Timestamp()
{
    SYSTEMTIME st{};
    GetLocalTime(&st);
    wchar_t buf[64]{};
    swprintf_s(
        buf, L"%04u-%02u-%02u %02u:%02u:%02u.%03u",
        st.wYear, st.wMonth, st.wDay,
        st.wHour, st.wMinute, st.wSecond, st.wMilliseconds);
    return buf;
}

std::filesystem::path AppRoot()
{
    PWSTR localAppData = nullptr;
    if (FAILED(SHGetKnownFolderPath(FOLDERID_LocalAppData, KF_FLAG_CREATE, nullptr, &localAppData)))
        return std::filesystem::temp_directory_path() / L"BROWSER4G-P0";

    std::filesystem::path path(localAppData);
    CoTaskMemFree(localAppData);
    return path / L"BROWSER4G" / L"P0";
}

void EnsureDirectories()
{
    std::error_code ec;
    std::filesystem::create_directories(g_appRoot / L"logs", ec);
    std::filesystem::create_directories(g_appRoot / L"state", ec);
    std::filesystem::create_directories(g_appRoot / L"UserData", ec);
}

void Log(const std::wstring& message)
{
    std::wofstream out(g_appRoot / L"logs" / L"p0.log", std::ios::app);
    if (out)
        out << L"[" << Timestamp() << L"] " << message << L"\n";
}

std::wstring ReadText(const std::filesystem::path& path)
{
    std::wifstream in(path);
    std::wstring value;
    if (in)
        std::getline(in, value);
    return value;
}

bool WriteTextAtomic(const std::filesystem::path& path, const std::wstring& value)
{
    const auto tmp = path.wstring() + L".tmp";
    {
        std::wofstream out(tmp, std::ios::trunc);
        if (!out)
            return false;
        out << value << L"\n";
        out.flush();
    }

    return MoveFileExW(tmp.c_str(), path.c_str(), MOVEFILE_REPLACE_EXISTING | MOVEFILE_WRITE_THROUGH) != FALSE;
}

std::wstring HrString(HRESULT hr)
{
    wchar_t buf[32]{};
    swprintf_s(buf, L"0x%08X", static_cast<unsigned int>(hr));
    return buf;
}

struct MemorySnapshot {
    double workingSetMb = 0.0;
    double privateMb = 0.0;
    DWORD systemLoadPct = 0;
    double availablePhysicalMb = 0.0;
    double commitTotalMb = 0.0;
    double commitLimitMb = 0.0;
    double commitPct = 0.0;
};

MemorySnapshot SampleMemory()
{
    MemorySnapshot s{};
    PROCESS_MEMORY_COUNTERS_EX pmc{};
    if (GetProcessMemoryInfo(GetCurrentProcess(), reinterpret_cast<PROCESS_MEMORY_COUNTERS*>(&pmc), sizeof(pmc))) {
        s.workingSetMb = static_cast<double>(pmc.WorkingSetSize) / (1024.0 * 1024.0);
        s.privateMb = static_cast<double>(pmc.PrivateUsage) / (1024.0 * 1024.0);
    }

    MEMORYSTATUSEX ms{};
    ms.dwLength = sizeof(ms);
    if (GlobalMemoryStatusEx(&ms)) {
        s.systemLoadPct = ms.dwMemoryLoad;
        s.availablePhysicalMb = static_cast<double>(ms.ullAvailPhys) / (1024.0 * 1024.0);
    }

    PERFORMANCE_INFORMATION pi{};
    if (GetPerformanceInfo(&pi, sizeof(pi)) && pi.PageSize != 0) {
        const double pageMb = static_cast<double>(pi.PageSize) / (1024.0 * 1024.0);
        s.commitTotalMb = static_cast<double>(pi.CommitTotal) * pageMb;
        s.commitLimitMb = static_cast<double>(pi.CommitLimit) * pageMb;
        if (s.commitLimitMb > 0.0)
            s.commitPct = (s.commitTotalMb / s.commitLimitMb) * 100.0;
    }
    return s;
}

std::wstring MemoryLine(const MemorySnapshot& s)
{
    std::wostringstream os;
    os << std::fixed << std::setprecision(1)
       << L"proc_ws_mb=" << s.workingSetMb
       << L" proc_private_mb=" << s.privateMb
       << L" sys_mem_load_pct=" << s.systemLoadPct
       << L" avail_phys_mb=" << s.availablePhysicalMb
       << L" commit_total_mb=" << s.commitTotalMb
       << L" commit_limit_mb=" << s.commitLimitMb
       << L" commit_pct=" << s.commitPct;
    return os.str();
}

void SetStatus(const std::wstring& text)
{
    if (g_status)
        SetWindowTextW(g_status, text.c_str());
}

void UpdateTelemetry(bool writeLog)
{
    const auto s = SampleMemory();
    std::wostringstream title;
    title << kAppName
          << L" | WS " << std::fixed << std::setprecision(0) << s.workingSetMb << L" MB"
          << L" | RAM " << s.systemLoadPct << L"%"
          << L" | Commit " << std::setprecision(0) << s.commitPct << L"%";
    if (!g_runtimeVersion.empty())
        title << L" | WV2 " << g_runtimeVersion;
    if (g_probePassed)
        title << L" | HEALTH OK";
    else if (g_probeRunning)
        title << L" | HEALTH PROBE";
    else if (!g_runtimeReady)
        title << L" | RUNTIME ERROR";

    if (g_mainWindow)
        SetWindowTextW(g_mainWindow, title.str().c_str());
    if (writeLog)
        Log(L"TELEMETRY " + MemoryLine(s));
}

void ResizeLayout()
{
    if (!g_mainWindow)
        return;
    RECT rc{};
    GetClientRect(g_mainWindow, &rc);
    const int width = rc.right - rc.left;
    const int height = rc.bottom - rc.top;
    const int goWidth = 72;

    if (g_address)
        MoveWindow(g_address, 8, 7, max(80, width - goWidth - 24), 24, TRUE);
    if (g_go)
        MoveWindow(g_go, max(88, width - goWidth - 8), 7, goWidth, 24, TRUE);
    if (g_status)
        MoveWindow(g_status, 8, max(kTopBarHeight, height - kStatusHeight), max(80, width - 16), 18, TRUE);

    if (g_controller) {
        RECT webBounds{0, kTopBarHeight, width, max(kTopBarHeight, height - kStatusHeight)};
        g_controller->put_Bounds(webBounds);
    }
}

std::wstring NormalizeAddress(std::wstring input)
{
    while (!input.empty() && iswspace(input.front()))
        input.erase(input.begin());
    while (!input.empty() && iswspace(input.back()))
        input.pop_back();

    if (input.empty())
        return L"about:blank";

    const auto starts = [&](const wchar_t* prefix) { return input.rfind(prefix, 0) == 0; };
    if (starts(L"http://") || starts(L"https://") || starts(L"file://") || starts(L"about:") || starts(L"data:"))
        return input;
    return L"https://" + input;
}

void NavigateFromAddressBar()
{
    if (!g_webView || !g_probePassed || !g_address)
        return;
    wchar_t buffer[2048]{};
    GetWindowTextW(g_address, buffer, static_cast<int>(std::size(buffer)));
    const std::wstring url = NormalizeAddress(buffer);
    const HRESULT hr = g_webView->Navigate(url.c_str());
    if (FAILED(hr)) {
        SetStatus(L"Navigation refusée par WebView2.");
        Log(L"NAVIGATE_FAIL hr=" + HrString(hr) + L" url=" + url);
    } else {
        Log(L"NAVIGATE url=" + url);
    }
}

void ShowWelcome()
{
    if (!g_webView)
        return;
    std::wstring html =
        L"<!doctype html><html><head><meta charset='utf-8'>"
        L"<style>body{font-family:Segoe UI,Arial;margin:40px;line-height:1.45}.ok{color:#0a6}code{background:#eee;padding:2px 5px}</style></head><body>"
        L"<h1>BROWSER4G P0</h1><p class='ok'><b>Runtime Health Guard: PASS</b></p>"
        L"<p>WebView2 runtime: <code>" + g_runtimeVersion + L"</code></p>"
        L"<p>SDK pin: <code>" + std::wstring(kSdkVersion) + L"</code></p>"
        L"<p>Un seul SLOT A est actif. Les onglets multiples restent volontairement hors P0.</p>"
        L"<p>Entre une URL dans la barre ci-dessus pour tester la navigation réelle.</p>"
        L"</body></html>";
    g_webView->NavigateToString(html.c_str());
}

void MarkProbeFailure(const std::wstring& reason)
{
    g_probeRunning = false;
    g_probePassed = false;
    EnableWindow(g_go, FALSE);
    SetStatus(L"Runtime Health Guard: FAIL — navigation externe bloquée.");
    Log(L"RUNTIME_PROBE_FAIL runtime=" + g_runtimeVersion + L" reason=" + reason);

    if (g_webView) {
        const std::wstring html =
            L"<!doctype html><html><body style='font-family:Segoe UI;margin:40px'>"
            L"<h1>BROWSER4G P0</h1><h2 style='color:#b00'>Runtime Health Guard: FAIL</h2>"
            L"<p>Le runtime WebView2 courant a échoué au micro-probe local.</p>"
            L"<p>Aucun downgrade automatique n'est tenté. Consulte <code>%LOCALAPPDATA%\\BROWSER4G\\P0\\logs\\p0.log</code>.</p>"
            L"</body></html>";
        g_webView->NavigateToString(html.c_str());
    }
}

void MarkProbeSuccess()
{
    g_probeRunning = false;
    g_probePassed = true;
    EnableWindow(g_go, TRUE);
    SetStatus(L"Runtime Health Guard: PASS");
    if (!WriteTextAtomic(g_appRoot / L"state" / L"last_good_runtime.txt", g_runtimeVersion))
        Log(L"STATE_WRITE_WARN last_good_runtime");
    Log(L"RUNTIME_PROBE_PASS runtime=" + g_runtimeVersion);
    ShowWelcome();
}

void RunRuntimeProbe()
{
    if (!g_webView)
        return;
    g_probeRunning = true;
    g_probePassed = false;
    EnableWindow(g_go, FALSE);
    SetStatus(L"Runtime Health Guard: micro-probe local en cours...");
    Log(L"RUNTIME_PROBE_START runtime=" + g_runtimeVersion);

    EventRegistrationToken token{};
    const HRESULT hr = g_webView->add_NavigationCompleted(
        Callback<ICoreWebView2NavigationCompletedEventHandler>(
            [](ICoreWebView2*, ICoreWebView2NavigationCompletedEventArgs* args) -> HRESULT {
                if (!g_probeRunning)
                    return S_OK;

                BOOL success = FALSE;
                if (!args || FAILED(args->get_IsSuccess(&success)) || !success) {
                    MarkProbeFailure(L"NavigateToString failed");
                    return S_OK;
                }

                const wchar_t* script =
                    L"(() => {const n=document.getElementById('probe');return (n && n.dataset.ok==='1') ? 2 : 0;})()";

                const HRESULT scriptHr = g_webView->ExecuteScript(
                    script,
                    Callback<ICoreWebView2ExecuteScriptCompletedHandler>(
                        [](HRESULT errorCode, LPCWSTR resultObjectAsJson) -> HRESULT {
                            if (FAILED(errorCode) || resultObjectAsJson == nullptr || wcscmp(resultObjectAsJson, L"2") != 0) {
                                MarkProbeFailure(L"ExecuteScript failed or returned unexpected result");
                                return S_OK;
                            }
                            MarkProbeSuccess();
                            return S_OK;
                        }).Get());

                if (FAILED(scriptHr))
                    MarkProbeFailure(L"ExecuteScript dispatch failed hr=" + HrString(scriptHr));
                return S_OK;
            }).Get(),
        &token);

    if (FAILED(hr)) {
        MarkProbeFailure(L"add_NavigationCompleted failed hr=" + HrString(hr));
        return;
    }

    const wchar_t* probeHtml =
        L"<!doctype html><html><head><meta charset='utf-8'></head><body><div id='probe' data-ok='1'>BROWSER4G_RUNTIME_PROBE</div></body></html>";

    const HRESULT navHr = g_webView->NavigateToString(probeHtml);
    if (FAILED(navHr))
        MarkProbeFailure(L"NavigateToString dispatch failed hr=" + HrString(navHr));
}

void FinishWebViewStartup()
{
    if (!g_environment || !g_controller)
        return;
    g_controller->get_CoreWebView2(&g_webView);
    if (!g_webView) {
        MarkProbeFailure(L"get_CoreWebView2 returned null");
        return;
    }

    LPWSTR actual = nullptr;
    if (SUCCEEDED(g_environment->get_BrowserVersionString(&actual)) && actual) {
        const std::wstring actualVersion(actual);
        CoTaskMemFree(actual);
        if (actualVersion != g_runtimeVersion) {
            Log(L"RUNTIME_PREFLIGHT_MISMATCH preflight=" + g_runtimeVersion + L" environment=" + actualVersion);
            g_runtimeVersion = actualVersion;
            g_probeRequired = true;
        }
    }

    ResizeLayout();
    if (g_probeRequired) {
        RunRuntimeProbe();
    } else {
        g_probePassed = true;
        EnableWindow(g_go, TRUE);
        SetStatus(L"Runtime Health Guard: version inchangée / dernier micro-probe PASS");
        Log(L"RUNTIME_REUSE_GOOD runtime=" + g_runtimeVersion);
        ShowWelcome();
    }
    UpdateTelemetry(true);
}

void InitWebView(HWND hwnd)
{
    const std::wstring userDataFolder = (g_appRoot / L"UserData").wstring();
    const HRESULT hr = CreateCoreWebView2EnvironmentWithOptions(
        nullptr, userDataFolder.c_str(), nullptr,
        Callback<ICoreWebView2CreateCoreWebView2EnvironmentCompletedHandler>(
            [hwnd](HRESULT result, ICoreWebView2Environment* environment) -> HRESULT {
                if (FAILED(result) || environment == nullptr) {
                    g_runtimeReady = false;
                    SetStatus(L"Échec de création de l'environnement WebView2.");
                    Log(L"ENV_CREATE_FAIL hr=" + HrString(result));
                    return S_OK;
                }

                g_environment = environment;
                const HRESULT controllerHr = environment->CreateCoreWebView2Controller(
                    hwnd,
                    Callback<ICoreWebView2CreateCoreWebView2ControllerCompletedHandler>(
                        [](HRESULT result, ICoreWebView2Controller* controller) -> HRESULT {
                            if (FAILED(result) || controller == nullptr) {
                                SetStatus(L"Échec de création du contrôleur WebView2.");
                                Log(L"CONTROLLER_CREATE_FAIL hr=" + HrString(result));
                                return S_OK;
                            }
                            g_controller = controller;
                            FinishWebViewStartup();
                            return S_OK;
                        }).Get());

                if (FAILED(controllerHr)) {
                    SetStatus(L"Échec immédiat de CreateCoreWebView2Controller.");
                    Log(L"CONTROLLER_DISPATCH_FAIL hr=" + HrString(controllerHr));
                }
                return S_OK;
            }).Get());

    if (FAILED(hr)) {
        g_runtimeReady = false;
        SetStatus(L"Échec immédiat de CreateCoreWebView2EnvironmentWithOptions.");
        Log(L"ENV_DISPATCH_FAIL hr=" + HrString(hr));
    }
}

bool RuntimePreflight()
{
    LPWSTR version = nullptr;
    const HRESULT hr = GetAvailableCoreWebView2BrowserVersionString(nullptr, &version);
    if (FAILED(hr) || version == nullptr) {
        Log(L"RUNTIME_PREFLIGHT_FAIL hr=" + HrString(hr));
        g_runtimeReady = false;
        return false;
    }

    g_runtimeVersion = version;
    CoTaskMemFree(version);
    g_runtimeReady = true;
    g_lastGoodRuntime = ReadText(g_appRoot / L"state" / L"last_good_runtime.txt");
    g_probeRequired = g_lastGoodRuntime.empty() || g_lastGoodRuntime != g_runtimeVersion;
    WriteTextAtomic(g_appRoot / L"state" / L"last_seen_runtime.txt", g_runtimeVersion);

    Log(L"START sdk=" + std::wstring(kSdkVersion) +
        L" runtime=" + g_runtimeVersion +
        L" last_good=" + (g_lastGoodRuntime.empty() ? L"<none>" : g_lastGoodRuntime) +
        L" probe_required=" + (g_probeRequired ? L"true" : L"false"));
    return true;
}

LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    switch (msg) {
    case WM_CREATE:
        g_address = CreateWindowExW(WS_EX_CLIENTEDGE, L"EDIT", L"https://www.google.com",
            WS_CHILD | WS_VISIBLE | ES_AUTOHSCROLL, 8, 7, 600, 24, hwnd,
            reinterpret_cast<HMENU>(static_cast<INT_PTR>(kAddressId)), GetModuleHandleW(nullptr), nullptr);

        g_go = CreateWindowW(L"BUTTON", L"Go", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            620, 7, 72, 24, hwnd,
            reinterpret_cast<HMENU>(static_cast<INT_PTR>(kGoId)), GetModuleHandleW(nullptr), nullptr);

        g_status = CreateWindowW(L"STATIC", L"Initialisation...", WS_CHILD | WS_VISIBLE | SS_LEFT,
            8, 500, 700, 18, hwnd,
            reinterpret_cast<HMENU>(static_cast<INT_PTR>(kStatusId)), GetModuleHandleW(nullptr), nullptr);

        SendMessageW(g_address, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
        SendMessageW(g_go, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
        SendMessageW(g_status, WM_SETFONT, reinterpret_cast<WPARAM>(GetStockObject(DEFAULT_GUI_FONT)), TRUE);
        EnableWindow(g_go, FALSE);
        SetTimer(hwnd, kTelemetryTimer, kTelemetryIntervalMs, nullptr);
        return 0;

    case WM_SIZE:
        ResizeLayout();
        return 0;

    case WM_COMMAND:
        if (LOWORD(wParam) == kGoId && HIWORD(wParam) == BN_CLICKED) {
            NavigateFromAddressBar();
            return 0;
        }
        break;

    case WM_TIMER:
        if (wParam == kTelemetryTimer) {
            UpdateTelemetry(true);
            return 0;
        }
        break;

    case WM_DESTROY:
        KillTimer(hwnd, kTelemetryTimer);
        if (g_controller)
            g_controller->Close();
        g_webView.Reset();
        g_controller.Reset();
        g_environment.Reset();
        Log(L"STOP");
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(hwnd, msg, wParam, lParam);
}

} // namespace

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE, PWSTR, int showCmd)
{
    SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);

    const HRESULT comHr = CoInitializeEx(nullptr, COINIT_APARTMENTTHREADED);
    if (FAILED(comHr)) {
        MessageBoxW(nullptr, L"COM STA initialization failed.", kAppName, MB_ICONERROR);
        return 2;
    }

    g_appRoot = AppRoot();
    EnsureDirectories();
    const bool runtimeOk = RuntimePreflight();

    WNDCLASSEXW wc{};
    wc.cbSize = sizeof(wc);
    wc.lpfnWndProc = WndProc;
    wc.hInstance = instance;
    wc.hCursor = LoadCursorW(nullptr, IDC_ARROW);
    wc.hIcon = LoadIconW(nullptr, IDI_APPLICATION);
    wc.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_WINDOW + 1);
    wc.lpszClassName = kWindowClass;

    if (!RegisterClassExW(&wc)) {
        Log(L"WINDOW_CLASS_FAIL error=" + std::to_wstring(GetLastError()));
        CoUninitialize();
        return 3;
    }

    g_mainWindow = CreateWindowExW(0, kWindowClass, kAppName, WS_OVERLAPPEDWINDOW,
        CW_USEDEFAULT, CW_USEDEFAULT, 1100, 760, nullptr, nullptr, instance, nullptr);

    if (!g_mainWindow) {
        Log(L"WINDOW_CREATE_FAIL error=" + std::to_wstring(GetLastError()));
        CoUninitialize();
        return 4;
    }

    ShowWindow(g_mainWindow, showCmd);
    UpdateWindow(g_mainWindow);
    UpdateTelemetry(true);

    if (runtimeOk) {
        InitWebView(g_mainWindow);
    } else {
        SetStatus(L"WebView2 Runtime introuvable. Installe/répare le Runtime Evergreen puis relance.");
        MessageBoxW(g_mainWindow,
            L"Microsoft Edge WebView2 Runtime est introuvable.\nBROWSER4G P0 ne tente aucun downgrade ni runtime alternatif automatique.",
            kAppName, MB_OK | MB_ICONERROR);
    }

    MSG msg{};
    while (GetMessageW(&msg, nullptr, 0, 0) > 0) {
        TranslateMessage(&msg);
        DispatchMessageW(&msg);
    }

    CoUninitialize();
    return static_cast<int>(msg.wParam);
}

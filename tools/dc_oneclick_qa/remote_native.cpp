// MBMPC Remote OneClick Native G1. Win32 GUI only, no resident watcher.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <tlhelp32.h>
#include <winhttp.h>
#include <psapi.h>
#include <winternl.h>
#include <cstring>
#include <cstdlib>
#include <string>
#include <vector>
#include <cstdio>
#include <cwchar>

#pragma comment(lib,"winhttp.lib")
#pragma comment(lib,"psapi.lib")
#pragma comment(lib,"gdi32.lib")
#pragma comment(lib,"user32.lib")

static HWND g_window=nullptr, g_launch=nullptr, g_consoleButton=nullptr;
static HFONT g_title=nullptr, g_body=nullptr, g_small=nullptr;
static HANDLE g_remote=nullptr, g_mutex=nullptr;
static DWORD g_remotePid=0;
static bool g_spawned=false, g_existing=false, g_laboratory=false, g_firstPaint=false;
static int g_network=0;
static std::wstring g_status=L"Préparation...",g_detail=L"Recherche d'une session Remote existante.";
static const wchar_t* kCommand=L"npx.cmd --yes @wonderwhy-er/desktop-commander@latest remote";
static const wchar_t* kWindow=L"MBMPC_REMOTE_ONECLICK_NATIVE";
static const int BUTTON_LAUNCH=101, BUTTON_CONSOLE=102, WM_NETWORK=WM_APP+17, WM_BOOTSTRAP=WM_APP+18;

std::wstring env(const wchar_t* name) {
    DWORD n=GetEnvironmentVariableW(name,nullptr,0);
    if(n==0 || n>32767) return L"";
    std::wstring s(n,L'\0'); DWORD got=GetEnvironmentVariableW(name,&s[0],n);
    if(got==0 || got>=n) return L"";
    s.resize(got); return s;
}
void logline(const wchar_t* event) {
    std::wstring file=env(L"MBMPC_LAB_LOG");
    if(file.empty()){
        std::wstring root=env(L"LOCALAPPDATA");
        if(root.empty()) return;
        root+=L"\\MBMPC-RemoteOneClick";
        CreateDirectoryW(root.c_str(),nullptr);
        file=root+L"\\native-events.log";
    }
    HANDLE h=CreateFileW(file.c_str(),FILE_APPEND_DATA,FILE_SHARE_READ,nullptr,OPEN_ALWAYS,FILE_ATTRIBUTE_NORMAL,nullptr);
    if(h==INVALID_HANDLE_VALUE) return;
    SYSTEMTIME t; GetLocalTime(&t);
    char line[200]={};
    char eventA[90]={};
    WideCharToMultiByte(CP_UTF8,0,event,-1,eventA,sizeof(eventA),nullptr,nullptr);
    int z=std::snprintf(line,sizeof(line),"%04u-%02u-%02u %02u:%02u:%02u %s\n",
       t.wYear,t.wMonth,t.wDay,t.wHour,t.wMinute,t.wSecond,eventA);
    if(z>0) {DWORD w=0; WriteFile(h,line,(DWORD)z,&w,nullptr);}
    CloseHandle(h);
}
std::wstring queryCmd(DWORD pid) {
    HANDLE h=OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION,FALSE,pid);
    if(!h) return L"";
    using Fn=LONG (NTAPI*)(HANDLE,ULONG,PVOID,ULONG,PULONG);
    Fn nt=reinterpret_cast<Fn>(GetProcAddress(GetModuleHandleW(L"ntdll.dll"),"NtQueryInformationProcess"));
    if(!nt){CloseHandle(h);return L"";}
    ULONG size=0; nt(h,60,nullptr,0,&size);
    if(size<sizeof(UNICODE_STRING) || size>65536){CloseHandle(h);return L"";}
    std::vector<BYTE> data(size+32);
    LONG status=nt(h,60,data.data(),(ULONG)data.size(),&size);
    CloseHandle(h);
    if(status!=0) return L"";
    struct BasicUnicode { USHORT len; USHORT cap; PWSTR str; };
    BasicUnicode u={}; memcpy(&u,data.data(),sizeof(u));
    auto lo=reinterpret_cast<ULONG_PTR>(data.data());
    auto hi=lo+data.size(), start=reinterpret_cast<ULONG_PTR>(u.str);
    if(!u.str || start<lo || start+u.len>hi || u.len%2) return L"";
    return std::wstring(u.str,u.len/sizeof(wchar_t));
}
bool remoteAlreadyRunning() {
    // Exact Desktop Commander package signature; never treat all node.exe as Remote.
    HANDLE snap=CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0);
    if(snap==INVALID_HANDLE_VALUE) return false;
    PROCESSENTRY32W e={};e.dwSize=sizeof(e);
    bool found=false;
    if(Process32FirstW(snap,&e)) do {
        if(_wcsicmp(e.szExeFile,L"cmd.exe") && _wcsicmp(e.szExeFile,L"node.exe")) continue;
        std::wstring c=queryCmd(e.th32ProcessID);
        if(c.empty()) continue;
        if(c.find(L"@wonderwhy-er/desktop-commander")!=std::wstring::npos ||
           c.find(L"@wonderwhy-er\\desktop-commander\\dist\\index.js")!=std::wstring::npos ||
           c.find(L"@wonderwhy-er/desktop-commander/dist/index.js")!=std::wstring::npos ||
           c.find(L"Desktop-Commander-ONE-CLICK.cmd")!=std::wstring::npos){
              if(c.find(L" remote")!=std::wstring::npos) {found=true;break;}
        }
    }while(Process32NextW(snap,&e));
    CloseHandle(snap); return found;
}
void setStatus(const std::wstring& title,const std::wstring& description){
    g_status=title; g_detail=description;
    if(g_window) InvalidateRect(g_window,nullptr,FALSE);
}
bool spawnRemote() {
    wchar_t sys[MAX_PATH]={};
    GetSystemDirectoryW(sys,MAX_PATH);
    std::wstring exe=std::wstring(sys)+L"\\cmd.exe";
    std::wstring command=L"\""+exe+L"\" /d /k "+kCommand;
    std::vector<wchar_t> mutableCmd(command.begin(),command.end());
    mutableCmd.push_back(0);
    STARTUPINFOW si={};si.cb=sizeof(si);si.dwFlags=STARTF_USESHOWWINDOW;si.wShowWindow=SW_SHOWNORMAL;
    PROCESS_INFORMATION pi={};
    BOOL ok=CreateProcessW(exe.c_str(),mutableCmd.data(),nullptr,nullptr,FALSE,
            CREATE_NEW_CONSOLE|CREATE_DEFAULT_ERROR_MODE,nullptr,nullptr,&si,&pi);
    if(!ok){
       DWORD error=GetLastError();
       wchar_t b[200];
       swprintf_s(b,L"Impossible de lancer CMD (erreur Windows %lu).",error);
       setStatus(L"Le démarrage a échoué",b);
       logline(L"CMD_CREATE_FAILED");
       return false;
    }
    g_remotePid=pi.dwProcessId;
    if(g_remote) CloseHandle(g_remote);
    g_remote=pi.hProcess;
    CloseHandle(pi.hThread);
    g_spawned=true;
    setStatus(L"Connexion lancée",L"La fenêtre CMD travaille. Garde-la ouverte pour rester connecté.");
    logline(L"CMD_SPAWNED");
    return true;
}
bool networkAvailable() {
    if(g_laboratory){
        std::wstring state=env(L"MBMPC_LAB_NET");
        return state!=L"offline";
    }
    HINTERNET session=WinHttpOpen(L"MBMPC-RemoteOneClick/1.0",WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                  WINHTTP_NO_PROXY_NAME,WINHTTP_NO_PROXY_BYPASS,0);
    if(!session) return false;
    WinHttpSetTimeouts(session,1200,1200,1600,1600);
    HINTERNET conn=WinHttpConnect(session,L"registry.npmjs.org",INTERNET_DEFAULT_HTTPS_PORT,0);
    bool result=false;
    if(conn){
      HINTERNET req=WinHttpOpenRequest(conn,L"HEAD",L"/",nullptr,WINHTTP_NO_REFERER,
                                      WINHTTP_DEFAULT_ACCEPT_TYPES,WINHTTP_FLAG_SECURE);
      if(req){
        if(WinHttpSendRequest(req,WINHTTP_NO_ADDITIONAL_HEADERS,0,WINHTTP_NO_REQUEST_DATA,0,0,0)
           && WinHttpReceiveResponse(req,nullptr)){
              DWORD code=0,size=sizeof(code);
              if(WinHttpQueryHeaders(req,WINHTTP_QUERY_STATUS_CODE|WINHTTP_QUERY_FLAG_NUMBER,
                 WINHTTP_HEADER_NAME_BY_INDEX,&code,&size,WINHTTP_NO_HEADER_INDEX))
                 result=(code>=200 && code<500);
        }
        WinHttpCloseHandle(req);
      }
      WinHttpCloseHandle(conn);
    }
    WinHttpCloseHandle(session);
    return result;
}
DWORD WINAPI networkThread(LPVOID) {
    bool ok=networkAvailable();
    if(g_window) PostMessageW(g_window,WM_NETWORK,ok?1:2,0);
    return 0;
}
DWORD WINAPI bootstrapThread(LPVOID) {
    bool found=remoteAlreadyRunning();
    if(g_window) PostMessageW(g_window,WM_BOOTSTRAP,found?1:0,0);
    return 0;
}
void drawText(HDC dc,const wchar_t* text,int x,int y,int w,int h,HFONT f,COLORREF color,UINT flags=DT_LEFT|DT_WORDBREAK){
    SelectObject(dc,f);SetTextColor(dc,color);SetBkMode(dc,TRANSPARENT);
    RECT r={x,y,x+w,y+h};DrawTextW(dc,text,-1,&r,flags);
}
void rect(HDC dc,RECT r,COLORREF fill,int radius=12) {
    HBRUSH b=CreateSolidBrush(fill),old=(HBRUSH)SelectObject(dc,b);
    HPEN p=CreatePen(PS_SOLID,1,fill),op=(HPEN)SelectObject(dc,p);
    RoundRect(dc,r.left,r.top,r.right,r.bottom,radius,radius);
    SelectObject(dc,op);SelectObject(dc,old);DeleteObject(p);DeleteObject(b);
}
int memoryPercent(DWORD& freeMb) {
    std::wstring fake=env(L"MBMPC_LAB_RAM");
    if(g_laboratory&&!fake.empty()) {
        freeMb=250; int p=_wtoi(fake.c_str());
        return p>100?100:(p<0?0:p);
    }
    MEMORYSTATUSEX ms={};ms.dwLength=sizeof(ms);
    if(!GlobalMemoryStatusEx(&ms)){freeMb=0;return -1;}
    freeMb=(DWORD)(ms.ullAvailPhys/1048576);
    return (int)ms.dwMemoryLoad;
}
void paint(HWND h) {
    PAINTSTRUCT ps={};HDC dc=BeginPaint(h,&ps);
    RECT outer;GetClientRect(h,&outer);
    HDC mem=CreateCompatibleDC(dc);
    HBITMAP bitmap=CreateCompatibleBitmap(dc,outer.right,outer.bottom);
    auto prev=SelectObject(mem,bitmap);
    HBRUSH bg=CreateSolidBrush(RGB(244,247,251));FillRect(mem,&outer,bg);DeleteObject(bg);
    rect(mem,{20,20,outer.right-20,79},RGB(14,38,65),18);
    drawText(mem,L"◉",36,34,28,30,g_title,RGB(106,219,169),DT_SINGLELINE);
    drawText(mem,L"REMOTE • MBMPC",70,31,355,27,g_title,RGB(255,255,255),DT_SINGLELINE);
    drawText(mem,L"Ton PC, reconnecté sans complication.",70,56,330,18,g_small,RGB(192,208,228),DT_SINGLELINE);
    rect(mem,{20,94,outer.right-20,178},RGB(255,255,255),17);
    COLORREF stColor=g_spawned?RGB(14,123,90):(g_existing?RGB(37,91,167):RGB(157,101,36));
    drawText(mem,g_status.c_str(),39,107,380,29,g_body,stColor,DT_SINGLELINE|DT_END_ELLIPSIS);
    drawText(mem,g_detail.c_str(),39,137,382,37,g_small,RGB(71,87,104));
    rect(mem,{20,194,225,272},RGB(255,255,255),16);
    rect(mem,{240,194,outer.right-20,272},RGB(255,255,255),16);
    DWORD freeMb=0; int load=memoryPercent(freeMb);
    wchar_t ram[90]={};
    swprintf_s(ram,L"%d %% • %lu Mo libres",load,freeMb);
    drawText(mem,L"MÉMOIRE",35,207,180,22,g_small,RGB(88,104,126),DT_SINGLELINE);
    drawText(mem,ram,35,235,181,25,g_small,load>=92?RGB(180,76,38):RGB(17,55,86),DT_SINGLELINE|DT_END_ELLIPSIS);
    drawText(mem,L"INTERNET",255,207,170,22,g_small,RGB(88,104,126),DT_SINGLELINE);
    const wchar_t* nt=g_network==1?L"Accès npm disponible":g_network==2?L"Réseau à vérifier":L"Vérification en cours...";
    drawText(mem,nt,255,235,177,25,g_small,g_network==2?RGB(180,76,38):RGB(17,55,86),DT_SINGLELINE|DT_END_ELLIPSIS);
    drawText(mem,L"Le démarrage local n'est pas une preuve de connexion cloud.",22,344,430,28,g_small,RGB(97,110,123));
    BitBlt(dc,0,0,outer.right,outer.bottom,mem,0,0,SRCCOPY);
    SelectObject(mem,prev);DeleteObject(bitmap);DeleteDC(mem);EndPaint(h,&ps);
}
LRESULT CALLBACK wndProc(HWND hwnd,UINT msg,WPARAM wp,LPARAM lp) {
    switch(msg){
      case WM_CREATE:{
        g_window=hwnd;
        g_title=CreateFontW(22,0,0,0,FW_BOLD,FALSE,FALSE,FALSE,DEFAULT_CHARSET,0,0,CLEARTYPE_QUALITY,0,L"Segoe UI");
        g_body=CreateFontW(21,0,0,0,FW_SEMIBOLD,FALSE,FALSE,FALSE,DEFAULT_CHARSET,0,0,CLEARTYPE_QUALITY,0,L"Segoe UI");
        g_small=CreateFontW(16,0,0,0,FW_NORMAL,FALSE,FALSE,FALSE,DEFAULT_CHARSET,0,0,CLEARTYPE_QUALITY,0,L"Segoe UI");
        g_launch=CreateWindowExW(0,L"BUTTON",L"Nouvelle tentative",WS_CHILD|WS_VISIBLE|BS_OWNERDRAW,
               20,288,208,40,hwnd,(HMENU)(INT_PTR)BUTTON_LAUNCH,nullptr,nullptr);
        g_consoleButton=CreateWindowExW(0,L"BUTTON",L"Fermer cet écran",WS_CHILD|WS_VISIBLE|BS_OWNERDRAW,
               241,288,208,40,hwnd,(HMENU)(INT_PTR)BUTTON_CONSOLE,nullptr,nullptr);
        SendMessageW(g_launch,WM_SETFONT,(WPARAM)g_small,TRUE);
        SendMessageW(g_consoleButton,WM_SETFONT,(WPARAM)g_small,TRUE);
        setStatus(L"Préparation de Remote",L"Je vérifie la session existante sans bloquer l'écran.");
        HANDLE starter=CreateThread(nullptr,0,bootstrapThread,nullptr,0,nullptr);
        if(starter) CloseHandle(starter);
        else {setStatus(L"Vérification indisponible",L"Windows manque de ressources. Réessaie avec le bouton.");logline(L"BOOTSTRAP_THREAD_FAILED");}
        HANDLE th=CreateThread(nullptr,0,networkThread,nullptr,0,nullptr);
        if(th) CloseHandle(th);
        SetTimer(hwnd,11,2500,nullptr);
        return 0;
      }
      case WM_DRAWITEM: {
        auto item=reinterpret_cast<DRAWITEMSTRUCT*>(lp);
        if(!item || (item->CtlID!=BUTTON_LAUNCH && item->CtlID!=BUTTON_CONSOLE)) break;
        const bool primary=item->CtlID==BUTTON_LAUNCH;
        const bool pressed=(item->itemState & ODS_SELECTED)!=0;
        COLORREF fill=primary?(pressed?RGB(15,65,116):RGB(23,95,166)):
                              (pressed?RGB(207,225,243):RGB(228,237,248));
        rect(item->hDC,item->rcItem,fill,15);
        wchar_t b[90]={};GetWindowTextW(item->hwndItem,b,90);
        RECT r=item->rcItem;
        SetBkMode(item->hDC,TRANSPARENT);
        SelectObject(item->hDC,g_small);
        SetTextColor(item->hDC,primary?RGB(255,255,255):RGB(17,58,101));
        DrawTextW(item->hDC,b,-1,&r,DT_CENTER|DT_VCENTER|DT_SINGLELINE);
        return TRUE;
      }
      case WM_BOOTSTRAP:
        g_existing=(wp!=0);
        if(g_existing){setStatus(L"Remote est déjà lancé",L"Je préserve cette session. Si elle est bloquée, fais une nouvelle tentative.");logline(L"REMOTE_ALREADY_RUNNING");}
        else spawnRemote();
        return 0;
      case WM_NETWORK:
        g_network=(int)wp;
        logline(g_network==1?L"NETWORK_REGISTRY_OK":L"NETWORK_CHECK_FAILED");
        if(g_network==2 && !g_existing && g_spawned) {
            g_detail=L"Réseau ou npm inaccessible. Vérifie le Wi-Fi; CMD reste ouverte.";
        }
        InvalidateRect(hwnd,nullptr,FALSE);return 0;
      case WM_TIMER:
        if(wp==11){
            if(g_remote && WaitForSingleObject(g_remote,0)==WAIT_OBJECT_0) {
                g_spawned=false;
                setStatus(L"Le terminal s'est fermé",L"Relance après avoir vérifié le réseau et Node.js.");
                logline(L"CMD_EXITED");
                CloseHandle(g_remote);g_remote=nullptr;
                KillTimer(hwnd,11);
            }else InvalidateRect(hwnd,nullptr,FALSE);
        }return 0;
      case WM_COMMAND:
        if(LOWORD(wp)==BUTTON_LAUNCH){
            if(g_existing){
               if(MessageBoxW(hwnd,L"Un autre Remote semble déjà tourner.\n\nUne nouvelle session utilisera davantage de RAM. Continuer ?",
                    L"Nouvelle session Remote",MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2)!=IDYES)return 0;
            }
            g_existing=false;
            spawnRemote();
            return 0;
        }
        if(LOWORD(wp)==BUTTON_CONSOLE){DestroyWindow(hwnd);return 0;}
        return 0;
      case WM_PAINT:
        if(!g_firstPaint){g_firstPaint=true;logline(L"UI_FIRST_PAINT");}
        paint(hwnd);return 0;
      case WM_ERASEBKGND:return 1;
      case WM_CLOSE:DestroyWindow(hwnd);return 0;
      case WM_DESTROY:
         if(g_title)DeleteObject(g_title);if(g_body)DeleteObject(g_body);if(g_small)DeleteObject(g_small);
         if(g_remote)CloseHandle(g_remote);
         // No process termination: closing the little UI does not stop the remote.
         PostQuitMessage(0);return 0;
    }
    return DefWindowProcW(hwnd,msg,wp,lp);
}
int WINAPI wWinMain(HINSTANCE app,HINSTANCE,PWSTR,int) {
    g_laboratory=(env(L"MBMPC_LAB_MODE")==L"1");
    g_mutex=CreateMutexW(nullptr,TRUE,L"Local\\MBMPC_REMOTE_ONECLICK_NATIVE_G1");
    if(!g_mutex) return 2;
    if(GetLastError()==ERROR_ALREADY_EXISTS) {
        HWND old=FindWindowW(kWindow,nullptr);
        if(old){ShowWindow(old,SW_RESTORE);SetForegroundWindow(old);}
        CloseHandle(g_mutex);return 0;
    }
    WNDCLASSEXW wc={};wc.cbSize=sizeof(wc);wc.lpfnWndProc=wndProc;
    wc.hInstance=app;wc.lpszClassName=kWindow;
    wc.hCursor=LoadCursorW(nullptr,IDC_ARROW);
    wc.hIcon=LoadIconW(nullptr,IDI_APPLICATION);
    wc.hbrBackground=(HBRUSH)(COLOR_WINDOW+1);
    if(!RegisterClassExW(&wc))return 3;
    HWND h=CreateWindowExW(0,kWindow,L"Desktop Commander • Reconnexion",
          WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX,
          CW_USEDEFAULT,CW_USEDEFAULT,483,413,nullptr,nullptr,app,nullptr);
    if(!h)return 4;
    ShowWindow(h,SW_SHOWNORMAL);UpdateWindow(h);
    MSG m;while(GetMessageW(&m,nullptr,0,0)>0){TranslateMessage(&m);DispatchMessageW(&m);}
    ReleaseMutex(g_mutex);CloseHandle(g_mutex);return 0;
}

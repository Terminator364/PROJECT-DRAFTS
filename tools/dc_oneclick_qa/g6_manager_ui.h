#pragma once
#include <shellapi.h>
#include "g6_approved_networks.h"

// Included from G6's Win32 main, after the global window/state declarations.
static const int NET_LIST=220, NET_ADD=221, NET_REMOVE=222, NET_WINDOWS=223, NET_REFRESH=224;
static HWND g_netWindow=nullptr, g_netList=nullptr;
static std::vector<RemoteApprovedNetwork> g_netItems;

static void drawApprovedNetworks(){
    if(!g_netList || !IsWindow(g_netList))return;
    SendMessageW(g_netList,LB_RESETCONTENT,0,0);
    g_netItems.clear();
    if(!loadApproved(g_netItems)){
        SendMessageW(g_netList,LB_ADDSTRING,0,(LPARAM)L"Fichier illisible — accès bloqué");
        return;
    }
    for(const auto& item:g_netItems) {
        std::wstring txt=item.ssid+L"  •  "+item.adapter;
        SendMessageW(g_netList,LB_ADDSTRING,0,(LPARAM)txt.c_str());
    }
    if(g_netItems.empty())SendMessageW(g_netList,LB_ADDSTRING,0,(LPARAM)L"Aucun réseau autorisé");
}
static void updateApprovalState(){
    g_wifi.approvedHome=hasApproved(g_wifi.ssid,g_wifi.wifiAdapterId);
    if(g_window)InvalidateRect(g_window,nullptr,FALSE);
}
static LRESULT CALLBACK networkManagerProc(HWND win,UINT msg,WPARAM wp,LPARAM lp){
    switch(msg){
    case WM_CREATE:{
        auto font=(HFONT)GetStockObject(DEFAULT_GUI_FONT);
        auto add=[&](const wchar_t* c,const wchar_t* label,int id,DWORD style,int x,int y,int w,int h){
            HWND child=CreateWindowExW(0,c,label,WS_VISIBLE|WS_CHILD|style,x,y,w,h,win,(HMENU)(INT_PTR)id,GetModuleHandleW(nullptr),nullptr);
            if(child)SendMessageW(child,WM_SETFONT,(WPARAM)font,TRUE);
            return child;
        };
        add(L"STATIC",L"Les réseaux autorisés pour une NOUVELLE connexion Remote :",0,0,15,14,460,25);
        g_netList=add(L"LISTBOX",L"",NET_LIST,WS_BORDER|WS_VSCROLL|LBS_NOTIFY,15,44,450,164);
        add(L"BUTTON",L"Autoriser le Wi-Fi connecté",NET_ADD,BS_PUSHBUTTON,15,218,217,39);
        add(L"BUTTON",L"Retirer la sélection",NET_REMOVE,BS_PUSHBUTTON,242,218,223,39);
        add(L"BUTTON",L"Actualiser la liste",NET_REFRESH,BS_PUSHBUTTON,15,268,164,38);
        add(L"BUTTON",L"Wi-Fi Windows (changer / déconnecter)",NET_WINDOWS,BS_PUSHBUTTON,187,268,278,38);
        add(L"STATIC",L"Retirer une autorisation ne coupe pas Remote.",0,0,15,320,455,24);
        drawApprovedNetworks();
        return 0;
    }
    case WM_COMMAND:{
        switch(LOWORD(wp)){
        case NET_REFRESH:drawApprovedNetworks();return 0;
        case NET_ADD:{
            auto now=detectNetwork();
            if(now.wifi!=WifiClass::Connected||!now.secured||now.ssid.empty()){
                MessageBoxW(win,L"Connecte-toi à un Wi-Fi sécurisé avant de l'autoriser.",
                            L"Wi-Fi non vérifiable",MB_OK|MB_ICONWARNING);return 0;
            }
            std::wstring prompt=L"Autoriser ce Wi-Fi : "+now.ssid+
                L"\n\nAttention : une connexion mobile peut être facturée.\nWindows doit aussi signaler un coût NON LIMITÉ avant tout lancement.\n\nConfirmer ?";
            if(MessageBoxW(win,prompt.c_str(),L"Autorisation réseau",MB_YESNO|MB_ICONQUESTION|MB_DEFBUTTON2)!=IDYES)return 0;
            auto recheck=detectNetwork();
            if(recheck.wifi!=WifiClass::Connected||recheck.ssid!=now.ssid||
               _wcsicmp(recheck.wifiAdapterId.c_str(),now.wifiAdapterId.c_str())!=0||!recheck.secured){
                MessageBoxW(win,L"Le réseau a changé. Rien n'a été enregistré.",
                            L"Changement détecté",MB_OK|MB_ICONWARNING);return 0;
            }
            if(!grantApproved({now.ssid,now.wifiAdapterId})){
                MessageBoxW(win,L"Impossible d'enregistrer ce réseau. La liste reste protégée.",
                            L"Erreur",MB_OK|MB_ICONERROR);return 0;
            }
            logline(L"G6_USER_GRANTED_WIFI");
            drawApprovedNetworks();
            updateApprovalState();
            return 0;
        }
        case NET_REMOVE:{
            LRESULT i=SendMessageW(g_netList,LB_GETCURSEL,0,0);
            if(i==LB_ERR || (size_t)i>=g_netItems.size()){
                MessageBoxW(win,L"Sélectionne un réseau enregistré.",L"Aucune sélection",MB_OK|MB_ICONINFORMATION);return 0;
            }
            auto item=g_netItems[(size_t)i];
            std::wstring prompt=L"Retirer l'autorisation de : "+item.ssid+
                 L"\n\nAucune session Remote déjà active ne sera interrompue.\n\nConfirmer ?";
            if(MessageBoxW(win,prompt.c_str(),L"Retirer l'autorisation ?",MB_YESNO|MB_ICONWARNING|MB_DEFBUTTON2)!=IDYES)return 0;
            if(!revokeApproved(item)){
                MessageBoxW(win,L"Retrait impossible. Réessaie.",L"Erreur",MB_OK|MB_ICONERROR);return 0;
            }
            logline(L"G6_USER_REVOKED_WIFI");
            drawApprovedNetworks();
            updateApprovalState();
            return 0;
        }
        case NET_WINDOWS:
            if(MessageBoxW(win,L"Changer ou déconnecter le Wi-Fi dans Windows peut interrompre Remote.\n\nOuvrir les paramètres Wi-Fi ?",
                            L"Connexion réseau",MB_YESNO|MB_ICONWARNING|MB_DEFBUTTON2)==IDYES)
                ShellExecuteW(win,L"open",L"ms-settings:network-wifi",nullptr,nullptr,SW_SHOWNORMAL);
            return 0;
        }
        return 0;
    }
    case WM_CLOSE:DestroyWindow(win);return 0;
    case WM_DESTROY:
        g_netWindow=nullptr;g_netList=nullptr;g_netItems.clear();
        return 0;
    }
    return DefWindowProcW(win,msg,wp,lp);
}
static void showNetworkManager(){
    if(g_netWindow && IsWindow(g_netWindow)){
        ShowWindow(g_netWindow,SW_RESTORE);
        SetForegroundWindow(g_netWindow);return;
    }
    HINSTANCE module=GetModuleHandleW(nullptr);
    WNDCLASSW wc={};wc.hInstance=module;wc.lpfnWndProc=networkManagerProc;
    wc.lpszClassName=L"MBMPC_G6_APPROVED_NETS";wc.hCursor=LoadCursorW(nullptr,IDC_ARROW);
    wc.hbrBackground=(HBRUSH)(COLOR_WINDOW+1);
    const ATOM atom=RegisterClassW(&wc);
    if(!atom && GetLastError()!=ERROR_CLASS_ALREADY_EXISTS){
        logline(L"G6_MANAGER_REGISTERCLASS_FAILED");
        return;
    }
    // Independent top-level window: avoids reliance on the parent/owner state
    // while the UI is being initialized under memory pressure.
    g_netWindow=CreateWindowExW(WS_EX_TOOLWINDOW,wc.lpszClassName,L"Remote • Réseaux autorisés",
                    WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX,
                    CW_USEDEFAULT,CW_USEDEFAULT,497,402,nullptr,nullptr,module,nullptr);
    if(g_netWindow){
       logline(L"G6_MANAGER_CREATED");
       ShowWindow(g_netWindow,SW_SHOW);
       UpdateWindow(g_netWindow);
    }else{
       DWORD err=GetLastError();
       wchar_t notice[96]={};
       swprintf_s(notice,L"G6_MANAGER_CREATE_FAILED_%lu",err);
       logline(notice);
       MessageBoxW(g_window,L"Impossible d'ouvrir les paramètres des réseaux. La connexion Remote reste active.",
                   L"Paramètres indisponibles",MB_OK|MB_ICONWARNING);
    }
}

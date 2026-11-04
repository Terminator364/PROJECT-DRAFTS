#!/usr/bin/env python3
"""KIN MOTO local-only development server: no account, CDN or Vercel.

Requires only Python 3 stdlib. Defaults to loopback for safety.
For a phone on the same *trusted* Wi-Fi, use --lan deliberately; HTTP LAN
is not a secure context for service workers/PWA installation on mobile.
"""
import argparse
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


class LocalHandler(SimpleHTTPRequestHandler):
    extensions_map = {**SimpleHTTPRequestHandler.extensions_map,
                      ".webmanifest": "application/manifest+json",
                      ".js": "application/javascript",
                      ".svg": "image/svg+xml",
                      ".png": "image/png"}

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, max-age=0')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        super().end_headers()

    def log_message(self, fmt, *args):
        print('[KINMOTO localhost] ' + (fmt % args), flush=True)


def parse_args(argv=None):
    p = argparse.ArgumentParser(description='KIN MOTO — serveur de test local sans déploiement')
    p.add_argument('--root', default=None, help='Dossier dist; défaut : ../dist relatif au script')
    p.add_argument('--port', type=int, default=8789)
    p.add_argument('--lan', action='store_true', help='ATTENTION : rend le jeu visible au réseau Wi-Fi local (HTTP).')
    return p.parse_args(argv)


def main(argv=None):
    opts = parse_args(argv)
    if not 1024 <= opts.port <= 65535:
        raise SystemExit('Port doit être entre 1024 et 65535')
    root = (Path(opts.root) if opts.root else Path(__file__).resolve().parent.parent / 'dist').resolve()
    if not (root / 'index.html').is_file():
        raise SystemExit(f'index.html absent dans {root}. Exécuter python build.py avant.')
    address = '0.0.0.0' if opts.lan else '127.0.0.1'
    handler = functools.partial(LocalHandler, directory=str(root))
    with ThreadingHTTPServer((address, opts.port), handler) as server:
        print(f'KIN MOTO — HTTP LOCAL : http://localhost:{opts.port}/', flush=True)
        print('Vercel : AUCUN APPEL. Ctrl+C pour arrêter.', flush=True)
        if opts.lan:
            print('ATTENTION : accessible aux appareils du Wi-Fi privé. Ne pas utiliser sur un réseau public.', flush=True)
            print('Sur Android en HTTP LAN : jeu 3D possible, installation PWA hors ligne non garantie.', flush=True)
        server.serve_forever(poll_interval=.3)


if __name__ == '__main__':
    main()

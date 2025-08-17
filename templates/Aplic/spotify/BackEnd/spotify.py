from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, request, session, url_for, jsonify
from login import roles_required
from menu import cargar_menu
import requests
import base64
import time

spotify_bp = Blueprint('indexspotify', __name__)

# Tus credenciales Spotify
CLIENT_ID = "221d18b67f2d4705a132d532b1d12ab2"
CLIENT_SECRET = "e7718966e674453c8dfe80e35728d519"
REDIRECT_URI = "http://127.0.0.1:5000/callback"
SCOPE = "user-read-email user-read-playback-state user-modify-playback-state streaming playlist-read-private"

def get_tokens():
    """Devuelve access_token y refresh_token desde la sesión."""
    return session.get("spotify_token"), session.get("spotify_refresh_token"), session.get("spotify_token_expiry", 0)

def save_tokens(access_token, refresh_token, expires_in):
    session["spotify_token"] = access_token
    session["spotify_refresh_token"] = refresh_token
    session["spotify_token_expiry"] = int(time.time()) + expires_in - 60  # 60s antes para seguridad

def refresh_token_if_needed():
    access_token, refresh_token, expiry = get_tokens()
    if not access_token or time.time() > expiry:
        if not refresh_token:
            return None  # No se puede refrescar
        # Refrescar token
        token_url = "https://accounts.spotify.com/api/token"
        auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        resp = requests.post(token_url, headers=headers, data=data)
        if resp.ok:
            tokens = resp.json()
            access_token = tokens["access_token"]
            expires_in = tokens.get("expires_in", 3600)
            # Spotify no siempre devuelve refresh_token al refrescar
            save_tokens(access_token, refresh_token, expires_in)
            return access_token
        else:
            return None
    return access_token

def get_all_playlists(token):
    headers = {"Authorization": f"Bearer {token}"}
    playlists = []
    url = "https://api.spotify.com/v1/me/playlists"

    while url:
        r = requests.get(url, headers=headers)
        if not r.ok:
            break
        data = r.json()
        playlists.extend(data.get("items", []))
        url = data.get("next")
    return playlists

def get_spotify_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    r = requests.get("https://api.spotify.com/v1/me", headers=headers)
    if r.ok:
        return r.json().get("display_name") or r.json().get("id")
    return "Usuario Spotify"

@spotify_bp.route('/spotify')
@login_required
@roles_required('viewer')
def indexspotify():
    nemu = cargar_menu()
    access_token = refresh_token_if_needed()
    spotify_user = None
    playlists = []

    if access_token:
        spotify_user = get_spotify_user(access_token)
        playlists = get_all_playlists(access_token)

    return render_template('Aplic/spotify/FrontEnd/spotify.html',
                           nemu=nemu, roles=current_user.roles,
                           access_token=access_token,
                           spotify_user=spotify_user,
                           playlists=playlists)

@spotify_bp.route('/login_spotify')
def login_spotify():
    auth_url = (
        "https://accounts.spotify.com/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPE.replace(' ', '%20')}"
    )
    return redirect(auth_url)

@spotify_bp.route('/callback')
def spotify_callback():
    code = request.args.get('code')
    if not code:
        return "Error: No se recibió el código de autenticación."

    token_url = "https://accounts.spotify.com/api/token"
    auth_header = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        return f"Error al obtener token: {response.text}"

    tokens = response.json()
    access_token = tokens["access_token"]
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in", 3600)

    save_tokens(access_token, refresh_token, expires_in)

    return redirect(url_for('indexspotify.indexspotify'))

# Endpoints para controlar reproducción

@spotify_bp.route('/spotify/play', methods=['POST'])
@login_required
def spotify_play():
    access_token = refresh_token_if_needed()
    if not access_token:
        return jsonify({"error": "Token inválido"}), 401
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.put("https://api.spotify.com/v1/me/player/play", headers=headers)
    return jsonify({"status": resp.status_code})

@spotify_bp.route('/spotify/pause', methods=['POST'])
@login_required
def spotify_pause():
    access_token = refresh_token_if_needed()
    if not access_token:
        return jsonify({"error": "Token inválido"}), 401
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.put("https://api.spotify.com/v1/me/player/pause", headers=headers)
    return jsonify({"status": resp.status_code})

@spotify_bp.route('/spotify/next', methods=['POST'])
@login_required
def spotify_next():
    access_token = refresh_token_if_needed()
    if not access_token:
        return jsonify({"error": "Token inválido"}), 401
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.post("https://api.spotify.com/v1/me/player/next", headers=headers)
    return jsonify({"status": resp.status_code})

"""
██████╗  █████╗ ██████╗ ██╗  ██╗    ██╗      █████╗ ██╗   ██╗███╗   ██╗ ██████╗██╗  ██╗███████╗██████╗
██╔══██╗██╔══██╗██╔══██╗╚██╗██╔╝    ██║     ██╔══██╗██║   ██║████╗  ██║██╔════╝██║  ██║██╔════╝██╔══██╗
██║  ██║███████║██████╔╝ ╚███╔╝     ██║     ███████║██║   ██║██╔██╗ ██║██║     ███████║█████╗  ██████╔╝
██║  ██║██╔══██║██╔══██╗ ██╔██╗     ██║     ██╔══██║██║   ██║██║╚██╗██║██║     ██╔══██║██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║  ██║██╔╝ ██╗    ███████╗██║  ██║╚██████╔╝██║ ╚████║╚██████╗██║  ██║███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                    The Ultimate Free Minecraft Launcher  v5.1
        Java Edition · Bedrock Edition · Forge · Fabric · Quilt · NeoForge
        Live Modrinth Mod Browser · Skin Editor · Modpacks · Settings · Light Mode

  Build to EXE:
    py -3.12 -m PyInstaller --onefile --windowed --name "DarxLauncher" DarxLauncher.py

  NEW in v5.0:
    • Black/Gray/White theme (dark) + Light Mode toggle
    • Skin Customization tab — upload OR draw skins with pixel brush + live 3D preview
    • Settings: per-instance RAM, close-to-tray, language, theme, game resolution,
                JVM args, auto-update, Discord RPC toggle, screenshot folder
    • Mods tab: unlimited pagination (Page 1/2/3…) — no 50-mod cap
    • Modpack builder — generate a shareable code; friends import with that code
    • Install mods directly — no popup dialog required

  NEW in v5.1:
    • Real Microsoft OAuth 2.0 Device Code Flow (no fake auth)
    • Xbox Live → XSTS → Minecraft Services full auth chain
    • Silent token refresh on launch (no re-login needed)
    • user_type=msa for online-mode server compatibility
    • Token + refresh_token persisted to auth.json
    • Offline/cracked mode still available as fallback
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import threading, os, json, shutil, subprocess, platform, datetime, time, hashlib, random, string, base64
import urllib.request, urllib.error, urllib.parse
import webbrowser
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
#  PATHS & URLS
# ══════════════════════════════════════════════════════════════════════════════
VERSION      = "5.1.0"
GITHUB_REPO  = "darxifyied/Darx-Launcher"
LAUNCHER_DIR = Path.home() / ".darxlauncher"
INSTANCES    = LAUNCHER_DIR / "instances"
ASSETS_DIR   = LAUNCHER_DIR / "assets"
LIBS_DIR     = LAUNCHER_DIR / "libraries"
VERSIONS_DIR = LAUNCHER_DIR / "versions"
SKINS_DIR    = LAUNCHER_DIR / "skins"
MODPACKS_DIR = LAUNCHER_DIR / "modpacks"

MC_VERSIONS_URL   = "https://launchermeta.mojang.com/mc/game/version_manifest_v2.json"
FABRIC_META_URL   = "https://meta.fabricmc.net/v2"
QUILT_META_URL    = "https://meta.quiltmc.org/v3"
FORGE_PROMO_URL   = "https://files.minecraftforge.net/net/minecraftforge/forge/promotions_slim.json"
NEOFORGE_META_URL = "https://maven.neoforged.net/releases/net/neoforged/neoforge/maven-metadata.xml"
MODRINTH_API      = "https://api.modrinth.com/v2"

AUTH_FILE      = LAUNCHER_DIR / "auth.json"
FIRST_RUN_FILE = LAUNCHER_DIR / ".first_run_done"

CONTENT_FOLDERS = {
    "mod":          "mods",
    "resourcepack": "resourcepacks",
    "shader":       "shaderpacks",
    "datapack":     "datapacks",
}
TYPE_ICONS  = {"mod":"🔧","resourcepack":"🎨","shader":"✨","datapack":"📦"}
TYPE_LABELS = {"mod":"Mod","resourcepack":"Resource Pack","shader":"Shader","datapack":"Data Pack"}

QUICK_CATS = [
    ("🔥 Trending",        "",              None),
    ("⚡ Performance",     "performance",   "optimization"),
    ("🌍 World Gen",       "world gen",     "world-generation"),
    ("🧙 Magic",           "magic",         "magic"),
    ("⚙ Tech / Machines",  "technology",    "technology"),
    ("🗺 Adventure",       "adventure",     "adventure"),
    ("🍖 Food / Farming",  "food farming",  "food"),
    ("🛡 RPG / Combat",    "rpg combat",    "combat"),
    ("🏠 Decoration",      "decoration",    "decoration"),
    ("🗃 Storage",         "storage",       "storage"),
    ("🔦 Utility",         "utility",       "utility"),
    ("🤝 Multiplayer",     "multiplayer",   "multiplayer-focused"),
    ("🗓 Quests",          "quests",        "quests"),
    ("📷 Minimap / HUD",   "minimap hud",   None),
    ("🌙 Dimensions",      "dimensions",    "dimensions"),
    ("🧰 Library / API",   "library api",   "library"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  THEME SYSTEM  (Dark = Black/Gray/White, Light Mode)
# ══════════════════════════════════════════════════════════════════════════════
DARK_THEME = {
    "bg":"#111111","bg2":"#1a1a1a","bg3":"#222222",
    "panel":"#1e1e1e","panel2":"#252525",
    "border":"#333333","border2":"#444444",
    "accent":"#888888","accent2":"#666666","accent3":"#555555",
    "green":"#5a9e6f","red":"#c0392b","yellow":"#c8a82b",
    "blue":"#4a7fb5","orange":"#b5703a","teal":"#3a9e8e",
    "bedrock":"#7ab8c8","java":"#aaaaaa",
    "text":"#f0f0f0","subtext":"#aaaaaa","muted":"#555555",
    "white":"#ffffff","selected":"#2a2a2a",
    "skin_bg":"#1a1a1a",
}
LIGHT_THEME = {
    "bg":"#f0f0f0","bg2":"#e0e0e0","bg3":"#d4d4d4",
    "panel":"#e8e8e8","panel2":"#dcdcdc",
    "border":"#bbbbbb","border2":"#999999",
    "accent":"#444444","accent2":"#333333","accent3":"#222222",
    "green":"#2e7d47","red":"#b02020","yellow":"#a07a10",
    "blue":"#2a5fa0","orange":"#a05020","teal":"#207870",
    "bedrock":"#3a8a9e","java":"#555555",
    "text":"#111111","subtext":"#444444","muted":"#888888",
    "white":"#000000","selected":"#c8c8c8",
    "skin_bg":"#cccccc",
}

C = dict(DARK_THEME)

F   = ("Segoe UI", 10)
FB  = ("Segoe UI", 10, "bold")
FS  = ("Segoe UI",  9)
FL  = ("Segoe UI", 13, "bold")
FXL = ("Segoe UI", 17, "bold")
FM  = ("Consolas",  9)

KNOWN_VERSIONS = [
    "1.21.4","1.21.3","1.21.2","1.21.1","1.21",
    "1.20.6","1.20.4","1.20.2","1.20.1","1.20",
    "1.19.4","1.19.3","1.19.2","1.19.1","1.19",
    "1.18.2","1.18.1","1.18","1.17.1","1.17",
    "1.16.5","1.16.4","1.16.3","1.16.2","1.16.1","1.16",
    "1.15.2","1.15.1","1.15","1.14.4","1.14.3","1.14.2","1.14.1","1.14",
    "1.13.2","1.13.1","1.13","1.12.2","1.12.1","1.12",
    "1.11.2","1.11","1.10.2","1.10","1.9.4","1.9","1.8.9","1.8","1.7.10",
]
MODLOADERS = ["Vanilla","Fabric","Forge","Quilt","NeoForge"]
ML_COLORS  = {
    "Vanilla": "#555555","Fabric":"#888888",
    "Forge":"#777777","Quilt":"#666666","NeoForge":"#999999",
}

MODS_PER_PAGE = 50


# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS  (persisted to disk)
# ══════════════════════════════════════════════════════════════════════════════
SETTINGS_FILE = LAUNCHER_DIR / "settings.json"

DEFAULT_SETTINGS = {
    "theme": "dark",
    "account_username": "",
    "account_uuid": "",
    "account_token": "",
    "account_refresh": "",
    "account_expiry": 0,
    "default_ram": 2,
    "close_to_tray": False,
    "show_snapshots": False,
    "game_width": 854,
    "game_height": 480,
    "fullscreen": False,
    "jvm_args": "",
    "auto_update": True,
    "discord_rpc": False,
    "screenshot_folder": "",
    "language": "English",
}

def load_settings():
    try:
        if SETTINGS_FILE.exists():
            d = json.loads(SETTINGS_FILE.read_text())
            out = dict(DEFAULT_SETTINGS)
            out.update(d)
            return out
    except Exception: pass
    return dict(DEFAULT_SETTINGS)

def save_settings(d):
    try:
        LAUNCHER_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_FILE.write_text(json.dumps(d, indent=2))
    except Exception: pass


# ══════════════════════════════════════════════════════════════════════════════
#  MICROSOFT AUTH  —  Blueprint-compliant Device Code OAuth
#  Following the ChatGPT/production blueprint exactly:
#    start_device_code_flow → poll_for_microsoft_token → authenticate_xbox
#    → authorize_xsts → authenticate_minecraft → get_minecraft_profile
#    → full_login_flow → refresh_token_if_needed → save auth.json
# ══════════════════════════════════════════════════════════════════════════════

# ── Standalone auth functions (blueprint §3) ──────────────────────────────────

def _http_post_form(url, data, timeout=30):
    body = urllib.parse.urlencode(data).encode()
    req  = urllib.request.Request(url, data=body,
           headers={"Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def _http_post_json(url, payload, timeout=30):
    body = json.dumps(payload).encode()
    req  = urllib.request.Request(url, data=body,
           headers={"Content-Type": "application/json", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def _http_get_json(url, bearer_token, timeout=30):
    req = urllib.request.Request(url,
          headers={"Authorization": f"Bearer {bearer_token}",
                   "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

# Blueprint §3 — Function: start_device_code_flow()
def start_device_code_flow():
    """
    POST to login.live.com device code endpoint (Live SDK).
    client_id 00000000402b5328 is a Live SDK app — must use live.com, NOT microsoftonline.com.
    Returns full response dict with user_code, device_code, verification_uri, interval.
    """
    return _http_post_form(
        "https://login.live.com/oauth20_connect.srf",
        {"client_id":     "00000000402b5328",
         "scope":         "service::user.auth.xboxlive.com::MBI_SSL",
         "response_type": "device_code"})

# Blueprint §3 — Function: poll_for_microsoft_token(device_code)
def poll_for_microsoft_token(device_code, interval=5, stop_event=None):
    """
    Poll token endpoint until user completes sign-in.
    Returns dict with access_token, refresh_token, expires_in.
    Raises RuntimeError or TimeoutError on failure.
    """
    deadline = time.time() + 900  # 15 min max
    while time.time() < deadline:
        if stop_event and stop_event.is_set():
            raise RuntimeError("Cancelled by user.")
        time.sleep(max(interval, 5))
        try:
            resp = _http_post_form(
                "https://login.live.com/oauth20_token.srf",
                {"client_id":   "00000000402b5328",
                 "grant_type":  "urn:ietf:params:oauth:grant-type:device_code",
                 "device_code": device_code})
            if "access_token" in resp:
                return resp
        except urllib.error.HTTPError as e:
            body = json.loads(e.read())
            err  = body.get("error", "")
            if err == "authorization_pending": continue
            if err == "slow_down":            interval = min(interval + 5, 30); continue
            if err == "authorization_declined": raise RuntimeError("Sign-in declined.")
            if err in ("expired_token", "bad_verification_code"):
                raise TimeoutError("Code expired — please try again.")
            raise RuntimeError(f"{err}: {body.get('error_description','')}")
    raise TimeoutError("Sign-in timed out.")

# Blueprint §3 — Function: authenticate_xbox(ms_token)
def authenticate_xbox(ms_access_token):
    """Exchange MSA access_token for Xbox Live token. Returns {xbox_token, uhs}."""
    resp = _http_post_json(
        "https://user.auth.xboxlive.com/user/authenticate",
        {"Properties": {
             "AuthMethod": "RPS",
             "SiteName":   "user.auth.xboxlive.com",
             "RpsTicket":  ms_access_token,   # Live SDK tokens: NO "d=" prefix
         },
         "RelyingParty": "http://auth.xboxlive.com",
         "TokenType":    "JWT"})
    return {
        "xbox_token": resp["Token"],
        "uhs":        resp["DisplayClaims"]["xui"][0]["uhs"],
    }

# Blueprint §3 — Function: authorize_xsts(xbox_token)
def authorize_xsts(xbox_token):
    """Exchange XBL token for XSTS token. Returns xsts_token string."""
    try:
        resp = _http_post_json(
            "https://xsts.auth.xboxlive.com/xsts/authorize",
            {"Properties": {
                 "SandboxId":  "RETAIL",
                 "UserTokens": [xbox_token],
             },
             "RelyingParty": "rp://api.minecraftservices.com/",
             "TokenType":    "JWT"})
        return resp["Token"]
    except urllib.error.HTTPError as e:
        body = json.loads(e.read())
        xerr = body.get("XErr", 0)
        msgs = {
            2148916233: "No Xbox profile — create one at xbox.com first.",
            2148916235: "Xbox Live unavailable in your region.",
            2148916236: "Adult verification required.",
            2148916238: "Child account — add to Microsoft Family Group first.",
        }
        raise RuntimeError(msgs.get(xerr, f"XSTS error XErr={xerr}"))

# Blueprint §3 — Function: authenticate_minecraft(uhs, xsts_token)
def authenticate_minecraft(uhs, xsts_token):
    """Exchange XSTS token for Minecraft access token. Returns mc_access_token string."""
    resp = _http_post_json(
        "https://api.minecraftservices.com/authentication/login_with_xbox",
        {"identityToken": f"XBL3.0 x={uhs};{xsts_token}"})
    return resp["access_token"]

# Blueprint §3 — Function: get_minecraft_profile(mc_token)
def get_minecraft_profile(mc_token):
    """GET Minecraft profile. Returns {uuid, username}."""
    try:
        resp = _http_get_json(
            "https://api.minecraftservices.com/minecraft/profile", mc_token)
        raw = resp.get("id", "")
        uuid_fmt = (f"{raw[:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}-{raw[20:]}"
                    if len(raw) == 32 else raw)
        return {"uuid": uuid_fmt, "username": resp.get("name", "")}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise RuntimeError(
                "This Microsoft account does not own Minecraft Java Edition. "
                "Purchase it at minecraft.net.")
        raise

# Blueprint §3 — Function: full_login_flow()
def full_login_flow(progress_cb=None, stop_event=None):
    """
    Complete auth chain: device_code → ms_token → xbox → xsts → minecraft → profile.
    progress_cb(step: int, total: int, message: str) — optional.
    Returns the saved auth dict.
    """
    def _p(s, msg):
        if progress_cb: progress_cb(s, 7, msg)

    _p(1, "Requesting device code…")
    dc_resp = start_device_code_flow()
    yield dc_resp                          # caller shows user_code / verification_uri

    _p(2, "Waiting for Microsoft sign-in…")
    ms_tok = poll_for_microsoft_token(
        dc_resp["device_code"],
        interval   = dc_resp.get("interval", 5),
        stop_event = stop_event)

    _p(3, "Authenticating with Xbox Live…")
    xbl = authenticate_xbox(ms_tok["access_token"])

    _p(4, "Authorizing XSTS…")
    xsts_token = authorize_xsts(xbl["xbox_token"])

    _p(5, "Logging into Minecraft…")
    mc_token = authenticate_minecraft(xbl["uhs"], xsts_token)

    _p(6, "Fetching Minecraft profile…")
    profile = get_minecraft_profile(mc_token)

    _p(7, "Saving session…")
    auth_data = {
        "access_token":  ms_tok["access_token"],
        "refresh_token": ms_tok.get("refresh_token", ""),
        "uuid":          profile["uuid"],
        "username":      profile["username"],
        "mc_token":      mc_token,
        "expires_at":    int(time.time()) + ms_tok.get("expires_in", 86400),
        "source":        "microsoft_oauth",
    }
    _save_auth(auth_data)
    yield auth_data

# Blueprint §3 — Function: refresh_token_if_needed()
def refresh_token_if_needed():
    """
    Silently refresh if token is expired. Called before every game launch.
    Updates auth.json in place. Returns current auth dict (refreshed or original).
    """
    auth = _load_auth()
    if not auth:
        return None
    if time.time() < auth.get("expires_at", 0) - 60:
        return auth   # still valid
    refresh_tok = auth.get("refresh_token", "")
    if not refresh_tok:
        return auth   # offline/cracked — no refresh needed
    try:
        ms_tok = _http_post_form(
            "https://login.live.com/oauth20_token.srf",
            {"client_id":     "00000000402b5328",
             "grant_type":    "refresh_token",
             "refresh_token": refresh_tok,
             "scope":         "service::user.auth.xboxlive.com::MBI_SSL"})
        xbl        = authenticate_xbox(ms_tok["access_token"])
        xsts_token = authorize_xsts(xbl["xbox_token"])
        mc_token   = authenticate_minecraft(xbl["uhs"], xsts_token)
        profile    = get_minecraft_profile(mc_token)
        auth.update({
            "access_token":  ms_tok["access_token"],
            "refresh_token": ms_tok.get("refresh_token", refresh_tok),
            "mc_token":      mc_token,
            "uuid":          profile["uuid"],
            "username":      profile["username"],
            "expires_at":    int(time.time()) + ms_tok.get("expires_in", 86400),
        })
        _save_auth(auth)
        return auth
    except Exception as e:
        print(f"[Auth] Silent refresh failed: {e}")
        return auth   # return stale — launcher will still try

def _save_auth(data):
    try:
        LAUNCHER_DIR.mkdir(parents=True, exist_ok=True)
        AUTH_FILE.write_text(json.dumps(data, indent=2))
    except Exception as e:
        print(f"[Auth] Save error: {e}")

def _load_auth():
    try:
        if AUTH_FILE.exists():
            return json.loads(AUTH_FILE.read_text())
    except Exception:
        pass
    return None

def _clear_auth():
    try:
        if AUTH_FILE.exists():
            AUTH_FILE.unlink()
    except Exception:
        pass

def _offline_uuid(username):
    data = ("OfflinePlayer:" + username).encode()
    h  = hashlib.md5(data).digest()
    ba = bytearray(h)
    ba[6] = (ba[6] & 0x0F) | 0x30
    ba[8] = (ba[8] & 0x3F) | 0x80
    hx = ba.hex()
    return f"{hx[:8]}-{hx[8:12]}-{hx[12:16]}-{hx[16:20]}-{hx[20:]}"

# ── Auth field normalizer (handles old schema → new blueprint schema) ────────
def _normalize_auth(auth):
    """Ensure auth dict always has blueprint field names regardless of how it was saved."""
    if not auth:
        return auth
    # Map old field names to blueprint names
    if "expiry" in auth and "expires_at" not in auth:
        auth["expires_at"] = auth["expiry"]
    if "mc_token" not in auth and "access_token" in auth:
        # mc_token is the Minecraft token; access_token is the MSA token
        # if only one exists, use it as mc_token
        auth["mc_token"] = auth.get("mc_token", "0")
    return auth

# ── MicrosoftAuth class (shim — delegates to standalone functions above) ──────
# Kept so the rest of the launcher code that calls self.msa.* still works.
class MicrosoftAuth:
    """Thin wrapper so existing self.msa.* calls route to the standalone functions."""

    def request_device_code(self):       return start_device_code_flow()
    def poll_token(self, device_code, interval=5, stop_event=None):
        return poll_for_microsoft_token(device_code, interval, stop_event)
    def xbl_auth(self, token):           return authenticate_xbox(token)
    def xsts_auth(self, xbl_token):
        return {"Token": authorize_xsts(xbl_token)}
    def mc_auth(self, xsts_token, uhs):  return authenticate_minecraft(uhs, xsts_token)
    def mc_profile(self, mc_token):
        p = get_minecraft_profile(mc_token)
        return {"name": p["username"], "id": p["uuid"].replace("-","")}
    def refresh_msa_token(self, _rt):    return refresh_token_if_needed()
    def load_saved(self):                return _load_auth()
    def _persist(self, data):            _save_auth(data)
    def save(self, username, uuid, email, mc_token):
        data = {"username": username, "uuid": uuid, "email": email,
                "mc_token": mc_token, "refresh_token": "", "access_token": "",
                "expires_at": int(time.time()) + 86400*30, "source": "offline"}
        _save_auth(data); return data
    def clear(self):                     _clear_auth()
    def is_expired(self, saved):
        saved = _normalize_auth(saved) or {}
        return time.time() >= saved.get("expires_at", saved.get("expiry", 0))
    def is_microsoft_account(self, saved):
        return saved.get("source") == "microsoft_oauth"
    @staticmethod
    def _gen_offline_uuid(username):     return _offline_uuid(username)


# ══════════════════════════════════════════════════════════════════════════════
#  MODPACK MANAGER
# ══════════════════════════════════════════════════════════════════════════════
class ModpackManager:
    def __init__(self):
        MODPACKS_DIR.mkdir(parents=True, exist_ok=True)

    def _gen_code(self):
        return "DX-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

    def create_modpack(self, name, description, instance_path, mods_list):
        code = self._gen_code()
        data = {
            "name": name,
            "description": description,
            "code": code,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mods": mods_list,
        }
        pack_file = MODPACKS_DIR / f"{code}.json"
        pack_file.write_text(json.dumps(data, indent=2))
        return code, data

    def import_modpack(self, code):
        code = code.strip().upper()
        pack_file = MODPACKS_DIR / f"{code}.json"
        if pack_file.exists():
            try: return json.loads(pack_file.read_text())
            except Exception: pass
        return None

    def get_all(self):
        out = []
        for f in sorted(MODPACKS_DIR.glob("*.json")):
            try: out.append(json.loads(f.read_text()))
            except Exception: pass
        return out

    def get_mods_from_instance(self, instance_path):
        mods_folder = Path(instance_path) / "mods"
        if not mods_folder.exists(): return []
        return [f.name for f in mods_folder.iterdir() if f.suffix in (".jar", ".zip")]


# ══════════════════════════════════════════════════════════════════════════════
#  SKIN MANAGER
# ══════════════════════════════════════════════════════════════════════════════
class SkinManager:
    def __init__(self):
        SKINS_DIR.mkdir(parents=True, exist_ok=True)

    def get_all(self):
        out = []
        for f in sorted(SKINS_DIR.glob("*.json")):
            try: out.append(json.loads(f.read_text()))
            except Exception: pass
        return out

    def save_skin(self, name, pixel_data, source="drawn"):
        safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
        meta = {
            "name": name,
            "safe": safe,
            "source": source,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "pixels": pixel_data,
        }
        (SKINS_DIR / f"{safe}.json").write_text(json.dumps(meta, indent=2))
        return meta

    def delete_skin(self, safe):
        f = SKINS_DIR / f"{safe}.json"
        if f.exists(): f.unlink()


# ══════════════════════════════════════════════════════════════════════════════
#  INSTANCE MANAGER
# ══════════════════════════════════════════════════════════════════════════════
class InstanceManager:
    def __init__(self):
        INSTANCES.mkdir(parents=True, exist_ok=True)

    def get_all(self):
        out = []
        if not INSTANCES.exists(): return out
        for d in sorted(INSTANCES.iterdir()):
            if d.is_dir():
                cfg = d / "instance.json"
                if cfg.exists():
                    try:
                        data = json.loads(cfg.read_text())
                        data["path"] = str(d)
                        out.append(data)
                    except Exception: pass
        return out

    def create(self, name, version, modloader, ram=2, icon="🎮", edition="Java"):
        safe  = "".join(c if c.isalnum() or c in " _-" else "_" for c in name).strip()
        safe  = safe.replace(" ", "_") or "instance"
        ipath = INSTANCES / safe
        ipath.mkdir(parents=True, exist_ok=True)
        for sub in ["mods","resourcepacks","shaderpacks","datapacks","screenshots","saves","config"]:
            (ipath / sub).mkdir(exist_ok=True)
        cfg = {
            "name": name, "version": version, "modloader": modloader,
            "ram": ram, "edition": edition,
            "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_played": None, "play_time": 0, "icon": icon, "loader_ver": ""
        }
        (ipath / "instance.json").write_text(json.dumps(cfg, indent=2))
        return ipath

    def delete(self, path):
        try: shutil.rmtree(path); return True
        except Exception: return False

    def update_cfg(self, path, key, value):
        p = Path(path) / "instance.json"
        try:
            cfg = json.loads(p.read_text())
            cfg[key] = value
            p.write_text(json.dumps(cfg, indent=2))
        except Exception: pass

    def get_folder(self, instance_path, folder_name):
        p = Path(instance_path) / folder_name
        p.mkdir(parents=True, exist_ok=True)
        return p


# ══════════════════════════════════════════════════════════════════════════════
#  DOWNLOADER
# ══════════════════════════════════════════════════════════════════════════════
class Downloader:
    H = {"User-Agent": "DarxLauncher/5.0"}

    def download(self, url, dest: Path, progress_cb=None):
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            req = urllib.request.Request(url, headers=self.H)
            with urllib.request.urlopen(req, timeout=60) as r:
                total = int(r.headers.get("Content-Length", 0))
                done  = 0
                with open(dest, "wb") as f:
                    while True:
                        chunk = r.read(65536)
                        if not chunk: break
                        f.write(chunk); done += len(chunk)
                        if progress_cb and total:
                            progress_cb(done / total * 100)
            return True
        except Exception as e:
            print(f"[DL] {e}"); return False

    def fetch_json(self, url):
        try:
            req = urllib.request.Request(url, headers=self.H)
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.loads(r.read())
        except Exception as e:
            print(f"[JSON] {e}"); return None

    def fetch_text(self, url):
        try:
            req = urllib.request.Request(url, headers=self.H)
            with urllib.request.urlopen(req, timeout=15) as r:
                return r.read().decode("utf-8")
        except Exception: return None

    def search_modrinth(self, query="", project_type="mod", limit=50,
                        offset=0, version=None, loader=None, category=None):
        facets = [[f"project_type:{project_type}"]]
        if version:  facets.append([f"versions:{version}"])
        if loader and loader.lower() not in ("vanilla","any","all",""):
            facets.append([f"categories:{loader.lower()}"])
        if category: facets.append([f"categories:{category}"])
        params = {
            "query":  query,
            "limit":  limit,
            "offset": offset,
            "index":  "downloads" if not query else "relevance",
            "facets": json.dumps(facets),
        }
        return self.fetch_json(f"{MODRINTH_API}/search?" +
                               urllib.parse.urlencode(params)) or {"hits": [], "total_hits": 0}

    def get_all_versions(self, slug):
        return self.fetch_json(f"{MODRINTH_API}/project/{slug}/version") or []

    def get_compatible_version(self, slug, game_version, loader):
        url    = f"{MODRINTH_API}/project/{slug}/version"
        params = {}
        if game_version: params["game_versions"] = json.dumps([game_version])
        if loader and loader.lower() not in ("vanilla","any","all",""):
            params["loaders"] = json.dumps([loader.lower()])
        if params: url += "?" + urllib.parse.urlencode(params)
        return self.fetch_json(url) or []

    def fetch_mc_versions(self):
        data = self.fetch_json(MC_VERSIONS_URL)
        return [v["id"] for v in data["versions"] if v["type"] == "release"] if data else KNOWN_VERSIONS

    def fetch_fabric_loaders(self, mc):
        data = self.fetch_json(f"{FABRIC_META_URL}/versions/loader/{mc}")
        return [d["loader"]["version"] for d in (data or [])[:8]] or ["0.16.5","0.15.11"]

    def get_fabric_profile(self, mc, lv):
        return self.fetch_json(f"{FABRIC_META_URL}/versions/loader/{mc}/{lv}/profile/json")

    def fetch_quilt_loaders(self, mc):
        data = self.fetch_json(f"{QUILT_META_URL}/versions/loader/{mc}")
        return [d["loader"]["version"] for d in (data or [])[:8]] or ["0.26.3"]

    def get_quilt_profile(self, mc, lv):
        return self.fetch_json(f"{QUILT_META_URL}/versions/loader/{mc}/{lv}/profile/json")

    def fetch_forge_versions(self, mc):
        data = self.fetch_json(FORGE_PROMO_URL)
        out  = []
        if data and "promos" in data:
            for k in [f"{mc}-recommended", f"{mc}-latest"]:
                if k in data["promos"] and data["promos"][k] not in out:
                    out.append(data["promos"][k])
        return out

    def forge_installer_url(self, mc, fv):
        s = f"{mc}-{fv}"
        return (f"https://maven.minecraftforge.net/net/minecraftforge/forge/"
                f"{s}/forge-{s}-installer.jar")

    def fetch_neoforge_versions(self, mc):
        import re
        xml = self.fetch_text(NEOFORGE_META_URL)
        if not xml: return []
        parts  = mc.split(".")
        prefix = ".".join(parts[1:]) if len(parts) >= 2 else mc
        vers   = [m.group(1) for m in re.finditer(r"<version>([^<]+)</version>", xml)
                  if m.group(1).startswith(prefix + ".")]
        return list(reversed(vers))[:8]

    def detect_bedrock(self):
        if platform.system() != "Windows": return False
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "Get-AppxPackage -Name Microsoft.MinecraftUWP | Select-Object Name"],
                capture_output=True, text=True, timeout=8)
            return "MinecraftUWP" in (result.stdout or "")
        except Exception: return False

    def detect_java_mc(self):
        paths = [Path.home() / "AppData/Roaming/.minecraft", Path.home() / ".minecraft"]
        return any(p.exists() for p in paths)


# ══════════════════════════════════════════════════════════════════════════════
#  MODLOADER INSTALLER
# ══════════════════════════════════════════════════════════════════════════════
class ModloaderInstaller:
    def __init__(self, dl, log_cb=None, prog_cb=None):
        self.dl   = dl
        self.log  = log_cb  or print
        self.prog = prog_cb or (lambda v: None)

    def install_fabric(self, mc, lv, ipath):
        self.log(f"Fetching Fabric {lv} for {mc}…")
        profile = self.dl.get_fabric_profile(mc, lv)
        if not profile: return False, "Could not fetch Fabric profile."
        pid = profile.get("id", f"fabric-loader-{lv}-{mc}")
        d   = VERSIONS_DIR / pid; d.mkdir(parents=True, exist_ok=True)
        (d / f"{pid}.json").write_text(json.dumps(profile, indent=2))
        self._dl_libs(profile); self.prog(100)
        return True, pid

    def install_quilt(self, mc, lv, ipath):
        self.log(f"Fetching Quilt {lv} for {mc}…")
        profile = self.dl.get_quilt_profile(mc, lv)
        if not profile: return False, "Could not fetch Quilt profile."
        pid = profile.get("id", f"quilt-loader-{lv}-{mc}")
        d   = VERSIONS_DIR / pid; d.mkdir(parents=True, exist_ok=True)
        (d / f"{pid}.json").write_text(json.dumps(profile, indent=2))
        self._dl_libs(profile); self.prog(100)
        return True, pid

    def install_forge(self, mc, fv, java, ipath):
        self.log("Downloading Forge installer…")
        url  = self.dl.forge_installer_url(mc, fv)
        dest = LAUNCHER_DIR / "forge_installers" / f"forge-{mc}-{fv}-installer.jar"
        dest.parent.mkdir(parents=True, exist_ok=True)
        self.prog(5)
        if not self.dl.download(url, dest, lambda p: self.prog(5 + p * 0.55)):
            return False, f"Download failed.\nURL: {url}"
        self.prog(60); self.log("Running Forge installer…")
        try:
            j    = java or shutil.which("java") or "java"
            proc = subprocess.run([j, "-jar", str(dest), "--installClient", str(LAUNCHER_DIR)],
                                  capture_output=True, text=True, timeout=300)
            self.prog(95)
            if proc.returncode == 0:
                self.prog(100); return True, f"{mc}-forge-{fv}"
            return False, f"Installer failed:\n{(proc.stderr or '')[-400:]}"
        except subprocess.TimeoutExpired: return False, "Timed out."
        except Exception as e:            return False, str(e)

    def install_neoforge(self, mc, nv, java, ipath):
        self.log("Downloading NeoForge installer…")
        url  = (f"https://maven.neoforged.net/releases/net/neoforged/neoforge/"
                f"{nv}/neoforge-{nv}-installer.jar")
        dest = LAUNCHER_DIR / "neoforge_installers" / f"neoforge-{nv}-installer.jar"
        dest.parent.mkdir(parents=True, exist_ok=True)
        self.prog(5)
        if not self.dl.download(url, dest, lambda p: self.prog(5 + p * 0.55)):
            return False, "Download failed."
        self.prog(60); self.log("Running NeoForge installer…")
        try:
            j    = java or shutil.which("java") or "java"
            proc = subprocess.run([j, "-jar", str(dest), "--installClient", str(LAUNCHER_DIR)],
                                  capture_output=True, text=True, timeout=300)
            self.prog(95)
            if proc.returncode == 0:
                self.prog(100); return True, f"neoforge-{nv}"
            return False, f"Installer failed:\n{(proc.stderr or '')[-400:]}"
        except Exception as e: return False, str(e)

    def _dl_libs(self, profile):
        for lib in profile.get("libraries", []):
            url  = lib.get("url", ""); name = lib.get("name", "")
            if not url or not name: continue
            parts = name.split(":")
            if len(parts) < 3: continue
            g, a, v = parts[0], parts[1], parts[2]
            gp  = g.replace(".", "/"); jn = f"{a}-{v}.jar"
            dest = LIBS_DIR / gp / a / v / jn
            if not dest.exists():
                self.dl.download(f"{url}{gp}/{a}/{v}/{jn}", dest)


# ══════════════════════════════════════════════════════════════════════════════
#  SKIN EDITOR WIDGET
# ══════════════════════════════════════════════════════════════════════════════
# Minecraft skin is 64×64 pixels. We'll edit 8×8 face + 8×8 body regions as simplified view.
# Full 64×64 grid with 6px cells = 384×384 canvas
SKIN_W, SKIN_H = 64, 64
CELL = 6  # pixels per skin pixel in editor (default zoom)

# Body part region definitions: (name, sx, sy, w, h, display_ox, display_oy)
SKIN_REGIONS = {
    "Head":      {"sx": 8,  "sy": 8,  "w": 8,  "h": 8,  "ox": 32,  "oy": 4},
    "Body":      {"sx": 20, "sy": 20, "w": 8,  "h": 12, "ox": 32,  "oy": 68},
    "Right Arm": {"sx": 44, "sy": 20, "w": 4,  "h": 12, "ox": 0,   "oy": 68},
    "Left Arm":  {"sx": 36, "sy": 52, "w": 4,  "h": 12, "ox": 96,  "oy": 68},
    "Right Leg": {"sx": 4,  "sy": 20, "w": 4,  "h": 12, "ox": 32,  "oy": 164},
    "Left Leg":  {"sx": 20, "sy": 52, "w": 4,  "h": 12, "ox": 64,  "oy": 164},
}

# Grid highlight colors per region
REGION_COLORS = {
    "Head":      "#cc3333",
    "Body":      "#33aa33",
    "Right Arm": "#3366cc",
    "Left Arm":  "#aa66cc",
    "Right Leg": "#aaaa22",
    "Left Leg":  "#22aaaa",
}

class SkinEditorWidget(tk.Frame):
    """Pixel art editor for Minecraft skins with live 2D/3D preview, zoom, and body-part isolation."""

    def __init__(self, parent, on_save, **kw):
        super().__init__(parent, **kw)
        self.on_save      = on_save
        self.brush_color  = "#cc6633"
        self.brush_size   = 1
        self.erasing      = False
        self.pixels       = {}  # (x,y) → "#rrggbb" or None
        self.zoom         = 6   # cell size in pixels
        self.active_parts = set(SKIN_REGIONS.keys())  # which parts are editable/shown
        self.invisible_mode = False
        self._part_vars      = {}
        self._part_hide_vars = {}
        self._pan_start      = None
        self._init_default_skin()
        self._build()

    def _init_default_skin(self):
        """Simple default skin colors."""
        for x in range(SKIN_W):
            for y in range(SKIN_H):
                self.pixels[(x, y)] = None  # transparent

        # Face area (8×8 at 8,8)
        face_color = "#c68642"
        for x in range(8, 16):
            for y in range(8, 16):
                self.pixels[(x, y)] = face_color
        # Eyes
        self.pixels[(9, 10)]  = "#333333"
        self.pixels[(10, 10)] = "#333333"
        self.pixels[(13, 10)] = "#333333"
        self.pixels[(14, 10)] = "#333333"
        # Body (4×12 at 20,20)
        body_color = "#3a6bbf"
        for x in range(20, 28):
            for y in range(20, 32):
                self.pixels[(x, y)] = body_color
        # Legs
        leg_color = "#2244aa"
        for x in range(4, 8):
            for y in range(20, 32):
                self.pixels[(x, y)] = leg_color
        for x in range(20, 24):
            for y in range(20, 32):
                self.pixels[(x, y)] = leg_color

    def _build(self):
        self.configure(bg=C["bg"])

        # ── Toolbar row 1: Color + Brush + Tools ─────────────────────────────
        tb = tk.Frame(self, bg=C["bg2"], padx=6, pady=4)
        tb.pack(fill="x")

        self.color_btn = tk.Button(tb, text="  🎨  ", bg=self.brush_color,
                                   relief="flat", width=4, cursor="hand2",
                                   command=self._pick_color)
        self.color_btn.pack(side="left", padx=3)

        tk.Label(tb, text="Brush:", font=FS, fg=C["text"], bg=C["bg2"]).pack(side="left", padx=(8,2))
        self.size_var = tk.IntVar(value=1)
        for sz in [1, 2, 3, 4]:
            tk.Radiobutton(tb, text=str(sz), variable=self.size_var, value=sz,
                           font=FS, fg=C["text"], bg=C["bg2"],
                           activebackground=C["bg2"], selectcolor=C["panel"],
                           relief="flat").pack(side="left", padx=2)

        self.erase_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tb, text="Eraser", variable=self.erase_var,
                       font=FS, fg=C["text"], bg=C["bg2"],
                       activebackground=C["bg2"], selectcolor=C["panel"]).pack(side="left", padx=8)

        # Zoom controls
        tk.Label(tb, text="  Zoom:", font=FS, fg=C["text"], bg=C["bg2"]).pack(side="left", padx=(8,2))
        self.zoom_var = tk.IntVar(value=self.zoom)
        zoom_scale = tk.Scale(tb, from_=1, to=40, orient="horizontal",
                              variable=self.zoom_var, length=120, showvalue=True,
                              bg=C["bg2"], fg=C["text"], troughcolor=C["bg3"],
                              highlightthickness=0, font=("Segoe UI", 7),
                              command=self._on_zoom_change)
        zoom_scale.pack(side="left", padx=2)
        tk.Button(tb, text="1:1", font=("Segoe UI", 7), bg=C["bg3"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  command=lambda: self.zoom_var.set(6)).pack(side="left", padx=2)

        tk.Button(tb, text="🗑 Clear All", font=FS, bg=C["bg3"], fg=C["text"],
                  relief="flat", cursor="hand2", command=self._clear_all).pack(side="left", padx=4)
        tk.Button(tb, text="📁 Load PNG", font=FS, bg=C["bg3"], fg=C["text"],
                  relief="flat", cursor="hand2", command=self._load_png).pack(side="left", padx=4)

        # Invisible avatar toggle
        self.invisible_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tb, text="👻 Invisible Avatar", variable=self.invisible_var,
                       font=FS, fg=C["yellow"], bg=C["bg2"],
                       activebackground=C["bg2"], selectcolor=C["panel"],
                       command=self._on_invisible_toggle).pack(side="left", padx=8)

        tk.Button(tb, text="💾 Save Skin", font=FS, bg=C["accent2"], fg=C["white"],
                  relief="flat", cursor="hand2", command=self._save_skin).pack(side="right", padx=4)

        # ── Toolbar row 2: Body Part Selector ────────────────────────────────
        tb2 = tk.Frame(self, bg=C["bg3"], padx=6, pady=3)
        tb2.pack(fill="x")
        tk.Label(tb2, text="✏ Edit:", font=FB, fg=C["subtext"], bg=C["bg3"]).pack(side="left", padx=(4,6))

        self._part_vars = {}       # controls which parts receive brush strokes
        self._part_hide_vars = {}  # controls which parts are visible in canvas
        for part_name in SKIN_REGIONS.keys():
            col = REGION_COLORS.get(part_name, C["accent"])
            pf = tk.Frame(tb2, bg=C["bg3"])
            pf.pack(side="left", padx=3)
            # Edit checkbox
            var = tk.BooleanVar(value=True)
            self._part_vars[part_name] = var
            cb = tk.Checkbutton(pf, text=part_name, variable=var,
                                font=("Segoe UI", 8), fg=col, bg=C["bg3"],
                                activebackground=C["bg3"], selectcolor=C["panel"],
                                command=self._on_part_toggle)
            cb.pack(anchor="w")
            # Hide toggle (eye icon)
            hide_var = tk.BooleanVar(value=False)  # False = visible
            self._part_hide_vars[part_name] = hide_var
            hcb = tk.Checkbutton(pf, text="hide", variable=hide_var,
                                 font=("Segoe UI", 7), fg=C["muted"], bg=C["bg3"],
                                 activebackground=C["bg3"], selectcolor=C["panel"],
                                 command=self._on_part_toggle)
            hcb.pack(anchor="w")

        sep = tk.Frame(tb2, bg=C["border2"], width=1)
        sep.pack(side="left", fill="y", padx=6)
        tk.Button(tb2, text="All", font=("Segoe UI", 8), bg=C["bg2"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  command=lambda: self._set_all_parts(True)).pack(side="left", padx=2)
        tk.Button(tb2, text="None", font=("Segoe UI", 8), bg=C["bg2"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  command=lambda: self._set_all_parts(False)).pack(side="left", padx=2)
        tk.Button(tb2, text="Show All", font=("Segoe UI", 8), bg=C["bg2"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  command=lambda: self._set_all_hidden(False)).pack(side="left", padx=2)

        tk.Label(tb2, text="  ✋ Right-click drag = Pan  |  Ctrl+Scroll = Zoom",
                 font=("Segoe UI", 7), fg=C["muted"], bg=C["bg3"]).pack(side="right", padx=8)

        # ── Main area: canvas + preview tabs ─────────────────────────────────
        area = tk.Frame(self, bg=C["bg"])
        area.pack(fill="both", expand=True, padx=4, pady=4)

        # Editor canvas (scrollable)
        editor_frame = tk.Frame(area, bg=C["bg"])
        editor_frame.pack(side="left", fill="both", expand=True)

        self._editor_label = tk.Label(editor_frame, text="Skin Editor (64×64) — All Parts",
                                      font=FB, fg=C["subtext"], bg=C["bg"])
        self._editor_label.pack(anchor="w", pady=(0, 2))

        cv_frame = tk.Frame(editor_frame, bg=C["bg"])
        cv_frame.pack(fill="both", expand=True)

        cv_w = SKIN_W * self.zoom
        cv_h = SKIN_H * self.zoom
        self.canvas = tk.Canvas(cv_frame, width=min(cv_w, 700), height=min(cv_h, 600),
                                bg=C["skin_bg"], cursor="crosshair",
                                highlightthickness=1, highlightbackground=C["border"])

        xsb = ttk.Scrollbar(cv_frame, orient="horizontal", command=self.canvas.xview)
        ysb = ttk.Scrollbar(cv_frame, orient="vertical",   command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=xsb.set, yscrollcommand=ysb.set,
                              scrollregion=(0, 0, cv_w, cv_h))
        xsb.pack(side="bottom", fill="x")
        ysb.pack(side="right",  fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind("<Button-1>",       self._on_click)
        self.canvas.bind("<B1-Motion>",      self._on_drag)
        self.canvas.bind("<Button-3>",       self._on_rclick)
        self.canvas.bind("<B3-Motion>",      self._on_rclick_drag)
        self.canvas.bind("<ButtonRelease-3>",self._on_rclick_release)
        # Ctrl+Scroll to zoom, plain scroll to scroll canvas
        self.canvas.bind("<Control-MouseWheel>", self._on_ctrl_scroll)
        self.canvas.bind("<MouseWheel>",     self._on_scroll)
        self.canvas.bind("<Control-Button-4>",   lambda e: self._zoom_step(2))
        self.canvas.bind("<Control-Button-5>",   lambda e: self._zoom_step(-2))
        self.canvas.bind("<Button-4>",       lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Button-5>",       lambda e: self.canvas.yview_scroll(1, "units"))

        # Pan state
        self._pan_start = None
        self._pan_scan_x = 0
        self._pan_scan_y = 0

        # ── Preview panel with 2D/3D tabs ─────────────────────────────────────
        prev_panel = tk.Frame(area, bg=C["panel"], width=230,
                              highlightthickness=1, highlightbackground=C["border"])
        prev_panel.pack(side="right", fill="y", padx=(8, 0))
        prev_panel.pack_propagate(False)

        tk.Label(prev_panel, text="Preview", font=FL,
                 fg=C["text"], bg=C["panel"]).pack(pady=(10, 2))

        # Tab bar for 2D/3D
        tab_bar = tk.Frame(prev_panel, bg=C["panel"])
        tab_bar.pack(fill="x", padx=8)
        self._preview_mode = tk.StringVar(value="2D")
        for mode in ("2D Front", "2D Back", "3D"):
            tk.Radiobutton(tab_bar, text=mode, variable=self._preview_mode, value=mode,
                           font=("Segoe UI", 8), fg=C["text"], bg=C["panel"],
                           activebackground=C["panel"], selectcolor=C["bg3"],
                           relief="flat", command=self._update_preview).pack(side="left", padx=4)

        self.prev_canvas = tk.Canvas(prev_panel, width=180, height=220,
                                     bg=C["skin_bg"], highlightthickness=0)
        self.prev_canvas.pack(pady=6, padx=8)

        # 3D rotation control
        rot_frame = tk.Frame(prev_panel, bg=C["panel"])
        rot_frame.pack(fill="x", padx=8)
        tk.Label(rot_frame, text="3D Rotate:", font=("Segoe UI", 8),
                 fg=C["subtext"], bg=C["panel"]).pack(side="left")
        self._rot_var = tk.IntVar(value=30)
        tk.Scale(rot_frame, from_=0, to=359, orient="horizontal",
                 variable=self._rot_var, length=120, showvalue=False,
                 bg=C["panel"], fg=C["text"], troughcolor=C["bg3"],
                 highlightthickness=0, font=("Segoe UI", 7),
                 command=lambda v: self._update_preview()).pack(side="left", padx=2)

        tk.Label(prev_panel, text="(Right-click = erase | Ctrl+Scroll = zoom)",
                 font=("Segoe UI", 7), fg=C["muted"], bg=C["panel"],
                 wraplength=190).pack(pady=(4,2))

        # Part legend
        tk.Frame(prev_panel, bg=C["border"], height=1).pack(fill="x", padx=8, pady=4)
        tk.Label(prev_panel, text="Body Parts:", font=FB,
                 fg=C["subtext"], bg=C["panel"]).pack(pady=(2, 2))
        for pname, col in REGION_COLORS.items():
            tk.Label(prev_panel, text=f"■ {pname}", font=("Segoe UI", 8),
                     fg=col, bg=C["panel"]).pack(anchor="w", padx=14)

        self._draw_grid()
        self._redraw_all()
        self._update_preview()

    # ── Body part / zoom / invisible helpers ──────────────────────────────────
    def _on_part_toggle(self):
        self.active_parts = {p for p, v in self._part_vars.items() if v.get()}
        active_list = ", ".join(self.active_parts) if self.active_parts else "None"
        self._editor_label.config(text=f"Skin Editor (64×64) — Editing: {active_list}")
        self._draw_grid()
        self._redraw_all()
        self._update_preview()

    def _set_all_parts(self, state: bool):
        for v in self._part_vars.values():
            v.set(state)
        self._on_part_toggle()

    def _set_all_hidden(self, hidden: bool):
        for v in self._part_hide_vars.values():
            v.set(hidden)
        self._on_part_toggle()

    def _is_hidden(self, part_name):
        hv = self._part_hide_vars.get(part_name)
        return hv.get() if hv else False

    def _on_invisible_toggle(self):
        self.invisible_mode = self.invisible_var.get()
        self._update_preview()

    def _on_zoom_change(self, val):
        self.zoom = int(val)
        cv_w = SKIN_W * self.zoom
        cv_h = SKIN_H * self.zoom
        self.canvas.configure(scrollregion=(0, 0, cv_w, cv_h))
        self.canvas.delete("all")
        self._draw_grid()
        self._redraw_all()

    def _on_rclick(self, event):
        """Right-click: start pan (move canvas view)."""
        self._pan_start = (event.x, event.y)
        self.canvas.scan_mark(event.x, event.y)
        self.canvas.config(cursor="fleur")

    def _on_rclick_drag(self, event):
        """Right-click drag: pan the canvas."""
        if self._pan_start:
            self.canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_rclick_release(self, event):
        """Right-click release: return to crosshair cursor."""
        self._pan_start = None
        self.canvas.config(cursor="crosshair")

    def _on_scroll(self, event):
        """Plain scroll: scroll canvas vertically."""
        if event.delta:
            self.canvas.yview_scroll(int(-event.delta / 120), "units")

    def _on_ctrl_scroll(self, event):
        if event.delta > 0:
            self._zoom_step(2)
        else:
            self._zoom_step(-2)

    def _zoom_step(self, delta):
        new_zoom = max(1, min(40, self.zoom + delta))
        self.zoom_var.set(new_zoom)
        self._on_zoom_change(new_zoom)

    def _pixel_in_active_region(self, x, y):
        """Return True if pixel (x,y) belongs to at least one active body part."""
        if not self.active_parts:
            return False
        for pname in self.active_parts:
            r = SKIN_REGIONS[pname]
            if r["sx"] <= x < r["sx"] + r["w"] and r["sy"] <= y < r["sy"] + r["h"]:
                return True
        return False

    # ── Color + painting ──────────────────────────────────────────────────────
    def _pick_color(self):
        col = colorchooser.askcolor(color=self.brush_color, title="Pick Brush Color")
        if col and col[1]:
            self.brush_color = col[1]
            self.color_btn.configure(bg=self.brush_color)

    def _canvas_to_pixel(self, event):
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        return int(cx // self.zoom), int(cy // self.zoom)

    def _on_click(self, event):
        self._paint(event, erase=self.erase_var.get())

    def _on_drag(self, event):
        self._paint(event, erase=self.erase_var.get())

    def _on_erase(self, event):
        self._paint(event, erase=True)

    def _paint(self, event, erase=False):
        px, py = self._canvas_to_pixel(event)
        sz = self.size_var.get()
        changed = False
        for dx in range(sz):
            for dy in range(sz):
                x, y = px + dx, py + dy
                if 0 <= x < SKIN_W and 0 <= y < SKIN_H:
                    # Only paint within active, non-hidden regions
                    if not self._pixel_in_active_region(x, y):
                        continue
                    # Skip hidden parts
                    skip = False
                    for pname in list(self.active_parts):
                        r = SKIN_REGIONS[pname]
                        if r["sx"] <= x < r["sx"] + r["w"] and r["sy"] <= y < r["sy"] + r["h"]:
                            if self._is_hidden(pname):
                                skip = True
                                break
                    if skip:
                        continue
                    old = self.pixels.get((x, y))
                    new = None if erase else self.brush_color
                    if old != new:
                        self.pixels[(x, y)] = new
                        self._paint_cell(x, y)
                        changed = True
        if changed:
            self._update_preview()

    def _paint_cell(self, x, y):
        z = self.zoom
        x0 = x * z; y0 = y * z
        x1 = x0 + z; y1 = y0 + z
        color = self.pixels.get((x, y))
        # Remove existing cell item
        for item in self.canvas.find_overlapping(x0+1, y0+1, x1-1, y1-1):
            tags = self.canvas.gettags(item)
            if "cell" in tags:
                self.canvas.delete(item)
        if color:
            self.canvas.create_rectangle(x0, y0, x1, y1,
                                         fill=color, outline="", tags="cell")

    def _draw_grid(self):
        """Draw grid lines and region outlines. Dim inactive/hidden regions."""
        z = self.zoom
        self.canvas.delete("grid")
        # Grid lines
        gc = "#2a2a2a" if z >= 3 else "#1a1a1a"
        for x in range(SKIN_W + 1):
            self.canvas.create_line(x * z, 0, x * z, SKIN_H * z,
                                    fill=gc, width=1, tags="grid")
        for y in range(SKIN_H + 1):
            self.canvas.create_line(0, y * z, SKIN_W * z, y * z,
                                    fill=gc, width=1, tags="grid")

        # Dim overlays
        for pname, r in SKIN_REGIONS.items():
            is_inactive = pname not in self.active_parts
            is_hidden   = self._is_hidden(pname)
            if is_hidden:
                # Strong dim — part is hidden from view
                self.canvas.create_rectangle(
                    r["sx"] * z, r["sy"] * z,
                    (r["sx"] + r["w"]) * z, (r["sy"] + r["h"]) * z,
                    fill="#000000", stipple="gray75", outline="", tags="grid")
            elif is_inactive:
                # Light dim — part visible but not editable
                self.canvas.create_rectangle(
                    r["sx"] * z, r["sy"] * z,
                    (r["sx"] + r["w"]) * z, (r["sy"] + r["h"]) * z,
                    fill="#000000", stipple="gray25", outline="", tags="grid")

        # Region outlines
        for pname, r in SKIN_REGIONS.items():
            col   = REGION_COLORS.get(pname, "#888888")
            active = pname in self.active_parts
            hidden = self._is_hidden(pname)
            width  = 3 if active and not hidden else 1
            dash   = () if active else (4, 4)
            self.canvas.create_rectangle(
                r["sx"] * z, r["sy"] * z,
                (r["sx"] + r["w"]) * z, (r["sy"] + r["h"]) * z,
                outline=col, width=width, fill="", dash=dash, tags="grid")

            # Label
            if z >= 5:
                label = pname + (" 🚫" if hidden else "")
                self.canvas.create_text(
                    r["sx"] * z + 3, r["sy"] * z + 2,
                    text=label, anchor="nw", fill=col,
                    font=("Segoe UI", max(6, min(z - 1, 10))), tags="grid")

    def _redraw_all(self):
        for (x, y), color in self.pixels.items():
            if color:
                self._paint_cell(x, y)

    def _update_preview(self):
        """Draw preview in selected mode (2D Front, 2D Back, or 3D)."""
        mode = self._preview_mode.get()
        if mode == "3D":
            self._draw_3d_preview()
        elif mode == "2D Back":
            self._draw_2d_preview(back=True)
        else:
            self._draw_2d_preview(back=False)

    def _draw_2d_preview(self, back=False):
        """Flat front or back view of the player skin."""
        c = self.prev_canvas
        c.delete("all")
        c.create_rectangle(0, 0, 180, 220, fill=C["skin_bg"], outline="")
        if self.invisible_mode:
            c.create_text(90, 110, text="👻\nInvisible", font=("Segoe UI", 14),
                          fill=C["yellow"], justify="center")
            return
        SCALE = 8

        # Part name -> (sx, sy, w, h, ox, oy, flip_for_back)
        FRONT_PARTS = [
            ("Head",      8, 8,  8, 8,  26, 4,   24, 8),
            ("Body",      20, 20, 8, 12, 26, 68,  32, 20),
            ("Right Arm", 44, 20, 4, 12, -6, 68,  44, 20),
            ("Left Arm",  36, 52, 4, 12, 90, 68,  36, 52),
            ("Right Leg", 4,  20, 4, 12, 26, 164, 12, 20),
            ("Left Leg",  20, 52, 4, 12, 58, 164, 28, 52),
        ]

        for part_name, fsx, fsy, w, h, ox, oy, bsx, bsy in FRONT_PARTS:
            if self._is_hidden(part_name):
                continue
            sx = bsx if back else fsx
            sy = bsy if back else fsy
            for dy in range(h):
                for dx in range(w):
                    src_x = (w - 1 - dx) if back else dx
                    col = self.pixels.get((sx + src_x, sy + dy))
                    if col:
                        c.create_rectangle(
                            ox + dx * SCALE, oy + dy * SCALE,
                            ox + dx * SCALE + SCALE, oy + dy * SCALE + SCALE,
                            fill=col, outline="")

        c.create_text(90, 215, text="Back" if back else "Front",
                      font=("Segoe UI", 8), fill=C["subtext"])

    def _draw_3d_preview(self):
        """Pseudo-3D isometric preview of the player model using tkinter canvas."""
        import math
        c = self.prev_canvas
        c.delete("all")
        c.create_rectangle(0, 0, 180, 220, fill=C["skin_bg"], outline="")

        if self.invisible_mode:
            c.create_text(90, 110, text="👻\nInvisible", font=("Segoe UI", 14),
                          fill=C["yellow"], justify="center")
            return

        angle_deg = self._rot_var.get()
        angle = math.radians(angle_deg)
        cos_a, sin_a = math.cos(angle), math.sin(angle)

        # Helper: project 3D point to 2D canvas
        CX, CY = 90, 105  # center of canvas
        SCALE = 10

        def project(x, y, z):
            # Simple perspective-ish projection: rotate around Y, then isometric-ish
            rx = x * cos_a - z * sin_a
            rz = x * sin_a + z * cos_a
            # Slight top-down tilt
            sx = CX + rx * SCALE
            sy = CY - y * SCALE + rz * SCALE * 0.4
            return sx, sy

        def draw_face(corners_3d, sx_skin, sy_skin, w, h, shade=1.0):
            """Draw one rectangular face of the body using skin pixels."""
            p = [project(*v) for v in corners_3d]
            # Check if face is front-facing (simple heuristic using cross product z)
            def cross_z(a, b, o):
                return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
            if cross_z(p[1], p[3], p[0]) < 0:
                return  # back face culling

            for gy in range(h):
                for gx in range(w):
                    col = self.pixels.get((sx_skin + gx, sy_skin + gy))
                    if not col:
                        continue
                    # Interpolate corners for this pixel cell
                    tx0, ty0 = gx / w, gy / h
                    tx1, ty1 = (gx+1) / w, (gy+1) / h

                    def lerp2d(t0, t1):
                        # Bilinear interp of 4 corner points
                        def li(a, b, t): return a + (b - a) * t
                        top_l = (li(p[0][0], p[1][0], t0), li(p[0][1], p[1][1], t0))
                        top_r = (li(p[0][0], p[1][0], t1), li(p[0][1], p[1][1], t1))
                        bot_l = (li(p[3][0], p[2][0], t0), li(p[3][1], p[2][1], t0))
                        bot_r = (li(p[3][0], p[2][0], t1), li(p[3][1], p[2][1], t1))
                        tl = (li(top_l[0], bot_l[0], t0), li(top_l[1], bot_l[1], t0))
                        return tl  # approximate: just use top-left of cell
                    _ = lerp2d  # not used fully — use simple grid

                    # Simple pixel cell corners via bilinear
                    def blerp(tx, ty):
                        def li(a, b, t): return a + (b-a)*t
                        top = (li(p[0][0], p[1][0], tx), li(p[0][1], p[1][1], tx))
                        bot = (li(p[3][0], p[2][0], tx), li(p[3][1], p[2][1], tx))
                        return (li(top[0], bot[0], ty), li(top[1], bot[1], ty))

                    corners = [
                        blerp(tx0, ty0), blerp(tx1, ty0),
                        blerp(tx1, ty1), blerp(tx0, ty1),
                    ]
                    flat = [v for pt in corners for v in pt]

                    # Apply shading
                    try:
                        r = int(int(col[1:3], 16) * shade)
                        g = int(int(col[3:5], 16) * shade)
                        b = int(int(col[5:7], 16) * shade)
                        shaded = f"#{max(0,min(255,r)):02x}{max(0,min(255,g)):02x}{max(0,min(255,b)):02x}"
                    except Exception:
                        shaded = col
                    c.create_polygon(flat, fill=shaded, outline="")

        # Body parts in 3D coordinates (x=right, y=up, z=forward)
        # Each part: front face corners (top-left, top-right, bottom-right, bottom-left)
        # HEAD  (8×8, positioned above body)
        hs = 0.8  # head size factor
        # Front face of head
        draw_face([(-hs, 2.8+hs*2, hs), (hs, 2.8+hs*2, hs),
                   (hs, 2.8,        hs), (-hs, 2.8,        hs)],
                  8, 8, 8, 8, shade=1.0)
        # Right side of head
        draw_face([(hs, 2.8+hs*2, hs),  (hs, 2.8+hs*2, -hs),
                   (hs, 2.8,       -hs), (hs, 2.8,        hs)],
                  16, 8, 8, 8, shade=0.75)
        # Top of head
        draw_face([(-hs, 2.8+hs*2, -hs), (hs, 2.8+hs*2, -hs),
                   (hs,  2.8+hs*2,  hs), (-hs, 2.8+hs*2,  hs)],
                  8, 0, 8, 8, shade=0.85)

        # BODY
        draw_face([(-0.5, 2.8, 0.25), (0.5, 2.8, 0.25),
                   (0.5, 0,    0.25), (-0.5, 0,   0.25)],
                  20, 20, 8, 12, shade=1.0)
        draw_face([(0.5, 2.8, 0.25),  (0.5, 2.8, -0.25),
                   (0.5, 0,   -0.25), (0.5, 0,    0.25)],
                  28, 20, 4, 12, shade=0.7)

        # RIGHT ARM
        draw_face([(-0.75, 2.8, 0.25), (-0.5, 2.8, 0.25),
                   (-0.5,  0,   0.25), (-0.75, 0,   0.25)],
                  44, 20, 4, 12, shade=0.9)
        # LEFT ARM
        draw_face([(0.5, 2.8, 0.25),  (0.75, 2.8, 0.25),
                   (0.75, 0,  0.25),  (0.5, 0,    0.25)],
                  36, 52, 4, 12, shade=0.9)

        # RIGHT LEG
        draw_face([(-0.5, 0, 0.25), (-0.0, 0, 0.25),
                   (-0.0, -2.8, 0.25), (-0.5, -2.8, 0.25)],
                  4, 20, 4, 12, shade=1.0)
        # LEFT LEG
        draw_face([(0.0, 0, 0.25), (0.5, 0, 0.25),
                   (0.5, -2.8, 0.25), (0.0, -2.8, 0.25)],
                  20, 52, 4, 12, shade=1.0)

        c.create_text(90, 215, text=f"3D ({angle_deg}°)",
                      font=("Segoe UI", 8), fill=C["subtext"])

    def _clear_all(self):
        if messagebox.askyesno("Clear Skin", "Clear all pixels? This cannot be undone."):
            self.pixels = {k: None for k in self.pixels}
            self.canvas.delete("cell")
            self._update_preview()

    def _load_png(self):
        try:
            import importlib
            pil = importlib.import_module("PIL.Image")
            path = filedialog.askopenfilename(
                title="Open Skin PNG",
                filetypes=[("PNG Images", "*.png"), ("All Files", "*")])
            if not path: return
            img = pil.open(path).convert("RGBA")
            if img.size != (64, 64):
                img = img.resize((64, 64), pil.NEAREST)
            for y in range(64):
                for x in range(64):
                    r, g, b, a = img.getpixel((x, y))
                    if a > 0:
                        self.pixels[(x, y)] = f"#{r:02x}{g:02x}{b:02x}"
                    else:
                        self.pixels[(x, y)] = None
            self.canvas.delete("cell")
            self._redraw_all()
            self._update_preview()
        except ImportError:
            messagebox.showinfo("Pillow Required",
                "To load PNG skins, install Pillow:\n  pip install Pillow\n\nYou can still draw skins manually.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _save_skin(self):
        if self.invisible_mode:
            # Save as empty (transparent) skin
            pixel_data = {"__invisible__": True}
        else:
            # Serialize pixel data
            pixel_data = {f"{x},{y}": col
                          for (x, y), col in self.pixels.items() if col}
        self.on_save(pixel_data)

    def get_pixel_data(self):
        return {f"{x},{y}": col for (x, y), col in self.pixels.items() if col}

    def load_pixel_data(self, data):
        self.pixels = {k: None for k in self.pixels}
        for key, col in data.items():
            parts = key.split(",")
            if len(parts) == 2:
                try:
                    x, y = int(parts[0]), int(parts[1])
                    self.pixels[(x, y)] = col
                except Exception: pass
        self.canvas.delete("cell")
        self._redraw_all()
        self._update_preview()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════
class DarxLauncher:
    def __init__(self, root):
        self.root        = root
        self.im          = InstanceManager()
        self.msa         = MicrosoftAuth()
        self._auth       = _normalize_auth(self.msa.load_saved())  # None if not logged in
        self.dl          = Downloader()
        self.sm          = SkinManager()
        self.mpm         = ModpackManager()
        self.instances   = []
        self.sel_inst    = None
        self.mc_versions = KNOWN_VERSIONS[:]
        self._bedrock_detected = False
        self._java_mc_detected = False
        self.settings    = load_settings()

        # Apply saved theme
        if self.settings.get("theme", "dark") == "light":
            C.update(LIGHT_THEME)

        # Mods pagination state
        self._mods_page   = 0
        self._mods_total  = 0
        self._mods_hits   = []
        self._mods_query  = ""
        self._mods_cat    = None

        self._build_window()
        self._style()
        self._build_ui()
        threading.Thread(target=self._startup_tasks, daemon=True).start()
        self._reload_instances()

    # ─────────────────────────────────────────────────────────────────────────
    #  WINDOW & STYLE
    # ─────────────────────────────────────────────────────────────────────────
    def _build_window(self):
        self.root.title("DarxLauncher v5")
        self.root.configure(bg=C["bg"])
        self.root.geometry("1540x940")
        self.root.minsize(1300, 760)
        try: self.root.state("zoomed")
        except Exception: pass

    def _style(self):
        s = ttk.Style(); s.theme_use("default")
        s.configure("Treeview", background=C["bg3"], foreground=C["text"],
                    fieldbackground=C["bg3"], borderwidth=0, rowheight=32, font=F)
        s.configure("Treeview.Heading", background=C["bg2"], foreground=C["subtext"],
                    relief="flat", font=("Segoe UI", 9, "bold"))
        s.map("Treeview",
              background=[("selected", C["selected"])],
              foreground=[("selected", C["accent"])])
        s.configure("DL.Horizontal.TProgressbar",
                    troughcolor=C["bg3"], background=C["accent"],
                    bordercolor=C["border"], lightcolor=C["accent"], darkcolor=C["accent2"])
        s.configure("TNotebook", background=C["bg2"], borderwidth=0)
        s.configure("TNotebook.Tab", background=C["panel"], foreground=C["subtext"],
                    padding=[12, 7], font=FS, borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", C["bg3"])],
              foreground=[("selected", C["accent"])])

    # ─────────────────────────────────────────────────────────────────────────
    #  SHELL
    # ─────────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._update_bar()      # sets up the blue banner (hidden until update found)
        self._topbar()
        body = tk.Frame(self.root, bg=C["bg"])
        body.pack(fill="both", expand=True)
        self._sidebar(body)
        self.content = tk.Frame(body, bg=C["bg"])
        self.content.pack(side="left", fill="both", expand=True)
        self.pages = {}

        self._page_home()
        self._page_editions()
        self._page_instances()
        self._page_mod_browser()
        self._page_content_browser("resourcepacks", "🎨  RESOURCE PACKS",
                                   "Browse & install resource packs → /resourcepacks/", "resourcepack")
        self._page_content_browser("shaderpacks", "✨  SHADER PACKS",
                                   "Browse & install shaders → /shaderpacks/", "shader")
        self._page_content_browser("datapacks", "📦  DATA PACKS",
                                   "Browse & install data packs → /datapacks/", "datapack")
        self._page_modloader()
        self._page_skins()
        self._page_modpacks()
        self._page_settings()
        self._page_account()
        self._nav("home")
        self._statusbar()   # ← bottom launch bar
        self.root.after(100, self._update_acct_badge)  # refresh badge on startup
        self.root.after(300, self._maybe_show_tutorial)  # first-run tutorial

    # ─────────────────────────────────────────────────────────────────────────
    #  TOPBAR
    # ─────────────────────────────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────────────
    #  AUTO-UPDATER  (blue banner at top)
    # ─────────────────────────────────────────────────────────────────────────
    def _update_bar(self):
        """
        Thin blue bar that appears at the top when a newer GitHub release exists.
        Checks the GitHub Releases API in a background thread on startup.
        Uses a placeholder frame so the bar can be reliably shown at the very top.
        """
        # Placeholder frame always packed first — zero height when hidden
        self._upd_bar_placeholder = tk.Frame(self.root, bg=C["bg"], height=0)
        self._upd_bar_placeholder.pack(fill="x")

        self._upd_bar_frame = tk.Frame(self._upd_bar_placeholder, bg="#1565C0")
        # NOT packed yet — only shown if update found

        # Left side: update message label
        self._upd_bar_lbl = tk.Label(
            self._upd_bar_frame,
            text="", font=("Segoe UI", 9, "bold"),
            fg="white", bg="#1565C0")
        self._upd_bar_lbl.pack(side="left", padx=16, pady=7)

        # View Update Notes button (shown next to label)
        self._upd_notes_btn = tk.Button(
            self._upd_bar_frame,
            text="📋  View Update Notes",
            font=("Segoe UI", 9),
            fg="white", bg="#1976D2",
            activebackground="#1e88e5",
            relief="flat", padx=10, pady=4,
            cursor="hand2",
            command=self._show_update_notes
        )
        self._upd_notes_btn.pack(side="left", padx=(0, 8), pady=5)

        # Download button
        tk.Button(
            self._upd_bar_frame,
            text="⬇  Download Update",
            font=("Segoe UI", 9, "bold"),
            fg="#1565C0", bg="white",
            activebackground="#e3f2fd",
            relief="flat", padx=10, pady=4,
            cursor="hand2",
            command=self._do_update
        ).pack(side="left", padx=4, pady=5)

        # Dismiss button on the right
        tk.Button(
            self._upd_bar_frame,
            text="✕ Dismiss",
            font=("Segoe UI", 8),
            fg="#bbdefb", bg="#1565C0",
            activebackground="#1976D2",
            relief="flat", padx=6,
            cursor="hand2",
            command=self._dismiss_update_bar
        ).pack(side="right", padx=10, pady=5)

        # Check for update in background
        threading.Thread(target=self._check_for_update, daemon=True).start()

    def _dismiss_update_bar(self):
        self._upd_bar_frame.pack_forget()
        self._upd_bar_placeholder.config(height=0)

    def _show_update_notes(self):
        """Show a popup window with the full update notes for the latest release."""
        ver   = getattr(self, "_upd_version", "?")
        notes = getattr(self, "_upd_notes_full", getattr(self, "_upd_notes", "No notes available."))

        dlg = tk.Toplevel(self.root)
        dlg.title(f"Update Notes — v{ver}")
        dlg.configure(bg=C["bg2"])
        dlg.geometry("560x420")
        dlg.resizable(True, True)
        dlg.transient(self.root)
        dlg.grab_set()

        # Header
        hdr = tk.Frame(dlg, bg="#1565C0", pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text=f"🔔  DarxLauncher v{ver} — Update Notes",
                 font=("Segoe UI", 11, "bold"), fg="white", bg="#1565C0").pack(padx=16)

        # Notes text area
        frm = tk.Frame(dlg, bg=C["bg2"])
        frm.pack(fill="both", expand=True, padx=16, pady=12)

        sb = tk.Scrollbar(frm)
        sb.pack(side="right", fill="y")

        txt = tk.Text(frm, font=("Segoe UI", 10), fg=C["text"], bg=C["panel"],
                      relief="flat", wrap="word", yscrollcommand=sb.set,
                      padx=12, pady=10, state="normal")
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)

        txt.insert("1.0", notes if notes else "No release notes provided.")
        txt.config(state="disabled")

        # Buttons row
        btn_row = tk.Frame(dlg, bg=C["bg2"])
        btn_row.pack(fill="x", padx=16, pady=(0, 14))
        tk.Button(btn_row, text="⬇  Download Update", font=("Segoe UI", 9, "bold"),
                  fg=C["bg"], bg=C["blue"], activebackground=C["accent"],
                  relief="flat", padx=12, pady=6, cursor="hand2",
                  command=lambda: [dlg.destroy(), self._do_update()]
                  ).pack(side="left")
        tk.Button(btn_row, text="Close", font=FS, fg=C["text"], bg=C["bg3"],
                  activebackground=C["border2"], relief="flat", padx=10, pady=6,
                  cursor="hand2", command=dlg.destroy).pack(side="right")

    def _check_for_update(self):
        """Fetch latest GitHub release tag and compare to current VERSION."""
        # Respect the auto_update setting
        if not self.settings.get("auto_update", True):
            return
        try:
            req = urllib.request.Request(
                f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest",
                headers={"User-Agent": f"DarxLauncher/{VERSION}",
                         "Accept": "application/vnd.github+json"})
            with urllib.request.urlopen(req, timeout=15) as r:
                data = json.loads(r.read())

            raw_tag = data.get("tag_name", "")
            tag  = raw_tag.lstrip("v")
            name = data.get("name", raw_tag or f"v{tag}")
            full_notes  = data.get("body", "").strip()
            short_notes = full_notes.split("\n")[0][:100] if full_notes else ""

            if not tag:
                return

            def _parse(v):
                try:    return tuple(int(x) for x in v.split("."))
                except: return (0,)

            if _parse(tag) > _parse(VERSION):
                # Store download URL for the .exe asset if present, else release page
                assets = data.get("assets", [])
                dl_url = next(
                    (a["browser_download_url"] for a in assets
                     if a["name"].lower().endswith(".exe")),
                    data.get("html_url",
                             f"https://github.com/{GITHUB_REPO}/releases/latest"))
                self._upd_download_url = dl_url
                self._upd_version      = tag
                self._upd_notes        = short_notes
                self._upd_notes_full   = full_notes  # full markdown notes for popup
                self._upd_tag_display  = raw_tag or f"v{tag}"

                def _show():
                    # Label: "Update (vX.X.X) is ready to be installed"
                    tag_display = getattr(self, "_upd_tag_display", f"v{tag}")
                    msg = f"🔔  Update ({tag_display}) is ready to be installed"
                    self._upd_bar_lbl.config(text=msg)
                    # Pack the blue bar inside its placeholder so it appears at top
                    self._upd_bar_frame.pack(fill="x")
                    # Resize placeholder to fit
                    self._upd_bar_placeholder.config(height=0)
                self.root.after(0, _show)
        except Exception as e:
            print(f"[Updater] Check failed: {e}")

    def _do_update(self):
        """Ask user to confirm then download the update."""
        url  = getattr(self, "_upd_download_url",
                       f"https://github.com/{GITHUB_REPO}/releases/latest")
        ver  = getattr(self, "_upd_version", "?")
        notes = getattr(self, "_upd_notes", "")

        msg = f"DarxLauncher v{ver} is available.\n\n"
        if notes: msg += f"Changes:\n{notes}\n\n"

        # If it's a .exe asset, offer to download and relaunch
        if url.endswith(".exe"):
            msg += "Download and install now? The launcher will restart."
            if not messagebox.askyesno("Update Available", msg): return
            self._download_and_replace(url, ver)
        else:
            msg += "Open the GitHub releases page to download manually?"
            if messagebox.askyesno("Update Available", msg):
                webbrowser.open(url)

    def _download_and_replace(self, url, ver):
        """Download new .exe, replace current executable, relaunch."""
        import tempfile, os

        dlg = tk.Toplevel(self.root)
        dlg.title("Updating DarxLauncher…")
        dlg.configure(bg=C["bg2"])
        dlg.geometry("420x160")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        tk.Label(dlg, text=f"Downloading DarxLauncher v{ver}…",
                 font=FB, fg=C["text"], bg=C["bg2"]).pack(pady=(24, 8))
        bar = ttk.Progressbar(dlg, style="DL.Horizontal.TProgressbar",
                              length=360, mode="determinate")
        bar.pack()
        lbl = tk.Label(dlg, text="Starting…", font=FS, fg=C["subtext"], bg=C["bg2"])
        lbl.pack(pady=6)

        def _do():
            try:
                req = urllib.request.Request(url,
                      headers={"User-Agent": f"DarxLauncher/{VERSION}"})
                with urllib.request.urlopen(req, timeout=60) as r:
                    total = int(r.headers.get("Content-Length", 0))
                    tmp   = tempfile.NamedTemporaryFile(delete=False,
                            suffix=".exe", dir=tempfile.gettempdir())
                    done  = 0
                    while True:
                        chunk = r.read(65536)
                        if not chunk: break
                        tmp.write(chunk)
                        done += len(chunk)
                        if total:
                            pct = done / total * 100
                            dlg.after(0, lambda p=pct: bar.configure(value=p))
                        dlg.after(0, lambda d=done: lbl.config(
                            text=f"Downloaded {d//1024} KB…"))
                    tmp.close()

                new_path = tmp.name
                cur_path = sys.executable if getattr(sys, "frozen", False) else __file__

                # Write a small batch/shell script to replace exe after we exit
                if platform.system() == "Windows":
                    bat = tempfile.NamedTemporaryFile(
                        delete=False, suffix=".bat",
                        dir=tempfile.gettempdir(), mode="w")
                    bat.write(f'@echo off\n'
                              f'timeout /t 2 /nobreak >nul\n'
                              f'move /y "{new_path}" "{cur_path}"\n'
                              f'start "" "{cur_path}"\n'
                              f'del "%~f0"\n')
                    bat.close()
                    subprocess.Popen(["cmd", "/c", bat.name],
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    sh = tempfile.NamedTemporaryFile(
                        delete=False, suffix=".sh",
                        dir=tempfile.gettempdir(), mode="w")
                    sh.write(f'#!/bin/sh\nsleep 2\n'
                             f'mv "{new_path}" "{cur_path}"\n'
                             f'chmod +x "{cur_path}"\n'
                             f'"{cur_path}" &\n')
                    sh.close()
                    os.chmod(sh.name, 0o755)
                    subprocess.Popen([sh.name])

                dlg.after(0, lambda: (
                    messagebox.showinfo("Update Ready",
                        f"DarxLauncher v{ver} downloaded!\nThe launcher will now restart."),
                    self.root.destroy()))

            except Exception as e:
                dlg.after(0, lambda: messagebox.showerror("Update Failed", str(e)))
                dlg.after(0, dlg.destroy)

        threading.Thread(target=_do, daemon=True).start()

    # ─────────────────────────────────────────────────────────────────────────
    #  FIRST-RUN TUTORIAL
    # ─────────────────────────────────────────────────────────────────────────
    def _maybe_show_tutorial(self):
        """Show the welcome tutorial only on first launch."""
        if FIRST_RUN_FILE.exists():
            return
        self.root.after(800, self._show_tutorial)   # slight delay so UI is ready

    def _show_tutorial(self):
        FIRST_RUN_FILE.parent.mkdir(parents=True, exist_ok=True)
        FIRST_RUN_FILE.touch()   # mark as done immediately so crash won't re-show

        dlg = tk.Toplevel(self.root)
        dlg.title("Welcome to DarxLauncher!")
        dlg.configure(bg=C["bg2"])
        dlg.geometry("680x620")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        # ── Header ────────────────────────────────────────────────────────────
        hdr = tk.Frame(dlg, bg=C["accent3"], pady=20); hdr.pack(fill="x")
        tk.Label(hdr, text="⛏", font=("Segoe UI Emoji", 32), bg=C["accent3"]).pack()
        tk.Label(hdr, text="Welcome to DarxLauncher!",
                 font=("Segoe UI", 18, "bold"), fg="white", bg=C["accent3"]).pack()
        tk.Label(hdr, text="Here's a quick tour of everything you need to know",
                 font=FS, fg="#ccffcc", bg=C["accent3"]).pack(pady=(2, 0))

        # ── Scrollable content ────────────────────────────────────────────────
        outer = tk.Frame(dlg, bg=C["bg2"]); outer.pack(fill="both", expand=True)
        canvas = tk.Canvas(outer, bg=C["bg2"], highlightthickness=0)
        sb = tk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(canvas, bg=C["bg2"])
        win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _resize(e):
            canvas.itemconfig(win, width=e.width)
        canvas.bind("<Configure>", _resize)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        def _section(icon, title, lines, btn_text=None, btn_cmd=None):
            card = tk.Frame(inner, bg=C["panel"],
                            highlightthickness=1, highlightbackground=C["border"],
                            padx=18, pady=14)
            card.pack(fill="x", padx=18, pady=6)
            top = tk.Frame(card, bg=C["panel"]); top.pack(fill="x")
            tk.Label(top, text=f"{icon}  {title}",
                     font=("Segoe UI", 12, "bold"),
                     fg=C["accent"], bg=C["panel"]).pack(side="left")
            for line in lines:
                tk.Label(card, text=line, font=FS, fg=C["subtext"],
                         bg=C["panel"], justify="left", wraplength=580,
                         anchor="w").pack(fill="x", pady=1)
            if btn_text and btn_cmd:
                tk.Button(card, text=btn_text, font=FS,
                          fg="white", bg=C["accent2"], relief="flat",
                          pady=4, padx=10, cursor="hand2",
                          command=lambda: (dlg.destroy(), btn_cmd())
                          ).pack(anchor="w", pady=(8, 0))

        _section("🔑", "Step 1 — Sign In (or play cracked)",
            ["Click 🔑 Microsoft Login in the top-right corner.",
             "A code will appear — go to microsoft.com/link in any browser and enter it.",
             "Sign in with your Microsoft account that owns Minecraft Java Edition.",
             "✅ Want to play cracked/offline instead? Click 'Play Offline / Cracked' in the login dialog.",
             "   Offline mode lets you play solo and on cracked servers, but NOT on online-mode servers."],
            "🔑 Open Login", lambda: self._msa_login())

        _section("📦", "Step 2 — Create an Instance",
            ["An 'instance' is a separate Minecraft installation (like a profile).",
             "Go to 📦 Instances → click ➕ New Instance.",
             "Pick a Minecraft version, give it a name, and click Create.",
             "You can have multiple instances — e.g. one for vanilla, one for mods."],
            "📦 Go to Instances", lambda: self._nav("instances"))

        _section("🔧", "Step 3 — Add Mods",
            ["Go to 🔧 Browse Mods in the sidebar.",
             "Search for any mod (e.g. 'Optifine', 'Sodium', 'JEI').",
             "Select your Minecraft version in the dropdown, then click ⬇ Install.",
             "Mods are saved inside your instance's /mods/ folder automatically.",
             "Tip: Make sure your instance uses Fabric or Forge — mods need a mod loader!"],
            "🔧 Browse Mods", lambda: self._nav("mods"))

        _section("🎨", "Step 4 — Resource Packs & Shaders",
            ["Go to 🎨 Resource Packs or ✨ Shader Packs in the sidebar.",
             "Browse and install packs the same way as mods.",
             "Resource packs change textures/sounds. Shaders add lighting effects.",
             "Shaders require OptiFine or Iris Shaders (install as a mod first)."],
            "🎨 Browse Resource Packs", lambda: self._nav("resourcepacks"))

        _section("⚙", "Step 5 — Settings",
            ["Go to ⚙ Settings to configure Java path, allocated RAM, and more.",
             "Recommended RAM: 2GB for vanilla, 4–6GB for modded.",
             "If the game won't launch, check that Java is installed (Java 17+ for 1.18+)."],
            "⚙ Open Settings", lambda: self._nav("settings"))

        _section("▶", "You're ready to play!",
            ["Select an instance from the 📦 Instances page.",
             "Click ▶ PLAY in the top-right corner.",
             "The launcher will download all required files automatically on first launch.",
             "Enjoy! 🎮"])

        # ── Footer buttons ────────────────────────────────────────────────────
        foot = tk.Frame(dlg, bg=C["bg2"], pady=12); foot.pack(fill="x")
        tk.Button(foot, text="✅  Got it — Let's Play!",
                  font=("Segoe UI", 11, "bold"),
                  fg="white", bg=C["accent2"],
                  activebackground=C["accent"],
                  relief="flat", padx=24, pady=10,
                  cursor="hand2",
                  command=dlg.destroy).pack()
        tk.Button(foot, text="Show this tutorial again",
                  font=("Segoe UI", 8), fg=C["muted"], bg=C["bg2"],
                  relief="flat", cursor="hand2",
                  command=lambda: None).pack(pady=(4, 0))
        # Bind "show again" to actually delete the flag file so it shows next time
        foot.winfo_children()[-1].config(
            command=lambda: (FIRST_RUN_FILE.unlink(missing_ok=True),
                             messagebox.showinfo("Tutorial",
                                 "The tutorial will show again next time you start DarxLauncher.")))

    def _topbar(self):
        bar = tk.Frame(self.root, bg=C["bg2"], height=56)
        bar.pack(fill="x"); bar.pack_propagate(False)

        lf = tk.Frame(bar, bg=C["bg2"])
        lf.pack(side="left", padx=18, pady=10)
        cv = tk.Canvas(lf, width=32, height=32, bg=C["bg2"], highlightthickness=0)
        cv.pack(side="left", padx=(0, 8))
        cv.create_polygon([16, 2, 28, 7, 28, 21, 16, 30, 4, 21, 4, 7],
                          fill=C["accent3"], outline=C["accent"], width=2)
        cv.create_text(16, 16, text="D", font=("Segoe UI", 11, "bold"), fill=C["white"])
        tk.Label(lf, text="DARX",     font=("Segoe UI", 16, "bold"), fg=C["white"],  bg=C["bg2"]).pack(side="left")
        tk.Label(lf, text="LAUNCHER", font=("Segoe UI", 16, "bold"), fg=C["accent"], bg=C["bg2"]).pack(side="left")
        tk.Label(lf, text=f" v{VERSION}", font=("Segoe UI", 8), fg=C["muted"], bg=C["bg2"]).pack(side="left")

        rf = tk.Frame(bar, bg=C["bg2"])
        rf.pack(side="right", padx=18)

        # ── Account badge ─────────────────────────────────────────────────────
        self._acct_frame = tk.Frame(rf, bg=C["bg2"])
        self._acct_frame.pack(side="right", padx=(0, 14))
        self._acct_lbl = tk.Label(self._acct_frame,
                                  text="⚠ Not logged in", font=("Segoe UI", 8),
                                  fg=C["yellow"], bg=C["bg2"])
        self._acct_lbl.pack()
        tk.Button(self._acct_frame, text="🔑 Microsoft Login",
                  font=("Segoe UI", 8, "bold"), fg=C["bg"], bg=C["blue"],
                  activebackground=C["accent"], activeforeground=C["bg"],
                  relief="flat", padx=8, pady=3, cursor="hand2",
                  command=self._msa_login).pack(pady=(2, 0))

        self.sel_lbl = tk.Label(rf, text="No instance selected",
                                font=FS, fg=C["subtext"], bg=C["bg2"])
        self.sel_lbl.pack(side="right", padx=10)
        self.play_btn = tk.Button(rf, text="▶  PLAY",
                                  font=("Segoe UI", 11, "bold"), fg=C["bg"], bg=C["text"],
                                  activebackground=C["subtext"], activeforeground=C["bg"],
                                  relief="flat", padx=22, pady=7, cursor="hand2", command=self._launch)
        self.play_btn.pack(side="right")

        # ── Server Quick-Connect ──────────────────────────────────────────────
        sc_frame = tk.Frame(rf, bg=C["bg2"])
        sc_frame.pack(side="right", padx=(0, 12))
        tk.Label(sc_frame, text="SERVER IP (offline-mode only):", font=("Segoe UI", 7),
                 fg=C["yellow"], bg=C["bg2"]).pack(anchor="w")
        sc_row = tk.Frame(sc_frame, bg=C["bg2"]); sc_row.pack()
        self._server_ip_var   = tk.StringVar()
        self._server_port_var = tk.StringVar(value="25565")
        tk.Entry(sc_row, textvariable=self._server_ip_var, font=FM,
                 bg=C["bg3"], fg=C["text"], relief="flat", insertbackground=C["text"],
                 width=22, highlightthickness=1, highlightbackground=C["border"]
                 ).pack(side="left", ipady=4, padx=(0, 4))
        tk.Label(sc_row, text="Port:", font=("Segoe UI", 7), fg=C["subtext"], bg=C["bg2"]).pack(side="left")
        tk.Entry(sc_row, textvariable=self._server_port_var, font=FM,
                 bg=C["bg3"], fg=C["text"], relief="flat", insertbackground=C["text"],
                 width=6, highlightthickness=1, highlightbackground=C["border"]
                 ).pack(side="left", ipady=4, padx=(2, 0))

        tk.Frame(self.root, bg=C["border"], height=1).pack(fill="x")

    # ─────────────────────────────────────────────────────────────────────────
    #  SIDEBAR
    # ─────────────────────────────────────────────────────────────────────────
    def _sidebar(self, body):
        sb = tk.Frame(body, bg=C["bg2"], width=220)
        sb.pack(side="left", fill="y"); sb.pack_propagate(False)
        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x")

        nav = [
            ("🏠", "Home",           "home"),
            ("🎮", "Editions",       "editions"),
            ("📦", "Instances",      "instances"),
            ("🔧", "Mods",           "mods"),
            ("🎨", "Resource Packs", "resourcepacks"),
            ("✨", "Shader Packs",   "shaderpacks"),
            ("📦", "Data Packs",     "datapacks"),
            ("🔩", "Mod Loaders",    "modloader"),
            ("👤", "Skin Editor",    "skins"),
            ("📦", "Modpacks",       "modpacks"),
            ("⚙",  "Settings",       "settings"),
            ("👤", "Account",        "account"),
        ]
        self._nav_btns = {}
        for icon, label, pid in nav:
            f  = tk.Frame(sb, bg=C["bg2"], cursor="hand2"); f.pack(fill="x")
            il = tk.Label(f, text=icon, font=("Segoe UI", 11),
                          fg=C["muted"], bg=C["bg2"], width=3)
            il.pack(side="left", padx=(12, 0), pady=10)
            tl = tk.Label(f, text=label, font=F,
                          fg=C["subtext"], bg=C["bg2"], anchor="w")
            tl.pack(side="left", fill="x", expand=True)
            ab = tk.Frame(f, bg=C["bg2"], width=3); ab.pack(side="right", fill="y")
            self._nav_btns[pid] = (f, il, tl, ab)
            for w in (f, il, tl):
                w.bind("<Button-1>", lambda e, p=pid: self._nav(p))

        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x", side="bottom")
        tk.Label(sb, text="ACTIVE INSTANCE", font=("Segoe UI", 7),
                 fg=C["muted"], bg=C["bg2"]).pack(side="bottom", padx=10, anchor="w")
        self.sb_lbl = tk.Label(sb, text="None selected", font=FS,
                                fg=C["accent"], bg=C["bg2"], wraplength=190)
        self.sb_lbl.pack(side="bottom", padx=10, pady=3, anchor="w")

        # ── Minecraft username display at bottom-left ──────────────────────
        tk.Frame(sb, bg=C["border"], height=1).pack(fill="x", side="bottom")
        self._sidebar_acct_lbl = tk.Label(sb, text="🎮 Offline Mode",
                                           font=("Segoe UI", 8, "bold"),
                                           fg=C["muted"], bg=C["bg2"],
                                           cursor="hand2", wraplength=190)
        self._sidebar_acct_lbl.pack(side="bottom", padx=10, pady=(4,2), anchor="w")
        self._sidebar_acct_lbl.bind("<Button-1>", lambda e: self._nav("account"))

    def _nav(self, pid):
        for p in self.pages.values(): p.pack_forget()
        self.pages[pid].pack(fill="both", expand=True)
        for p2, (f, il, tl, ab) in self._nav_btns.items():
            if p2 == pid:
                for w in (f, il, tl): w.config(bg=C["bg3"])
                il.config(fg=C["text"]); tl.config(fg=C["text"]); ab.config(bg=C["accent"])
            else:
                for w in (f, il, tl): w.config(bg=C["bg2"])
                il.config(fg=C["muted"]); tl.config(fg=C["subtext"]); ab.config(bg=C["bg2"])

    # ─────────────────────────────────────────────────────────────────────────
    #  BOTTOM STATUS / LAUNCH BAR
    # ─────────────────────────────────────────────────────────────────────────
    def _statusbar(self):
        """Permanent bottom bar — shows launch progress and system info."""
        # Separator line
        tk.Frame(self.root, bg=C["border"], height=1).pack(fill="x", side="bottom")

        bar = tk.Frame(self.root, bg=C["bg2"], height=38)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        # Left: launch status text
        left = tk.Frame(bar, bg=C["bg2"])
        left.pack(side="left", fill="y", padx=12)

        self._launch_icon_lbl = tk.Label(left, text="⛏", font=("Segoe UI Emoji", 13),
                                          fg=C["muted"], bg=C["bg2"])
        self._launch_icon_lbl.pack(side="left", padx=(0, 6))

        self._launch_status_lbl = tk.Label(left,
            text="Ready — select an instance and press ▶ PLAY",
            font=("Segoe UI", 9), fg=C["subtext"], bg=C["bg2"])
        self._launch_status_lbl.pack(side="left")

        # Right: progress bar + pct label
        right = tk.Frame(bar, bg=C["bg2"])
        right.pack(side="right", fill="y", padx=12)

        self._launch_pct_lbl = tk.Label(right, text="", font=("Segoe UI", 8, "bold"),
                                         fg=C["accent"], bg=C["bg2"], width=5)
        self._launch_pct_lbl.pack(side="right", padx=(4, 0))

        self._launch_bar = ttk.Progressbar(right, style="DL.Horizontal.TProgressbar",
                                            mode="determinate", length=340)
        self._launch_bar.pack(side="right", pady=9)
        self._launch_bar["value"] = 0

    def _set_launch_status(self, text, pct=0, icon="⛏", color=None):
        """Update the bottom launch bar — safe to call from any thread."""
        def _do():
            try:
                self._launch_status_lbl.config(text=text,
                    fg=color or C["subtext"])
                self._launch_icon_lbl.config(text=icon)
                self._launch_bar["value"] = pct
                self._launch_pct_lbl.config(
                    text=f"{int(pct)}%" if pct > 0 else "")
            except Exception:
                pass
        self.root.after(0, _do)

    # ─────────────────────────────────────────────────────────────────────────
    #  HOME
    # ─────────────────────────────────────────────────────────────────────────
    def _page_home(self):
        p = self._newpage("home")
        hero = tk.Frame(p, bg=C["panel2"], pady=22,
                        highlightthickness=1, highlightbackground=C["border"])
        hero.pack(fill="x", padx=22, pady=14)
        tk.Label(hero, text="⛏", font=("Segoe UI Emoji", 36), bg=C["panel2"]).pack()
        tk.Label(hero, text="Welcome to DarxLauncher", font=FXL,
                 fg=C["text"], bg=C["panel2"]).pack()
        tk.Label(hero,
                 text="Java & Bedrock · Forge · Fabric · Quilt · NeoForge · Live Mod Browser · Skin Editor · Modpacks",
                 font=FS, fg=C["subtext"], bg=C["panel2"]).pack(pady=3)

        qa = tk.Frame(p, bg=C["bg"]); qa.pack(pady=8)
        shortcuts = [
            ("🎮 Editions",      "editions"),
            ("📦 Instances",     "instances"),
            ("🔧 Browse Mods",   "mods"),
            ("🎨 Resource Packs","resourcepacks"),
            ("✨ Shaders",       "shaderpacks"),
            ("👤 Skin Editor",   "skins"),
            ("📦 Modpacks",      "modpacks"),
            ("⚙ Settings",       "settings"),
        ]
        for txt, pid in shortcuts:
            self._gbtn(qa, txt, lambda p=pid: self._nav(p), 145, C["accent2"]).pack(side="left", padx=3)

        nh = tk.Frame(p, bg=C["bg"]); nh.pack(fill="x", padx=22, pady=(8, 3))
        tk.Label(nh, text="MINECRAFT NEWS", font=FB, fg=C["text"], bg=C["bg"]).pack(side="left")
        self._sbtn(nh, "🔄 Refresh", self._load_news).pack(side="right")
        self.news_frame = tk.Frame(p, bg=C["bg"])
        self.news_frame.pack(fill="both", expand=True, padx=22, pady=(0, 12))
        for t, d, dt, dot in [
            ("Minecraft Java 1.21.4",  "Latest with new blocks & biomes.",        "2024-12-03", "⬤"),
            ("Forge for 1.21.x",       "Forge fully supports 1.21.1 & 1.21.4.",   "2024-11-20", "⬤"),
            ("Fabric 0.16.x",          "Full 1.21.4 support.",                    "2024-11-15", "⬤"),
            ("NeoForge 21.1.x",        "Stable release for 1.21.1.",              "2024-11-10", "⬤"),
        ]: self._news_card(self.news_frame, t, d, dt, dot)
        threading.Thread(target=self._load_news, daemon=True).start()

    def _news_card(self, parent, title, desc, date, dot="⬤"):
        card = tk.Frame(parent, bg=C["panel"],
                        highlightthickness=1, highlightbackground=C["border"],
                        pady=9, padx=14)
        card.pack(fill="x", pady=2)
        top = tk.Frame(card, bg=C["panel"]); top.pack(fill="x")
        tk.Label(top, text=f"{dot}  {title}", font=FB, fg=C["text"], bg=C["panel"]).pack(side="left")
        tk.Label(top, text=date, font=FS, fg=C["muted"], bg=C["panel"]).pack(side="right")
        tk.Label(card, text=desc, font=FS, fg=C["subtext"], bg=C["panel"], justify="left").pack(anchor="w", pady=(2, 0))

    def _load_news(self):
        try:
            data = self.dl.fetch_json("https://launchercontent.mojang.com/javaPatchNotes.json")
            if data and "entries" in data:
                for w in self.news_frame.winfo_children(): w.destroy()
                for e in data["entries"][:5]:
                    self.root.after(0, self._news_card, self.news_frame,
                                    e.get("title", "Update"), "See full notes on minecraft.net",
                                    e.get("date", "")[:10], "⬤")
        except Exception: pass

    # ─────────────────────────────────────────────────────────────────────────
    #  EDITIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _page_editions(self):
        p = self._newpage("editions")
        self._ptitle(p, "🎮  MINECRAFT EDITIONS",
                     "Choose which edition of Minecraft to play — Java, Bedrock, or both")

        cards_row = tk.Frame(p, bg=C["bg"])
        cards_row.pack(fill="x", padx=22, pady=12)

        java_card = tk.Frame(cards_row, bg=C["panel"],
                             highlightthickness=2, highlightbackground=C["border"],
                             padx=24, pady=24)
        java_card.pack(side="left", fill="both", expand=True, padx=(0, 10))
        tk.Label(java_card, text="☕", font=("Segoe UI Emoji", 44), bg=C["panel"]).pack()
        tk.Label(java_card, text="Java Edition", font=("Segoe UI", 18, "bold"),
                 fg=C["text"], bg=C["panel"]).pack(pady=(4, 2))
        tk.Label(java_card,
                 text="The original PC version. Supports mods, custom servers,\n"
                      "and all modloaders (Forge, Fabric, Quilt, NeoForge).\n"
                      "Create instances and install mods directly from this launcher.",
                 font=FS, fg=C["subtext"], bg=C["panel"], justify="center").pack(pady=8)
        self._java_status_lbl = tk.Label(java_card, text="Checking…", font=FS, fg=C["yellow"], bg=C["panel"])
        self._java_status_lbl.pack(pady=4)
        jbf = tk.Frame(java_card, bg=C["panel"]); jbf.pack(pady=8)
        self._gbtn(jbf, "📦 New Java Instance",
                   lambda: (self._nav("instances"), self._new_instance_dialog()), 200).pack(side="left", padx=4)
        self._sbtn(jbf, "🔧 Browse Mods", lambda: self._nav("mods")).pack(side="left", padx=4)
        self._gbtn(java_card, "▶  Launch Java Minecraft", self._launch_official_java, 240).pack(pady=4)

        be_card = tk.Frame(cards_row, bg=C["panel"],
                           highlightthickness=2, highlightbackground=C["border"],
                           padx=24, pady=24)
        be_card.pack(side="left", fill="both", expand=True, padx=(10, 0))
        tk.Label(be_card, text="🪨", font=("Segoe UI Emoji", 44), bg=C["panel"]).pack()
        tk.Label(be_card, text="Bedrock Edition", font=("Segoe UI", 18, "bold"),
                 fg=C["text"], bg=C["panel"]).pack(pady=(4, 2))
        tk.Label(be_card,
                 text="Cross-platform version (PC, Xbox, Mobile, PlayStation).\n"
                      "Supports Add-ons & Marketplace content.\n"
                      "Cannot use Java mods — uses Microsoft's own launcher.",
                 font=FS, fg=C["subtext"], bg=C["panel"], justify="center").pack(pady=8)
        self._bedrock_status_lbl = tk.Label(be_card, text="Checking…", font=FS, fg=C["yellow"], bg=C["panel"])
        self._bedrock_status_lbl.pack(pady=4)
        bbf = tk.Frame(be_card, bg=C["panel"]); bbf.pack(pady=8)
        self._gbtn(bbf, "▶  Open Bedrock", self._launch_bedrock, 200).pack(side="left", padx=4)
        self._sbtn(bbf, "🛒 Marketplace",
                   lambda: webbrowser.open("https://www.minecraft.net/en-us/marketplace")).pack(side="left", padx=4)

        info = self._scard(p, "WHICH EDITION?")
        tk.Label(info, justify="left", font=FS, fg=C["subtext"], bg=C["panel"], text=(
            "Java Edition  →  Best for mods, custom servers, and full modloader support\n"
            "Bedrock Edition  →  Best for cross-play with Xbox/Mobile/Console friends\n"
            "You can have BOTH installed at the same time."
        )).pack(anchor="w")

        threading.Thread(target=self._detect_editions, daemon=True).start()

    def _detect_editions(self):
        bedrock = self.dl.detect_bedrock()
        java    = self.dl.detect_java_mc()
        def upd():
            self._bedrock_status_lbl.config(
                text="✅ Detected" if bedrock else "⚪ Not detected",
                fg=C["green"] if bedrock else C["muted"])
            self._java_status_lbl.config(
                text="✅ Detected (.minecraft found)" if java else "⚪ Not detected",
                fg=C["green"] if java else C["muted"])
        self.root.after(0, upd)

    def _launch_bedrock(self):
        if platform.system() == "Windows":
            try:
                subprocess.Popen(["powershell", "-Command", "Start-Process 'minecraft:'"], shell=False)
                return
            except Exception: pass
        webbrowser.open("https://www.minecraft.net/en-us/download")

    def _launch_official_java(self):
        candidates = [
            Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Minecraft Launcher/MinecraftLauncher.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Minecraft Launcher/MinecraftLauncher.exe",
            Path.home() / "AppData/Roaming/Minecraft Launcher/MinecraftLauncher.exe",
        ]
        for c in candidates:
            if c.exists():
                try: subprocess.Popen([str(c)]); return
                except Exception: pass
        webbrowser.open("https://www.minecraft.net/en-us/download")

    # ─────────────────────────────────────────────────────────────────────────
    #  INSTANCES
    # ─────────────────────────────────────────────────────────────────────────
    def _page_instances(self):
        p = self._newpage("instances")
        self._ptitle(p, "📦  INSTANCES", "Each instance is a fully isolated Minecraft install")
        tb = tk.Frame(p, bg=C["bg"]); tb.pack(fill="x", padx=22, pady=(0, 8))
        self._gbtn(tb, "＋  New Instance", self._new_instance_dialog, 172).pack(side="left", padx=(0, 5))
        self._sbtn(tb, "📂 Open Folder",   self._open_inst_folder).pack(side="left", padx=3)
        self._sbtn(tb, "🔩 Mod Loader",    self._quick_install_loader).pack(side="left", padx=3)
        self._sbtn(tb, "🗑 Delete",         self._delete_instance, C["red"]).pack(side="left", padx=3)

        self._inst_canvas = tk.Canvas(p, bg=C["bg"], highlightthickness=0)
        isb = ttk.Scrollbar(p, orient="vertical", command=self._inst_canvas.yview)
        self._inst_inner = tk.Frame(self._inst_canvas, bg=C["bg"])
        self._inst_inner.bind("<Configure>",
                              lambda e: self._inst_canvas.configure(
                                  scrollregion=self._inst_canvas.bbox("all")))
        self._inst_canvas.create_window((0, 0), window=self._inst_inner, anchor="nw")
        self._inst_canvas.configure(yscrollcommand=isb.set)
        isb.pack(side="right", fill="y", padx=(0, 22))
        self._inst_canvas.pack(fill="both", expand=True, padx=22)

    def _reload_instances(self):
        self.instances = self.im.get_all()
        if not hasattr(self, "_inst_inner"): return
        for w in self._inst_inner.winfo_children(): w.destroy()
        if not self.instances:
            tk.Label(self._inst_inner,
                     text="\n\n  No instances yet — click '＋ New Instance' to get started!\n",
                     font=F, fg=C["subtext"], bg=C["bg"]).pack()
            return
        row = None
        for i, inst in enumerate(self.instances):
            if i % 4 == 0:
                row = tk.Frame(self._inst_inner, bg=C["bg"])
                row.pack(fill="x", pady=4)
            self._inst_card(row, inst)
        self._refresh_ml_inst_list()

    def _inst_card(self, parent, inst):
        sel    = self.sel_inst and self.sel_inst.get("name") == inst["name"]
        card   = tk.Frame(parent, bg=C["panel"], width=248, height=190,
                          highlightthickness=2,
                          highlightbackground=C["text"] if sel else C["border"],
                          cursor="hand2")
        card.pack(side="left", padx=5); card.pack_propagate(False)

        tk.Label(card, text=inst.get("icon", "🎮"),
                 font=("Segoe UI Emoji", 28), bg=C["panel"]).pack(pady=(10, 2))
        tk.Label(card, text=inst["name"], font=FB, fg=C["text"], bg=C["panel"]).pack()
        tk.Label(card, text=inst["version"], font=FS, fg=C["subtext"], bg=C["panel"]).pack()

        bf = tk.Frame(card, bg=C["panel"]); bf.pack(pady=3)
        ml_col = ML_COLORS.get(inst.get("modloader", "Vanilla"), C["muted"])
        for badge_text, bcol in [(inst.get("edition","Java"), C["accent2"]),
                                 (inst.get("modloader","Vanilla"), ml_col)]:
            b = tk.Frame(bf, bg=bcol, padx=6, pady=1); b.pack(side="left", padx=2)
            tk.Label(b, text=badge_text, font=("Segoe UI", 7, "bold"), fg=C["bg"], bg=bcol).pack()

        tk.Label(card, text=f"RAM: {inst.get('ram', 2)} GB", font=FS, fg=C["muted"], bg=C["panel"]).pack()
        lp = inst.get("last_played") or "Never played"
        tk.Label(card, text=f"Last: {lp}", font=("Segoe UI", 7), fg=C["muted"], bg=C["panel"]).pack()

        for w in card.winfo_children() + [card]:
            w.bind("<Button-1>", lambda e, i=inst: self._select_instance(i))
        card.bind("<Double-1>", lambda e, i=inst: (self._select_instance(i), self._launch()))

    def _select_instance(self, inst):
        self.sel_inst = inst
        n, v, ml = inst["name"], inst["version"], inst.get("modloader", "Vanilla")
        self.sel_lbl.config(text=f"{inst.get('icon','🎮')} {n}  [{v} · {ml}]")
        self.sb_lbl.config(text=f"{n}\n{v} · {ml}")
        self._reload_instances()
        self._sync_browser_instance()
        # Update bottom status bar
        self._set_launch_status(
            f"Selected: {n}  ·  {v}  ·  {ml}  ·  {inst.get('ram',2)} GB RAM  —  Press ▶ PLAY to launch",
            pct=0, icon=inst.get("icon", "🎮"))

    def _sync_browser_instance(self):
        if not self.sel_inst: return
        inst = self.sel_inst
        for pid in ("mods", "resourcepacks", "shaderpacks", "datapacks"):
            lbl = getattr(self, f"_{pid}_inst_lbl", None)
            if lbl: lbl.config(
                text=f"✅  Installing to: {inst['name']}  [{inst['version']} · {inst.get('modloader','Vanilla')}]")
            vv = getattr(self, f"_{pid}_ver_var", None)
            if vv: vv.set(inst["version"])
            lv = getattr(self, f"_{pid}_ldr_var", None)
            if lv: lv.set(inst.get("modloader", "Any"))

    def _new_instance_dialog(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("New Instance"); dlg.configure(bg=C["bg2"])
        dlg.geometry("520x540"); dlg.resizable(False, False)
        dlg.transient(self.root); dlg.grab_set()
        tk.Label(dlg, text="Create New Instance", font=FL, fg=C["text"], bg=C["bg2"]).pack(pady=(16, 12))

        def row(lbl, wfn):
            f = tk.Frame(dlg, bg=C["bg2"]); f.pack(fill="x", padx=26, pady=4)
            tk.Label(f, text=lbl, font=FS, fg=C["subtext"], bg=C["bg2"],
                     width=14, anchor="w").pack(side="left")
            wfn(f)

        name_v = tk.StringVar(value="My Instance")
        row("Name:", lambda f: tk.Entry(f, textvariable=name_v, font=F,
            bg=C["bg3"], fg=C["text"], relief="flat", insertbackground=C["text"],
            highlightthickness=1, highlightbackground=C["border"]).pack(
            side="left", fill="x", expand=True, ipady=6))

        ed_v = tk.StringVar(value="Java")
        row("Edition:", lambda f: ttk.Combobox(f, textvariable=ed_v,
            values=["Java", "Bedrock"], font=F, state="readonly", width=18).pack(side="left"))

        ver_v = tk.StringVar(value=self.mc_versions[0])
        row("MC Version:", lambda f: ttk.Combobox(f, textvariable=ver_v,
            values=self.mc_versions, font=F, state="readonly", width=18).pack(side="left"))

        ml_v = tk.StringVar(value="Vanilla")
        row("Modloader:", lambda f: ttk.Combobox(f, textvariable=ml_v,
            values=MODLOADERS, font=F, state="readonly", width=18).pack(side="left"))

        ram_v = tk.IntVar(value=self.settings.get("default_ram", 2))
        def ram_w(f):
            tk.Scale(f, variable=ram_v, from_=1, to=32, orient="horizontal",
                     bg=C["bg2"], fg=C["text"], highlightthickness=0,
                     troughcolor=C["bg3"], length=200).pack(side="left")
            ram_lbl = tk.Label(f, textvariable=ram_v, font=FS, fg=C["text"], bg=C["bg2"])
            ram_lbl.pack(side="left", padx=3)
            tk.Label(f, text="GB", font=FS, fg=C["subtext"], bg=C["bg2"]).pack(side="left")
        row("RAM:", ram_w)

        icon_v = tk.StringVar(value="🎮")
        icons  = ["🎮", "⚔️", "🏹", "🧪", "🌋", "🏔️", "🌊", "🔥", "❄️", "🌿", "💎", "🛡️", "🐉", "🦋", "🎯", "🚀"]
        def icon_w(f):
            icf = tk.Frame(f, bg=C["bg2"]); icf.pack(side="left")
            for ic in icons:
                tk.Button(icf, text=ic, font=("Segoe UI Emoji", 12), bg=C["bg3"],
                          relief="flat", cursor="hand2", padx=2,
                          command=lambda i=ic: icon_v.set(i)).pack(side="left", padx=1)
        row("Icon:", icon_w)

        warn = tk.Label(dlg, text="", font=FS, fg=C["yellow"], bg=C["bg2"])
        warn.pack(pady=(2, 0))
        def on_change(*_):
            ml = ml_v.get(); ed = ed_v.get()
            if ed == "Bedrock":
                warn.config(text="ℹ Bedrock instances launch via Microsoft's app.")
            elif ml == "NeoForge": warn.config(text="ℹ NeoForge requires MC 1.20.2+")
            else: warn.config(text="")
        ml_v.trace_add("write", on_change); ed_v.trace_add("write", on_change)

        def create():
            n = name_v.get().strip()
            if not n: messagebox.showerror("Error", "Enter an instance name.", parent=dlg); return
            self.im.create(n, ver_v.get(), ml_v.get(), ram_v.get(), icon_v.get(), ed_v.get())
            dlg.destroy(); self._reload_instances()
            if ml_v.get() != "Vanilla" and ed_v.get() == "Java":
                if messagebox.askyesno("Install Modloader",
                                       f"Install {ml_v.get()} for Minecraft {ver_v.get()} now?"):
                    self._nav("modloader"); self._ml_preselect(n)

        tk.Button(dlg, text="CREATE INSTANCE", font=FB, fg=C["bg"],
                  bg=C["text"], activebackground=C["subtext"], relief="flat",
                  pady=11, cursor="hand2", command=create).pack(fill="x", padx=26, pady=14)

    def _delete_instance(self):
        if not self.sel_inst:
            messagebox.showwarning("DarxLauncher", "Select an instance first."); return
        if messagebox.askyesno("Delete",
                               f"Delete '{self.sel_inst['name']}'?\nRemoves ALL files. Cannot be undone."):
            self.im.delete(self.sel_inst["path"])
            self.sel_inst = None
            self.sel_lbl.config(text="No instance selected")
            self.sb_lbl.config(text="None selected")
            self._reload_instances()

    def _open_inst_folder(self):
        if not self.sel_inst: messagebox.showwarning("DarxLauncher", "Select an instance first."); return
        self._open_path(self.sel_inst["path"])

    def _quick_install_loader(self):
        if not self.sel_inst: messagebox.showwarning("DarxLauncher", "Select an instance first."); return
        self._nav("modloader"); self._ml_preselect(self.sel_inst["name"])

    # ─────────────────────────────────────────────────────────────────────────
    #  MOD BROWSER  (paginated — no 50-mod cap)
    # ─────────────────────────────────────────────────────────────────────────
    def _page_mod_browser(self):
        p = self._newpage("mods")
        self._ptitle(p, "🔧  MOD BROWSER",
                     "Live Modrinth — unlimited mods, pages, 1-click install (no popup)")

        ib = tk.Frame(p, bg=C["panel"], highlightthickness=1,
                      highlightbackground=C["border"], padx=14, pady=7)
        ib.pack(fill="x", padx=22, pady=(0, 6))
        self._mods_inst_lbl = tk.Label(ib,
                                       text="⚠  No instance selected — pick one in Instances",
                                       font=FS, fg=C["yellow"], bg=C["panel"])
        self._mods_inst_lbl.pack(side="left")
        self._sbtn(ib, "📂 Open /mods/",
                   lambda: self._open_content_folder("mod")).pack(side="right")

        tf = tk.Frame(p, bg=C["bg"]); tf.pack(fill="x", padx=22, pady=(0, 5))
        self._mods_search_v = tk.StringVar()
        tk.Label(tf, text="🔍", font=F, fg=C["subtext"], bg=C["bg"]).pack(side="left", padx=(0, 3))
        se = tk.Entry(tf, textvariable=self._mods_search_v, font=F,
                      bg=C["bg3"], fg=C["text"], relief="flat",
                      insertbackground=C["text"],
                      highlightthickness=1, highlightbackground=C["border"])
        se.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 6))

        self._mods_ver_var = tk.StringVar(value=self.mc_versions[0])
        tk.Label(tf, text="Version:", font=FS, fg=C["subtext"], bg=C["bg"]).pack(side="left", padx=(0, 3))
        ttk.Combobox(tf, textvariable=self._mods_ver_var,
                     values=self.mc_versions, font=FS, state="readonly", width=9).pack(side="left", padx=(0, 6))

        self._mods_ldr_var = tk.StringVar(value="All")
        tk.Label(tf, text="Loader:", font=FS, fg=C["subtext"], bg=C["bg"]).pack(side="left", padx=(0, 3))
        ttk.Combobox(tf, textvariable=self._mods_ldr_var,
                     values=["All", "Fabric", "Forge", "Quilt", "NeoForge"],
                     font=FS, state="readonly", width=10).pack(side="left", padx=(0, 6))

        self._gbtn(tf, "🔍 Search",
                   lambda: self._mods_do_search(self._mods_search_v.get()), 100).pack(side="left", padx=2)
        se.bind("<Return>", lambda e: self._mods_do_search(self._mods_search_v.get()))

        # Category pills
        cat_frame = tk.Frame(p, bg=C["bg"]); cat_frame.pack(fill="x", padx=22, pady=(0, 5))
        self._active_cat = None; self._cat_btns = {}
        for lbl, query, cat in QUICK_CATS:
            btn = tk.Button(cat_frame, text=lbl, font=("Segoe UI", 8),
                            fg=C["subtext"], bg=C["bg3"],
                            activebackground=C["border2"], activeforeground=C["text"],
                            relief="flat", padx=8, pady=3, cursor="hand2",
                            command=lambda q=query, c=cat, l=lbl: self._mods_load_category(q, c, l))
            btn.pack(side="left", padx=2, pady=2)
            self._cat_btns[lbl] = btn

        # Split: list | detail
        split = tk.Frame(p, bg=C["bg"])
        split.pack(fill="both", expand=True, padx=22, pady=(0, 2))

        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True)

        cols = ("icon", "name", "author", "downloads", "updated", "loaders")
        self._mods_tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for col, hd, w, anch in [
            ("icon",     "",        28,  "center"),
            ("name",     "Name",    230, "w"),
            ("author",   "Author",  115, "w"),
            ("downloads","⬇ DLs",  90,  "center"),
            ("updated",  "Updated", 90,  "center"),
            ("loaders",  "Loaders", 120, "center"),
        ]:
            self._mods_tree.heading(col, text=hd)
            self._mods_tree.column(col, width=w, anchor=anch, stretch=(col == "name"))
        tsb = ttk.Scrollbar(left, orient="vertical", command=self._mods_tree.yview)
        self._mods_tree.configure(yscrollcommand=tsb.set)
        tsb.pack(side="right", fill="y")
        self._mods_tree.pack(fill="both", expand=True)
        self._mods_tree.bind("<<TreeviewSelect>>", self._mods_on_select)

        # RIGHT detail panel
        self._mods_detail = tk.Frame(split, bg=C["panel"], width=350,
                                     highlightthickness=1, highlightbackground=C["border"])
        self._mods_detail.pack(side="right", fill="y", padx=(8, 0))
        self._mods_detail.pack_propagate(False)
        self._detail_placeholder(self._mods_detail)

        # Pagination + status bar
        pb = tk.Frame(p, bg=C["bg"]); pb.pack(fill="x", padx=22, pady=(0, 4))
        self._mods_status = tk.Label(pb, text="Loading popular mods…",
                                     font=FS, fg=C["subtext"], bg=C["bg"])
        self._mods_status.pack(side="left")

        page_frame = tk.Frame(pb, bg=C["bg"]); page_frame.pack(side="right")
        self._prev_btn = tk.Button(page_frame, text="◀ Prev", font=FS,
                                   bg=C["bg3"], fg=C["text"], relief="flat",
                                   cursor="hand2", padx=8, pady=3,
                                   command=self._mods_prev_page)
        self._prev_btn.pack(side="left", padx=2)
        self._page_lbl = tk.Label(page_frame, text="Page 1", font=FS,
                                  fg=C["subtext"], bg=C["bg"])
        self._page_lbl.pack(side="left", padx=6)
        self._next_btn = tk.Button(page_frame, text="Next ▶", font=FS,
                                   bg=C["bg3"], fg=C["text"], relief="flat",
                                   cursor="hand2", padx=8, pady=3,
                                   command=self._mods_next_page)
        self._next_btn.pack(side="left", padx=2)
        self._mods_prog = ttk.Progressbar(pb, style="DL.Horizontal.TProgressbar",
                                          mode="determinate", length=200)
        self._mods_prog.pack(side="right", padx=(0, 10))
        self._mods_prog.pack_forget()

        threading.Thread(target=lambda: self._mods_load_category("", "optimization", "🔥 Trending"),
                         daemon=True).start()

    def _mods_load_category(self, query, category, label=None):
        for l, btn in self._cat_btns.items():
            btn.config(bg=C["text"] if l == label else C["bg3"],
                       fg=C["bg"] if l == label else C["subtext"])
        self._active_cat = category
        self._mods_query = query
        self._mods_page  = 0
        self._mods_status.config(text=f"Loading {label or query}…", fg=C["subtext"])
        self._detail_placeholder(self._mods_detail)
        self._mods_fetch()

    def _mods_do_search(self, query):
        for btn in self._cat_btns.values(): btn.config(bg=C["bg3"], fg=C["subtext"])
        self._active_cat = None
        self._mods_query = query
        self._mods_page  = 0
        self._mods_status.config(text=f"Searching '{query}'…", fg=C["subtext"])
        self._detail_placeholder(self._mods_detail)
        self._mods_fetch()

    def _mods_fetch(self):
        ver    = self._mods_ver_var.get()
        loader = self._mods_ldr_var.get()
        offset = self._mods_page * MODS_PER_PAGE
        threading.Thread(target=self._mods_fetch_worker,
                         args=(self._mods_query, ver, loader, self._active_cat, offset),
                         daemon=True).start()

    def _mods_fetch_worker(self, query, ver, loader, category, offset):
        results = self.dl.search_modrinth(
            query, "mod", MODS_PER_PAGE, offset,
            version=ver if ver else None,
            loader=loader if loader not in ("All", "", "Any") else None,
            category=category)
        hits  = results.get("hits", [])
        total = results.get("total_hits", len(hits))
        self._mods_hits  = hits
        self._mods_total = total
        self.root.after(0, self._mods_populate, hits, total)

    def _mods_populate(self, hits, total):
        self._mods_tree.delete(*self._mods_tree.get_children())
        for h in hits:
            dls    = h.get("downloads", 0)
            dl_fmt = f"{dls:,}" if dls < 1_000_000 else f"{dls/1_000_000:.1f}M"
            cats   = h.get("categories", [])
            loaders = ", ".join(c for c in cats if c in ("fabric","forge","quilt","neoforge"))[:20]
            self._mods_tree.insert("", "end", values=(
                "🔧", h.get("title","?"), h.get("author","?"),
                dl_fmt, h.get("date_modified","")[:10], loaders))
        n = len(hits)
        page = self._mods_page + 1
        total_pages = max(1, -(-total // MODS_PER_PAGE))
        self._page_lbl.config(text=f"Page {page} / {total_pages}")
        self._prev_btn.config(state="normal" if self._mods_page > 0 else "disabled")
        self._next_btn.config(state="normal" if page < total_pages else "disabled")
        self._mods_status.config(
            text=f"✓ {total:,} total mods — showing {(self._mods_page)*MODS_PER_PAGE+1}–{(self._mods_page)*MODS_PER_PAGE+n}",
            fg=C["text"] if n else C["yellow"])

    def _mods_prev_page(self):
        if self._mods_page > 0:
            self._mods_page -= 1
            self._mods_fetch()

    def _mods_next_page(self):
        total_pages = max(1, -(-self._mods_total // MODS_PER_PAGE))
        if self._mods_page + 1 < total_pages:
            self._mods_page += 1
            self._mods_fetch()

    def _mods_on_select(self, *_):
        sel = self._mods_tree.selection()
        if not sel or not self._mods_hits: return
        idx = self._mods_tree.index(sel[0])
        if idx >= len(self._mods_hits): return
        self._show_detail(self._mods_detail, self._mods_hits[idx], "mod",
                          self._mods_ver_var.get(), self._mods_ldr_var.get())

    # ─────────────────────────────────────────────────────────────────────────
    #  GENERIC CONTENT BROWSER
    # ─────────────────────────────────────────────────────────────────────────
    def _page_content_browser(self, page_id, title, subtitle, project_type):
        p = self._newpage(page_id)
        self._ptitle(p, title, subtitle)

        ib = tk.Frame(p, bg=C["panel"], highlightthickness=1, highlightbackground=C["border"],
                      padx=14, pady=7)
        ib.pack(fill="x", padx=22, pady=(0, 6))
        inst_lbl = tk.Label(ib, text="⚠  No instance selected",
                            font=FS, fg=C["yellow"], bg=C["panel"])
        inst_lbl.pack(side="left")
        setattr(self, f"_{page_id}_inst_lbl", inst_lbl)
        self._sbtn(ib, "📂 Open Folder",
                   lambda pt=project_type: self._open_content_folder(pt)).pack(side="right")

        sf = tk.Frame(p, bg=C["bg"]); sf.pack(fill="x", padx=22, pady=(0, 5))
        sv    = tk.StringVar()
        ver_v = tk.StringVar(value=self.mc_versions[0])
        ldr_v = tk.StringVar(value="Any")
        setattr(self, f"_{page_id}_ver_var", ver_v)
        setattr(self, f"_{page_id}_ldr_var", ldr_v)

        tk.Label(sf, text="🔍", font=F, fg=C["subtext"], bg=C["bg"]).pack(side="left", padx=(0, 3))
        se = tk.Entry(sf, textvariable=sv, font=F, bg=C["bg3"], fg=C["text"],
                      relief="flat", insertbackground=C["text"],
                      highlightthickness=1, highlightbackground=C["border"])
        se.pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 6))
        tk.Label(sf, text="Version:", font=FS, fg=C["subtext"], bg=C["bg"]).pack(side="left", padx=(0, 3))
        ttk.Combobox(sf, textvariable=ver_v, values=self.mc_versions,
                     font=FS, state="readonly", width=9).pack(side="left", padx=(0, 6))
        self._gbtn(sf, "🔍 Search",
                   lambda s=sv, v=ver_v, l=ldr_v, pt=project_type, pg=page_id:
                       self._generic_search(s.get(), v.get(), l.get(), pt, pg), 100).pack(side="left", padx=2)
        self._sbtn(sf, "🔥 Popular",
                   lambda v=ver_v, l=ldr_v, pt=project_type, pg=page_id:
                       self._generic_search("", v.get(), l.get(), pt, pg)).pack(side="left", padx=2)
        se.bind("<Return>",
                lambda e, s=sv, v=ver_v, l=ldr_v, pt=project_type, pg=page_id:
                    self._generic_search(s.get(), v.get(), l.get(), pt, pg))

        split = tk.Frame(p, bg=C["bg"])
        split.pack(fill="both", expand=True, padx=22, pady=(0, 4))

        left = tk.Frame(split, bg=C["bg"])
        left.pack(side="left", fill="both", expand=True)
        cols = ("icon", "name", "author", "downloads", "updated")
        tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for col, hd, w, anch in [
            ("icon","",28,"center"),("name","Name",230,"w"),
            ("author","Author",120,"w"),("downloads","⬇ DLs",90,"center"),
            ("updated","Updated",90,"center"),
        ]:
            tree.heading(col, text=hd); tree.column(col, width=w, anchor=anch, stretch=(col == "name"))
        tsb = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=tsb.set)
        tsb.pack(side="right", fill="y"); tree.pack(fill="both", expand=True)
        setattr(self, f"_{page_id}_tree", tree)
        setattr(self, f"_{page_id}_hits", [])

        right = tk.Frame(split, bg=C["panel"], width=340,
                         highlightthickness=1, highlightbackground=C["border"])
        right.pack(side="right", fill="y", padx=(8, 0))
        right.pack_propagate(False)
        setattr(self, f"_{page_id}_detail", right)
        self._detail_placeholder(right)

        bb = tk.Frame(p, bg=C["bg"]); bb.pack(fill="x", padx=22, pady=(0, 4))
        status = tk.Label(bb, text="Search above or click Popular",
                          font=FS, fg=C["subtext"], bg=C["bg"])
        status.pack(side="left")
        setattr(self, f"_{page_id}_status", status)
        prog = ttk.Progressbar(bb, style="DL.Horizontal.TProgressbar",
                               mode="determinate", length=180)
        prog.pack(side="right"); prog.pack_forget()
        setattr(self, f"_{page_id}_prog", prog)

        tree.bind("<<TreeviewSelect>>",
                  lambda e, pg=page_id, pt=project_type: self._generic_on_select(pg, pt))
        threading.Thread(
            target=lambda: self._generic_search("", self.mc_versions[0], "Any", project_type, page_id),
            daemon=True).start()

    def _generic_search(self, query, ver, loader, project_type, page_id):
        status = getattr(self, f"_{page_id}_status")
        status.config(text="Searching…", fg=C["subtext"])
        self._detail_placeholder(getattr(self, f"_{page_id}_detail"))
        threading.Thread(target=self._generic_search_worker,
                         args=(query, ver, loader, project_type, page_id), daemon=True).start()

    def _generic_search_worker(self, query, ver, loader, project_type, page_id):
        results = self.dl.search_modrinth(query, project_type, 40, 0,
                                          version=ver if ver else None,
                                          loader=loader if loader not in ("Any","All","") else None)
        hits = results.get("hits", [])
        setattr(self, f"_{page_id}_hits", hits)
        self.root.after(0, self._generic_populate, page_id, hits, project_type)

    def _generic_populate(self, page_id, hits, project_type):
        tree   = getattr(self, f"_{page_id}_tree")
        status = getattr(self, f"_{page_id}_status")
        tree.delete(*tree.get_children())
        icon = TYPE_ICONS.get(project_type, "📦")
        for h in hits:
            dls    = h.get("downloads", 0)
            dl_fmt = f"{dls:,}" if dls < 1_000_000 else f"{dls/1_000_000:.1f}M"
            tree.insert("", "end", values=(
                icon, h.get("title","?"), h.get("author","?"),
                dl_fmt, h.get("date_modified","")[:10]))
        n = len(hits)
        status.config(text=f"✓ {n} results — click to preview, then Install",
                      fg=C["text"] if n else C["yellow"])

    def _generic_on_select(self, page_id, project_type):
        tree = getattr(self, f"_{page_id}_tree")
        sel  = tree.selection()
        hits = getattr(self, f"_{page_id}_hits", [])
        if not sel or not hits: return
        idx = tree.index(sel[0])
        if idx >= len(hits): return
        panel = getattr(self, f"_{page_id}_detail")
        ver_v = getattr(self, f"_{page_id}_ver_var", None)
        ldr_v = getattr(self, f"_{page_id}_ldr_var", None)
        ver   = ver_v.get() if ver_v else ""
        ldr   = ldr_v.get() if ldr_v else "Any"
        self._show_detail(panel, hits[idx], project_type, ver, ldr)

    def _detail_placeholder(self, panel):
        for w in panel.winfo_children(): w.destroy()
        tk.Label(panel, text="📦", font=("Segoe UI Emoji", 32), bg=C["panel"]).pack(pady=(40, 8))
        tk.Label(panel, text="Click a result\nto see details",
                 font=F, fg=C["muted"], bg=C["panel"], justify="center").pack()

    # ─────────────────────────────────────────────────────────────────────────
    #  DETAIL PANEL + DIRECT INSTALL (no popup dialog)
    # ─────────────────────────────────────────────────────────────────────────
    def _show_detail(self, panel, hit, project_type, game_version="", loader=""):
        for w in panel.winfo_children(): w.destroy()
        icon = TYPE_ICONS.get(project_type, "📦")

        hdr = tk.Frame(panel, bg=C["panel2"], padx=12, pady=12); hdr.pack(fill="x")
        tk.Label(hdr, text=icon, font=("Segoe UI Emoji", 24), bg=C["panel2"]).pack()
        tk.Label(hdr, text=hit.get("title","?"), font=FB, fg=C["text"],
                 bg=C["panel2"], wraplength=320).pack(pady=(3, 1))
        tk.Label(hdr, text=f"by {hit.get('author','?')}",
                 font=FS, fg=C["subtext"], bg=C["panel2"]).pack()

        dls    = hit.get("downloads", 0)
        dl_fmt = f"{dls:,}" if dls < 1_000_000 else f"{dls/1_000_000:.1f}M"
        sr = tk.Frame(panel, bg=C["panel"], padx=10, pady=5); sr.pack(fill="x")
        for lbl, val in [("⬇", dl_fmt), ("❤", f"{hit.get('follows',0):,}"),
                         ("📅", hit.get("date_modified","")[:10])]:
            sf2 = tk.Frame(sr, bg=C["panel"]); sf2.pack(side="left", expand=True)
            tk.Label(sf2, text=lbl, font=("Segoe UI", 7), fg=C["muted"], bg=C["panel"]).pack()
            tk.Label(sf2, text=val, font=("Segoe UI", 9, "bold"), fg=C["text"], bg=C["panel"]).pack()

        cats    = hit.get("categories", [])
        loaders = [c for c in cats if c in ("fabric","forge","quilt","neoforge","iris","optifine")]
        tags    = [c for c in cats if c not in loaders]
        if loaders:
            lf = tk.Frame(panel, bg=C["panel"], padx=10, pady=2); lf.pack(fill="x")
            for ldr in loaders:
                b = tk.Frame(lf, bg=C["accent2"], padx=6, pady=1); b.pack(side="left", padx=2)
                tk.Label(b, text=ldr, font=("Segoe UI", 7, "bold"), fg=C["bg"], bg=C["accent2"]).pack()
        if tags:
            tf2 = tk.Frame(panel, bg=C["panel"], padx=10, pady=2); tf2.pack(fill="x")
            for tag in tags[:5]:
                tk.Label(tf2, text=tag, font=("Segoe UI", 7), fg=C["text"],
                         bg=C["bg3"], padx=4, pady=1).pack(side="left", padx=1)

        vers = sorted(set(hit.get("versions", [])), reverse=True)[:6]
        if vers:
            vf = tk.Frame(panel, bg=C["panel"], padx=10, pady=2); vf.pack(fill="x")
            tk.Label(vf, text="MC:", font=FS, fg=C["muted"], bg=C["panel"]).pack(side="left")
            tk.Label(vf, text="  ".join(vers), font=FM, fg=C["subtext"], bg=C["panel"],
                     wraplength=290).pack(side="left")

        desc = hit.get("description", "No description.")
        if len(desc) > 250: desc = desc[:250] + "…"
        df = tk.Frame(panel, bg=C["panel"], padx=10, pady=4); df.pack(fill="x")
        tk.Label(df, text=desc, font=FS, fg=C["subtext"], bg=C["panel"],
                 wraplength=318, justify="left").pack(anchor="w")

        tk.Frame(panel, bg=C["border"], height=1).pack(fill="x", padx=10, pady=5)

        vp = tk.Frame(panel, bg=C["panel"], padx=10, pady=3); vp.pack(fill="x")
        tk.Label(vp, text="Version to install:", font=FS, fg=C["subtext"], bg=C["panel"]).pack(anchor="w")
        ver_var = tk.StringVar(value="⏳ Loading versions…")
        ver_cb  = ttk.Combobox(vp, textvariable=ver_var, font=FS, state="readonly", width=40)
        ver_cb.pack(fill="x", pady=3)

        panel._hit             = hit
        panel._install_ver_var = ver_var
        panel._install_ver_cb  = ver_cb
        panel._project_type    = project_type

        # Status label replaces popup
        self._install_status_lbl = tk.Label(panel, text="", font=FS, fg=C["text"],
                                            bg=C["panel"], wraplength=320, justify="left")
        self._install_status_lbl.pack(fill="x", padx=10, pady=(0, 2))

        folder_name = CONTENT_FOLDERS.get(project_type, "mods")
        install_btn = tk.Button(panel,
                                text=f"⬇  INSTALL  {icon}  →  /{folder_name}/",
                                font=FB, fg=C["bg"], bg=C["text"],
                                activebackground=C["subtext"],
                                relief="flat", pady=10, cursor="hand2",
                                command=lambda: self._install_from_detail(panel))
        install_btn.pack(fill="x", padx=10, pady=4)

        self._sbtn(panel, "🌐 Open on Modrinth",
                   lambda s=hit.get("slug",""): webbrowser.open(
                       f"https://modrinth.com/project/{s}")).pack(fill="x", padx=10, pady=(0, 6))

        slug = hit.get("project_id") or hit.get("slug", "")
        threading.Thread(target=self._auto_load_versions,
                         args=(slug, game_version, loader, ver_var, ver_cb),
                         daemon=True).start()

    def _auto_load_versions(self, slug, game_version, loader, ver_var, ver_cb):
        if game_version or loader:
            ldr = loader if loader not in ("All","Any","") else None
            gv  = game_version if game_version else None
            vers = self.dl.get_compatible_version(slug, gv, ldr)
        else:
            vers = []
        if not vers:
            vers = self.dl.get_all_versions(slug)

        choices = []
        for v in vers:
            gvs  = ", ".join(sorted(v.get("game_versions", []))[-2:])
            ldrs = ", ".join(v.get("loaders", []))
            nm   = v.get("name") or v.get("version_number","?")
            choices.append(f"{nm}  [{gvs}]  [{ldrs}]")

        def upd():
            try:
                if choices:
                    ver_cb["values"] = choices
                    ver_var.set(choices[0])
                    ver_cb._version_entries = vers
                else:
                    ver_var.set("No compatible versions found")
            except Exception: pass
        self.root.after(0, upd)

    def _install_from_detail(self, panel):
        """Install directly — no popup dialog, status shown inline."""
        hit          = getattr(panel, "_hit", None)
        ver_cb       = getattr(panel, "_install_ver_cb", None)
        project_type = getattr(panel, "_project_type", "mod")
        if not hit or not ver_cb: return

        entries = getattr(ver_cb, "_version_entries", [])
        idx     = ver_cb.current()
        if not entries or idx < 0 or idx >= len(entries):
            self._install_status_lbl.config(
                text="⏳ Versions still loading — please wait a moment.", fg=C["yellow"])
            return

        ver_entry   = entries[idx]
        folder_name = CONTENT_FOLDERS.get(project_type, "mods")

        # Auto-pick or ask for instance
        if not self.sel_inst:
            if not self.instances:
                self._install_status_lbl.config(
                    text="⚠ No instances exist. Create one first.", fg=C["red"])
                return
            picked = self._pick_instance_dialog(hit.get("title","?"))
            if not picked: return

        inst        = self.sel_inst
        dest_folder = self.im.get_folder(inst["path"], folder_name)
        files       = ver_entry.get("files", [])
        if not files:
            self._install_status_lbl.config(text="✗ No files in this version.", fg=C["red"])
            return

        file_data = next((f for f in files if f.get("primary")), files[0])
        url       = file_data.get("url", "")
        filename  = file_data.get("filename",
                                  hit.get("title","file").replace(" ","_") + ".jar")
        dest      = dest_folder / filename

        # Direct install — just show inline status, no popup
        self._install_status_lbl.config(
            text=f"⬇ Downloading {hit.get('title','?')}…", fg=C["subtext"])

        page_id = {"mod":"mods","resourcepack":"resourcepacks",
                   "shader":"shaderpacks","datapack":"datapacks"}.get(project_type,"mods")
        prog    = getattr(self, f"_{page_id}_prog", None)
        status  = getattr(self, f"_{page_id}_status", getattr(self, "_mods_status", None))
        if prog: prog.pack(side="right"); prog.configure(value=0)
        if status: status.config(text=f"⬇ Downloading {hit.get('title','?')}…", fg=C["subtext"])

        threading.Thread(target=self._dl_worker,
                         args=(url, dest, hit.get("title","?"), folder_name, page_id, prog, status),
                         daemon=True).start()

    def _dl_worker(self, url, dest, name, folder_name, page_id, prog, status):
        def on_prog(pct):
            if prog: self.root.after(0, prog.configure, {"value": pct})
        ok = self.dl.download(url, dest, on_prog)
        self.root.after(0, self._dl_done, ok, name, dest, folder_name, page_id, prog, status)

    def _dl_done(self, ok, name, dest, folder_name, page_id, prog, status):
        if prog: prog.pack_forget(); prog.configure(value=0)
        if ok:
            if status: status.config(text=f"✓ '{name}' installed → /{folder_name}/", fg=C["text"])
            try:
                self._install_status_lbl.config(
                    text=f"✅ Installed! Saved to /{folder_name}/{dest.name}", fg=C["text"])
            except Exception: pass
        else:
            if status: status.config(text=f"✗ Download failed: {name}", fg=C["red"])
            try:
                self._install_status_lbl.config(
                    text="✗ Download failed. Check internet or try another version.", fg=C["red"])
            except Exception: pass

    def _pick_instance_dialog(self, mod_name):
        dlg = tk.Toplevel(self.root)
        dlg.title("Choose Instance"); dlg.configure(bg=C["bg2"])
        dlg.geometry("440x360"); dlg.resizable(False, False)
        dlg.transient(self.root); dlg.grab_set()
        tk.Label(dlg, text="Choose Instance", font=FL, fg=C["text"], bg=C["bg2"]).pack(pady=(14, 3))
        tk.Label(dlg, text=f"Where should '{mod_name}' go?",
                 font=FS, fg=C["subtext"], bg=C["bg2"]).pack(pady=(0, 8))
        chosen = [None]
        lb = tk.Listbox(dlg, bg=C["bg3"], fg=C["text"], font=F,
                        selectbackground=C["selected"], selectforeground=C["text"],
                        relief="flat", borderwidth=0, activestyle="none", height=9)
        lb.pack(fill="both", expand=True, padx=20, pady=4)
        for i in self.instances:
            lb.insert("end", f"  {i.get('icon','🎮')}  {i['name']}  [{i['version']} · {i.get('modloader','Vanilla')}]")
        def confirm():
            idx = lb.curselection()
            if not idx: messagebox.showwarning("DarxLauncher","Select an instance.", parent=dlg); return
            chosen[0] = self.instances[idx[0]]
            self._select_instance(chosen[0]); dlg.destroy()
        def new_inst():
            dlg.destroy(); self._new_instance_dialog()
        bf = tk.Frame(dlg, bg=C["bg2"]); bf.pack(fill="x", padx=20, pady=8)
        self._gbtn(bf, "Install Here", confirm, 165).pack(side="left", padx=(0, 6))
        self._sbtn(bf, "＋ New Instance", new_inst).pack(side="left")
        dlg.wait_window(); return chosen[0]

    def _open_content_folder(self, project_type):
        if not self.sel_inst:
            messagebox.showwarning("DarxLauncher","Select an instance first."); return
        folder = CONTENT_FOLDERS.get(project_type, "mods")
        self._open_path(str(self.im.get_folder(self.sel_inst["path"], folder)))

    # ─────────────────────────────────────────────────────────────────────────
    #  MODLOADER PAGE
    # ─────────────────────────────────────────────────────────────────────────
    def _page_modloader(self):
        p = self._newpage("modloader")
        self._ptitle(p, "🔩  MOD LOADER INSTALLER",
                     "Install Forge, Fabric, Quilt or NeoForge")

        ib = tk.Frame(p, bg=C["panel"], highlightthickness=1,
                      highlightbackground=C["border"], padx=14, pady=9)
        ib.pack(fill="x", padx=22, pady=(0, 8))
        tk.Label(ib, text="Target:", font=FS, fg=C["subtext"], bg=C["panel"]).pack(side="left")
        self._ml_inst_var = tk.StringVar(value="— select —")
        self._ml_inst_cb  = ttk.Combobox(ib, textvariable=self._ml_inst_var,
                                         font=F, state="readonly", width=32)
        self._ml_inst_cb.pack(side="left", padx=8)
        self._ml_inst_cb.bind("<<ComboboxSelected>>", self._ml_inst_changed)
        self._sbtn(ib, "🔄", self._refresh_ml_inst_list).pack(side="left")
        self._ml_inst_info = tk.Label(ib, text="", font=FS, fg=C["subtext"], bg=C["panel"])
        self._ml_inst_info.pack(side="right")
        self._current_ml_inst = None; self._ml_instances = []

        nb = ttk.Notebook(p); nb.pack(fill="both", expand=True, padx=22, pady=(0, 5))
        self._ml_tabs = {}
        for ml in ["Fabric","Forge","Quilt","NeoForge"]:
            tab = tk.Frame(nb, bg=C["bg3"]); nb.add(tab, text=f"  {ml}  ")
            self._build_ml_tab(tab, ml)

        lf = tk.Frame(p, bg=C["bg"]); lf.pack(fill="x", padx=22, pady=(0, 3))
        self._ml_prog_lbl = tk.Label(lf, text="", font=FS, fg=C["subtext"], bg=C["bg"])
        self._ml_prog_lbl.pack(side="left")
        self._ml_prog = ttk.Progressbar(lf, style="DL.Horizontal.TProgressbar",
                                        mode="determinate", length=240)
        self._ml_prog.pack(side="right")
        self._ml_log_box = tk.Text(p, height=5, font=FM, bg=C["bg2"], fg=C["text"],
                                   relief="flat", state="disabled", wrap="word")
        self._ml_log_box.pack(fill="x", padx=22, pady=(0, 12))
        self._refresh_ml_inst_list()

    def _build_ml_tab(self, tab, loader):
        descs = {
            "Fabric":   "Lightweight & fast. Best for performance mods (Sodium, Lithium, Iris).",
            "Forge":    "Most popular since 2011. Largest mod ecosystem.",
            "Quilt":    "Fabric fork with extra APIs. Compatible with most Fabric mods.",
            "NeoForge": "Modern Forge fork — best for MC 1.20.2+ modpacks.",
        }
        info = tk.Frame(tab, bg=C["panel"], padx=14, pady=10,
                        highlightthickness=1, highlightbackground=C["border"])
        info.pack(fill="x", padx=14, pady=10)
        tk.Label(info, text=loader, font=FL, fg=C["text"], bg=C["panel"]).pack(anchor="w")
        tk.Label(info, text=descs.get(loader,""), font=FS, fg=C["subtext"], bg=C["panel"]).pack(anchor="w")

        vf = tk.Frame(tab, bg=C["bg3"]); vf.pack(fill="x", padx=14, pady=3)
        tk.Label(vf, text=f"{loader} version:", font=FS, fg=C["subtext"],
                 bg=C["bg3"], width=16, anchor="w").pack(side="left", padx=8, pady=8)
        ver_v  = tk.StringVar(value="Select an instance above")
        ver_cb = ttk.Combobox(vf, textvariable=ver_v, font=F, state="readonly", width=30)
        ver_cb.pack(side="left", pady=8)
        key = loader.lower().replace(" ","")
        inst_lbl = tk.Label(tab, text="", font=FS, fg=C["text"], bg=C["bg3"])
        self._ml_tabs[key] = {"var": ver_v, "cb": ver_cb, "inst_lbl": inst_lbl}

        if loader == "Forge":
            tk.Label(tab, text="⚠  Forge installer requires Java 21.",
                     font=FS, fg=C["yellow"], bg=C["bg3"]).pack(padx=14, anchor="w")
        if loader == "NeoForge":
            tk.Label(tab, text="ℹ  NeoForge requires MC 1.20.2+.",
                     font=FS, fg=C["subtext"], bg=C["bg3"]).pack(padx=14, anchor="w")

        bf = tk.Frame(tab, bg=C["bg3"]); bf.pack(fill="x", padx=14, pady=10)
        self._gbtn(bf, f"⬇  Install {loader}",
                   lambda l=loader: self._do_ml_install(l), 200).pack(side="left")
        inst_lbl.pack(side="left", padx=12)

    def _refresh_ml_inst_list(self):
        insts = self.im.get_all()
        self._ml_instances = insts
        names = [f"{i['name']}  [{i['version']} · {i.get('modloader','?')}]" for i in insts]
        self._ml_inst_cb["values"] = names
        if self.sel_inst:
            for i, inst in enumerate(insts):
                if inst["name"] == self.sel_inst["name"]:
                    self._ml_inst_var.set(names[i])
                    self._ml_inst_cb.current(i)
                    self._ml_inst_changed(); break

    def _ml_inst_changed(self, *_):
        idx = self._ml_inst_cb.current()
        if idx < 0: return
        self._current_ml_inst = self._ml_instances[idx]
        inst = self._current_ml_inst
        self._ml_inst_info.config(text=f"MC {inst['version']}  ·  {inst.get('modloader','?')}")
        ml  = inst.get("modloader", "Vanilla")
        key = ml.lower().replace(" ","")
        if key in self._ml_tabs:
            threading.Thread(target=self._fetch_ml_versions_worker,
                             args=(ml, inst["version"], key), daemon=True).start()

    def _ml_preselect(self, name):
        self._refresh_ml_inst_list()
        for i, inst in enumerate(self._ml_instances):
            if inst["name"] == name:
                vals = self._ml_inst_cb["values"]
                if i < len(vals):
                    self._ml_inst_var.set(vals[i])
                    self._ml_inst_cb.current(i)
                    self._ml_inst_changed()
                break

    def _fetch_ml_versions_worker(self, loader, mc_ver, key):
        vers = []
        try:
            if loader == "Fabric":   vers = self.dl.fetch_fabric_loaders(mc_ver)
            elif loader == "Forge":  vers = self.dl.fetch_forge_versions(mc_ver)
            elif loader == "Quilt":  vers = self.dl.fetch_quilt_loaders(mc_ver)
            elif loader == "NeoForge": vers = self.dl.fetch_neoforge_versions(mc_ver)
        except Exception as e:
            self._ml_log(f"Error: {e}")
        def upd():
            d = self._ml_tabs.get(key)
            if not d: return
            if vers:
                d["cb"]["values"] = vers; d["var"].set(vers[0])
                self._ml_log(f"{loader}: {len(vers)} versions for MC {mc_ver}")
            else:
                d["var"].set("None found for this MC version")
                self._ml_log(f"No {loader} for MC {mc_ver}")
        self.root.after(0, upd)

    def _do_ml_install(self, loader):
        inst = self._current_ml_inst
        if not inst: messagebox.showwarning("DarxLauncher","Select a target instance first."); return
        key  = loader.lower().replace(" ","")
        d    = self._ml_tabs.get(key, {})
        ver  = d.get("var", tk.StringVar()).get()
        if not ver or "None" in ver or "Select" in ver:
            messagebox.showwarning("DarxLauncher","No version selected or loaded yet."); return
        if not messagebox.askyesno("Install",
                                   f"Install {loader} {ver} for MC {inst['version']}?\nInstance: {inst['name']}"): return
        self._ml_prog.configure(value=0)
        threading.Thread(target=self._ml_install_worker,
                         args=(loader, ver, inst, key), daemon=True).start()

    def _ml_install_worker(self, loader, lv, inst, key):
        java = getattr(self, "java_var", None)
        jp   = java.get() if java else self._find_java()
        log  = lambda m: self.root.after(0, self._ml_log, m)
        prog = lambda v: self.root.after(0, self._ml_prog.configure, {"value": v})
        installer = ModloaderInstaller(self.dl, log, prog)
        ok, res   = False, "Unknown"
        if loader == "Fabric":   ok, res = installer.install_fabric(inst["version"],lv,inst["path"])
        elif loader == "Forge":  ok, res = installer.install_forge(inst["version"],lv,jp,inst["path"])
        elif loader == "Quilt":  ok, res = installer.install_quilt(inst["version"],lv,inst["path"])
        elif loader == "NeoForge": ok, res = installer.install_neoforge(inst["version"],lv,jp,inst["path"])
        def done():
            lbl = self._ml_tabs.get(key,{}).get("inst_lbl")
            if ok:
                if lbl: lbl.config(text=f"✓ {loader} {lv} installed!", fg=C["text"])
                self.im.update_cfg(inst["path"],"loader_ver",lv)
                messagebox.showinfo("Done!", f"{loader} {lv} installed in '{inst['name']}'!")
            else:
                if lbl: lbl.config(text="✗ Failed", fg=C["red"])
                messagebox.showerror("Failed", f"Could not install {loader}.\n\n{res}")
        self.root.after(0, done)

    def _ml_log(self, msg):
        self._ml_log_box.config(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M:%S")
        self._ml_log_box.insert("end", f"[{ts}] {msg}\n")
        self._ml_log_box.see("end")
        self._ml_log_box.config(state="disabled")
        self._ml_prog_lbl.config(text=msg[:90])

    # ─────────────────────────────────────────────────────────────────────────
    #  SKIN EDITOR PAGE
    # ─────────────────────────────────────────────────────────────────────────
    def _page_skins(self):
        p = self._newpage("skins")
        self._ptitle(p, "👤  SKIN EDITOR",
                     "Draw your own skin pixel-by-pixel or upload a PNG — 64×64 Minecraft standard")

        # Split: left=skin list, right=editor
        body = tk.Frame(p, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=22, pady=(0, 12))

        # LEFT — saved skins panel
        left = tk.Frame(body, bg=C["panel"], width=200,
                        highlightthickness=1, highlightbackground=C["border"])
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)

        tk.Label(left, text="Saved Skins", font=FL, fg=C["text"], bg=C["panel"]).pack(pady=(10, 4))

        skin_list_frame = tk.Frame(left, bg=C["panel"])
        skin_list_frame.pack(fill="both", expand=True, padx=6)
        self._skin_listbox = tk.Listbox(skin_list_frame, bg=C["bg3"], fg=C["text"],
                                        font=FS, selectbackground=C["selected"],
                                        selectforeground=C["text"], relief="flat",
                                        borderwidth=0, activestyle="none")
        slsb = ttk.Scrollbar(skin_list_frame, orient="vertical",
                              command=self._skin_listbox.yview)
        self._skin_listbox.configure(yscrollcommand=slsb.set)
        slsb.pack(side="right", fill="y")
        self._skin_listbox.pack(fill="both", expand=True)
        self._skin_listbox.bind("<<ListboxSelect>>", self._load_selected_skin)

        btn_area = tk.Frame(left, bg=C["panel"])
        btn_area.pack(fill="x", padx=6, pady=6)
        tk.Button(btn_area, text="🗑 Delete", font=FS, bg=C["bg3"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  command=self._delete_selected_skin).pack(fill="x", pady=2)
        tk.Button(btn_area, text="＋ New Blank", font=FS, bg=C["bg3"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  command=self._new_blank_skin).pack(fill="x", pady=2)

        # RIGHT — editor
        right_frame = tk.Frame(body, bg=C["bg"])
        right_frame.pack(side="left", fill="both", expand=True)

        # Name input
        nf = tk.Frame(right_frame, bg=C["bg"]); nf.pack(fill="x", pady=(0, 4))
        tk.Label(nf, text="Skin Name:", font=FS, fg=C["subtext"], bg=C["bg"]).pack(side="left", padx=(0, 6))
        self._skin_name_var = tk.StringVar(value="My Skin")
        tk.Entry(nf, textvariable=self._skin_name_var, font=F,
                 bg=C["bg3"], fg=C["text"], relief="flat",
                 insertbackground=C["text"],
                 highlightthickness=1, highlightbackground=C["border"],
                 width=28).pack(side="left", ipady=4)

        def on_save(pixel_data):
            name = self._skin_name_var.get().strip() or "MySkin"
            self.sm.save_skin(name, pixel_data)
            self._reload_skin_list()
            messagebox.showinfo("Saved!", f"Skin '{name}' saved successfully!")

        self._skin_editor = SkinEditorWidget(right_frame, on_save=on_save, bg=C["bg"])
        self._skin_editor.pack(fill="both", expand=True)

        self._reload_skin_list()

    def _reload_skin_list(self):
        self._skin_listbox.delete(0, "end")
        self._saved_skins = self.sm.get_all()
        for s in self._saved_skins:
            self._skin_listbox.insert("end", f"  {s['name']}")

    def _load_selected_skin(self, *_):
        sel = self._skin_listbox.curselection()
        if not sel: return
        skin = self._saved_skins[sel[0]]
        self._skin_name_var.set(skin["name"])
        self._skin_editor.load_pixel_data(skin.get("pixels", {}))

    def _delete_selected_skin(self):
        sel = self._skin_listbox.curselection()
        if not sel: return
        skin = self._saved_skins[sel[0]]
        if messagebox.askyesno("Delete Skin", f"Delete '{skin['name']}'?"):
            self.sm.delete_skin(skin["safe"])
            self._reload_skin_list()

    def _new_blank_skin(self):
        self._skin_name_var.set("New Skin")
        self._skin_editor.pixels = {(x, y): None for x in range(64) for y in range(64)}
        self._skin_editor.canvas.delete("cell")
        self._skin_editor._update_preview()

    # ─────────────────────────────────────────────────────────────────────────
    #  MODPACKS PAGE
    # ─────────────────────────────────────────────────────────────────────────
    def _page_modpacks(self):
        p = self._newpage("modpacks")
        self._ptitle(p, "📦  MODPACKS",
                     "Create modpacks from your instances and share them with a code")

        body = tk.Frame(p, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=22, pady=(0, 12))

        # LEFT — existing packs
        left = tk.Frame(body, bg=C["panel"], width=320,
                        highlightthickness=1, highlightbackground=C["border"])
        left.pack(side="left", fill="both", padx=(0, 12))
        left.pack_propagate(False)

        tk.Label(left, text="Your Modpacks", font=FL, fg=C["text"], bg=C["panel"]).pack(pady=(10, 4))

        self._pack_listbox = tk.Listbox(left, bg=C["bg3"], fg=C["text"], font=FS,
                                        selectbackground=C["selected"], selectforeground=C["text"],
                                        relief="flat", borderwidth=0, activestyle="none", height=12)
        plsb = ttk.Scrollbar(left, orient="vertical", command=self._pack_listbox.yview)
        self._pack_listbox.configure(yscrollcommand=plsb.set)
        plsb.pack(side="right", fill="y", padx=(0, 4))
        self._pack_listbox.pack(fill="both", expand=True, padx=6)
        self._pack_listbox.bind("<<ListboxSelect>>", self._show_pack_detail)

        tk.Button(left, text="🗑 Delete Pack", font=FS, bg=C["bg3"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  command=self._delete_selected_pack).pack(fill="x", padx=6, pady=6)

        # RIGHT — create + import
        right = tk.Frame(body, bg=C["bg"])
        right.pack(side="left", fill="both", expand=True)

        # Create section
        create_card = self._scard(right, "CREATE MODPACK FROM INSTANCE")

        cf = tk.Frame(create_card, bg=C["panel"]); cf.pack(fill="x", pady=4)
        tk.Label(cf, text="Pack Name:", font=FS, fg=C["subtext"], bg=C["panel"],
                 width=14, anchor="w").pack(side="left")
        self._pack_name_var = tk.StringVar(value="My Modpack")
        tk.Entry(cf, textvariable=self._pack_name_var, font=F,
                 bg=C["bg3"], fg=C["text"], relief="flat",
                 insertbackground=C["text"]).pack(side="left", fill="x", expand=True, ipady=4)

        df2 = tk.Frame(create_card, bg=C["panel"]); df2.pack(fill="x", pady=4)
        tk.Label(df2, text="Description:", font=FS, fg=C["subtext"], bg=C["panel"],
                 width=14, anchor="w").pack(side="left")
        self._pack_desc_var = tk.StringVar(value="")
        tk.Entry(df2, textvariable=self._pack_desc_var, font=F,
                 bg=C["bg3"], fg=C["text"], relief="flat",
                 insertbackground=C["text"]).pack(side="left", fill="x", expand=True, ipady=4)

        instf = tk.Frame(create_card, bg=C["panel"]); instf.pack(fill="x", pady=4)
        tk.Label(instf, text="Instance:", font=FS, fg=C["subtext"], bg=C["panel"],
                 width=14, anchor="w").pack(side="left")
        self._pack_inst_var = tk.StringVar()
        self._pack_inst_cb  = ttk.Combobox(instf, textvariable=self._pack_inst_var,
                                           font=F, state="readonly", width=28)
        self._pack_inst_cb.pack(side="left")

        self._pack_code_lbl = tk.Label(create_card, text="", font=("Consolas", 14, "bold"),
                                       fg=C["text"], bg=C["panel"])
        self._pack_code_lbl.pack(pady=4)

        def create_pack():
            name = self._pack_name_var.get().strip()
            desc = self._pack_desc_var.get().strip()
            if not name:
                messagebox.showwarning("Modpacks","Enter a pack name."); return
            idx = self._pack_inst_cb.current()
            if idx < 0 or not self.instances:
                messagebox.showwarning("Modpacks","Select an instance."); return
            inst = self.instances[idx]
            mods = self.mpm.get_mods_from_instance(inst["path"])
            code, data = self.mpm.create_modpack(name, desc, inst["path"], mods)
            self._pack_code_lbl.config(
                text=f"🎉 Pack Code: {code}  ({len(mods)} mods)")
            self._reload_pack_list()

        self._gbtn(create_card, "📦 Create Modpack", create_pack, 200).pack(anchor="w", pady=8)

        # Import section
        import_card = self._scard(right, "IMPORT MODPACK BY CODE")

        imf = tk.Frame(import_card, bg=C["panel"]); imf.pack(fill="x", pady=4)
        tk.Label(imf, text="Enter Code:", font=FS, fg=C["subtext"], bg=C["panel"],
                 width=14, anchor="w").pack(side="left")
        self._import_code_var = tk.StringVar()
        tk.Entry(imf, textvariable=self._import_code_var, font=("Consolas",11),
                 bg=C["bg3"], fg=C["text"], relief="flat",
                 insertbackground=C["text"]).pack(side="left", fill="x", expand=True, ipady=4)

        self._import_result_lbl = tk.Label(import_card, text="", font=FS,
                                           fg=C["subtext"], bg=C["panel"], wraplength=500)
        self._import_result_lbl.pack(pady=4, anchor="w")

        def import_pack():
            code = self._import_code_var.get().strip()
            data = self.mpm.import_modpack(code)
            if data:
                mods = data.get("mods", [])
                self._import_result_lbl.config(
                    text=f"✅ Found: '{data['name']}' — {len(mods)} mods\n"
                         f"Description: {data.get('description','')}\n"
                         f"Mods: {', '.join(mods[:6])}{'…' if len(mods)>6 else ''}",
                    fg=C["text"])
                self._reload_pack_list()
            else:
                self._import_result_lbl.config(
                    text="✗ Code not found. Make sure the code is correct (format: DX-XXXXXXXX)\n"
                         "Note: the modpack creator must be on the same machine or share their ~/.darxlauncher/modpacks/ folder.",
                    fg=C["red"])

        self._gbtn(import_card, "📥 Import Modpack", import_pack, 200).pack(anchor="w", pady=8)

        # Pack detail label
        self._pack_detail_lbl = tk.Label(right, text="", font=FS, fg=C["subtext"],
                                         bg=C["bg"], justify="left", wraplength=500)
        self._pack_detail_lbl.pack(anchor="w", padx=4, pady=8)

        self._reload_pack_list()

    def _reload_pack_list(self):
        self._pack_listbox.delete(0, "end")
        self._all_packs = self.mpm.get_all()
        for pack in self._all_packs:
            self._pack_listbox.insert("end", f"  {pack['name']}  [{pack['code']}]")
        # Refresh instance dropdown
        insts = self.im.get_all()
        self.instances = insts
        self._pack_inst_cb["values"] = [f"{i['name']} [{i['version']}]" for i in insts]

    def _show_pack_detail(self, *_):
        sel = self._pack_listbox.curselection()
        if not sel: return
        pack = self._all_packs[sel[0]]
        mods = pack.get("mods", [])
        self._pack_detail_lbl.config(
            text=f"Name: {pack['name']}\nCode: {pack['code']}\n"
                 f"Created: {pack.get('created','?')}\n"
                 f"Description: {pack.get('description','')}\n"
                 f"Mods ({len(mods)}): {', '.join(mods[:10])}{'…' if len(mods)>10 else ''}")

    def _delete_selected_pack(self):
        sel = self._pack_listbox.curselection()
        if not sel: return
        pack = self._all_packs[sel[0]]
        if messagebox.askyesno("Delete Pack", f"Delete '{pack['name']}'?"):
            f = MODPACKS_DIR / f"{pack['code']}.json"
            if f.exists(): f.unlink()
            self._reload_pack_list()

    # ─────────────────────────────────────────────────────────────────────────
    #  SETTINGS PAGE  (expanded)
    # ─────────────────────────────────────────────────────────────────────────
    def _page_settings(self):
        p = self._newpage("settings")
        self._ptitle(p, "⚙  SETTINGS", "Configure DarxLauncher")

        # Scrollable settings
        outer = tk.Frame(p, bg=C["bg"])
        outer.pack(fill="both", expand=True)
        sc = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        ssb = ttk.Scrollbar(outer, orient="vertical", command=sc.yview)
        self._settings_inner = tk.Frame(sc, bg=C["bg"])
        self._settings_inner.bind("<Configure>",
                                  lambda e: sc.configure(scrollregion=sc.bbox("all")))
        sc.create_window((0, 0), window=self._settings_inner, anchor="nw")
        sc.configure(yscrollcommand=ssb.set)
        ssb.pack(side="right", fill="y")
        sc.pack(fill="both", expand=True)
        si = self._settings_inner

        # ── Microsoft Account ─────────────────────────────────────────────────
        s_acct = self._scard(si, "MICROSOFT ACCOUNT")
        tk.Label(s_acct,
                 text="Sign in with your Microsoft / Mojang account to play on online-mode servers.\n"
                      "Without login, you can only join servers with online-mode=false.",
                 font=FS, fg=C["subtext"], bg=C["panel"], justify="left").pack(anchor="w", pady=(0,6))
        acct_row = tk.Frame(s_acct, bg=C["panel"]); acct_row.pack(fill="x", pady=4)
        self._settings_acct_lbl = tk.Label(acct_row, text="", font=FB,
                                            fg=C["subtext"], bg=C["panel"])
        self._settings_acct_lbl.pack(side="left")
        def _refresh_settings_acct():
            auth = self._auth
            if auth and auth.get("username"):
                self._settings_acct_lbl.config(
                    text=f"✅ Logged in as: {auth['username']}  (UUID: {auth.get('uuid','-')})",
                    fg=C["green"])
            else:
                self._settings_acct_lbl.config(text="⚠  Not logged in — offline mode",
                                                fg=C["yellow"])
        _refresh_settings_acct()
        btn_row = tk.Frame(s_acct, bg=C["panel"]); btn_row.pack(anchor="w", pady=6)
        self._gbtn(btn_row, "🔑 Sign in with Microsoft",
                   lambda: (self._msa_login(), self.root.after(3000, _refresh_settings_acct)),
                   220, C["blue"]).pack(side="left", padx=(0,8))
        self._sbtn(btn_row, "🚪 Sign Out",
                   lambda: (self._msa_logout(), _refresh_settings_acct())).pack(side="left")

        # ── Java ──────────────────────────────────────────────────────────────
        s1 = self._scard(si, "JAVA SETTINGS")
        jr = tk.Frame(s1, bg=C["panel"]); jr.pack(fill="x", pady=4)
        tk.Label(jr, text="Java Path:", font=FS, fg=C["subtext"],
                 bg=C["panel"], width=16, anchor="w").pack(side="left")
        self.java_var = tk.StringVar(value=self._find_java())
        tk.Entry(jr, textvariable=self.java_var, font=FM,
                 bg=C["bg3"], fg=C["text"], relief="flat",
                 insertbackground=C["text"]).pack(side="left", fill="x", expand=True, ipady=5)
        self._sbtn(jr, "Browse",       self._browse_java).pack(side="left", padx=5)
        self._sbtn(jr, "Auto-detect",  self._autodetect_java).pack(side="left", padx=3)

        jr2 = tk.Frame(s1, bg=C["panel"]); jr2.pack(fill="x", pady=4)
        tk.Label(jr2, text="", bg=C["panel"], width=16).pack(side="left")
        self._java_ver_lbl = tk.Label(jr2, text="(not tested)", font=FS, fg=C["subtext"], bg=C["panel"])
        self._java_ver_lbl.pack(side="left")
        self._sbtn(jr2, "🔍 Test Java", self._test_java).pack(side="left", padx=10)

        # ── RAM ───────────────────────────────────────────────────────────────
        s_ram = self._scard(si, "RAM ALLOCATION")

        rr = tk.Frame(s_ram, bg=C["panel"]); rr.pack(fill="x", pady=4)
        tk.Label(rr, text="Default RAM for new instances:", font=FS, fg=C["subtext"],
                 bg=C["panel"], width=28, anchor="w").pack(side="left")
        self.def_ram = tk.IntVar(value=self.settings.get("default_ram", 2))
        tk.Scale(rr, variable=self.def_ram, from_=1, to=32, orient="horizontal",
                 bg=C["panel"], fg=C["text"], highlightthickness=0,
                 troughcolor=C["bg3"], length=220).pack(side="left")
        tk.Label(rr, textvariable=self.def_ram, font=FB, fg=C["text"], bg=C["panel"]).pack(side="left", padx=4)
        tk.Label(rr, text="GB", font=FS, fg=C["subtext"], bg=C["panel"]).pack(side="left")

        tk.Label(s_ram, text="Tip: 2 GB is fine for vanilla. 4–6 GB for modpacks. 8+ GB for large packs.",
                 font=FS, fg=C["muted"], bg=C["panel"]).pack(anchor="w", pady=(0, 4))

        if self.sel_inst:
            ir = tk.Frame(s_ram, bg=C["panel"]); ir.pack(fill="x", pady=4)
            tk.Label(ir, text=f"Current instance RAM  ({self.sel_inst['name']}):", font=FS,
                     fg=C["subtext"], bg=C["panel"], width=28, anchor="w").pack(side="left")
            self._inst_ram_var = tk.IntVar(value=self.sel_inst.get("ram", 2))
            tk.Scale(ir, variable=self._inst_ram_var, from_=1, to=32, orient="horizontal",
                     bg=C["panel"], fg=C["text"], highlightthickness=0,
                     troughcolor=C["bg3"], length=220).pack(side="left")
            tk.Label(ir, textvariable=self._inst_ram_var, font=FB, fg=C["text"], bg=C["panel"]).pack(side="left", padx=4)
            tk.Label(ir, text="GB", font=FS, fg=C["subtext"], bg=C["panel"]).pack(side="left")
            def save_inst_ram():
                if self.sel_inst:
                    self.im.update_cfg(self.sel_inst["path"], "ram", self._inst_ram_var.get())
                    messagebox.showinfo("Saved", f"RAM set to {self._inst_ram_var.get()} GB for '{self.sel_inst['name']}'")
            self._gbtn(s_ram, "💾 Save RAM for Instance", save_inst_ram, 220).pack(anchor="w", pady=4)

        # ── Appearance ────────────────────────────────────────────────────────
        s_app = self._scard(si, "APPEARANCE")
        thf = tk.Frame(s_app, bg=C["panel"]); thf.pack(fill="x", pady=4)
        tk.Label(thf, text="Theme:", font=FS, fg=C["subtext"], bg=C["panel"],
                 width=16, anchor="w").pack(side="left")
        self._theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))

        def toggle_theme():
            new = "light" if self._theme_var.get() == "dark" else "dark"
            self._theme_var.set(new)
            C.update(LIGHT_THEME if new == "light" else DARK_THEME)
            self.settings["theme"] = new
            save_settings(self.settings)
            messagebox.showinfo("Theme Changed",
                                f"Switched to {new.title()} Mode.\nRestart the launcher to fully apply.")
        self._gbtn(thf, "🌓 Toggle Light/Dark", toggle_theme, 200).pack(side="left")
        tk.Label(thf, text="(Restart required to fully apply)", font=("Segoe UI", 8),
                 fg=C["muted"], bg=C["panel"]).pack(side="left", padx=8)

        # ── Game Window ───────────────────────────────────────────────────────
        s_win = self._scard(si, "GAME WINDOW")
        def row_s(parent, label, var, min_v, max_v, w=120):
            f = tk.Frame(parent, bg=C["panel"]); f.pack(fill="x", pady=3)
            tk.Label(f, text=label, font=FS, fg=C["subtext"], bg=C["panel"],
                     width=16, anchor="w").pack(side="left")
            tk.Scale(f, variable=var, from_=min_v, to=max_v, orient="horizontal",
                     bg=C["panel"], fg=C["text"], highlightthickness=0,
                     troughcolor=C["bg3"], length=w).pack(side="left")
            tk.Label(f, textvariable=var, font=FS, fg=C["text"], bg=C["panel"]).pack(side="left", padx=4)

        self._gw_var = tk.IntVar(value=self.settings.get("game_width", 854))
        self._gh_var = tk.IntVar(value=self.settings.get("game_height", 480))
        row_s(s_win, "Width:", self._gw_var, 640, 3840, 240)
        row_s(s_win, "Height:", self._gh_var, 480, 2160, 240)
        self._fs_var = tk.BooleanVar(value=self.settings.get("fullscreen", False))
        tk.Checkbutton(s_win, text="Launch in Fullscreen", variable=self._fs_var,
                       font=FS, fg=C["text"], bg=C["panel"],
                       activebackground=C["panel"], selectcolor=C["bg3"]).pack(anchor="w", pady=3)

        # ── JVM Arguments ─────────────────────────────────────────────────────
        s_jvm = self._scard(si, "JVM ARGUMENTS")
        tk.Label(s_jvm, text="Extra JVM flags (advanced users):", font=FS,
                 fg=C["subtext"], bg=C["panel"]).pack(anchor="w")
        self._jvm_var = tk.StringVar(value=self.settings.get("jvm_args",""))
        tk.Entry(s_jvm, textvariable=self._jvm_var, font=FM,
                 bg=C["bg3"], fg=C["text"], relief="flat",
                 insertbackground=C["text"]).pack(fill="x", ipady=5, pady=4)
        tk.Label(s_jvm,
                 text="Example: -XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions",
                 font=("Segoe UI", 8), fg=C["muted"], bg=C["panel"]).pack(anchor="w")

        # ── Launcher Options ──────────────────────────────────────────────────
        s_opts = self._scard(si, "LAUNCHER OPTIONS")
        self._tray_var   = tk.BooleanVar(value=self.settings.get("close_to_tray", False))
        self._update_var = tk.BooleanVar(value=self.settings.get("auto_update", True))
        self._rpc_var    = tk.BooleanVar(value=self.settings.get("discord_rpc", False))
        for text, var in [
            ("Close to tray instead of quitting", self._tray_var),
            ("Auto-check for launcher updates",   self._update_var),
            ("Enable Discord Rich Presence",       self._rpc_var),
        ]:
            tk.Checkbutton(s_opts, text=text, variable=var,
                           font=FS, fg=C["text"], bg=C["panel"],
                           activebackground=C["panel"], selectcolor=C["bg3"]).pack(anchor="w", pady=2)

        # Language
        lanf = tk.Frame(s_opts, bg=C["panel"]); lanf.pack(fill="x", pady=6)
        tk.Label(lanf, text="Language:", font=FS, fg=C["subtext"], bg=C["panel"],
                 width=12, anchor="w").pack(side="left")
        self._lang_var = tk.StringVar(value=self.settings.get("language","English"))
        ttk.Combobox(lanf, textvariable=self._lang_var,
                     values=["English","Español","Français","Deutsch","Português","日本語","中文"],
                     font=FS, state="readonly", width=16).pack(side="left")

        # Screenshot folder
        ssf = tk.Frame(s_opts, bg=C["panel"]); ssf.pack(fill="x", pady=4)
        tk.Label(ssf, text="Screenshot Folder:", font=FS, fg=C["subtext"], bg=C["panel"],
                 width=18, anchor="w").pack(side="left")
        self._ss_var = tk.StringVar(value=self.settings.get("screenshot_folder",""))
        tk.Entry(ssf, textvariable=self._ss_var, font=FM,
                 bg=C["bg3"], fg=C["text"], relief="flat",
                 insertbackground=C["text"]).pack(side="left", fill="x", expand=True, ipady=4)
        tk.Button(ssf, text="Browse", font=FS, bg=C["bg3"], fg=C["text"],
                  relief="flat", cursor="hand2",
                  command=lambda: self._ss_var.set(
                      filedialog.askdirectory(title="Screenshots folder") or self._ss_var.get()
                  )).pack(side="left", padx=4)

        # ── In-Game Keybinds ──────────────────────────────────────────────────
        s_kb = self._scard(si, "IN-GAME KEYBINDS  (applied to every instance on launch)")
        tk.Label(s_kb,
                 text="These keybinds will be written to options.txt in each instance when you press Play.\n"
                      "Use Minecraft key names: key.keyboard.w, key.keyboard.space, key.mouse.left, etc.",
                 font=("Segoe UI", 8), fg=C["muted"], bg=C["panel"], justify="left").pack(anchor="w", pady=(0,6))

        # Minecraft options.txt key names
        KB_DEFAULTS = [
            ("Forward",        "key_key.keyboard.w",          "key.keyboard.w"),
            ("Back",           "key_key.keyboard.s",          "key.keyboard.s"),
            ("Left",           "key_key.keyboard.a",          "key.keyboard.a"),
            ("Right",          "key_key.keyboard.d",          "key.keyboard.d"),
            ("Jump",           "key_key.keyboard.space",      "key.keyboard.space"),
            ("Sneak",          "key_key.keyboard.left.shift", "key.keyboard.left.shift"),
            ("Sprint",         "key_key.keyboard.left.control","key.keyboard.left.control"),
            ("Attack/Destroy", "key_key.mouse.left",          "key.mouse.left"),
            ("Use/Place",      "key_key.mouse.right",         "key.mouse.right"),
            ("Drop Item",      "key_key.keyboard.q",          "key.keyboard.q"),
            ("Inventory",      "key_key.keyboard.e",          "key.keyboard.e"),
            ("Chat",           "key_key.keyboard.t",          "key.keyboard.t"),
            ("Command",        "key_key.keyboard.slash",      "key.keyboard.slash"),
            ("Perspective",    "key_key.keyboard.f5",         "key.keyboard.f5"),
            ("Screenshot",     "key_key.keyboard.f2",         "key.keyboard.f2"),
            ("Fullscreen",     "key_key.keyboard.f11",        "key.keyboard.f11"),
            ("Swap Hands",     "key_key.keyboard.f",          "key.keyboard.f"),
            ("Advancements",   "key_key.keyboard.l",          "key.keyboard.l"),
            ("Highlight Players","key_key.keyboard.tab",      "key.keyboard.tab"),
            ("Slot 1",         "key_key.keyboard.1",          "key.keyboard.1"),
            ("Slot 2",         "key_key.keyboard.2",          "key.keyboard.2"),
            ("Slot 3",         "key_key.keyboard.3",          "key.keyboard.3"),
            ("Slot 4",         "key_key.keyboard.4",          "key.keyboard.4"),
            ("Slot 5",         "key_key.keyboard.5",          "key.keyboard.5"),
        ]

        self._keybind_vars = {}
        # Load saved keybinds from settings
        saved_kb = self.settings.get("keybinds", {})

        # 3-column grid layout
        kb_grid = tk.Frame(s_kb, bg=C["panel"])
        kb_grid.pack(fill="x")
        col_count = 3
        for idx, (label, opt_key, default) in enumerate(KB_DEFAULTS):
            row = idx // col_count
            col = idx % col_count
            cell = tk.Frame(kb_grid, bg=C["panel"], padx=4, pady=2)
            cell.grid(row=row, column=col, sticky="ew", padx=4)
            tk.Label(cell, text=label, font=("Segoe UI", 8), fg=C["subtext"],
                     bg=C["panel"], width=14, anchor="w").pack(side="left")
            var = tk.StringVar(value=saved_kb.get(opt_key, default))
            self._keybind_vars[opt_key] = var
            entry = tk.Entry(cell, textvariable=var, font=("Consolas", 8),
                             bg=C["bg3"], fg=C["text"], relief="flat",
                             insertbackground=C["text"], width=22)
            entry.pack(side="left", ipady=3)
        for c in range(col_count):
            kb_grid.columnconfigure(c, weight=1)

        def reset_keybinds():
            for label, opt_key, default in KB_DEFAULTS:
                if opt_key in self._keybind_vars:
                    self._keybind_vars[opt_key].set(default)
        self._sbtn(s_kb, "↺ Reset to Defaults", reset_keybinds).pack(anchor="w", pady=(8,0))

        tk.Label(s_kb,
                 text="💡 Tip: After saving, these apply on next Play. You can still change them in-game.",
                 font=("Segoe UI", 8), fg=C["blue"], bg=C["panel"]).pack(anchor="w", pady=(4,0))

        # Save button
        def save_all():
            self.settings.update({
                "default_ram":    self.def_ram.get(),
                "theme":          self._theme_var.get(),
                "game_width":     self._gw_var.get(),
                "game_height":    self._gh_var.get(),
                "fullscreen":     self._fs_var.get(),
                "jvm_args":       self._jvm_var.get(),
                "close_to_tray":  self._tray_var.get(),
                "auto_update":    self._update_var.get(),
                "discord_rpc":    self._rpc_var.get(),
                "language":       self._lang_var.get(),
                "screenshot_folder": self._ss_var.get(),
                "keybinds":       {k: v.get() for k, v in self._keybind_vars.items()} if hasattr(self, "_keybind_vars") else {},
            })
            save_settings(self.settings)
            messagebox.showinfo("Settings Saved", "All settings saved! Keybinds will apply on next launch.")
        self._gbtn(si, "💾  SAVE ALL SETTINGS", save_all, 220).pack(pady=12, padx=22)

        # ── Folders ───────────────────────────────────────────────────────────
        s2 = self._scard(si, "FOLDERS")
        for lbl, path in [("Launcher data:", str(LAUNCHER_DIR)),
                           ("Instances:",     str(INSTANCES)),
                           ("Versions:",      str(VERSIONS_DIR)),
                           ("Skins:",         str(SKINS_DIR)),
                           ("Modpacks:",      str(MODPACKS_DIR))]:
            rf = tk.Frame(s2, bg=C["panel"]); rf.pack(fill="x", pady=3)
            tk.Label(rf, text=lbl, font=FS, fg=C["subtext"], bg=C["panel"],
                     width=16, anchor="w").pack(side="left")
            tk.Label(rf, text=path, font=FM, fg=C["text"], bg=C["panel"]).pack(side="left")
            self._sbtn(rf, "📂 Open", lambda pth=path: self._open_path(pth)).pack(side="right")

        # ── Java Download ─────────────────────────────────────────────────────
        s3 = self._scard(si, "JAVA DOWNLOAD")
        tk.Label(s3, text="MC 1.17+ needs Java 17+.  MC 1.21+ needs Java 21.",
                 font=FS, fg=C["subtext"], bg=C["panel"]).pack(anchor="w")
        bf = tk.Frame(s3, bg=C["panel"]); bf.pack(anchor="w", pady=6)
        self._gbtn(bf, "⬇ Java 21",
                   lambda: webbrowser.open("https://adoptium.net/temurin/releases/?version=21"),
                   180).pack(side="left", padx=(0, 8))
        self._gbtn(bf, "⬇ Java 17",
                   lambda: webbrowser.open("https://adoptium.net/temurin/releases/?version=17"),
                   160).pack(side="left")

        # ── About ─────────────────────────────────────────────────────────────
        s4 = self._scard(si, "ABOUT")
        tk.Label(s4, justify="left", font=FS, fg=C["subtext"], bg=C["panel"], text=(
            f"DarxLauncher v{VERSION}  —  Free & open-source Minecraft launcher\n\n"
            "• Java & Bedrock, Forge, Fabric, Quilt, NeoForge\n"
            "• Live Modrinth mod browser — paginated, no 50-mod cap\n"
            "• Skin Editor — pixel art brush, color picker, live preview, PNG import\n"
            "• Modpack creator — share packs with codes\n"
            "• 1-click install — no popups\n"
            "• Settings — RAM, JVM args, window size, theme, language\n"
            "• Light Mode / Dark Mode\n"
        )).pack(anchor="w")

    # ─────────────────────────────────────────────────────────────────────────
    #  LAUNCH
    # ─────────────────────────────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────────────────────
    #  MICROSOFT ACCOUNT  UI
    # ─────────────────────────────────────────────────────────────────────────
    def _update_acct_badge(self):
        auth = self._auth
        if auth and auth.get("username"):
            self._acct_lbl.config(
                text=f"✅ {auth['username']}", fg=C["green"])
            if hasattr(self, "_sidebar_acct_lbl"):
                self._sidebar_acct_lbl.config(
                    text=f"🟢 {auth['username']}", fg=C["green"])
            if hasattr(self, "_acct_page_status"):
                self._acct_page_status.config(
                    text=f"✅ Logged in as {auth['username']}", fg=C["green"])
        else:
            self._acct_lbl.config(text="⚠ Not logged in", fg=C["yellow"])
            if hasattr(self, "_sidebar_acct_lbl"):
                self._sidebar_acct_lbl.config(
                    text="🎮 Offline Mode", fg=C["muted"])
            if hasattr(self, "_acct_page_status"):
                self._acct_page_status.config(
                    text="⚠ Not logged in — Offline Mode", fg=C["yellow"])

    def _msa_login(self):
        """
        Blueprint §3 — full_login_flow() wrapped in a Tkinter dialog.
        Shows user_code and verification_uri; polls in background thread.
        On success saves auth.json via _save_auth() and updates UI.
        """
        import threading as _th
        import webbrowser as _wb

        dlg = tk.Toplevel(self.root)
        dlg.title("Sign In with Microsoft — DarxLauncher")
        dlg.configure(bg=C["bg2"])
        dlg.geometry("480x510")
        dlg.resizable(False, False)
        dlg.transient(self.root)
        dlg.grab_set()

        # Header
        hdr = tk.Frame(dlg, bg="#107c10", pady=18); hdr.pack(fill="x")
        tk.Label(hdr, text="🎮", font=("Segoe UI Emoji", 26), bg="#107c10").pack()
        tk.Label(hdr, text="Sign In with Microsoft",
                 font=("Segoe UI", 14, "bold"), fg="white", bg="#107c10").pack()
        tk.Label(hdr, text="Secure Device Code Flow — no password stored",
                 font=FS, fg="#bbffbb", bg="#107c10").pack(pady=(2, 0))

        body = tk.Frame(dlg, bg=C["bg2"], padx=32)
        body.pack(fill="both", expand=True, pady=10)

        status_lbl = tk.Label(body, text="⏳ Connecting to Microsoft…",
                              font=("Segoe UI", 10, "bold"), fg=C["yellow"],
                              bg=C["bg2"], wraplength=400, justify="center")
        status_lbl.pack(pady=(8, 4))

        # Code display card
        card = tk.Frame(body, bg=C["panel"], pady=16, padx=16,
                        highlightthickness=1, highlightbackground=C["border"])
        card.pack(fill="x", pady=6)

        tk.Label(card, text="STEP 1 — Open this URL in any browser:",
                 font=("Segoe UI", 8, "bold"), fg=C["muted"], bg=C["panel"]).pack(anchor="w")
        url_lbl = tk.Label(card, text="microsoft.com/link",
                           font=("Segoe UI", 12, "bold"), fg=C["blue"],
                           bg=C["panel"], cursor="hand2")
        url_lbl.pack(pady=(2, 10))
        url_lbl.bind("<Button-1>", lambda e: _wb.open("https://microsoft.com/link"))

        tk.Label(card, text="STEP 2 — Enter this code (click to select, Ctrl+C to copy):",
                 font=("Segoe UI", 8, "bold"), fg=C["muted"], bg=C["panel"]).pack(anchor="w")

        # Use a read-only Entry so the user can click to select and copy normally
        code_var = tk.StringVar(value="Loading…")
        code_entry = tk.Entry(card, textvariable=code_var,
                              font=("Consolas", 28, "bold"),
                              fg=C["text"], bg=C["panel"],
                              relief="flat", justify="center",
                              readonlybackground=C["panel"],
                              state="readonly",
                              width=12)
        code_entry.pack(pady=(4, 6), fill="x")

        # Clicking the entry selects all so Ctrl+C works immediately
        def _select_all(e):
            code_entry.select_range(0, "end")
            code_entry.icursor("end")
        code_entry.bind("<Button-1>", _select_all)
        code_entry.bind("<FocusIn>",  _select_all)

        # Keep code_lbl as an alias so the rest of the code still works
        class _CodeLbl:
            def config(self, **kw):
                if "text" in kw:
                    code_var.set(kw["text"])
                    # Also auto-copy to clipboard when code arrives
                    try:
                        dlg.clipboard_clear()
                        dlg.clipboard_append(kw["text"])
                    except Exception:
                        pass
            def cget(self, key):
                return code_var.get() if key == "text" else ""
        code_lbl = _CodeLbl()

        copy_btn = tk.Button(card, text="📋  Copy Code to Clipboard",
                             font=FS, bg=C["bg3"], fg=C["text"],
                             relief="flat", pady=4, cursor="hand2")

        open_btn = tk.Button(body,
                             text="🌐  Open Browser",
                             font=("Segoe UI", 11, "bold"),
                             fg="white", bg="#107c10",
                             activebackground="#0e6b0e",
                             relief="flat", pady=11, cursor="hand2",
                             state="disabled")
        open_btn.pack(fill="x", pady=(8, 4))

        tk.Frame(body, bg=C["border"], height=1).pack(fill="x", pady=8)

        def _go_offline():
            stop_ev.set(); dlg.destroy(); self._offline_quick_login()

        tk.Button(body, text="🎮  Play Offline / Cracked instead",
                  font=FS, fg=C["subtext"], bg=C["bg3"],
                  relief="flat", pady=7, cursor="hand2",
                  command=_go_offline).pack(fill="x")

        stop_ev = _th.Event()

        def _set_status(msg, col=None):
            if dlg.winfo_exists():
                dlg.after(0, lambda m=msg, c=col: status_lbl.config(
                    text=m, fg=c or C["subtext"]))

        def _auth_worker():
            try:
                # Step 1 — device code
                _set_status("⏳ Requesting code from Microsoft…", C["yellow"])
                dc = start_device_code_flow()
                user_code = dc.get("user_code", "")
                verif_uri = dc.get("verification_uri",
                                   dc.get("verification_url","https://microsoft.com/link"))
                interval  = dc.get("interval", 5)

                def _show():
                    code_lbl.config(text=user_code)
                    url_lbl.config(text=verif_uri)
                    url_lbl.bind("<Button-1>", lambda e: _wb.open(verif_uri))
                    open_btn.config(state="normal",
                                    command=lambda: _wb.open(verif_uri))
                    copy_btn.config(command=lambda: (
                        dlg.clipboard_clear(), dlg.clipboard_append(user_code)))
                    status_lbl.config(
                        text=f"✅ Code ready! Sign in at the URL above, enter code  {user_code}  then come back.",
                        fg=C["green"])
                    _wb.open(verif_uri)   # auto-open browser
                dlg.after(0, _show)

                # Step 2 — poll
                _set_status(f"⏳ Waiting for sign-in… (code: {user_code})", C["yellow"])
                ms_tok = poll_for_microsoft_token(dc["device_code"], interval, stop_ev)

                # Steps 3-6
                _set_status("🔄 Authenticating with Xbox Live…")
                xbl = authenticate_xbox(ms_tok["access_token"])

                _set_status("🔄 Getting XSTS token…")
                xsts_token = authorize_xsts(xbl["xbox_token"])

                _set_status("🔄 Logging into Minecraft services…")
                mc_token = authenticate_minecraft(xbl["uhs"], xsts_token)

                _set_status("🔄 Fetching Minecraft profile…")
                profile = get_minecraft_profile(mc_token)

                # Step 7 — save (blueprint schema)
                auth_data = {
                    "access_token":  ms_tok["access_token"],
                    "refresh_token": ms_tok.get("refresh_token", ""),
                    "uuid":          profile["uuid"],
                    "username":      profile["username"],
                    "mc_token":      mc_token,
                    "expires_at":    int(time.time()) + ms_tok.get("expires_in", 86400),
                    "source":        "microsoft_oauth",
                }
                _save_auth(auth_data)
                self._auth = auth_data

                def _done():
                    if not dlg.winfo_exists(): return
                    self._update_acct_badge()
                    if hasattr(self, "_page_account_refresh"):
                        self._page_account_refresh()
                    status_lbl.config(
                        text=f"✅  Signed in as  {profile['username']}!",
                        fg=C["green"])
                    code_lbl.config(text="✓")
                    dlg.after(2000, dlg.destroy)
                dlg.after(0, _done)

            except (RuntimeError, TimeoutError) as e:
                def _err(m=str(e)):
                    if dlg.winfo_exists():
                        status_lbl.config(text=f"✗  {m}", fg=C["red"])
                dlg.after(0, _err)
            except Exception as e:
                def _ue(m=str(e)):
                    if dlg.winfo_exists():
                        status_lbl.config(text=f"✗  Unexpected: {m}", fg=C["red"])
                dlg.after(0, _ue)

        _th.Thread(target=_auth_worker, daemon=True).start()

        def _on_close():
            stop_ev.set(); dlg.destroy()
        dlg.protocol("WM_DELETE_WINDOW", _on_close)

    def _msa_logout(self):
        self.msa.clear()
        self._auth = None
        self._update_acct_badge()
        messagebox.showinfo("Logged Out",
            "Microsoft account removed.\nYou are now in offline mode.")
        if hasattr(self, "_page_account_refresh"):
            self._page_account_refresh()

    # ─────────────────────────────────────────────────────────────────────────
    #  ACCOUNT TAB
    # ─────────────────────────────────────────────────────────────────────────
    def _page_account(self):
        p = self._newpage("account")
        self._ptitle(p, "👤  ACCOUNT", "Manage your Minecraft account — online or offline (cracked) mode")

        outer = tk.Frame(p, bg=C["bg"]); outer.pack(fill="both", expand=True)
        sc = tk.Canvas(outer, bg=C["bg"], highlightthickness=0)
        ssb = ttk.Scrollbar(outer, orient="vertical", command=sc.yview)
        inner = tk.Frame(sc, bg=C["bg"])
        inner.bind("<Configure>", lambda e: sc.configure(scrollregion=sc.bbox("all")))
        sc.create_window((0, 0), window=inner, anchor="nw")
        sc.configure(yscrollcommand=ssb.set)
        ssb.pack(side="right", fill="y"); sc.pack(fill="both", expand=True)

        auth = self._auth

        # ── Current Account Status ─────────────────────────────────────────────
        s_status = self._scard(inner, "CURRENT ACCOUNT")
        avatar_row = tk.Frame(s_status, bg=C["panel"]); avatar_row.pack(fill="x", pady=6)

        av = tk.Canvas(avatar_row, width=72, height=72, bg=C["panel"],
                       highlightthickness=2, highlightbackground=C["border"])
        av.pack(side="left", padx=(0, 18))
        if auth and auth.get("username"):
            av.create_rectangle(4, 4, 68, 68, fill=C["green"], outline="")
            av.create_text(36, 36, text=auth["username"][0].upper(),
                           font=("Segoe UI", 32, "bold"), fill=C["bg"])
        else:
            av.create_rectangle(4, 4, 68, 68, fill=C["bg3"], outline="")
            av.create_text(36, 36, text="?", font=("Segoe UI", 32, "bold"), fill=C["muted"])

        info_col = tk.Frame(avatar_row, bg=C["panel"]); info_col.pack(side="left", fill="x", expand=True)

        if auth and auth.get("username"):
            badge_f = tk.Frame(info_col, bg=C["green"], padx=8, pady=2); badge_f.pack(anchor="w", pady=(0,4))
            tk.Label(badge_f, text="● ONLINE  —  Microsoft Account",
                     font=("Segoe UI", 8, "bold"), fg=C["bg"], bg=C["green"]).pack()
            tk.Label(info_col, text=auth["username"],
                     font=("Segoe UI", 20, "bold"), fg=C["text"], bg=C["panel"]).pack(anchor="w")
            tk.Label(info_col, text=f"UUID: {auth.get('uuid','-')}",
                     font=FM, fg=C["muted"], bg=C["panel"]).pack(anchor="w")
            remaining = max(0, int(auth.get("expiry", 0) - time.time()))
            exp_txt = (f"Token expires in: {remaining//60} min {remaining%60} sec"
                       if remaining > 0 else "Token expired — will auto-refresh on next launch")
            tk.Label(info_col, text=exp_txt, font=FS,
                     fg=C["green"] if remaining > 300 else C["yellow"], bg=C["panel"]).pack(anchor="w", pady=(2,0))
        else:
            badge_f = tk.Frame(info_col, bg=C["yellow"], padx=8, pady=2); badge_f.pack(anchor="w", pady=(0,4))
            tk.Label(badge_f, text="● OFFLINE  —  Cracked / No Account",
                     font=("Segoe UI", 8, "bold"), fg=C["bg"], bg=C["yellow"]).pack()
            tk.Label(info_col, text="Not Logged In",
                     font=("Segoe UI", 20, "bold"), fg=C["subtext"], bg=C["panel"]).pack(anchor="w")
            tk.Label(info_col,
                     text="You can play offline or on servers with online-mode=false",
                     font=FS, fg=C["muted"], bg=C["panel"]).pack(anchor="w")

        self._acct_page_status = tk.Label(s_status, text="", font=FS, bg=C["panel"])
        self._acct_page_status.pack(anchor="w")
        self._update_acct_badge()

        # ── Microsoft Account ──────────────────────────────────────────────────
        s_msa = self._scard(inner, "🔑  MICROSOFT ACCOUNT  (play on any online-mode server)")
        tk.Label(s_msa,
                 text="Sign in with your Microsoft / Mojang account.\n"
                      "Uses a secure browser-based Device Code flow — your password is NEVER stored.\n"
                      "After login, your real Minecraft username and UUID are used automatically.",
                 font=FS, fg=C["subtext"], bg=C["panel"], justify="left").pack(anchor="w", pady=(0,10))

        msa_btn_row = tk.Frame(s_msa, bg=C["panel"]); msa_btn_row.pack(anchor="w", pady=4)
        if auth and auth.get("username"):
            self._gbtn(msa_btn_row, "🔄 Switch Microsoft Account",
                       lambda: (self._msa_login(), self.root.after(4000, self._page_account_refresh)),
                       240).pack(side="left", padx=(0,8))
            self._gbtn(msa_btn_row, "🚪 Sign Out",
                       self._msa_logout, 140, C["red"]).pack(side="left")
        else:
            self._gbtn(msa_btn_row, "🔑 Sign in with Microsoft",
                       lambda: (self._msa_login(), self.root.after(4000, self._page_account_refresh)),
                       240, C["blue"]).pack(side="left")

        tk.Label(s_msa,
                 text="ℹ  Your account must own Minecraft: Java Edition. Game Pass (Java) also works.",
                 font=("Segoe UI", 8), fg=C["blue"], bg=C["panel"]).pack(anchor="w", pady=(8,0))

        # ── Offline / Cracked Mode ─────────────────────────────────────────────
        s_offline = self._scard(inner, "🎮  OFFLINE MODE  (Cracked / No Account)")
        tk.Label(s_offline,
                 text="Play without a Microsoft account.\n"
                      "Works only on servers with online-mode=false in server.properties.\n"
                      "Set a custom username below — it will override the instance name.",
                 font=FS, fg=C["subtext"], bg=C["panel"], justify="left").pack(anchor="w", pady=(0,8))

        nr = tk.Frame(s_offline, bg=C["panel"]); nr.pack(fill="x", pady=4)
        tk.Label(nr, text="Offline username:", font=FS, fg=C["subtext"],
                 bg=C["panel"], width=18, anchor="w").pack(side="left")
        self._offline_name_var = tk.StringVar(
            value=self.sel_inst["name"].replace(" ","_") if self.sel_inst else "Player")
        tk.Entry(nr, textvariable=self._offline_name_var, font=F,
                 bg=C["bg3"], fg=C["text"], relief="flat", insertbackground=C["text"],
                 width=22, highlightthickness=1, highlightbackground=C["border"]
                 ).pack(side="left", ipady=5)
        tk.Label(nr, text="no spaces / special chars",
                 font=("Segoe UI", 8), fg=C["muted"], bg=C["panel"]).pack(side="left", padx=8)

        def _use_offline():
            name = self._offline_name_var.get().strip().replace(" ","_")
            if not name: messagebox.showerror("Error", "Enter a username."); return
            if self._auth:
                if not messagebox.askyesno("Switch to Offline",
                    "This will log out your Microsoft account.\nContinue?"): return
            self.msa.clear(); self._auth = None
            self._update_acct_badge()
            # Patch _fire_game to use this name for offline sessions
            self._offline_username_override = name
            messagebox.showinfo("Offline Mode Set",
                f"Offline mode active as '{name}'.\n"
                "You can join servers with online-mode=false.\n"
                "For online servers, use Microsoft sign-in above.")
            self._page_account_refresh()

        off_row = tk.Frame(s_offline, bg=C["panel"]); off_row.pack(anchor="w", pady=6)
        self._gbtn(off_row, "✅ Use Offline Mode", _use_offline, 180).pack(side="left", padx=(0,8))
        if auth:
            self._gbtn(off_row, "🚪 Log Out & Go Offline",
                       self._msa_logout, 200, C["red"]).pack(side="left")

        # ── Xbox / Game Pass ───────────────────────────────────────────────────
        s_xbox = self._scard(inner, "🎮  XBOX & GAME PASS")
        tk.Label(s_xbox,
                 text="If you have Minecraft Java Edition through Xbox Game Pass, sign in with Microsoft above.\n"
                      "Game Pass subscribers use the same Microsoft OAuth — no extra steps.",
                 font=FS, fg=C["subtext"], bg=C["panel"], justify="left").pack(anchor="w", pady=(0,6))
        xrow = tk.Frame(s_xbox, bg=C["panel"]); xrow.pack(anchor="w", pady=4)
        self._gbtn(xrow, "🎮 Open Xbox.com", lambda: webbrowser.open("https://www.xbox.com/play"), 180
                   ).pack(side="left", padx=(0,8))
        self._sbtn(xrow, "🛒 Get Game Pass",
                   lambda: webbrowser.open("https://www.xbox.com/en-US/xbox-game-pass")).pack(side="left")
        tk.Label(s_xbox,
                 text="⚠ Game Pass default is Bedrock Edition. Java Edition requires purchase or Game Pass Ultimate.",
                 font=("Segoe UI", 8), fg=C["yellow"], bg=C["panel"], wraplength=680, justify="left"
                 ).pack(anchor="w", pady=(4,0))

        # ── Buy / Other options ────────────────────────────────────────────────
        s_buy = self._scard(inner, "🛒  BUY MINECRAFT  /  OTHER")
        tk.Label(s_buy,
                 text="Minecraft Java Edition is purchased through a Microsoft account (not Google).",
                 font=FS, fg=C["subtext"], bg=C["panel"]).pack(anchor="w", pady=(0,6))
        brow = tk.Frame(s_buy, bg=C["panel"]); brow.pack(anchor="w", pady=4)
        self._gbtn(brow, "🛒 Buy Java Edition",
                   lambda: webbrowser.open("https://www.minecraft.net/en-us/store/minecraft-java-bedrock-edition-pc"),
                   200, C["green"]).pack(side="left", padx=(0,8))
        self._sbtn(brow, "🔗 Microsoft Account",
                   lambda: webbrowser.open("https://account.microsoft.com")).pack(side="left", padx=(0,8))
        self._sbtn(brow, "🔗 Mojang Help",
                   lambda: webbrowser.open("https://help.minecraft.net/hc/en-us")).pack(side="left")

        # ── Session Debug ──────────────────────────────────────────────────────
        s_info = self._scard(inner, "SESSION INFO")
        debug_rows = [
            ("Mode",         "Online (MSA)" if (auth and auth.get("username")) else "Offline"),
            ("Username",     auth.get("username","—") if auth else "—"),
            ("UUID",         auth.get("uuid","—") if auth else "—"),
            ("Token",        ("Valid" if time.time() < auth.get("expiry",0) else "Expired") if auth else "—"),
            ("Auth file",    str(AUTH_FILE)),
        ]
        for lbl, val in debug_rows:
            dr = tk.Frame(s_info, bg=C["panel"]); dr.pack(fill="x", pady=2)
            tk.Label(dr, text=lbl+":", font=FS, fg=C["subtext"], bg=C["panel"],
                     width=14, anchor="w").pack(side="left")
            tk.Label(dr, text=val, font=FM, fg=C["text"], bg=C["panel"]).pack(side="left")
        self._sbtn(s_info, "📂 Open auth folder",
                   lambda: self._open_path(str(LAUNCHER_DIR))).pack(anchor="w", pady=(6,0))

    def _page_account_refresh(self):
        """Destroy and rebuild the account page to reflect new auth state."""
        was_on_account = False
        if "account" in self.pages:
            was_on_account = self.pages["account"].winfo_ismapped()
            self.pages["account"].destroy()
            del self.pages["account"]
        self._page_account()
        if was_on_account:
            self._nav("account")

    def _launch(self):
        if not self.sel_inst:
            self._set_launch_status("⚠  No instance selected — pick one from Instances",
                                    pct=0, icon="⚠", color=C["yellow"])
            return
        # Disable play button while launching
        self.play_btn.config(state="disabled", text="⏳  LAUNCHING…")
        threading.Thread(target=self._launch_worker,
                         args=(self.sel_inst,), daemon=True).start()

    def _launch_worker(self, inst):
        """Run the full launch sequence in a background thread, updating status bar."""
        try:
            self._do_launch(inst)
        except Exception as e:
            self._set_launch_status(f"✗  Launch error: {e}", pct=0, icon="✗", color=C["red"])
        finally:
            self.root.after(0, self._reset_play_btn)

    def _reset_play_btn(self):
        self.play_btn.config(state="normal", text="▶  PLAY")

    def _do_launch(self, inst):
        """
        Fast Mojang-spec launch. Downloads are parallelised with a thread pool.
        A per-version '.ready' stamp is written after first-time setup so repeat
        launches skip every download/extract check and go straight to Popen.
        """
        import zipfile
        from concurrent.futures import ThreadPoolExecutor, as_completed

        ed  = inst.get("edition", "Java")
        if ed == "Bedrock":
            self.root.after(0, self._launch_bedrock); return

        ver  = inst.get("version", "1.21.4")
        ram  = inst.get("ram", self.settings.get("default_ram", 2))
        ml   = inst.get("modloader", "Vanilla")
        gdir = inst.get("path", str(INSTANCES / inst["name"].replace(" ", "_")))
        Path(gdir).mkdir(parents=True, exist_ok=True)

        vdir        = VERSIONS_DIR / ver
        vjson_path  = vdir / f"{ver}.json"
        mc_jar      = vdir / f"{ver}.jar"
        libs_dir    = vdir / "libraries"
        natives_dir = vdir / "natives"
        ready_stamp = vdir / ".darx_ready"          # written once setup is complete
        indexes_dir = ASSETS_DIR / "indexes"
        objects_dir = ASSETS_DIR / "objects"

        # ── STAGE 1: Java (always fast) ───────────────────────────────────────
        self._set_launch_status("Locating Java…", pct=2, icon="☕")
        java_ui = getattr(self, "java_var", None)
        jp = (java_ui.get() if java_ui else "") or ""
        if not jp or jp == "java" or not (Path(jp).exists() or shutil.which(jp)):
            jp = self._find_java()
        jp = shutil.which(jp) or (str(jp) if Path(str(jp)).exists() else None)
        if not jp:
            self._set_launch_status("✗  Java not found — install Java 21 and Auto-detect in Settings",
                                    pct=0, icon="✗", color=C["red"])
            def _ask_java():
                if messagebox.askyesno("Java Not Found",
                    "Java 21 is required but could not be found.\n\n"
                    "Click YES to download Java 21.\nClick NO to browse manually."):
                    webbrowser.open("https://adoptium.net/temurin/releases/?version=21")
                else:
                    p = filedialog.askopenfilename(title="Locate java.exe",
                        filetypes=[("Java","javaw.exe java java.exe"),("All","*")])
                    if p and java_ui: java_ui.set(p)
            self.root.after(0, _ask_java); return

        # ── AUTH: Blueprint §3 — refresh_token_if_needed() before every launch ──
        self._set_launch_status("🔄 Checking auth token…", pct=3, icon="🔄")
        self._auth = refresh_token_if_needed()
        if self._auth:
            self.root.after(0, self._update_acct_badge)

        # ── FAST PATH: already fully set up — skip straight to launch ─────────
        if ready_stamp.exists() and mc_jar.exists() and vjson_path.exists():
            self._set_launch_status(f"✅ Ready — launching {ver}…", pct=90, icon="🚀")
            try:
                vdata = json.loads(vjson_path.read_text())
            except Exception as e:
                self._set_launch_status(f"✗  Corrupt version JSON: {e}", pct=0, icon="✗", color=C["red"]); return
            _sip  = getattr(self, "_server_ip_var",   None)
            _sprt = getattr(self, "_server_port_var", None)
            self._fire_game(jp, ver, vdata, ml, inst, gdir, ram,
                            libs_dir, natives_dir, indexes_dir,
                            server_ip   = _sip.get().strip()   if _sip   else "",
                            server_port = _sprt.get().strip()  if _sprt  else "25565")
            return

        # ── FIRST-TIME SETUP ──────────────────────────────────────────────────

        # Stage 2: Version JSON
        self._set_launch_status(f"Fetching version info for {ver}…", pct=5, icon="📋")
        if not vjson_path.exists():
            manifest = self.dl.fetch_json(MC_VERSIONS_URL)
            if not manifest:
                self._set_launch_status("✗  No internet — cannot fetch version list",
                                        pct=0, icon="✗", color=C["red"]); return
            info = next((v for v in manifest["versions"] if v["id"] == ver), None)
            if not info:
                self._set_launch_status(f"✗  Version {ver} not found in manifest",
                                        pct=0, icon="✗", color=C["red"]); return
            vdata = self.dl.fetch_json(info["url"])
            if not vdata:
                self._set_launch_status("✗  Cannot download version JSON",
                                        pct=0, icon="✗", color=C["red"]); return
            vdir.mkdir(parents=True, exist_ok=True)
            vjson_path.write_text(json.dumps(vdata, indent=2))
        try:
            vdata = json.loads(vjson_path.read_text())
        except Exception as e:
            self._set_launch_status(f"✗  Corrupt version JSON: {e}",
                                    pct=0, icon="✗", color=C["red"]); return

        # Stage 3: Client JAR
        if not mc_jar.exists():
            dl_info   = vdata.get("downloads", {}).get("client", {})
            jar_url   = dl_info.get("url", "")
            jar_size  = dl_info.get("size", 0)
            if not jar_url:
                self._set_launch_status("✗  No client JAR URL in version JSON",
                                        pct=0, icon="✗", color=C["red"]); return
            self._set_launch_status(f"Downloading Minecraft {ver}…", pct=8, icon="⬇")
            def _prog_jar(p):
                mb = jar_size * p / 100 / 1_048_576 if jar_size else 0
                tot = jar_size / 1_048_576 if jar_size else 0
                self._set_launch_status(f"Downloading {ver}.jar  {mb:.1f}/{tot:.1f} MB",
                                        pct=8 + p * 0.18, icon="⬇")
            if not self.dl.download(jar_url, mc_jar, _prog_jar):
                self._set_launch_status("✗  Client JAR download failed",
                                        pct=0, icon="✗", color=C["red"]); return

        # Stage 4: Libraries — collect what's needed then parallel-download
        self._set_launch_status("Checking libraries…", pct=27, icon="📚")
        sys_os  = {"Windows":"windows","Darwin":"osx","Linux":"linux"}.get(platform.system(),"linux")
        libs_dir.mkdir(parents=True, exist_ok=True)
        natives_dir.mkdir(parents=True, exist_ok=True)

        need_libs    = []   # (url, dest)  — normal JARs
        need_natives = []   # (url, dest)  — native ZIPs to extract

        for lib in vdata.get("libraries", []):
            # Evaluate rules
            rules   = lib.get("rules", [])
            allowed = True
            if rules:
                allowed = False
                for rule in rules:
                    action  = rule.get("action", "allow")
                    os_name = rule.get("os", {}).get("name", "")
                    if not os_name or os_name == sys_os:
                        allowed = (action == "allow")

            if not allowed:
                continue

            downloads = lib.get("downloads", {})

            # Regular artifact
            art = downloads.get("artifact", {})
            if art.get("url") and art.get("path"):
                dest = libs_dir / art["path"].replace("/", os.sep)
                if not dest.exists():
                    need_libs.append((art["url"], dest))

            # Natives classifier
            native_key = lib.get("natives", {}).get(sys_os, "")
            if native_key:
                clf = downloads.get("classifiers", {}).get(native_key, {})
                if clf.get("url") and clf.get("path"):
                    dest = libs_dir / clf["path"].replace("/", os.sep)
                    if not dest.exists():
                        need_natives.append((clf["url"], dest))

        total_dl = len(need_libs) + len(need_natives)
        if total_dl:
            self._set_launch_status(f"Downloading {total_dl} files in parallel…",
                                    pct=28, icon="⬇")
            done_count = [0]

            def _dl_one(url_dest):
                url, dest = url_dest
                dest.parent.mkdir(parents=True, exist_ok=True)
                self.dl.download(url, dest)
                done_count[0] += 1
                p = 28 + (done_count[0] / total_dl) * 30
                self._set_launch_status(
                    f"Downloaded {done_count[0]}/{total_dl}  ({dest.name})",
                    pct=p, icon="⬇")

            # 12 parallel workers — fast but not so many we get throttled
            with ThreadPoolExecutor(max_workers=12) as ex:
                futures = [ex.submit(_dl_one, item)
                           for item in need_libs + need_natives]
                for f in as_completed(futures):
                    f.result()   # surface any exceptions

        # Stage 5: Extract natives (only if not already done)
        self._set_launch_status("Extracting natives…", pct=59, icon="⚙")
        for lib in vdata.get("libraries", []):
            rules   = lib.get("rules", [])
            allowed = True
            if rules:
                allowed = False
                for rule in rules:
                    action  = rule.get("action", "allow")
                    os_name = rule.get("os", {}).get("name", "")
                    if not os_name or os_name == sys_os:
                        allowed = (action == "allow")
            if not allowed: continue

            native_key = lib.get("natives", {}).get(sys_os, "")
            if not native_key: continue
            clf = lib.get("downloads", {}).get("classifiers", {}).get(native_key, {})
            if not clf.get("path"): continue
            src = libs_dir / clf["path"].replace("/", os.sep)
            if not src.exists(): continue
            try:
                with zipfile.ZipFile(src) as z:
                    for entry in z.namelist():
                        if entry.startswith("META-INF"): continue
                        if any(entry.endswith(ext) for ext in (".dll",".so",".dylib")):
                            out = natives_dir / Path(entry).name
                            if not out.exists():
                                data_bytes = z.read(entry)
                                out.write_bytes(data_bytes)
            except Exception:
                pass

        # Stage 6: Asset index + parallel asset download
        self._set_launch_status("Checking assets…", pct=61, icon="🖼")
        asset_info = vdata.get("assetIndex", {})
        asset_id   = asset_info.get("id", ver)
        asset_url  = asset_info.get("url", "")
        indexes_dir.mkdir(parents=True, exist_ok=True)
        objects_dir.mkdir(parents=True, exist_ok=True)

        index_file = indexes_dir / f"{asset_id}.json"
        if not index_file.exists() and asset_url:
            self._set_launch_status(f"Downloading asset index…", pct=62, icon="⬇")
            self.dl.download(asset_url, index_file)

        if index_file.exists():
            try:
                idx_data  = json.loads(index_file.read_text())
                objects   = idx_data.get("objects", {})
                ASSET_BASE = "https://resources.download.minecraft.net/"

                # Collect missing assets — fast set-based check, no stat per file
                existing = {f.name for f in objects_dir.rglob("*") if f.is_file()}
                missing  = [(info["hash"], objects_dir / info["hash"][:2] / info["hash"])
                            for info in objects.values()
                            if len(info.get("hash","")) >= 2
                            and info["hash"] not in existing]

                if missing:
                    total_a  = len(missing)
                    done_a   = [0]
                    self._set_launch_status(
                        f"Downloading {total_a} assets in parallel… (first time only)",
                        pct=63, icon="⬇")

                    def _dl_asset(h_dest):
                        h, dest = h_dest
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        self.dl.download(f"{ASSET_BASE}{h[:2]}/{h}", dest)
                        done_a[0] += 1
                        if done_a[0] % 100 == 0:
                            p = 63 + (done_a[0] / total_a) * 24
                            self._set_launch_status(
                                f"Assets {done_a[0]}/{total_a}…", pct=p, icon="⬇")

                    with ThreadPoolExecutor(max_workers=24) as ex:
                        list(ex.map(_dl_asset, missing))

            except Exception as e:
                self._set_launch_status(f"Asset warning (non-fatal): {e}",
                                        pct=87, icon="⚠")

        # Write ready stamp so next launch skips all of the above
        try:
            ready_stamp.write_text(datetime.datetime.now().isoformat())
        except Exception:
            pass

        # ── Fire the game ─────────────────────────────────────────────────────
        self._set_launch_status(f"Starting Minecraft {ver}…", pct=92, icon="🚀")
        _sip  = getattr(self, "_server_ip_var",   None)
        _sprt = getattr(self, "_server_port_var", None)
        self._fire_game(jp, ver, vdata, ml, inst, gdir, ram,
                        libs_dir, natives_dir, indexes_dir,
                        server_ip   = _sip.get().strip()   if _sip   else "",
                        server_port = _sprt.get().strip()  if _sprt  else "25565")

    def _fire_game(self, jp, ver, vdata, ml, inst, gdir, ram,
                   libs_dir, natives_dir, indexes_dir,
                   server_ip="", server_port="25565"):
        """Build the final command and Popen — always fast."""
        asset_id    = vdata.get("assetIndex", {}).get("id", ver)
        vdir        = VERSIONS_DIR / ver
        mc_jar      = vdir / f"{ver}.jar"
        sys_os      = {"Windows":"windows","Darwin":"osx","Linux":"linux"}.get(platform.system(),"linux")

        # Classpath — build once from what's on disk
        sep = ";" if platform.system() == "Windows" else ":"
        seen = set(); cp_parts = []
        def _add(p):
            s = str(p)
            if s not in seen and Path(p).exists():
                seen.add(s); cp_parts.append(s)
        _add(mc_jar)
        for lib in vdata.get("libraries", []):
            rules   = lib.get("rules", [])
            allowed = True
            if rules:
                allowed = False
                for rule in rules:
                    action  = rule.get("action","allow")
                    os_name = rule.get("os",{}).get("name","")
                    if not os_name or os_name == sys_os:
                        allowed = (action == "allow")
            if not allowed: continue
            art = lib.get("downloads",{}).get("artifact",{})
            if art.get("path"):
                _add(libs_dir / art["path"].replace("/", os.sep))
        cp = sep.join(cp_parts)

        # Main class
        main_class = vdata.get("mainClass", "net.minecraft.client.main.Main")
        lv = inst.get("loader_ver", "")
        if inst.get("modloader","Vanilla") in ("Fabric","Quilt") and lv:
            pj = VERSIONS_DIR / lv / f"{lv}.json"
            if pj.exists():
                try: main_class = json.loads(pj.read_text()).get("mainClass", main_class)
                except Exception: pass

        # Write keybinds
        self._write_keybinds_to_instance(gdir)

        jvm_extra  = self.settings.get("jvm_args","").split()
        w, h, fs   = (self.settings.get("game_width",854),
                      self.settings.get("game_height",480),
                      self.settings.get("fullscreen",False))
        # Blueprint §5 — load auth, set --userType msa for Microsoft accounts
        auth = self._auth or _load_auth()
        if auth and auth.get("username"):
            username  = auth["username"]
            uuid_str  = auth.get("uuid", "00000000-0000-0000-0000-000000000000")
            mc_token  = auth.get("mc_token", "0")      # blueprint field name
            user_type = "msa" if auth.get("source") == "microsoft_oauth" else "offline"
        else:
            override  = getattr(self, "_offline_username_override", "")
            username  = (override or inst.get("name", "Player")).replace(" ", "_")
            uuid_str  = _offline_uuid(username)
            mc_token  = "0"
            user_type = "offline"

        # JVM args from version JSON
        jvm_from_json = []
        for arg in vdata.get("arguments",{}).get("jvm",[]):
            if isinstance(arg, str):
                jvm_from_json.append(
                    arg.replace("${natives_directory}", str(natives_dir))
                       .replace("${launcher_name}",    "DarxLauncher")
                       .replace("${launcher_version}",  VERSION)
                       .replace("${classpath}",         cp))

        # Game args
        def fill(s):
            return (s.replace("${auth_player_name}",  username)
                     .replace("${version_name}",       ver)
                     .replace("${game_directory}",     gdir)
                     .replace("${assets_root}",        str(ASSETS_DIR))
                     .replace("${game_assets}",        str(ASSETS_DIR))
                     .replace("${assets_index_name}",  asset_id)
                     .replace("${auth_uuid}",          uuid_str)
                     .replace("${auth_access_token}",  mc_token)
                     .replace("${user_type}",          user_type)
                     .replace("${version_type}",       vdata.get("type","release"))
                     .replace("${resolution_width}",   str(w))
                     .replace("${resolution_height}",  str(h)))

        game_args_raw = [a for a in vdata.get("arguments",{}).get("game",[]) if isinstance(a,str)]
        if not game_args_raw and "minecraftArguments" in vdata:
            game_args_raw = vdata["minecraftArguments"].split()
        game_args = [fill(a) for a in game_args_raw]

        if not game_args:
            game_args = [
                "--username", username, "--version", ver,
                "--gameDir",  gdir,     "--assetsDir", str(ASSETS_DIR),
                "--assetIndex", asset_id, "--uuid", uuid_str,
                "--accessToken", mc_token, "--userType", user_type,
                "--width", str(w), "--height", str(h),
            ]



        cmd = (
            [jp, f"-Xms512m", f"-Xmx{ram*1024}m"]
            + (jvm_from_json or [f"-Djava.library.path={natives_dir}"])
            + jvm_extra
            + ["-cp", cp, main_class]
            + game_args
        )
        if fs and "--fullscreen" not in game_args:
            cmd.append("--fullscreen")

        # Quick-Connect: join server on launch (only works on offline-mode servers)
        if server_ip:
            cmd += ["--server", server_ip]
            port = server_port.strip() if server_port.strip() else "25565"
            if port != "25565":
                cmd += ["--port", port]

        launch_kw = {"cwd": gdir}
        if platform.system() == "Windows":
            launch_kw["creationflags"] = 0x00000008 | 0x08000000  # DETACHED | NO_WINDOW
        else:
            launch_kw["start_new_session"] = True

        try:
            proc = subprocess.Popen(cmd, **launch_kw)
        except FileNotFoundError as e:
            self._set_launch_status(f"✗  {e} — check Java path in Settings",
                                    pct=0, icon="✗", color=C["red"]); return
        except Exception as e:
            self._set_launch_status(f"✗  Launch failed: {e}",
                                    pct=0, icon="✗", color=C["red"]); return

        self.im.update_cfg(gdir, "last_played",
                           datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self._set_launch_status(
            f"✅  Minecraft {ver} running  (PID {proc.pid}) — minimizing…",
            pct=100, icon="🎮", color=C["green"])
        self.root.after(1400, self.root.iconify)

        def _watch():
            proc.wait()
            code = proc.returncode
            self._set_launch_status(
                "Minecraft closed. Ready." if code == 0
                else f"Minecraft exited (code {code}). Check logs in your instance folder.",
                pct=0, icon="⛏" if code == 0 else "⚠",
                color=None if code == 0 else C["yellow"])
            self.root.after(0, self.root.deiconify)
        threading.Thread(target=_watch, daemon=True).start()

    def _download_mc(self, ver):
        self._set_launch_status(f"Downloading Minecraft {ver}…", pct=5, icon="⬇")
        manifest = self.dl.fetch_json(MC_VERSIONS_URL)
        if not manifest:
            self._set_launch_status("✗  Cannot fetch version list", pct=0, icon="✗", color=C["red"])
            self.root.after(0, messagebox.showerror, "Error", "Cannot fetch version list."); return
        info = next((v for v in manifest["versions"] if v["id"] == ver), None)
        if not info:
            self._set_launch_status(f"✗  Version {ver} not found", pct=0, icon="✗", color=C["red"])
            self.root.after(0, messagebox.showerror, "Error", f"Version {ver} not found."); return
        data = self.dl.fetch_json(info["url"])
        if not data:
            self._set_launch_status("✗  Cannot fetch version data", pct=0, icon="✗", color=C["red"])
            self.root.after(0, messagebox.showerror, "Error", "Cannot fetch version data."); return
        vdir = VERSIONS_DIR / ver; vdir.mkdir(parents=True, exist_ok=True)
        (vdir / f"{ver}.json").write_text(json.dumps(data, indent=2))

        def on_prog(pct):
            self._set_launch_status(f"Downloading Minecraft {ver}… {pct:.0f}%", pct=pct, icon="⬇")

        ok = self.dl.download(data["downloads"]["client"]["url"], vdir / f"{ver}.jar", on_prog)
        if ok:
            self._set_launch_status(f"✓  Minecraft {ver} downloaded!", pct=100, icon="✅", color=C["green"])
            self.root.after(0, messagebox.showinfo, "Downloaded!", f"Minecraft {ver} ready!")
        else:
            self._set_launch_status("✗  Download failed", pct=0, icon="✗", color=C["red"])
            self.root.after(0, messagebox.showerror, "Error", "Download failed.")

    # ─────────────────────────────────────────────────────────────────────────
    #  STARTUP
    # ─────────────────────────────────────────────────────────────────────────
    def _startup_tasks(self):
        vers = self.dl.fetch_mc_versions()
        if vers:
            self.mc_versions = vers
            self.root.after(0, self._push_versions)

    def _push_versions(self):
        v0 = self.mc_versions[0]
        self._mods_ver_var.set(v0)
        for pid in ("resourcepacks","shaderpacks","datapacks"):
            vv = getattr(self, f"_{pid}_ver_var", None)
            if vv and vv.get() == KNOWN_VERSIONS[0]: vv.set(v0)

    # ─────────────────────────────────────────────────────────────────────────
    #  HELPERS
    # ─────────────────────────────────────────────────────────────────────────
    def _find_java(self):
        """Deep system scan for Java — checks PATH, registry, common install dirs, and recursive search."""
        import glob

        # 1. Check PATH first (fastest)
        for exe in ("javaw", "java"):
            found = shutil.which(exe)
            if found:
                return found

        sys_name = platform.system()

        # 2. Windows: registry + common dirs + recursive glob
        if sys_name == "Windows":
            # Try Windows registry
            try:
                import winreg
                reg_keys = [
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\JDK"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Development Kit"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\JavaSoft\Java Runtime Environment"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Eclipse Adoptium\JDK"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Eclipse Foundation\JDK"),
                    (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\JDK"),
                ]
                for hkey, reg_path in reg_keys:
                    try:
                        key = winreg.OpenKey(hkey, reg_path)
                        # enumerate sub-keys (versions)
                        i = 0
                        while True:
                            try:
                                sub = winreg.EnumKey(key, i)
                                sub_key = winreg.OpenKey(key, sub)
                                try:
                                    home, _ = winreg.QueryValueEx(sub_key, "JavaHome")
                                    candidate = Path(home) / "bin" / "javaw.exe"
                                    if candidate.exists():
                                        return str(candidate)
                                    candidate = Path(home) / "bin" / "java.exe"
                                    if candidate.exists():
                                        return str(candidate)
                                except FileNotFoundError:
                                    pass
                                winreg.CloseKey(sub_key)
                                i += 1
                            except OSError:
                                break
                        winreg.CloseKey(key)
                    except FileNotFoundError:
                        continue
            except ImportError:
                pass

            # Common Windows install roots
            roots = [
                r"C:\Program Files\Eclipse Adoptium",
                r"C:\Program Files\Java",
                r"C:\Program Files\Microsoft",
                r"C:\Program Files\BellSoft",  # Liberica JDK
                r"C:\Program Files\Amazon Corretto",
                r"C:\Program Files\Zulu",
                r"C:\Program Files\GraalVM",
                r"C:\Program Files\Temurin",
                r"C:\Program Files (x86)\Java",
                r"C:\Program Files (x86)\Eclipse Adoptium",
            ]
            for root in roots:
                rp = Path(root)
                if not rp.exists():
                    continue
                # Prefer newer versions (sort descending by dir name)
                try:
                    subdirs = sorted(rp.iterdir(), key=lambda d: d.name, reverse=True)
                except Exception:
                    continue
                for d in subdirs:
                    for exe in ("javaw.exe", "java.exe"):
                        cand = d / "bin" / exe
                        if cand.exists():
                            return str(cand)
                        # Sometimes nested one more level
                        for sub in (d / "bin").glob("../**/bin/" + exe) if (d / "bin").exists() else []:
                            if sub.exists():
                                return str(sub)

            # Last resort: glob scan under Program Files
            for pattern in [
                r"C:\Program Files\**\javaw.exe",
                r"C:\Program Files (x86)\**\javaw.exe",
            ]:
                try:
                    matches = glob.glob(pattern, recursive=True)
                    if matches:
                        # Prefer java 21, then 17, then highest
                        def version_score(p):
                            for v in ("21", "17", "11", "8"):
                                if v in p:
                                    return int(v)
                            return 0
                        matches.sort(key=version_score, reverse=True)
                        return matches[0]
                except Exception:
                    pass

        # 3. macOS: common Homebrew and system locations
        elif sys_name == "Darwin":
            mac_cands = [
                "/opt/homebrew/opt/openjdk@21/bin/java",
                "/opt/homebrew/opt/openjdk@17/bin/java",
                "/opt/homebrew/opt/openjdk/bin/java",
                "/usr/local/opt/openjdk@21/bin/java",
                "/usr/local/opt/openjdk@17/bin/java",
                "/usr/local/opt/openjdk/bin/java",
                "/Library/Java/JavaVirtualMachines",
            ]
            for c in mac_cands:
                cp = Path(c)
                if cp.is_file() and cp.exists():
                    return str(cp)
                if cp.is_dir():
                    # scan inside /Library/Java/JavaVirtualMachines
                    try:
                        jvms = sorted(cp.iterdir(), key=lambda d: d.name, reverse=True)
                        for jvm in jvms:
                            cand = jvm / "Contents" / "Home" / "bin" / "java"
                            if cand.exists():
                                return str(cand)
                    except Exception:
                        pass
            try:
                result = subprocess.run(["/usr/libexec/java_home", "-v", "21"],
                                        capture_output=True, text=True, timeout=5)
                home = result.stdout.strip()
                if home:
                    cand = Path(home) / "bin" / "java"
                    if cand.exists():
                        return str(cand)
                # Try any version
                result2 = subprocess.run(["/usr/libexec/java_home"],
                                         capture_output=True, text=True, timeout=5)
                home2 = result2.stdout.strip()
                if home2:
                    cand2 = Path(home2) / "bin" / "java"
                    if cand2.exists():
                        return str(cand2)
            except Exception:
                pass

        # 4. Linux: common paths + update-alternatives
        else:
            linux_cands = [
                "/usr/lib/jvm/java-21-openjdk-amd64/bin/java",
                "/usr/lib/jvm/java-21-openjdk/bin/java",
                "/usr/lib/jvm/java-17-openjdk-amd64/bin/java",
                "/usr/lib/jvm/java-17-openjdk/bin/java",
                "/usr/lib/jvm/java-11-openjdk-amd64/bin/java",
                "/usr/local/lib/jvm/java-21/bin/java",
                "/usr/bin/java",
                "/usr/local/bin/java",
                "/opt/java/21/bin/java",
                "/opt/jdk/21/bin/java",
            ]
            for c in linux_cands:
                if Path(c).exists():
                    return c
            # Try update-alternatives
            try:
                result = subprocess.run(
                    ["update-alternatives", "--list", "java"],
                    capture_output=True, text=True, timeout=5)
                lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
                if lines:
                    return lines[0]
            except Exception:
                pass
            # Scan /usr/lib/jvm
            jvm_dir = Path("/usr/lib/jvm")
            if jvm_dir.exists():
                try:
                    jvms = sorted(jvm_dir.iterdir(), key=lambda d: d.name, reverse=True)
                    for jvm in jvms:
                        cand = jvm / "bin" / "java"
                        if cand.exists():
                            return str(cand)
                except Exception:
                    pass

        return "java"  # fallback — let OS resolve it

    def _browse_java(self):
        p = filedialog.askopenfilename(title="Select Java",
                                       filetypes=[("Java","javaw.exe java"),("All","*")])
        if p: self.java_var.set(p)

    def _write_keybinds_to_instance(self, gdir):
        """Write keybind settings to the instance's options.txt before launch."""
        keybinds = getattr(self, "_keybind_vars", None)
        if not keybinds:
            return
        options_file = Path(gdir) / "options.txt"
        # Read existing options if present
        existing = {}
        if options_file.exists():
            try:
                for line in options_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                    if ":" in line:
                        k, _, v = line.partition(":")
                        existing[k.strip()] = v.strip()
            except Exception:
                pass
        # Overwrite keybind lines
        for action_key, var in keybinds.items():
            val = var.get().strip()
            if val:
                existing[action_key] = val
        # Write back
        try:
            lines = [f"{k}:{v}" for k, v in existing.items()]
            options_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        except Exception as e:
            print(f"[Keybinds] Could not write options.txt: {e}")

    def _autodetect_java(self):
        self._java_ver_lbl.config(text="⏳ Scanning system for Java…", fg=C["yellow"])
        self.root.update_idletasks()
        def _scan():
            found = self._find_java()
            def _done():
                self.java_var.set(found)
                if found and found != "java":
                    self._java_ver_lbl.config(text=f"✓ Found: {found}", fg=C["green"])
                else:
                    self._java_ver_lbl.config(
                        text="⚠ Could not auto-detect. Browse manually or install Java 21.",
                        fg=C["yellow"])
            self.root.after(0, _done)
        threading.Thread(target=_scan, daemon=True).start()

    def _test_java(self):
        try:
            r = subprocess.run([self.java_var.get(),"-version"],
                               capture_output=True, text=True, timeout=5)
            out = (r.stderr or r.stdout).strip().split("\n")[0]
            self._java_ver_lbl.config(text=f"✓ {out}", fg=C["text"])
        except Exception as e:
            self._java_ver_lbl.config(text=f"✗ {e}", fg=C["red"])

    def _open_path(self, path):
        try:
            if platform.system() == "Windows": os.startfile(path)
            elif platform.system() == "Darwin": subprocess.Popen(["open", path])
            else: subprocess.Popen(["xdg-open", path])
        except Exception: messagebox.showinfo("Path", path)

    def _newpage(self, name):
        f = tk.Frame(self.content, bg=C["bg"])
        self.pages[name] = f; return f

    def _ptitle(self, parent, title, sub=""):
        h = tk.Frame(parent, bg=C["bg"], pady=12); h.pack(fill="x", padx=22)
        tk.Frame(h, bg=C["border"], width=3).pack(side="left", fill="y", padx=(0, 10))
        t = tk.Frame(h, bg=C["bg"]); t.pack(side="left")
        tk.Label(t, text=title, font=FL, fg=C["text"], bg=C["bg"]).pack(anchor="w")
        if sub: tk.Label(t, text=sub, font=FS, fg=C["subtext"], bg=C["bg"]).pack(anchor="w")
        tk.Frame(parent, bg=C["border"], height=1).pack(fill="x", padx=22, pady=(0, 5))

    def _scard(self, parent, title):
        tk.Label(parent, text=title, font=("Segoe UI", 8, "bold"),
                 fg=C["subtext"], bg=C["bg"]).pack(anchor="w", padx=22, pady=(10, 2))
        f = tk.Frame(parent, bg=C["panel"], padx=14, pady=12,
                     highlightthickness=1, highlightbackground=C["border"])
        f.pack(fill="x", padx=22, pady=3); return f

    def _gbtn(self, parent, text, cmd, width=160, color=None):
        c = color or C["accent2"]
        return tk.Button(parent, text=text, font=FS, fg=C["bg"],
                         bg=c, activebackground=C["accent"],
                         activeforeground=C["bg"], relief="flat",
                         padx=10, pady=6, cursor="hand2",
                         width=width // 8, command=cmd)

    def _sbtn(self, parent, text, cmd, color=None):
        return tk.Button(parent, text=text, font=FS, fg=C["text"],
                         bg=C["bg3"] if not color else color,
                         activebackground=C["border2"],
                         activeforeground=C["text"], relief="flat",
                         padx=8, pady=4, cursor="hand2", command=cmd)


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    for d in (LAUNCHER_DIR, INSTANCES, VERSIONS_DIR, LIBS_DIR, ASSETS_DIR, SKINS_DIR, MODPACKS_DIR):
        d.mkdir(parents=True, exist_ok=True)
    root = tk.Tk()
    app  = DarxLauncher(root)
    root.mainloop()
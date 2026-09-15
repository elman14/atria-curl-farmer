#!/usr/bin/env python3
"""Atria curl farmer — full curl_cffi, no playwright. ~30-60s/akun."""
import json, re, sys, time, secrets
import requests as req
from curl_cffi import requests as creq
from pathlib import Path

BASE = "https://api.atria-asi.ai"
AUTH = "https://auth.atria-asi.ai"
ELF = "https://tempmail.elf.biz.id"
ELF_DOMAINS = ["elf.biz.id", "elfgank.my.id", "siapbelajar.web.id",
               "bangdodo.bond", "sakithati.bond", "widodojoko.biz.id",
               "ruangguru.my.id"]
WORKDIR = Path(__file__).parent
KEYS_FILE = WORKDIR / "api_keys.json"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"

def get_domain():
    try:
        r = req.get(f"{ELF}/api/domains", timeout=15)
        ds = r.json().get("domains") or ELF_DOMAINS
        return ds[int(time.time() * 1000) % len(ds)]
    except Exception:
        return ELF_DOMAINS[0]

def new_session():
    s = creq.Session(impersonate="chrome131")
    s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    return s

def farm_one(idx=1, total=1):
    L = f"[{idx}/{total}]"
    domain = get_domain()
    addr = f"atria-{int(time.time()*1000) % 10**9}-{secrets.token_hex(2)}@{domain}"
    r = req.post(f"{ELF}/api/mailbox", json={"address": addr}, timeout=15)
    if r.status_code != 200:
        print(f"{L} FAIL: mailbox {r.status_code}", flush=True)
        return None
    print(f"{L} {addr}", flush=True)
    H = {"Origin": AUTH, "Referer": f"{AUTH}/register", "Content-Type": "application/json"}
    try:
        s = new_session()
        r = s.get(f"{BASE}/sign-in", allow_redirects=False, timeout=20)
        loc = r.headers.get("location")
        r = s.get(loc, allow_redirects=False, timeout=20)
        loc2 = r.headers.get("location")
        url3 = loc2 if loc2.startswith("http") else AUTH + loc2
        s.get(url3, timeout=20)
        r = s.put(f"{AUTH}/api/experience", json={"interactionEvent": "Register"}, headers=H, timeout=20)
        if r.status_code != 204:
            print(f"{L} FAIL: PUT exp {r.status_code}", flush=True)
            return None
        r = s.post(f"{AUTH}/api/experience/verification/verification-code",
                   json={"interactionEvent": "Register", "identifier": {"type": "email", "value": addr}},
                   headers=H, timeout=20)
        if r.status_code != 200:
            print(f"{L} FAIL: send code {r.status_code} {r.text[:100]}", flush=True)
            return None
        vid = r.json().get("verificationId")
        code = None
        for _ in range(24):
            time.sleep(5)
            try:
                d = req.get(f"{ELF}/api/inbox", params={"address": addr}, timeout=15).json()
                for m in d.get("data", []):
                    mm = re.search(r"(\d{6})", f"{m.get('subject','')} {m.get('text','')} {m.get('content','')}")
                    if mm:
                        code = mm.group(1)
                        break
                if code:
                    break
            except Exception:
                pass
        if not code:
            print(f"{L} FAIL: No code", flush=True)
            return None
        print(f"{L} Code: {code}", flush=True)
        r = s.post(f"{AUTH}/api/experience/verification/verification-code/verify",
                   json={"verificationId": vid, "identifier": {"type": "email", "value": addr}, "code": code},
                   headers=H, timeout=20)
        if r.status_code != 200:
            print(f"{L} FAIL: verify {r.status_code}", flush=True)
            return None
        r = s.post(f"{AUTH}/api/experience/identification", json={"verificationId": vid}, headers=H, timeout=20)
        if r.status_code != 201:
            print(f"{L} FAIL: ident {r.status_code}", flush=True)
            return None
        r = s.post(f"{AUTH}/api/experience/submit", headers=H, timeout=20)
        redir = r.json().get("redirectTo")
        if not redir:
            print(f"{L} FAIL: no redirect", flush=True)
            return None
        s.get(redir, allow_redirects=True, timeout=30)  # oidc -> consent -> callback -> console
        r = s.post(f"{BASE}/api/keys", json={"name": f"key-{idx}"}, timeout=20)
        if r.status_code not in (200, 201):
            print(f"{L} FAIL: keys {r.status_code} {r.text[:100]}", flush=True)
            return None
        key = r.json().get("key")
        if not key:
            print(f"{L} FAIL: No key", flush=True)
            return None
        print(f"{L} OK: {key[:30]}...", flush=True)
        return {"email": addr, "key": key, "name": f"key-{idx}",
                "source": "tempmail", "status": "active",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    except Exception as e:
        print(f"{L} ERROR: {e}", flush=True)
        return None

def load_keys():
    if KEYS_FILE.exists():
        return json.loads(KEYS_FILE.read_text())
    return []

def save_keys(data):
    KEYS_FILE.write_text(json.dumps(data, indent=2))

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "1"
    if arg == "loop":
        i = 0
        while True:
            i += 1
            existing = load_keys()
            res = farm_one(i, 0)
            if res:
                existing.append(res)
                save_keys(existing)
            time.sleep(5)
    else:
        n = int(arg) if arg.isdigit() else 1
        existing = load_keys()
        ok = 0
        for idx in range(1, n + 1):
            if idx > 1:
                time.sleep(5)
            res = farm_one(idx, n)
            if res:
                existing.append(res)
                save_keys(existing)
                ok += 1
        print(f"\nDONE: {ok}/{n} | total file: {len(load_keys())}")

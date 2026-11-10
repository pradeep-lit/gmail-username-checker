"""
gmail-username-checker
Generate Gmail username ideas from a name and check availability using your OWN
logged-in Google session. Secrets are read from environment variables or a
local .env file (git-ignored). Nothing secret is ever stored in this repo.
"""
import argparse, itertools, json, os, random, re, sys, time
import urllib.parse, urllib.request, urllib.error

URL = ("https://myaccount.google.com/_/AccountSettingsUi/data/batchexecute"
       "?rpcids=chspYe&source-path=%2Fembedded%2Fgoogle-account-email"
       "&hl=en_GB&soc-app=1&soc-platform=1&soc-device=2&rt=c")
DEFAULT_BL = "boq_identityaccountsettingsuiserver_20261107.10_p0"
SUFFIXES = ["dev", "codes", "code", "py", "tech", "mobile", "android", "backend", "works", "hq"]


def load_dotenv(path=".env"):
    """Minimal .env loader (KEY='value' per line). Existing env vars win."""
    if not os.path.exists(path):
        return
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def valid(u):
    plain = u.replace(".", "")
    return (6 <= len(plain) <= 30 and re.fullmatch(r"[a-z0-9.]+", u)
            and not u.startswith(".") and not u.endswith(".") and ".." not in u)


def generate(first, last):
    f, l = first.lower(), last.lower()
    c = [f"{f}{l}", f"{f}.{l}", f"{f[0]}{l}", f"{f}{l[0]}", f"{l}{f}", f"{l}.{f}", f"{l}{f[0]}"]
    for w, b in itertools.product(SUFFIXES, [f"{f}{l}", f"{f[0]}{l}", f"{f}.{l}"]):
        c += [f"{b}.{w}", f"{b}{w}"]
    for b, n in itertools.product([f"{f}{l}", f"{f}.{l}"], ["01", "07", "26", "2026", "11"]):
        c.append(f"{b}{n}")
    seen, out = set(), []
    for u in c:                      # Gmail ignores dots -> dedupe without them
        k = u.replace(".", "")
        if valid(u) and k not in seen:
            seen.add(k); out.append(u)
    return sorted(out, key=len)


def parse_response(raw):
    """Return (status_code, suggestions) from a batchexecute response."""
    for line in raw.splitlines():
        if '"wrb.fr"' in line:
            inner = json.loads(json.loads(line)[0][2])
            return inner[0], inner[1] if len(inner) > 1 else []
    raise ValueError("unexpected response (session expired?)")


def check(username, reqid):
    env = os.environ
    at, cookie = env.get("GOOGLE_AT"), env.get("GOOGLE_COOKIE")
    if not at or not cookie:
        sys.exit("Missing GOOGLE_AT / GOOGLE_COOKIE. See README (.env.example).")
    url = URL + "&bl=" + urllib.parse.quote(env.get("GOOGLE_BL", DEFAULT_BL)) + f"&_reqid={reqid}"
    if env.get("GOOGLE_FSID"):
        url += "&f.sid=" + urllib.parse.quote(env["GOOGLE_FSID"])
    if env.get("GOOGLE_RAPT"):
        url += "&rapt=" + urllib.parse.quote(env["GOOGLE_RAPT"])
    freq = json.dumps([[["chspYe", json.dumps([username]), None, "generic"]]])
    body = urllib.parse.urlencode({"f.req": freq, "at": at.strip()}).encode()
    req = urllib.request.Request(url, data=body, headers={
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "x-same-domain": "1",
        "x-goog-ext-525002608-jspb": "[507]",
        "x-requested-with": "com.google.android.gms",
        "origin": "https://myaccount.google.com",
        "referer": "https://myaccount.google.com/",
        "user-agent": "Mozilla/5.0",
        "cookie": cookie.strip().replace("\n", ""),
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return parse_response(r.read().decode())


def main():
    ap = argparse.ArgumentParser(description="Generate and check Gmail usernames.")
    ap.add_argument("--first", default="pradeep")
    ap.add_argument("--last", default="chauhan")
    ap.add_argument("--generate", action="store_true", help="only print candidates")
    ap.add_argument("--check", action="store_true", help="check availability")
    ap.add_argument("--names", nargs="*", help="check these instead of generated ones")
    ap.add_argument("--limit", type=int, default=25, help="max names per run")
    a = ap.parse_args()

    load_dotenv()
    names = a.names or generate(a.first, a.last)
    if not a.check:
        print("\n".join(names)); return

    reqid = random.randint(100000, 900000)
    for n in names[: a.limit]:
        try:
            code, sugg = check(n, reqid)
        except urllib.error.HTTPError as e:
            sys.exit(f"HTTP {e.code} - stopping. Google said: {e.read().decode(errors='ignore')[:200]!r}\n"
                     "Copy fresh session values and retry.")
        except Exception as e:
            sys.exit(f"Stopped: {e}")
        label = "TAKEN" if code == 2 else f"code={code} (likely available)"
        print(f"{n}@gmail.com -> {label}  {sugg if code == 2 else ''}")
        reqid += 100000
        time.sleep(random.uniform(4, 8))


if __name__ == "__main__":
    main()

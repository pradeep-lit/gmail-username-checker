"""Fail if staged/tracked files look like they contain Google session secrets."""
import re, subprocess, sys

PATTERNS = {
    "cookie header": r"(?i)\bcookie\s*:\s*\S{20,}",
    "Google SID/PSID cookie": r"\b(__Secure-[0-9A-Z]*(PSID|PAPISID|OSID|PSIDCC)|SAPISID|APISID|HSID|SSID|SIDCC)=[^\s;']{8,}",
    "g.a000 session token": r"\bg\.a000[\w\-]{20,}",
    "at token": r"\bACEssn[\w\-]{10,}",
    "rapt token": r"\bAEjHL4[\w\-]{20,}",
    "NID cookie": r"\bNID=[\w\-]{40,}",
}

def files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                         capture_output=True, text=True).stdout.split()
    return out or subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split()

bad = False
for f in files():
    if f.endswith(".har"):
        print(f"BLOCKED: {f} (HAR files contain live credentials)"); bad = True; continue
    try:
        text = open(f, encoding="utf-8", errors="ignore").read()
    except OSError:
        continue
    for name, pat in PATTERNS.items():
        if re.search(pat, text):
            print(f"BLOCKED: {f} looks like it contains a {name}"); bad = True
sys.exit(1 if bad else 0)

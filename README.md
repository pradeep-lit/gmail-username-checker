# gmail-username-checker

Generate Gmail username ideas from a name and check which are free, using your
own logged-in Google session. Pure Python 3, no dependencies.

> **Unofficial.** It calls an internal Google endpoint that can change or stop
> working at any time. Use it gently (small batches, built-in delay) on your own
> account only. Heavy automation may get your account flagged.

## Usage

```bash
python email_checker.py --first jane --last doe --generate     # list ideas
python email_checker.py --first jane --last doe --check        # check them
python email_checker.py --check --names jane.doe.dev jdoe.codes
```

Options: `--limit N` (default 25 names per run).

## Setup (secrets stay local)

1. Sign in at myaccount.google.com, open the "add email" page, press F12 -> Network.
2. Filter by `batchexecute`, type a name, open the request with `rpcids=chspYe`.
3. `cp .env.example .env` and fill in:

| Variable | Where to find it |
|---|---|
| `GOOGLE_COOKIE` | Request headers -> `cookie` (whole value, one line) |
| `GOOGLE_AT` | Form data -> `at` |
| `GOOGLE_FSID` | URL -> `f.sid` |
| `GOOGLE_RAPT` | URL -> `rapt` |
| `GOOGLE_BL` | URL -> `bl` |

Values expire within minutes to hours; copy fresh ones if you get an HTTP 400.

Output: `TAKEN` means unavailable (response code 2). Any other code is printed raw
as "likely available" - confirm once with a gibberish name to see what free looks like.

## Keeping secrets out of git

- `.env`, `*.har`, and raw request dumps are in `.gitignore`.
- Enable the pre-commit guard that blocks cookies/tokens:

```bash
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

- Run a manual scan any time: `python scripts/check_secrets.py`
- **Never** share a HAR file or a copied request. If you did, sign out of that
  device in Google Account -> Security -> Your devices.

## License

MIT

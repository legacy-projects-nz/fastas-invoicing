#!/usr/bin/env python3
"""
push_invoice.py - send a finished invoice straight into FASTAS (Supabase) so it
lands on the matching business tile in the admin pipeline. No Google Drive, no email.

Standard library only - nothing to pip install.

Use as a module (add this to the end of your invoice generator):

    from push_invoice import push_invoice

    push_invoice(
        "Tech Iron Group - March.xlsx",   # the file you just created
        business_name="Tech Iron Group",  # who it's for
        licensee_email="sales@fastnz.nz", # which licensee (optional if only one)
        total=234.50,                     # optional, shows on the tile
    )

Use from the command line:

    python push_invoice.py "Tech Iron Group - March.xlsx" "Tech Iron Group" \
        --licensee sales@fastnz.nz --total 234.50

The business is matched even with a messy name/typo (e.g. "Tech Ion" -> "Tech Iron Group").
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

FUNCTION_URL = "https://ecgvkifvlrcfrnqbades.supabase.co/functions/v1/invoice-intake"
PUBLISHABLE_KEY = "sb_publishable_qGgoGsfKwLELehUzbC25Bw_u_rwVwk2"


def push_invoice(file_path, business_name=None, licensee_email=None, licensee_id=None,
                 total=None, summary=None, subject=None, source=None, timeout=60):
    """Upload an invoice file to FASTAS. Returns the parsed JSON response (a dict)."""
    with open(file_path, "rb") as fh:
        content = fh.read()

    payload = {
        "file_name": os.path.basename(file_path),
        "file_base64": base64.b64encode(content).decode("ascii"),
    }
    if business_name:        payload["business_name"] = business_name
    if subject:              payload["subject"] = subject
    if licensee_email:       payload["licensee_email"] = licensee_email
    if licensee_id:          payload["licensee_id"] = licensee_id
    if total is not None:    payload["total"] = total
    if summary:              payload["summary"] = summary
    if source:              payload["source"] = source

    req = urllib.request.Request(
        FUNCTION_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": PUBLISHABLE_KEY,
            "Authorization": "Bearer " + PUBLISHABLE_KEY,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", "replace")
        try:
            return json.loads(body)
        except Exception:
            return {"error": body, "status": exc.code}
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def _cli(argv=None):
    ap = argparse.ArgumentParser(description="Push a finished invoice into FASTAS (Supabase).")
    ap.add_argument("file", help="Path to the invoice file (.xlsx / .pdf / .csv)")
    ap.add_argument("business", nargs="?", help="Business name (recommended)")
    ap.add_argument("--subject", help="Use instead of business name; the business is matched from this text")
    ap.add_argument("--licensee", help="Licensee email, e.g. sales@fastnz.nz")
    ap.add_argument("--licensee-id", help="Licensee id (alternative to --licensee)")
    ap.add_argument("--total", type=float, help="Invoice total")
    ap.add_argument("--summary", help="Short summary line")
    args = ap.parse_args(argv)

    result = push_invoice(
        args.file,
        business_name=args.business,
        subject=args.subject,
        licensee_email=args.licensee,
        licensee_id=args.licensee_id,
        total=args.total,
        summary=args.summary,
    )
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(_cli())

# FASTAS — Security headers (Render static site)

Add these response headers to the static site on Render:
**Render dashboard → your `fastas-invoicing` static site → Settings → Headers → Add**, with
**Path = `/*`** and each Name/Value below. (No code change; takes effect on next deploy.)

These headers were chosen so they DON'T break the app's third parties:
Supabase, the ElevenLabs voice widget (`unpkg.com` + `*.elevenlabs.io`), and
Cloudflare Turnstile (`challenges.cloudflare.com`). The microphone permission is
left ON because the voice "Invoice Generator" needs it.

---

## 1. Safe to enforce immediately (zero breakage risk)

| Name | Value |
|------|-------|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` |
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), geolocation=(), microphone=(self)` |

## 2. Content-Security-Policy — START IN REPORT-ONLY

Add this first as **`Content-Security-Policy-Report-Only`** (it reports violations
to the browser console but blocks NOTHING). Use the app normally for a week —
especially run a voice call and a .gar upload — and watch the console for
`Refused to … because it violates … Content Security Policy`. If nothing legit is
blocked, rename the header to `Content-Security-Policy` to enforce it.

**Name:** `Content-Security-Policy-Report-Only`
**Value (single line):**

```
default-src 'self'; base-uri 'self'; object-src 'none'; frame-ancestors 'none'; img-src 'self' data: blob: https:; font-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://challenges.cloudflare.com https://*.elevenlabs.io; connect-src 'self' https://ecgvkifvlrcfrnqbades.supabase.co wss://ecgvkifvlrcfrnqbades.supabase.co https://*.elevenlabs.io wss://*.elevenlabs.io https://challenges.cloudflare.com; media-src 'self' blob: https://*.elevenlabs.io; frame-src https://challenges.cloudflare.com https://*.elevenlabs.io; worker-src 'self' blob:
```

Notes:
- `'unsafe-inline'` for `script-src` is required because the app uses inline
  `<script>` blocks and inline event handlers. So CSP is NOT your primary XSS
  defence (the `esc()` output-escaping we added is). CSP's value here is the
  `connect-src` allow-list, which stops a successful injection from exfiltrating
  data to an attacker's server, plus blocking external script loads.
- If you ever remove the ElevenLabs widget, delete the `*.elevenlabs.io` and
  `unpkg.com` entries to tighten it further.

---

## Verify after applying
- https://securityheaders.com — grade should jump to A/B.
- https://observatory.mozilla.org — re-scan the live URL.

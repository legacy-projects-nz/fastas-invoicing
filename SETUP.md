# FASTAS Invoicing — app, pricing, training & admin

A static front-end (deploy on Render) backed by Supabase for auth, pricing and
fire-safety training reports.

## Pages (the four buttons)

| Page | Who | What |
|------|-----|------|
| `index.html` | Logged-in staff | Landing with **4 buttons**: Invoice Generator (voice), Invoice Changes (WhatsApp), **Pricing**, **Training**. Real Supabase email/password login replaces the old shared password. |
| `pricing.html` | Admin + Licensee | Edit any item price. Saves to Supabase; feeds the invoice flow. |
| `training.html` | **Public** (kiosk) | Business owner fills in their details + attendees. On submit, generates the report + certificates and emails them out. Leave this open on the on-site desktop. |
| `admin.html` | Admin only | Users & roles, training reports (download PDFs), report-template upload, pricing link. |

## Supabase project

- Project: **fastas - fire safety** (`ecgvkifvlrcfrnqbades`), region ap-southeast-2 (Sydney).
- URL: `https://ecgvkifvlrcfrnqbades.supabase.co`
- Publishable key is embedded in the HTML (safe to expose — it only allows what RLS permits).

### Tables
- `profiles` — one per user, with `role` = `admin` | `licensee`.
- `pricing_items` — seeded from your InventoryItems CSV (39 items).
- `training_reports` + `training_attendees` — generated from the training form.
- `report_templates` — your uploaded master .docx template (on file).
- Storage buckets (private): `templates`, `reports`, `certificates`.

### Edge functions
- `prices` — public read API for the invoice/voice flow: `GET /functions/v1/prices` (optional `?code=FR`). Returns live prices as JSON.
- `submit-training` — receives the form, generates the report PDF + per-attendee certificate PDFs, stores them, emails them.
- `admin-users` — admin-only user management (create/list/set-role/delete).

## Your admin login
- Email: **jeremybotting@gmail.com**
- Temp password: **FastasAdmin#2026** — change it after first sign-in (Supabase → Authentication, or just re-create yourself).

## ⚠️ Before training emails will send: add a Resend key
Emails are sent via [Resend]. Until a key is set, reports/certs are still
generated and stored — they just aren't emailed (status shows `generated`).

1. Create a Resend account, verify the **fastnz.nz** domain.
2. Supabase → Project Settings → Edge Functions → Secrets, add:
   - `RESEND_API_KEY` = your key
   - `EMAIL_FROM` = `FAST NZ <noreply@fastnz.nz>`
3. Done — new submissions email automatically (status becomes `emailed`).

## Deploy
Upload the `FASTAS/` folder to your Render static site (publish dir `.`).
`training.html` is public; the other pages require login.

## Security recommendations
See the "Boost security" notes below / ask Claude. Key ones:
- Turn OFF open sign-up in Supabase Auth (create users from the admin portal instead).
- Enable leaked-password protection and a min password length in Auth settings.
- Enable MFA for admin accounts.
- Verify the Resend domain so emails aren't spoofable.

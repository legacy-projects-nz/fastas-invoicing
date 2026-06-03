# FASTAS — step-by-step guide for each area

Logins created for you:
- **Admin** — jeremybotting@gmail.com / `FastasAdmin#2026`
- **FASTNZ - Dunedin licensee** — sales@fastnz.nz / `Sa92018201!` (owns all 39 existing prices)
(Change the admin password after first sign-in.)

---

## 0. One-time setup (do these once)

1. **Deploy** the `FASTAS/` folder to your Render static site (publish dir `.`).
2. **Turn off open sign-up:** Supabase → Authentication → Providers → Email → turn OFF "Allow new users to sign up". (Accounts are created from the admin portal instead.)
3. **Enable email security:** Authentication → Policies → turn on leaked-password protection + a minimum password length.
4. **Email sending (so training emails go out):** create a Resend account, verify the `fastas.nz` domain, then in Supabase → Project Settings → Edge Functions → Secrets add:
   - `RESEND_API_KEY` = your Resend key
   - `EMAIL_FROM` = `FAST AS <support@fastas.nz>`
5. **(Optional) Lock CORS to your site:** add secret `ALLOWED_ORIGINS` = `https://your-site.onrender.com`.
6. **(Optional) Spam-protect the training form:** create a Cloudflare Turnstile widget, paste the **site key** into `TURNSTILE_SITEKEY` near the top of `training.html`, and add the **secret** as Supabase secret `TURNSTILE_SECRET`.

---

## 1. Admin portal  (`/admin.html` — admins only)

How to open it: sign in on the home page as the admin, then click **"⚙ Admin portal →"** under the four buttons (or go straight to `/admin.html`).

**Add a user (licensee or another admin)**
1. Open the **Users & roles** tab.
2. Fill name, email, a temporary password, pick the role, click **Add user**.
3. Share the password with them; they sign in on the home page.

**Change or remove a user**
1. Users & roles tab → change the **role dropdown** next to anyone, or click **Remove**.

**View / download training reports & certificates**
1. Open the **Training reports** tab.
2. Click **Download** to get the business report PDF.
3. Click **Show** under Certificates, then a name, to download that attendee's certificate. A ✓ means it was emailed.
4. **Delete** removes a report (and its attendees).

**Upload your master report template**
1. Open the **Report template** tab → choose your `.docx` → **Upload template**. (Kept on file for reference.)

**Edit any licensee's prices** — see section 2 (as admin you also get a licensee picker).

---

## 2. Pricing  (`/pricing.html`)

**As a licensee (e.g. FAST NZ):** you only ever see **your own** price list.
1. Click the **Pricing** button on the home page.
2. Type a new price in any row → the save bar appears → **Save changes**.
3. Use the search box to find an item; **Show inactive** to see disabled items.

**As an admin:** you get a **"Viewing prices for:"** licensee picker.
1. Pick the licensee whose list you want.
2. Edit prices the same way, or click **+ Add item** to add a code/description/price (used when setting up a new licensee's empty list).

Saved prices feed the invoice flow automatically (see section 4).

---

## 3. Training kiosk  (`/training.html` — public, no login)

Leave this open on the desktop you leave with the business owner.
1. They fill in **business & site details** (the report is emailed to the business email they enter).
2. They add each **attendee**: first name, last name, email, position. **+ Add another attendee** for more.
3. Pick the training type (fire safety / fire warden / both).
4. **Submit & generate certificates.** The system then:
   - creates the **business training report PDF**,
   - creates a **certificate PDF per attendee**,
   - emails the report to the business and each certificate to its attendee,
   - and the report appears in the admin portal.
5. The screen resets for the next business via **Add another business**.

(You can also reach this from the **Training** button on the home page.)

---

## 4. Invoice flow — using live prices

Your invoice/voice automation reads current prices from:

```
GET https://ecgvkifvlrcfrnqbades.supabase.co/functions/v1/prices?email=sales@fastnz.nz
```

- Returns every active item for that licensee as `{ "prices": { "FR": 20, "T&T - SP": 6, ... } }`.
- Add `&code=FR` for a single item.
- Send the `apikey` header with the publishable key.
- For other licensees, change the `email` (or pass `?owner=<uuid>`).

Whenever a price is edited in the Pricing screen, this endpoint returns the new value immediately.

# Stripe NZ Direct Debit — setup & build plan

Goal: auto-charge each licensee weekly for the invoices they processed
(invoices × their per-invoice rate, from the Billing tab) by pulling funds from
their bank account via **NZ BECS Direct Debit**, and email them the invoice.

The database is already prepared:
- `profiles.stripe_customer_id`, `profiles.stripe_mandate_status`
- `billing_settings.autocharge_enabled` (master switch — stays **OFF** until tested)
- `billing_charges` (audit of every charge, one per licensee per week)

---

## What YOU do (≈30 min, all in dashboards — I can't do these)

1. **Create a Stripe account** at https://dashboard.stripe.com (NZ business, NZD).
2. **Enable NZ BECS Direct Debit**: Stripe Dashboard → Settings → Payment methods →
   turn on **BECS Direct Debit (New Zealand)**.
3. **Stay in TEST MODE** for now (toggle top-right). Grab the **test** keys:
   Developers → API keys → **Publishable key** (`pk_test_…`) and **Secret key** (`sk_test_…`).
4. **Set the secret in Supabase** (never in the website): Supabase Dashboard →
   Project Settings → Edge Functions → Secrets → add
   `STRIPE_SECRET_KEY = sk_test_…` (and later `STRIPE_WEBHOOK_SECRET` once I create the webhook).
5. **Send me the publishable key** (`pk_test_…`) — it's safe to put in the page; I'll
   wire it into the mandate screen.

## What I build once you've done the above

- `stripe-customer` edge function — create/find a Stripe Customer per licensee.
- `stripe-setup.html` — a page where a licensee enters their bank details and
  agrees to the BECS mandate (Stripe Elements; no bank data ever touches our DB).
- `stripe-webhook` edge function — flips `stripe_mandate_status` to **active** when
  the mandate succeeds, and records charge outcomes.
- `billing-charge` edge function — for a given week, sums that licensee's
  `billing_events` × rate and raises the Direct Debit off-session; writes to
  `billing_charges`. **Manual (super-admin button) first.**
- Super portal Billing tab: mandate status per licensee, "Send setup link", and
  "Charge this week".
- A weekly cron — **only switched on after** you've confirmed a real test charge works.

## Safe rollout (important — it's real money)

1. Test mode: set up a mandate against a **Stripe test bank account**, run one
   `billing-charge` for $1, confirm `billing_charges` shows **paid**.
2. Flip Stripe + Supabase to **live keys**, set `autocharge_enabled = true`, and
   onboard one licensee as a pilot before the rest.
3. I will only ever build the code — **I never move money or enter bank details**;
   each licensee authorises their own mandate, and you control the live switch.

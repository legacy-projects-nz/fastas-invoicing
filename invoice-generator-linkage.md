# Linking the Invoice Generator into the pipeline

**The idea you asked about:** when a licensee runs the Invoice Generator and an
invoice is produced for a business, a faint "ghost" card appears in the admin
pipeline's **Received** column for that business. It turns **solid/bold** once the
matching **.gar** file is uploaded — and the invoice info + file ride along on the
same card right through Sent → Approved → Complete.

## How it works (the wiring)

Everything is keyed by **business name + licensee**. Three sources feed one card:

1. **Invoice Generator** → calls the `invoice-intake` endpoint → writes a
   `generated_invoices` row. Card appears **ghost** (no .gar yet).
2. **.gar upload** (licensee or admin) → now requires choosing the **business** →
   writes `patguard_files.business_id`. Card becomes **solid**.
3. **Build** (admin sends invoice/reports) → `documents` for that business →
   card moves to **Sent**, carrying the invoice info + .gar download.

Because all three match on the same business name, they collapse into **one card**
that progresses through the board.

## Endpoint the invoice flow calls

```
POST https://ecgvkifvlrcfrnqbades.supabase.co/functions/v1/invoice-intake
Header: apikey: sb_publishable_qGgoGsfKwLELehUzbC25Bw_u_rwVwk2
Body (JSON):
{
  "licensee_email": "sales@fastnz.nz",   // or "licensee_id": "<uuid>"
  "business_name":  "Acme Ltd",          // REQUIRED — must match the .gar's business
  "summary":        "FEC x5, FR, Site Fee",  // optional, shown on the card
  "total":          95,                    // optional
  "file_url":       "https://…/invoice.pdf"  // optional link to the emailed PDF
}
```

It resolves the licensee, inserts a `generated_invoices` row, and returns `{ok:true}`.
(Verified working.)

## Where to add the call

In whatever assembles/sends the invoice (the automation or Claude step after the
ElevenLabs conversation), add one HTTP POST to the URL above right after the
invoice is generated/emailed — passing the business name and, ideally, the link to
the emailed PDF as `file_url`. That single call lights up the pipeline card.

## The one thing to keep consistent

The **business name** must be spelled the same across the Invoice Generator call,
the .gar upload, and the admin Build step — that's the key that links them. The
.gar upload and Build both now use a **business picker** (existing businesses for
that licensee, or “add new”), so names stay consistent. Have the Invoice Generator
use the same business name the licensee selected.

# Make invoice generation use Supabase pricing (per licensee)

**Goal:** the invoice builder currently takes unit prices from the static
`InventoryItems` CSV. Switch it so unit prices come from the live Supabase
price list for the licensee. Everything else in the flow stays the same.

The orchestration is unchanged:
`ElevenLabs conversation → Claude builds the invoice`.
Only the **price source** changes.

---

## 1. The price source

Before (or while) building the invoice, fetch the licensee's current prices:

```
GET https://ecgvkifvlrcfrnqbades.supabase.co/functions/v1/prices?email=sales@fastnz.nz
Header:  apikey: sb_publishable_qGgoGsfKwLELehUzbC25Bw_u_rwVwk2
```

`sales@fastnz.nz` = FASTNZ – Dunedin licensee. For a different licensee, change
the `email` (or pass `?owner=<uuid>`).

Response:

```json
{
  "owner": "e8e2472a-…",
  "updated": "2026-06-03T…Z",
  "count": 30,
  "prices": { "FR": 20, "T&T - SP": 6, "T&T - 3P": 18, "FEC - Testing": 15, "Site Fee": 45, "Site Fee - Wider": 65, "T&T - MW": 25, … },
  "items": [ { "item_code": "FR", "item_name": "Fire - Report", "unit_price": 20, "status": "active" }, … ]
}
```

Use the `prices` object as the authoritative `ItemCode → unit price` lookup.

---

## 2. Where to plug it in

Pick whichever matches your setup:

- **If an automation (Make / Zapier / n8n / a script) assembles the invoice:**
  add one HTTP GET step that calls the URL above, then pass the returned JSON
  into the Claude step as the price list (replacing the CSV prices).

- **If a Claude prompt builds the invoice directly:** give that step the JSON
  (fetched by the automation) and add the instruction block in section 3, or
  give Claude a tool/webhook that calls the endpoint itself.

---

## 3. Instruction block to add to the invoice-builder prompt

> **PRICING — authoritative source.**
> Do NOT use the InventoryItems CSV for unit prices. The CSV is only for which
> item codes exist and their descriptions. For every line item, take the unit
> price from the Supabase price list provided as `prices` (an object of
> `ItemCode → price`), fetched from the FASTAS `prices` API for this licensee
> (`sales@fastnz.nz`).
>
> Rules:
> - Match each line's ItemCode exactly to a key in `prices` and use that value.
> - Test & Tag must use the right code/rate: `T&T - SP` (single phase),
>   `T&T - 3P` (three phase), `T&T - MW` (microwave).
> - `FR` (Fire Report) is auto-added once per invoice — price from `prices`.
> - Site fee: `Site Fee` (inner Dunedin) or `Site Fee - Wider` — price from `prices`.
> - If an ItemCode on the invoice is NOT present in `prices`, do not guess a
>   price — flag it for the admin to add in the Pricing screen.
> - Reference field stays `FASTNZ - Dunedin`.

---

## 4. Confirm the loop works

1. Open the Pricing screen, change `FR` from 20 to 21, Save.
2. Call `…/functions/v1/prices?email=sales@fastnz.nz&code=FR` — it returns 21.
3. The next generated invoice prices FR at 21.

Caching: the API caches for ~30 seconds, so a freshly edited price appears
within half a minute.

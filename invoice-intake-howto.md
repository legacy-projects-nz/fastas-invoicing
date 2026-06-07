# Pushing a generated invoice onto the pipeline

After your invoice is created/emailed (ElevenLabs → Claude → Excel → email), make **one HTTP POST** to the
`invoice-intake` function. That creates a `generated_invoices` record, which appears on the matching
business tile in the admin Invoice & Report pipeline (and auto-creates a Sales Pipeline tile if there
isn't one).

## Endpoint
```
POST https://ecgvkifvlrcfrnqbades.supabase.co/functions/v1/invoice-intake
```

## Headers
```
Content-Type: application/json
apikey: sb_publishable_qGgoGsfKwLELehUzbC25Bw_u_rwVwk2
Authorization: Bearer sb_publishable_qGgoGsfKwLELehUzbC25Bw_u_rwVwk2
```

## Body (JSON)
| field           | required | notes |
|-----------------|----------|-------|
| `business_name` | one of these* | The business the invoice is for. Best if you can pass it directly. |
| `subject`       | one of these* | The email subject. Used to find the business if `business_name` is missing. |
| `file_name`     | optional | Filename, also used as a matching hint. |
| `licensee_email`| recommended | The licensee the business belongs to (e.g. `sales@fastnz.nz`). Or pass `licensee_id`. Optional if there's only one licensee. |
| `total`         | optional | Invoice total (number). Shows on the tile. |
| `summary`       | optional | Short line summary. |
| `file_url`      | optional | Link to the invoice file. |
| `source`        | optional | Defaults to `invoice-generator`. |

\* Provide **`business_name`** OR **`subject`** (one is enough). `business_name` is the most reliable.

## How matching works
The function matches your text against the licensee's existing businesses, in order:
1. **Exact** name (case-insensitive).
2. **Contains** — the business name appears inside your text (or vice-versa).
3. **Token coverage with typo tolerance** — e.g. a subject of *"Invoice for Tech Ion Group - March service"*
   still matches the business **"Tech Iron Group"** (Ion≈Iron handled by edit-distance).

If nothing matches, it still records the invoice using the text you sent (so it's never lost) — it just
won't auto-attach to an existing tile.

## Example
```json
{
  "subject": "Invoice for Tech Iron Group - March service",
  "licensee_email": "sales@fastnz.nz",
  "total": 234.50,
  "summary": "FEC x12, T&T x40",
  "file_url": "https://your-store/invoice-tech-iron.xlsx"
}
```

## Success response
```json
{ "ok": true, "id": "…", "business_name": "Tech Iron Group", "matched": true, "match_type": "cover(1.00)" }
```

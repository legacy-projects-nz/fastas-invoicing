# Push a generated invoice straight into Supabase → onto the tile

No Google Drive, no email round-trip. When your script creates the invoice, make **one HTTP POST**
to the `invoice-intake` function with the file itself. The function:
1. stores the file in Supabase Storage (the private `invoices` bucket),
2. matches it to the right business (even with a messy subject / typo),
3. creates a `generated_invoices` record → it shows on that business's tile in the admin pipeline,
   downloadable, and auto-creates a Sales Pipeline tile if one doesn't exist.

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
| field           | notes |
|-----------------|-------|
| `business_name` | The business (best to pass directly). OR pass `subject`. |
| `subject`       | Email/invoice subject — used to find the business if `business_name` is missing. |
| `file_base64`   | **The invoice file**, base64-encoded. Pair with `file_name`. The file is stored in Supabase. |
| `file_name`     | e.g. `Tech Iron Group - March.xlsx` (also used as a matching hint). |
| `file_url`      | Alternative to base64: a link to the file. The function fetches it and stores it in Supabase. |
| `licensee_email`| The licensee (e.g. `sales@fastnz.nz`). Or `licensee_id`. Optional if only one licensee. |
| `total`         | Invoice total (number) — shows on the tile. |
| `summary`       | Optional short line. |

You only need **one of** `business_name`/`subject`, and (optionally) **one of** `file_base64`/`file_url`.

## Example (with the file)
```json
{
  "business_name": "Tech Iron Group",
  "licensee_email": "sales@fastnz.nz",
  "total": 234.50,
  "file_name": "Tech Iron Group - March.xlsx",
  "file_base64": "UEsDBBQABgAIAAAAIQ...."
}
```

## Matching
exact → contains → token coverage with typo tolerance (e.g. a subject "Tech Ion Group" matches the
business "Tech Iron Group"). If nothing matches it still records the invoice with the text you sent.

## Response
```json
{ "ok": true, "id": "…", "business_name": "Tech Iron Group", "matched": true,
  "match_type": "cover(1.00)", "file_stored": true, "file_path": "…/…-Tech_Iron_Group_-_March.xlsx" }
```

## So your script just does, at the end:
1. produce the invoice file (xlsx/pdf),
2. base64-encode it,
3. POST the JSON above.

That's it — it lives in Supabase and appears on the tile. (Nothing needs Google Drive or email.)

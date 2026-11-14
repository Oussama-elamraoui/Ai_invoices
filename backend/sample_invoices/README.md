# Sample invoice batch

All names, tax IDs, and invoice details in these files are fictional and for
testing only. Regenerate the PDFs and upload ZIP with:

```bash
cd backend
python script/generate_sample_invoices.py
```

The script uses only the Python standard library.

## Files and test cases

- `01_standard_mad.pdf` — complete invoice with two line items and 20% tax.
  Expected subtotal MAD 2,140.00; tax MAD 428.00; total MAD 2,568.00.
- `02_mixed_tax_eur.pdf` — EUR invoice with 10% and 20% tax lines.
  Expected subtotal EUR 270.00; tax EUR 42.00; total EUR 312.00.
- `03_incomplete_review.pdf` — missing invoice number; use it to test validation,
  editing a draft, and preventing confirmation until required data is supplied.
- `04_multi_page.pdf` — one invoice across two pages, to test multi-page PDF
  extraction. Expected subtotal MAD 10,590.00; tax MAD 2,968.00; total MAD
  13,558.00.
- `05_rif_tech_mad.pdf` — complete MAD invoice with supplier/client addresses
  and tax IDs, payment details, and three line items. Expected subtotal MAD
  23,450.00; tax MAD 4,600.00; total MAD 28,050.00.
- `06_blue_dune_mad.pdf` — complete MAD invoice with supplier/client addresses
  and tax IDs, payment details, and three line items. Expected subtotal MAD
  6,200.00; tax MAD 1,240.00; total MAD 7,440.00.

## Manual app test

1. Start the backend and frontend using the commands in the repository README.
   Set `OPENAI_API_KEY` in `backend/.env`; extraction and correction suggestions
   require an API key.
2. Open the frontend, choose **Upload invoices**, and select
   `backend/sample_invoices/sample_invoices.zip`.
3. Check that the upload appears as a job and moves from processing to completed.
   Six drafts should be created. Extraction is AI-based, so compare values
   against each PDF rather than expecting perfect OCR.
4. Open the review queue. Check supplier, client, invoice number/date, currency,
   each line's quantity, unit price, and tax rate. If a supplier or client is not
   already listed, use **Add** in the review form to create it. For the
   incomplete invoice, enter a test invoice number (for example,
   `DEMO-2026-003`) before confirming.
5. Confirm the complete drafts and check **Invoices** for the saved records and
   calculated totals. Compare them with the expected amounts above. Do not
   confirm a draft until its values and entities are correct.
6. To test upload errors separately, try a non-ZIP file, then a valid ZIP that
   contains only an unsupported file type; the former should be rejected at
   upload, and the latter should result in a failed processing job.

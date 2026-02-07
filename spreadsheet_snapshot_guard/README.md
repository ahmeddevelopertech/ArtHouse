# Spreadsheet Snapshot Guard (Odoo 17 Enterprise)

Fixes crashes like:

`json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)`

caused by empty or invalid `spreadsheet_data` on Spreadsheet Dashboards/Documents.

## What it does
- Overrides `spreadsheet.mixin._get_spreadsheet_snapshot()`
- If `spreadsheet_data` is empty/whitespace or invalid JSON:
  - returns `{}` to avoid crashing the UI
  - writes `'{}'` back (best-effort) to repair the record

## Install
- Copy module folder to your addons path
- Update Apps list
- Install **Spreadsheet Snapshot Guard**

No database manual edits required.

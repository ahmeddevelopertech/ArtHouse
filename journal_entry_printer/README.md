# Journal Entry Printer - Odoo 17 Addon

This module enables accountants to print journal entries across all branches (companies) in Odoo 17.

## Features

- Print journal entries across branches
- Custom report format with professional layout
- Shows all journal entry details in a clear format
- Works with multi-company environments
- Simple integration with existing Odoo interface

## Installation

1. Place the `journal_entry_printer` folder in your Odoo addons path
2. Restart your Odoo server
3. Go to Apps > Update Apps List
4. Search for "Journal Entry Printer" and click Install

## Usage

1. Open any journal entry
2. Click on "Print Journal Entry" button
3. The custom journal entry report will be generated in PDF format

## Troubleshooting

If you encounter "Access Error" messages:

1. Make sure you are using the "Accountant" group (not just "Adviser")
2. Verify that the record rules are properly set up
3. If needed, manually disable the default "Account Entry" rule:
   - Go to Settings > Technical > Record Rules
   - Find the rule named "Account Entry" (in account.move model)
   - Disable it (uncheck the "Active" box)

## Compatibility

This module is compatible with Odoo 17 Enterprise Edition.
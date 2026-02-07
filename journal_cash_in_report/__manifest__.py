# -*- coding: utf-8 -*-
{
    "name": "Cash In by Journal (Payments Pivot)",
    "version": "17.0.1.2.0",
    "category": "Accounting",
    "summary": "Dynamic report: inbound posted customer payments by journal (list/pivot/graph) with Amount totals",
    "depends": ["account"],
    "data": [
        "views/account_payment_cash_in_search.xml",
        "views/account_payment_cash_in_views.xml",
        "views/account_payment_cash_in_action.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
}

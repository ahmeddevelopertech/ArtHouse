# -*- coding: utf-8 -*-
import json

from odoo import models
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    # -----------------------------
    # Small safe utils (no QWeb probing)
    # -----------------------------
    def _contract_placeholder(self):
        return "—"

    def _contract_data_uri_from_logo(self, logo_value):
        if not logo_value:
            return ""
        try:
            if isinstance(logo_value, bytes):
                logo_value = logo_value.decode()
            return "data:image/png;base64,%s" % (logo_value or "")
        except Exception:
            return ""

    def _contract_format_date_dict(self, date_value):
        if not date_value:
            return {"raw": "", "iso": ""}
        iso = ""
        raw = ""
        try:
            iso = date_value.isoformat()
        except Exception:
            iso = ""
        try:
            raw = date_value.strftime("%Y/%m/%d")
        except Exception:
            raw = iso or ""
        return {"raw": raw or "", "iso": iso or ""}

    def _contract_truncate(self, text, limit=220):
        if not text:
            return ""
        txt = str(text).strip()
        if len(txt) <= limit:
            return txt
        return txt[: limit - 1].rstrip() + "…"

    def _contract_company_hotline(self):
        self.ensure_one()
        company = self.company_id
        hotline = company.phone or company.partner_id.phone or company.partner_id.mobile or ""
        return hotline or self._contract_placeholder()

    # -----------------------------
    # Branding payload for header/footer + watermark
    # -----------------------------
    def _get_company_branding_payload(self):
        self.ensure_one()
        company = self.company_id

        logo_src = self._contract_data_uri_from_logo(company.logo)
        has_logo = bool(logo_src)
        has_watermark = bool(logo_src)

        # company_line (address-ish)
        bits = []
        if company.street:
            bits.append(company.street)
        if company.city:
            bits.append(company.city)
        if company.state_id and company.state_id.name:
            bits.append(company.state_id.name)
        if company.country_id and company.country_id.name:
            bits.append(company.country_id.name)
        company_line = " - ".join([b for b in bits if b]) or (company.website or "").strip() or self._contract_placeholder()

        # branch block (no hardcode)
        branch_1 = company.name or self._contract_placeholder()
        branch_2 = (company.city or (company.state_id and company.state_id.name) or "").strip() or self._contract_placeholder()
        branch_3 = (company.country_id and company.country_id.name or "").strip() or self._contract_placeholder()

        hotline_text = self._contract_company_hotline()
        hotline_label = "HOTLINE "

        # footer lines (no hardcode)
        footer_line_1 = self._contract_placeholder()
        footer_line_2 = self._contract_placeholder()
        footer_line_3 = self._contract_placeholder()

        if company.report_footer:
            lines = [l.strip() for l in str(company.report_footer).splitlines() if l.strip()]
            if lines:
                footer_line_1 = lines[0]
            if len(lines) > 1:
                footer_line_2 = lines[1]
            if len(lines) > 2:
                footer_line_3 = lines[2]
        else:
            addr_bits = []
            if company.street:
                addr_bits.append(company.street)
            if company.street2:
                addr_bits.append(company.street2)
            if company.city:
                addr_bits.append(company.city)
            if company.state_id and company.state_id.name:
                addr_bits.append(company.state_id.name)
            if company.country_id and company.country_id.name:
                addr_bits.append(company.country_id.name)
            footer_line_1 = " - ".join([b for b in addr_bits if b]) or self._contract_placeholder()

            contact_bits = []
            if company.website:
                contact_bits.append(company.website)
            if company.email:
                contact_bits.append(company.email)
            if company.phone:
                contact_bits.append(company.phone)
            footer_line_2 = " - ".join([b for b in contact_bits if b]) or self._contract_placeholder()

            footer_line_3 = self._contract_placeholder()

        return {
            "has_logo": has_logo,
            "logo_src": logo_src or "",
            "has_watermark": has_watermark,
            "watermark_src": logo_src or "",
            "company_line": company_line or self._contract_placeholder(),
            "branch_block_1": branch_1,
            "branch_block_2": branch_2,
            "branch_block_3": branch_3,
            "hotline_label": hotline_label,
            "hotline_text": hotline_text,
            "footer_line_1": footer_line_1,
            "footer_line_2": footer_line_2,
            "footer_line_3": footer_line_3,
        }

    # -----------------------------
    # Header data (no QWeb chaining)
    # -----------------------------
    def _get_contract_header_data(self):
        self.ensure_one()
        move = self.with_context(lang=self.env.context.get("lang"))
        partner = move.partner_id

        contract_code = ""
        if "contract_code" in move._fields:
            contract_code = move.contract_code or ""
        if not contract_code:
            contract_code = partner.ref or ""
        if not contract_code:
            contract_code = move.name or ""

        delivery_date = False
        if "delivery_date" in move._fields:
            delivery_date = move.delivery_date

        contract_type = ""
        if "contract_type" in move._fields:
            contract_type = move.contract_type or ""
        if not contract_type and move.invoice_payment_term_id:
            contract_type = move.invoice_payment_term_id.name or ""
        if not contract_type:
            contract_type = self._contract_placeholder()

        phone = partner.mobile or partner.phone or self._contract_placeholder()

        notes = move.ref or move.narration or ""
        notes = self._contract_truncate(notes, limit=220) or self._contract_placeholder()

        return {
            "contract_date": self._contract_format_date_dict(move.invoice_date),
            "customer_name": partner.name or self._contract_placeholder(),
            "contract_code": contract_code or self._contract_placeholder(),
            "delivery_address": partner.street or self._contract_placeholder(),
            "phone": phone,
            "delivery_date": self._contract_format_date_dict(delivery_date),
            "due_date": self._contract_format_date_dict(move.invoice_date_due),
            "contract_type": contract_type,
            "notes": notes,
        }

    # -----------------------------
    # Lines (fix: no QWeb idx scope issues)
    # -----------------------------
    def _get_contract_lines(self):
        self.ensure_one()
        move = self.with_context(lang=self.env.context.get("lang"))
        currency = move.currency_id

        raw_lines = (move.invoice_line_ids or move.line_ids.filtered_domain([("exclude_from_invoice_tab", "=", False)])).sorted("sequence")

        rows = []
        has_lines = False
        idx = 0

        for line in raw_lines:
            if line.display_type == "line_section":
                rows.append(
                    {
                        "row_type": "section",
                        "idx": "",
                        "statement": line.name or "",
                        "product_name": "",
                        "qty_formatted": "",
                        "unit_formatted": "",
                        "discount_amount_formatted": "",
                        "price_after_discount_formatted": "",
                        "line_total_formatted": "",
                    }
                )
                continue

            if line.display_type == "line_note":
                rows.append(
                    {
                        "row_type": "note",
                        "idx": "",
                        "statement": line.name or "",
                        "product_name": "",
                        "qty_formatted": "",
                        "unit_formatted": "",
                        "discount_amount_formatted": "",
                        "price_after_discount_formatted": "",
                        "line_total_formatted": "",
                    }
                )
                continue

            idx += 1
            has_lines = True

            qty = line.quantity or 0.0
            unit = line.price_unit or 0.0
            disc_pct = line.discount or 0.0

            gross = qty * unit
            disc_amt = gross * (disc_pct / 100.0)
            net = gross - disc_amt

            product_name = line.product_id.display_name if line.product_id else (line.product_id.name if line.product_id else "")
            if not product_name:
                product_name = self._contract_placeholder()

            rows.append(
                {
                    "row_type": "line",
                    "idx": str(idx),
                    "statement": line.name or "",
                    "product_name": product_name,
                    "qty_formatted": formatLang(self.env, qty, digits=2) or "0.00",
                    "unit_formatted": formatLang(self.env, unit, monetary=True, currency_obj=currency) or "",
                    "discount_amount_formatted": formatLang(self.env, disc_amt, monetary=True, currency_obj=currency) or "",
                    "price_after_discount_formatted": formatLang(self.env, net, monetary=True, currency_obj=currency) or "",
                    "line_total_formatted": formatLang(self.env, net, monetary=True, currency_obj=currency) or "",
                }
            )

        return {"rows": rows, "has_lines": bool(has_lines)}

    # -----------------------------
    # Totals (FIXED: computed from product lines only, formatted in Python)
    # -----------------------------
    def _get_contract_totals(self):
        self.ensure_one()
        move = self.with_context(lang=self.env.context.get("lang"))
        currency = move.currency_id

        raw_lines = (move.invoice_line_ids or move.line_ids.filtered_domain([("exclude_from_invoice_tab", "=", False)])).sorted("sequence")

        gross_before_discount = 0.0
        discount_amount_total = 0.0

        for line in raw_lines:

            qty = line.quantity or 0.0
            unit = line.price_unit or 0.0
            disc_pct = line.discount or 0.0
            gross = qty * unit
            disc_amt = gross * (disc_pct / 100.0)
            gross_before_discount += gross
            discount_amount_total += disc_amt

        net_total = gross_before_discount - discount_amount_total

        paid = (move.amount_total or 0.0) - (move.amount_residual or 0.0)
        due = move.amount_residual or 0.0


        return {
            "gross_before_discount_formatted": formatLang(self.env, gross_before_discount, monetary=True, currency_obj=currency) or "",
            "discount_amount_total_formatted": formatLang(self.env, discount_amount_total, monetary=True, currency_obj=currency) or "",
            "net_total_formatted": formatLang(self.env, net_total, monetary=True, currency_obj=currency) or "",
            "contract_total_formatted": formatLang(self.env, move.amount_total or 0.0, monetary=True, currency_obj=currency) or "",
            "paid_formatted": formatLang(self.env, paid, monetary=True, currency_obj=currency) or "",
            "due_formatted": formatLang(self.env, due, monetary=True, currency_obj=currency) or "",
        }


    # -----------------------------
    # Payments (list dict, parsing in Python only)
    # -----------------------------
    def _get_contract_payment_infos(self):
        self.ensure_one()
        move = self.with_context(lang=self.env.context.get("lang"))

        infos = []
        try:
            infos = move._get_reconciled_info_JSON_values() or []
        except Exception:
            infos = []

        res = []
        idx = 0

        if isinstance(infos, list) and infos:
            for p in infos:
                idx += 1
                amount = p.get("amount") or 0.0
                cur = move.currency_id
                cur_id = p.get("currency_id")
                if cur_id:
                    cur = self.env["res.currency"].browse(cur_id)
                res.append(
                    {
                        "idx": str(idx),
                        "date": p.get("date") or "",
                        "journal_name": p.get("journal_name") or self._contract_placeholder(),
                        "ref": p.get("name") or p.get("move_name") or p.get("ref") or self._contract_placeholder(),
                        "amount_formatted": formatLang(self.env, amount, monetary=True, currency_obj=cur) or "",
                    }
                )
            return res

        widget = move.invoice_payments_widget or "{}"
        try:
            data = json.loads(widget)
        except Exception:
            data = {}

        content = data.get("content") or []
        if not isinstance(content, list) or not content:
            return []

        for item in content:
            idx += 1
            amount = item.get("amount") or 0.0
            cur = move.currency_id
            cur_id = item.get("currency_id")
            if cur_id:
                cur = self.env["res.currency"].browse(cur_id)
            res.append(
                {
                    "idx": str(idx),
                    "date": item.get("date") or "",
                    "journal_name": item.get("journal_name") or self._contract_placeholder(),
                    "ref": item.get("ref") or item.get("name") or item.get("move_name") or self._contract_placeholder(),
                    "amount_formatted": formatLang(self.env, amount, monetary=True, currency_obj=cur) or "",
                }
            )
        return res

    # -----------------------------
    # Installments (optional)
    # -----------------------------
    def _get_contract_installments(self):
        self.ensure_one()
        move = self.with_context(lang=self.env.context.get("lang"))

        if "installment_ids" not in move._fields:
            return []

        installments = move.installment_ids
        if not installments:
            return []

        installments = installments.sorted(lambda r: (getattr(r, "due_date", False) or r.create_date or r.id))
        currency = move.currency_id

        # state labels if any
        state_labels = {}
        if "state" in installments._fields:
            sel = installments._fields["state"].selection
            try:
                sel = sel(self.env) if callable(sel) else sel
            except Exception:
                sel = []
            state_labels = dict(sel or {})

        res = []
        idx = 0
        for inst in installments:
            idx += 1
            due_date = getattr(inst, "due_date", False)
            amount = getattr(inst, "amount", 0.0) or 0.0
            state = getattr(inst, "state", "") or ""
            res.append(
                {
                    "idx": str(idx),
                    "name": inst.display_name or self._contract_placeholder(),
                    "date": due_date.strftime("%Y/%m/%d") if due_date else "",
                    "amount_formatted": formatLang(self.env, amount, monetary=True, currency_obj=currency) or "",
                    "state": state_labels.get(state, state) or self._contract_placeholder(),
                }
            )
        return res

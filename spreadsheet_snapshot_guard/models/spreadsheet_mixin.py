# -*- coding: utf-8 -*-
import json
import logging

from odoo import models

_logger = logging.getLogger(__name__)


class SpreadsheetMixin(models.AbstractModel):
    _inherit = "spreadsheet.mixin"

    def _get_spreadsheet_snapshot(self):
        """Guard against empty/invalid JSON in spreadsheet_data.

        Why:
            In Enterprise spreadsheets/dashboards, join_spreadsheet_session() calls
            _get_spreadsheet_snapshot() and does json.loads(self.spreadsheet_data).
            If spreadsheet_data is empty or corrupted, the UI crashes with JSONDecodeError.

        What this does:
            - If spreadsheet_data is empty/whitespace -> returns {} and (best-effort) writes '{}' back.
            - If spreadsheet_data is invalid JSON -> returns {} and (best-effort) writes '{}' back.

        Notes:
            Standard callers often use sudo() for reading the snapshot; we still don't force sudo here.
        """
        self.ensure_one()

        raw = (self.spreadsheet_data or "")
        if not raw or not raw.strip():
            # Best-effort auto-repair to a valid empty JSON document
            try:
                self.write({"spreadsheet_data": "{}"})
            except Exception:
                _logger.exception("Failed to repair empty spreadsheet_data for %s(%s)", self._name, self.id)
            return {}

        try:
            return json.loads(raw)
        except Exception:
            _logger.exception("Invalid spreadsheet_data JSON for %s(%s). Auto-repairing.", self._name, self.id)
            try:
                self.write({"spreadsheet_data": "{}"})
            except Exception:
                _logger.exception("Failed to repair invalid spreadsheet_data for %s(%s)", self._name, self.id)
            return {}

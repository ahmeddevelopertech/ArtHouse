from odoo.tests.common import SavepointCase
from odoo.exceptions import UserError


class TestMoveUnpostGuard(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

        # Basic accounting user (NOT account manager)
        cls.user_basic = cls.env["res.users"].create({
            "name": "Basic Accountant",
            "login": "basic_unpost_guard_oyrzbvyk",
            "email": "basic_unpost_guard_oyrzbvyk@example.com",
            "groups_id": [(6, 0, [cls.env.ref("account.group_account_user").id])],
        })

        # Account Manager user
        cls.user_manager = cls.env["res.users"].create({
            "name": "Accounting Manager",
            "login": "manager_unpost_guard_oyrzbvyk",
            "email": "manager_unpost_guard_oyrzbvyk@example.com",
            "groups_id": [(6, 0, [cls.env.ref("account.group_account_manager").id])],
        })

        # Journal
        cls.journal = cls.env["account.journal"].search(
            [("type", "=", "general"), ("company_id", "=", cls.company.id)],
            limit=1
        ) or cls.env["account.journal"].create({
            "name": "Miscellaneous",
            "code": "MOYR",
            "type": "general",
            "company_id": cls.company.id,
        })

        # Accounts (fallback if chart missing)
        cls.acc_debit = cls.env["account.account"].search(
            [("company_id", "=", cls.company.id), ("account_type", "=", "asset_current")],
            limit=1
        ) or cls.env["account.account"].create({
            "name": "Test Debit",
            "code": "TDOY",
            "account_type": "asset_current",
            "company_id": cls.company.id,
        })

        cls.acc_credit = cls.env["account.account"].search(
            [("company_id", "=", cls.company.id), ("account_type", "=", "income_other")],
            limit=1
        ) or cls.env["account.account"].create({
            "name": "Test Credit",
            "code": "TCOY",
            "account_type": "income_other",
            "company_id": cls.company.id,
        })

    def _create_posted_entry(self):
        move = self.env["account.move"].create({
            "move_type": "entry",
            "journal_id": self.journal.id,
            "line_ids": [
                (0, 0, {"name": "d", "account_id": self.acc_debit.id, "debit": 100.0, "credit": 0.0}),
                (0, 0, {"name": "c", "account_id": self.acc_credit.id, "debit": 0.0, "credit": 100.0}),
            ],
        })
        move.action_post()
        return move

    def test_basic_user_cannot_unpost_via_button_draft_for_entry(self):
        move = self._create_posted_entry().with_user(self.user_basic)
        with self.assertRaises(UserError):
            move.button_draft()

    def test_basic_user_cannot_unpost_via_write_state_draft_for_entry(self):
        move = self._create_posted_entry().with_user(self.user_basic)
        with self.assertRaises(UserError):
            move.write({"state": "draft"})

    def test_manager_can_unpost_entry(self):
        move = self._create_posted_entry().with_user(self.user_manager)
        move.button_draft()
        self.assertEqual(move.state, "draft")

    def test_basic_user_can_edit_non_state_fields_on_posted_entry(self):
        move = self._create_posted_entry().with_user(self.user_basic)
        move.write({"ref": "OK"})
        self.assertEqual(move.ref, "OK")

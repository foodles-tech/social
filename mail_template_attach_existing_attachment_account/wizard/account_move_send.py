# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

from odoo import api, models


class AccountMoveSend(models.TransientModel):
    _inherit = "account.move.send"

    @api.model
    def _match_attachment(self, re_pattern, model, res_ids):
        """Could be nice to perform regex in sql side using PGSQL `~` operator"""
        return (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_model", "=", model),
                    ("res_id", "in", res_ids),
                ],
                order="res_id",
            )
            .filtered(
                lambda attachement, pattern=re_pattern: pattern.match(attachement.name)
                is not None
            )
        )

    def _get_regex_attachment_ids(self, move):
        result = {}
        for record in self:
            object_attachment_ids = self.env["ir.attachment"].browse()
            if (
                record.mail_template_id
                and record.mail_template_id.attach_exist_document_regex
            ):
                pattern = re.compile(
                    record.mail_template_id.attach_exist_document_regex
                )
                object_attachment_ids |= self._match_attachment(
                    pattern, "account.move", move.ids
                )
            result[record.id] = object_attachment_ids
        return result

    @api.model
    def _get_invoice_extra_attachments(self, move):
        res = super()._get_invoice_extra_attachments(move)
        regex_attachments = self._get_regex_attachment_ids(move)
        if regex_attachments:
            res |= regex_attachments[self.id]
        return res

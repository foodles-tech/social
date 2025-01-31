# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import re

from odoo import api, models, tools

from odoo.addons.mail.tools.parser import parse_res_ids


class MailComposeMessage(models.TransientModel):
    _inherit = "mail.compose.message"

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

    @api.depends("composition_mode", "model", "res_domain", "res_ids", "template_id")
    def _compute_attachment_ids(self):
        for composer in self:
            composer.object_attachment_ids = self.env["ir.attachment"].browse()
            if (
                composer.template_id
                and composer.template_id.attach_exist_document_regex
            ):
                pattern = re.compile(composer.template_id.attach_exist_document_regex)
                composer.object_attachment_ids |= composer._match_attachment(
                    pattern, composer.model, parse_res_ids(composer.res_ids)
                )

    def _prepare_mail_values_dynamic(self, res_ids):
        res = super()._prepare_mail_values_dynamic(res_ids)
        self.ensure_one()
        if (
            self.template_id
            and self.template_id.attach_exist_document_regex
            and len(res_ids) > 1
        ):
            # Mass mailing case only
            pattern = re.compile(self.template_id.attach_exist_document_regex)
            attachment_per_res_id = tools.groupby(
                self._match_attachment(pattern, self.model, res_ids),
                lambda att: att.res_id,
            )
            for res_id, attachments in attachment_per_res_id:
                res[res_id].setdefault("attachment_ids", []).extend(
                    [(4, attachment.id) for attachment in attachments]
                )
        return res

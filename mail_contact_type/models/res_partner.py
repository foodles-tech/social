# Copyright 2023 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# @author Matthias Barkat <matthias.barkat@foodles.co>
# @author Alexandre Galdeano <alexandre.galdeano@foodles.co>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.osv import expression


class ResPartner(models.Model):
    _inherit = "res.partner"

    mail_contact_type_ids = fields.Many2many(
        "mail.contact.type",
        string="Mail Contact Types",
        help="Used by email template to select contacts by mail contact type",
    )

    def _find_contacts_by_mail_contact_types(self, codes):
        """
        Example of usage:
        self._find_contacts_by_mail_contact_types(
            [["customer","accounting"], "supplier"]
        )
        return contacts that are (customer and accounting) or supplier
        """
        contacts = self.env["res.partner"].browse()
        for code_list in codes:
            if not isinstance(code_list, list):
                code_list = [code_list]
            contacts |= (
                self.commercial_partner_id.child_ids | self.commercial_partner_id
            ).filtered(
                lambda contact: all(
                    code in contact.mail_contact_type_ids.mapped("code")
                    for code in code_list  # noqa: B023
                )
            )
        return contacts

    def contact_by_types(self, *codes):
        return ",".join(
            [
                str(contact.id)
                for contact in self._find_contacts_by_mail_contact_types(codes)
            ]
        )

    @api.depends("mail_contact_type_ids")
    @api.depends_context("show_mail_contact_types")
    def _compute_display_name(self):
        super()._compute_display_name()
        for record in self:
            if (
                not self._context.get("show_mail_contact_types")
                or not record.mail_contact_type_ids
            ):
                return record.display_name

            mail_contact_types_str = ", ".join(
                record.mail_contact_type_ids.mapped("name")
            )

            record.display_name = f"{record.display_name} ({mail_contact_types_str})"

    @api.model
    def _name_search(self, name, args=None, operator="ilike", limit=100, order=None):
        partners = super()._name_search(
            name, args, operator=operator, limit=limit, order=order
        )
        if self._context.get("show_mail_contact_types"):
            partners = self.search(
                expression.OR(
                    [
                        [("id", "in", partners)],
                        [("mail_contact_type_ids.name", "=ilike", name)],
                    ]
                ),
                limit=limit,
            ).ids
        return partners

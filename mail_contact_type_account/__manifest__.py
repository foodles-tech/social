# Copyright 2023 Foodles (https://www.foodles.com/)
# @author Pierre Verkest <pierreverkest84@gmail.com>
# @author Matthias Barkat <matthias.barkat@foodles.co>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Mail Contact Type Account",
    "summary": "Mail Contact Type Account",
    "version": "17.0.1.0.0",
    "development_status": "Alpha",
    "category": "Productivity/Discuss",
    "website": "https://github.com/OCA/social",
    "author": "Foodles, Odoo Community Association (OCA)",
    "maintainers": ["damdam-s"],
    "license": "AGPL-3",
    "depends": [
        "account",
        "mail_contact_type",
        "base_view_inheritance_extension",
    ],
    "data": [
        "views/account_move_send_view.xml",
    ],
    "installable": True,
    "auto_install": True,
}

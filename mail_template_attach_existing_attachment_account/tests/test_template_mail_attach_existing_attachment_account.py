# Copyright 2022 Foodles (http://www.foodles.co).
# @author Pierre Verkest <pierreverkest84@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.account.tests.test_account_move_send import TestAccountMoveSendCommon


class TestTemplateAttachExistingAttachment(TestAccountMoveSendCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.template = cls.env.ref("account.email_template_edi_invoice")

        cls.invoice_01 = cls.init_invoice("out_invoice", amounts=[1000], post=True)
        cls.invoice_02 = cls.init_invoice("out_invoice", amounts=[1000], post=True)
        cls.invoice_03_no_attachment = cls.init_invoice(
            "out_invoice", amounts=[1000], post=True
        )
        cls.attach_p1_csv1 = cls.env["ir.attachment"].create(
            {
                "name": "attach1.csv",
                "datas": "bWlncmF0aW9uIHRlc3Q=",
                "res_model": "account.move",
                "res_id": cls.invoice_01.id,
            }
        )
        cls.attach_p1_jpg = cls.env["ir.attachment"].create(
            {
                "name": "attach.jpg",
                "datas": "bWlncmF0aW9uIHRlc3Q=",
                "res_model": "account.move",
                "res_id": cls.invoice_01.id,
            }
        )
        cls.attach_p1_csv2 = cls.env["ir.attachment"].create(
            {
                "name": "attach2.csv",
                "datas": "bWlncmF0aW9uIHRlc3Q=",
                "res_model": "account.move",
                "res_id": cls.invoice_01.id,
            }
        )
        cls.attach_p1_png = cls.env["ir.attachment"].create(
            {
                "name": "attach.png",
                "datas": "bWlncmF0aW9uIHRlc3Q=",
                "res_model": "account.move",
                "res_id": cls.invoice_01.id,
            }
        )
        cls.attach_p2_csv = cls.env["ir.attachment"].create(
            {
                "name": "attach.csv",
                "datas": "bWlncmF0aW9uIHRlc3Q=",
                "res_model": "account.move",
                "res_id": cls.invoice_02.id,
            }
        )
        cls.attach_p2_png = cls.env["ir.attachment"].create(
            {
                "name": "attach.png",
                "datas": "bWlncmF0aW9uIHRlc3Q=",
                "res_model": "account.move",
                "res_id": cls.invoice_02.id,
            }
        )

    def test_default_images_attachments_from_template(self):
        self.template.attach_exist_document_regex = ".*.[png|jpg]"
        composer = self.create_send_and_print(self.invoice_01, mail_template_id=None)

        # invoice report
        self.assertEqual(len(composer.mail_attachments_widget), 1)
        composer.mail_template_id = self.template
        # invoice report + 2 images
        self.assertEqual(len(composer.mail_attachments_widget), 3)

        self.assertTrue(
            any(
                [
                    attachment["name"].endswith(".jpg")
                    for attachment in composer.mail_attachments_widget
                ]
            )
        )
        self.assertTrue(
            any(
                [
                    attachment["name"].endswith(".png")
                    for attachment in composer.mail_attachments_widget
                ]
            )
        )

        composer.action_send_and_print(allow_fallback_pdf=True)
        message = self._get_mail_message(self.invoice_01)
        self.assertTrue(len(message.attachment_ids), 3)

    def test_clear_default_images_attachments_changing_template(self):
        self.template.attach_exist_document_regex = ".*.[png|jpg]"
        composer = self.create_send_and_print(self.invoice_01)

        self.assertEqual(len(composer.mail_attachments_widget), 3)
        composer.mail_template_id = False
        self.assertEqual(len(composer.mail_attachments_widget), 1)
        composer.action_send_and_print(allow_fallback_pdf=True)
        message = self._get_mail_message(self.invoice_01)
        self.assertTrue(len(message.attachment_ids), 1)

    def test_send_email_with_default_and_manual_extra_attachment(self):
        self.template.attach_exist_document_regex = ".*.[png|jpg]"
        composer = self.create_send_and_print(self.invoice_01)

        self.assertEqual(len(composer.mail_attachments_widget), 3)
        composer.object_attachment_ids |= self.attach_p1_csv1
        composer.action_send_and_print(allow_fallback_pdf=True)
        message = self._get_mail_message(self.invoice_01)
        self.assertTrue(len(message.attachment_ids), 4)

    def test_no_pattern(self):
        self.template.attach_exist_document_regex = False
        composer = self.create_send_and_print(self.invoice_01)

        self.assertEqual(len(composer.mail_attachments_widget), 1)
        composer.action_send_and_print(allow_fallback_pdf=True)
        message = self._get_mail_message(self.invoice_01)
        self.assertTrue(len(message.attachment_ids), 1)

    def test_send_mass_mail_with_default_extra_attachment(self):
        self.template.attach_exist_document_regex = ".*.csv"
        records = self.invoice_01 | self.invoice_02 | self.invoice_03_no_attachment
        composer = self.create_send_and_print(records)
        composer.action_send_and_print(allow_fallback_pdf=True)

        message_invoice_01 = self._get_mail_message(self.invoice_01)
        message_invoice_02 = self._get_mail_message(self.invoice_02)
        message_invoice_03 = self._get_mail_message(self.invoice_03_no_attachment)

        self.assertEqual(len(message_invoice_01.attachment_ids), 3)
        self.assertTrue(
            self.attach_p1_csv1.name
            in message_invoice_01.attachment_ids.mapped("name"),
        )
        self.assertTrue(
            self.attach_p1_csv2.name
            in message_invoice_01.attachment_ids.mapped("name"),
        )

        self.assertEqual(len(message_invoice_02.attachment_ids), 2)
        self.assertTrue(
            self.attach_p2_csv.name in message_invoice_02.attachment_ids.mapped("name")
        )
        self.assertEqual(len(message_invoice_03.attachment_ids), 1)

    def test_mass_mailing_no_pattern(self):
        self.template.attach_exist_document_regex = False
        records = self.invoice_01 | self.invoice_02 | self.invoice_03_no_attachment
        composer = self.create_send_and_print(records)
        composer.action_send_and_print(allow_fallback_pdf=True)

        message_invoice_01 = self._get_mail_message(self.invoice_01)
        message_invoice_02 = self._get_mail_message(self.invoice_02)
        message_invoice_03 = self._get_mail_message(self.invoice_03_no_attachment)

        self.assertEqual(len(message_invoice_01.attachment_ids), 1)
        self.assertEqual(len(message_invoice_02.attachment_ids), 1)
        self.assertEqual(len(message_invoice_03.attachment_ids), 1)

    def test_switch_template_with_different_templates(self):
        jpg_template = self.template
        png_template = self.template.copy()
        jpg_template.attach_exist_document_regex = ".*.jpg"
        png_template.attach_exist_document_regex = ".*.png"
        composer = self.create_send_and_print(self.invoice_01, mail_template_id=None)
        self.assertEqual(len(composer.mail_attachments_widget), 1)
        composer.mail_template_id = jpg_template
        self.assertEqual(len(composer.mail_attachments_widget), 2)
        composer.mail_template_id = png_template
        self.assertEqual(len(composer.mail_attachments_widget), 2)
        composer.action_send_and_print(allow_fallback_pdf=True)
        message = self._get_mail_message(self.invoice_01)
        self.assertTrue(
            self.attach_p1_png.name in message.attachment_ids.mapped("name")
        )

from odoo import api, fields, models


class BotMessage(models.Model):
    _name = "botmsg"
    _description = "Bot Message"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "provider_timestamp desc, id desc"
    _rec_name = "display_name"

    chat_id = fields.Many2one(
        "botchat",
        required=True,
        ondelete="cascade",
        index=True,
        tracking=True,
    )
    provider = fields.Selection(related="chat_id.provider", store=True, index=True)
    messageid = fields.Char(
        string="Provider Message ID",
        required=True,
        index=True,
        tracking=True,
        help="Native message identifier from Telegram, WhatsApp, or Google Chat.",
    )
    provider_resource_name = fields.Char(
        string="Provider Resource Name",
        index=True,
        help="Canonical API resource name, such as Google Chat spaces/*/messages/*.",
    )
    display_name = fields.Char(compute="_compute_display_name", store=True, index=True)

    direction = fields.Selection(
        [
            ("inbound", "Inbound"),
            ("outbound", "Outbound"),
            ("system", "System"),
        ],
        default="inbound",
        required=True,
        index=True,
        tracking=True,
    )
    message_type = fields.Selection(
        [
            ("text", "Text"),
            ("html", "HTML"),
            ("image", "Image"),
            ("audio", "Audio"),
            ("voice", "Voice"),
            ("video", "Video"),
            ("video_note", "Video Note"),
            ("document", "Document"),
            ("sticker", "Sticker"),
            ("animation", "Animation"),
            ("location", "Location"),
            ("venue", "Venue"),
            ("contact", "Contact"),
            ("poll", "Poll"),
            ("reaction", "Reaction"),
            ("button", "Button"),
            ("interactive", "Interactive"),
            ("card", "Google Chat Card"),
            ("command", "Command"),
            ("system", "System"),
            ("unsupported", "Unsupported"),
        ],
        default="text",
        required=True,
        index=True,
        tracking=True,
    )
    state = fields.Selection(
        [
            ("received", "Received"),
            ("queued", "Queued"),
            ("sent", "Sent"),
            ("delivered", "Delivered"),
            ("read", "Read"),
            ("edited", "Edited"),
            ("deleted", "Deleted"),
            ("failed", "Failed"),
        ],
        default="received",
        required=True,
        index=True,
        tracking=True,
    )

    sender_id = fields.Char(index=True, help="Provider user, bot, or business sender ID.")
    sender_name = fields.Char(index=True)
    sender_username = fields.Char(index=True)
    sender_phone = fields.Char(index=True)
    sender_type = fields.Selection(
        [
            ("user", "User"),
            ("bot", "Bot"),
            ("business", "Business"),
            ("system", "System"),
            ("unknown", "Unknown"),
        ],
        default="unknown",
        index=True,
    )
    recipient_id = fields.Char(index=True)
    recipient_name = fields.Char()

    provider_timestamp = fields.Datetime(string="Provider Timestamp", index=True, tracking=True)
    sent_at = fields.Datetime(index=True)
    delivered_at = fields.Datetime(index=True)
    read_at = fields.Datetime(index=True)
    edited_at = fields.Datetime(index=True)
    deleted_at = fields.Datetime(index=True)

    text = fields.Text()
    html = fields.Html(string="HTML Body", sanitize=True)
    caption = fields.Text()
    summary = fields.Char()
    command = fields.Char(index=True)
    command_arguments = fields.Char()
    language_code = fields.Char()

    thread_id = fields.Char(index=True, help="Google Chat thread name or provider thread ID.")
    reply_to_id = fields.Many2one("botmsg", string="Reply To", ondelete="set null", index=True)
    reply_to_messageid = fields.Char(string="Reply To Provider Message ID", index=True)
    forwarded_from = fields.Char(index=True)
    forward_origin_json = fields.Json(string="Forward Origin", copy=False)

    media_id = fields.Char(index=True)
    media_url = fields.Char(string="Media URL")
    media_mime_type = fields.Char(string="Media MIME Type")
    media_filename = fields.Char()
    media_sha256 = fields.Char(string="Media SHA256")
    media_size = fields.Integer(string="Media Size")
    attachment_ids = fields.Many2many("ir.attachment", string="Odoo Attachments")

    location_latitude = fields.Float(digits=(10, 7))
    location_longitude = fields.Float(digits=(10, 7))
    location_address = fields.Char()
    contact_json = fields.Json(string="Contacts", copy=False)
    poll_json = fields.Json(string="Poll", copy=False)
    reaction_emoji = fields.Char()
    reaction_to_messageid = fields.Char(string="Reaction To Provider Message ID", index=True)
    entities_json = fields.Json(string="Text Entities", copy=False)
    buttons_json = fields.Json(string="Buttons", copy=False)
    cards_json = fields.Json(string="Google Chat Cards", copy=False)
    interactive_json = fields.Json(string="WhatsApp Interactive", copy=False)

    webhook_event = fields.Char(index=True)
    status_payload_json = fields.Json(string="Status Payload", copy=False)
    error_code = fields.Char(index=True)
    error_message = fields.Text()
    metadata_json = fields.Json(string="Metadata", copy=False)
    raw_payload = fields.Json(string="Raw Provider Payload", copy=False)

    _sql_constraints = [
        (
            "provider_chat_message_unique",
            "unique(provider, chat_id, messageid)",
            "Each provider message can only be stored once per chat.",
        )
    ]

    @api.depends("messageid", "text", "caption", "message_type")
    def _compute_display_name(self):
        for record in self:
            body = (record.text or record.caption or "").strip().replace("\n", " ")
            if body:
                record.display_name = body[:80]
            elif record.messageid:
                record.display_name = f"{record.message_type or 'message'}:{record.messageid}"
            else:
                record.display_name = record.message_type or "Bot Message"

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._update_chat_activity()
        return records

    def write(self, vals):
        result = super().write(vals)
        if {"provider_timestamp", "direction", "state"} & set(vals):
            self._update_chat_activity()
        return result

    def _update_chat_activity(self):
        for chat in self.mapped("chat_id"):
            messages = self.search(
                [("chat_id", "=", chat.id), ("provider_timestamp", "!=", False)],
                order="provider_timestamp desc, id desc",
                limit=1,
            )
            vals = {}
            if messages:
                vals["last_message_at"] = messages.provider_timestamp
            inbound = self.search(
                [
                    ("chat_id", "=", chat.id),
                    ("direction", "=", "inbound"),
                    ("provider_timestamp", "!=", False),
                ],
                order="provider_timestamp desc, id desc",
                limit=1,
            )
            if inbound:
                vals["last_inbound_at"] = inbound.provider_timestamp
            outbound = self.search(
                [
                    ("chat_id", "=", chat.id),
                    ("direction", "=", "outbound"),
                    ("provider_timestamp", "!=", False),
                ],
                order="provider_timestamp desc, id desc",
                limit=1,
            )
            if outbound:
                vals["last_outbound_at"] = outbound.provider_timestamp
            if vals:
                chat.write(vals)

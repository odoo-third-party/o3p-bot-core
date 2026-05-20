from odoo import api, fields, models


class BotChat(models.Model):
    _name = "botchat"
    _description = "Bot Chat"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "last_message_at desc, name, id"
    _rec_name = "display_name"

    provider = fields.Selection(
        [
            ("google_chat", "Google Chat"),
            ("telegram", "Telegram"),
            ("whatsapp", "WhatsApp"),
        ],
        required=True,
        index=True,
        tracking=True,
    )
    chatid = fields.Char(
        string="Provider Chat ID",
        required=True,
        index=True,
        tracking=True,
        help="Native conversation identifier from the provider API.",
    )
    name = fields.Char(index=True, tracking=True)
    display_name = fields.Char(compute="_compute_display_name", store=True, index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company, index=True)

    chat_type = fields.Selection(
        [
            ("direct", "Direct"),
            ("group", "Group"),
            ("supergroup", "Telegram Supergroup"),
            ("channel", "Telegram Channel"),
            ("space", "Google Chat Space"),
            ("room", "Google Chat Room"),
            ("dm", "Google Chat DM"),
            ("business", "WhatsApp Business Chat"),
            ("unknown", "Unknown"),
        ],
        default="unknown",
        required=True,
        index=True,
        tracking=True,
    )
    external_thread_key = fields.Char(
        string="External Thread Key",
        index=True,
        help="Google Chat external thread key or equivalent provider thread grouping key.",
    )
    provider_resource_name = fields.Char(
        string="Provider Resource Name",
        index=True,
        help="Canonical API resource name, such as Google Chat spaces/*.",
    )
    title = fields.Char(help="Provider title for groups, spaces, channels, or rooms.")
    description = fields.Text()
    avatar_url = fields.Char(string="Avatar URL")
    invite_link = fields.Char(string="Invite Link")
    username = fields.Char(index=True, help="Telegram username or provider conversation handle.")
    phone_number = fields.Char(index=True, help="WhatsApp user or business phone number.")
    phone_number_id = fields.Char(index=True, help="WhatsApp Business phone number ID.")
    first_name = fields.Char(help="First name for one-to-one Telegram or WhatsApp chats.")
    last_name = fields.Char(help="Last name for one-to-one Telegram or WhatsApp chats.")
    locale = fields.Char(help="Provider locale/language code when available.")

    member_count = fields.Integer()
    is_forum = fields.Boolean(help="Telegram forum-enabled supergroup.")
    is_read_only = fields.Boolean(help="Provider marks the chat/channel/space as read-only.")
    is_bot_member = fields.Boolean(default=True, help="Whether the configured bot is currently a member.")
    last_message_at = fields.Datetime(index=True)
    last_inbound_at = fields.Datetime(index=True)
    last_outbound_at = fields.Datetime(index=True)

    message_ids = fields.One2many("botmsg", "chat_id", string="Messages")
    message_count = fields.Integer(compute="_compute_message_count")
    metadata_json = fields.Json(string="Metadata", copy=False)
    raw_payload = fields.Json(string="Raw Provider Payload", copy=False)

    _sql_constraints = [
        (
            "provider_chatid_unique",
            "unique(provider, chatid)",
            "Each provider chat ID can only be stored once.",
        )
    ]

    @api.depends("name", "title", "chatid", "provider")
    def _compute_display_name(self):
        provider_labels = dict(self._fields["provider"].selection)
        for record in self:
            label = record.name or record.title or record.chatid or "Bot Chat"
            provider = provider_labels.get(record.provider, record.provider or "")
            record.display_name = f"{label} ({provider})" if provider else label

    def _compute_message_count(self):
        grouped = self.env["botmsg"].read_group(
            [("chat_id", "in", self.ids)],
            ["chat_id"],
            ["chat_id"],
        )
        counts = {item["chat_id"][0]: item["chat_id_count"] for item in grouped}
        for record in self:
            record.message_count = counts.get(record.id, 0)

{
    "name": "O3P Bot Core",
    "summary": "Unified bot chat and message storage for Google Chat, Telegram, and WhatsApp.",
    "description": (
        "O3P Bot Core provides normalized Odoo models for bot conversations and messages "
        "across Google Chat, Telegram, and WhatsApp. It stores common chat/message fields "
        "as searchable columns and keeps provider-specific API payloads in JSON fields."
    ),
    "version": "19.0.1.0.0",
    "category": "Productivity/Discuss",
    "author": "O3P",
    "website": "https://github.com/o3p/o3p-bot-core",
    "license": "LGPL-3",
    "sequence": 20,
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/botmsg_views.xml",
        "views/botchat_views.xml",
        "views/menu_views.xml",
    ],
    "images": [
        "thumb.png",
        "static/description/thumbnail.svg",
        "static/description/banner.svg",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

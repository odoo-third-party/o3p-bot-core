# O3P Bot Core

O3P Bot Core is an Odoo 19 addon for storing bot conversations and messages from
Google Chat, Telegram, and WhatsApp in a shared schema.

It is intended for Ubuntu/Debian Odoo servers where addons are installed from
the filesystem and managed through the Odoo service.

## Models

- `botchat`: provider chats, groups, spaces, channels, and WhatsApp business conversations.
- `botmsg`: provider messages, sender/recipient metadata, delivery state, media, structured payloads, and raw API data.

The models keep common data in searchable columns and preserve provider-specific fields in JSON payload fields.

## Provider Coverage

- Google Chat: spaces, rooms, DMs, threads, cards, buttons, and resource names.
- Telegram: private chats, groups, supergroups, channels, commands, entities, replies, media, contacts, locations, and polls.
- WhatsApp Business: phone number IDs, contacts, interactive payloads, media IDs, reactions, delivery status, and read receipts.

## Usage

Install on an Ubuntu/Debian Odoo host with:

```bash
curl -fsSL https://raw.githubusercontent.com/odoo-third-party/o3p-module-install-script/sources/run.sh | bash -s -- --config "https://raw.githubusercontent.com/odoo-third-party/o3p-bot-core/o3p-bot-core.o3p.json"
```

Then open **Bot Core** in the Odoo main menu. Use **Chats** for provider
conversations and **Messages** for the message/event records linked to each
chat.

The addon is a storage layer. Provider connectors can create or update
`botchat` and `botmsg` records while keeping the original webhook/API payloads in
`raw_payload` and provider-specific JSON fields.

# O3P Bot Core

O3P Bot Core is an Odoo 19 addon that provides a shared data model for bot
conversations and messages across Google Chat, Telegram, and WhatsApp.

The module does not implement provider API clients. It gives those clients a
clean Odoo-native storage layer for chats, groups, spaces, channels, message
content, media metadata, delivery status, structured payloads, and raw webhook
data.

It is intended for Ubuntu/Debian Odoo servers where addons are installed from
the filesystem and managed with the Odoo service.

## What It Adds

- `botchat`: one normalized record for a provider chat, group, channel, space,
  room, direct message, or WhatsApp business conversation.
- `botmsg`: one normalized record for each provider message, linked to its
  `botchat`.
- Bot Core menu entries with list, form, and search views.
- Access rules for internal users and full system-user administration.
- Odoo app metadata, icon, thumbnail, banner, and HTML description.

## Supported Providers

The schema is designed around fields commonly exposed by:

- Google Chat: spaces, rooms, DMs, resource names, threads, cards, buttons, and
  event payloads.
- Telegram: private chats, groups, supergroups, channels, usernames, commands,
  text entities, replies, media, locations, contacts, and polls.
- WhatsApp Business: phone number IDs, contacts, interactive messages, media
  IDs, status webhooks, reactions, delivery receipts, and read receipts.

Provider-specific data that does not fit the shared schema is retained in JSON
fields, so integrations can preserve the full API payload.

## Repository Layout

```text
o3p_bot_core/
  __manifest__.py
  models/
    botchat.py
    botmsg.py
  security/
    ir.model.access.csv
  views/
    botchat_views.xml
    botmsg_views.xml
    menu_views.xml
  static/description/
    icon.png
    icon.svg
    banner.svg
    thumbnail.svg
    index.html
  thumb.png
```

## Installation

On Ubuntu/Debian Odoo hosts, install with:

```bash
curl -fsSL https://raw.githubusercontent.com/odoo-third-party/o3p-module-install-script/sources/run.sh | bash -s -- --config "https://raw.githubusercontent.com/odoo-third-party/o3p-bot-core/o3p-bot-core.o3p.json"
```

The installer is expected to copy the addon into the configured Odoo addons
path, refresh the app list, and prepare the module for installation or upgrade.

For a manual command-line upgrade after the addon is already available in an
Odoo addons path:

```bash
/opt/odoo19/venv/bin/python3 /opt/odoo19/odoo-bin \
  -c /etc/odoo19.conf \
  -d YOUR_DATABASE \
  -u o3p_bot_core \
  --stop-after-init \
  --workers=0
```

Restart Odoo after installing or upgrading the module.

## Core Models

### `botchat`

Important fields include:

- `provider`: `google_chat`, `telegram`, or `whatsapp`
- `chatid`: native provider chat/conversation ID
- `name`, `title`, `display_name`
- `chat_type`: direct, group, supergroup, channel, space, room, DM, business, or
  unknown
- `provider_resource_name`, `external_thread_key`
- `username`, `phone_number`, `phone_number_id`
- `member_count`, `is_forum`, `is_read_only`, `is_bot_member`
- `last_message_at`, `last_inbound_at`, `last_outbound_at`
- `metadata_json`, `raw_payload`

The pair `provider + chatid` is unique.

### `botmsg`

Important fields include:

- `chat_id`: link to `botchat`
- `messageid`: native provider message ID
- `direction`: inbound, outbound, or system
- `message_type`: text, media, location, contact, poll, reaction, card,
  interactive, command, system, and other supported message shapes
- `state`: received, queued, sent, delivered, read, edited, deleted, or failed
- sender and recipient metadata
- text, HTML, caption, command, and language fields
- thread, reply, forward, and reaction fields
- media metadata and Odoo attachments
- structured JSON fields for contacts, polls, entities, buttons, Google Chat
  cards, WhatsApp interactive payloads, delivery status, metadata, and raw API
  payloads

The tuple `provider + chat_id + messageid` is unique.

## Branching

Development for Odoo 19 happens on branch `19.0`.

## Local Helper Scripts

This repository may contain local deployment helpers such as `upush.sh`,
`fulldeploy.sh`, and `restart_odoo19.sh`. They are intentionally ignored by Git
because they contain machine-specific deployment assumptions.

Before using them on a new host, check:

- the local checkout path
- the Odoo service name
- the Odoo database name
- the Odoo config and binary paths
- whether the remote branch exists

## License

LGPL-3, matching the addon manifest.

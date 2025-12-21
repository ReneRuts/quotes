# 📖 Quote Bot

> Automated daily motivational quotes for your Discord server

[![Discord](https://img.shields.io/badge/Discord-Add%20Bot-7289DA?style=for-the-badge&logo=discord&logoColor=white)](YOUR_INVITE_LINK)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)

## ✨ Features

- 🕐 **Customizable Schedule** - Set any time and timezone
- ⏰ **Flexible Intervals** - Daily or custom intervals (24-168 hours)
- 🔔 **Role Mentions** - Optional role pings with quotes
- 🌍 **Multi-Timezone Support** - Works for international communities
- 📖 **Quality Quotes** - Daily quotes from ZenQuotes API
- 😄 **Funny Fallbacks** - Entertaining quotes when API is down
- ⚡ **Simple Setup** - One command to get started

## 🚀 Quick Start

### For Server Owners

1. **[Invite the bot](YOUR_INVITE_LINK)** to your server
2. Use `/setup channel:#your-channel timezone:Europe/Brussels quote_time:08:00`
3. Done! Daily quotes will arrive automatically

## 📋 Commands

| Command | Description | Permission Required |
|---------|-------------|---------------------|
| `/setup` | View current configuration | None |
| `/setup [options]` | Configure bot settings | Manage Server |
| `/testquote` | Send a test quote immediately | Manage Server |

### Setup Options

- `timezone` - Timezone (e.g., `Europe/Brussels`, `America/New_York`)
- `quote_time` - Time in 24h format (e.g., `08:00`, `13:30`)
- `interval` - Hours between quotes (24-168)
- `channel` - Channel to send quotes to
- `role` - Role to mention (optional)

## 📸 Screenshots

### Daily Quote Example
![Daily Quote](screenshots/quote.png)

### Test Quote
![Test Quote](screenshots/test.png)

## 💬 Support

- **Discord Support Server**: [Join here](https://discord.gg/5jkADM2Wt5)
- **Discord**: reneruts

## 🙏 Acknowledgments

- Quotes provided by [ZenQuotes API](https://zenquotes.io/)
- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by the need for daily motivation

---

Made with ❤️ by [René Ruts](https://github.com/ReneRuts)

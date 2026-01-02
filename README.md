# 📖 Quote Bot

> Automated daily motivational quotes for your Discord server

[![Discord](https://img.shields.io/badge/Discord-Add%20Bot-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/api/oauth2/authorize?client_id=1377996959893164052&permissions=19456&scope=bot%20applications.commands) [![Discord](https://img.shields.io/badge/Discord-Support%20Server-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/5jkADM2Wt5) [![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
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

1. **[Invite the bot](https://discord.com/api/oauth2/authorize?client_id=1377996959893164052&permissions=19456&scope=bot%20applications.commands)** to your server
2. Use `/setup channel:#your-channel timezone:Europe/Brussels quote_time:08:00`
3. Done! Daily quotes will arrive automatically

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/setup` | View current configuration |
| `/setup [options]` | Configure bot settings |
| `/favorites` | Save a quote to your personal favorite ones |

### Setup Options

- `timezone` - Timezone (e.g., `Europe/Brussels`, `America/New_York`)
- `quote_time` - Time in 24h format (e.g., `08:00`, `13:30`)
- `interval` - Hours between quotes (24-168)
- `channel` - Channel to send quotes to
- `role` - Role to mention (optional)

### Features
- `/favorites` - React with ❤️ to a quote to save it to your own favorites, then get all your favorites using the command.

## 💬 Support

- **Discord Support Server**: [Join here](https://discord.gg/5jkADM2Wt5)
- **Discord**: reneruts

## 📜 Legal

- **[Privacy Policy](PRIVACY_POLICY.md)** - How we collect and protect your data
- **[Terms of Service](TERMS_OF_SERVICE.md)** - Rules and guidelines for using the bot

By using Quote Bot, you agree to our Terms of Service and Privacy Policy.

## 🙏 Acknowledgments

- Quotes provided by [ZenQuotes API](https://zenquotes.io/)
- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by the need for daily motivation

---

Made with ❤️ by [René Ruts](https://github.com/ReneRuts)

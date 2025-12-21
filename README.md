# 📖 Quote Bot

> Automated daily motivational quotes for your Discord server

[![Discord](https://img.shields.io/badge/Discord-Add%20Bot-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/api/oauth2/authorize?client_id=1377996959893164052&permissions=414464593920&scope=bot%20applications.commands)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)](https://www.python.org/)

## ✨ Features

- 🕐 **Customizable Schedule** - Set any time and timezone
- ⏰ **Flexible Intervals** - Daily or custom intervals (24-168 hours)
- 🔔 **Role Mentions** - Optional role pings with quotes
- 🌍 **Multi-Timezone Support** - Works for international communities
- 📖 **Quality Quotes** - Daily quotes from ZenQuotes API
- ✏️ **Custom Quotes** - Add your own server-specific quotes
- 📂 **Quote Categories** - Organize quotes by topic (motivational, funny, etc.)
- 🎮 **Games & Stats** - Track streaks, earn XP, and compete on leaderboards
- ⭐ **Favorites System** - Save and collect your favorite quotes
- 👍 **Voting System** - Like and dislike quotes
- 😄 **Funny Fallbacks** - Entertaining quotes when API is down
- ⚡ **Simple Setup** - One command to get started

## 🚀 Quick Start

### For Server Owners

1. **[Invite the bot](https://discord.com/api/oauth2/authorize?client_id=1377996959893164052&permissions=414464593920&scope=bot%20applications.commands)** to your server
2. Use `/setup channel:#your-channel timezone:Europe/Brussels quote_time:08:00`
3. Done! Daily quotes will arrive automatically

## 📋 Commands

### ⚙️ Setup Commands
| Command | Description | Permission Required |
|---------|-------------|---------------------|
| `/setup` | View current configuration | None |
| `/setup [options]` | Configure bot settings | Manage Server |
| `/testquote` | Send a test quote immediately | Manage Server |

### 📖 Quote Commands
| Command | Description |
|---------|-------------|
| `/quote` | Get a random quote instantly |
| `/quote author:<name>` | Get quotes by specific author |
| `/quote category:<cat>` | Get quotes from a category |
| `/search <keyword>` | Search for quotes |
| `/favorites` | View your favorite quotes |

### ✏️ Custom Quotes
| Command | Description |
|---------|-------------|
| `/addquote` | Submit a custom quote |
| `/myquotes` | View your submitted quotes |
| `/deletequote` | Delete one of your quotes |
| `/categories` | View all available categories |

### 🎮 Games & Stats
| Command | Description |
|---------|-------------|
| `/stats` | View your statistics |
| `/leaderboard` | View server leaderboard |
| `/streak` | View your daily streak |
| `/level` | View your level and XP progress |

### 🛡️ Moderation (Admin Only)
| Command | Description |
|---------|-------------|
| `/pending` | View pending quotes for approval |
| `/approve <quote_id>` | Approve a pending quote |

### Setup Options

- `timezone` - Timezone (e.g., `Europe/Brussels`, `America/New_York`)
- `quote_time` - Time in 24h format (e.g., `08:00`, `13:30`)
- `interval` - Hours between quotes (24-168)
- `channel` - Channel to send quotes to
- `role` - Role to mention (optional)

## 💬 Support

- **Discord Support Server**: [Join here](https://discord.gg/5jkADM2Wt5)
- **Discord**: reneruts

## 🙏 Acknowledgments

- Quotes provided by [ZenQuotes API](https://zenquotes.io/)
- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by the need for daily motivation

---

Made with ❤️ by [René Ruts](https://github.com/ReneRuts)

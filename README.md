# 📖 Quote Bot

> Automated daily motivational quotes for your Discord server

[![Discord](https://img.shields.io/badge/Discord-Add%20Bot-7289DA?style=for-the-badge&logo=discord&logoColor=white)](YOUR_INVITE_LINK)
[![GitHub](https://img.shields.io/github/stars/ReneRuts/Quote?style=for-the-badge)](https://github.com/ReneRuts/Quote)
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

### For Developers (Self-Hosting)

#### Prerequisites
- Python 3.11+
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))

#### Installation

```bash
# Clone the repository
git clone https://github.com/ReneRuts/Quote.git
cd Quote

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your bot token and application ID

# Run the bot
python bot.py
```

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

### Setup Command
![Setup Command](screenshots/setup.png)

### Daily Quote Example
![Daily Quote](screenshots/quote.png)

### Test Quote
![Test Quote](screenshots/test.png)

## 🏗️ Project Structure

```
discord-quote-bot/
├── bot.py                 # Main bot file
├── cogs/
│   ├── setup.py          # Setup commands
│   └── quotes.py         # Quote scheduling logic
├── utils/
│   ├── config.py         # Configuration management
│   └── quote_fetcher.py  # Quote API integration
├── .env                  # Environment variables (not in repo)
├── requirements.txt      # Python dependencies
└── README.md            # You are here!
```

## 🛠️ Configuration

The bot stores configuration in `server_config.json`:

```json
{
  "SERVER_ID": {
    "timezone": "Europe/Brussels",
    "quote_time": "08:00",
    "channel_id": 123456789,
    "interval": 24,
    "role_id": 987654321
  }
}
```

Last sent times are tracked in `last_sent.json` to ensure quotes are sent on schedule even after restarts.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions

- [ ] Add support for custom quote collections
- [ ] Implement quote categories (motivational, funny, inspirational)
- [ ] Add quote voting system
- [ ] Multiple quotes per day
- [ ] Quote of the week feature
- [ ] Embed customization options

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports & Feature Requests

Found a bug or have an idea? Please [open an issue](https://github.com/ReneRuts/Quote/issues)!

## 💬 Support

- **Discord Support Server**: [Join here](https://discord.gg/5jkADM2Wt5)
- **GitHub Issues**: [Report bugs](https://github.com/ReneRuts/Quote/issues)
- **Discord**: reneruts

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/ReneRuts/Quote?style=social)
![GitHub forks](https://img.shields.io/github/forks/ReneRuts/Quote?style=social)

## 🙏 Acknowledgments

- Quotes provided by [ZenQuotes API](https://zenquotes.io/)
- Built with [discord.py](https://github.com/Rapptz/discord.py)
- Inspired by the need for daily motivation

---

Made with ❤️ by [René Ruts](https://github.com/ReneRuts)

import requests

ZEN_QUOTES_API_URL = "https://zenquotes.io/api/today"

def fetch_quote():
    """Fetches a daily quote from ZenQuotes API."""
    response = requests.get(ZEN_QUOTES_API_URL)
    if response.status_code == 200:
        quote_data = response.json()[0]
        return f"📖 **Daily Quote:**\n_{quote_data['q']}_\n— {quote_data['a']}"
    else:
        return "📖 **Daily Quote:**\n_In its prime, it dispensed wisdom. Now, it dispenses silence. Even the bot must rest._\n— René Ruts"

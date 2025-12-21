import requests
import random

ZEN_QUOTES_API_URL = "https://zenquotes.io/api/today"
FALLBACK_QUOTES = [
    {
        "quote": "In its prime, it dispensed wisdom. Now, it dispenses silence. Even the bot must rest.",
        "author": "[René Ruts](https://github.com/ReneRuts)"
    },
    {
        "quote": "The bot is currently experiencing an existential crisis. Please check back when it finds meaning again.",
        "author": "The Bot Gods"
    },
    {
        "quote": "404: Wisdom not found. But hey, at least the bot tried.",
        "author": "Anonymous Developer"
    },
    {
        "quote": "The quote bot took a day off. Even bots need mental health days.",
        "author": "The Bot Union"
    },
    {
        "quote": "Error: Too wise for the internet today. Please try again when reality is more stable.",
        "author": "System Administrator"
    }
]

def fetch_quote():
    """Fetch daily quote from ZenQuotes API"""
    try:
        response = requests.get(ZEN_QUOTES_API_URL, timeout=10)
        
        if response.status_code == 200:
            quote_data = response.json()[0]
            quote_text = quote_data.get('q', 'No quote available')
            author = quote_data.get('a', 'Unknown')
            
            return f"📖 **Daily Quote**\n\n_{quote_text}_\n\n— **{author}**"
        else:
            return get_fallback_quote()
            
    except Exception as e:
        print(f"❌ Error fetching quote: {e}")
        return get_fallback_quote()

def get_fallback_quote():
    """Return a random funny fallback quote when API fails"""
    quote_data = random.choice(FALLBACK_QUOTES)
    return (
        f"📖 **Bonus Quote**\n\n"
        f"_{quote_data['quote']}_\n\n"
        f"— **{quote_data['author']}**"
    )

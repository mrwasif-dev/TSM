import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '123456789').split(',')]

# Database
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///smm_bot.db')

# Payment Accounts (Pakistan)
JAZZCASH_NUMBER = os.getenv('JAZZCASH_NUMBER', '03001234567')
EASYPAISA_NUMBER = os.getenv('EASYPAISA_NUMBER', '03001234567')

# Upstream API (where you'll order services from)
UPSTREAM_API_URL = os.getenv('UPSTREAM_API_URL', 'https://api.example.com')
UPSTREAM_API_KEY = os.getenv('UPSTREAM_API_KEY', 'your-api-key')

# Currency
CURRENCY = "PKR"

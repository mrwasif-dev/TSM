# 🤖 TSM - Telegram SMM Bot

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Telegram](https://img.shields.io/badge/telegram-bot-blue.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

A **complete Telegram Bot** for Social Media Marketing services. Users can buy Instagram followers, YouTube views, TikTok likes, and more directly from Telegram with easy payment through JazzCash/EasyPaisa.

---

## 🚀 **One-Click Deploy to Heroku**

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/mrwasif-dev/TSM)

> Click the button above to deploy instantly! No coding required.

---

## ✨ **Features**

### 👤 **For Users**
| Feature | Description |
|---------|-------------|
| 🛍 **Buy Services** | Instagram, YouTube, TikTok, Facebook, Twitter services |
| 💰 **Check Balance** | Real-time balance updates |
| 📦 **Order History** | View all past orders |
| ➕ **Add Balance** | Via JazzCash/EasyPaisa |
| 🔔 **Order Updates** | Get notified when order is processed |
| 📱 **Easy to Use** | Simple button-based interface |

### 👑 **For Admins**
| Feature | Description |
|---------|-------------|
| 👥 **User Management** | View all users |
| 📊 **Order Management** | Track and manage orders |
| 💵 **Add Balance** | Manually add balance to users |
| 📈 **Statistics** | View bot performance |
| 🔔 **Notifications** | Get alerts for new orders |
| ⚙️ **Full Control** | Complete admin panel |

---

## 💳 **Payment Methods**

| Method | Details |
|--------|---------|
| **JazzCash** | `03001234567` |
| **EasyPaisa** | `03001234567` |
| **Admin Add** | Manual balance addition |

---

## 🛒 **Services Available**

### 📸 **Instagram**
| Service | Price (per 1K) | Min | Max |
|---------|---------------|-----|-----|
| Followers | 100 PKR | 100 | 10,000 |
| Likes | 50 PKR | 50 | 5,000 |
| Views | 30 PKR | 100 | 10,000 |

### ▶️ **YouTube**
| Service | Price (per 1K) | Min | Max |
|---------|---------------|-----|-----|
| Subscribers | 200 PKR | 50 | 5,000 |
| Views | 40 PKR | 100 | 50,000 |
| Likes | 60 PKR | 50 | 5,000 |

### 🎵 **TikTok**
| Service | Price (per 1K) | Min | Max |
|---------|---------------|-----|-----|
| Followers | 150 PKR | 100 | 10,000 |
| Likes | 80 PKR | 50 | 5,000 |
| Views | 25 PKR | 100 | 50,000 |

### 📘 **Facebook**
| Service | Price (per 1K) | Min | Max |
|---------|---------------|-----|-----|
| Followers | 120 PKR | 100 | 10,000 |
| Post Likes | 70 PKR | 50 | 5,000 |

### 🐦 **Twitter**
| Service | Price (per 1K) | Min | Max |
|---------|---------------|-----|-----|
| Followers | 130 PKR | 100 | 10,000 |
| Retweets | 90 PKR | 50 | 5,000 |
| Likes | 60 PKR | 50 | 5,000 |

---

## 📋 **Prerequisites**

Before deploying, make sure you have:

1. **Telegram Bot Token** - Get from [@BotFather](https://t.me/botfather)
2. **Heroku Account** - Sign up at [heroku.com](https://heroku.com)
3. **JazzCash/EasyPaisa Number** - For receiving payments

---

## ⚙️ **Environment Variables**

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BOT_TOKEN` | Your Telegram Bot Token | ✅ | - |
| `ADMIN_IDS` | Comma-separated admin IDs | ✅ | - |
| `JAZZCASH_NUMBER` | Your JazzCash number | ✅ | 03001234567 |
| `EASYPAISA_NUMBER` | Your EasyPaisa number | ✅ | 03001234567 |
| `UPSTREAM_API_URL` | Upstream panel API URL | ❌ | https://api.example.com |
| `UPSTREAM_API_KEY` | Upstream panel API key | ❌ | - |
| `CURRENCY` | Currency symbol | ❌ | PKR |

---

## 🚀 **Deployment Options**

### **Option 1: One-Click Heroku Deploy (Easiest)**
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/mrwasif-dev/TSM)

Just click and fill in the variables!

### **Option 2: Manual Deploy**

```bash
# Clone the repository
git clone https://github.com/mrwasif-dev/TSM.git
cd TSM

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "BOT_TOKEN=your_bot_token_here" > .env
echo "ADMIN_IDS=123456789" >> .env

# Initialize database
python init_db.py

# Run the bot
python bot.py

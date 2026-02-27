#!/usr/bin/env python3
"""
Complete Telegram SMM Bot
Author: Your Name
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes
)
from sqlalchemy.orm import Session
import requests
import json

from database import SessionLocal, User, Service, Order, Transaction
from config import (
    BOT_TOKEN, ADMIN_IDS, JAZZCASH_NUMBER,
    EASYPAISA_NUMBER, CURRENCY, UPSTREAM_API_URL,
    UPSTREAM_API_KEY
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(SELECTING_CATEGORY, SELECTING_SERVICE, ENTERING_LINK,
 ENTERING_QUANTITY, CONFIRM_ORDER, ADDING_BALANCE) = range(6)

# ==================== DATABASE HELPERS ====================

def get_or_create_user(update):
    """Get user from database or create new one"""
    db = SessionLocal()
    telegram_user = update.effective_user
    
    user = db.query(User).filter_by(telegram_id=telegram_user.id).first()
    
    if not user:
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            balance=0.0
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    db.close()
    return user

def is_admin(user_id):
    """Check if user is admin"""
    return user_id in ADMIN_IDS

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    user = get_or_create_user(update)
    
    welcome_message = f"""
🌟 *Welcome to SMM Panel Bot!* 🌟

👤 *Your Account:*
• User ID: `{user.telegram_id}`
• Balance: *{CURRENCY} {user.balance:.2f}*
• Joined: {user.joined_date.strftime('%Y-%m-%d')}

✨ *What can you do?*
• Buy social media services
• Check your orders
• Add balance

👇 *Select an option below:*
    """
    
    keyboard = [
        [InlineKeyboardButton("🛍 Buy Services", callback_data="buy_services")],
        [InlineKeyboardButton("📊 My Account", callback_data="my_account")],
        [InlineKeyboardButton("➕ Add Balance", callback_data="add_balance")],
        [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ]
    
    if is_admin(user.telegram_id):
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data == "buy_services":
        await show_categories(query, context)
    
    elif data == "my_account":
        await show_account(query, context)
    
    elif data == "add_balance":
        await show_balance_options(query, context)
    
    elif data == "my_orders":
        await show_user_orders(query, context)
    
    elif data == "help":
        await show_help(query, context)
    
    elif data == "back_to_main":
        await back_to_main(query, context)
    
    elif data.startswith("category_"):
        category = data.replace("category_", "")
        await show_services(query, context, category)
    
    elif data.startswith("service_"):
        service_id = int(data.replace("service_", ""))
        context.user_data['selected_service'] = service_id
        await query.edit_message_text(
            "📎 *Enter your link:*\n\n"
            "Example:\n"
            "• Instagram Post: https://www.instagram.com/p/xxx\n"
            "• YouTube Video: https://youtu.be/xxx\n"
            "• TikTok Video: https://www.tiktok.com/@user/video/xxx",
            parse_mode='Markdown'
        )
        return ENTERING_LINK
    
    # Admin callbacks
    elif data == "admin_panel":
        await show_admin_panel(query, context)
    
    elif data == "admin_users":
        await show_all_users(query, context)
    
    elif data == "admin_orders":
        await show_all_orders(query, context)
    
    elif data == "admin_stats":
        await show_stats(query, context)
    
    elif data == "admin_add_balance":
        await query.edit_message_text(
            "🔹 *Add Balance to User*\n\n"
            "Send: `user_id amount`\n"
            "Example: `123456789 500`",
            parse_mode='Markdown'
        )
        return ADDING_BALANCE

async def show_categories(query, context):
    """Show service categories"""
    db = SessionLocal()
    categories = db.query(Service.category).distinct().all()
    db.close()
    
    keyboard = []
    for cat in categories:
        if cat[0]:
            keyboard.append([InlineKeyboardButton(
                f"📁 {cat[0]}",
                callback_data=f"category_{cat[0]}"
            )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_main")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📂 *Select Category:*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_services(query, context, category):
    """Show services in selected category"""
    db = SessionLocal()
    services = db.query(Service).filter_by(category=category, is_active=True).all()
    db.close()
    
    message = f"📁 *{category} Services*\n\n"
    
    keyboard = []
    for service in services:
        price_per_k = service.price_per_1000
        message += f"🔹 *{service.name}*\n"
        message += f"   💰 Price: {CURRENCY} {price_per_k}/1K\n"
        message += f"   📊 Min: {service.min_order} | Max: {service.max_order}\n\n"
        
        keyboard.append([InlineKeyboardButton(
            f"✅ {service.name}",
            callback_data=f"service_{service.id}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="buy_services")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_account(query, context):
    """Show user account details"""
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
    
    # Get recent transactions
    recent_transactions = db.query(Transaction).filter_by(
        user_id=user.id
    ).order_by(Transaction.created_at.desc()).limit(5).all()
    
    db.close()
    
    message = f"""
📊 *Your Account Details*

🆔 *User ID:* `{user.telegram_id}`
👤 *Username:* @{user.username or 'Not set'}
💰 *Balance:* {CURRENCY} {user.balance:.2f}
📦 *Total Orders:* {user.total_orders}
💸 *Total Spent:* {CURRENCY} {user.total_spent:.2f}
📅 *Member Since:* {user.joined_date.strftime('%Y-%m-%d')}

📋 *Recent Transactions:*
    """
    
    for trans in recent_transactions:
        status_emoji = "✅" if trans.status == 'completed' else "⏳"
        message += f"\n{status_emoji} {trans.type}: {CURRENCY} {trans.amount} ({trans.status})"
    
    keyboard = [
        [InlineKeyboardButton("➕ Add Balance", callback_data="add_balance")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_balance_options(query, context):
    """Show balance addition options"""
    message = f"""
💰 *Add Balance*

Choose payment method:

💳 *JazzCash:* `{JAZZCASH_NUMBER}`
📱 *EasyPaisa:* `{EASYPAISA_NUMBER}`

📝 *How to add:*
1. Send payment to above number
2. Take screenshot
3. Click "I have paid" below
4. Send payment screenshot

⚠️ *Minimum deposit:* {CURRENCY} 100
    """
    
    keyboard = [
        [InlineKeyboardButton("✅ I have paid", callback_data="payment_done")],
        [InlineKeyboardButton("🔙 Back", callback_data="my_account")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_user_orders(query, context):
    """Show user's orders"""
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=query.from_user.id).first()
    orders = db.query(Order).filter_by(user_id=user.id).order_by(
        Order.created_at.desc()
    ).limit(10).all()
    db.close()
    
    if not orders:
        await query.edit_message_text(
            "📦 *No orders yet*\n\nStart buying services from the main menu!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back", callback_data="back_to_main")
            ]]),
            parse_mode='Markdown'
        )
        return
    
    message = "📦 *Your Recent Orders*\n\n"
    
    for order in orders:
        status_emoji = {
            'pending': '⏳',
            'processing': '⚙️',
            'completed': '✅',
            'cancelled': '❌'
        }.get(order.status, '⏳')
        
        message += f"{status_emoji} *{order.service_name}*\n"
        message += f"   Quantity: {order.quantity}\n"
        message += f"   Price: {CURRENCY} {order.price}\n"
        message += f"   Status: {order.status}\n"
        message += f"   Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ==================== ORDER PROCESSING ====================

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle link input from user"""
    link = update.message.text
    context.user_data['order_link'] = link
    
    service_id = context.user_data.get('selected_service')
    db = SessionLocal()
    service = db.query(Service).filter_by(id=service_id).first()
    db.close()
    
    await update.message.reply_text(
        f"🔢 *Enter Quantity*\n\n"
        f"Service: *{service.name}*\n"
        f"Min: {service.min_order} | Max: {service.max_order}\n"
        f"Price: {CURRENCY} {service.price_per_1000}/1K\n\n"
        f"Send number between {service.min_order}-{service.max_order}:",
        parse_mode='Markdown'
    )
    
    return ENTERING_QUANTITY

async def handle_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle quantity input and show order confirmation"""
    try:
        quantity = int(update.message.text)
    except ValueError:
        await update.message.reply_text("❌ Please send a valid number!")
        return ENTERING_QUANTITY
    
    service_id = context.user_data.get('selected_service')
    link = context.user_data.get('order_link')
    
    db = SessionLocal()
    service = db.query(Service).filter_by(id=service_id).first()
    user = db.query(User).filter_by(telegram_id=update.effective_user.id).first()
    
    if quantity < service.min_order or quantity > service.max_order:
        await update.message.reply_text(
            f"❌ Quantity must be between {service.min_order} and {service.max_order}!"
        )
        db.close()
        return ENTERING_QUANTITY
    
    # Calculate price
    price = (quantity / 1000) * service.price_per_1000
    
    # Check balance
    if user.balance < price:
        await update.message.reply_text(
            f"❌ *Insufficient Balance!*\n\n"
            f"Required: {CURRENCY} {price:.2f}\n"
            f"Your Balance: {CURRENCY} {user.balance:.2f}\n\n"
            f"Please add balance first.",
            parse_mode='Markdown'
        )
        db.close()
        return ConversationHandler.END
    
    context.user_data['order_quantity'] = quantity
    context.user_data['order_price'] = price
    
    # Show confirmation
    confirm_message = f"""
📋 *Order Confirmation*

🛍 *Service:* {service.name}
📎 *Link:* {link[:50]}...
🔢 *Quantity:* {quantity}
💰 *Price:* {CURRENCY} {price:.2f}
💳 *Your Balance:* {CURRENCY} {user.balance:.2f}
💵 *Balance After:* {CURRENCY} {user.balance - price:.2f}

✅ *Confirm order?*
    """
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data="confirm_order_yes"),
            InlineKeyboardButton("❌ Cancel", callback_data="confirm_order_no")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        confirm_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    
    db.close()
    return CONFIRM_ORDER

async def confirm_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process confirmed order"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "confirm_order_no":
        await query.edit_message_text("❌ Order cancelled.")
        context.user_data.clear()
        return ConversationHandler.END
    
    # Get order details
    service_id = context.user_data.get('selected_service')
    link = context.user_data.get('order_link')
    quantity = context.user_data.get('order_quantity')
    price = context.user_data.get('order_price')
    user_id = update.effective_user.id
    
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    service = db.query(Service).filter_by(id=service_id).first()
    
    # Deduct balance
    user.balance -= price
    user.total_orders += 1
    user.total_spent += price
    
    # Create order
    order = Order(
        user_id=user.id,
        service_id=service.id,
        service_name=service.name,
        link=link,
        quantity=quantity,
        price=price,
        status='pending'
    )
    db.add(order)
    
    # Create transaction
    transaction = Transaction(
        user_id=user.id,
        amount=price,
        type='order_payment',
        status='completed',
        reference=f"Order #{order.id}"
    )
    db.add(transaction)
    
    db.commit()
    
    # Here you would call upstream API to place the order
    # api_response = place_upstream_order(service.api_service_id, link, quantity)
    # if api_response:
    #     order.api_order_id = api_response['order_id']
    #     order.status = 'processing'
    #     db.commit()
    
    db.close()
    
    await query.edit_message_text(
        f"✅ *Order Placed Successfully!*\n\n"
        f"📦 *Order ID:* #{order.id}\n"
        f"🛍 *Service:* {service.name}\n"
        f"🔢 *Quantity:* {quantity}\n"
        f"💰 *Price:* {CURRENCY} {price:.2f}\n"
        f"💳 *Remaining Balance:* {CURRENCY} {user.balance:.2f}\n\n"
        f"Your order is being processed. You'll get updates soon!",
        parse_mode='Markdown'
    )
    
    # Notify admins
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(
                admin_id,
                f"🆕 *New Order!*\n\n"
                f"👤 User: @{user.username or 'No username'}\n"
                f"🛍 Service: {service.name}\n"
                f"🔢 Quantity: {quantity}\n"
                f"💰 Price: {CURRENCY} {price:.2f}\n"
                f"📎 Link: {link}",
                parse_mode='Markdown'
            )
        except:
            pass
    
    context.user_data.clear()
    return ConversationHandler.END

# ==================== ADMIN PANEL ====================

async def show_admin_panel(query, context):
    """Show admin panel"""
    if not is_admin(query.from_user.id):
        await query.edit_message_text("❌ Unauthorized!")
        return
    
    keyboard = [
        [InlineKeyboardButton("👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton("📦 Orders", callback_data="admin_orders")],
        [InlineKeyboardButton("📊 Statistics", callback_data="admin_stats")],
        [InlineKeyboardButton("➕ Add Balance", callback_data="admin_add_balance")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "⚙️ *Admin Panel*\n\nSelect an option:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_all_users(query, context):
    """Show all users to admin"""
    if not is_admin(query.from_user.id):
        return
    
    db = SessionLocal()
    users = db.query(User).order_by(User.joined_date.desc()).limit(20).all()
    total_users = db.query(User).count()
    db.close()
    
    message = f"👥 *Users (Last 20 of {total_users})*\n\n"
    
    for user in users:
        message += f"🆔 `{user.telegram_id}` | @{user.username or 'N/A'}\n"
        message += f"💰 {CURRENCY} {user.balance:.2f} | 📦 {user.total_orders}\n"
        message += f"📅 {user.joined_date.strftime('%Y-%m-%d')}\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def show_all_orders(query, context):
    """Show all orders to admin"""
    if not is_admin(query.from_user.id):
        return
    
    db = SessionLocal()
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(20).all()
    db.close()
    
    message = "📦 *Recent Orders*\n\n"
    
    for order in orders:
        status_emoji = {
            'pending': '⏳',
            'processing': '⚙️',
            'completed': '✅',
            'cancelled': '❌'
        }.get(order.status, '⏳')
        
        message += f"{status_emoji} *Order #{order.id}*\n"
        message += f"👤 User ID: `{order.user_id}`\n"
        message += f"🛍 {order.service_name}\n"
        message += f"🔢 {order.quantity} | 💰 {CURRENCY} {order.price}\n"
        message += f"📎 [Link]({order.link[:50]}...)\n"
        message += f"📅 {order.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown',
        disable_web_page_preview=True
    )

async def show_stats(query, context):
    """Show bot statistics"""
    if not is_admin(query.from_user.id):
        return
    
    db = SessionLocal()
    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    pending_orders = db.query(Order).filter_by(status='pending').count()
    completed_orders = db.query(Order).filter_by(status='completed').count()
    
    total_deposits = db.query(Transaction).filter_by(
        type='deposit', status='completed'
    ).count()
    total_deposit_amount = db.query(Transaction).filter_by(
        type='deposit', status='completed'
    ).with_entities(Transaction.amount).all()
    total_deposit_sum = sum([t[0] for t in total_deposit_amount]) if total_deposit_amount else 0
    
    db.close()
    
    message = f"""
📊 *Bot Statistics*

👥 *Users:*
• Total Users: {total_users}

📦 *Orders:*
• Total Orders: {total_orders}
• Pending: {pending_orders}
• Completed: {completed_orders}

💰 *Finance:*
• Total Deposits: {total_deposits}
• Deposit Amount: {CURRENCY} {total_deposit_sum:.2f}
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="admin_panel")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_admin_add_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle admin adding balance to user"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Unauthorized!")
        return ConversationHandler.END
    
    try:
        parts = update.message.text.split()
        user_id = int(parts[0])
        amount = float(parts[1])
    except:
        await update.message.reply_text(
            "❌ Invalid format!\n\nUse: `user_id amount`\nExample: `123456789 500`",
            parse_mode='Markdown'
        )
        return ConversationHandler.END
    
    db = SessionLocal()
    user = db.query(User).filter_by(telegram_id=user_id).first()
    
    if not user:
        await update.message.reply_text("❌ User not found!")
        db.close()
        return ConversationHandler.END
    
    # Add balance
    user.balance += amount
    
    # Create transaction
    transaction = Transaction(
        user_id=user.id,
        amount=amount,
        type='deposit',
        method='admin',
        status='completed',
        reference=f"Added by admin {update.effective_user.id}"
    )
    db.add(transaction)
    db.commit()
    
    await update.message.reply_text(
        f"✅ Balance added successfully!\n\n"
        f"👤 User: @{user.username or 'No username'}\n"
        f"💰 Added: {CURRENCY} {amount:.2f}\n"
        f"💳 New Balance: {CURRENCY} {user.balance:.2f}"
    )
    
    # Notify user
    try:
        await context.bot.send_message(
            user.telegram_id,
            f"💰 *Balance Added!*\n\n"
            f"Amount: {CURRENCY} {amount:.2f}\n"
            f"New Balance: {CURRENCY} {user.balance:.2f}\n\n"
            f"Thank you for using our service!",
            parse_mode='Markdown'
        )
    except:
        pass
    
    db.close()
    return ConversationHandler.END

# ==================== HELPER FUNCTIONS ====================

async def show_help(query, context):
    """Show help message"""
    help_text = """
🆘 *Help & Support*

🤖 *How to use this bot:*

1️⃣ *Buy Services*
• Click "Buy Services"
• Select category
• Choose service
• Enter your link
• Enter quantity
• Confirm order

2️⃣ *Add Balance*
• Click "Add Balance"
• Send payment to given number
• Click "I have paid"
• Send screenshot
• Admin will add balance

3️⃣ *Check Orders*
• Click "My Orders"
• View your order history

📞 *Support*
• For issues, contact @YourSupport
• Payment issues: +92XXXXXXXXX

💰 *Minimum Deposit:* {CURRENCY} 100
⚡ *Fast Delivery:* 5-30 minutes
    """
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_main(query, context):
    """Return to main menu"""
    user = get_or_create_user(query)
    
    main_message = f"""
🌟 *Welcome to SMM Panel Bot!* 🌟

👤 *Your Balance:* {CURRENCY} {user.balance:.2f}

👇 *Select an option below:*
    """
    
    keyboard = [
        [InlineKeyboardButton("🛍 Buy Services", callback_data="buy_services")],
        [InlineKeyboardButton("📊 My Account", callback_data="my_account")],
        [InlineKeyboardButton("➕ Add Balance", callback_data="add_balance")],
        [InlineKeyboardButton("📦 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("🆘 Help", callback_data="help")]
    ]
    
    if is_admin(user.telegram_id):
        keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        main_message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ==================== UPSTREAM API ====================

def place_upstream_order(api_service_id, link, quantity):
    """Place order to upstream panel"""
    try:
        response = requests.post(
            f"{UPSTREAM_API_URL}/order",
            json={
                'key': UPSTREAM_API_KEY,
                'service': api_service_id,
                'link': link,
                'quantity': quantity
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot"""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for ordering
    order_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^service_")],
        states={
            ENTERING_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)],
            ENTERING_QUANTITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quantity)],
            CONFIRM_ORDER: [CallbackQueryHandler(confirm_order, pattern="^confirm_order_")]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    # Admin balance addition conversation
    admin_balance_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^admin_add_balance")],
        states={
            ADDING_BALANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_add_balance)]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(order_conv)
    application.add_handler(admin_balance_conv)
    
    # Start bot
    print("🤖 Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

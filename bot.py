#!/usr/bin/env python3
"""
Telegram Bot - Freepik Link Generator
Optimized for Railway
"""

import os
import re
import time
import random
import asyncio
import requests
from urllib.parse import quote_plus
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# تنظیمات
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8458966976:AAGvp6xc5t3z62RAmNgHpBOxeQmVye0MUME')

def get_image_links_alternative(query, num_links):
    """روش جایگزین بدون Selenium - استفاده از API یا اسکرپ ساده"""
    try:
        print(f"🔍 جستجوی جایگزین برای: {query}")
        
        # استفاده از Google Images API ساده
        search_url = f"https://www.freepik.com/search?query={quote_plus(query)}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"❌ خطا در دریافت صفحه: {response.status_code}")
            return []
        
        # استخراج لینک‌های عکس از HTML
        html_content = response.text
        image_urls = set()
        
        # پیدا کردن لینک‌های عکس در HTML
        image_patterns = [
            r'src="(https://img\.freepik\.com/[^"]+\.(jpg|jpeg|png|webp)[^"]*)"',
            r'data-src="(https://img\.freepik\.com/[^"]+\.(jpg|jpeg|png|webp)[^"]*)"',
            r'https://img\.freepik\.com/[^"\s]+\.(jpg|jpeg|png|webp)'
        ]
        
        for pattern in image_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    url = match[0]
                else:
                    url = match
                
                if 'premium' not in url.lower() and 'watermark' not in url.lower():
                    clean_url = url.split('?')[0]
                    image_urls.add(clean_url)
        
        print(f"✅ {len(image_urls)} لینک پیدا شد")
        image_urls = list(image_urls)
        random.shuffle(image_urls)
        return image_urls[:num_links] if image_urls else []
        
    except Exception as e:
        print(f"❌ خطا در روش جایگزین: {e}")
        return []

# دستورات ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 **ربات لینک‌ساز Freepik**\n\n"
        "🔍 عبارت جستجو رو بفرست..."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    user_data = context.chat_data['user_data']
    
    if 'query' not in user_data:
        user_data['query'] = user_message
        await update.message.reply_text(f"🔍 عبارت: {user_message}\n\n📊 تعداد لینک؟ (1-10)")
        
    elif 'num_links' not in user_data:
        try:
            num_links = int(user_message)
            if not 1 <= num_links <= 10:
                await update.message.reply_text("⚠️ لطفاً عدد بین 1-10 وارد کن:")
                return
            
            user_data['num_links'] = num_links
            await update.message.reply_text("⏳ در حال جستجو...")
            
            # دریافت لینک‌ها با روش جایگزین
            links = get_image_links_alternative(user_data['query'], num_links)
            
            if links:
                await update.message.reply_text(f"✅ {len(links)} لینک پیدا شد:")
                for i, link in enumerate(links, 1):
                    # کوتاه کردن لینک برای نمایش بهتر
                    display_link = link[:80] + "..." if len(link) > 80 else link
                    await update.message.reply_text(f"📸 {i}:\n`{link}`", parse_mode='Markdown')
                    await asyncio.sleep(0.3)
            else:
                await update.message.reply_text(
                    "❌ عکسی پیدا نشد\n\n"
                    "• عبارت رو تغییر بده\n"
                    "• یا دوباره امتحان کن"
                )
            
            context.chat_data['user_data'] = {}
            
        except ValueError:
            await update.message.reply_text("⚠️ لطفاً عدد وارد کن")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 **راهنما:**\n\n"
        "🔍 عبارت‌های پیشنهادی:\n"
        "• طبیعت (nature)\n"
        "• گل (flower)\n" 
        "• پس‌زمینه (background)\n"
        "• مردم (people)\n\n"
        "⚡ ربات از روش مستقیم استفاده می‌کنه\n"
        "🎯 سریع و بدون نیاز به مرورگر"
    )

def main():
    print("🚀 شروع ربات روی Railway...")
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ BOT_TOKEN رو تنظیم کن")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ ربات آماده! (بدون Selenium)")
    app.run_polling()

if __name__ == "__main__":
    main()

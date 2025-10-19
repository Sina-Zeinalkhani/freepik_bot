#!/usr/bin/env python3
"""
Telegram Bot - Freepik Link Generator
GitHub + Render Version
"""

import os
import re
import time
import random
import asyncio
from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# تنظیمات
BOT_TOKEN = os.environ.get('BOT_TOKEN', '8458966976:AAGvp6xc5t3z62RAmNgHpBOxeQmVye0MUME')
SCROLL_PAUSE = 2
MAX_SCROLLS = 10

def setup_driver():
    """تنظیم مرورگر"""
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36")
    
    try:
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=opts
        )
        return driver
    except Exception as e:
        print(f"❌ خطا در مرورگر: {e}")
        return None

def get_image_links(query, num_links):
    """دریافت لینک عکس‌ها از Freepik"""
    driver = None
    try:
        driver = setup_driver()
        if not driver:
            return []
        
        # جستجو در Freepik
        search_url = f"https://www.freepik.com/search?query={quote_plus(query)}"
        driver.get(search_url)
        time.sleep(5)
        
        # اسکرول
        for i in range(MAX_SCROLLS):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE)
        
        # استخراج لینک‌ها
        image_urls = set()
        imgs = driver.find_elements(By.TAG_NAME, "img")
        
        for img in imgs:
            try:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                    if 'freepik.com' in src and 'premium' not in src.lower():
                        clean_url = src.split('?')[0]
                        image_urls.add(clean_url)
            except:
                continue
        
        # انتخاب تصادفی
        image_urls = list(image_urls)
        random.shuffle(image_urls)
        return image_urls[:num_links] if len(image_urls) > num_links else image_urls
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        return []
    finally:
        if driver:
            driver.quit()

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
            
            # دریافت لینک‌ها
            links = get_image_links(user_data['query'], num_links)
            
            if links:
                await update.message.reply_text(f"✅ {len(links)} لینک پیدا شد:")
                for i, link in enumerate(links, 1):
                    await update.message.reply_text(f"📸 {i}:\n`{link}`", parse_mode='Markdown')
                    await asyncio.sleep(0.3)
            else:
                await update.message.reply_text("❌ عکسی پیدا نشد")
            
            context.chat_data['user_data'] = {}
            
        except ValueError:
            await update.message.reply_text("⚠️ لطفاً عدد وارد کن")

def main():
    print("🚀 شروع ربات...")
    
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("❌ BOT_TOKEN رو تنظیم کن")
        return
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ ربات آماده!")
    app.run_polling()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Telegram Bot - Freepik Link Generator
Fixed for Railway (Chromium)
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
BOT_TOKEN = "8458966976:AAGvp6xc5t3z62RAmNgHpBOxeQmVye0MUME"
SCROLL_PAUSE = 2
MAX_SCROLLS = 10

def setup_driver():
    """تنظیم مرورگر برای Railway با Chromium"""
    opts = Options()
    
    # تنظیمات برای Railway
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--remote-debugging-port=9222")
    opts.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # استفاده از chromium که روی Railway موجوده
    opts.binary_location = "/usr/bin/chromium"
    
    try:
        # نصب chromium-browser در Railway
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
        return driver
    except Exception as e:
        print(f"❌ خطا در راه‌اندازی مرورگر: {e}")
        # روش جایگزین
        return setup_driver_fallback()

def setup_driver_fallback():
    """روش جایگزین اگر chromium کار نکرد"""
    try:
        opts = Options()
        opts.add_argument("--headless")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--remote-debugging-port=9222")
        
        # بدون مشخص کردن binary location
        driver = webdriver.Chrome(options=opts)
        return driver
    except Exception as e:
        print(f"❌ خطا در روش جایگزین: {e}")
        return None

def get_image_links_simple(query, num_links):
    """روش ساده‌تر اگر Selenium کار نکرد"""
    try:
        import requests
        
        # استفاده از API جایگزین
        # Pixabay API (رایگان)
        API_KEY = "38023921-5e6e28d1c64b41394a39f2f5a"  # API Key تست
        url = f"https://pixabay.com/api/?key={API_KEY}&q={quote_plus(query)}&per_page={num_links}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            image_urls = [hit['webformatURL'] for hit in data.get('hits', [])]
            print(f"✅ {len(image_urls)} عکس از Pixabay پیدا شد")
            return image_urls
        return []
    except Exception as e:
        print(f"❌ خطا در روش ساده: {e}")
        return []

def get_image_links(query, num_links):
    """گرفتن لینک عکس‌ها"""
    # اول با Selenium امتحان کن
    driver = None
    try:
        print(f"🔍 جستجو برای: {query} (با Selenium)")
        
        driver = setup_driver()
        if not driver:
            print("🔧 استفاده از روش جایگزین...")
            return get_image_links_simple(query, num_links)
        
        # تنظیم timeout
        driver.set_page_load_timeout(30)
        
        # باز کردن صفحه جستجو
        search_url = f"https://www.freepik.com/search?query={quote_plus(query)}"
        print(f"🌐 باز کردن: {search_url}")
        driver.get(search_url)
        time.sleep(5)
        
        # اسکرول
        print("🔄 در حال اسکرول...")
        for i in range(MAX_SCROLLS):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE)
        
        # استخراج لینک عکس‌ها
        image_urls = set()
        img_elements = driver.find_elements(By.TAG_NAME, "img")
        
        print(f"📷 پیدا شد {len(img_elements)} المنت تصویر")
        
        for img in img_elements:
            try:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    if 'freepik.com' in src and 'premium' not in src.lower():
                        clean_url = src.split('?')[0]
                        if clean_url.startswith('http'):
                            image_urls.add(clean_url)
            except:
                continue
        
        print(f"✅ {len(image_urls)} لینک معتبر پیدا شد")
        driver.quit()
        
        # انتخاب رندوم
        image_urls = list(image_urls)
        random.shuffle(image_urls)
        if len(image_urls) > num_links:
            image_urls = image_urls[:num_links]
        
        return image_urls
        
    except Exception as e:
        print(f"❌ خطا در Selenium: {e}")
        if driver:
            driver.quit()
        
        # اگر Selenium شکست خورد، از روش جایگزین استفاده کن
        print("🔧 استفاده از روش جایگزین...")
        return get_image_links_simple(query, num_links)

# دستورات ربات (همان قبلی)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
🤖 **ربات لینک‌ساز عکس**

🎯 **ویژگی‌ها:**
• جستجو در منابع مختلف
• دریافت لینک مستقیم عکس‌ها
• انتخاب رندوم از بین نتایج

📝 **نحوه استفاده:**
1. عبارت جستجو رو بنویس
2. تعداد لینک مورد نظر رو مشخص کن

حالا عبارت جستجو رو وارد کن...
    """
    await update.message.reply_text(welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    
    if 'user_data' not in context.chat_data:
        context.chat_data['user_data'] = {}
    
    user_data = context.chat_data['user_data']
    
    if 'query' not in user_data:
        user_data['query'] = user_message
        await update.message.reply_text(
            f"🔍 عبارت جستجو: {user_message}\n\n"
            f"📊 حالا تعداد لینک مورد نظر رو وارد کن (1-10):"
        )
        
    elif 'num_links' not in user_data:
        try:
            num_links = int(user_message)
            if not 1 <= num_links <= 10:
                await update.message.reply_text("⚠️ لطفاً عدد بین 1-10 وارد کن:")
                return
            
            user_data['num_links'] = num_links
            await update.message.reply_text("⏳ در حال جستجو... لطفاً منتظر بمانید")
            
            # دریافت لینک‌ها
            query = user_data['query']
            image_links = get_image_links(query, num_links)
            
            if image_links:
                await update.message.reply_text(f"✅ {len(image_links)} لینک پیدا شد:\n")
                
                for i, link in enumerate(image_links, 1):
                    message = f"📸 لینک {i}:\n`{link}`"
                    await update.message.reply_text(message, parse_mode='Markdown')
                    await asyncio.sleep(0.5)
                
                summary = f"🎉 **جستجو کامل شد!**\n\n🔍 عبارت: {query}\n📎 تعداد لینک: {len(image_links)}"
                await update.message.reply_text(summary)
                
            else:
                await update.message.reply_text("❌ هیچ عکسی پیدا نشد. عبارت رو تغییر بده")
            
            context.chat_data['user_data'] = {}
            
        except ValueError:
            await update.message.reply_text("⚠️ لطفاً عدد وارد کن")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"خطا: {context.error}")

def main():
    print("🤖 در حال راه‌اندازی ربات...")
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    print("✅ ربات آماده است...")
    app.run_polling(poll_interval=3)

if __name__ == "__main__":
    main()

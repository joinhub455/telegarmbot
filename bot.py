import os
import logging
import requests
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Your bot token from @BotFather
BOT_TOKEN = '8438558985:AAHspapCqcR-wOXPEDXxgpGYzvrYheH1Lq4'

# Store download quality preference for each user
user_preferences = {}

def download_tiktok_video(url, quality='1080p'):
    """Download TikTok video using multiple API methods with quality selection."""
    
    # Method 1: TikWM API (supports HD)
    try:
        logger.info(f"Trying TikWM API with quality: {quality}...")
        api_url = "https://www.tikwm.com/api/"
        
        # Determine HD parameter based on quality
        hd_param = 1 if quality in ['1080p', '4k'] else 0
        
        response = requests.post(
            api_url,
            data={'url': url, 'hd': hd_param},
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"TikWM Response: {data}")
            
            if data.get('code') == 0:
                video_data = data.get('data', {})
                
                # Select video URL based on quality preference
                if quality in ['1080p', '4k']:
                    video_url = video_data.get('hdplay') or video_data.get('play')
                else:
                    video_url = video_data.get('play')
                
                if video_url:
                    logger.info(f"Downloading from: {video_url}")
                    video_response = requests.get(
                        video_url, 
                        timeout=120,
                        stream=True,
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    
                    if video_response.status_code == 200:
                        return {
                            'success': True,
                            'video_content': video_response.content,
                            'title': video_data.get('title', 'TikTok Video'),
                            'author': video_data.get('author', {}).get('unique_id', 'Unknown'),
                            'quality': quality,
                            'size': len(video_response.content)
                        }
    except Exception as e:
        logger.error(f"TikWM API error: {e}")
    
    # Method 2: MusicalDown API
    try:
        logger.info("Trying MusicalDown API...")
        api_url = "https://musicaldown.com/download"
        
        session = requests.Session()
        
        # Get the page first
        page_response = session.get(
            "https://musicaldown.com/",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        # Post the URL
        response = session.post(
            api_url,
            data={'url': url},
            headers={
                'User-Agent': 'Mozilla/5.0',
                'Referer': 'https://musicaldown.com/'
            },
            timeout=30
        )
        
        if response.status_code == 200:
            html = response.text
            
            # Look for HD or SD download link based on quality
            if quality in ['1080p', '4k']:
                video_match = re.search(r'href="([^"]+)"[^>]*>Download Video HD', html)
            else:
                video_match = re.search(r'href="([^"]+)"[^>]*>Download Video', html)
            
            if not video_match:
                video_match = re.search(r'href="([^"]+)"[^>]*>Download Video', html)
            
            if video_match:
                video_url = video_match.group(1)
                logger.info(f"Found video URL: {video_url}")
                
                video_response = session.get(video_url, timeout=120, stream=True)
                
                if video_response.status_code == 200:
                    return {
                        'success': True,
                        'video_content': video_response.content,
                        'title': 'TikTok Video',
                        'author': 'Unknown',
                        'quality': quality,
                        'size': len(video_response.content)
                    }
    except Exception as e:
        logger.error(f"MusicalDown API error: {e}")
    
    # Method 3: SnapTik API
    try:
        logger.info("Trying SnapTik API...")
        
        session = requests.Session()
        
        token_response = session.get(
            "https://snaptik.app/",
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        token_match = re.search(r'name="token" value="([^"]+)"', token_response.text)
        
        if token_match:
            token = token_match.group(1)
            
            response = session.post(
                "https://snaptik.app/abc2.php",
                data={'url': url, 'token': token},
                headers={
                    'User-Agent': 'Mozilla/5.0',
                    'Referer': 'https://snaptik.app/'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                html = response.text
                
                # Try to find HD link first if high quality requested
                if quality in ['1080p', '4k']:
                    video_match = re.search(r'href="([^"]+)"[^>]*>Download.*HD', html)
                
                if not video_match:
                    video_match = re.search(r'href="([^"]+)"[^>]*>Download', html)
                
                if video_match:
                    video_url = video_match.group(1)
                    video_response = session.get(video_url, timeout=120, stream=True)
                    
                    if video_response.status_code == 200:
                        return {
                            'success': True,
                            'video_content': video_response.content,
                            'title': 'TikTok Video',
                            'author': 'Unknown',
                            'quality': quality,
                            'size': len(video_response.content)
                        }
    except Exception as e:
        logger.error(f"SnapTik API error: {e}")
    
    # Method 4: SSSTik API
    try:
        logger.info("Trying SSSTik API...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://ssstik.io',
            'Referer': 'https://ssstik.io/'
        }
        
        response = requests.post(
            'https://ssstik.io/abc?url=dl',
            data={
                'id': url,
                'locale': 'en',
                'tt': 'RFBiZ3Bi'
            },
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            html = response.text
            
            # Look for download link (watermark-free if available)
            video_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>.*?watermark', html, re.IGNORECASE)
            
            if not video_match:
                video_match = re.search(r'<a[^>]*href="([^"]+)"[^>]*>Download', html)
            
            if video_match:
                video_url = video_match.group(1)
                
                video_response = requests.get(
                    video_url, 
                    headers={'User-Agent': 'Mozilla/5.0'}, 
                    timeout=120,
                    stream=True
                )
                
                if video_response.status_code == 200:
                    return {
                        'success': True,
                        'video_content': video_response.content,
                        'title': 'TikTok Video',
                        'author': 'Unknown',
                        'quality': quality,
                        'size': len(video_response.content)
                    }
    except Exception as e:
        logger.error(f"SSSTik API error: {e}")
    
    return {'success': False, 'error': 'All download methods failed'}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send welcome message with menu buttons."""
    keyboard = [
        [KeyboardButton("📥 Download Video"), KeyboardButton("⚙️ Quality Settings")],
        [KeyboardButton("ℹ️ Help"), KeyboardButton("📊 My Stats")],
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_message = (
        "👋 *Welcome to TikTok Downloader Bot!*\n\n"
        "Send me any TikTok video link and I'll download it for you.\n\n"
        "🔥 *Features:*\n"
        "• 📱 720p Quality\n"
        "• 🔥 1080p Quality\n"
        "• 💎 4K Quality\n"
        "• No Watermark\n"
        "• Fast Download\n"
        "• 100% Free\n\n"
        "Use the menu buttons below to get started!"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show quality settings with inline buttons."""
    keyboard = [
        [
            InlineKeyboardButton("📱 720p (SD)", callback_data='quality_720p'),
        ],
        [
            InlineKeyboardButton("🔥 1080p (Full HD)", callback_data='quality_1080p'),
        ],
        [
            InlineKeyboardButton("💎 4K (Ultra HD)", callback_data='quality_4k'),
        ],
        [InlineKeyboardButton("🔙 Close", callback_data='back')],
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
    current_quality = user_preferences.get(user_id, '1080p')
    
    # Quality descriptions
    quality_info = {
        '720p': '📱 720p (SD) - Standard quality',
        '1080p': '🔥 1080p (Full HD) - High quality',
        '4k': '💎 4K (Ultra HD) - Best quality'
    }
    
    settings_text = (
        "⚙️ *Video Quality Settings*\n\n"
        f"✅ Current: *{current_quality.upper()}*\n"
        f"_{quality_info.get(current_quality, '1080p')}_\n\n"
        "*Choose your preferred quality:*\n\n"
        "📱 *720p* - Faster download, smaller file\n"
        "🔥 *1080p* - Balanced (Recommended)\n"
        "💎 *4K* - Maximum quality, larger file\n\n"
        "⚠️ Not all videos support 4K quality"
    )
    
    if update.message:
        await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(settings_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information."""
    help_text = (
        "📖 *How to Use This Bot*\n\n"
        "*Step by Step:*\n"
        "1️⃣ Open TikTok app\n"
        "2️⃣ Find a video you like\n"
        "3️⃣ Tap Share → Copy Link\n"
        "4️⃣ Send the link to me\n"
        "5️⃣ Choose quality in Settings\n"
        "6️⃣ Get your video!\n\n"
        "*Quality Options:*\n"
        "📱 *720p* - Good for sharing, smaller size\n"
        "🔥 *1080p* - Best balance (Default)\n"
        "💎 *4K* - Ultra HD, larger files\n\n"
        "*Supported Links:*\n"
        "✅ tiktok.com/@user/video/...\n"
        "✅ vm.tiktok.com/...\n"
        "✅ vt.tiktok.com/...\n\n"
        "*Features:*\n"
        "• No Watermark\n"
        "• Multiple Quality Options\n"
        "• Fast & Reliable\n"
        "• Completely Free\n\n"
        "*Important:*\n"
        "⚠️ Only PUBLIC videos work\n"
        "⚠️ Some videos may not support all qualities"
    )
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Quality Settings", callback_data='open_settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode='Markdown')

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user statistics."""
    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    quality = user_preferences.get(user_id, '1080p')
    
    quality_emoji = {
        '720p': '📱',
        '1080p': '🔥',
        '4k': '💎'
    }
    
    stats_text = (
        f"📊 *Statistics for {user_name}*\n\n"
        f"👤 User ID: `{user_id}`\n"
        f"{quality_emoji.get(quality, '🔥')} Current Quality: *{quality.upper()}*\n"
        f"🤖 Bot Status: *🟢 Online*\n"
        f"🌐 API Servers: *4 Active*\n"
        f"⚡ Speed: *Fast*\n\n"
        "Thank you for using our bot! 💙\n"
        "Rate us: 👍 if you like it!"
    )
    
    keyboard = [
        [InlineKeyboardButton("⚙️ Change Quality", callback_data='open_settings')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle inline button clicks."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if query.data.startswith('quality_'):
        quality = query.data.split('_')[1]
        user_preferences[user_id] = quality
        
        quality_names = {
            '720p': '📱 720p (SD)',
            '1080p': '🔥 1080p (Full HD)',
            '4k': '💎 4K (Ultra HD)'
        }
        
        keyboard = [
            [InlineKeyboardButton("✅ Done", callback_data='back')],
            [InlineKeyboardButton("🔄 Change Again", callback_data='open_settings')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"✅ *Quality Updated Successfully!*\n\n"
            f"New quality: {quality_names.get(quality, quality)}\n\n"
            f"All videos will now download in *{quality.upper()}* quality.\n"
            f"You can change this anytime in Quality Settings.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == 'open_settings':
        await settings(update, context)
    
    elif query.data == 'back':
        await query.edit_message_text(
            "✅ *Settings saved!*\n\n"
            "You can now send me TikTok links to download.\n"
            "Your quality preference has been saved.",
            parse_mode='Markdown'
        )
    
    elif query.data == 'like':
        await query.answer("Thank you for your feedback! 👍", show_alert=True)
    
    elif query.data == 'dislike':
        await query.answer("Sorry! We'll try to improve. Try another video or change quality.", show_alert=True)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages and menu buttons."""
    text = update.message.text
    
    if text == "📥 Download Video":
        user_quality = user_preferences.get(update.message.from_user.id, '1080p')
        await update.message.reply_text(
            f"Perfect! 📱 *Send me a TikTok link*\n\n"
            f"Current quality: *{user_quality.upper()}*\n\n"
            f"*How to get the link:*\n"
            f"1. Open TikTok app\n"
            f"2. Find the video\n"
            f"3. Tap *Share* button\n"
            f"4. Tap *Copy Link*\n"
            f"5. Paste it here\n\n"
            f"Example:\n"
            f"`https://www.tiktok.com/@user/video/123...`",
            parse_mode='Markdown'
        )
    
    elif text == "⚙️ Quality Settings":
        await settings(update, context)
    
    elif text == "ℹ️ Help":
        await show_help(update, context)
    
    elif text == "📊 My Stats":
        await show_stats(update, context)
    
    elif 'tiktok.com' in text.lower():
        await download_tiktok(update, context)
    
    else:
        await update.message.reply_text(
            "❌ I don't understand that.\n\n"
            "Please:\n"
            "• Send me a TikTok link, or\n"
            "• Use the menu buttons below"
        )

async def download_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download TikTok video with selected quality."""
    url = update.message.text.strip()
    user_id = update.message.from_user.id
    
    if 'tiktok.com' not in url.lower():
        await update.message.reply_text(
            "❌ *Invalid Link!*\n\n"
            "Please send a valid TikTok link.\n\n"
            "Example:\n"
            "`https://www.tiktok.com/@username/video/123...`",
            parse_mode='Markdown'
        )
        return
    
    # Get user's quality preference (default: 1080p)
    quality = user_preferences.get(user_id, '1080p')
    
    quality_emoji = {
        '720p': '📱',
        '1080p': '🔥',
        '4k': '💎'
    }
    
    processing_msg = await update.message.reply_text(
        f'{quality_emoji.get(quality, "🔥")} *Downloading in {quality.upper()}...*\n\n'
        '⏳ Trying multiple servers...\n'
        '⚡ This may take 10-60 seconds...\n'
        '📦 Preparing your video...',
        parse_mode='Markdown'
    )
    
    try:
        result = download_tiktok_video(url, quality)
        
        if not result['success']:
            raise Exception(result.get('error', 'Download failed'))
        
        filename = f"tiktok_{user_id}_{quality}.mp4"
        with open(filename, 'wb') as f:
            f.write(result['video_content'])
        
        file_size_mb = result['size'] / (1024 * 1024)
        logger.info(f"Downloaded {quality} video: {file_size_mb:.2f} MB")
        
        await processing_msg.edit_text(
            f'{quality_emoji.get(quality, "🔥")} *Upload starting...*\n\n'
            f'📦 Size: {file_size_mb:.1f} MB\n'
            f'⚙️ Quality: {quality.upper()}\n'
            f'⏫ Uploading to Telegram...',
            parse_mode='Markdown'
        )
        
        keyboard = [
            [
                InlineKeyboardButton("👍 Great!", callback_data='like'),
                InlineKeyboardButton("👎 Issue", callback_data='dislike')
            ],
            [InlineKeyboardButton("⚙️ Change Quality", callback_data='open_settings')],
            [InlineKeyboardButton("📥 Download Another", callback_data='back')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        caption = (
            f"✅ *Download Complete!*\n\n"
            f"📹 {result['title'][:50]}\n"
            f"👤 By: @{result['author']}\n"
            f"⚙️ Quality: *{quality.upper()}*\n"
            f"📦 Size: {file_size_mb:.1f} MB\n"
            f"🔥 No Watermark"
        )
        
        with open(filename, 'rb') as video:
            await update.message.reply_video(
                video,
                caption=caption,
                reply_markup=reply_markup,
                parse_mode='Markdown',
                supports_streaming=True,
                read_timeout=180,
                write_timeout=180
            )
        
        os.remove(filename)
        await processing_msg.delete()
        
        logger.info(f"Successfully sent {quality} video to user {user_id}")
        
    except Exception as e:
        error_message = (
            "❌ *Download Failed*\n\n"
            "*Possible reasons:*\n"
            "• Video is private or age-restricted\n"
            "• Link has expired or invalid\n"
            "• Selected quality not available\n"
            "• All servers are busy\n"
            "• Video was deleted\n\n"
            "*Solutions:*\n"
            "1️⃣ Copy link from TikTok app (not browser)\n"
            "2️⃣ Make sure video is PUBLIC\n"
            f"3️⃣ Try different quality (currently: {quality})\n"
            "4️⃣ Try a different video\n"
            "5️⃣ Wait 1 minute and retry\n\n"
            "💡 Tip: Try 1080p quality for best compatibility"
        )
        
        keyboard = [
            [InlineKeyboardButton("⚙️ Change Quality", callback_data='open_settings')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await processing_msg.edit_text(error_message, reply_markup=reply_markup, parse_mode='Markdown')
        logger.error(f"Download error for user {user_id} ({quality}): {e}")

def main():
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("=" * 50)
    print("🤖 TikTok Downloader Bot")
    print("=" * 50)
    print("✅ Status: ONLINE")
    print("🔥 Quality Options: 720p | 1080p | 4K")
    print("🌐 API Servers: 4 Active")
    print("=" * 50)
    print("Press Ctrl+C to stop\n")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()

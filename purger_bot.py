import discord
from discord.ext import commands
import os
import asyncio
import logging
from dotenv import load_dotenv

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('purger_selfbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Selfbot configuration
bot = commands.Bot(command_prefix=".", self_bot=True)

# Global variable for automatic user monitoring (Auto-Delete)
target_user_id = None

@bot.event
async def on_ready():
    logger.info(f"Selfbot logged in as {bot.user}")
    print(f"--- SELFBOT READY ---")
    print(f"Commands:")
    print(f"  .purge_user @User [limit]  - Delete history (0 = full history scan)")
    print(f"  .watch_user @User         - Toggle real-time auto-deletion of new messages")

@bot.event
async def on_message(message):
    global target_user_id
    
    # Auto-delete new messages from the targeted user if monitoring is active
    if target_user_id and message.author.id == target_user_id:
        try:
            await message.delete()
            print(f"🔥 [AUTO-DELETE] Deleted new message from {message.author.name}")
        except:
            pass
            
    await bot.process_commands(message)

@bot.command(name="watch_user")
async def watch_user(ctx, user: discord.User = None):
    global target_user_id
    
    try:
        await ctx.message.delete()
    except:
        pass
        
    if user is None or (target_user_id == user.id):
        target_user_id = None
        print("🛑 Stopped automatic monitoring.")
        await ctx.author.send("🛑 Real-time monitoring disabled.")
    else:
        target_user_id = user.id
        print(f"👀 Started monitoring user: {user.name}")
        await ctx.author.send(f"👀 Real-time monitoring enabled for: {user.name}. Type `.watch_user` again to disable.")

@bot.command(name="purge_user")
async def purge_user(ctx, user: discord.User = None, limit: int = 1000):
    """
    Deletes messages from a specific user.
    If no user is specified, it cleans your own messages.
    """
    target = user or ctx.author
    actual_limit = limit if limit > 0 else None
    limit_text = f"limit: {limit}" if actual_limit else "NO LIMIT (full history scan)"

    try:
        await ctx.message.delete()
    except:
        pass

    print(f"--- STARTED DEEP CLEANUP FOR {target.name} ({limit_text}) ---")
    
    scanned_count = 0
    deleted_count = 0
    
    async def process_messages(history_iterator):
        nonlocal scanned_count, deleted_count
        async for message in history_iterator:
            scanned_count += 1
            
            if scanned_count % 1000 == 0:
                print(f"📡 Scanned {scanned_count} messages in the channel...")

            if message.author.id == target.id:
                try:
                    await message.delete()
                    deleted_count += 1
                    print(f"🔥 [DELETE] #{deleted_count} (Scanned: {scanned_count})")
                    
                    # Safe delay for selfbots
                    await asyncio.sleep(2.2)
                    
                except discord.HTTPException as e:
                    if e.status == 429:
                        wait_time = e.retry_after + 2
                        print(f"⚠️ Rate limit hit! Waiting {wait_time:.2f}s...")
                        await asyncio.sleep(wait_time)
                        try: # Retry once after waiting
                            await message.delete()
                            deleted_count += 1
                        except: pass
                    else:
                        print(f"❌ API Error: {e}")

    try:
        # 1. Scan main channel history
        await process_messages(ctx.channel.history(limit=actual_limit))
        
        # 2. Scan threads if no limit is set
        if hasattr(ctx.channel, 'threads') and not actual_limit:
            print(f"🧵 Checking threads in channel: {ctx.channel.name}...")
            for thread in ctx.channel.threads:
                await process_messages(thread.history(limit=None))

        msg_text = f"✅ FINISHED! Deleted **{deleted_count}** messages from {target.name} (Scanned {scanned_count} total messages on {ctx.channel.name})."
        print(f"--- {msg_text} ---")
        logger.info(msg_text)
        
        try:
            await ctx.author.send(msg_text)
        except:
            pass
            
    except Exception as e:
        print(f"❌ Critical error during scan: {e}")
        logger.error(f"Critical Error: {e}")

@bot.event
async def on_command_error(ctx, error):
    error_msg = ""
    if isinstance(error, commands.UserNotFound):
        error_msg = "❌ User not found."
    elif isinstance(error, commands.MissingRequiredArgument):
        error_msg = "❌ Usage: `.purge_user @User [limit]` or `.watch_user @User`"
    else:
        error_msg = f"❌ Command error: {error}"
    
    print(error_msg)
    try:
        await ctx.author.send(error_msg)
    except:
        pass
    
    try:
        await ctx.message.delete()
    except:
        pass

if __name__ == "__main__":
    if TOKEN:
        try:
            bot.run(TOKEN)
        except discord.LoginFailure:
            print("CRITICAL: Login failed. Make sure DISCORD_BOT_TOKEN in .env is your USER TOKEN, not a bot token.")
    else:
        print("CRITICAL: Missing DISCORD_BOT_TOKEN in .env file")

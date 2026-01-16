import discord
from discord.ext import commands
import os
import asyncio
import logging
import re
from datetime import datetime
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler
from rich.text import Text

# Initialize Rich Console
console = Console()

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    datefmt="[%X]",
    handlers=[
        logging.FileHandler('purger_selfbot.log'),
        RichHandler(console=console, rich_tracebacks=True)
    ]
)
logger = logging.getLogger("purger")

def draw_banner():
    banner_text = r"""
    [magenta]
    ██████╗ ██╗   ██╗██████╗  ██████╗ ███████╗██████╗ 
    ██╔══██╗██║   ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗
    ██████╔╝██║   ██║██████╔╝██║  ███╗█████╗  ██████╔╝
    ██╔═══╝ ██║   ██║██╔══██╗██║   ██║██╔══╝  ██╔══██╗
    ██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗██║  ██║
    ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
    [/magenta]
              [white]      .-.      [/white]
              [white]     (o o)     [/white]
              [white]     | O |     [/white]
              [white]    /     \    [/white]
              [white]   |       |   [/white]
              [white]   '~^~^~^~'   [/white]

    [cyan]        >> DISCORD MESSAGE PURGER SELFBOT << [/cyan]
    [bold yellow]              Created by GH0ST [/bold yellow]
    """
    console.print(Panel(banner_text.strip(), border_style="magenta"))

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Selfbot configuration
bot = commands.Bot(command_prefix=".", self_bot=True)

# Global configuration state
target_user_id = None
watched_words = []
whitelist_ids = set()
deletion_delay = 2.2 # Default safe delay
cancel_purge = False # Global flag for stopping ongoing operations

URL_REGEX = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

@bot.event
async def on_ready():
    draw_banner()
    
    table = Table(title="Advanced Commands", show_header=True, header_style="bold cyan")
    table.add_column("Command", style="magenta", no_wrap=True)
    table.add_column("Usage", style="green")
    table.add_column("Description", style="white")
    
    table.add_row(".purge_user", ".purge_user @User [limit]", "Delete user messages (0=full)")
    table.add_row(".purge_word", ".purge_word <word> [limit]", "Delete messages with word (0=full)")
    table.add_row(".purge_media", ".purge_media [limit]", "Delete messages with attachments")
    table.add_row(".purge_links", ".purge_links [limit]", "Delete messages with links")
    table.add_row(".purge_since", ".purge_since <YYYY-MM-DD>", "Delete messages after date")
    table.add_row(".watch_user", ".watch_user @User", "Toggle user monitoring")
    table.add_row(".watch_word", ".watch_word <word>", "Add/remove word from monitoring")
    table.add_row(".whitelist", ".whitelist <add/list/clear>", "Manage protected messages")
    table.add_row(".speed", ".speed <safe/fast/insane>", "Adjust deletion delay")
    table.add_row(".multipurge", ".multipurge #c1 #c2", "Purge across multiple channels")
    table.add_row(".stop", ".stop", "Cancel any ongoing purge operation")
    table.add_row(".shutdown", ".shutdown", "Gracefully stop the bot")
    
    console.print(table)
    console.print(f"[bold green]Selfbot logged in as {bot.user}[/bold green]\n")
    logger.info(f"Selfbot logged in as {bot.user}")

async def smart_purge(ctx, history_iterator, scanned_limit=None, filter_func=None):
    """
    Unified purging logic with rate-limit handling, whitelist protection, 
    dynamic delays, and permission auto-detection.
    """
    global whitelist_ids, deletion_delay, cancel_purge
    cancel_purge = False # Reset flag when a new purge starts
    scanned_count = 0
    deleted_count = 0
    
    # 🕵️ Permission Check: Can we delete other people's messages?
    permissions = ctx.channel.permissions_for(ctx.author)
    can_manage = permissions.manage_messages or permissions.administrator
    
    if not can_manage:
        console.print("[bold yellow]⚠️ No 'Manage Messages' permission! Switching to PERSONAL MODE (clearing only your own content).[/bold yellow]")

    async for message in history_iterator:
        if cancel_purge:
            console.print("[bold yellow]🛑 Purge operation cancelled by user.[/bold yellow]")
            break
            
        scanned_count += 1
        
        # Stop if we hit the limit
        if scanned_limit and scanned_count > scanned_limit:
            break
            
        if scanned_count % 100 == 0:
            console.print(f"[blue]📡 Scanned {scanned_count} messages...[/blue]", end="\r")

        # Whitelist protection
        if message.id in whitelist_ids:
            continue

        # Logic: If no admin perms, we ONLY delete OUR messages, even if filter_func matches.
        # If we have admin perms, we follow the filter_func exactly.
        is_own_message = message.author.id == bot.user.id
        
        if filter_func(message):
            if can_manage or is_own_message:
                try:
                    await message.delete()
                    deleted_count += 1
                    
                    # Truncate content for cleaner output
                    content = (message.content[:40] + '...') if len(message.content) > 40 else message.content
                    content = content.replace("\n", " ") # Keep it on one line
                    
                    console.print(f"[bold red]🔥 [DELETE][/bold red] [cyan]#{deleted_count}[/cyan] [dim]|[/dim] [green]#{message.channel.name}[/green] [dim]|[/dim] [white]{content}[/white]")
                    await asyncio.sleep(deletion_delay)
                except discord.HTTPException as e:
                    if e.status == 429:
                        wait_time = e.retry_after + 2
                        console.print(f"[bold yellow]⚠️ Rate limit hit! Waiting {wait_time:.2f}s...[/bold yellow]")
                        await asyncio.sleep(wait_time)
                        try: 
                            await message.delete()
                            deleted_count += 1
                        except: pass
                    else:
                        console.print(f"[bold red]❌ API Error: {e}[/bold red]")
                    
    return scanned_count, deleted_count

@bot.event
async def on_message(message):
    global target_user_id, watched_words, whitelist_ids
    
    # Pre-check: Never auto-delete whitelisted messages
    if message.id in whitelist_ids:
        await bot.process_commands(message)
        return

    # 1. Auto-delete new messages from the targeted user
    is_everyone = target_user_id == "everyone"
    is_target_user = target_user_id and message.author.id == target_user_id
    
    if (is_everyone or is_target_user) and message.author.id != bot.user.id:
        try:
            await message.delete()
            mode_label = "EVERYONE" if is_everyone else "USER"
            
            # Truncate content for cleaner output
            content = (message.content[:500] + '...') if len(message.content) > 500 else message.content
            content = content.replace("\n", " ")
            
            console.print(f"[bold red]🔥 [AUTO-DELETE-{mode_label}][/bold red] [cyan]{message.author}[/cyan] [dim]|[/dim] [white]{content}[/white]")
        except:
            pass
            
    # 2. Auto-delete messages containing watched words
    content_lower = message.content.lower()
    for word in watched_words:
        if word.lower() in content_lower:
            try:
                await message.delete()
                
                # Truncate content for cleaner output
                disp_content = (message.content[:500] + '...') if len(message.content) > 500 else message.content
                disp_content = disp_content.replace("\n", " ")
                
                console.print(f"[bold red]🔥 [WATCH-WORD][/bold red] '[yellow]{word}[/yellow]' [dim]|[/dim] [cyan]{message.author}[/cyan] [dim]|[/dim] [white]{disp_content}[/white]")
                break # One deletion is enough
            except:
                pass

    await bot.process_commands(message)

@bot.command(name="watch_user")
async def watch_user(ctx, user_input: str = None):
    global target_user_id
    
    try:
        await ctx.message.delete()
    except:
        pass
        
    # Check for "everyone" or "@everyone"
    is_everyone = user_input and user_input.lower() in ["everyone", "@everyone"]
    
    if user_input is None or (not is_everyone and target_user_id == user_input):
        # Reset if no input or toggling off specific user ID string (legacy check)
        target_user_id = None
        console.print("[bold yellow]🛑 Stopped monitoring.[/bold yellow]")
        return

    if is_everyone:
        if target_user_id == "everyone":
            target_user_id = None
            console.print("[bold yellow]🛑 Stopped monitoring everyone.[/bold yellow]")
        else:
            target_user_id = "everyone"
            console.print("[bold green]👀 Started monitoring EVERYONE.[/bold green]")
        return

    # Try to resolve user
    try:
        # Check if it's a mention or ID
        converter = commands.UserConverter()
        user = await converter.convert(ctx, user_input)
        
        if target_user_id == user.id:
            target_user_id = None
            console.print(f"[bold yellow]🛑 Stopped monitoring user: {user.name}[/bold yellow]")
        else:
            target_user_id = user.id
            console.print(f"[bold green]👀 Started monitoring user: {user.name}[/bold green]")
    except commands.BadArgument:
        console.print(f"[bold red]❌ Could not find user: {user_input}[/bold red]")


@bot.command(name="watch_word")
async def watch_word(ctx, word: str = None):
    global watched_words
    
    try:
        await ctx.message.delete()
    except:
        pass
        
    if word is None:
        console.print(f"[cyan]📋 Currently watched words: {', '.join(watched_words) or 'None'}[/cyan]")
        return

    if word.lower() in [w.lower() for w in watched_words]:
        watched_words = [w for w in watched_words if w.lower() != word.lower()]
        console.print(f"🛑 Stopped monitoring word: {word}")
    else:
        watched_words.append(word)
        console.print(f"👀 Started monitoring word: {word}")

@bot.command(name="purge_user")
async def purge_user(ctx, user: discord.User = None, limit: int = 1000):
    target = user or ctx.author
    actual_limit = limit if limit > 0 else None

    try:
        await ctx.message.delete()
    except:
        pass

    console.print(f"[bold cyan]--- STARTED PURGE FOR {target.name} ---[/bold cyan]")
    
    s_count, d_count = await smart_purge(
        ctx, 
        ctx.channel.history(limit=actual_limit), 
        filter_func=lambda m: m.author.id == target.id
    )

    msg = f"✅ Deleted {d_count} messages from {target.name} (Scanned {s_count})"
    console.print(f"[bold green]{msg}[/bold green]")

@bot.command(name="purge_word")
async def purge_word(ctx, word: str, limit: int = 1000):
    actual_limit = limit if limit > 0 else None

    try:
        await ctx.message.delete()
    except:
        pass

    console.print(f"[bold cyan]--- STARTED PURGE FOR WORD: '{word}' ---[/bold cyan]")
    
    s_count, d_count = await smart_purge(
        ctx, 
        ctx.channel.history(limit=actual_limit), 
        filter_func=lambda m: word.lower() in m.content.lower()
    )

    msg = f"✅ Deleted {d_count} messages containing '{word}' (Scanned {s_count})"
    console.print(f"[bold green]{msg}[/bold green]")

@bot.command(name="purge_media")
async def purge_media(ctx, limit: int = 1000):
    actual_limit = limit if limit > 0 else None

    try:
        await ctx.message.delete()
    except:
        pass

    console.print(f"[bold cyan]--- STARTED PURGE FOR MEDIA/ATTACHMENTS ---[/bold cyan]")
    
    s_count, d_count = await smart_purge(
        ctx, 
        ctx.channel.history(limit=actual_limit), 
        filter_func=lambda m: len(m.attachments) > 0
    )

    msg = f"✅ Deleted {d_count} messages with media (Scanned {s_count})"
    console.print(f"[bold green]{msg}[/bold green]")

@bot.command(name="purge_links")
async def purge_links(ctx, limit: int = 1000):
    actual_limit = limit if limit > 0 else None

    try:
        await ctx.message.delete()
    except:
        pass

    console.print(f"[bold cyan]--- STARTED PURGE FOR LINKS ---[/bold cyan]")
    
    s_count, d_count = await smart_purge(
        ctx, 
        ctx.channel.history(limit=actual_limit), 
        filter_func=lambda m: re.search(URL_REGEX, m.content)
    )

    msg = f"✅ Deleted {d_count} messages with links (Scanned {s_count})"
    console.print(f"[bold green]{msg}[/bold green]")

@bot.command(name="purge_since")
async def purge_since(ctx, date_str: str, limit: int = 1000):
    try:
        since_date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        console.print("❌ Invalid format! Use: `.purge_since YYYY-MM-DD`")
        return

    actual_limit = limit if limit > 0 else None

    try:
        await ctx.message.delete()
    except:
        pass

    console.print(f"[bold cyan]--- STARTED PURGE SINCE {date_str} ---[/bold cyan]")
    
    s_count, d_count = await smart_purge(
        ctx, 
        ctx.channel.history(limit=actual_limit, after=since_date), 
        filter_func=lambda m: True # All messages after date
    )

    msg = f"✅ Deleted {d_count} messages since {date_str} (Scanned {s_count})"
    console.print(f"[bold green]{msg}[/bold green]")

@bot.command(name="whitelist")
async def whitelist(ctx, action: str = "list", message_id: int = None):
    global whitelist_ids
    
    try:
        await ctx.message.delete()
    except:
        pass

    if action == "add" and message_id:
        whitelist_ids.add(message_id)
        msg = f"🛡️ Added message `{message_id}` to whitelist."
    elif action == "remove" and message_id:
        whitelist_ids.discard(message_id)
        msg = f"🔓 Removed message `{message_id}` from whitelist."
    elif action == "clear":
        whitelist_ids.clear()
        msg = "🧹 Whitelist cleared."
    else:
        msg = f"📋 Current Whitelist: {', '.join(map(str, whitelist_ids)) or 'Empty'}"

    console.print(msg)

@bot.command(name="speed")
async def speed(ctx, mode: str = "safe"):
    global deletion_delay
    
    try:
        await ctx.message.delete()
    except:
        pass

    modes = {
        "safe": 2.2,
        "fast": 1.2,
        "insane": 0.5
    }

    if mode in modes:
        deletion_delay = modes[mode]
    else:
        try:
            deletion_delay = float(mode)
        except ValueError:
            console.print("❌ Usage: `.speed <safe/fast/insane/float>`")
            return

    msg = f"⚡ Speed set to: {mode} ({deletion_delay}s delay)"
    console.print(f"[bold yellow]{msg}[/bold yellow]")

@bot.command(name="multipurge")
async def multipurge(ctx, *channels: discord.TextChannel):
    if not channels:
        console.print("❌ Usage: `.multipurge #chan1 #chan2 ...`")
        return

    try:
        await ctx.message.delete()
    except:
        pass

    console.print(f"[bold cyan]--- STARTED MULTI-CHANNEL PURGE ({len(channels)} channels) ---[/bold cyan]")
    
    total_deleted = 0
    for channel in channels:
        if cancel_purge:
            break
            
        console.print(f"[magenta]🌐 Purging channel: {channel.name}...[/magenta]")
        try:
            _, d_count = await smart_purge(
                ctx, 
                channel.history(limit=1000), # Default limit for multipurge
                filter_func=lambda m: m.author.id == bot.user.id
            )
            total_deleted += d_count
        except Exception as e:
            console.print(f"[red]❌ Error in {channel.name}: {e}[/red]")

    msg = f"✅ MULTI-PURGE FINISHED! Deleted {total_deleted} messages across {len(channels)} channels."
    console.print(f"[bold green]{msg}[/bold green]")

@bot.command(name="shutdown")
async def shutdown(ctx):
    try:
        await ctx.message.delete()
    except:
        pass

    msg = "👋 Selfbot is shutting down. Goodbye!"
    console.print(f"\n[bold magenta]{'='*40}[/bold magenta]")
    console.print(f"[bold magenta]   {msg}   [/bold magenta]")
    console.print(f"[bold magenta]{'='*40}[/bold magenta]\n")
    
    await bot.close()

@bot.command(name="stop")
async def stop_purge(ctx):
    global cancel_purge
    cancel_purge = True
    
    try:
        await ctx.message.delete()
    except:
        pass
        
    msg = "🛑 Requested purge cancellation..."
    console.print(f"[bold yellow]{msg}[/bold yellow]")

@bot.event
async def on_command_error(ctx, error):
    error_msg = ""
    if isinstance(error, commands.UserNotFound):
        error_msg = "❌ User not found."
    elif isinstance(error, commands.MissingRequiredArgument):
        error_msg = "❌ Missing argument. Check `.on_ready` for command list."
    elif isinstance(error, commands.ChannelNotFound):
        error_msg = "❌ Channel not found."
    elif isinstance(error, commands.BadArgument):
        error_msg = "❌ Bad argument. Make sure ID or mention is correct."
    else:
        error_msg = f"❌ Command error: {error}"
    
    print(error_msg)
    
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

# 🤖 Discord Bot Top.gg Integration Guide

A comprehensive guide on how to properly integrate your Discord bot with Top.gg, focusing on command posting and synchronization using discord.py only idk discord.js lol 

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [⚙️ Setup & Configuration](#️-setup--configuration)
- [🔧 Environment Variables](#-environment-variables)
- [📡 Top.gg Integration](#-topgg-integration)
- [🎯 Command Synchronization](#-command-synchronization)
- [📊 Server Count Posting](#-server-count-posting)
- [🛠️ Usage Examples](#️-usage-examples)
- [🐛 Troubleshooting](#-troubleshooting)
- [📚 Advanced Features](#-advanced-features)
- [❓ FAQ](#-faq)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- A Discord bot application
- Top.gg account and bot listing

### Installation

1. **Clone or download the files:**
   ```bash
   # Download main.py and place it in your project directory
   ```

2. **Install required dependencies:**
   ```bash
   pip install discord.py python-dotenv aiohttp
   ```

3. **Create a `.env` file:**
   ```env
   BOT_TOKEN=your_discord_bot_token_here
   Commands-TK=your_topgg_commands_token_here
   APPLICATION_ID=your_bot_application_id
   ```

4. **Run the bot:**
   ```bash
   python main.py
   ```

## ⚙️ Setup & Configuration

### Discord Bot Setup

1. **Create a Discord Application:**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Click "New Application"
   - Give your bot a name and create it

2. **Create a Bot User:**
   - Navigate to the "Bot" section
   - Click "Add Bot"
   - Copy the bot token (keep this secret!)

3. **Configure Bot Permissions:**
   ```python
   # Required intents for the bot
   intents = discord.Intents.default()
   intents.message_content = True  # For reading message content
   intents.members = True          # For member-related events
   intents.guilds = True           # For guild-related events
   ```

### Top.gg Setup

1. **Create a Top.gg Account:**
   - Visit [Top.gg](https://top.gg/)
   - Sign up with your Discord account

2. **Add Your Bot:**
   - Go to "Add Bot" on Top.gg
   - Fill in your bot's information
   - Submit for approval

3. **Get API Tokens:**
   - **Server Count Token:** Found in your bot's page settings
   - **Commands Token:** Available in the API section

## 🔧 Environment Variables

Create a `.env` file in your project root with the following variables:

```env
# Required
BOT_TOKEN=your_discord_bot_token_here

# Optional but recommended for Top.gg integration
TOPGG_TOKEN=your_topgg_server_count_token
Commands-TK=your_topgg_commands_token (get this from your bot profile under the integration & API tab make sure to give both read and write permissions and name it anything you want)
APPLICATION_ID=your_bot_application_id
```

### Environment Variable Descriptions

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ Yes | Your Discord bot's token |
| `TOPGG_TOKEN` | ❌ Optional | Token for posting server count to Top.gg |
| `Commands-TK` | ✅ | Token for posting commands to Top.gg aka v1 token |
| `APPLICATION_ID` | ✅ Optional | Your bot's application ID |

## 📡 Top.gg Integration

### Server Count Posting

The bot automatically posts server count to Top.gg every 30 minutes:

```python
async def post_server_count(self) -> bool:
    """Post the bot's server count to Top.gg"""
    url = f"https://top.gg/api/bots/{self.bot.user.id}/stats"
    headers = {
        "Authorization": self.topgg_token,
        "Content-Type": "application/json"
    }
    payload = {
        "server_count": len(self.bot.guilds),
        "shard_count": getattr(self.bot, 'shard_count', 1) or 1
    }
    
    # POST request to Top.gg API
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            return response.status == 200
```

### Command Posting

Commands are automatically posted to Top.gg every 24 hours:

```python
async def post_commands_to_topgg(self) -> bool:
    """Post bot commands to Top.gg"""
    url = f"https://top.gg/api/v1/projects/@me/commands"
    headers = {
        "Authorization": f"Bearer {self.commands_token}",
        "Content-Type": "application/json"
    }
    
    commands_data = await self._get_bot_commands_for_topgg()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=commands_data) as response:
            return response.status in [200, 204]
```

## 🎯 Command Synchronization

### Understanding Command Sync

Discord bots need to sync their slash commands with Discord's API. There are two types of syncing:

1. **Guild Sync (Fast):** Commands appear immediately in a specific server
2. **Global Sync (Slow):** Commands appear in all servers (takes up to 1 hour)

### Sync Implementation

```python
class CommandSyncer:
    async def sync_commands(self, guild_id: Optional[int] = None) -> int:
        """Sync commands to Discord"""
        if guild_id:
            # Sync to specific guild (for testing)
            guild = discord.Object(id=guild_id)
            synced = await self.bot.tree.sync(guild=guild)
        else:
            # Sync globally (for production)
            synced = await self.bot.tree.sync()
        
        return len(synced)
```

### When to Sync Commands

- **Development:** Sync to a test guild for immediate updates
- **Production:** Sync globally when deploying new commands
- **Updates:** Only sync when commands change to avoid rate limits

## 📊 Server Count Posting

### Automatic Updates

The bot automatically updates server count when:
- Bot starts up
- Joins a new server
- Leaves a server
- Every 30 minutes (periodic update)

### Manual Server Count Update

```python
# Create Top.gg integration instance
topgg = TopGGIntegration(bot)

# Post server count manually
success = await topgg.post_server_count()
if success:
    print("✅ Server count updated successfully")
else:
    print("❌ Failed to update server count")
```

## 🛠️ Usage Examples

### Basic Bot Setup

```python
import discord
from discord.ext import commands

# Create bot with proper intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot logged in as {bot.user}')
    
    # Initialize Top.gg integration
    topgg = TopGGIntegration(bot)
    await topgg.start_periodic_updates()

bot.run('YOUR_BOT_TOKEN')
```

### Creating Slash Commands

```python
@bot.tree.command(name="hello", description="Say hello!")
async def hello(interaction: discord.Interaction, name: str):
    """A simple slash command with a parameter"""
    await interaction.response.send_message(f"Hello, {name}! 👋")

@bot.tree.command(name="serverinfo", description="Get server information")
async def serverinfo(interaction: discord.Interaction):
    """Command that shows server information"""
    guild = interaction.guild
    embed = discord.Embed(
        title=f"📊 {guild.name}",
        description=f"Server information for {guild.name}",
        color=discord.Color.blue()
    )
    embed.add_field(name="Members", value=guild.member_count, inline=True)
    embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    
    await interaction.response.send_message(embed=embed)
```

### Command Groups

```python
@bot.tree.command(name="admin")
async def admin_group(interaction: discord.Interaction):
    """Admin command group"""
    pass

@admin_group.command(name="kick", description="Kick a user")
async def admin_kick(interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
    """Kick command within admin group"""
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("❌ You don't have permission to kick members!", ephemeral=True)
        return
    
    try:
        await user.kick(reason=reason)
        await interaction.response.send_message(f"✅ Kicked {user.mention} for: {reason}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to kick this user!", ephemeral=True)
```

### Context Menu Commands

```python
@bot.tree.context_menu(name="Get User Info")
async def user_info(interaction: discord.Interaction, user: discord.Member):
    """Right-click context menu for user info"""
    embed = discord.Embed(
        title=f"👤 {user.display_name}",
        color=user.color
    )
    embed.add_field(name="Username", value=str(user), inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.add_field(name="Joined", value=user.joined_at.strftime("%Y-%m-%d"), inline=True)
    embed.set_thumbnail(url=user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Commands Not Syncing

**Problem:** Slash commands don't appear in Discord

**Solutions:**
```python
# Check if commands are properly defined
print(f"Commands in tree: {len(bot.tree.get_commands())}")

# Sync to a test guild first (faster)
await bot.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID))

# Check for errors in command definitions
try:
    synced = await bot.tree.sync()
    print(f"Synced {len(synced)} commands")
except Exception as e:
    print(f"Sync failed: {e}")
```

#### 2. Top.gg API Errors

**Problem:** Server count or commands not posting to Top.gg

**Common Error Codes:**
- `401 Unauthorized`: Invalid token
- `405 Forbidden`: Mehtod not allowed (ONLY poST request allowed
- `429 Too Many Requests`: Rate limited

**Solutions:**
```python
# Check token validity
if not TOPGG_TOKEN:
    print("❌ Top.gg token not set")

# Add error handling
try:
    success = await topgg.post_server_count()
    if not success:
        print("❌ Failed to post server count")
except Exception as e:
    print(f"❌ Top.gg error: {e}")
```

#### 3. Permission Issues

**Problem:** Bot can't perform certain actions

**Solutions:**
```python
# Check bot permissions
@bot.event
async def on_guild_join(guild):
    # Check if bot has necessary permissions
    permissions = guild.me.guild_permissions
    if not permissions.send_messages:
        print(f"❌ Missing send_messages permission in {guild.name}")
```

#### 4. Environment Variables Not Loading

**Problem:** Bot can't find tokens

**Solutions:**
```python
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Check if variables are loaded
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ BOT_TOKEN not found in environment")
    exit(1)
```

### Debug Mode

Enable debug logging to see detailed information:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Or for discord.py specific logging
logging.getLogger('discord').setLevel(logging.DEBUG)
```

## 📚 Advanced Features

### Rate Limit Handling

```python
import asyncio
from discord.errors import RateLimited

async def safe_api_call(func, *args, **kwargs):
    """Safely make API calls with rate limit handling"""
    try:
        return await func(*args, **kwargs)
    except RateLimited as e:
        print(f"Rate limited, waiting {e.retry_after} seconds")
        await asyncio.sleep(e.retry_after)
        return await func(*args, **kwargs)
```

### Sharding Support

For large bots (2500+ servers):

```python
import discord
from discord.ext import commands

class ShardedBot(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix='!',
            intents=intents,
            shard_count=4  # Adjust based on your bot size
        )

bot = ShardedBot()
```

### Command Cooldowns

```python
from discord.ext import commands

@bot.tree.command(name="limited", description="Command with cooldown")
@app_commands.describe(message="Message to send")
async def limited_command(interaction: discord.Interaction, message: str):
    """Command with built-in cooldown handling"""
    # Implement your own cooldown logic
    user_id = interaction.user.id
    current_time = time.time()
    
    # Check cooldown (example: 60 seconds)
    if user_id in cooldowns and current_time - cooldowns[user_id] < 60:
        remaining = 60 - (current_time - cooldowns[user_id])
        await interaction.response.send_message(
            f"⏰ Please wait {remaining:.1f} seconds before using this command again!",
            ephemeral=True
        )
        return
    
    cooldowns[user_id] = current_time
    await interaction.response.send_message(f"📢 {message}")
```

### Error Handling

```python
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Global error handler for slash commands"""
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏰ Command is on cooldown. Try again in {error.retry_after:.2f} seconds.",
            ephemeral=True
        )
    elif isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command!",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "❌ An error occurred while processing your command.",
            ephemeral=True
        )
        print(f"Unhandled error: {error}")
```

## ❓ FAQ

### Q: How often should I sync commands?

**A:** Only sync when you add, remove, or modify commands. Excessive syncing can lead to rate limits.

### Q: Why aren't my commands showing up?

**A:** 
- Global sync takes up to 1 hour to propagate
- Try syncing to a test guild first for immediate testing
- Check for errors in your command definitions

### Q: Can I post to Top.gg without the commands token?

**A:** Yes! The commands token is optional. You can still post server counts with just the main Top.gg token.

### Q: How do I handle different command types?

**A:** The integration automatically handles:
- Regular slash commands (`/command`)
- Command groups (`/group subcommand`)
- Context menu commands (right-click menus)

### Q: What if my bot is in 2500+ servers?

**A:** Consider using `AutoShardedBot` instead of regular `Bot` for better performance and reliability.

### Q: How do I test commands locally?

**A:** 
1. Create a test Discord server
2. Sync commands to that specific guild
3. Commands will appear immediately for testing

```python
# Sync to test guild
TEST_GUILD_ID = 123456789012345678
await bot.tree.sync(guild=discord.Object(id=TEST_GUILD_ID))
```

### Q: Can I customize the posting intervals?

**A:** Yes! Modify the sleep times in the periodic functions:

```python
async def _periodic_server_count(self):
    while True:
        await self.post_server_count()
        await asyncio.sleep(900)  # 15 minutes instead of 30
```

---



### Support

If you encounter issues:
- Join https://discord.gg/dbl and ping @techcodes27 lol 
- Check Top.gg API documentation

Happy coding! 🚀✨

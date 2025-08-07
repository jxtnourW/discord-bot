import discord
from discord.ext import commands
import asyncio
import logging
import os
from config import BOT_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('discord_member_bot')

# Bot intents - required for member events
intents = discord.Intents.default()
intents.members = True  # Required to detect member join events
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    """Event fired when bot is ready and connected to Discord."""
    logger.info(f'{bot.user} has connected to Discord!')
    logger.info(f'Bot is ready and serving {len(bot.guilds)} guild(s)')
    
    # Log guilds the bot is in
    for guild in bot.guilds:
        logger.info(f'Connected to guild: {guild.name} (ID: {guild.id})')

@bot.event
async def on_member_join(member):
    """
    Event fired when a new member joins a guild.
    Automatically assigns the configured member role to the new user.
    """
    guild = member.guild
    role_name = BOT_CONFIG['MEMBER_ROLE_NAME']
    
    logger.info(f'New member joined {guild.name}: {member.name}#{member.discriminator} (ID: {member.id})')
    
    try:
        # Find the member role in the guild
        member_role = discord.utils.get(guild.roles, name=role_name)
        
        if member_role is None:
            logger.error(f'Role "{role_name}" not found in guild "{guild.name}". Please create this role or update the configuration.')
            return
        
        # Check if bot has permission to manage roles
        if not guild.me.guild_permissions.manage_roles:
            logger.error(f'Bot lacks "Manage Roles" permission in guild "{guild.name}"')
            return
        
        # Check if the bot's role is higher than the member role
        if guild.me.top_role <= member_role:
            logger.error(f'Bot\'s highest role is not above the "{role_name}" role in guild "{guild.name}". Cannot assign role.')
            return
        
        # Assign the role to the new member
        await member.add_roles(member_role, reason='Auto-assigned member role on join')
        
        logger.info(f'Successfully assigned "{role_name}" role to {member.name}#{member.discriminator} in guild "{guild.name}"')
        
        # Optional: Send welcome message to member (if enabled in config)
        if BOT_CONFIG['SEND_WELCOME_MESSAGE']:
            try:
                welcome_message = BOT_CONFIG['WELCOME_MESSAGE'].format(
                    member=member.mention,
                    guild=guild.name,
                    role=role_name
                )
                await member.send(welcome_message)
                logger.info(f'Sent welcome message to {member.name}#{member.discriminator}')
            except discord.Forbidden:
                logger.warning(f'Could not send welcome message to {member.name}#{member.discriminator} - DMs disabled')
            except Exception as e:
                logger.error(f'Error sending welcome message to {member.name}#{member.discriminator}: {str(e)}')
        
    except discord.Forbidden:
        logger.error(f'Bot lacks permission to assign roles to {member.name}#{member.discriminator} in guild "{guild.name}"')
    except discord.HTTPException as e:
        logger.error(f'HTTP error occurred while assigning role to {member.name}#{member.discriminator}: {str(e)}')
    except Exception as e:
        logger.error(f'Unexpected error occurred while processing new member {member.name}#{member.discriminator}: {str(e)}')

@bot.event
async def on_guild_join(guild):
    """Event fired when bot joins a new guild."""
    logger.info(f'Bot joined new guild: {guild.name} (ID: {guild.id})')
    
    # Check if the member role exists
    role_name = BOT_CONFIG['MEMBER_ROLE_NAME']
    member_role = discord.utils.get(guild.roles, name=role_name)
    
    if member_role is None:
        logger.warning(f'Role "{role_name}" not found in new guild "{guild.name}". Please create this role.')
    else:
        logger.info(f'Role "{role_name}" found in guild "{guild.name}"')

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler for bot events."""
    logger.error(f'An error occurred in event {event}', exc_info=True)

@bot.command(name='check_permissions')
@commands.has_permissions(administrator=True)
async def check_permissions(ctx):
    """
    Admin command to check bot permissions and role setup.
    Usage: !check_permissions
    """
    guild = ctx.guild
    role_name = BOT_CONFIG['MEMBER_ROLE_NAME']
    
    embed = discord.Embed(title='Bot Permission Check', color=0x00ff00)
    
    # Check if member role exists
    member_role = discord.utils.get(guild.roles, name=role_name)
    if member_role:
        embed.add_field(name=f'Role "{role_name}"', value='✅ Exists', inline=True)
    else:
        embed.add_field(name=f'Role "{role_name}"', value='❌ Not Found', inline=True)
    
    # Check manage roles permission
    if guild.me.guild_permissions.manage_roles:
        embed.add_field(name='Manage Roles Permission', value='✅ Yes', inline=True)
    else:
        embed.add_field(name='Manage Roles Permission', value='❌ No', inline=True)
    
    # Check role hierarchy
    if member_role and guild.me.top_role > member_role:
        embed.add_field(name='Role Hierarchy', value='✅ Bot role is higher', inline=True)
    elif member_role:
        embed.add_field(name='Role Hierarchy', value='❌ Bot role is not higher', inline=True)
    else:
        embed.add_field(name='Role Hierarchy', value='❓ Cannot check (role missing)', inline=True)
    
    await ctx.send(embed=embed)

@check_permissions.error
async def check_permissions_error(ctx, error):
    """Error handler for check_permissions command."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('❌ You need Administrator permissions to use this command.')
    else:
        logger.error(f'Error in check_permissions command: {str(error)}')
        await ctx.send('❌ An error occurred while checking permissions.')

def main():
    """Main function to start the bot."""
    # Get bot token from environment variable
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        logger.error('DISCORD_BOT_TOKEN environment variable not found. Please set your bot token.')
        return
    
    logger.info('Starting Discord Member Bot...')
    
    try:
        # Start the bot
        bot.run(token)
    except discord.LoginFailure:
        logger.error('Invalid bot token provided. Please check your DISCORD_BOT_TOKEN environment variable.')
    except Exception as e:
        logger.error(f'Error starting bot: {str(e)}')

if __name__ == '__main__':
    main()

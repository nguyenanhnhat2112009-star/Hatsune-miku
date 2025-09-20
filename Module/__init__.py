# Bot modules package
"""
Discord bot modules/cogs package.

This package contains all the bot's functionality modules:
- music: Music player and related commands
- help: Help system and command documentation
- fishing: Fishing game module
- moderator: Moderation commands
- owner: Owner-only commands
- ping: Ping and latency commands
- language: Language switching commands
- invite: Invite management
- lyrics: Lyrics search functionality
- bank_cog: Banking/economy system
- emoji: Emoji management
- errorhandler: Global error handling
- member_invite: Member invitation tracking
- purge: Message purging commands
- sech: Search functionality
"""

# This file is not meant to be loaded as an extension
# Individual modules are loaded separately by the bot

def setup(bot):
    """This function is required for disnake extensions but not used here."""
    pass

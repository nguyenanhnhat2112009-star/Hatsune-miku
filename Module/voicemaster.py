import disnake
from disnake.ext import commands
import json
import os
import asyncio
from datetime import datetime
from typing import Dict, List, Optional


class VoiceMaster(commands.Cog):
    """Module VoiceMaster - Tạo voice channel tự động"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config_file = 'data/voicemaster_config.json'
        self.temp_channels: Dict[int, Dict] = {}  # Store temp channel info
    
    def load_config(self) -> Dict:
        """Load VoiceMaster configuration"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def save_config(self, data: Dict):
        """Save VoiceMaster configuration"""
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving voicemaster config: {e}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        """Handle voice state changes"""
        try:
            config = self.load_config()
            guild_config = config.get(str(member.guild.id), {})
            
            if not guild_config.get('enabled', False):
                return
            
            # User joined a voice channel
            if after.channel and after.channel.id == guild_config.get('join_to_create_id'):
                await self.create_temp_channel(member, after.channel)
            
            # User left a voice channel
            if before.channel and before.channel.id in self.temp_channels:
                await self.check_delete_temp_channel(before.channel)
                
        except Exception as e:
            print(f"Error in voice state update: {e}")
    
    async def create_temp_channel(self, member: disnake.Member, join_channel: disnake.VoiceChannel):
        """Create temporary voice channel for user"""
        try:
            guild = member.guild
            config = self.load_config()
            guild_config = config.get(str(guild.id), {})
            
            # Get category
            category_id = guild_config.get('category_id')
            category = guild.get_channel(category_id) if category_id else join_channel.category
            
            # Create channel name
            channel_name = guild_config.get('channel_name_format', "{user}'s Channel").format(
                user=member.display_name
            )
            
            # Set permissions
            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(view_channel=True),
                member: disnake.PermissionOverwrite(
                    view_channel=True,
                    connect=True,
                    speak=True,
                    manage_channels=True,
                    manage_permissions=True
                ),
                guild.me: disnake.PermissionOverwrite(
                    view_channel=True,
                    connect=True,
                    manage_channels=True,
                    manage_permissions=True
                )
            }
            
            # Create the channel
            temp_channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites,
                user_limit=guild_config.get('default_limit', 0) or None
            )
            
            # Move user to new channel
            await member.move_to(temp_channel)
            
            # Store temp channel info
            self.temp_channels[temp_channel.id] = {
                'owner_id': member.id,
                'guild_id': guild.id,
                'created_at': datetime.now().isoformat()
            }
                
        except Exception as e:
            print(f"Error creating temp channel: {e}")
    
    async def check_delete_temp_channel(self, channel: disnake.VoiceChannel):
        """Check if temp channel should be deleted"""
        try:
            # Wait a bit to ensure all users have left
            await asyncio.sleep(2)
            
            # Refresh channel to get current members
            channel = self.bot.get_channel(channel.id)
            if not channel:
                return
            
            # If channel is empty, delete it
            if len(channel.members) == 0:
                if channel.id in self.temp_channels:
                    del self.temp_channels[channel.id]
                await channel.delete(reason="Temporary voice channel - empty")
                
        except Exception as e:
            print(f"Error checking temp channel deletion: {e}")
    
    @commands.slash_command(name="voicemaster")
    async def voicemaster_command(self, interaction):
        """VoiceMaster system commands"""
        pass
    
    @voicemaster_command.sub_command(name="setup")
    async def setup_voicemaster(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        category: disnake.CategoryChannel = commands.Param(description="Category để tạo voice channels"),
        channel_name: str = commands.Param(description="Tên cho Join to Create channel", default="➕ Join to Create")
    ):
        """
        Thiết lập hệ thống VoiceMaster
        
        Parameters
        ----------
        category: Category để tạo các voice channel
        channel_name: Tên cho channel Join to Create
        """
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bạn cần quyền Administrator!", ephemeral=True)
            return
        
        try:
            guild = interaction.guild
            
            # Create Join to Create channel
            join_channel = await guild.create_voice_channel(
                name=channel_name,
                category=category,
                overwrites={
                    guild.default_role: disnake.PermissionOverwrite(connect=True, view_channel=True),
                    guild.me: disnake.PermissionOverwrite(connect=True, manage_channels=True)
                }
            )
            
            # Save config
            config = self.load_config()
            config[str(guild.id)] = {
                'enabled': True,
                'join_to_create_id': join_channel.id,
                'category_id': category.id,
                'channel_name_format': "{user}'s Channel",
                'default_limit': 0,
                'setup_by': interaction.user.id,
                'setup_time': datetime.now().isoformat()
            }
            self.save_config(config)
            
            embed = disnake.Embed(
                title="✅ VoiceMaster Setup Complete!",
                description="**Hệ thống VoiceMaster đã được thiết lập thành công!**",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="📍 Join to Create Channel",
                value=join_channel.mention,
                inline=True
            )
            
            embed.add_field(
                name="📁 Category",
                value=category.name,
                inline=True
            )
            
            embed.add_field(
                name="👤 Setup by",
                value=interaction.user.mention,
                inline=True
            )
            
            embed.add_field(
                name="🎉 How it works",
                value="• Join vào channel **Join to Create**\n"
                      "• Bot sẽ tự động tạo voice channel riêng\n"
                      "• Channel sẽ tự động xóa khi không còn ai",
                inline=False
            )
            
            embed.set_footer(text="VoiceMaster • Powered by Hatsune Miku Bot")
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi setup: {str(e)}", ephemeral=True)

    @voicemaster_command.sub_command(name="disable")
    async def disable_voicemaster(self, interaction: disnake.ApplicationCommandInteraction):
        """Tắt hệ thống VoiceMaster"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bạn cần quyền Administrator!", ephemeral=True)
            return

        try:
            config = self.load_config()
            guild_config = config.get(str(interaction.guild.id), {})

            if not guild_config.get('enabled', False):
                await interaction.response.send_message("❌ VoiceMaster chưa được thiết lập!", ephemeral=True)
                return

            
            config[str(interaction.guild.id)]['enabled'] = False
            self.save_config(config)

            embed = disnake.Embed(
                title="🔕 VoiceMaster Disabled",
                description="Hệ thống VoiceMaster đã được tắt. Sử dụng `/voicemaster setup` để bật lại.",
                color=0xff6b6b
            )

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)

    @voicemaster_command.sub_command(name="stats")
    async def voicemaster_stats(self, interaction: disnake.ApplicationCommandInteraction):
        """Xem thống kê VoiceMaster"""
        try:
            config = self.load_config()
            guild_config = config.get(str(interaction.guild.id), {})

            if not guild_config.get('enabled', False):
                await interaction.response.send_message("❌ VoiceMaster chưa được thiết lập!", ephemeral=True)
                return

            
            guild_temp_channels = [
                ch for ch_id, ch_info in self.temp_channels.items()
                if ch_info['guild_id'] == interaction.guild.id
            ]

            embed = disnake.Embed(
                title="📊 VoiceMaster Statistics",
                color=0x7289da,
                timestamp=datetime.now()
            )

            
            join_channel = interaction.guild.get_channel(guild_config.get('join_to_create_id'))

            embed.add_field(
                name="📍 Join to Create Channel",
                value=join_channel.mention if join_channel else "❌ Channel not found",
                inline=True
            )

            embed.add_field(
                name="🎙️ Active Temp Channels",
                value=str(len(guild_temp_channels)),
                inline=True
            )

            embed.add_field(
                name="⚙️ Status",
                value="✅ Enabled" if guild_config.get('enabled', False) else "❌ Disabled",
                inline=True
            )

            embed.set_footer(text=f"Server ID: {interaction.guild.id}")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)


def setup(bot):
    bot.add_cog(VoiceMaster(bot))

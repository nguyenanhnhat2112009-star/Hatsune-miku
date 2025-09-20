import disnake
from disnake.ext import commands
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import json
import os
import asyncio
from utils.ClientUser import ClientUser


class BoostView(disnake.ui.View):
    """View cho boost notification với buttons tương tác"""
    
    def __init__(self, bot: 'ClientUser', booster: disnake.Member):
        super().__init__(timeout=300)
        self.bot = bot
        self.booster = booster
    
    @disnake.ui.button(
        label="🎉 Cảm ơn",
        style=disnake.ButtonStyle.primary,
        emoji="🎉"
    )
    async def thank_booster(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        """Button cảm ơn booster"""
        embed = disnake.Embed(
            title="💖 Cảm ơn bạn!",
            description=f"**{interaction.author.mention}** đã gửi lời cảm ơn đến {self.booster.mention} vì đã boost server! 🚀",
            color=0xFF69B4
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @disnake.ui.button(
        label="📊 Thống kê Boost",
        style=disnake.ButtonStyle.secondary,
        emoji="📊"
    )
    async def boost_stats(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        """Hiển thị thống kê boost"""
        guild = interaction.guild
        
        embed = disnake.Embed(
            title="📊 Thống kê Server Boost",
            color=0x9B59B6,
            timestamp=datetime.now()
        )
        
        # Server boost info
        boost_count = guild.premium_subscription_count or 0
        boost_tier = guild.premium_tier
        
        # Tier benefits
        tier_benefits = {
            0: "• 50 emoji slots\n• 8MB upload limit",
            1: "• 100 emoji slots\n• 8MB upload limit\n• Better audio quality",
            2: "• 150 emoji slots\n• 50MB upload limit\n• 1080p screen share\n• Server banner",
            3: "• 250 emoji slots\n• 100MB upload limit\n• Animated server icon\n• Vanity URL"
        }
        
        embed.add_field(
            name="🚀 Boost hiện tại",
            value=f"**Số boost:** {boost_count}\n**Tier:** {boost_tier}/3",
            inline=True
        )
        
        embed.add_field(
            name="🎁 Lợi ích Tier hiện tại",
            value=tier_benefits.get(boost_tier, "Không có"),
            inline=True
        )
        
        # Next tier requirements
        next_tier_requirements = {0: 2, 1: 7, 2: 14, 3: None}
        next_requirement = next_tier_requirements.get(boost_tier)
        
        if next_requirement:
            remaining = next_requirement - boost_count
            embed.add_field(
                name="⬆️ Tier tiếp theo",
                value=f"Cần thêm **{remaining}** boost để đạt Tier {boost_tier + 1}",
                inline=False
            )
        else:
            embed.add_field(
                name="👑 Đã đạt Tier tối đa!",
                value="Server đã đạt Tier 3 - cao nhất!",
                inline=False
            )
        
        embed.set_footer(text=f"Thống kê của {guild.name}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @disnake.ui.button(
        label="🎁 Phần thưởng",
        style=disnake.ButtonStyle.success,
        emoji="🎁"
    )
    async def boost_rewards(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        """Hiển thị phần thưởng cho booster"""
        embed = disnake.Embed(
            title="🎁 Phần thưởng Booster",
            description="**Cảm ơn bạn đã boost server! Đây là những đặc quyền của bạn:**",
            color=0x00FF00
        )
        
        rewards = [
            "👑 **Role Booster** với màu đặc biệt",
            "🎨 **Quyền thay đổi nickname** của bản thân",
            "📱 **Ưu tiên kết nối** khi server đầy",
            "🔊 **Chất lượng âm thanh cao** trong voice chat",
            "📁 **Upload file lớn hơn** (tùy theo tier)",
            "🎭 **Sử dụng emoji** từ server khác",
            "💬 **Badge Booster** trên profile Discord",
            "🌟 **Được ghi nhận** trong danh sách boosters"
        ]
        
        embed.add_field(
            name="🎉 Đặc quyền của bạn",
            value="\n".join(rewards),
            inline=False
        )
        
        embed.add_field(
            name="💝 Cảm ơn đặc biệt",
            value=f"Server {interaction.guild.name} trân trọng sự đóng góp của bạn!",
            inline=False
        )
        
        embed.set_thumbnail(url=self.booster.display_avatar.url)
        await interaction.response.send_message(embed=embed, ephemeral=True)


class BoostTracker(commands.Cog):
    """Module theo dõi và thông báo Server Boost đẹp mắt"""
    
    def __init__(self, bot: ClientUser):
        self.bot = bot
        self.boost_data_file = 'data/boost_settings.json'
        self.boost_history_file = 'data/boost_history.json'
    
    async def load_boost_settings(self) -> Dict:
        """Load boost settings from file"""
        try:
            if os.path.exists(self.boost_data_file):
                with open(self.boost_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    async def save_boost_settings(self, data: Dict):
        """Save boost settings to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.boost_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving boost settings: {e}")
    
    async def load_boost_history(self) -> List:
        """Load boost history from file"""
        try:
            if os.path.exists(self.boost_history_file):
                with open(self.boost_history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except:
            return []
    
    async def save_boost_history(self, data: List):
        """Save boost history to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.boost_history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving boost history: {e}")
    
    @commands.Cog.listener()
    async def on_member_update(self, before: disnake.Member, after: disnake.Member):
        """Detect when someone boosts the server"""
        try:
            # Check if premium status changed
            before_boosting = before.premium_since is not None
            after_boosting = after.premium_since is not None

            # Someone started boosting
            if not before_boosting and after_boosting:
                await self.handle_new_boost(after)

            # Someone stopped boosting
            elif before_boosting and not after_boosting:
                await self.handle_boost_removed(after)

        except Exception as e:
            print(f"Error in on_member_update: {e}")
    
    async def handle_new_boost(self, member: disnake.Member):
        """Handle new boost notification"""
        try:
            settings = await self.load_boost_settings()
            guild_settings = settings.get(str(member.guild.id), {})

            # Check if boost notifications are enabled
            if not guild_settings.get('enabled', False):
                return

            # Get notification channel
            channel_id = guild_settings.get('channel_id')
            if not channel_id:
                return

            channel = self.bot.get_channel(channel_id)
            if not channel:
                return

            # Check if member actually has premium_since (for test command)
            if not member.premium_since:
                # For test purposes, use current time
                boost_time = datetime.now()
            else:
                boost_time = member.premium_since

            # Create beautiful boost notification
            embed = disnake.Embed(
                title="🚀 SOMEONE BOOSTED THE SERVER! 🚀",
                description=f"**{member.mention}** vừa boost server và mang lại những lợi ích tuyệt vời cho tất cả mọi người! 🎉",
                color=0xFF73FA,  # Discord Nitro pink
                timestamp=datetime.now()
            )

            # Add booster info
            embed.add_field(
                name="👤 Booster",
                value=f"**{member.display_name}**\n{member.mention}",
                inline=True
            )

            # Add boost time
            embed.add_field(
                name="⏰ Thời gian boost",
                value=f"<t:{int(boost_time.timestamp())}:F>",
                inline=True
            )
            
            # Add server boost stats
            guild = member.guild
            boost_count = guild.premium_subscription_count or 0
            boost_tier = guild.premium_tier
            
            embed.add_field(
                name="📊 Thống kê Server",
                value=f"🚀 **Tổng boost:** {boost_count}\n👑 **Tier:** {boost_tier}/3",
                inline=True
            )
            
            # Add tier progress
            next_tier_requirements = {0: 2, 1: 7, 2: 14, 3: None}
            next_requirement = next_tier_requirements.get(boost_tier)
            
            if next_requirement and boost_count < next_requirement:
                remaining = next_requirement - boost_count
                embed.add_field(
                    name="⬆️ Tiến độ Tier tiếp theo",
                    value=f"Cần thêm **{remaining}** boost để đạt Tier {boost_tier + 1}",
                    inline=False
                )
            elif boost_tier == 3:
                embed.add_field(
                    name="👑 Đã đạt Tier tối đa!",
                    value="Server đã đạt Tier 3 - cao nhất có thể!",
                    inline=False
                )
            
            # Add benefits
            tier_benefits = {
                1: "🎉 **Tier 1 Benefits:** Better audio quality, 100 emoji slots",
                2: "🎊 **Tier 2 Benefits:** 1080p screen share, 50MB uploads, server banner",
                3: "👑 **Tier 3 Benefits:** Animated icon, vanity URL, 100MB uploads"
            }
            
            if boost_tier > 0:
                embed.add_field(
                    name="🎁 Lợi ích hiện tại",
                    value=tier_benefits.get(boost_tier, ""),
                    inline=False
                )
            
            # Set booster avatar
            embed.set_thumbnail(url=member.display_avatar.url)
            
            # Add footer
            try:
                embed.set_footer(
                    text=f"Cảm ơn {member.display_name} đã boost {guild.name}! 💖",
                    icon_url=guild.icon.url if guild.icon else None
                )
            except:
                embed.set_footer(text=f"Cảm ơn {member.display_name} đã boost server! 💖")
            
            # Create view with buttons
            view = BoostView(self.bot, member)
            
            # Send notification
            message = await channel.send(
                content=f"🎉 **BOOST ALERT!** 🎉\n{member.mention} đã boost server! Hãy cảm ơn họ! 💖",
                embed=embed,
                view=view
            )
            
            # Save to boost history
            history = await self.load_boost_history()
            history.append({
                'user_id': member.id,
                'user_name': str(member),
                'guild_id': guild.id,
                'guild_name': guild.name,
                'boost_time': boost_time.isoformat(),
                'boost_count_after': boost_count,
                'tier_after': boost_tier,
                'message_id': message.id,
                'channel_id': channel.id
            })
            
            # Keep only last 100 boosts
            if len(history) > 100:
                history = history[-100:]
            
            await self.save_boost_history(history)
            
            # Add reaction to the message
            try:
                await message.add_reaction("🚀")
                await message.add_reaction("💖")
                await message.add_reaction("🎉")
            except:
                pass
                
        except Exception as e:
            print(f"Error handling new boost: {e}")
    
    async def handle_boost_removed(self, member: disnake.Member):
        """Handle boost removal notification"""
        try:
            settings = await self.load_boost_settings()
            guild_settings = settings.get(str(member.guild.id), {})
            
            # Check if boost notifications are enabled
            if not guild_settings.get('enabled', False):
                return
            
            # Check if removal notifications are enabled
            if not guild_settings.get('notify_removal', False):
                return
            
            # Get notification channel
            channel_id = guild_settings.get('channel_id')
            if not channel_id:
                return
            
            channel = self.bot.get_channel(channel_id)
            if not channel:
                return
            
            # Create boost removal notification
            embed = disnake.Embed(
                title="💔 Boost Removed",
                description=f"**{member.mention}** đã ngừng boost server.",
                color=0xFF6B6B,
                timestamp=datetime.now()
            )
            
            embed.add_field(
                name="👤 Member",
                value=f"{member.display_name}\n{member.mention}",
                inline=True
            )
            
            # Add current server stats
            guild = member.guild
            boost_count = guild.premium_subscription_count or 0
            boost_tier = guild.premium_tier
            
            embed.add_field(
                name="📊 Server Stats",
                value=f"🚀 **Boosts:** {boost_count}\n👑 **Tier:** {boost_tier}/3",
                inline=True
            )
            
            embed.set_footer(text=f"Cảm ơn {member.display_name} đã từng boost server! 💙")
            
            await channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error handling boost removal: {e}")

    @commands.slash_command(name="boost-setup", description="Thiết lập thông báo boost cho server")
    @commands.has_permissions(manage_guild=True)
    async def boost_setup(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        channel: disnake.TextChannel = commands.Param(description="Kênh để gửi thông báo boost"),
        enable_removal_notifications: bool = commands.Param(description="Thông báo khi ai đó ngừng boost", default=False)
    ):
        """Thiết lập hệ thống thông báo boost"""

        settings = await self.load_boost_settings()

        settings[str(interaction.guild.id)] = {
            'enabled': True,
            'channel_id': channel.id,
            'notify_removal': enable_removal_notifications,
            'setup_by': interaction.author.id,
            'setup_time': datetime.now().isoformat()
        }

        await self.save_boost_settings(settings)

        embed = disnake.Embed(
            title="✅ Boost Tracker đã được thiết lập!",
            description=f"**Hệ thống thông báo boost đã được kích hoạt thành công!**",
            color=0x00FF00,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="📍 Kênh thông báo",
            value=channel.mention,
            inline=True
        )

        embed.add_field(
            name="🔔 Thông báo ngừng boost",
            value="✅ Bật" if enable_removal_notifications else "❌ Tắt",
            inline=True
        )

        embed.add_field(
            name="👤 Thiết lập bởi",
            value=interaction.author.mention,
            inline=True
        )

        embed.add_field(
            name="🎉 Tính năng",
            value="• Thông báo tự động khi có boost mới\n"
                  "• Hiển thị thống kê server\n"
                  "• Buttons tương tác đẹp mắt\n"
                  "• Theo dõi tiến độ tier\n"
                  "• Lưu lịch sử boost",
            inline=False
        )

        embed.set_footer(text="Boost Tracker • Powered by Hatsune Miku Bot")
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif")

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="boost-disable", description="Tắt thông báo boost cho server")
    @commands.has_permissions(manage_guild=True)
    async def boost_disable(self, interaction: disnake.ApplicationCommandInteraction):
        """Tắt hệ thống thông báo boost"""

        settings = await self.load_boost_settings()

        if str(interaction.guild.id) not in settings:
            await interaction.response.send_message("❌ Boost tracker chưa được thiết lập cho server này!", ephemeral=True)
            return

        settings[str(interaction.guild.id)]['enabled'] = False
        await self.save_boost_settings(settings)

        embed = disnake.Embed(
            title="🔕 Boost Tracker đã được tắt",
            description="Hệ thống thông báo boost đã được tắt. Sử dụng `/boost-setup` để bật lại.",
            color=0xFF6B6B
        )

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="boost-stats", description="Xem thống kê boost của server")
    async def boost_stats(self, interaction: disnake.ApplicationCommandInteraction):
        """Hiển thị thống kê boost chi tiết"""

        guild = interaction.guild

        embed = disnake.Embed(
            title=f"📊 Thống kê Boost - {guild.name}",
            color=0xFF73FA,
            timestamp=datetime.now()
        )

        # Current boost info
        boost_count = guild.premium_subscription_count or 0
        boost_tier = guild.premium_tier
        boosters = [member for member in guild.members if member.premium_since]

        embed.add_field(
            name="🚀 Boost hiện tại",
            value=f"**Số boost:** {boost_count}\n**Tier:** {boost_tier}/3\n**Boosters:** {len(boosters)}",
            inline=True
        )

        # Tier benefits
        tier_benefits = {
            0: "• 50 emoji slots\n• 8MB upload limit",
            1: "• 100 emoji slots\n• Better audio quality\n• 8MB upload limit",
            2: "• 150 emoji slots\n• 50MB upload limit\n• 1080p screen share\n• Server banner",
            3: "• 250 emoji slots\n• 100MB upload limit\n• Animated server icon\n• Vanity URL"
        }

        embed.add_field(
            name="🎁 Lợi ích hiện tại",
            value=tier_benefits.get(boost_tier, "Không có"),
            inline=True
        )

        # Next tier requirements
        next_tier_requirements = {0: 2, 1: 7, 2: 14, 3: None}
        next_requirement = next_tier_requirements.get(boost_tier)

        if next_requirement:
            remaining = max(0, next_requirement - boost_count)
            progress = min(100, (boost_count / next_requirement) * 100)
            progress_bar = "█" * int(progress / 10) + "░" * (10 - int(progress / 10))

            embed.add_field(
                name=f"⬆️ Tiến độ Tier {boost_tier + 1}",
                value=f"`{progress_bar}` {progress:.1f}%\nCần thêm **{remaining}** boost",
                inline=False
            )
        else:
            embed.add_field(
                name="👑 Đã đạt Tier tối đa!",
                value="Server đã đạt Tier 3 - cao nhất có thể!",
                inline=False
            )

        # Recent boosters (last 5)
        if boosters:
            try:
                recent_boosters = sorted(
                    [b for b in boosters if b.premium_since],
                    key=lambda m: m.premium_since,
                    reverse=True
                )[:5]
                booster_list = []
                for booster in recent_boosters:
                    boost_time = f"<t:{int(booster.premium_since.timestamp())}:R>"
                    booster_list.append(f"• {booster.mention} - {boost_time}")

                if booster_list:
                    embed.add_field(
                        name="🌟 Boosters gần đây",
                        value="\n".join(booster_list),
                        inline=False
                    )
            except Exception as e:
                print(f"Error processing recent boosters: {e}")

        embed.set_footer(text=f"Server ID: {guild.id}")
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed)

    @commands.slash_command(name="boost-history", description="Xem lịch sử boost của server")
    @commands.has_permissions(manage_guild=True)
    async def boost_history(self, interaction: disnake.ApplicationCommandInteraction):
        """Hiển thị lịch sử boost"""

        history = await self.load_boost_history()
        guild_history = [entry for entry in history if entry['guild_id'] == interaction.guild.id]

        if not guild_history:
            embed = disnake.Embed(
                title="📋 Lịch sử Boost",
                description="Chưa có lịch sử boost nào được ghi nhận cho server này.",
                color=0x7289DA
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = disnake.Embed(
            title=f"📋 Lịch sử Boost - {interaction.guild.name}",
            description=f"Hiển thị {len(guild_history)} boost gần đây:",
            color=0xFF73FA,
            timestamp=datetime.now()
        )

        # Show last 10 boosts
        recent_history = guild_history[-10:]

        for i, entry in enumerate(reversed(recent_history), 1):
            try:
                boost_time = datetime.fromisoformat(entry['boost_time'])
                time_str = f"<t:{int(boost_time.timestamp())}:F>"

                embed.add_field(
                    name=f"🚀 Boost #{len(guild_history) - i + 1}",
                    value=f"**User:** {entry.get('user_name', 'Unknown')}\n"
                          f"**Time:** {time_str}\n"
                          f"**Tier after:** {entry.get('tier_after', 0)}/3",
                    inline=True
                )
            except Exception as e:
                print(f"Error processing boost history entry: {e}")
                continue

        embed.set_footer(text=f"Tổng cộng {len(guild_history)} boost • Hiển thị 10 gần nhất")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="boost-test", description="Test thông báo boost (chỉ admin)")
    @commands.has_permissions(administrator=True)
    async def boost_test(self, interaction: disnake.ApplicationCommandInteraction):
        """Test boost notification"""
        try:
            settings = await self.load_boost_settings()
            guild_settings = settings.get(str(interaction.guild.id), {})

            if not guild_settings.get('enabled', False):
                await interaction.response.send_message("❌ Boost tracker chưa được thiết lập! Sử dụng `/boost-setup` trước.", ephemeral=True)
                return

            # Simulate boost notification
            await self.handle_new_boost(interaction.author)

            embed = disnake.Embed(
                title="✅ Test thành công!",
                description="Thông báo boost test đã được gửi đến kênh đã thiết lập.",
                color=0x00FF00
            )

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            embed = disnake.Embed(
                title="❌ Lỗi test boost",
                description=f"Có lỗi xảy ra: {str(e)}",
                color=0xFF6B6B
            )
            try:
                await interaction.response.send_message(embed=embed, ephemeral=True)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)


def setup(bot: ClientUser):
    bot.add_cog(BoostTracker(bot))

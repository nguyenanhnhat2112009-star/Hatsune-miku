import disnake
from disnake.ext import commands, tasks
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import random
import asyncio
import json
import os
from utils.ClientUser import ClientUser


class GiveawayView(disnake.ui.View):
    """View cho giveaway với button tham gia"""
    
    def __init__(self, giveaway_id: str, bot: 'ClientUser'):
        super().__init__(timeout=None)
        self.giveaway_id = giveaway_id
        self.bot = bot
        
    @disnake.ui.button(
        label="🎉 Tham gia Giveaway",
        style=disnake.ButtonStyle.primary,
        emoji="🎉",
        custom_id="giveaway_join"
    )
    async def join_giveaway(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        """Button tham gia giveaway"""
        try:
            # Load giveaway data
            giveaway_data = await self.load_giveaway_data()
            
            if self.giveaway_id not in giveaway_data:
                await interaction.response.send_message("❌ Giveaway này không tồn tại!", ephemeral=True)
                return
                
            giveaway = giveaway_data[self.giveaway_id]
            
            # Check if giveaway is still active
            end_time = datetime.fromisoformat(giveaway['end_time'])
            if datetime.now() >= end_time:
                await interaction.response.send_message("❌ Giveaway này đã kết thúc!", ephemeral=True)
                return
            
            # Check if user already joined
            if interaction.author.id in giveaway['participants']:
                await interaction.response.send_message("❌ Bạn đã tham gia giveaway này rồi!", ephemeral=True)
                return
            
            # Add user to participants
            giveaway['participants'].append(interaction.author.id)
            await self.save_giveaway_data(giveaway_data)
            
            # Success response
            embed = disnake.Embed(
                title="🎉 Tham gia thành công!",
                description=f"**Bạn đã tham gia giveaway:**\n🎁 **{giveaway['prize']}**\n\n"
                           f"👥 **Số người tham gia:** {len(giveaway['participants'])}\n"
                           f"⏰ **Kết thúc:** <t:{int(end_time.timestamp())}:R>",
                color=0x00FF00
            )
            embed.set_footer(text="Chúc bạn may mắn! 🍀")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(f"❌ Có lỗi xảy ra: {str(e)}", ephemeral=True)
    
    async def load_giveaway_data(self) -> Dict:
        """Load giveaway data from file"""
        try:
            if os.path.exists('data/giveaways.json'):
                with open('data/giveaways.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    async def save_giveaway_data(self, data: Dict):
        """Save giveaway data to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open('data/giveaways.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving giveaway data: {e}")


class Giveaway(commands.Cog):
    """Hệ thống Giveaway đẹp và đầy đủ tính năng"""
    
    def __init__(self, bot: ClientUser):
        self.bot = bot
        self.giveaway_data_file = 'data/giveaways.json'
        self.check_giveaways.start()
    
    def cog_unload(self):
        self.check_giveaways.cancel()
    
    async def load_giveaway_data(self) -> Dict:
        """Load giveaway data from file"""
        try:
            if os.path.exists(self.giveaway_data_file):
                with open(self.giveaway_data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except:
            return {}
    
    async def save_giveaway_data(self, data: Dict):
        """Save giveaway data to file"""
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.giveaway_data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving giveaway data: {e}")
    
    @tasks.loop(seconds=30)
    async def check_giveaways(self):
        """Check for ended giveaways every 30 seconds"""
        try:
            giveaway_data = await self.load_giveaway_data()
            current_time = datetime.now()
            
            for giveaway_id, giveaway in list(giveaway_data.items()):
                end_time = datetime.fromisoformat(giveaway['end_time'])
                
                if current_time >= end_time and not giveaway.get('ended', False):
                    await self.end_giveaway(giveaway_id, giveaway)
                    giveaway['ended'] = True
                    await self.save_giveaway_data(giveaway_data)
                    
        except Exception as e:
            print(f"Error checking giveaways: {e}")
    
    @check_giveaways.before_loop
    async def before_check_giveaways(self):
        await self.bot.wait_until_ready()
    
    async def end_giveaway(self, giveaway_id: str, giveaway: Dict):
        """End a giveaway and announce winners"""
        try:
            channel = self.bot.get_channel(giveaway['channel_id'])
            if not channel:
                return
            
            participants = giveaway['participants']
            winners_count = giveaway['winners']
            
            if len(participants) == 0:
                # No participants
                embed = disnake.Embed(
                    title="🎉 Giveaway Kết Thúc",
                    description=f"**🎁 Giải thưởng:** {giveaway['prize']}\n\n"
                               f"😢 **Không có ai tham gia giveaway này!**",
                    color=0xFF6B6B
                )
                embed.set_footer(text="Giveaway đã kết thúc • Không có người thắng")
                
            elif len(participants) < winners_count:
                # Not enough participants
                winners = participants
                winner_mentions = []
                for winner_id in winners:
                    user = self.bot.get_user(winner_id)
                    if user:
                        winner_mentions.append(user.mention)
                
                embed = disnake.Embed(
                    title="🎉 Giveaway Kết Thúc",
                    description=f"**🎁 Giải thưởng:** {giveaway['prize']}\n\n"
                               f"🏆 **Người thắng:** {', '.join(winner_mentions)}\n"
                               f"👥 **Tổng người tham gia:** {len(participants)}",
                    color=0x00FF00
                )
                embed.set_footer(text="Giveaway đã kết thúc • Chúc mừng người thắng! 🎊")
                
            else:
                # Normal case - select random winners
                winners = random.sample(participants, winners_count)
                winner_mentions = []
                for winner_id in winners:
                    user = self.bot.get_user(winner_id)
                    if user:
                        winner_mentions.append(user.mention)
                
                embed = disnake.Embed(
                    title="🎉 Giveaway Kết Thúc",
                    description=f"**🎁 Giải thưởng:** {giveaway['prize']}\n\n"
                               f"🏆 **Người thắng:** {', '.join(winner_mentions)}\n"
                               f"👥 **Tổng người tham gia:** {len(participants)}",
                    color=0x00FF00
                )
                embed.set_footer(text="Giveaway đã kết thúc • Chúc mừng người thắng! 🎊")
            
            # Add host info
            host = self.bot.get_user(giveaway['host_id'])
            if host:
                embed.add_field(
                    name="👤 Người tổ chức",
                    value=host.mention,
                    inline=True
                )
            
            embed.add_field(
                name="⏰ Thời gian kết thúc",
                value=f"<t:{int(datetime.fromisoformat(giveaway['end_time']).timestamp())}:F>",
                inline=True
            )
            
            # Send result message
            try:
                original_message = await channel.fetch_message(giveaway['message_id'])
                await original_message.edit(embed=embed, view=None)
            except:
                await channel.send(embed=embed)
            
            # Send congratulations message if there are winners
            if len(participants) > 0 and (len(participants) >= winners_count or len(participants) < winners_count):
                congrats_embed = disnake.Embed(
                    title="🎊 Chúc mừng!",
                    description=f"Chúc mừng {', '.join(winner_mentions)} đã thắng **{giveaway['prize']}**!\n\n"
                               f"Hãy liên hệ với {host.mention if host else 'người tổ chức'} để nhận giải thưởng!",
                    color=0xFFD700
                )
                congrats_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif")
                await channel.send(embed=congrats_embed)
                
        except Exception as e:
            print(f"Error ending giveaway: {e}")
    
    @commands.slash_command(name="giveaway", description="Tạo giveaway mới")
    @commands.has_permissions(manage_guild=True)
    async def create_giveaway(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        prize: str = commands.Param(description="Giải thưởng của giveaway"),
        duration: str = commands.Param(description="Thời gian (ví dụ: 1h, 30m, 1d)"),
        winners: int = commands.Param(description="Số người thắng", default=1, ge=1, le=10),
        channel: Optional[disnake.TextChannel] = commands.Param(description="Kênh để tổ chức (mặc định: kênh hiện tại)", default=None)
    ):
        """Tạo giveaway mới với giao diện đẹp"""
        
        # Parse duration
        try:
            duration_seconds = self.parse_duration(duration)
            if duration_seconds < 60:  # Minimum 1 minute
                await interaction.response.send_message("❌ Thời gian tối thiểu là 1 phút!", ephemeral=True)
                return
            if duration_seconds > 7 * 24 * 3600:  # Maximum 7 days
                await interaction.response.send_message("❌ Thời gian tối đa là 7 ngày!", ephemeral=True)
                return
        except ValueError:
            await interaction.response.send_message(
                "❌ Định dạng thời gian không hợp lệ!\n"
                "**Ví dụ:** `1h` (1 giờ), `30m` (30 phút), `1d` (1 ngày), `2h30m` (2 giờ 30 phút)",
                ephemeral=True
            )
            return
        
        target_channel = channel or interaction.channel
        end_time = datetime.now() + timedelta(seconds=duration_seconds)
        
        # Generate unique giveaway ID
        giveaway_id = f"{interaction.guild.id}_{int(datetime.now().timestamp())}"
        
        # Create beautiful giveaway embed
        embed = disnake.Embed(
            title="🎉 GIVEAWAY 🎉",
            description=f"**🎁 Giải thưởng:** {prize}\n\n"
                       f"🏆 **Số người thắng:** {winners}\n"
                       f"⏰ **Kết thúc:** <t:{int(end_time.timestamp())}:R>\n"
                       f"👤 **Người tổ chức:** {interaction.author.mention}\n\n"
                       f"**Nhấn nút 🎉 bên dưới để tham gia!**",
            color=0xFF69B4
        )
        
        embed.add_field(
            name="📊 Thống kê",
            value="👥 **Người tham gia:** 0\n⏱️ **Trạng thái:** Đang diễn ra",
            inline=True
        )
        
        embed.add_field(
            name="📋 Thông tin",
            value=f"🆔 **ID:** `{giveaway_id}`\n📅 **Tạo lúc:** <t:{int(datetime.now().timestamp())}:F>",
            inline=True
        )
        
        embed.set_footer(
            text="Giveaway • Nhấn button để tham gia!",
            icon_url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif"
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif")
        
        # Create view with join button
        view = GiveawayView(giveaway_id, self.bot)
        
        # Send giveaway message
        await interaction.response.send_message("✅ Đang tạo giveaway...", ephemeral=True)
        giveaway_message = await target_channel.send(embed=embed, view=view)
        
        # Save giveaway data
        giveaway_data = await self.load_giveaway_data()
        giveaway_data[giveaway_id] = {
            'prize': prize,
            'duration': duration_seconds,
            'winners': winners,
            'host_id': interaction.author.id,
            'channel_id': target_channel.id,
            'message_id': giveaway_message.id,
            'guild_id': interaction.guild.id,
            'participants': [],
            'start_time': datetime.now().isoformat(),
            'end_time': end_time.isoformat(),
            'ended': False
        }
        await self.save_giveaway_data(giveaway_data)
        
        # Success message
        success_embed = disnake.Embed(
            title="✅ Giveaway đã được tạo!",
            description=f"**🎁 Giải thưởng:** {prize}\n"
                       f"📍 **Kênh:** {target_channel.mention}\n"
                       f"⏰ **Kết thúc:** <t:{int(end_time.timestamp())}:R>\n"
                       f"🆔 **ID:** `{giveaway_id}`",
            color=0x00FF00
        )
        await interaction.edit_original_response(content=None, embed=success_embed)
    
    def parse_duration(self, duration_str: str) -> int:
        """Parse duration string to seconds"""
        duration_str = duration_str.lower().replace(' ', '')
        total_seconds = 0
        
        # Parse different time units
        import re
        
        # Find all time components
        time_pattern = r'(\d+)([smhd])'
        matches = re.findall(time_pattern, duration_str)
        
        if not matches:
            raise ValueError("Invalid duration format")
        
        for amount, unit in matches:
            amount = int(amount)
            if unit == 's':
                total_seconds += amount
            elif unit == 'm':
                total_seconds += amount * 60
            elif unit == 'h':
                total_seconds += amount * 3600
            elif unit == 'd':
                total_seconds += amount * 86400
        
        return total_seconds

    @commands.slash_command(name="giveaway-list", description="Xem danh sách giveaway đang diễn ra")
    async def list_giveaways(self, interaction: disnake.ApplicationCommandInteraction):
        """Hiển thị danh sách giveaway đang diễn ra"""

        giveaway_data = await self.load_giveaway_data()
        active_giveaways = []

        for giveaway_id, giveaway in giveaway_data.items():
            if giveaway['guild_id'] == interaction.guild.id and not giveaway.get('ended', False):
                end_time = datetime.fromisoformat(giveaway['end_time'])
                if datetime.now() < end_time:
                    active_giveaways.append((giveaway_id, giveaway))

        if not active_giveaways:
            embed = disnake.Embed(
                title="📋 Danh sách Giveaway",
                description="🔍 **Không có giveaway nào đang diễn ra trong server này!**\n\n"
                           "💡 Sử dụng `/giveaway` để tạo giveaway mới!",
                color=0x7289DA
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = disnake.Embed(
            title="📋 Danh sách Giveaway đang diễn ra",
            description=f"🎉 **Tìm thấy {len(active_giveaways)} giveaway đang diễn ra:**",
            color=0x00FF88
        )

        for i, (giveaway_id, giveaway) in enumerate(active_giveaways[:10], 1):  # Limit to 10
            end_time = datetime.fromisoformat(giveaway['end_time'])
            host = self.bot.get_user(giveaway['host_id'])

            embed.add_field(
                name=f"🎁 {i}. {giveaway['prize'][:50]}{'...' if len(giveaway['prize']) > 50 else ''}",
                value=f"👥 **Tham gia:** {len(giveaway['participants'])}\n"
                      f"🏆 **Số người thắng:** {giveaway['winners']}\n"
                      f"⏰ **Kết thúc:** <t:{int(end_time.timestamp())}:R>\n"
                      f"👤 **Host:** {host.mention if host else 'Unknown'}\n"
                      f"🆔 **ID:** `{giveaway_id}`",
                inline=True
            )

        embed.set_footer(text=f"Trang 1 • Tổng cộng {len(active_giveaways)} giveaway")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="giveaway-end", description="Kết thúc giveaway sớm")
    @commands.has_permissions(manage_guild=True)
    async def end_giveaway_early(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        giveaway_id: str = commands.Param(description="ID của giveaway cần kết thúc")
    ):
        """Kết thúc giveaway sớm"""

        giveaway_data = await self.load_giveaway_data()

        if giveaway_id not in giveaway_data:
            await interaction.response.send_message("❌ Không tìm thấy giveaway với ID này!", ephemeral=True)
            return

        giveaway = giveaway_data[giveaway_id]

        if giveaway['guild_id'] != interaction.guild.id:
            await interaction.response.send_message("❌ Giveaway này không thuộc server này!", ephemeral=True)
            return

        if giveaway.get('ended', False):
            await interaction.response.send_message("❌ Giveaway này đã kết thúc rồi!", ephemeral=True)
            return

        # Check permissions (host or manage_guild)
        if giveaway['host_id'] != interaction.author.id and not interaction.author.guild_permissions.manage_guild:
            await interaction.response.send_message("❌ Bạn không có quyền kết thúc giveaway này!", ephemeral=True)
            return

        # End the giveaway
        await interaction.response.send_message("⏳ Đang kết thúc giveaway...", ephemeral=True)

        await self.end_giveaway(giveaway_id, giveaway)
        giveaway['ended'] = True
        await self.save_giveaway_data(giveaway_data)

        embed = disnake.Embed(
            title="✅ Giveaway đã kết thúc!",
            description=f"**🎁 Giải thưởng:** {giveaway['prize']}\n"
                       f"🆔 **ID:** `{giveaway_id}`\n"
                       f"👤 **Kết thúc bởi:** {interaction.author.mention}",
            color=0x00FF00
        )
        await interaction.edit_original_response(embed=embed)

    @commands.slash_command(name="giveaway-reroll", description="Quay lại người thắng cho giveaway")
    @commands.has_permissions(manage_guild=True)
    async def reroll_giveaway(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        giveaway_id: str = commands.Param(description="ID của giveaway cần quay lại"),
        new_winners: Optional[int] = commands.Param(description="Số người thắng mới (mặc định: giữ nguyên)", default=None)
    ):
        """Quay lại người thắng cho giveaway đã kết thúc"""

        giveaway_data = await self.load_giveaway_data()

        if giveaway_id not in giveaway_data:
            await interaction.response.send_message("❌ Không tìm thấy giveaway với ID này!", ephemeral=True)
            return

        giveaway = giveaway_data[giveaway_id]

        if giveaway['guild_id'] != interaction.guild.id:
            await interaction.response.send_message("❌ Giveaway này không thuộc server này!", ephemeral=True)
            return

        if not giveaway.get('ended', False):
            await interaction.response.send_message("❌ Giveaway này chưa kết thúc!", ephemeral=True)
            return

        participants = giveaway['participants']
        if len(participants) == 0:
            await interaction.response.send_message("❌ Không có ai tham gia giveaway này!", ephemeral=True)
            return

        # Use new winners count or keep original
        winners_count = new_winners if new_winners is not None else giveaway['winners']
        winners_count = min(winners_count, len(participants))  # Can't have more winners than participants

        # Select new winners
        winners = random.sample(participants, winners_count)
        winner_mentions = []
        for winner_id in winners:
            user = self.bot.get_user(winner_id)
            if user:
                winner_mentions.append(user.mention)

        # Create reroll embed
        embed = disnake.Embed(
            title="🔄 Giveaway Reroll",
            description=f"**🎁 Giải thưởng:** {giveaway['prize']}\n\n"
                       f"🏆 **Người thắng mới:** {', '.join(winner_mentions)}\n"
                       f"👥 **Tổng người tham gia:** {len(participants)}\n"
                       f"🔄 **Reroll bởi:** {interaction.author.mention}",
            color=0xFFD700
        )

        host = self.bot.get_user(giveaway['host_id'])
        if host:
            embed.add_field(name="👤 Người tổ chức gốc", value=host.mention, inline=True)

        embed.add_field(name="🆔 Giveaway ID", value=f"`{giveaway_id}`", inline=True)
        embed.set_footer(text="Giveaway Reroll • Chúc mừng người thắng mới! 🎊")

        await interaction.response.send_message(embed=embed)

        # Send congratulations message
        channel = self.bot.get_channel(giveaway['channel_id'])
        if channel:
            congrats_embed = disnake.Embed(
                title="🎊 Chúc mừng người thắng mới!",
                description=f"Chúc mừng {', '.join(winner_mentions)} đã thắng **{giveaway['prize']}** (Reroll)!\n\n"
                           f"Hãy liên hệ với {host.mention if host else 'người tổ chức'} để nhận giải thưởng!",
                color=0xFFD700
            )
            congrats_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif")
            await channel.send(embed=congrats_embed)

    @commands.slash_command(name="giveaway-info", description="Xem thông tin chi tiết giveaway")
    async def giveaway_info(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        giveaway_id: str = commands.Param(description="ID của giveaway")
    ):
        """Xem thông tin chi tiết về giveaway"""

        giveaway_data = await self.load_giveaway_data()

        if giveaway_id not in giveaway_data:
            await interaction.response.send_message("❌ Không tìm thấy giveaway với ID này!", ephemeral=True)
            return

        giveaway = giveaway_data[giveaway_id]

        if giveaway['guild_id'] != interaction.guild.id:
            await interaction.response.send_message("❌ Giveaway này không thuộc server này!", ephemeral=True)
            return

        # Get times
        start_time = datetime.fromisoformat(giveaway['start_time'])
        end_time = datetime.fromisoformat(giveaway['end_time'])
        is_ended = giveaway.get('ended', False) or datetime.now() >= end_time

        # Get host
        host = self.bot.get_user(giveaway['host_id'])

        # Create info embed
        embed = disnake.Embed(
            title="📊 Thông tin Giveaway",
            description=f"**🎁 Giải thưởng:** {giveaway['prize']}",
            color=0x00FF00 if not is_ended else 0xFF6B6B
        )

        embed.add_field(
            name="📈 Thống kê",
            value=f"👥 **Người tham gia:** {len(giveaway['participants'])}\n"
                  f"🏆 **Số người thắng:** {giveaway['winners']}\n"
                  f"⏱️ **Trạng thái:** {'Đã kết thúc' if is_ended else 'Đang diễn ra'}",
            inline=True
        )

        embed.add_field(
            name="⏰ Thời gian",
            value=f"📅 **Bắt đầu:** <t:{int(start_time.timestamp())}:F>\n"
                  f"🏁 **Kết thúc:** <t:{int(end_time.timestamp())}:F>\n"
                  f"⏳ **Thời lượng:** {giveaway['duration']} giây",
            inline=True
        )

        embed.add_field(
            name="👤 Thông tin khác",
            value=f"🎪 **Người tổ chức:** {host.mention if host else 'Unknown'}\n"
                  f"📍 **Kênh:** <#{giveaway['channel_id']}>\n"
                  f"🆔 **ID:** `{giveaway_id}`",
            inline=False
        )

        # Show some participants (max 10)
        if giveaway['participants']:
            participant_mentions = []
            for participant_id in giveaway['participants'][:10]:
                user = self.bot.get_user(participant_id)
                if user:
                    participant_mentions.append(user.mention)

            participants_text = ', '.join(participant_mentions)
            if len(giveaway['participants']) > 10:
                participants_text += f" và {len(giveaway['participants']) - 10} người khác..."

            embed.add_field(
                name="👥 Người tham gia",
                value=participants_text,
                inline=False
            )

        embed.set_footer(text=f"Giveaway {'đã kết thúc' if is_ended else 'đang diễn ra'}")
        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: ClientUser):
    bot.add_cog(Giveaway(bot))

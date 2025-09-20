import disnake
from disnake.ext import commands
from datetime import datetime, timedelta
import re
from typing import Optional, Union

from utils.ClientUser import ClientUser


def parse_duration(duration_str: str) -> Optional[int]:
    """
    Parse duration string into seconds.
    Supports formats like: 1d2h3m4s, 30m, 1h, etc.
    Returns None if invalid format.
    """
    if not duration_str:
        return None

    # Remove spaces and convert to lowercase
    duration_str = duration_str.lower().strip()

    # Pattern to match time units
    pattern = r'(\d+)([dhms])'
    matches = re.findall(pattern, duration_str)

    if not matches:
        # Try to parse as pure number (assume seconds)
        try:
            return int(duration_str)
        except ValueError:
            return None

    total_seconds = 0
    time_units = {'d': 86400, 'h': 3600, 'm': 60, 's': 1}

    for amount, unit in matches:
        try:
            total_seconds += int(amount) * time_units.get(unit, 0)
        except ValueError:
            return None

    # Discord timeout limit is 28 days
    max_timeout = 28 * 24 * 60 * 60  # 28 days in seconds
    return min(total_seconds, max_timeout) if total_seconds > 0 else None


def format_duration(seconds: int) -> str:
    """Format seconds into human readable duration."""
    if seconds <= 0:
        return "0 giây"

    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if days > 0:
        parts.append(f"{days} ngày")
    if hours > 0:
        parts.append(f"{hours} giờ")
    if minutes > 0:
        parts.append(f"{minutes} phút")
    if secs > 0:
        parts.append(f"{secs} giây")

    return ", ".join(parts)

class Moderator(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot: ClientUser = bot

    async def _check_hierarchy(self, interaction: disnake.CommandInteraction, target: disnake.Member) -> bool:
        """Check if the bot and user have permission to moderate the target member."""
        # Check if target is bot owner or has higher role than bot
        if target.id == interaction.guild.owner_id:
            await interaction.response.send_message("❌ Không thể thực hiện hành động với chủ sở hữu server!", ephemeral=True)
            return False

        if target.top_role >= interaction.guild.me.top_role:
            await interaction.response.send_message("❌ Tôi không thể thực hiện hành động với thành viên có vai trò cao hơn hoặc bằng tôi!", ephemeral=True)
            return False

        if target.top_role >= interaction.author.top_role and interaction.author.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Bạn không thể thực hiện hành động với thành viên có vai trò cao hơn hoặc bằng bạn!", ephemeral=True)
            return False

        if target.id == interaction.author.id:
            await interaction.response.send_message("❌ Bạn không thể thực hiện hành động với chính mình!", ephemeral=True)
            return False

        return True

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(moderate_members=True)
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.slash_command(name="mute", description="Timeout một thành viên trong server")
    async def mute(self,
                   interaction: disnake.CommandInteraction,
                   member: disnake.Member = commands.Param(description="Thành viên cần timeout"),
                   duration: str = commands.Param(description="Thời gian timeout (vd: 1d2h3m, 30m, 1h)"),
                   reason: Optional[str] = commands.Param(default=None, description="Lý do timeout")):

        # Check hierarchy first
        if not await self._check_hierarchy(interaction, member):
            return

        # Parse duration
        duration_seconds = parse_duration(duration)
        if duration_seconds is None or duration_seconds <= 0:
            await interaction.response.send_message(
                "❌ Thời gian timeout không hợp lệ!\n"
                "**Định dạng hợp lệ:** `1d2h3m4s`, `30m`, `1h`, `120` (giây)\n"
                "**Ví dụ:** `1d` (1 ngày), `2h30m` (2 giờ 30 phút)",
                ephemeral=True
            )
            return

        try:
            # Calculate timeout until time
            timeout_until = datetime.now() + timedelta(seconds=duration_seconds)

            await member.timeout(until=timeout_until, reason=reason)

            # Create success embed
            embed = disnake.Embed(
                title="✅ Timeout thành công",
                color=0xff9500,
                timestamp=datetime.now()
            )
            embed.add_field(name="Thành viên", value=member.mention, inline=True)
            embed.add_field(name="Thời gian", value=format_duration(duration_seconds), inline=True)
            embed.add_field(name="Lý do", value=reason or "Không có lý do", inline=True)
            embed.add_field(name="Người thực hiện", value=interaction.author.mention, inline=True)
            embed.add_field(name="Kết thúc lúc", value=f"<t:{int(timeout_until.timestamp())}:F>", inline=False)
            embed.set_footer(text=f"ID: {member.id}")

            await interaction.response.send_message(embed=embed)

        except disnake.Forbidden:
            await interaction.response.send_message("❌ Tôi không có quyền timeout thành viên này!", ephemeral=True)
        except disnake.HTTPException as e:
            await interaction.response.send_message(f"❌ Lỗi HTTP khi timeout: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi không xác định: {str(e)}", ephemeral=True)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(moderate_members=True)
    @commands.bot_has_guild_permissions(moderate_members=True)
    @commands.slash_command(name="unmute", description="Bỏ timeout cho một thành viên")
    async def unmute(self,
                     interaction: disnake.CommandInteraction,
                     member: disnake.Member = commands.Param(description="Thành viên cần bỏ timeout"),
                     reason: Optional[str] = commands.Param(default=None, description="Lý do bỏ timeout")):

        if not member.is_timed_out():
            await interaction.response.send_message("❌ Thành viên này không bị timeout!", ephemeral=True)
            return

        try:
            await member.timeout(until=None, reason=reason)

            embed = disnake.Embed(
                title="✅ Đã bỏ timeout",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Thành viên", value=member.mention, inline=True)
            embed.add_field(name="Lý do", value=reason or "Không có lý do", inline=True)
            embed.add_field(name="Người thực hiện", value=interaction.author.mention, inline=True)
            embed.set_footer(text=f"ID: {member.id}")

            await interaction.response.send_message(embed=embed)

        except disnake.Forbidden:
            await interaction.response.send_message("❌ Tôi không có quyền bỏ timeout cho thành viên này!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi không xác định: {str(e)}", ephemeral=True)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(kick_members=True)
    @commands.bot_has_guild_permissions(kick_members=True)
    @commands.slash_command(name="kick", description="Kick một thành viên ra khỏi server")
    async def kick(self,
                   interaction: disnake.CommandInteraction,
                   member: disnake.Member = commands.Param(description="Thành viên cần kick"),
                   reason: Optional[str] = commands.Param(default=None, description="Lý do kick")):

        # Check hierarchy
        if not await self._check_hierarchy(interaction, member):
            return

        try:
            # Store member info before kicking
            member_name = str(member)
            member_id = member.id

            await member.kick(reason=reason)

            embed = disnake.Embed(
                title="✅ Kick thành công",
                color=0xff6b00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Thành viên", value=f"{member_name} ({member_id})", inline=True)
            embed.add_field(name="Lý do", value=reason or "Không có lý do", inline=True)
            embed.add_field(name="Người thực hiện", value=interaction.author.mention, inline=True)
            embed.set_footer(text=f"ID: {member_id}")

            await interaction.response.send_message(embed=embed)

        except disnake.Forbidden:
            await interaction.response.send_message("❌ Tôi không có quyền kick thành viên này!", ephemeral=True)
        except disnake.HTTPException as e:
            await interaction.response.send_message(f"❌ Lỗi HTTP khi kick: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi không xác định: {str(e)}", ephemeral=True)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.slash_command(name="ban", description="Ban một thành viên khỏi server")
    async def ban(self,
                  interaction: disnake.CommandInteraction,
                  member: Union[disnake.Member, disnake.User] = commands.Param(description="Thành viên/User cần ban"),
                  delete_message_days: int = commands.Param(default=0, description="Xóa tin nhắn trong X ngày (0-7)", min_value=0, max_value=7),
                  reason: Optional[str] = commands.Param(default=None, description="Lý do ban")):

        # Check hierarchy if member is in guild
        if isinstance(member, disnake.Member):
            if not await self._check_hierarchy(interaction, member):
                return

        try:
            # Store member info before banning
            member_name = str(member)
            member_id = member.id

            await interaction.guild.ban(member, delete_message_days=delete_message_days, reason=reason)

            embed = disnake.Embed(
                title="✅ Ban thành công",
                color=0xff0000,
                timestamp=datetime.now()
            )
            embed.add_field(name="Thành viên", value=f"{member_name} ({member_id})", inline=True)
            embed.add_field(name="Xóa tin nhắn", value=f"{delete_message_days} ngày", inline=True)
            embed.add_field(name="Lý do", value=reason or "Không có lý do", inline=True)
            embed.add_field(name="Người thực hiện", value=interaction.author.mention, inline=True)
            embed.set_footer(text=f"ID: {member_id}")

            await interaction.response.send_message(embed=embed)

        except disnake.Forbidden:
            await interaction.response.send_message("❌ Tôi không có quyền ban thành viên này!", ephemeral=True)
        except disnake.HTTPException as e:
            await interaction.response.send_message(f"❌ Lỗi HTTP khi ban: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi không xác định: {str(e)}", ephemeral=True)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.has_guild_permissions(ban_members=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    @commands.slash_command(name="unban", description="Unban một user khỏi server")
    async def unban(self,
                    interaction: disnake.CommandInteraction,
                    user_id: str = commands.Param(description="ID của user cần unban"),
                    reason: Optional[str] = commands.Param(default=None, description="Lý do unban")):

        try:
            # Validate user ID
            try:
                user_id_int = int(user_id)
            except ValueError:
                await interaction.response.send_message("❌ ID user không hợp lệ!", ephemeral=True)
                return

            # Check if user is banned
            try:
                ban_entry = await interaction.guild.fetch_ban(disnake.Object(user_id_int))
                banned_user = ban_entry.user
            except disnake.NotFound:
                await interaction.response.send_message("❌ User này không bị ban!", ephemeral=True)
                return

            await interaction.guild.unban(banned_user, reason=reason)

            embed = disnake.Embed(
                title="✅ Unban thành công",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="User", value=f"{banned_user} ({banned_user.id})", inline=True)
            embed.add_field(name="Lý do", value=reason or "Không có lý do", inline=True)
            embed.add_field(name="Người thực hiện", value=interaction.author.mention, inline=True)
            embed.set_footer(text=f"ID: {banned_user.id}")

            await interaction.response.send_message(embed=embed)

        except disnake.Forbidden:
            await interaction.response.send_message("❌ Tôi không có quyền unban user này!", ephemeral=True)
        except disnake.HTTPException as e:
            await interaction.response.send_message(f"❌ Lỗi HTTP khi unban: {str(e)}", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi không xác định: {str(e)}", ephemeral=True)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.slash_command(name="purge", description="Xóa nhiều tin nhắn trong channel")
    async def purge(self,
                    interaction: disnake.CommandInteraction,
                    amount: int = commands.Param(description="Số lượng tin nhắn cần xóa (1-100)", min_value=1, max_value=100),
                    member: Optional[disnake.Member] = commands.Param(default=None, description="Chỉ xóa tin nhắn của thành viên này")):

        await interaction.response.defer(ephemeral=True)

        try:
            def check_message(message):
                if member:
                    return message.author == member
                return True

            deleted = await interaction.channel.purge(limit=amount, check=check_message)

            embed = disnake.Embed(
                title="✅ Xóa tin nhắn thành công",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Số lượng xóa", value=f"{len(deleted)} tin nhắn", inline=True)
            embed.add_field(name="Channel", value=interaction.channel.mention, inline=True)
            if member:
                embed.add_field(name="Từ thành viên", value=member.mention, inline=True)
            embed.add_field(name="Người thực hiện", value=interaction.author.mention, inline=True)

            await interaction.edit_original_response(embed=embed)

        except disnake.Forbidden:
            await interaction.edit_original_response(content="❌ Tôi không có quyền xóa tin nhắn trong channel này!")
        except disnake.HTTPException as e:
            await interaction.edit_original_response(content=f"❌ Lỗi HTTP khi xóa tin nhắn: {str(e)}")
        except Exception as e:
            await interaction.edit_original_response(content=f"❌ Lỗi không xác định: {str(e)}")


def setup(bot: ClientUser):
    bot.add_cog(Moderator(bot))
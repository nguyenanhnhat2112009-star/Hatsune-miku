import disnake
from disnake.ext import commands
from datetime import datetime, timedelta
from typing import Optional, Union, Callable
import asyncio
import re
from utils.ClientUser import ClientUser


class PurgeConfirmView(disnake.ui.View):
    def __init__(self, user: disnake.User, purge_func: Callable, **kwargs):
        super().__init__(timeout=30)
        self.user = user
        self.purge_func = purge_func
        self.kwargs = kwargs
        self.confirmed = False

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Chỉ người dùng lệnh mới có thể xác nhận!", ephemeral=True)
            return False
        return True

    @disnake.ui.button(label="✅ Xác nhận", style=disnake.ButtonStyle.danger)
    async def confirm_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.confirmed = True
        await interaction.response.edit_message(
            content="🔄 Đang xóa tin nhắn...",
            embed=None,
            view=None
        )

        try:
            await self.purge_func(**self.kwargs)
        except Exception as e:
            await interaction.edit_original_response(
                content=f"❌ Lỗi khi xóa tin nhắn: {str(e)}"
            )

    @disnake.ui.button(label="❌ Hủy bỏ", style=disnake.ButtonStyle.secondary)
    async def cancel_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="❌ Đã hủy",
            description="Thao tác xóa tin nhắn đã được hủy bỏ.",
            color=0xff0000
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def on_timeout(self):
        if not self.confirmed:
            for item in self.children:
                item.disabled = True


class Purge(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot

    def _create_purge_embed(self,
                           deleted_count: int,
                           total_requested: int,
                           channel: disnake.TextChannel,
                           user: disnake.User,
                           filter_type: str = "all",
                           target_user: Optional[disnake.User] = None) -> disnake.Embed:
        """Create a beautiful embed for purge results."""

        embed = disnake.Embed(
            title="🧹 Xóa tin nhắn thành công",
            color=0x00ff00,
            timestamp=datetime.now()
        )

        # Main info
        embed.add_field(
            name="📊 Thống kê",
            value=f"""
            **Đã xóa:** `{deleted_count}` tin nhắn
            **Yêu cầu:** `{total_requested}` tin nhắn
            **Hiệu quả:** `{(deleted_count/total_requested*100):.1f}%`
            """,
            inline=True
        )

        # Channel info
        embed.add_field(
            name="📍 Vị trí",
            value=f"""
            **Channel:** {channel.mention}
            **Loại:** `{filter_type}`
            **Thời gian:** <t:{int(datetime.now().timestamp())}:R>
            """,
            inline=True
        )

        # User info
        user_info = f"**Người thực hiện:** {user.mention}\n"
        if target_user:
            user_info += f"**Mục tiêu:** {target_user.mention}\n"
        user_info += f"**ID:** `{user.id}`"

        embed.add_field(
            name="👤 Thông tin",
            value=user_info,
            inline=True
        )

        # Add warning if not all messages were deleted
        if deleted_count < total_requested:
            embed.add_field(
                name="⚠️ Lưu ý",
                value="Một số tin nhắn có thể không được xóa do:\n• Tin nhắn quá cũ (>14 ngày)\n• Quyền hạn không đủ\n• Tin nhắn đã bị xóa",
                inline=False
            )

        embed.set_footer(
            text=f"Message Cleaner • ID: {channel.id}",
            icon_url=self.bot.user.display_avatar.url
        )

        return embed

    async def _safe_purge(self,
                         interaction: disnake.ApplicationCommandInteraction,
                         amount: int,
                         check_func: Optional[Callable] = None,
                         filter_name: str = "all",
                         target_user: Optional[disnake.User] = None):
        """Safely purge messages with proper error handling."""

        try:
            deleted = await interaction.channel.purge(
                limit=amount,
                check=check_func,
                before=datetime.now(),
                oldest_first=False
            )

            embed = self._create_purge_embed(
                deleted_count=len(deleted),
                total_requested=amount,
                channel=interaction.channel,
                user=interaction.author,
                filter_type=filter_name,
                target_user=target_user
            )

            await interaction.edit_original_response(embed=embed)

            # Auto-delete success message after 10 seconds
            await asyncio.sleep(10)
            try:
                await interaction.delete_original_response()
            except:
                pass

        except disnake.Forbidden:
            embed = disnake.Embed(
                title="❌ Không có quyền",
                description="Bot không có quyền xóa tin nhắn trong channel này!",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)
        except disnake.HTTPException as e:
            embed = disnake.Embed(
                title="❌ Lỗi HTTP",
                description=f"Lỗi khi xóa tin nhắn: {str(e)}",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Lỗi không xác định",
                description=f"Đã xảy ra lỗi: {str(e)}",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.slash_command(name="clear", description="Xóa tin nhắn với nhiều tùy chọn lọc")
    async def clear_messages(self,
                            interaction: disnake.ApplicationCommandInteraction,
                            amount: int = commands.Param(description="Số lượng tin nhắn cần xóa (1-100)", min_value=1, max_value=100),
                            user: Optional[disnake.Member] = commands.Param(default=None, description="Chỉ xóa tin nhắn của user này"),
                            contains: Optional[str] = commands.Param(default=None, description="Chỉ xóa tin nhắn chứa text này"),
                            starts_with: Optional[str] = commands.Param(default=None, description="Chỉ xóa tin nhắn bắt đầu bằng text này"),
                            ends_with: Optional[str] = commands.Param(default=None, description="Chỉ xóa tin nhắn kết thúc bằng text này"),
                            has_attachments: Optional[bool] = commands.Param(default=None, description="Chỉ xóa tin nhắn có/không có file đính kèm"),
                            has_embeds: Optional[bool] = commands.Param(default=None, description="Chỉ xóa tin nhắn có/không có embeds"),
                            from_bots: Optional[bool] = commands.Param(default=None, description="Chỉ xóa tin nhắn từ bot"),
                            confirm: bool = commands.Param(default=True, description="Yêu cầu xác nhận trước khi xóa")):
        """Advanced message clearing with multiple filter options."""

        # Build filter description
        filters = []
        if user:
            filters.append(f"👤 User: {user.mention}")
        if contains:
            filters.append(f"📝 Chứa: `{contains}`")
        if starts_with:
            filters.append(f"▶️ Bắt đầu: `{starts_with}`")
        if ends_with:
            filters.append(f"⏹️ Kết thúc: `{ends_with}`")
        if has_attachments is not None:
            filters.append(f"📎 File: {'Có' if has_attachments else 'Không'}")
        if has_embeds is not None:
            filters.append(f"📋 Embed: {'Có' if has_embeds else 'Không'}")
        if from_bots is not None:
            filters.append(f"🤖 Bot: {'Chỉ bot' if from_bots else 'Không bot'}")

        filter_description = "\n".join(filters) if filters else "Không có bộ lọc (xóa tất cả)"

        # Create check function
        def message_check(message):
            # User filter
            if user and message.author != user:
                return False

            # Content filters
            if contains and contains.lower() not in message.content.lower():
                return False
            if starts_with and not message.content.lower().startswith(starts_with.lower()):
                return False
            if ends_with and not message.content.lower().endswith(ends_with.lower()):
                return False

            # Attachment filter
            if has_attachments is not None:
                if has_attachments and not message.attachments:
                    return False
                if not has_attachments and message.attachments:
                    return False

            # Embed filter
            if has_embeds is not None:
                if has_embeds and not message.embeds:
                    return False
                if not has_embeds and message.embeds:
                    return False

            # Bot filter
            if from_bots is not None:
                if from_bots and not message.author.bot:
                    return False
                if not from_bots and message.author.bot:
                    return False

            return True

        if confirm:
            # Show confirmation embed
            embed = disnake.Embed(
                title="⚠️ Xác nhận xóa tin nhắn",
                description=f"Bạn có chắc muốn xóa **{amount}** tin nhắn với các bộ lọc sau?",
                color=0xffaa00,
                timestamp=datetime.now()
            )

            embed.add_field(
                name="📍 Channel",
                value=interaction.channel.mention,
                inline=True
            )

            embed.add_field(
                name="📊 Số lượng",
                value=f"`{amount}` tin nhắn",
                inline=True
            )

            embed.add_field(
                name="🔍 Bộ lọc",
                value=filter_description,
                inline=False
            )

            embed.add_field(
                name="⚠️ Cảnh báo",
                value="• Hành động này không thể hoàn tác\n• Tin nhắn cũ hơn 14 ngày không thể xóa\n• Bot cần quyền Manage Messages",
                inline=False
            )

            embed.set_footer(
                text="Nhấn ✅ để xác nhận hoặc ❌ để hủy • Timeout: 30s",
                icon_url=interaction.author.display_avatar.url
            )

            # Create confirmation view
            view = PurgeConfirmView(
                user=interaction.author,
                purge_func=self._safe_purge,
                interaction=interaction,
                amount=amount,
                check_func=message_check,
                filter_name="filtered",
                target_user=user
            )

            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        else:
            await interaction.response.defer(ephemeral=True)
            await self._safe_purge(
                interaction=interaction,
                amount=amount,
                check_func=message_check,
                filter_name="filtered",
                target_user=user
            )

    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.slash_command(name="purge-bots", description="Xóa tin nhắn từ bot trong channel")
    async def purge_bots(self,
                        interaction: disnake.ApplicationCommandInteraction,
                        amount: int = commands.Param(description="Số lượng tin nhắn cần kiểm tra (1-100)", min_value=1, max_value=100)):
        """Remove messages from bots only."""

        await interaction.response.defer(ephemeral=True)

        def bot_check(message):
            return message.author.bot

        await self._safe_purge(
            interaction=interaction,
            amount=amount,
            check_func=bot_check,
            filter_name="bot messages"
        )

    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.slash_command(name="purge-embeds", description="Xóa tin nhắn có embeds")
    async def purge_embeds(self,
                          interaction: disnake.ApplicationCommandInteraction,
                          amount: int = commands.Param(description="Số lượng tin nhắn cần kiểm tra (1-100)", min_value=1, max_value=100)):
        """Remove messages with embeds."""

        await interaction.response.defer(ephemeral=True)

        def embed_check(message):
            return len(message.embeds) > 0

        await self._safe_purge(
            interaction=interaction,
            amount=amount,
            check_func=embed_check,
            filter_name="messages with embeds"
        )

    @commands.cooldown(1, 15, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.slash_command(name="purge-files", description="Xóa tin nhắn có file đính kèm")
    async def purge_files(self,
                         interaction: disnake.ApplicationCommandInteraction,
                         amount: int = commands.Param(description="Số lượng tin nhắn cần kiểm tra (1-100)", min_value=1, max_value=100)):
        """Remove messages with file attachments."""

        await interaction.response.defer(ephemeral=True)

        def file_check(message):
            return len(message.attachments) > 0

        await self._safe_purge(
            interaction=interaction,
            amount=amount,
            check_func=file_check,
            filter_name="messages with files"
        )

    @commands.cooldown(1, 20, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.slash_command(name="purge-regex", description="Xóa tin nhắn khớp với regex pattern")
    async def purge_regex(self,
                         interaction: disnake.ApplicationCommandInteraction,
                         pattern: str = commands.Param(description="Regex pattern để tìm tin nhắn"),
                         amount: int = commands.Param(description="Số lượng tin nhắn cần kiểm tra (1-100)", min_value=1, max_value=100),
                         case_sensitive: bool = commands.Param(default=False, description="Phân biệt chữ hoa/thường")):
        """Remove messages matching regex pattern."""

        try:
            # Validate regex pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            compiled_pattern = re.compile(pattern, flags)
        except re.error as e:
            embed = disnake.Embed(
                title="❌ Regex không hợp lệ",
                description=f"Pattern regex không đúng định dạng:\n```\n{str(e)}\n```",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        def regex_check(message):
            return compiled_pattern.search(message.content) is not None

        await self._safe_purge(
            interaction=interaction,
            amount=amount,
            check_func=regex_check,
            filter_name=f"regex: {pattern}"
        )

    @commands.cooldown(1, 30, commands.BucketType.guild)
    @commands.has_guild_permissions(manage_messages=True)
    @commands.bot_has_guild_permissions(manage_messages=True)
    @commands.slash_command(name="purge-old", description="Xóa tin nhắn cũ hơn X ngày")
    async def purge_old(self,
                       interaction: disnake.ApplicationCommandInteraction,
                       days: int = commands.Param(description="Xóa tin nhắn cũ hơn X ngày (1-14)", min_value=1, max_value=14),
                       amount: int = commands.Param(description="Số lượng tin nhắn tối đa cần kiểm tra (1-100)", min_value=1, max_value=100)):
        """Remove messages older than specified days."""

        cutoff_date = datetime.now() - timedelta(days=days)

        await interaction.response.defer(ephemeral=True)

        def age_check(message):
            return message.created_at < cutoff_date

        await self._safe_purge(
            interaction=interaction,
            amount=amount,
            check_func=age_check,
            filter_name=f"older than {days} days"
        )

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="purge-info", description="Thông tin về các lệnh xóa tin nhắn")
    async def purge_info(self, interaction: disnake.ApplicationCommandInteraction):
        """Show information about purge commands."""

        embed = disnake.Embed(
            title="🧹 Message Cleaner - Hướng dẫn sử dụng",
            description="Hệ thống xóa tin nhắn chuyên nghiệp với nhiều tùy chọn lọc",
            color=0x7289da,
            timestamp=datetime.now()
        )

        # Basic commands
        embed.add_field(
            name="🔧 Lệnh cơ bản",
            value="""
            `/clear` - Xóa tin nhắn với bộ lọc nâng cao
            `/purge-bots` - Xóa tin nhắn từ bot
            `/purge-embeds` - Xóa tin nhắn có embeds
            `/purge-files` - Xóa tin nhắn có file đính kèm
            """,
            inline=False
        )

        # Advanced commands
        embed.add_field(
            name="⚙️ Lệnh nâng cao",
            value="""
            `/purge-regex` - Xóa tin nhắn khớp regex
            `/purge-old` - Xóa tin nhắn cũ hơn X ngày
            `/purge-info` - Hiển thị hướng dẫn này
            """,
            inline=False
        )

        # Filter options for /clear
        embed.add_field(
            name="🔍 Bộ lọc /clear",
            value="""
            **user** - Chỉ xóa tin nhắn của user cụ thể
            **contains** - Chỉ xóa tin nhắn chứa text
            **starts_with** - Chỉ xóa tin nhắn bắt đầu bằng text
            **ends_with** - Chỉ xóa tin nhắn kết thúc bằng text
            **has_attachments** - Lọc theo file đính kèm
            **has_embeds** - Lọc theo embeds
            **from_bots** - Lọc theo tin nhắn từ bot
            """,
            inline=False
        )

        # Important notes
        embed.add_field(
            name="⚠️ Lưu ý quan trọng",
            value="""
            🔒 **Quyền:** Cần quyền `Manage Messages`
            ⏰ **Giới hạn:** Chỉ xóa được tin nhắn <14 ngày
            🔢 **Số lượng:** Tối đa 100 tin nhắn mỗi lần
            ❌ **Không hoàn tác:** Hành động không thể hoàn tác
            ⏱️ **Cooldown:** Có giới hạn thời gian sử dụng
            """,
            inline=False
        )

        # Examples
        embed.add_field(
            name="💡 Ví dụ sử dụng",
            value="""
            `/clear amount:50 user:@spam_user` - Xóa 50 tin nhắn của user
            `/clear amount:20 contains:spam` - Xóa tin nhắn chứa "spam"
            `/purge-bots amount:30` - Xóa 30 tin nhắn từ bot
            `/purge-regex pattern:\\d{4,}` - Xóa tin nhắn có 4+ số liên tiếp
            """,
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text="Message Cleaner v2.0 • Use responsibly",
            icon_url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: ClientUser):
    bot.add_cog(Purge(bot))

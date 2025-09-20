import disnake
from disnake.ext import commands
from datetime import datetime
from typing import Optional
from utils.ClientUser import ClientUser


class ServerInfo(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="server-info", description="Xem thông tin chi tiết về server")
    async def server_info(self, interaction: disnake.ApplicationCommandInteraction):
        """Display detailed server information."""
        if not interaction.guild:
            await interaction.response.send_message("❌ Lệnh này chỉ có thể sử dụng trong server!", ephemeral=True)
            return

        guild = interaction.guild

        # Get server statistics
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != disnake.Status.offline)
        bot_count = sum(1 for member in guild.members if member.bot)
        human_count = total_members - bot_count

        # Get channel counts
        text_channels = len([c for c in guild.channels if isinstance(c, disnake.TextChannel)])
        voice_channels = len([c for c in guild.channels if isinstance(c, disnake.VoiceChannel)])
        categories = len([c for c in guild.channels if isinstance(c, disnake.CategoryChannel)])

        # Get role count
        role_count = len(guild.roles) - 1  # Exclude @everyone

        # Get emoji count
        emoji_count = len(guild.emojis)
        animated_emoji_count = sum(1 for emoji in guild.emojis if emoji.animated)
        static_emoji_count = emoji_count - animated_emoji_count

        # Server creation date
        created_at = guild.created_at.strftime("%d/%m/%Y %H:%M:%S")
        server_age = (datetime.now() - guild.created_at.replace(tzinfo=None)).days

        embed = disnake.Embed(
            title=f"🏰 Thông tin Server - {guild.name}",
            color=0x7289da,
            timestamp=datetime.now()
        )

        # Basic info
        basic_info = f"""
        **Tên:** {guild.name}
        **ID:** `{guild.id}`
        **Chủ sở hữu:** {guild.owner.mention if guild.owner else "Không xác định"}
        **Tạo lúc:** {created_at}
        **Tuổi server:** {server_age} ngày
        """
        embed.add_field(name="📋 Thông tin cơ bản", value=basic_info, inline=False)

        # Member statistics
        member_stats = f"""
        **Tổng thành viên:** {total_members:,}
        **Đang online:** {online_members:,}
        **Con người:** {human_count:,}
        **Bot:** {bot_count:,}
        """
        embed.add_field(name="👥 Thành viên", value=member_stats, inline=True)

        # Channel statistics
        channel_stats = f"""
        **Text channels:** {text_channels}
        **Voice channels:** {voice_channels}
        **Categories:** {categories}
        **Tổng channels:** {len(guild.channels)}
        """
        embed.add_field(name="📺 Kênh", value=channel_stats, inline=True)

        # Other statistics
        other_stats = f"""
        **Roles:** {role_count}
        **Emoji:** {emoji_count} ({static_emoji_count} tĩnh, {animated_emoji_count} động)
        **Boost level:** {guild.premium_tier}
        **Boosts:** {guild.premium_subscription_count or 0}
        """
        embed.add_field(name="🎭 Khác", value=other_stats, inline=True)

        # Verification level
        verification_levels = {
            disnake.VerificationLevel.none: "Không",
            disnake.VerificationLevel.low: "Thấp",
            disnake.VerificationLevel.medium: "Trung bình",
            disnake.VerificationLevel.high: "Cao",
            disnake.VerificationLevel.highest: "Cao nhất"
        }

        # Content filter
        content_filters = {
            disnake.ContentFilter.disabled: "Tắt",
            disnake.ContentFilter.no_role: "Thành viên không có role",
            disnake.ContentFilter.all_members: "Tất cả thành viên"
        }

        security_info = f"""
        **Xác minh:** {verification_levels.get(guild.verification_level, "Không xác định")}
        **Lọc nội dung:** {content_filters.get(guild.explicit_content_filter, "Không xác định")}
        **2FA required:** {"Có" if guild.mfa_level else "Không"}
        """
        embed.add_field(name="🔒 Bảo mật", value=security_info, inline=False)

        # Features
        if guild.features:
            features_text = ", ".join([feature.replace("_", " ").title() for feature in guild.features[:10]])
            if len(guild.features) > 10:
                features_text += f" và {len(guild.features) - 10} tính năng khác"
            embed.add_field(name="✨ Tính năng", value=features_text, inline=False)

        # Set server icon and banner
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        if guild.banner:
            embed.set_image(url=guild.banner.url)

        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="server-icon", description="Xem icon của server")
    async def server_icon(self, interaction: disnake.ApplicationCommandInteraction):
        """Display server icon."""
        if not interaction.guild:
            await interaction.response.send_message("❌ Lệnh này chỉ có thể sử dụng trong server!", ephemeral=True)
            return

        guild = interaction.guild

        if not guild.icon:
            embed = disnake.Embed(
                title="ℹ️ Không có icon",
                description=f"Server **{guild.name}** không có icon.",
                color=0xffaa00,
                timestamp=datetime.now()
            )
        else:
            # Get icon URLs
            icon_url = guild.icon.url
            icon_png = guild.icon.with_format('png').url
            icon_jpg = guild.icon.with_format('jpg').url
            icon_webp = guild.icon.with_format('webp').url

            # Check if animated
            icon_gif = None
            if guild.icon.is_animated():
                icon_gif = guild.icon.with_format('gif').url

            embed = disnake.Embed(
                title=f"🖼️ Icon Server - {guild.name}",
                color=0x7289da,
                timestamp=datetime.now()
            )

            embed.set_image(url=icon_url)

            # Add download links
            download_links = f"[PNG]({icon_png}) • [JPG]({icon_jpg}) • [WebP]({icon_webp})"
            if icon_gif:
                download_links += f" • [GIF]({icon_gif})"

            embed.add_field(
                name="📥 Tải xuống",
                value=download_links,
                inline=False
            )

            # Add different sizes
            sizes = ["16", "32", "64", "128", "256", "512", "1024", "2048", "4096"]
            size_links = []
            for size in sizes:
                size_url = guild.icon.with_size(int(size)).url
                size_links.append(f"[{size}px]({size_url})")

            embed.add_field(
                name="📏 Kích thước khác nhau",
                value=" • ".join(size_links),
                inline=False
            )

        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="server-banner", description="Xem banner của server")
    async def server_banner(self, interaction: disnake.ApplicationCommandInteraction):
        """Display server banner."""
        if not interaction.guild:
            await interaction.response.send_message("❌ Lệnh này chỉ có thể sử dụng trong server!", ephemeral=True)
            return

        guild = interaction.guild

        if not guild.banner:
            embed = disnake.Embed(
                title="ℹ️ Không có banner",
                description=f"Server **{guild.name}** không có banner.",
                color=0xffaa00,
                timestamp=datetime.now()
            )
            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
        else:
            # Get banner URLs
            banner_url = guild.banner.url
            banner_png = guild.banner.with_format('png').url
            banner_jpg = guild.banner.with_format('jpg').url
            banner_webp = guild.banner.with_format('webp').url

            # Check if animated
            banner_gif = None
            if guild.banner.is_animated():
                banner_gif = guild.banner.with_format('gif').url

            embed = disnake.Embed(
                title=f"🎨 Banner Server - {guild.name}",
                color=0x7289da,
                timestamp=datetime.now()
            )

            embed.set_image(url=banner_url)

            # Add download links
            download_links = f"[PNG]({banner_png}) • [JPG]({banner_jpg}) • [WebP]({banner_webp})"
            if banner_gif:
                download_links += f" • [GIF]({banner_gif})"

            embed.add_field(
                name="📥 Tải xuống",
                value=download_links,
                inline=False
            )

        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.slash_command(name="member-count", description="Thống kê thành viên server")
    async def member_count(self, interaction: disnake.ApplicationCommandInteraction):
        """Display detailed member statistics."""
        if not interaction.guild:
            await interaction.response.send_message("❌ Lệnh này chỉ có thể sử dụng trong server!", ephemeral=True)
            return

        guild = interaction.guild

        # Count members by status
        online = sum(1 for member in guild.members if member.status == disnake.Status.online)
        idle = sum(1 for member in guild.members if member.status == disnake.Status.idle)
        dnd = sum(1 for member in guild.members if member.status == disnake.Status.dnd)
        offline = sum(1 for member in guild.members if member.status == disnake.Status.offline)

        # Count bots vs humans
        bots = sum(1 for member in guild.members if member.bot)
        humans = guild.member_count - bots

        embed = disnake.Embed(
            title=f"📊 Thống kê thành viên - {guild.name}",
            color=0x00ff88,
            timestamp=datetime.now()
        )

        # Total members
        embed.add_field(
            name="👥 Tổng thành viên",
            value=f"**{guild.member_count:,}** thành viên",
            inline=False
        )

        # Status breakdown
        status_info = f"""
        🟢 **Online:** {online:,}
        🟡 **Idle:** {idle:,}
        🔴 **DND:** {dnd:,}
        ⚫ **Offline:** {offline:,}
        """
        embed.add_field(name="📈 Trạng thái", value=status_info, inline=True)

        # Type breakdown
        type_info = f"""
        👤 **Con người:** {humans:,}
        🤖 **Bot:** {bots:,}
        """
        embed.add_field(name="🔍 Loại", value=type_info, inline=True)

        # Create a simple progress bar for online members
        online_percentage = (online / guild.member_count) * 100 if guild.member_count > 0 else 0
        filled = int(online_percentage / 10)
        bar = "█" * filled + "░" * (10 - filled)

        embed.add_field(
            name="📊 Tỷ lệ online",
            value=f"`{bar}` {online_percentage:.1f}%",
            inline=False
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_footer(
            text=f"Cập nhật bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)


def setup(bot: ClientUser):
    bot.add_cog(ServerInfo(bot))

import disnake
from disnake.ext import commands
from datetime import datetime
from typing import Optional
from utils.ClientUser import ClientUser


class Avatar(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="avatar", description="Xem avatar của người dùng")
    async def avatar(
        self, 
        interaction: disnake.ApplicationCommandInteraction,
        user: Optional[disnake.User] = None
    ):
        """Display user's avatar with various formats and sizes."""
        target_user = user or interaction.author
        
        # Get avatar URL with different formats
        avatar_url = target_user.display_avatar.url
        avatar_png = target_user.display_avatar.with_format('png').url
        avatar_jpg = target_user.display_avatar.with_format('jpg').url
        avatar_webp = target_user.display_avatar.with_format('webp').url
        
        # Check if user has animated avatar (GIF)
        avatar_gif = None
        if target_user.display_avatar.is_animated():
            avatar_gif = target_user.display_avatar.with_format('gif').url

        # Create embed
        embed = disnake.Embed(
            title=f"🖼️ Avatar của {target_user.display_name}",
            color=0x7289da,
            timestamp=datetime.now()
        )

        # Set the main avatar image
        embed.set_image(url=avatar_url)
        
        # Add user info
        embed.add_field(
            name="👤 Thông tin người dùng",
            value=f"**Tên:** {target_user.display_name}\n**Username:** {target_user.name}\n**ID:** `{target_user.id}`",
            inline=False
        )

        # Add download links
        download_links = f"[PNG]({avatar_png}) • [JPG]({avatar_jpg}) • [WebP]({avatar_webp})"
        if avatar_gif:
            download_links += f" • [GIF]({avatar_gif})"
        
        embed.add_field(
            name="📥 Tải xuống",
            value=download_links,
            inline=False
        )

        # Add different sizes
        sizes = ["16", "32", "64", "128", "256", "512", "1024", "2048", "4096"]
        size_links = []
        for size in sizes:
            size_url = target_user.display_avatar.with_size(int(size)).url
            size_links.append(f"[{size}px]({size_url})")
        
        embed.add_field(
            name="📏 Kích thước khác nhau",
            value=" • ".join(size_links),
            inline=False
        )

        # Set footer
        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="server-avatar", description="Xem avatar server của thành viên")
    async def server_avatar(
        self, 
        interaction: disnake.ApplicationCommandInteraction,
        member: Optional[disnake.Member] = None
    ):
        """Display member's server-specific avatar."""
        if not interaction.guild:
            await interaction.response.send_message("❌ Lệnh này chỉ có thể sử dụng trong server!", ephemeral=True)
            return

        target_member = member or interaction.author
        
        # Check if member has server-specific avatar
        if target_member.guild_avatar is None:
            embed = disnake.Embed(
                title="ℹ️ Không có avatar server",
                description=f"{target_member.display_name} không có avatar riêng cho server này.",
                color=0xffaa00,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=target_member.display_avatar.url)
        else:
            # Get server avatar URLs
            server_avatar_url = target_member.guild_avatar.url
            server_avatar_png = target_member.guild_avatar.with_format('png').url
            server_avatar_jpg = target_member.guild_avatar.with_format('jpg').url
            server_avatar_webp = target_member.guild_avatar.with_format('webp').url
            
            # Check if animated
            server_avatar_gif = None
            if target_member.guild_avatar.is_animated():
                server_avatar_gif = target_member.guild_avatar.with_format('gif').url

            embed = disnake.Embed(
                title=f"🏠 Avatar Server của {target_member.display_name}",
                color=0x7289da,
                timestamp=datetime.now()
            )

            embed.set_image(url=server_avatar_url)
            
            # Add member info
            embed.add_field(
                name="👤 Thông tin thành viên",
                value=f"**Tên hiển thị:** {target_member.display_name}\n**Username:** {target_member.name}\n**ID:** `{target_member.id}`",
                inline=False
            )

            # Add download links
            download_links = f"[PNG]({server_avatar_png}) • [JPG]({server_avatar_jpg}) • [WebP]({server_avatar_webp})"
            if server_avatar_gif:
                download_links += f" • [GIF]({server_avatar_gif})"
            
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

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="avatar-compare", description="So sánh avatar của hai người dùng")
    async def avatar_compare(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        user1: disnake.User,
        user2: Optional[disnake.User] = None
    ):
        """Compare avatars of two users."""
        user2 = user2 or interaction.author
        
        embed = disnake.Embed(
            title="🔄 So sánh Avatar",
            color=0x7289da,
            timestamp=datetime.now()
        )

        # User 1 info
        embed.add_field(
            name=f"👤 {user1.display_name}",
            value=f"**Username:** {user1.name}\n**ID:** `{user1.id}`\n[Xem avatar]({user1.display_avatar.url})",
            inline=True
        )

        # User 2 info
        embed.add_field(
            name=f"👤 {user2.display_name}",
            value=f"**Username:** {user2.name}\n**ID:** `{user2.id}`\n[Xem avatar]({user2.display_avatar.url})",
            inline=True
        )

        # Add a spacer field
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        # Set thumbnail to first user's avatar
        embed.set_thumbnail(url=user1.display_avatar.url)
        
        # Set image to second user's avatar
        embed.set_image(url=user2.display_avatar.url)

        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)


    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="banner", description="Xem banner của người dùng")
    async def banner(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        user: Optional[disnake.User] = None
    ):
        """Display user's banner."""
        target_user = user or interaction.author

        # Fetch user to get banner info
        try:
            fetched_user = await self.bot.fetch_user(target_user.id)
        except:
            await interaction.response.send_message("❌ Không thể lấy thông tin người dùng!", ephemeral=True)
            return

        if fetched_user.banner is None:
            embed = disnake.Embed(
                title="ℹ️ Không có banner",
                description=f"{target_user.display_name} không có banner.",
                color=0xffaa00,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=target_user.display_avatar.url)
        else:
            banner_url = fetched_user.banner.url
            banner_png = fetched_user.banner.with_format('png').url
            banner_jpg = fetched_user.banner.with_format('jpg').url
            banner_webp = fetched_user.banner.with_format('webp').url

            # Check if animated
            banner_gif = None
            if fetched_user.banner.is_animated():
                banner_gif = fetched_user.banner.with_format('gif').url

            embed = disnake.Embed(
                title=f"🎨 Banner của {target_user.display_name}",
                color=fetched_user.accent_color or 0x7289da,
                timestamp=datetime.now()
            )

            embed.set_image(url=banner_url)

            # Add user info
            embed.add_field(
                name="👤 Thông tin người dùng",
                value=f"**Tên:** {target_user.display_name}\n**Username:** {target_user.name}\n**ID:** `{target_user.id}`",
                inline=False
            )

            # Add download links
            download_links = f"[PNG]({banner_png}) • [JPG]({banner_jpg}) • [WebP]({banner_webp})"
            if banner_gif:
                download_links += f" • [GIF]({banner_gif})"

            embed.add_field(
                name="📥 Tải xuống",
                value=download_links,
                inline=False
            )

            # Add accent color if available
            if fetched_user.accent_color:
                embed.add_field(
                    name="🎨 Màu chủ đạo",
                    value=f"`{str(fetched_user.accent_color)}`",
                    inline=True
                )

        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="user-info", description="Xem thông tin chi tiết của người dùng")
    async def user_info(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        user: Optional[disnake.User] = None
    ):
        """Display detailed user information including avatar, banner, and more."""
        target_user = user or interaction.author

        # Fetch user to get complete info
        try:
            fetched_user = await self.bot.fetch_user(target_user.id)
        except:
            await interaction.response.send_message("❌ Không thể lấy thông tin người dùng!", ephemeral=True)
            return

        embed = disnake.Embed(
            title=f"📋 Thông tin chi tiết - {target_user.display_name}",
            color=fetched_user.accent_color or 0x7289da,
            timestamp=datetime.now()
        )

        # Basic info
        created_at = target_user.created_at.strftime("%d/%m/%Y %H:%M:%S")
        account_age = (datetime.now() - target_user.created_at.replace(tzinfo=None)).days

        basic_info = f"""
        **Tên hiển thị:** {target_user.display_name}
        **Username:** {target_user.name}
        **ID:** `{target_user.id}`
        **Tạo tài khoản:** {created_at}
        **Tuổi tài khoản:** {account_age} ngày
        """
        embed.add_field(name="👤 Thông tin cơ bản", value=basic_info, inline=False)

        # Avatar info
        avatar_info = f"[Xem avatar]({target_user.display_avatar.url})"
        if target_user.display_avatar.is_animated():
            avatar_info += " • 🎬 Có hoạt ảnh"
        embed.add_field(name="🖼️ Avatar", value=avatar_info, inline=True)

        # Banner info
        if fetched_user.banner:
            banner_info = f"[Xem banner]({fetched_user.banner.url})"
            if fetched_user.banner.is_animated():
                banner_info += " • 🎬 Có hoạt ảnh"
        else:
            banner_info = "Không có banner"
        embed.add_field(name="🎨 Banner", value=banner_info, inline=True)

        # Accent color
        if fetched_user.accent_color:
            embed.add_field(name="🌈 Màu chủ đạo", value=f"`{str(fetched_user.accent_color)}`", inline=True)

        # Set avatar as thumbnail
        embed.set_thumbnail(url=target_user.display_avatar.url)

        # Set banner as image if available
        if fetched_user.banner:
            embed.set_image(url=fetched_user.banner.url)

        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.slash_command(name="avatar-history", description="Xem lịch sử avatar của người dùng (giả lập)")
    async def avatar_history(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        user: Optional[disnake.User] = None
    ):
        """Display a simulated avatar history (for demonstration)."""
        target_user = user or interaction.author

        embed = disnake.Embed(
            title=f"📚 Lịch sử Avatar - {target_user.display_name}",
            description="*Tính năng này đang trong giai đoạn phát triển. Hiện tại chỉ hiển thị avatar hiện tại.*",
            color=0x7289da,
            timestamp=datetime.now()
        )

        # Current avatar
        embed.add_field(
            name="🔄 Avatar hiện tại",
            value=f"[Xem avatar]({target_user.display_avatar.url})\n*Cập nhật: Hiện tại*",
            inline=False
        )

        # Note about future features
        embed.add_field(
            name="🚧 Tính năng tương lai",
            value="• Lưu trữ lịch sử avatar\n• Thông báo khi thay đổi avatar\n• So sánh avatar cũ và mới",
            inline=False
        )

        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)


def setup(bot: ClientUser):
    bot.add_cog(Avatar(bot))

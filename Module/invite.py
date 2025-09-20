import disnake
from disnake.ext import commands
from datetime import datetime
from typing import Optional
from utils.ClientUser import ClientUser


class InviteView(disnake.ui.View):
    def __init__(self, bot: ClientUser, user: disnake.User):
        super().__init__(timeout=300)
        self.bot = bot
        self.user = user

        # Generate different invite links with different permissions
        self.full_permissions = disnake.Permissions(
            administrator=True
        )

        self.recommended_permissions = disnake.Permissions(
            manage_channels=True,
            manage_roles=True,
            manage_messages=True,
            embed_links=True,
            attach_files=True,
            read_message_history=True,
            use_external_emojis=True,
            add_reactions=True,
            connect=True,
            speak=True,
            use_voice_activation=True,
            priority_speaker=True,
            moderate_members=True,
            kick_members=True,
            ban_members=True,
            send_messages=True,
            view_channel=True
        )

        self.minimal_permissions = disnake.Permissions(
            send_messages=True,
            embed_links=True,
            connect=True,
            speak=True,
            use_voice_activation=True,
            view_channel=True
        )

        # Add buttons with invite links
        self.add_item(disnake.ui.Button(
            label="🔗 Invite với quyền đầy đủ",
            url=disnake.utils.oauth_url(
                bot.user.id,
                permissions=self.full_permissions,
                scopes=('bot', 'applications.commands')
            ),
            style=disnake.ButtonStyle.link
        ))

        self.add_item(disnake.ui.Button(
            label="⭐ Invite khuyến nghị",
            url=disnake.utils.oauth_url(
                bot.user.id,
                permissions=self.recommended_permissions,
                scopes=('bot', 'applications.commands')
            ),
            style=disnake.ButtonStyle.link
        ))

        self.add_item(disnake.ui.Button(
            label="🔒 Invite quyền tối thiểu",
            url=disnake.utils.oauth_url(
                bot.user.id,
                permissions=self.minimal_permissions,
                scopes=('bot', 'applications.commands')
            ),
            style=disnake.ButtonStyle.link
        ))

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Chỉ người dùng lệnh mới có thể sử dụng!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for item in self.children:
            if hasattr(item, 'disabled'):
                item.disabled = True

    @disnake.ui.button(label="📊 Thống kê Bot", style=disnake.ButtonStyle.secondary, row=1)
    async def stats_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="📊 Thống kê Bot",
            color=0x00ff88,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="🏠 Servers",
            value=f"`{len(self.bot.guilds)}`",
            inline=True
        )

        embed.add_field(
            name="👥 Users",
            value=f"`{len(self.bot.users)}`",
            inline=True
        )

        embed.add_field(
            name="🏓 Latency",
            value=f"`{round(self.bot.latency * 1000)}ms`",
            inline=True
        )

        # Calculate uptime
        if hasattr(self.bot, 'uptime'):
            uptime_seconds = int((datetime.now() - self.bot.uptime).total_seconds())
            days = uptime_seconds // 86400
            hours = (uptime_seconds % 86400) // 3600
            minutes = (uptime_seconds % 3600) // 60

            uptime_str = f"{days}d {hours}h {minutes}m"
        else:
            uptime_str = "Unknown"

        embed.add_field(
            name="⏰ Uptime",
            value=f"`{uptime_str}`",
            inline=True
        )

        embed.add_field(
            name="📝 Commands",
            value=f"`{len(self.bot.slash_commands)}`",
            inline=True
        )

        embed.add_field(
            name="🎵 Music Nodes",
            value=f"`{len(getattr(self.bot, 'available_nodes', []))}`",
            inline=True
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Bot ID: {self.bot.user.id}",
            icon_url=self.bot.user.display_avatar.url
        )

        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="🔙 Quay lại", style=disnake.ButtonStyle.primary, row=1)
    async def back_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = self.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="❌ Đóng", style=disnake.ButtonStyle.danger, row=1)
    async def close_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        embed = disnake.Embed(
            title="✅ Menu đã đóng",
            description="Cảm ơn bạn đã quan tâm đến bot! Sử dụng `/invite` để mở lại menu.",
            color=0x00ff00
        )
        await interaction.response.edit_message(embed=embed, view=None)

    def create_main_embed(self) -> disnake.Embed:
        """Create the main invite embed."""
        embed = disnake.Embed(
            title="🤖 Mời Hatsune Miku Bot vào Server!",
            description="Chọn loại invite phù hợp với nhu cầu của bạn:",
            color=0x7289da,
            timestamp=datetime.now()
        )

        # Add permission explanations
        embed.add_field(
            name="🔗 Quyền đầy đủ (Administrator)",
            value="""
            ✅ **Tất cả quyền** - Bot có thể làm mọi thứ
            ✅ **Dễ dàng setup** - Không cần cấu hình thêm
            ⚠️ **Rủi ro cao** - Cần tin tưởng bot hoàn toàn
            """,
            inline=False
        )

        embed.add_field(
            name="⭐ Quyền khuyến nghị (Recommended)",
            value="""
            ✅ **Đủ chức năng** - Tất cả tính năng hoạt động
            ✅ **An toàn** - Chỉ quyền cần thiết
            ✅ **Khuyến nghị** - Lựa chọn tốt nhất
            """,
            inline=False
        )

        embed.add_field(
            name="🔒 Quyền tối thiểu (Minimal)",
            value="""
            ✅ **An toàn nhất** - Quyền cơ bản
            ⚠️ **Hạn chế** - Một số tính năng không hoạt động
            ⚠️ **Cần setup** - Phải cấp quyền thủ công sau
            """,
            inline=False
        )

        # Add bot info
        embed.add_field(
            name="📋 Thông tin Bot",
            value=f"""
            **Tên:** {self.bot.user.name}
            **ID:** `{self.bot.user.id}`
            **Servers:** `{len(self.bot.guilds)}`
            **Users:** `{len(self.bot.users)}`
            """,
            inline=True
        )

        # Add features
        embed.add_field(
            name="🎵 Tính năng chính",
            value="""
            🎶 **Music Player** - Phát nhạc chất lượng cao
            🛡️ **Moderation** - Quản lý server hiệu quả
            ⚙️ **Utilities** - Công cụ hữu ích
            🎮 **Fun Commands** - Giải trí và tương tác
            """,
            inline=True
        )

        # Add support links
        embed.add_field(
            name="🔗 Liên kết hữu ích",
            value="""
            [Discord Server](https://discord.gg/mFnAZp49ZU)
            [Website](https://guns.lol/themiy2009)
            [Support](https://discord.gg/mFnAZp49ZU)
            """,
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Requested by {self.user.display_name} • Click buttons below to invite",
            icon_url=self.user.display_avatar.url
        )

        return embed


class Invite(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot: ClientUser = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="invite", description="Mời bot vào server của bạn với các tùy chọn quyền khác nhau")
    async def invite(self, interaction: disnake.ApplicationCommandInteraction):
        """Enhanced invite command with multiple permission options."""

        view = InviteView(self.bot, interaction.author)
        embed = view.create_main_embed()

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="botinfo", description="Thông tin chi tiết về bot")
    async def botinfo(self, interaction: disnake.ApplicationCommandInteraction):
        """Detailed bot information command."""

        embed = disnake.Embed(
            title="🤖 Thông tin Bot - Hatsune Miku",
            description="Bot nhạc và tiện ích đa chức năng cho Discord",
            color=0x00ff88,
            timestamp=datetime.now()
        )

        # Bot basic info
        embed.add_field(
            name="📋 Thông tin cơ bản",
            value=f"""
            **Tên:** {self.bot.user.name}
            **ID:** `{self.bot.user.id}`
            **Tag:** {self.bot.user.discriminator}
            **Created:** <t:{int(self.bot.user.created_at.timestamp())}:F>
            """,
            inline=True
        )

        # Statistics
        embed.add_field(
            name="📊 Thống kê",
            value=f"""
            **Servers:** `{len(self.bot.guilds)}`
            **Users:** `{len(self.bot.users)}`
            **Commands:** `{len(self.bot.slash_commands)}`
            **Latency:** `{round(self.bot.latency * 1000)}ms`
            """,
            inline=True
        )

        # Technical info
        embed.add_field(
            name="⚙️ Kỹ thuật",
            value=f"""
            **Python:** `{__import__('platform').python_version()}`
            **Disnake:** `{disnake.__version__}`
            **Shards:** `{self.bot.shard_count or 1}`
            **Prefix:** `/` (Slash Commands)
            """,
            inline=True
        )

        # Features
        embed.add_field(
            name="🎵 Tính năng Music",
            value="""
            🎶 **Multi-platform** - YouTube, Spotify, SoundCloud
            🔊 **High Quality** - Lossless audio streaming
            📱 **Queue System** - Playlist management
            🔄 **Loop & Shuffle** - Advanced playback
            🎚️ **Effects** - Nightcore, Bass boost
            """,
            inline=False
        )

        embed.add_field(
            name="🛡️ Tính năng Moderation",
            value="""
            ⏰ **Timeout System** - Modern Discord timeouts
            🚫 **Ban/Kick** - Member management
            🧹 **Message Purge** - Bulk delete messages
            🔐 **Permission Checks** - Role hierarchy respect
            📝 **Audit Logs** - Detailed action logging
            """,
            inline=False
        )

        embed.add_field(
            name="⚙️ Tính năng System",
            value="""
            📊 **Real-time Stats** - Performance monitoring
            🏓 **Ping Checker** - Latency testing
            💾 **System Info** - Server specifications
            🔧 **Admin Tools** - Bot management
            📋 **Help System** - Interactive documentation
            """,
            inline=False
        )

        # Developer info
        embed.add_field(
            name="👨‍💻 Developer",
            value="""
            **Creator:** <@1299777672905363569>
            **Support:** [Discord Server](https://discord.gg/mFnAZp49ZU)
            **Website:** [Profile](https://guns.lol/themiy2009)
            """,
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Requested by {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        # Add invite button
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(
            label="🔗 Invite Bot",
            url=disnake.utils.oauth_url(
                self.bot.user.id,
                permissions=disnake.Permissions(
                    manage_channels=True,
                    manage_roles=True,
                    manage_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True,
                    use_external_emojis=True,
                    add_reactions=True,
                    connect=True,
                    speak=True,
                    use_voice_activation=True,
                    priority_speaker=True,
                    moderate_members=True,
                    kick_members=True,
                    ban_members=True,
                    send_messages=True,
                    view_channel=True
                ),
                scopes=('bot', 'applications.commands')
            ),
            style=disnake.ButtonStyle.link
        ))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.slash_command(name="support", description="Thông tin hỗ trợ và liên hệ")
    async def support(self, interaction: disnake.ApplicationCommandInteraction):
        """Support and contact information."""

        embed = disnake.Embed(
            title="🆘 Hỗ trợ & Liên hệ",
            description="Cần trợ giúp? Chúng tôi luôn sẵn sàng hỗ trợ bạn!",
            color=0xff6b6b,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="💬 Discord Server",
            value="""
            **Main Server:** [Join Here](https://discord.gg/mFnAZp49ZU)
            📞 **Voice Support:** Available
            💬 **Text Support:** 24/7
            🎫 **Ticket System:** Yes
            """,
            inline=False
        )

        embed.add_field(
            name="📧 Liên hệ trực tiếp",
            value="""
            **Developer:** <@1299777672905363569>
            **Website:** [guns.lol/themiy2009](https://guns.lol/themiy2009)
            **Response Time:** Usually within 24h
            """,
            inline=False
        )

        embed.add_field(
            name="🐛 Báo lỗi",
            value="""
            1️⃣ Join Discord server
            2️⃣ Tạo ticket hoặc post trong #bug-reports
            3️⃣ Mô tả chi tiết lỗi và cách tái hiện
            4️⃣ Attach screenshots nếu có thể
            """,
            inline=False
        )

        embed.add_field(
            name="💡 Đề xuất tính năng",
            value="""
            📝 **Feature Requests:** #suggestions channel
            🗳️ **Voting System:** Community votes
            ⭐ **Priority:** Based on popularity
            🚀 **Implementation:** Regular updates
            """,
            inline=False
        )

        embed.add_field(
            name="❓ FAQ",
            value="""
            **Q: Bot không phát nhạc?**
            A: Kiểm tra quyền Connect và Speak trong voice channel

            **Q: Lệnh không hoạt động?**
            A: Đảm bảo bot có quyền Send Messages và Use Slash Commands

            **Q: Bot bị lag?**
            A: Kiểm tra `/ping` và báo cáo nếu >500ms
            """,
            inline=False
        )

        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1403540948331532369.png")
        embed.set_footer(
            text="Chúng tôi luôn lắng nghe và cải thiện!",
            icon_url=self.bot.user.display_avatar.url
        )

        # Add support buttons
        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(
            label="💬 Discord Server",
            url="https://discord.gg/mFnAZp49ZU",
            style=disnake.ButtonStyle.link
        ))
        view.add_item(disnake.ui.Button(
            label="🌐 Website",
            url="https://guns.lol/themiy2009",
            style=disnake.ButtonStyle.link
        ))

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # Legacy command support
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="invite", description="Mời bot vào server")
    async def invite_legacy(self, ctx: commands.Context):
        """Legacy prefix command support."""
        if ctx.author.bot:
            return

        view = InviteView(self.bot, ctx.author)
        embed = view.create_main_embed()

        await ctx.send(embed=embed, view=view)

def setup(bot: ClientUser):
    bot.add_cog(Invite(bot))
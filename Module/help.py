"""
🤖 Hatsune Miku Bot - Help System Module

This module provides a comprehensive help system with:
- Interactive UI with buttons and dropdown menus
- Categorized command listings with detailed information
- Search functionality for commands
- Beautiful embeds with proper formatting
- User-friendly navigation and feedback system

Author: Hatsune Miku Bot Team
Version: 2.0.0
Last Updated: 2024-12-26
"""

import disnake
from disnake.ext import commands
from datetime import datetime
from typing import Dict, List, Optional, Union
import asyncio
import re
from utils.ClientUser import ClientUser

# Try to import SelectOption with fallback
try:
    from disnake import SelectOption
except ImportError:
    SelectOption = None

# Module Configuration
MODULE_INFO = {
    "name": "Help System",
    "version": "2.0.0",
    "author": "Hatsune Miku Bot Team",
    "description": "Comprehensive help system with interactive UI",
    "last_updated": "2024-12-26"
}

# UI Configuration
UI_CONFIG = {
    "timeout": 300,
    "max_commands_per_field": 5,
    "max_search_results": 10,
    "min_keyword_length": 2,
    "embed_colors": {
        "primary": 0x00ff88,
        "secondary": 0x7289da,
        "success": 0x00ff00,
        "warning": 0xff9900,
        "error": 0xff0000
    }
}

# Bot Links and Information
BOT_LINKS = {
    "discord_server": "https://discord.gg/mFnAZp49ZU",
    "website": "https://guns.lol/themiy2009",
    "invite": "https://discord.com/api/oauth2/authorize",
    "support": "https://discord.gg/mFnAZp49ZU"
}


# Helper function to create command info
def create_command(desc: str, usage: str, example: str, perms: str = "None") -> Dict[str, str]:
    """Create a standardized command info dictionary."""
    return {
        "description": desc,
        "usage": usage,
        "example": example,
        "permissions": perms
    }

# Command categories with detailed information (optimized structure)
COMMAND_CATEGORIES = {
    "🛡️ Moderation": {
        "description": "Các lệnh quản lý và kiểm duyệt server với tính năng nâng cao",
        "color": 0xff6b6b,
        "emoji": "🛡️",
        "commands": {
            "mute": create_command(
                "Timeout thành viên với thời gian tùy chỉnh",
                "/mute <member> <duration> [reason]",
                "/mute @user 1h30m Spam tin nhắn",
                "Moderate Members"
            ),
            "unmute": create_command(
                "Bỏ timeout cho thành viên",
                "/unmute <member> [reason]",
                "/unmute @user Đã hết thời gian phạt",
                "Moderate Members"
            ),
            "kick": create_command(
                "Kick thành viên ra khỏi server",
                "/kick <member> [reason]",
                "/kick @user Vi phạm quy định",
                "Kick Members"
            ),
            "ban": create_command(
                "Ban thành viên với tùy chọn xóa tin nhắn",
                "/ban <member> [delete_days] [reason]",
                "/ban @user 7 Spam nghiêm trọng",
                "Ban Members"
            ),
            "unban": create_command(
                "Unban user khỏi server",
                "/unban <user_id> [reason]",
                "/unban 123456789 Đã hết thời gian phạt",
                "Ban Members"
            ),
            "clear": create_command(
                "Xóa tin nhắn với bộ lọc thông minh",
                "/clear <amount> [filters...]",
                "/clear 50 user:@spam_user contains:spam",
                "Manage Messages"
            ),
            "purge-bots": create_command(
                "Xóa tin nhắn từ bot",
                "/purge-bots <amount>",
                "/purge-bots 30",
                "Manage Messages"
            ),
            "purge-embeds": create_command(
                "Xóa tin nhắn có embeds",
                "/purge-embeds <amount>",
                "/purge-embeds 20",
                "Manage Messages"
            ),
            "purge-files": create_command(
                "Xóa tin nhắn có file đính kèm",
                "/purge-files <amount>",
                "/purge-files 25",
                "Manage Messages"
            ),
            "purge-regex": create_command(
                "Xóa tin nhắn khớp regex pattern",
                "/purge-regex <pattern> <amount>",
                r"/purge-regex \d{4,} 50",
                "Manage Messages"
            )
        }
    },
    "🎫 Ticket": {
        "description": "Hệ thống ticket hỗ trợ chuyên nghiệp với giao diện modal đẹp như Discord",
        "color": 0x5865f2,
        "emoji": "🎫",
        "features": [
            "🎨 Modal forms đẹp như Discord với validation thông minh",
            "⚙️ Config panel với 4 button: Basic, Appearance, Advanced, Preview",
            "🖼️ Tùy chỉnh title, description, color, image, button label",
            "🔧 Setup category, support roles, auto-close timer",
            "👥 Role-based permissions và user limits",
            "📊 Debug tools và real-time preview"
        ],
        "commands": {
            "ticket setup": create_command(
                "Setup hệ thống ticket (category, roles)",
                "/ticket setup <type> <value>",
                "/ticket setup category #tickets",
                "Administrator"
            ),
            "ticket panel": create_command(
                "Gửi panel ticket với giao diện đã config",
                "/ticket panel",
                "/ticket panel",
                "Administrator"
            ),
            "ticket config": create_command(
                "Config giao diện với modal forms đẹp",
                "/ticket config",
                "/ticket config",
                "Administrator"
            ),
            "ticket close": create_command(
                "Đóng ticket hiện tại với xác nhận",
                "/ticket close",
                "/ticket close"
            ),
            "ticket reopen": create_command(
                "Mở lại ticket đã đóng",
                "/ticket reopen",
                "/ticket reopen",
                "Support Role"
            ),
            "ticket add": create_command(
                "Thêm user vào ticket",
                "/ticket add <user>",
                "/ticket add @user",
                "Support Role"
            ),
            "ticket remove": create_command(
                "Xóa user khỏi ticket",
                "/ticket remove <user>",
                "/ticket remove @user",
                "Support Role"
            ),
            "ticket debug": create_command(
                "Debug config hiện tại (JSON format)",
                "/ticket debug",
                "/ticket debug",
                "Administrator"
            )
        }
    },
    "🎵 Music": {
        "description": "Hệ thống phát nhạc chuyên nghiệp với player controller đẹp và tính năng nâng cao",
        "color": 0x9b59b6,
        "emoji": "🎵",
        "features": [
            "🎛️ Interactive Controller với progress bar thời gian thực",
            "🎵 5 Buttons tương tác: ⏮️ ⏸️ ⏹️ ⏭️ 🎵",
            "🔧 Select Menu với tùy chọn nâng cao",
            "🎨 Professional UI với màu sắc động",
            "🔊 Audio filters và equalizer",
            "🎼 Multi-platform: YouTube, Spotify, SoundCloud"
        ],
        "commands": {
            "play": create_command(
                "Phát nhạc từ YouTube/Spotify/SoundCloud với controller đẹp",
                "/play <song>",
                "/play Hatsune Miku - Senbonzakura",
                "Connect to Voice"
            ),
            "pause": create_command("Tạm dừng bài hát", "/pause", "/pause", "Connect to Voice"),
            "resume": create_command("Tiếp tục phát nhạc", "/resume", "/resume", "Connect to Voice"),
            "skip": create_command("Bỏ qua bài hiện tại", "/skip", "/skip", "Connect to Voice"),
            "stop": create_command(
                "Dừng nhạc với thông báo đẹp và hướng dẫn",
                "/stop",
                "/stop",
                "Connect to Voice"
            ),
            "queue": create_command("Hiển thị danh sách nhạc chờ", "/queue", "/queue"),
            "remove": create_command("Xóa bài khỏi queue", "/remove <position>", "/remove 3", "Connect to Voice"),
            "clear-queue": create_command("Xóa toàn bộ queue", "/clear-queue", "/clear-queue", "Connect to Voice"),
            "move": create_command("Di chuyển bài trong queue", "/move <from> <to>", "/move 3 1", "Connect to Voice"),
            "skipto": create_command("Bỏ qua đến bài cụ thể", "/skipto <position>", "/skipto 5", "Connect to Voice"),
            "volume": create_command("Điều chỉnh âm lượng (0-100)", "/volume <level>", "/volume 50", "Connect to Voice"),
            "loop": create_command("Chế độ lặp lại", "/loop [mode]", "/loop track", "Connect to Voice"),
            "shuffle": create_command("Trộn ngẫu nhiên queue", "/shuffle", "/shuffle", "Connect to Voice"),
            "autoplay": create_command("Tự động phát nhạc liên quan", "/autoplay", "/autoplay", "Connect to Voice"),
            "search": create_command("Tìm kiếm và chọn nhạc", "/search <query>", "/search Hatsune Miku", "Connect to Voice"),
            "nowplaying": create_command("Hiển thị bài đang phát", "/nowplaying", "/nowplaying"),
            "lyrics": create_command("Hiển thị lời bài hát", "/lyrics [song]", "/lyrics Senbonzakura"),
            "seek": create_command("Tua đến thời điểm cụ thể", "/seek <time>", "/seek 1:30", "Connect to Voice"),
            "replay": create_command("Phát lại từ đầu", "/replay", "/replay", "Connect to Voice"),
            "previous": create_command("Quay lại bài trước", "/previous", "/previous", "Connect to Voice"),
            "filters": create_command("Menu bộ lọc âm thanh", "/filters", "/filters", "Connect to Voice"),
            "equalizer": create_command("Điều chỉnh equalizer", "/equalizer [preset]", "/equalizer bass", "Connect to Voice"),
            "bassboost": create_command("Hiệu ứng bass boost", "/bassboost [level]", "/bassboost 3", "Connect to Voice"),
            "nightcore": create_command("Hiệu ứng nightcore", "/nightcore", "/nightcore", "Connect to Voice"),
            "speed": create_command("Thay đổi tốc độ phát", "/speed <rate>", "/speed 1.25", "Connect to Voice"),
            "pitch": create_command("Thay đổi cao độ âm", "/pitch <level>", "/pitch 1.2", "Connect to Voice"),
            "reset-filters": create_command("Reset tất cả bộ lọc", "/reset-filters", "/reset-filters", "Connect to Voice"),
            "join": create_command("Bot join voice channel", "/join [channel]", "/join General", "Connect to Voice"),
            "leave": create_command("Bot rời voice channel", "/leave", "/leave", "Connect to Voice"),
            "247": create_command("Bot ở lại 24/7", "/247", "/247", "Manage Guild"),
            "musiccontrol": create_command("Bảng điều khiển đầy đủ", "/musiccontrol", "/musiccontrol", "Connect to Voice"),
            "musicmenu": create_command("Menu tương tác với dropdown", "/musicmenu", "/musicmenu", "Connect to Voice")
        }
    },
    "🎣 Fishing Game": {
        "description": "Trò chơi câu cá tương tác với hệ thống kinh tế hoàn chỉnh",
        "color": 0x1abc9c,
        "emoji": "🎣",
        "features": [
            "🐟 8 loại cá từ Common đến Legendary",
            "🎣 5 cấp độ cần câu để nâng cấp",
            "💰 Hệ thống kinh tế với mua bán",
            "🎯 Quest system và Leaderboard",
            "🎁 Daily rewards và achievements"
        ],
        "commands": {
            "fish": create_command("Câu cá để kiếm tiền (cooldown 30s)", "/fish", "/fish"),
            "inventory": create_command("Xem túi đồ và thống kê", "/inventory", "/inventory"),
            "fishmarket": create_command("Cửa hàng - bán cá và nâng cấp", "/fishmarket", "/fishmarket"),
            "dailyfish": create_command("Phần thưởng hàng ngày", "/dailyfish", "/dailyfish"),
            "fishquest": create_command("Nhiệm vụ câu cá", "/fishquest", "/fishquest"),
            "fishhelp": create_command("Hướng dẫn chi tiết game", "/fishhelp", "/fishhelp")
        }
    },
    "⚙️ System": {
        "description": "Các lệnh hệ thống và thông tin bot với giao diện chuyên nghiệp",
        "color": 0x3498db,
        "emoji": "⚙️",
        "features": [
            "📊 Thống kê chi tiết bot",
            "🔗 Menu invite với permissions",
            "📞 Hỗ trợ và liên hệ",
            "🔍 Tìm kiếm lệnh thông minh",
            "📋 Help system tương tác"
        ],
        "commands": {
            "ping": create_command("Kiểm tra độ trễ bot", "/ping", "/ping"),
            "about": create_command("Thông tin chi tiết về bot", "/about", "/about"),
            "status": create_command("Trạng thái chi tiết bot", "/status", "/status"),
            "invite": create_command("Menu mời bot với quyền", "/invite", "/invite"),
            "botinfo": create_command("Thông tin kỹ thuật bot", "/botinfo", "/botinfo"),
            "support": create_command("Hỗ trợ và liên hệ", "/support", "/support"),
            "help": create_command("Menu trợ giúp tương tác", "/help [category]", "/help music"),
            "commands": create_command("Danh sách tất cả lệnh", "/commands", "/commands"),
            "command": create_command("Chi tiết lệnh cụ thể", "/command <name>", "/command play"),
            "search-command": create_command("Tìm kiếm lệnh", "/search-command <keyword>", "/search-command music")
        }
    },
    "🎉 Giveaway": {
        "description": "Hệ thống giveaway chuyên nghiệp với tự động hóa hoàn toàn",
        "color": 0xFF69B4,
        "emoji": "🎉",
        "features": [
            "🎁 Beautiful giveaway embeds với countdown timer",
            "🎉 Interactive join button với real-time counter",
            "⏰ Auto-end system và winner selection",
            "📊 Management commands với permissions",
            "💾 Persistent data và crash recovery"
        ],
        "commands": {
            "giveaway": create_command(
                "Tạo giveaway với giao diện đẹp và auto-end",
                "/giveaway <prize> <duration> [winners] [channel]",
                "/giveaway 'Discord Nitro' 1h 2 #giveaway",
                "Manage Guild"
            ),
            "giveaway-list": create_command("Danh sách giveaway đang diễn ra", "/giveaway-list", "/giveaway-list"),
            "giveaway-end": create_command("Kết thúc giveaway sớm", "/giveaway-end <id>", "/giveaway-end 123456", "Manage Guild"),
            "giveaway-reroll": create_command("Quay lại người thắng mới", "/giveaway-reroll <id>", "/giveaway-reroll 123456", "Manage Guild"),
            "giveaway-info": create_command("Thông tin chi tiết giveaway", "/giveaway-info <id>", "/giveaway-info 123456")
        }
    },
    "🚀 Boost Tracker": {
        "description": "Hệ thống theo dõi Server Boost tự động với thông báo đẹp",
        "color": 0xFF73FA,
        "emoji": "🚀",
        "features": [
            "🚀 Auto-detect boost và ngừng boost",
            "📊 Beautiful notifications với tier progress",
            "🎉 Interactive buttons: Cảm ơn | Stats | Rewards",
            "📋 Boost history với thời gian chi tiết",
            "🎯 Tier tracking và requirements"
        ],
        "commands": {
            "boost-setup": create_command("Setup thông báo boost", "/boost-setup <channel>", "/boost-setup #boost", "Manage Guild"),
            "boost-disable": create_command("Tắt hệ thống boost", "/boost-disable", "/boost-disable", "Manage Guild"),
            "boost-stats": create_command("Thống kê boost với tier", "/boost-stats", "/boost-stats"),
            "boost-history": create_command("Lịch sử boost server", "/boost-history", "/boost-history", "Manage Guild"),
            "boost-test": create_command("Test thông báo boost", "/boost-test", "/boost-test", "Administrator")
        }
    },
    "🎮 Fun & Games": {
        "description": "Các lệnh giải trí và game tương tác vui nhộn",
        "color": 0xf39c12,
        "emoji": "🎮",
        "commands": {
            "8ball": create_command("Hỏi quả cầu thần số 8", "/8ball <question>", "/8ball Hôm nay có may mắn không?"),
            "dice": create_command("Tung xúc xắc", "/dice [sides] [count]", "/dice 6 2"),
            "flip": create_command("Tung đồng xu", "/flip", "/flip"),
            "choose": create_command("Chọn ngẫu nhiên", "/choose <choices>", "/choose Pizza, Burger, Phở"),
            "joke": create_command("Chuyện cười lập trình", "/joke", "/joke"),
            "love": create_command("Tính độ tương hợp", "/love <person1> [person2]", "/love @crush"),
            "rate": create_command("Đánh giá 0-10 sao", "/rate <thing>", "/rate Discord Bot này"),
            "sfw": create_command("Ảnh anime an toàn", "/sfw <category>", "/sfw neko"),
            "nsfw": create_command("Ảnh NSFW (18+)", "/nsfw <category>", "/nsfw waifu", "NSFW Channel")
        }
    },
    "🎭 Emoji Management": {
        "description": "Quản lý emoji server chuyên nghiệp",
        "color": 0xe67e22,
        "emoji": "🎭",
        "commands": {
            "emoji-create": create_command("Tạo emoji từ URL", "/emoji-create <url> [name]", "/emoji-create https://... miku", "Manage Emojis"),
            "emoji-add": create_command("Copy emoji từ server khác", "/emoji-add <emojis>", "/emoji-add :custom_emoji:", "Manage Emojis"),
            "emoji-delete": create_command("Xóa emoji", "/emoji-delete <emoji>", "/emoji-delete custom_emoji", "Manage Emojis"),
            "emoji-list": create_command("Danh sách emoji server", "/emoji-list", "/emoji-list"),
            "emoji-info": create_command("Thông tin emoji", "/emoji-info <emoji>", "/emoji-info custom_emoji")
        }
    },
    "🖼️ Avatar & User Info": {
        "description": "Avatar, banner và thông tin người dùng chi tiết",
        "color": 0x7289da,
        "emoji": "🖼️",
        "commands": {
            "avatar": create_command("Xem avatar với nhiều định dạng", "/avatar [user]", "/avatar @user"),
            "server-avatar": create_command("Avatar riêng trong server", "/server-avatar [member]", "/server-avatar @member"),
            "banner": create_command("Xem banner profile", "/banner [user]", "/banner @user"),
            "user-info": create_command("Thông tin chi tiết user", "/user-info [user]", "/user-info @user")
        }
    },
    "🏰 Server Info": {
        "description": "Thông tin chi tiết về server",
        "color": 0x3498db,
        "emoji": "🏰",
        "commands": {
            "server-info": create_command("Thông tin server đầy đủ", "/server-info", "/server-info"),
            "server-icon": create_command("Icon server nhiều định dạng", "/server-icon", "/server-icon"),
            "server-banner": create_command("Banner server", "/server-banner", "/server-banner"),
            "member-count": create_command("Thống kê thành viên", "/member-count", "/member-count")
        }
    },

    "🔧 Admin": {
        "description": "Các lệnh dành cho admin bot",
        "color": 0xe74c3c,
        "emoji": "🔧",
        "commands": {
            "shutdown": create_command("Tắt bot", "/shutdown", "/shutdown", "Bot Owner"),
            "reload": create_command("Reload module", "/reload <module>", "/reload music", "Bot Owner"),
            "eval": create_command("Thực thi Python code", "/eval <code>", "/eval print('Hello')", "Bot Owner"),
            "sql": create_command("Thực thi SQL query", "/sql <query>", "/sql SELECT * FROM users", "Bot Owner"),
            "logs": create_command("Xem logs bot", "/logs [lines]", "/logs 50", "Bot Owner")
        }
    }
}

# Helper functions for embed creation
def create_embed(title: str, description: str, color: int = UI_CONFIG["embed_colors"]["primary"]) -> disnake.Embed:
    """Create a standardized embed with consistent styling."""
    embed = disnake.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=datetime.now()
    )
    return embed

def format_command_list(commands: Dict[str, Dict], max_per_field: int = 5) -> List[str]:
    """Format command list for embed fields."""
    formatted = []
    for cmd_name, cmd_info in commands.items():
        formatted.append(f"**`/{cmd_name}`** - {cmd_info['description'][:50]}...")
    return formatted

def get_category_stats() -> Dict[str, int]:
    """Get statistics about command categories."""
    stats = {}
    for category, info in COMMAND_CATEGORIES.items():
        stats[category] = len(info['commands'])
    return stats


class CategoryDropdown(disnake.ui.Select):
    """Dropdown menu for category selection with auto-generated options."""

    def __init__(self, view_instance):
        self.view_instance = view_instance

        # Auto-generate options from COMMAND_CATEGORIES
        options = []
        if SelectOption:
            # Add main menu option
            options.append(SelectOption(
                label="🏠 Main Menu",
                description="Quay về menu chính",
                value="main",
                emoji="🏠"
            ))

            # Add category options
            for category_name, category_info in COMMAND_CATEGORIES.items():
                emoji = category_info.get("emoji", "📁")
                short_name = category_name.split(" ", 1)[1] if " " in category_name else category_name
                description = category_info["description"][:50] + "..." if len(category_info["description"]) > 50 else category_info["description"]

                options.append(SelectOption(
                    label=short_name,
                    description=description,
                    value=category_name,
                    emoji=emoji
                ))

        super().__init__(
            placeholder="🔽 Chọn danh mục để xem...",
            options=options if options else [],
            disabled=not bool(SelectOption)  # Disable if SelectOption not available
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.author != self.view_instance.user:
            await interaction.response.send_message("❌ Bạn không thể sử dụng menu này!", ephemeral=True)
            return

        selected_value = self.values[0]

        if selected_value == "main":
            self.view_instance.current_page = "main"
            embed = self.view_instance.create_main_embed()
        else:
            self.view_instance.current_page = selected_value
            embed = self.view_instance.create_category_embed(selected_value)

        await interaction.response.edit_message(embed=embed, view=self.view_instance)


class HelpView(disnake.ui.View):
    """Enhanced help view with interactive navigation and beautiful UI."""

    def __init__(self, bot: ClientUser, user: disnake.User):
        super().__init__(timeout=UI_CONFIG["timeout"])
        self.bot = bot
        self.user = user
        self.current_page = "main"

        # Add dropdown menu if SelectOption is available
        if SelectOption:
            self.add_item(CategoryDropdown(self))

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> bool:
        """Check if user can interact with this view."""
        if interaction.user.id != self.user.id:
            await interaction.response.send_message("❌ Chỉ người dùng lệnh mới có thể sử dụng!", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        """Disable all components when view times out."""
        for item in self.children:
            item.disabled = True

    def create_main_embed(self) -> disnake.Embed:
        """Create the main help embed with category overview."""
        embed = create_embed(
            "🤖 Hatsune Miku Bot - Menu Trợ Giúp",
            f"""
            **Chào mừng đến với {MODULE_INFO['name']} v{MODULE_INFO['version']}!**

            � **Tính năng nổi bật:**
            🎫 **Ticket System** - Modal forms đẹp như Discord với config panel
            🎵 **Music System** - Player controller đẹp với 25+ lệnh
            🎣 **Fishing Game** - 8 loại cá, 5 cấp cần câu, hệ thống kinh tế
            🎉 **Giveaway System** - Tự động hóa hoàn toàn với UI đẹp
            🚀 **Boost Tracker** - Theo dõi boost với thông báo chuyên nghiệp
            🛡️ **Moderation** - Quản lý server với bộ lọc nâng cao

            📊 **Thống kê:** {len(self.bot.guilds)} servers • {len(self.bot.users)} users • {sum(len(cat['commands']) for cat in COMMAND_CATEGORIES.values())} commands
            """
        )

        # Add category overview
        categories_text = ""
        for category, info in COMMAND_CATEGORIES.items():
            command_count = len(info['commands'])
            emoji = info.get('emoji', '📁')
            categories_text += f"{emoji} **{category}** - `{command_count} lệnh`\n"

        embed.add_field(
            name="📋 Danh mục lệnh",
            value=categories_text,
            inline=True
        )

        # Add quick actions
        embed.add_field(
            name="🎯 Quick Actions",
            value="""
            🔍 `/search-command <keyword>` - Tìm lệnh
            📋 `/commands` - Danh sách tất cả lệnh
            📖 `/command <name>` - Chi tiết lệnh
            🎵 `/play <song>` - Phát nhạc ngay
            """,
            inline=True
        )

        # Add links
        embed.add_field(
            name="🔗 Liên kết",
            value=f"""
            [Discord Server]({BOT_LINKS['discord_server']})
            [Website]({BOT_LINKS['website']})
            [Invite Bot]({BOT_LINKS['invite']})
            [Support]({BOT_LINKS['support']})
            """,
            inline=True
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text=f"Requested by {self.user.display_name} • {MODULE_INFO['version']} • Use dropdown to navigate",
            icon_url=self.user.display_avatar.url
        )

        return embed

    def create_category_embed(self, category_name: str) -> disnake.Embed:
        """Create embed for specific category with enhanced formatting."""
        if category_name not in COMMAND_CATEGORIES:
            return self.create_main_embed()

        category_info = COMMAND_CATEGORIES[category_name]

        embed = create_embed(
            f"{category_name} Commands",
            category_info['description'],
            category_info['color']
        )

        # Add features if available
        if 'features' in category_info:
            features_text = "\n".join(category_info['features'])
            embed.add_field(
                name="✨ Tính năng nổi bật",
                value=features_text,
                inline=False
            )

        # Add commands in organized chunks
        commands = category_info['commands']
        command_items = list(commands.items())

        # Split commands into chunks for better readability
        chunk_size = UI_CONFIG["max_commands_per_field"]
        for i in range(0, len(command_items), chunk_size):
            chunk = command_items[i:i+chunk_size]
            field_value = ""

            for cmd_name, cmd_info in chunk:
                field_value += f"**`/{cmd_name}`**\n"
                field_value += f"└ {cmd_info['description']}\n"
                field_value += f"└ **Usage:** `{cmd_info['usage']}`\n"
                if cmd_info['permissions'] != "None":
                    field_value += f"└ **Permissions:** `{cmd_info['permissions']}`\n"
                field_value += "\n"

            field_name = f"Commands {i//chunk_size + 1}" if len(command_items) > chunk_size else "Commands"
            embed.add_field(
                name=field_name,
                value=field_value,
                inline=False
            )

        embed.set_footer(
            text=f"Page {category_name} • {len(commands)} commands • Use dropdown to navigate",
            icon_url=self.bot.user.display_avatar.url
        )

        return embed

    # Optimized button methods with dynamic category handling
    def create_button_method(self, category_key: str):
        """Create a button method for a specific category."""
        async def button_callback(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
            self.current_page = category_key
            embed = self.create_category_embed(category_key) if category_key != "main" else self.create_main_embed()
            await interaction.response.edit_message(embed=embed, view=self)
        return button_callback

    # Main navigation buttons
    @disnake.ui.button(label="🏠 Home", style=disnake.ButtonStyle.primary, row=0)
    async def home_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "main"
        embed = self.create_main_embed()
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="🛡️ Moderation", style=disnake.ButtonStyle.secondary, row=0)
    async def moderation_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "🛡️ Moderation"
        embed = self.create_category_embed("🛡️ Moderation")
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="🎵 Music", style=disnake.ButtonStyle.secondary, row=0)
    async def music_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "🎵 Music"
        embed = self.create_category_embed("🎵 Music")
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="⚙️ System", style=disnake.ButtonStyle.secondary, row=0)
    async def system_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "⚙️ System"
        embed = self.create_category_embed("⚙️ System")
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="🎮 Fun", style=disnake.ButtonStyle.secondary, row=0)
    async def fun_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "🎮 Fun & Games"
        embed = self.create_category_embed("🎮 Fun & Games")
        await interaction.response.edit_message(embed=embed, view=self)

    # Secondary buttons
    @disnake.ui.button(label="🎣 Fishing", style=disnake.ButtonStyle.secondary, row=1)
    async def fishing_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "🎣 Fishing Game"
        embed = self.create_category_embed("🎣 Fishing Game")
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="🎉 Giveaway", style=disnake.ButtonStyle.secondary, row=1)
    async def giveaway_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "🎉 Giveaway"
        embed = self.create_category_embed("🎉 Giveaway")
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="🚀 Boost", style=disnake.ButtonStyle.secondary, row=1)
    async def boost_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "🚀 Boost Tracker"
        embed = self.create_category_embed("🚀 Boost Tracker")
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="🎫 Ticket", style=disnake.ButtonStyle.secondary, row=1)
    async def ticket_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.current_page = "🎫 Ticket"
        embed = self.create_category_embed("🎫 Ticket")
        await interaction.response.edit_message(embed=embed, view=self)

    @disnake.ui.button(label="📊 Stats", style=disnake.ButtonStyle.secondary, row=1)
    async def stats_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if interaction.author != self.user:
            await interaction.response.send_message("❌ Bạn không thể sử dụng menu này!", ephemeral=True)
            return

        # Quick stats embed
        total_commands = sum(len(cat['commands']) for cat in COMMAND_CATEGORIES.values())
        stats_embed = create_embed(
            "📊 Bot Statistics",
            f"""
            **Server Stats:**
            🏰 Servers: `{len(self.bot.guilds)}`
            👥 Users: `{len(self.bot.users)}`
            📡 Latency: `{round(self.bot.latency * 1000)}ms`

            **Command Stats:**
            📋 Total Commands: `{total_commands}`
            📂 Categories: `{len(COMMAND_CATEGORIES)}`

            **Module Info:**
            📦 Version: `{MODULE_INFO['version']}`
            👨‍💻 Author: `{MODULE_INFO['author']}`
            📅 Last Updated: `{MODULE_INFO['last_updated']}`
            """,
            UI_CONFIG["embed_colors"]["secondary"]
        )
        await interaction.response.send_message(embed=stats_embed, ephemeral=True)


class Help(commands.Cog):
    """Enhanced Help System Cog with interactive UI and comprehensive command information."""

    def __init__(self, bot: ClientUser):
        self.bot: ClientUser = bot

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="help", description="Hiển thị menu trợ giúp tương tác với tất cả lệnh của bot")
    async def help(self,
                   interaction: disnake.ApplicationCommandInteraction,
                   category: Optional[str] = commands.Param(
                       default=None,
                       description="Danh mục cụ thể để xem",
                       choices=["ticket", "moderation", "music", "fishing", "system", "fun", "avatar", "server", "emoji", "giveaway", "boost", "admin"]
                   )):
        """Enhanced help command with interactive navigation and beautiful UI."""

        # Create view and initial embed
        view = HelpView(self.bot, interaction.author)

        if category:
            # Map category choices to actual category names
            category_map = {
                "ticket": "🎫 Ticket",
                "moderation": "�️ Moderation",
                "music": "🎵 Music",
                "fishing": "🎣 Fishing Game",
                "system": "⚙️ System",
                "fun": "🎮 Fun & Games",
                "avatar": "🖼️ Avatar & User Info",
                "server": "🏰 Server Info",
                "emoji": "🎭 Emoji Management",
                "giveaway": "🎉 Giveaway",
                "boost": "🚀 Boost Tracker",
                "admin": "🔧 Admin"
            }

            if category in category_map:
                view.current_page = category_map[category]
                embed = view.create_category_embed(category_map[category])
            else:
                embed = view.create_main_embed()
        else:
            embed = view.create_main_embed()

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="commands", description="Hiển thị danh sách tất cả lệnh")
    async def commands_list(self, interaction: disnake.ApplicationCommandInteraction):
        """Show a simple list of all commands."""
        embed = create_embed(
            "📋 Danh sách tất cả lệnh",
            "Dưới đây là tất cả lệnh có sẵn của bot:",
            UI_CONFIG["embed_colors"]["secondary"]
        )

        for category_name, category_info in COMMAND_CATEGORIES.items():
            commands_list = []
            for cmd_name in category_info['commands'].keys():
                commands_list.append(f"`/{cmd_name}`")

            embed.add_field(
                name=f"{category_name} ({len(commands_list)} lệnh)",
                value=" • ".join(commands_list),
                inline=False
            )

        embed.set_footer(text=f"Total: {sum(len(cat['commands']) for cat in COMMAND_CATEGORIES.values())} commands")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="search-command", description="Tìm kiếm lệnh theo từ khóa")
    async def search_command(self,
                           interaction: disnake.ApplicationCommandInteraction,
                           keyword: str = commands.Param(description="Từ khóa để tìm kiếm")):
        """Search for commands by keyword."""
        keyword = keyword.lower().strip()
        if len(keyword) < UI_CONFIG["min_keyword_length"]:
            embed = create_embed(
                "❌ Từ khóa quá ngắn",
                f"Vui lòng nhập từ khóa có ít nhất {UI_CONFIG['min_keyword_length']} ký tự",
                UI_CONFIG["embed_colors"]["error"]
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Search in command names and descriptions
        results = []
        for category_name, category_info in COMMAND_CATEGORIES.items():
            for cmd_name, cmd_info in category_info['commands'].items():
                if keyword in cmd_name.lower() or keyword in cmd_info['description'].lower():
                    results.append({
                        'name': cmd_name,
                        'category': category_name,
                        'info': cmd_info,
                        'match_type': 'name' if keyword in cmd_name.lower() else 'description'
                    })

        if not results:
            embed = create_embed(
                "🔍 Không tìm thấy kết quả",
                f"Không tìm thấy lệnh nào chứa từ khóa `{keyword}`",
                UI_CONFIG["embed_colors"]["warning"]
            )
            embed.add_field(
                name="� Gợi ý",
                value="• Thử từ khóa khác\n• Sử dụng `/commands` để xem tất cả lệnh\n• Sử dụng `/help` để duyệt theo danh mục",
                inline=False
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        # Create results embed
        embed = create_embed(
            f"🔍 Kết quả tìm kiếm: `{keyword}`",
            f"Tìm thấy {len(results)} lệnh phù hợp:",
            UI_CONFIG["embed_colors"]["success"]
        )

        # Group results by category and limit to max results
        by_category = {}
        for result in results[:UI_CONFIG["max_search_results"]]:
            category = result['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)

        for category, commands in by_category.items():
            command_list = []
            for cmd in commands:
                match_indicator = "📝" if cmd['match_type'] == 'name' else "📄"
                command_list.append(f"{match_indicator} `/{cmd['name']}` - {cmd['info']['description'][:50]}...")

            embed.add_field(
                name=f"{category} ({len(commands)} lệnh)",
                value="\n".join(command_list),
                inline=False
            )

        if len(results) > UI_CONFIG["max_search_results"]:
            embed.set_footer(text=f"Hiển thị {UI_CONFIG['max_search_results']}/{len(results)} kết quả đầu tiên")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    # Legacy prefix command support
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="help", description="Hiển thị menu trợ giúp")
    async def help_legacy(self, ctx: commands.Context, category: str = None):
        """Legacy prefix command support for help."""
        if ctx.author.bot:
            return

        # Create view and embed
        view = HelpView(self.bot, ctx.author)

        if category:
            # Map category names
            category_map = {
                "ticket": "🎫 Ticket",
                "moderation": "🛡️ Moderation",
                "music": "🎵 Music",
                "fishing": "🎣 Fishing Game",
                "system": "⚙️ System",
                "fun": "🎮 Fun & Games",
                "avatar": "🖼️ Avatar & User Info",
                "server": "🏰 Server Info",
                "emoji": "🎭 Emoji Management",
                "giveaway": "🎉 Giveaway",
                "boost": "🚀 Boost Tracker",
                "admin": "🔧 Admin"
            }

            if category.lower() in category_map:
                view.current_page = category_map[category.lower()]
                embed = view.create_category_embed(category_map[category.lower()])
            else:
                embed = view.create_main_embed()
        else:
            embed = view.create_main_embed()

        await ctx.send(embed=embed, view=view)


def setup(bot: ClientUser):
    """Setup function to add the cog to the bot."""
    bot.add_cog(Help(bot))

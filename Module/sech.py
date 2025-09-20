import disnake
from disnake.ext import commands
import aiohttp
import asyncio
from datetime import datetime
from typing import Optional, Dict, List
from utils.ClientUser import ClientUser


# NSFW Categories with descriptions (based on waifu.im API)
NSFW_CATEGORIES = {
    "ass": {
        "description": "Girls with a large butt",
        "emoji": "�",
        "safe_level": 3
    },
    "hentai": {
        "description": "Explicit sexual content",
        "emoji": "🔞",
        "safe_level": 3
    },
    "milf": {
        "description": "A sexually attractive middle-aged woman",
        "emoji": "�‍🦳",
        "safe_level": 3
    },
    "oral": {
        "description": "Oral sex content",
        "emoji": "💋",
        "safe_level": 3
    },
    "paizuri": {
        "description": "Breast sex content",
        "emoji": "🔞",
        "safe_level": 3
    },
    "ecchi": {
        "description": "Slightly explicit sexual content",
        "emoji": "😏",
        "safe_level": 2
    },
    "ero": {
        "description": "Any kind of erotic content",
        "emoji": "�",
        "safe_level": 2
    }
}

# SFW Categories (versatile tags from waifu.im API)
SFW_CATEGORIES = {
    "waifu": {
        "description": "A female anime/manga character",
        "emoji": "👩‍🎨"
    },
    "maid": {
        "description": "Cute womans or girl employed to do domestic work in their working uniform",
        "emoji": "👩‍�"
    },
    "marin-kitagawa": {
        "description": "One of two main protagonists in My Dress-Up Darling",
        "emoji": "💄"
    },
    "mori-calliope": {
        "description": "English Virtual YouTuber associated with hololive",
        "emoji": "�"
    },
    "raiden-shogun": {
        "description": "Genshin Impact's Raiden Shogun",
        "emoji": "⚡"
    },
    "oppai": {
        "description": "Girls with large breasts",
        "emoji": "🎈"
    },
    "selfies": {
        "description": "A photo-like image of a waifu",
        "emoji": "📸"
    },
    "uniform": {
        "description": "Girls wearing any kind of uniform, cosplay etc",
        "emoji": "👮‍♀️"
    },
    "kamisato-ayaka": {
        "description": "Kamisato Ayaka is a playable Cryo character in Genshin Impact",
        "emoji": "❄️"
    }
}

BASE_API = "https://api.waifu.im"


class ImageAPIError(Exception):
    """Custom exception for API errors."""
    pass


async def fetch_image(session: aiohttp.ClientSession, tags: List[str], is_nsfw: bool = False) -> Optional[str]:
    """
    Fetch image URL from waifu.im API.

    Args:
        session: aiohttp session
        tags: list of tags to search for
        is_nsfw: whether to include NSFW content

    Returns:
        Image URL or None if failed
    """
    try:
        url = f"{BASE_API}/search"

        # Prepare parameters for waifu.im API
        params = {
            "included_tags": tags[0] if tags else "waifu",  # Use first tag
            "is_nsfw": str(is_nsfw).lower()
        }

        print(f"DEBUG: Requesting {url} with params {params}")  # Debug log

        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
            print(f"DEBUG: Response status: {response.status}")  # Debug log
            if response.status == 200:
                data = await response.json()
                images = data.get("images", [])
                print(f"DEBUG: Found {len(images)} images")  # Debug log
                if images and len(images) > 0:
                    image_url = images[0].get("url")
                    print(f"DEBUG: Image URL: {image_url}")  # Debug log
                    return image_url
                else:
                    raise ImageAPIError("No images found")
            elif response.status == 404:
                raise ImageAPIError(f"Tags '{', '.join(tags)}' not found")
            else:
                text = await response.text()
                print(f"DEBUG: Error response: {text}")  # Debug log
                raise ImageAPIError(f"API returned status {response.status}")

    except asyncio.TimeoutError:
        raise ImageAPIError("Request timed out")
    except aiohttp.ClientError as e:
        raise ImageAPIError(f"Network error: {str(e)}")
    except Exception as e:
        raise ImageAPIError(f"Unexpected error: {str(e)}")


def create_nsfw_warning_embed() -> disnake.Embed:
    """Create warning embed for NSFW content."""
    embed = disnake.Embed(
        title="⚠️ NSFW Content Warning",
        description="This command contains adult content and is restricted to NSFW channels only.",
        color=0xff6b6b,
        timestamp=datetime.now()
    )

    embed.add_field(
        name="📋 Requirements",
        value="""
        🔞 **Age:** 18+ only
        🔒 **Channel:** NSFW channel required
        👥 **Server:** Must allow NSFW content
        """,
        inline=False
    )

    embed.add_field(
        name="💡 Alternative",
        value="Use `/sfw` command for safe anime images in any channel!",
        inline=False
    )

    embed.set_footer(text="Please use responsibly and follow Discord ToS")

    return embed

class Sech(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot
        self.session: Optional[aiohttp.ClientSession] = None

    async def cog_load(self):
        """Initialize aiohttp session when cog loads."""
        self.session = aiohttp.ClientSession()

    async def cog_unload(self):
        """Clean up aiohttp session when cog unloads."""
        if self.session:
            await self.session.close()

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="sfw", description="Lấy ảnh anime an toàn từ waifu.im")
    async def sfw_images(self,
                        interaction: disnake.ApplicationCommandInteraction,
                        category: str = commands.Param(
                            description="Loại ảnh muốn lấy",
                            choices=[
                                disnake.OptionChoice(name=f"{info['emoji']} {cat.title()} - {info['description']}", value=cat)
                                for cat, info in SFW_CATEGORIES.items()
                            ]
                        )):
        """Get safe anime images that can be used in any channel."""

        await interaction.response.defer()

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            image_url = await fetch_image(self.session, [category], is_nsfw=False)

            if not image_url:
                embed = disnake.Embed(
                    title="❌ Lỗi",
                    description="Không thể lấy ảnh. Vui lòng thử lại sau!",
                    color=0xff0000
                )
                await interaction.edit_original_response(embed=embed)
                return

            # Create beautiful embed
            category_info = SFW_CATEGORIES.get(category, {"emoji": "🖼️", "description": "Anime image"})

            embed = disnake.Embed(
                title=f"{category_info['emoji']} {category.title()} Image",
                description=category_info['description'],
                color=0x00ff88,
                timestamp=datetime.now()
            )

            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Requested by {interaction.author.display_name} • Powered by waifu.im",
                icon_url=interaction.author.display_avatar.url
            )

            await interaction.edit_original_response(embed=embed)

        except ImageAPIError as e:
            embed = disnake.Embed(
                title="❌ API Error",
                description=f"Lỗi khi lấy ảnh: {str(e)}",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Unexpected Error",
                description="Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau!",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)

    @commands.is_nsfw()
    @commands.cooldown(1, 15, commands.BucketType.user)
    @commands.slash_command(name="nsfw", description="🔞 Lấy ảnh NSFW từ waifu.im (chỉ trong NSFW channel)")
    async def nsfw_images(self,
                         interaction: disnake.ApplicationCommandInteraction,
                         category: str = commands.Param(
                             description="Loại ảnh NSFW muốn lấy",
                             choices=[
                                 disnake.OptionChoice(
                                     name=f"{info['emoji']} {cat.title()} - {info['description']}",
                                     value=cat
                                 )
                                 for cat, info in NSFW_CATEGORIES.items()
                             ]
                         )):
        """Get NSFW anime images (18+ only, NSFW channels only)."""

        # Double check NSFW channel
        if not interaction.channel.is_nsfw():
            embed = create_nsfw_warning_embed()
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer()

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            image_url = await fetch_image(self.session, [category], is_nsfw=True)

            if not image_url:
                embed = disnake.Embed(
                    title="❌ Lỗi",
                    description="Không thể lấy ảnh. Vui lòng thử lại sau!",
                    color=0xff0000
                )
                await interaction.edit_original_response(embed=embed)
                return

            # Create NSFW embed with warning
            category_info = NSFW_CATEGORIES.get(category, {"emoji": "🔞", "description": "NSFW content", "safe_level": 3})

            embed = disnake.Embed(
                title=f"🔞 {category_info['emoji']} {category.title()} Image",
                description=f"{category_info['description']} (18+ only)",
                color=0xff6b6b,
                timestamp=datetime.now()
            )

            embed.set_image(url=image_url)

            # Add safety level indicator
            safety_levels = {
                1: "🟢 Mild content",
                2: "🟡 Moderate content",
                3: "🔴 Explicit content"
            }

            embed.add_field(
                name="⚠️ Content Level",
                value=safety_levels.get(category_info['safe_level'], "🔴 Explicit content"),
                inline=True
            )

            embed.set_footer(
                text=f"Requested by {interaction.author.display_name} • 18+ only • Powered by waifu.im",
                icon_url=interaction.author.display_avatar.url
            )

            await interaction.edit_original_response(embed=embed)

        except ImageAPIError as e:
            embed = disnake.Embed(
                title="❌ API Error",
                description=f"Lỗi khi lấy ảnh: {str(e)}",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Unexpected Error",
                description="Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau!",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.slash_command(name="random-anime", description="Lấy ảnh anime ngẫu nhiên (SFW)")
    async def random_anime(self, interaction: disnake.ApplicationCommandInteraction):
        """Get a random safe anime image."""

        await interaction.response.defer()

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Pick random SFW category
            import random
            category = random.choice(list(SFW_CATEGORIES.keys()))

            image_url = await fetch_image(self.session, [category], is_nsfw=False)

            if not image_url:
                embed = disnake.Embed(
                    title="❌ Lỗi",
                    description="Không thể lấy ảnh. Vui lòng thử lại sau!",
                    color=0xff0000
                )
                await interaction.edit_original_response(embed=embed)
                return

            category_info = SFW_CATEGORIES.get(category, {"emoji": "🖼️", "description": "Random anime image"})

            embed = disnake.Embed(
                title=f"🎲 {category_info['emoji']} Random {category.title()}",
                description=f"Ngẫu nhiên: {category_info['description']}",
                color=0x7289da,
                timestamp=datetime.now()
            )

            embed.set_image(url=image_url)
            embed.set_footer(
                text=f"Random pick for {interaction.author.display_name} • Powered by waifu.im",
                icon_url=interaction.author.display_avatar.url
            )

            await interaction.edit_original_response(embed=embed)

        except ImageAPIError as e:
            embed = disnake.Embed(
                title="❌ API Error",
                description=f"Lỗi khi lấy ảnh: {str(e)}",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Unexpected Error",
                description="Đã xảy ra lỗi không mong muốn. Vui lòng thử lại sau!",
                color=0xff0000
            )
            await interaction.edit_original_response(embed=embed)

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.slash_command(name="anime-info", description="Thông tin về các loại ảnh anime có sẵn")
    async def anime_info(self, interaction: disnake.ApplicationCommandInteraction):
        """Show information about available anime image categories."""

        embed = disnake.Embed(
            title="🎨 Anime Images - Thông tin danh mục",
            description="Dưới đây là các loại ảnh anime có sẵn:",
            color=0x7289da,
            timestamp=datetime.now()
        )

        # SFW Categories
        sfw_text = ""
        for category, info in SFW_CATEGORIES.items():
            sfw_text += f"{info['emoji']} **{category.title()}** - {info['description']}\n"

        embed.add_field(
            name="✅ SFW Categories (Safe for all channels)",
            value=sfw_text,
            inline=False
        )

        # NSFW Categories
        nsfw_text = ""
        for category, info in NSFW_CATEGORIES.items():
            safety_indicator = "🟢" if info['safe_level'] == 1 else "🟡" if info['safe_level'] == 2 else "🔴"
            nsfw_text += f"{info['emoji']} **{category.title()}** {safety_indicator} - {info['description']}\n"

        embed.add_field(
            name="🔞 NSFW Categories (NSFW channels only, 18+)",
            value=nsfw_text,
            inline=False
        )

        # Commands info
        embed.add_field(
            name="📋 Available Commands",
            value="""
            `/sfw <category>` - Get safe anime images
            `/nsfw <category>` - Get NSFW images (NSFW channels only)
            `/random-anime` - Get random safe anime image
            `/anime-info` - Show this information
            """,
            inline=False
        )

        embed.add_field(
            name="⚠️ Important Notes",
            value="""
            🔞 NSFW commands require NSFW channels and 18+ age
            🚫 Misuse may result in command restrictions
            📝 Follow Discord Terms of Service
            🛡️ Report inappropriate content to moderators
            """,
            inline=False
        )

        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.set_footer(
            text="Powered by waifu.pics API • Use responsibly",
            icon_url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)


def setup(bot: ClientUser):
    bot.add_cog(Sech(bot))
    
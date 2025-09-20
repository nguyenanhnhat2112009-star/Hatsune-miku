import disnake
from disnake.ext import commands
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import random
import asyncio
import aiohttp
import json
import os
from utils.ClientUser import ClientUser


class Fun(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="8ball", description="Hỏi quả cầu thần số 8")
    async def eight_ball(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        question: str
    ):
        """Magic 8-ball command."""
        responses = [
            "🎱 Chắc chắn rồi!",
            "🎱 Không nghi ngờ gì nữa!",
            "🎱 Có, chắc chắn!",
            "🎱 Rất có khả năng!",
            "🎱 Triển vọng tốt!",
            "🎱 Có thể!",
            "🎱 Hỏi lại sau nhé!",
            "🎱 Tốt hơn là đừng nói cho bạn biết bây giờ...",
            "🎱 Không thể dự đoán được!",
            "🎱 Tập trung và hỏi lại!",
            "🎱 Đừng mơ tưởng!",
            "🎱 Câu trả lời của tôi là không!",
            "🎱 Nguồn tin của tôi nói là không!",
            "🎱 Triển vọng không tốt lắm!",
            "🎱 Rất đáng nghi ngờ!"
        ]

        embed = disnake.Embed(
            title="🎱 Quả cầu thần số 8",
            color=0x7289da,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="❓ Câu hỏi",
            value=question,
            inline=False
        )

        embed.add_field(
            name="💭 Trả lời",
            value=random.choice(responses),
            inline=False
        )

        embed.set_footer(
            text=f"Hỏi bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="dice", description="Tung xúc xắc")
    async def dice(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        sides: Optional[int] = 6,
        count: Optional[int] = 1
    ):
        """Roll dice command."""
        if sides < 2 or sides > 100:
            await interaction.response.send_message("❌ Số mặt phải từ 2 đến 100!", ephemeral=True)
            return

        if count < 1 or count > 10:
            await interaction.response.send_message("❌ Số lượng xúc xắc phải từ 1 đến 10!", ephemeral=True)
            return

        results = [random.randint(1, sides) for _ in range(count)]
        total = sum(results)

        embed = disnake.Embed(
            title="🎲 Kết quả tung xúc xắc",
            color=0x00ff88,
            timestamp=datetime.now()
        )

        if count == 1:
            embed.add_field(
                name=f"🎲 Xúc xắc {sides} mặt",
                value=f"**{results[0]}**",
                inline=False
            )
        else:
            embed.add_field(
                name=f"🎲 {count} xúc xắc {sides} mặt",
                value=f"Kết quả: {' + '.join(map(str, results))}\n**Tổng: {total}**",
                inline=False
            )

        embed.set_footer(
            text=f"Tung bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="flip", description="Tung đồng xu")
    async def flip(self, interaction: disnake.ApplicationCommandInteraction):
        """Coin flip command."""
        result = random.choice(["Ngửa", "Sấp"])
        emoji = "🪙" if result == "Ngửa" else "🥇"

        embed = disnake.Embed(
            title="🪙 Tung đồng xu",
            description=f"{emoji} **{result}**",
            color=0xffd700,
            timestamp=datetime.now()
        )

        embed.set_footer(
            text=f"Tung bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="choose", description="Chọn ngẫu nhiên từ danh sách")
    async def choose(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        choices: str
    ):
        """Random choice command."""
        options = [choice.strip() for choice in choices.split(',') if choice.strip()]
        
        if len(options) < 2:
            await interaction.response.send_message("❌ Bạn cần cung cấp ít nhất 2 lựa chọn, cách nhau bằng dấu phẩy!", ephemeral=True)
            return

        if len(options) > 20:
            await interaction.response.send_message("❌ Tối đa 20 lựa chọn!", ephemeral=True)
            return

        chosen = random.choice(options)

        embed = disnake.Embed(
            title="🎯 Lựa chọn ngẫu nhiên",
            color=0xff6b6b,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="📝 Các lựa chọn",
            value=", ".join(options),
            inline=False
        )

        embed.add_field(
            name="🎲 Kết quả",
            value=f"**{chosen}**",
            inline=False
        )

        embed.set_footer(
            text=f"Chọn bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.slash_command(name="joke", description="Kể một câu chuyện cười")
    async def joke(self, interaction: disnake.ApplicationCommandInteraction):
        """Random joke command."""
        jokes = [
            "Tại sao lập trình viên không thích thiên nhiên? Vì có quá nhiều bug! 🐛",
            "Tại sao máy tính không bao giờ đói? Vì nó đã có byte! 🍔",
            "Làm sao để làm cho một lập trình viên khóc? Xóa code của họ! 😭",
            "Tại sao lập trình viên thích màu tối? Vì light mode làm họ bug! 🌙",
            "Có 10 loại người trên thế giới: những người hiểu nhị phân và những người không hiểu! 💻",
            "Tại sao lập trình viên luôn nhầm Halloween với Christmas? Vì Oct 31 = Dec 25! 🎃🎄",
            "Một lập trình viên đi vào quán bar và gọi 1 bia, 0 bia, -1 bia, NULL bia... Quán bar crash! 🍺",
            "Tại sao Java lập trình viên đeo kính? Vì họ không thể C#! 👓",
            "Có bao nhiêu lập trình viên cần để thay bóng đèn? Không có, đó là hardware problem! 💡",
            "Tại sao lập trình viên không thích đi biển? Vì họ sợ C! 🌊"
        ]

        joke = random.choice(jokes)

        embed = disnake.Embed(
            title="😂 Chuyện cười",
            description=joke,
            color=0xffeb3b,
            timestamp=datetime.now()
        )

        embed.set_footer(
            text=f"Yêu cầu bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="love", description="Tính độ tương hợp tình yêu")
    async def love(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        person1: disnake.User,
        person2: Optional[disnake.User] = None
    ):
        """Love compatibility calculator."""
        if person2 is None:
            person2 = interaction.author

        # Create a "random" but consistent percentage based on user IDs
        combined_id = str(person1.id) + str(person2.id)
        random.seed(hash(combined_id) % (2**32))
        percentage = random.randint(0, 100)

        # Reset random seed
        random.seed()

        if percentage >= 90:
            emoji = "💕"
            status = "Tình yêu hoàn hảo!"
        elif percentage >= 70:
            emoji = "💖"
            status = "Rất tương hợp!"
        elif percentage >= 50:
            emoji = "💗"
            status = "Khá tốt!"
        elif percentage >= 30:
            emoji = "💛"
            status = "Có thể thử!"
        else:
            emoji = "💔"
            status = "Không phù hợp lắm..."

        embed = disnake.Embed(
            title="💘 Máy tính tình yêu",
            color=0xff69b4,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="👫 Cặp đôi",
            value=f"{person1.display_name} ❤️ {person2.display_name}",
            inline=False
        )

        embed.add_field(
            name="📊 Độ tương hợp",
            value=f"{emoji} **{percentage}%** - {status}",
            inline=False
        )

        # Add a progress bar
        filled = int(percentage / 10)
        bar = "█" * filled + "░" * (10 - filled)
        embed.add_field(
            name="📈 Biểu đồ",
            value=f"`{bar}` {percentage}%",
            inline=False
        )

        embed.set_footer(
            text=f"Tính bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="rate", description="Đánh giá một thứ gì đó")
    async def rate(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        thing: str
    ):
        """Rate something command."""
        # Create consistent rating based on the thing being rated
        rating = hash(thing.lower()) % 11  # 0-10

        stars = "⭐" * rating + "☆" * (10 - rating)
        
        if rating >= 9:
            comment = "Tuyệt vời!"
        elif rating >= 7:
            comment = "Rất tốt!"
        elif rating >= 5:
            comment = "Ổn!"
        elif rating >= 3:
            comment = "Không tệ!"
        else:
            comment = "Cần cải thiện..."

        embed = disnake.Embed(
            title="⭐ Đánh giá",
            color=0xffd700,
            timestamp=datetime.now()
        )

        embed.add_field(
            name="📝 Đối tượng",
            value=thing,
            inline=False
        )

        embed.add_field(
            name="🌟 Điểm số",
            value=f"{stars}\n**{rating}/10** - {comment}",
            inline=False
        )

        embed.set_footer(
            text=f"Đánh giá bởi {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)


def setup(bot: ClientUser):
    bot.add_cog(Fun(bot))

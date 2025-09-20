from __future__ import annotations

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from disnake.ext import commands
from disnake import Embed, ApplicationCommandInteraction, Option, MessageFlags, ButtonStyle
try:
    from disnake import SelectOption
except ImportError:
    # Fallback for older disnake versions
    SelectOption = None
from disnake.ui import View, Button, Select
import disnake

from utils.ClientUser import ClientUser


class Fishing(commands.Cog):
    def __init__(self, bot):
        self.bot: ClientUser = bot
        
        # Database giả lập cho fishing data
        self.fishing_data = {}
        
        # Danh sách các loại cá
        self.fish_types = {
            "🐟": {"name": "Cá nhỏ", "rarity": "common", "price": 10, "chance": 40},
            "🐠": {"name": "Cá nhiệt đới", "rarity": "common", "price": 15, "chance": 30},
            "🐡": {"name": "Cá nóc", "rarity": "uncommon", "price": 25, "chance": 15},
            "🦈": {"name": "Cá mập", "rarity": "rare", "price": 100, "chance": 5},
            "🐙": {"name": "Bạch tuộc", "rarity": "rare", "price": 80, "chance": 7},
            "🦞": {"name": "Tôm hùm", "rarity": "epic", "price": 200, "chance": 2},
            "🐋": {"name": "Cá voi", "rarity": "legendary", "price": 500, "chance": 0.8},
            "🦑": {"name": "Mực khổng lồ", "rarity": "legendary", "price": 600, "chance": 0.2}
        }
        
        # Loại cần câu
        self.fishing_rods = {
            1: {"name": "Cần câu tre", "price": 0, "bonus": 0, "emoji": "🎣"},
            2: {"name": "Cần câu sắt", "price": 500, "bonus": 10, "emoji": "🎣"},
            3: {"name": "Cần câu vàng", "price": 2000, "bonus": 25, "emoji": "✨"},
            4: {"name": "Cần câu kim cương", "price": 10000, "bonus": 50, "emoji": "💎"},
            5: {"name": "Cần câu huyền thoại", "price": 50000, "bonus": 100, "emoji": "🌟"}
        }

    def get_user_data(self, user_id: int) -> Dict:
        """Lấy dữ liệu người chơi"""
        if user_id not in self.fishing_data:
            self.fishing_data[user_id] = {
                "money": 100,
                "fish_caught": {},
                "rod_level": 1,
                "last_fish": None,
                "total_caught": 0,
                "achievements": []
            }
        return self.fishing_data[user_id]

    def can_fish(self, user_id: int) -> bool:
        """Kiểm tra có thể câu cá không (cooldown)"""
        data = self.get_user_data(user_id)
        if data["last_fish"] is None:
            return True
        
        cooldown = timedelta(seconds=30)  # 30 giây cooldown
        return datetime.now() - data["last_fish"] >= cooldown

    def catch_fish(self, user_id: int) -> Optional[str]:
        """Logic câu cá"""
        data = self.get_user_data(user_id)
        rod_bonus = self.fishing_rods[data["rod_level"]]["bonus"]
        
        # Tính toán xác suất với bonus từ cần câu
        total_chance = 0
        for fish_emoji, fish_data in self.fish_types.items():
            adjusted_chance = fish_data["chance"] + (rod_bonus * 0.1)
            if random.random() * 100 < adjusted_chance:
                # Câu được cá!
                data["last_fish"] = datetime.now()
                data["total_caught"] += 1
                
                if fish_emoji not in data["fish_caught"]:
                    data["fish_caught"][fish_emoji] = 0
                data["fish_caught"][fish_emoji] += 1
                
                return fish_emoji
        
        # Không câu được gì
        data["last_fish"] = datetime.now()
        return None

    @commands.slash_command(name="fish", description="🎣 Câu cá để kiếm tiền!")
    async def fish(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()
        
        user_data = self.get_user_data(inter.author.id)
        
        # Kiểm tra cooldown
        if not self.can_fish(inter.author.id):
            cooldown_left = 30 - (datetime.now() - user_data["last_fish"]).seconds
            embed = Embed(
                title="⏰ Chờ một chút!",
                description=f"Bạn cần chờ **{cooldown_left}** giây nữa mới có thể câu cá tiếp!",
                color=0xFFFF00
            )
            await inter.edit_original_response(embed=embed)
            return
        
        # Thực hiện câu cá
        embed = Embed(
            title="🎣 Đang câu cá...",
            description="Bạn đang thả cần xuống nước...",
            color=0x00FFFF
        )
        await inter.edit_original_response(embed=embed)
        
        # Delay để tạo cảm giác hồi hộp
        await asyncio.sleep(2)
        
        caught_fish = self.catch_fish(inter.author.id)
        
        if caught_fish:
            fish_info = self.fish_types[caught_fish]
            user_data["money"] += fish_info["price"]
            
            # Tạo embed thành công
            embed = Embed(
                title="🎉 Câu được cá!",
                description=f"Bạn đã câu được {caught_fish} **{fish_info['name']}**!\n"
                           f"💰 Kiếm được: **{fish_info['price']}** xu\n"
                           f"💵 Tổng tiền: **{user_data['money']}** xu",
                color=0x00FF00
            )
            
            # Thêm thông tin độ hiếm
            rarity_colors = {
                "common": "🟢",
                "uncommon": "🟡", 
                "rare": "🟠",
                "epic": "🟣",
                "legendary": "🔴"
            }
            rarity_color = rarity_colors.get(fish_info["rarity"], "⚪")
            embed.add_field(
                name="Độ hiếm",
                value=f"{rarity_color} {fish_info['rarity'].title()}",
                inline=True
            )
            
        else:
            embed = Embed(
                title="😔 Không câu được gì",
                description="Cá không cắn câu lần này. Hãy thử lại sau!",
                color=0xFF0000
            )
        
        # Thêm thông tin cần câu hiện tại
        rod_info = self.fishing_rods[user_data["rod_level"]]
        embed.add_field(
            name="Cần câu hiện tại",
            value=f"{rod_info['emoji']} {rod_info['name']}",
            inline=True
        )
        
        await inter.edit_original_response(embed=embed)

    @commands.slash_command(name="inventory", description="🎒 Xem túi đồ câu cá của bạn")
    async def inventory(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()
        
        user_data = self.get_user_data(inter.author.id)
        
        embed = Embed(
            title=f"🎒 Túi đồ của {inter.author.display_name}",
            color=0x7289DA
        )
        
        # Thông tin tiền và cần câu
        rod_info = self.fishing_rods[user_data["rod_level"]]
        embed.add_field(
            name="💰 Thông tin tài khoản",
            value=f"💵 Tiền: **{user_data['money']}** xu\n"
                  f"🎣 Cần câu: {rod_info['emoji']} {rod_info['name']}\n"
                  f"🐟 Tổng cá câu được: **{user_data['total_caught']}**",
            inline=False
        )
        
        # Danh sách cá đã câu
        if user_data["fish_caught"]:
            fish_list = ""
            total_value = 0
            
            for fish_emoji, count in user_data["fish_caught"].items():
                fish_info = self.fish_types[fish_emoji]
                value = count * fish_info["price"]
                total_value += value
                fish_list += f"{fish_emoji} **{fish_info['name']}** x{count} (💰 {value} xu)\n"
            
            embed.add_field(
                name="🐟 Cá đã câu được",
                value=fish_list,
                inline=False
            )
            
            embed.add_field(
                name="💎 Tổng giá trị",
                value=f"**{total_value}** xu",
                inline=True
            )
        else:
            embed.add_field(
                name="🐟 Cá đã câu được",
                value="Chưa câu được cá nào. Hãy dùng `/fish` để bắt đầu!",
                inline=False
            )
        
        await inter.edit_original_response(embed=embed)

    @commands.slash_command(name="fishmarket", description="🏪 Cửa hàng câu cá")
    async def fish_market(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()
        
        user_data = self.get_user_data(inter.author.id)
        
        class FishMarketView(View):
            def __init__(self, fishing_game):
                super().__init__(timeout=300)
                self.fishing_game = fishing_game
                
            @disnake.ui.select(
                placeholder="Chọn hành động...",
                options=[
                    SelectOption(
                        label="Bán tất cả cá",
                        description="Bán toàn bộ cá trong túi đồ",
                        emoji="💰",
                        value="sell_all"
                    ),
                    SelectOption(
                        label="Nâng cấp cần câu",
                        description="Mua cần câu tốt hơn",
                        emoji="⬆️",
                        value="upgrade_rod"
                    ),
                    SelectOption(
                        label="Xem bảng xếp hạng",
                        description="Top người câu cá giỏi nhất",
                        emoji="🏆",
                        value="leaderboard"
                    )
                ]
            )
            async def market_select(self, select: Select, interaction: disnake.MessageInteraction):
                await interaction.response.defer(ephemeral=True)
                
                user_data = self.fishing_game.get_user_data(interaction.author.id)
                
                if select.values[0] == "sell_all":
                    if not user_data["fish_caught"]:
                        embed = Embed(
                            title="❌ Không có cá để bán",
                            description="Bạn chưa có cá nào trong túi đồ!",
                            color=0xFF0000
                        )
                    else:
                        total_money = 0
                        fish_sold = ""
                        
                        for fish_emoji, count in user_data["fish_caught"].items():
                            fish_info = self.fishing_game.fish_types[fish_emoji]
                            money = count * fish_info["price"]
                            total_money += money
                            fish_sold += f"{fish_emoji} {fish_info['name']} x{count} = {money} xu\n"
                        
                        user_data["money"] += total_money
                        user_data["fish_caught"] = {}
                        
                        embed = Embed(
                            title="💰 Đã bán cá thành công!",
                            description=f"**Cá đã bán:**\n{fish_sold}\n"
                                       f"💵 Tổng tiền nhận được: **{total_money}** xu\n"
                                       f"💰 Tiền hiện tại: **{user_data['money']}** xu",
                            color=0x00FF00
                        )
                
                elif select.values[0] == "upgrade_rod":
                    current_level = user_data["rod_level"]
                    next_level = current_level + 1
                    
                    if next_level > len(self.fishing_game.fishing_rods):
                        embed = Embed(
                            title="✨ Cần câu đã tối đa!",
                            description="Bạn đã có cần câu tốt nhất rồi!",
                            color=0xFFD700
                        )
                    else:
                        next_rod = self.fishing_game.fishing_rods[next_level]
                        
                        if user_data["money"] >= next_rod["price"]:
                            user_data["money"] -= next_rod["price"]
                            user_data["rod_level"] = next_level
                            
                            embed = Embed(
                                title="🎉 Nâng cấp thành công!",
                                description=f"Bạn đã mua {next_rod['emoji']} **{next_rod['name']}**!\n"
                                           f"💰 Tiền còn lại: **{user_data['money']}** xu\n"
                                           f"⚡ Bonus câu cá: +{next_rod['bonus']}%",
                                color=0x00FF00
                            )
                        else:
                            embed = Embed(
                                title="❌ Không đủ tiền",
                                description=f"Bạn cần **{next_rod['price']}** xu để mua {next_rod['emoji']} **{next_rod['name']}**\n"
                                           f"💰 Tiền hiện tại: **{user_data['money']}** xu",
                                color=0xFF0000
                            )
                
                elif select.values[0] == "leaderboard":
                    # Tạo bảng xếp hạng
                    leaderboard = []
                    for user_id, data in self.fishing_game.fishing_data.items():
                        leaderboard.append((user_id, data["total_caught"]))
                    
                    leaderboard.sort(key=lambda x: x[1], reverse=True)
                    
                    lb_text = ""
                    for i, (user_id, count) in enumerate(leaderboard[:10], 1):
                        try:
                            user = self.fishing_game.bot.get_user(user_id)
                            name = user.display_name if user else f"User {user_id}"
                        except:
                            name = f"User {user_id}"
                        
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
                        lb_text += f"{medal} **{name}**: {count} cá\n"
                    
                    embed = Embed(
                        title="🏆 Bảng xếp hạng câu cá",
                        description=lb_text or "Chưa có ai câu cá!",
                        color=0xFFD700
                    )
                
                await interaction.edit_original_response(embed=embed)
        
        # Tạo embed chính cho market
        embed = Embed(
            title="🏪 Cửa hàng câu cá",
            description="Chào mừng đến với cửa hàng câu cá!\nChọn hành động bạn muốn thực hiện:",
            color=0x7289DA
        )
        
        # Hiển thị thông tin cần câu có thể mua
        rod_info = ""
        current_level = user_data["rod_level"]
        
        for level, rod_data in self.fishing_rods.items():
            if level == current_level:
                rod_info += f"✅ {rod_data['emoji']} **{rod_data['name']}** (Đang sử dụng)\n"
            elif level == current_level + 1:
                rod_info += f"🛒 {rod_data['emoji']} **{rod_data['name']}** - {rod_data['price']} xu\n"
            elif level > current_level + 1:
                rod_info += f"🔒 {rod_data['emoji']} **{rod_data['name']}** (Chưa mở khóa)\n"
        
        embed.add_field(
            name="🎣 Cần câu",
            value=rod_info,
            inline=False
        )
        
        embed.add_field(
            name="💰 Tiền của bạn",
            value=f"**{user_data['money']}** xu",
            inline=True
        )
        
        view = FishMarketView(self)
        await inter.edit_original_response(embed=embed, view=view)

    @commands.slash_command(name="fishhelp", description="❓ Hướng dẫn chơi game câu cá")
    async def fish_help(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()
        
        embed = Embed(
            title="🎣 Hướng dẫn game câu cá",
            color=0x7289DA
        )
        
        embed.add_field(
            name="🎮 Cách chơi",
            value="• Dùng `/fish` để câu cá (cooldown 30 giây)\n"
                  "• Dùng `/inventory` để xem túi đồ\n"
                  "• Dùng `/fishmarket` để bán cá và nâng cấp\n"
                  "• Dùng `/fishhelp` để xem hướng dẫn",
            inline=False
        )
        
        embed.add_field(
            name="🐟 Độ hiếm cá",
            value="🟢 **Common**: Cá nhỏ, cá nhiệt đới\n"
                  "🟡 **Uncommon**: Cá nóc\n"
                  "🟠 **Rare**: Cá mập, bạch tuộc\n"
                  "🟣 **Epic**: Tôm hùm\n"
                  "🔴 **Legendary**: Cá voi, mực khổng lồ",
            inline=False
        )
        
        embed.add_field(
            name="🎣 Cần câu",
            value="Nâng cấp cần câu để tăng tỷ lệ câu được cá hiếm!\n"
                  "🎣 Tre → 🎣 Sắt → ✨ Vàng → 💎 Kim cương → 🌟 Huyền thoại",
            inline=False
        )
        
        embed.add_field(
            name="💡 Mẹo",
            value="• Bán cá thường xuyên để có tiền nâng cấp\n"
                  "• Cần câu tốt hơn = cá hiếm hơn\n"
                  "• Kiên nhẫn để câu được cá legendary!",
            inline=False
        )
        
        await inter.edit_original_response(embed=embed)

    @commands.slash_command(name="dailyfish", description="🎁 Nhận phần thưởng câu cá hàng ngày")
    async def daily_fish(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()

        user_data = self.get_user_data(inter.author.id)

        # Kiểm tra đã nhận daily chưa
        today = datetime.now().date()
        last_daily = user_data.get("last_daily")

        if last_daily and last_daily == today:
            embed = Embed(
                title="⏰ Đã nhận rồi!",
                description="Bạn đã nhận phần thưởng hàng ngày hôm nay rồi!\nQuay lại vào ngày mai nhé!",
                color=0xFFFF00
            )
            await inter.edit_original_response(embed=embed)
            return

        # Tặng phần thưởng
        daily_money = random.randint(50, 200)
        user_data["money"] += daily_money
        user_data["last_daily"] = today

        # Có cơ hội nhận cá miễn phí
        bonus_fish = None
        if random.random() < 0.3:  # 30% cơ hội
            fish_list = list(self.fish_types.keys())
            bonus_fish = random.choice(fish_list)

            if bonus_fish not in user_data["fish_caught"]:
                user_data["fish_caught"][bonus_fish] = 0
            user_data["fish_caught"][bonus_fish] += 1

        embed = Embed(
            title="🎁 Phần thưởng hàng ngày!",
            description=f"Bạn đã nhận được:\n💰 **{daily_money}** xu",
            color=0x00FF00
        )

        if bonus_fish:
            fish_info = self.fish_types[bonus_fish]
            embed.description += f"\n🎉 Bonus: {bonus_fish} **{fish_info['name']}**!"

        embed.add_field(
            name="💵 Tổng tiền",
            value=f"**{user_data['money']}** xu",
            inline=True
        )

        await inter.edit_original_response(embed=embed)

    @commands.slash_command(name="fishquest", description="📋 Nhiệm vụ câu cá")
    async def fish_quest(self, inter: ApplicationCommandInteraction):
        await inter.response.defer()

        user_data = self.get_user_data(inter.author.id)

        # Định nghĩa các nhiệm vụ
        quests = [
            {
                "id": "first_fish",
                "name": "Cá đầu tiên",
                "description": "Câu được 1 con cá bất kỳ",
                "requirement": 1,
                "reward": 100,
                "check": lambda data: data["total_caught"] >= 1
            },
            {
                "id": "fish_collector",
                "name": "Thợ câu cá",
                "description": "Câu được 10 con cá",
                "requirement": 10,
                "reward": 500,
                "check": lambda data: data["total_caught"] >= 10
            },
            {
                "id": "rare_hunter",
                "name": "Thợ săn hiếm",
                "description": "Câu được 1 con cá rare trở lên",
                "requirement": 1,
                "reward": 1000,
                "check": lambda data: any(fish in ["🦈", "🐙", "🦞", "🐋", "🦑"] for fish in data["fish_caught"])
            },
            {
                "id": "master_fisher",
                "name": "Bậc thầy câu cá",
                "description": "Câu được 50 con cá",
                "requirement": 50,
                "reward": 2000,
                "check": lambda data: data["total_caught"] >= 50
            }
        ]

        embed = Embed(
            title="📋 Nhiệm vụ câu cá",
            description="Hoàn thành nhiệm vụ để nhận phần thưởng!",
            color=0x7289DA
        )

        completed_quests = user_data.get("completed_quests", [])

        for quest in quests:
            if quest["id"] in completed_quests:
                status = "✅ Đã hoàn thành"
            elif quest["check"](user_data):
                status = "🎉 Có thể nhận thưởng!"
                # Tự động nhận thưởng
                if quest["id"] not in completed_quests:
                    user_data["money"] += quest["reward"]
                    completed_quests.append(quest["id"])
                    user_data["completed_quests"] = completed_quests
                    status = f"✅ Vừa hoàn thành! +{quest['reward']} xu"
            else:
                progress = 0
                if quest["id"] == "first_fish" or quest["id"] == "fish_collector" or quest["id"] == "master_fisher":
                    progress = min(user_data["total_caught"], quest["requirement"])
                elif quest["id"] == "rare_hunter":
                    progress = 1 if any(fish in ["🦈", "🐙", "🦞", "🐋", "🦑"] for fish in user_data["fish_caught"]) else 0

                status = f"📊 Tiến độ: {progress}/{quest['requirement']}"

            embed.add_field(
                name=f"🎯 {quest['name']}",
                value=f"{quest['description']}\n💰 Thưởng: {quest['reward']} xu\n{status}",
                inline=False
            )

        await inter.edit_original_response(embed=embed)


def setup(bot: ClientUser):
    bot.add_cog(Fishing(bot))

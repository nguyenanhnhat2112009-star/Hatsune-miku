# bank_cog.py
from utils.ClientUser import ClientUser
import disnake
from disnake.ext import commands
from utils.genqr import gen_qr

class BankCog(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot: ClientUser = bot
        self.accounts = {
                "ngan_hang": "MB Bank",
                "so_tai_khoan": "9990328421004",
                "chu_tai_khoan": "NGUYEN ANH NHAT",
                "qr_data": "https://cdn.discordapp.com/attachments/1370732207177596989/1385459230085222592/IMG_20250620_101524.jpg?ex=685624f5&is=6854d375&hm=8ac93d4ebd77c6816d8aee6074b270786f2d7cad22e6cabebca23c0083cd8047&"
            }
    
    async def generate_embed(self, bin, bank, bankowner, amount, info) -> disnake.Embed:
        embed = disnake.Embed()
        embed.title = "Thanh toán qua VietQR"
        embed.add_field(name="Ngân hàng", value=f"```{bank}```", inline=False)
        embed.add_field(name="Số tài khoản", value=f"```{bin}```", inline=False)
        embed.add_field(name="Chủ tài khoản", value=f"```{bankowner}```", inline=False)
        embed.add_field(name="Số tiền", value=f"```{amount} VNĐ```", inline=False)
        embed.add_field(name="Thông tin chuyển khoản", value=f"```{info}```", inline=False)
        qr = gen_qr(bin, bankowner, info, amount)
        embed.set_image(url=qr)
        embed.set_footer(text="Vui lòng quét mã QR để thanh toán")

        return embed
    
    @commands.command(name="pay", aliases=["thanhtoan", "transfer"], description="Thanh toán qua VietQR")
    async def pay_legacy(self, interaction: disnake.CommandInteraction, amount: int = None, *, info: str = None):
        if amount is None or info is None:
            await interaction.send("Vui lòng cung cấp số tiền và thông tin chuyển khoản.")
            return
        
        try: 
            await interaction.message.delete()
        except (disnake.NotFound, disnake.HTTPException):
            pass
        
        bank = self.accounts["ngan_hang"]
        bin = self.accounts["so_tai_khoan"]
        bankowner = self.accounts["chu_tai_khoan"]
        
        embed = await self.generate_embed(bin, bank, bankowner, amount, info)
        
        await interaction.send(embed=embed)

    @commands.slash_command(name="pay", description="Thanh toán qua VietQR", options=[
        disnake.Option(
            name="amount",
            description="Số tiền cần thanh toán (VNĐ)",
            type=disnake.OptionType.integer,
            required=True
        ),
        disnake.Option(
            name="info",
            description="Thông tin chuyển khoản",
            type=disnake.OptionType.string,
            required=True
        )
    ])
    async def slash_pay(self, interaction: disnake.CommandInteraction, amount: int, info: str):
        await interaction.response.defer(ephemeral=True)
        await self.pay_legacy(interaction, amount, info)
    
def setup(bot: ClientUser):
    bot.add_cog(BankCog(bot))


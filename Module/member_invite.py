import disnake 
from disnake.ext import commands
from utils.ClientUser import ClientUser

class MemberInvite(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot: ClientUser = bot

    async def get_user_invite(self, context_manager: disnake.CommandInteraction, member: disnake.Member):
        invite = await context_manager.guild.invites()
        user_invites = set()
        user_has_invite = 0
        for invs in invite:
            if invs.inviter.id != member.id:
                continue

            if invs.uses < 1:
                continue
            
            if invs.target_type == disnake.InviteTarget.stream:
                user_invites.add(invs.target_user)
            elif invs.target_type == disnake.InviteTarget.unknown:
                user_has_invite  += invs.uses
            else:
                if invs.target_user is None:
                    continue
                user_invites.add(invs.target_user)

        return user_invites, user_has_invite
    
    async def build_list_invite(self, list_user_invites: set[disnake.Member] = None, user_has_invite: int = 0) -> str:
        if list_user_invites is None:
            return ""
        txt = ""
        for user in list_user_invites:
            txt += f"{user.id} - {user.display_name}\n"
        
        return txt if txt else "Không có người dùng nào được mời hoặc không lấy được dữ liệu."
    
    @commands.bot_has_guild_permissions(manage_guild=True)
    @commands.slash_command(name="list_invite", description="Liệt kê người dùng được mời bởi một thành viên")
    async def list_invite(self, interaction: disnake.CommandInteraction, member: disnake.Member = None):
        if member is None:
            member = interaction.author

        await interaction.response.defer(ephemeral=True)
        
        user_invites, user_has_invite = await self.get_user_invite(interaction, member)
        
        if user_invites is None and user_has_invite == 0:
            await interaction.edit_original_response("Không tìm thấy thành viên hoặc không có người dùng nào được mời.")
            return
        
        if user_invites:
            invite_list = await self.build_list_invite(user_invites)
        elif user_has_invite > 0:
            invite_list = f"Thành viên {member.display_name} đã mời {user_has_invite} người dùng."
        else:
            invite_list = "Không có người dùng nào được mời hoặc không lấy được dữ liệu."
        
        embed = disnake.Embed(title=f"Người dùng được mời bởi {member.display_name}", description=invite_list, color=disnake.Color.blue())
        await interaction.edit_original_response(embed=embed)

            
def setup(bot: ClientUser):
    bot.add_cog(MemberInvite(bot))
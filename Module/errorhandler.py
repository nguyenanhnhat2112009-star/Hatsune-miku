from disnake import AppCmdInter, Embed, Color, MessageFlags, NotFound, Colour, ApplicationCommandInteraction, AppCommandInter
from disnake.ext import commands

from utils.ClientUser import ClientUser
from utils.error import ClientException, parse_error, paginator, send_message
from traceback import print_exc
from typing import Union


class ErrorHandler(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot    
    
    @commands.Cog.listener('on_user_command_error')
    @commands.Cog.listener('on_message_command_error')
    @commands.Cog.listener('on_slash_command_error')
    async def on_interaction_command_error(self, inter: AppCmdInter, error: Exception):
        lang = await self.bot.database.cached_databases.get_language(inter.guild.id)
        await self.hander_error_cmd(ctx=inter, error=error, language=lang)
    
    async def hander_error_cmd(self, ctx: ApplicationCommandInteraction, error: Exception, language: str = 'vi'):
        
        if isinstance(error, ClientException):
            return
        
        error_msg = parse_error(ctx, error, language)
        
        if isinstance(error, NotFound) and str(error).endswith("Unknown Interaction"):
            return
        
        kwargs = {"text": ""}
        color = Color.red()

        if not error_msg:

            kwargs["embeds"] = Embed( # noqa
                color=color,
                title = "Đã có một sự cố xảy ra, nhưng đó không phải lỗi của bạn:",
                description=f"```py\n{repr(error)[:2030].replace(self.bot.http.token, 'mytoken')}```"
            )
        else:

            kwargs["embeds"] = []

            for p in paginator(error_msg):
                kwargs["embeds"].append(Embed(color=color, description=p))

        kwargs["flags"] = MessageFlags(suppress_notifications=True)

        try:
            await send_message(ctx, **kwargs)
            
        except ValueError:
            error_msg = parse_error(ctx, error, language)
        
            if isinstance(error, NotFound) and str(error).endswith("Unknown Interaction"):
                return
            
            kwargs = {"text": ""}
            color = Color.red()

            if not error_msg:

                kwargs["embed"] = Embed( # noqa
                    color=color,
                    title = "Đã có một sự cố xảy ra, nhưng đó không phải lỗi của bạn:",
                    description=f"```py\n{repr(error)[:2030].replace(self.bot.http.token, 'mytoken')}```"
                )
            else:

                kwargs["embed"] = []

                for p in paginator(error_msg):
                    kwargs["embed"].append(Embed(color=color, description=p))

            kwargs["flags"] = MessageFlags(suppress_notifications=True)
                    
            await send_message(ctx, **kwargs)
        except:
            print(("-"*50) + f"\n{error_msg}\n" + ("-"*50))
            print_exc()
        
    @commands.Cog.listener("on_command_error")
    async def prefix_command_handle(self, ctx: Union[AppCommandInter, commands.Context], error: Exception):
        
        if isinstance(error, commands.CommandNotFound):
            return
        
        if isinstance(error, commands.NotOwner):
            print(f"{ctx.author} [{ctx.author.id}] không sở hữu bot để sử dụng: {ctx.command.name}")
            return

        if isinstance(error, commands.MissingPermissions) and (await ctx.bot.is_owner(ctx.author)):
            try:
                await ctx.reinvoke()
            except Exception as e:
                await self.on_legacy_command_error(ctx, e)
            return

        lang = await self.bot.database.cached_databases.get_language(ctx.guild.id)

        error_msg = parse_error(ctx, error, lang)
        kwargs = {"content": ""}
       
        if not error_msg:

            if ctx.channel.permissions_for(ctx.guild.me).embed_links:
                kwargs["embed"] = Embed(
                    color=Colour.red(),
                    title="Đã có một sự cố đã xảy ra:",
                    description=f"```py\n{repr(error)[:2030].replace(self.bot.http.token, 'mytoken')}```"
                ).set_thumbnail(url="https://cdn.discordapp.com/attachments/1172052818501308427/1176426375704498257/1049220311318540338.png?ex=656ed370&is=655c5e70&hm=11d80b14a3ca28d04f7ac48d3a39b0c6d5947d20c9ae78cee9a4e511ce65f301&")

            else:
                kwargs["content"] += "\n**Đã có một sự cố đã xảy ra:**\n" \
                                     f"```py\n{repr(error)[:2030].replace(self.bot.http.token, 'mytoken')}```"

        else:

            if ctx.channel.permissions_for(ctx.guild.me).embed_links:
                kwargs["embed"] = Embed(color=Colour.red(), description=error_msg)
            else:
                kwargs["content"] += f"\n{error_msg}"

        try:
            kwargs["delete_after"] = error.delete_original
        except AttributeError:
            pass

        try:
            if error.self_delete and ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await ctx.message.delete()
        except:
            pass

        if hasattr(ctx, "inter"):
            if ctx.inter.response.is_done():
                func = ctx.inter.edit_original_message
            else:
                func = ctx.inter.response.edit_message
                kwargs.pop("delete_after", None)
        else:
            try:
                func = ctx.store_message.edit
            except:
                func = ctx.send

        kwargs["flags"] = MessageFlags(suppress_notifications=True)

        await func(**kwargs)
        
            
def setup(bot: ClientUser):
    bot.add_cog(ErrorHandler(bot))
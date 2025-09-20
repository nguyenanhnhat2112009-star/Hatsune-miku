import disnake
from disnake.ext import commands
import json
import os
from datetime import datetime
import asyncio

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "Data/ticket_config.json"
        self.tickets_file = "Data/tickets.json"
        self.load_config()
        self.load_tickets()
        
    def load_config(self):
        """Load ticket configuration"""
        default_config = {
            "panel_channel": None,
            "category_id": None,
            "support_roles": [],
            "max_tickets_per_user": 3,
            "ui_settings": {
                "panel": {
                    "title": "🎫 Hệ thống Ticket",
                    "description": "Nhấn nút bên dưới để tạo ticket",
                    "color": 0x00d4aa,
                    "image": "https://i.imgur.com/YQgzaOJ.png",
                    "button_label": "📋 Tạo Ticket",
                    "button_emoji": "🎫"
                }
            },
            "ticket_types": {
                "support": {
                    "name": "Hỗ trợ chung",
                    "emoji": "❓",
                    "description": "Cần hỗ trợ về bot hoặc server"
                },
                "report": {
                    "name": "Báo cáo",
                    "emoji": "⚠️", 
                    "description": "Báo cáo vi phạm hoặc lỗi"
                },
                "suggestion": {
                    "name": "Góp ý",
                    "emoji": "💡",
                    "description": "Đóng góp ý kiến cải thiện"
                }
            }
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save ticket configuration"""
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
    
    def load_tickets(self):
        """Load active tickets"""
        if os.path.exists(self.tickets_file):
            with open(self.tickets_file, 'r', encoding='utf-8') as f:
                self.tickets = json.load(f)
        else:
            self.tickets = {}
    
    def save_tickets(self):
        """Save active tickets"""
        os.makedirs(os.path.dirname(self.tickets_file), exist_ok=True)
        with open(self.tickets_file, 'w', encoding='utf-8') as f:
            json.dump(self.tickets, f, indent=4, ensure_ascii=False)

    @commands.slash_command(name="ticket")
    async def ticket_command(self, interaction):
        """Ticket system commands"""
        pass
    
    @ticket_command.sub_command(name="setup")
    async def setup_ticket(
        self, 
        interaction: disnake.ApplicationCommandInteraction,
        channel: disnake.TextChannel,
        category: disnake.CategoryChannel = None
    ):
        """
        Thiết lập hệ thống ticket
        
        Parameters
        ----------
        channel: Kênh để đặt panel ticket
        category: Category để tạo ticket (tùy chọn)
        """
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bạn cần quyền Administrator!", ephemeral=True)
            return
        
        self.config["panel_channel"] = channel.id
        if category:
            self.config["category_id"] = category.id
        
        self.save_config()
        
        embed = disnake.Embed(
            title="✅ Thiết lập thành công",
            description=f"Panel ticket sẽ được gửi tới {channel.mention}",
            color=0x00ff00
        )
        if category:
            embed.add_field(name="Category", value=category.name, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @ticket_command.sub_command(name="panel")
    async def send_panel(self, interaction: disnake.ApplicationCommandInteraction):
        """Gửi panel ticket"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bạn cần quyền Administrator!", ephemeral=True)
            return
        
        # Get UI settings
        ui_settings = self.config.get("ui_settings", {}).get("panel", {})
        title = ui_settings.get("title", "🎫 Hệ thống Ticket")
        description = ui_settings.get("description", "Nhấn nút bên dưới để tạo ticket")
        color = ui_settings.get("color", 0x00d4aa)
        image = ui_settings.get("image")
        
        # Create embed
        embed = disnake.Embed(
            title=title,
            description=description,
            color=color
        )
        
        if image:
            embed.set_image(url=image)
        
        # Create view
        view = TicketPanelView(self)
        
        await interaction.response.send_message(embed=embed, view=view)

    @ticket_command.sub_command(name="config")
    async def config_ticket(self, interaction: disnake.ApplicationCommandInteraction):
        """
        Cấu hình ticket system với giao diện đẹp
        """
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bạn cần quyền Administrator!", ephemeral=True)
            return

        # Show config panel with buttons
        current_config = self.config.get("ui_settings", {}).get("panel", {})

        embed = disnake.Embed(
            title="⚙️ Cấu hình Ticket System",
            description="🎨 **Chọn phần bạn muốn chỉnh sửa với giao diện đẹp như Discord!**",
            color=0x5865f2
        )

        # Create beautiful info display
        title_display = current_config.get('title', 'Chưa đặt')
        desc_display = current_config.get('description', 'Chưa đặt')
        if len(desc_display) > 50:
            desc_display = desc_display[:50] + "..."

        embed.add_field(
            name="📋 Thông tin hiện tại",
            value=f"""
            ```yaml
            Title: {title_display}
            Description: {desc_display}
            Color: {hex(current_config.get('color', 0x00d4aa))}
            Image: {'✅ Đã đặt' if current_config.get('image') else '❌ Chưa đặt'}
            Max tickets: {self.config.get('max_tickets_per_user', 3)}
            Button: {current_config.get('button_label', '📋 Tạo Ticket')}
            ```
            """,
            inline=False
        )

        embed.add_field(
            name="💡 Hướng dẫn",
            value="• **📝 Chỉnh sửa cơ bản**: Title và Description\n• **🎨 Chỉnh sửa giao diện**: Màu sắc, hình ảnh, button\n• **⚙️ Cài đặt nâng cao**: Giới hạn ticket, emoji\n• **👀 Xem trước**: Preview panel trước khi áp dụng",
            inline=False
        )

        embed.set_footer(text="💫 Giao diện modal đẹp như Discord • Click để chỉnh sửa!")

        view = SimpleConfigView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @ticket_command.sub_command(name="debug")
    async def debug_config(self, interaction: disnake.ApplicationCommandInteraction):
        """Debug config hiện tại"""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bạn cần quyền Administrator!", ephemeral=True)
            return

        import json
        config_text = json.dumps(self.config, indent=2, ensure_ascii=False)

        embed = disnake.Embed(
            title="🔍 Debug Config",
            description=f"```json\n{config_text}\n```",
            color=0xff9900
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ticket_command.sub_command(name="roles")
    async def manage_support_roles(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        action: str = commands.Param(choices=["add", "remove", "list"]),
        role: disnake.Role = None
    ):
        """
        Quản lý support roles

        Parameters
        ----------
        action: Hành động (add/remove/list)
        role: Role cần thêm/xóa
        """
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Bạn cần quyền Administrator!", ephemeral=True)
            return

        if action == "list":
            support_roles = self.config.get("support_roles", [])
            if not support_roles:
                embed = disnake.Embed(title="📋 Support Roles", description="Chưa có support role nào", color=0x7289da)
            else:
                roles_text = "\n".join([f"<@&{role_id}>" for role_id in support_roles])
                embed = disnake.Embed(title="📋 Support Roles", description=roles_text, color=0x7289da)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        if not role:
            await interaction.response.send_message("❌ Vui lòng chọn role!", ephemeral=True)
            return

        support_roles = self.config.get("support_roles", [])

        if action == "add":
            if role.id in support_roles:
                await interaction.response.send_message("❌ Role này đã là support role!", ephemeral=True)
                return
            support_roles.append(role.id)
            self.config["support_roles"] = support_roles
            self.save_config()

            embed = disnake.Embed(
                title="✅ Đã thêm support role",
                description=f"Role {role.mention} đã được thêm vào danh sách support",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

        elif action == "remove":
            if role.id not in support_roles:
                await interaction.response.send_message("❌ Role này không phải support role!", ephemeral=True)
                return
            support_roles.remove(role.id)
            self.config["support_roles"] = support_roles
            self.save_config()

            embed = disnake.Embed(
                title="✅ Đã xóa support role",
                description=f"Role {role.mention} đã được xóa khỏi danh sách support",
                color=0x00ff00
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @ticket_command.sub_command(name="stats")
    async def ticket_stats(self, interaction: disnake.ApplicationCommandInteraction):
        """Xem thống kê ticket"""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Bạn cần quyền Manage Messages!", ephemeral=True)
            return

        guild_tickets = [t for t in self.tickets.values() if t.get("guild_id") == interaction.guild.id]
        open_tickets = [t for t in guild_tickets if t.get("status") == "open"]

        # Count by type
        type_counts = {}
        for ticket in guild_tickets:
            ticket_type = ticket.get("type", "unknown")
            type_counts[ticket_type] = type_counts.get(ticket_type, 0) + 1

        embed = disnake.Embed(title="📊 Thống kê Ticket", color=0x7289da)
        embed.add_field(name="🎫 Tổng ticket", value=len(guild_tickets), inline=True)
        embed.add_field(name="🔓 Đang mở", value=len(open_tickets), inline=True)
        embed.add_field(name="🔒 Đã đóng", value=len(guild_tickets) - len(open_tickets), inline=True)

        if type_counts:
            ticket_types = self.config.get('ticket_types', {})
            types_text = "\n".join([f"{ticket_types.get(t, {}).get('emoji', '❓')} {t}: {count}"
                                   for t, count in type_counts.items()])
            embed.add_field(name="📋 Theo loại", value=types_text, inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @ticket_command.sub_command(name="close")
    async def force_close_ticket(
        self,
        interaction: disnake.ApplicationCommandInteraction,
        channel: disnake.TextChannel = None
    ):
        """
        Đóng ticket (dành cho staff)

        Parameters
        ----------
        channel: Kênh ticket cần đóng (mặc định là kênh hiện tại)
        """
        # Check permissions
        support_roles = self.config.get("support_roles", [])
        user_roles = [role.id for role in interaction.user.roles]

        if not (interaction.user.guild_permissions.manage_messages or
                any(role_id in user_roles for role_id in support_roles)):
            await interaction.response.send_message("❌ Bạn không có quyền đóng ticket!", ephemeral=True)
            return

        target_channel = channel or interaction.channel
        ticket_id = str(target_channel.id)

        if ticket_id not in self.tickets:
            await interaction.response.send_message("❌ Đây không phải kênh ticket!", ephemeral=True)
            return

        # Close ticket
        self.tickets[ticket_id]["status"] = "closed"
        self.save_tickets()

        embed = disnake.Embed(
            title="🔒 Ticket đã được đóng",
            description=f"Ticket được đóng bởi {interaction.user.mention}",
            color=0xff6b6b
        )

        await target_channel.send(embed=embed)
        await interaction.response.send_message("✅ Đã đóng ticket!", ephemeral=True)

        # Delete after 10 seconds
        await asyncio.sleep(10)
        await target_channel.delete()

class TicketPanelView(disnake.ui.View):
    def __init__(self, ticket_system):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system

        # Get button config
        ui_settings = ticket_system.config.get("ui_settings", {}).get("panel", {})
        button_label = ui_settings.get("button_label", "📋 Tạo Ticket")
        button_emoji = ui_settings.get("button_emoji", "🎫")

        # Create dynamic button
        button = disnake.ui.Button(
            label=button_label,
            emoji=button_emoji,
            style=disnake.ButtonStyle.primary,
            custom_id="create_ticket"
        )
        button.callback = self.create_ticket_button
        self.add_item(button)

    async def create_ticket_button(self, interaction: disnake.MessageInteraction):
        try:
            # Check max tickets
            user_tickets = [t for t in self.ticket_system.tickets.values()
                           if t.get("user_id") == interaction.user.id and t.get("guild_id") == interaction.guild.id and t.get("status") == "open"]
            max_tickets = self.ticket_system.config.get("max_tickets_per_user", 3)

            if len(user_tickets) >= max_tickets:
                embed = disnake.Embed(
                    title="❌ Quá nhiều ticket",
                    description=f"Bạn đã có {len(user_tickets)} ticket đang mở. Tối đa {max_tickets} ticket/người.",
                    color=0xff6b6b
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

            # Show ticket type selection
            embed = disnake.Embed(
                title="🎫 Tạo Ticket Mới",
                description="Chọn loại ticket phù hợp với vấn đề của bạn:",
                color=0x7289da
            )

            view = TicketTypeView(self.ticket_system)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Lỗi",
                description=f"Có lỗi xảy ra khi tạo ticket: {str(e)}",
                color=0xff6b6b
            )
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass

class TicketTypeView(disnake.ui.View):
    def __init__(self, ticket_system):
        super().__init__(timeout=300)
        self.ticket_system = ticket_system

        # Add select menu for ticket types
        options = []
        ticket_types = ticket_system.config.get("ticket_types", {})

        # If no ticket types configured, use default ones
        if not ticket_types:
            ticket_types = {
                "support": {
                    "name": "Hỗ trợ chung",
                    "emoji": "❓",
                    "description": "Cần hỗ trợ về bot hoặc server"
                },
                "report": {
                    "name": "Báo cáo",
                    "emoji": "⚠️",
                    "description": "Báo cáo vi phạm hoặc lỗi"
                },
                "suggestion": {
                    "name": "Góp ý",
                    "emoji": "💡",
                    "description": "Đóng góp ý kiến cải thiện"
                }
            }

        for type_key, type_info in ticket_types.items():
            options.append(disnake.SelectOption(
                label=type_info.get("name", type_key),
                description=type_info.get("description", "Không có mô tả"),
                emoji=type_info.get("emoji", "❓"),
                value=type_key
            ))

        select = disnake.ui.Select(
            placeholder="Chọn loại ticket...",
            options=options,
            custom_id="ticket_type_select"
        )
        select.callback = self.ticket_type_callback
        self.add_item(select)
    
    async def ticket_type_callback(self, interaction: disnake.MessageInteraction):
        try:
            ticket_type = interaction.values[0]
            ticket_types = self.ticket_system.config.get("ticket_types", {})

            # Use default if not found
            if ticket_type not in ticket_types:
                default_types = {
                    "support": {
                        "name": "Hỗ trợ chung",
                        "emoji": "❓",
                        "description": "Cần hỗ trợ về bot hoặc server"
                    },
                    "report": {
                        "name": "Báo cáo",
                        "emoji": "⚠️",
                        "description": "Báo cáo vi phạm hoặc lỗi"
                    },
                    "suggestion": {
                        "name": "Góp ý",
                        "emoji": "💡",
                        "description": "Đóng góp ý kiến cải thiện"
                    }
                }
                type_info = default_types.get(ticket_type, {
                    "name": "Hỗ trợ chung",
                    "emoji": "❓",
                    "description": "Cần hỗ trợ"
                })
            else:
                type_info = ticket_types[ticket_type]

            # Create ticket channel
            guild = interaction.guild
            category_id = self.ticket_system.config.get("category_id")
            category = guild.get_channel(category_id) if category_id else None

            # Create channel with safe name
            safe_username = ''.join(c for c in interaction.user.name if c.isalnum() or c in '-_')[:20]
            channel_name = f"ticket-{safe_username}-{len(self.ticket_system.tickets) + 1}"

            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(read_messages=False),
                interaction.user: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: disnake.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            # Add support roles
            for role_id in self.ticket_system.config.get("support_roles", []):
                role = guild.get_role(role_id)
                if role:
                    overwrites[role] = disnake.PermissionOverwrite(read_messages=True, send_messages=True)

            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )

            # Save ticket info
            ticket_id = str(channel.id)
            self.ticket_system.tickets[ticket_id] = {
                "user_id": interaction.user.id,
                "guild_id": guild.id,
                "channel_id": channel.id,
                "type": ticket_type,
                "created_at": datetime.now().isoformat(),
                "status": "open"
            }
            self.ticket_system.save_tickets()

            # Send welcome message
            embed = disnake.Embed(
                title=f"{type_info.get('emoji', '❓')} {type_info.get('name', 'Ticket')}",
                description=f"Chào {interaction.user.mention}! Ticket của bạn đã được tạo.\n\nMô tả chi tiết vấn đề của bạn và đợi staff hỗ trợ.",
                color=0x00d4aa
            )
            embed.set_footer(text=f"Ticket ID: {ticket_id}")

            view = TicketControlView(self.ticket_system)
            await channel.send(embed=embed, view=view)

            # Response to user
            embed = disnake.Embed(
                title="✅ Ticket đã được tạo",
                description=f"Ticket của bạn: {channel.mention}",
                color=0x00ff00
            )
            await interaction.response.edit_message(embed=embed, view=None)

        except Exception as e:
            embed = disnake.Embed(
                title="❌ Lỗi tạo ticket",
                description=f"Có lỗi xảy ra: {str(e)}",
                color=0xff6b6b
            )
            try:
                await interaction.response.edit_message(embed=embed, view=None)
            except:
                await interaction.followup.send(embed=embed, ephemeral=True)

class TicketControlView(disnake.ui.View):
    def __init__(self, ticket_system):
        super().__init__(timeout=None)
        self.ticket_system = ticket_system
    
    @disnake.ui.button(label="🔒 Đóng Ticket", style=disnake.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            ticket_id = str(interaction.channel.id)

            if ticket_id not in self.ticket_system.tickets:
                await interaction.response.send_message("❌ Không tìm thấy ticket!", ephemeral=True)
                return

            # Check if user can close ticket
            ticket_info = self.ticket_system.tickets[ticket_id]
            support_roles = self.ticket_system.config.get("support_roles", [])
            user_roles = [role.id for role in interaction.user.roles]

            can_close = (
                interaction.user.id == ticket_info.get("user_id") or  # Ticket owner
                interaction.user.guild_permissions.manage_messages or  # Staff permission
                any(role_id in user_roles for role_id in support_roles)  # Support role
            )

            if not can_close:
                await interaction.response.send_message("❌ Bạn không có quyền đóng ticket này!", ephemeral=True)
                return

            # Confirm close
            embed = disnake.Embed(
                title="⚠️ Xác nhận đóng ticket",
                description="Bạn có chắc muốn đóng ticket này?",
                color=0xff9900
            )

            view = ConfirmCloseView(self.ticket_system, ticket_id)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        except Exception as e:
            embed = disnake.Embed(
                title="❌ Lỗi",
                description=f"Có lỗi xảy ra: {str(e)}",
                color=0xff6b6b
            )
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    await interaction.followup.send(embed=embed, ephemeral=True)
            except:
                pass

class ConfirmCloseView(disnake.ui.View):
    def __init__(self, ticket_system, ticket_id):
        super().__init__(timeout=60)
        self.ticket_system = ticket_system
        self.ticket_id = ticket_id

    @disnake.ui.button(label="✅ Xác nhận", style=disnake.ButtonStyle.danger)
    async def confirm_close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            # Mark ticket as closed instead of deleting immediately
            if self.ticket_id in self.ticket_system.tickets:
                self.ticket_system.tickets[self.ticket_id]["status"] = "closed"
                self.ticket_system.save_tickets()

            await interaction.response.edit_message(
                embed=disnake.Embed(title="✅ Ticket sẽ bị xóa sau 5 giây", color=0x00ff00),
                view=None
            )

            await asyncio.sleep(5)
            try:
                await interaction.channel.delete()
            except:
                # Channel might already be deleted or no permission
                pass

        except Exception as e:
            try:
                await interaction.response.edit_message(
                    embed=disnake.Embed(title=f"❌ Lỗi: {str(e)}", color=0xff6b6b),
                    view=None
                )
            except:
                pass

    @disnake.ui.button(label="❌ Hủy", style=disnake.ButtonStyle.secondary)
    async def cancel_close(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            await interaction.response.edit_message(
                embed=disnake.Embed(title="❌ Đã hủy", color=0xff6b6b),
                view=None
            )
        except Exception as e:
            pass

# ==================== CONFIG PANEL VIEWS ====================

class SimpleConfigView(disnake.ui.View):
    def __init__(self, ticket_system):
        super().__init__(timeout=300)
        self.ticket_system = ticket_system

    @disnake.ui.button(label="📝 Chỉnh sửa cơ bản", style=disnake.ButtonStyle.primary, row=0)
    async def edit_basic(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            modal = BasicConfigModal(self.ticket_system)
            await interaction.response.send_modal(modal)
        except Exception as e:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Lỗi: {str(e)}", ephemeral=True)
            except:
                pass

    @disnake.ui.button(label="🎨 Chỉnh sửa giao diện", style=disnake.ButtonStyle.secondary, row=0)
    async def edit_appearance(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            modal = AppearanceConfigModal(self.ticket_system)
            await interaction.response.send_modal(modal)
        except Exception as e:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Lỗi: {str(e)}", ephemeral=True)
            except:
                pass

    @disnake.ui.button(label="⚙️ Cài đặt nâng cao", style=disnake.ButtonStyle.secondary, row=1)
    async def edit_advanced(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            modal = AdvancedConfigModal(self.ticket_system)
            await interaction.response.send_modal(modal)
        except Exception as e:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Lỗi: {str(e)}", ephemeral=True)
            except:
                pass

    @disnake.ui.button(label="👀 Xem trước", style=disnake.ButtonStyle.success, row=1)
    async def preview_panel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        try:
            # Create preview embed
            ui_settings = self.ticket_system.config.get("ui_settings", {}).get("panel", {})
            title = ui_settings.get("title", "🎫 Hệ thống Ticket")
            description = ui_settings.get("description", "Nhấn nút bên dưới để tạo ticket")
            color = ui_settings.get("color", 0x00d4aa)
            image = ui_settings.get("image")

            embed = disnake.Embed(
                title=f"🔍 Xem trước: {title}",
                description=description,
                color=color
            )

            if image:
                embed.set_image(url=image)

            embed.set_footer(text="Đây là bản xem trước panel ticket")

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Lỗi: {str(e)}", ephemeral=True)
            except:
                pass



class BasicConfigModal(disnake.ui.Modal):
    def __init__(self, ticket_system):
        self.ticket_system = ticket_system
        current_config = ticket_system.config.get("ui_settings", {}).get("panel", {})

        # Create components first
        components = [
            disnake.ui.TextInput(
                label="Title",
                placeholder="🎫 Hệ thống Ticket",
                value=current_config.get("title", ""),
                style=disnake.TextInputStyle.short,
                max_length=100,
                required=True,
                custom_id="title_input"
            ),
            disnake.ui.TextInput(
                label="Description",
                placeholder="Nhấn nút bên dưới để tạo ticket",
                value=current_config.get("description", ""),
                style=disnake.TextInputStyle.paragraph,
                max_length=4000,
                required=True,
                custom_id="description_input"
            )
        ]

        super().__init__(
            title="📝 Chỉnh sửa thông tin cơ bản",
            components=components,
            timeout=300
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        try:
            # Get values from interaction data
            title = interaction.text_values["title_input"]
            description = interaction.text_values["description_input"]

            # Update config
            if "ui_settings" not in self.ticket_system.config:
                self.ticket_system.config["ui_settings"] = {}
            if "panel" not in self.ticket_system.config["ui_settings"]:
                self.ticket_system.config["ui_settings"]["panel"] = {}

            self.ticket_system.config["ui_settings"]["panel"]["title"] = title
            self.ticket_system.config["ui_settings"]["panel"]["description"] = description
            self.ticket_system.save_config()

            embed = disnake.Embed(
                title="✅ Cập nhật thành công!",
                description=f"**Title:** {title}\n**Description:** {description[:100]}{'...' if len(description) > 100 else ''}",
                color=0x00ff00
            )
            embed.set_footer(text="Thông tin cơ bản đã được cập nhật")

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Lỗi: {str(e)}", ephemeral=True)
            except:
                pass

class AppearanceConfigModal(disnake.ui.Modal):
    def __init__(self, ticket_system):
        self.ticket_system = ticket_system
        current_config = ticket_system.config.get("ui_settings", {}).get("panel", {})

        # Create components first
        components = [
            disnake.ui.TextInput(
                label="Hex Color",
                placeholder="#00d4aa",
                value=hex(current_config.get("color", 0x00d4aa)),
                style=disnake.TextInputStyle.short,
                max_length=7,
                required=True,
                custom_id="color_input"
            ),
            disnake.ui.TextInput(
                label="Image URL",
                placeholder="https://i.imgur.com/YQgzaOJ.png",
                value=current_config.get("image", ""),
                style=disnake.TextInputStyle.short,
                max_length=500,
                required=False,
                custom_id="image_input"
            ),
            disnake.ui.TextInput(
                label="Button Label",
                placeholder="📋 Tạo Ticket",
                value=current_config.get("button_label", "📋 Tạo Ticket"),
                style=disnake.TextInputStyle.short,
                max_length=80,
                required=True,
                custom_id="button_input"
            )
        ]

        super().__init__(
            title="🎨 Chỉnh sửa giao diện",
            components=components,
            timeout=300
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        try:
            # Get values from interaction data
            color_hex = interaction.text_values["color_input"]
            image_url = interaction.text_values["image_input"]
            button_label = interaction.text_values["button_input"]

            # Validate color
            try:
                color_value = int(color_hex.replace("#", ""), 16)
            except ValueError:
                await interaction.response.send_message("❌ Màu không hợp lệ! Sử dụng format hex như #00d4aa", ephemeral=True)
                return

            # Update config
            if "ui_settings" not in self.ticket_system.config:
                self.ticket_system.config["ui_settings"] = {}
            if "panel" not in self.ticket_system.config["ui_settings"]:
                self.ticket_system.config["ui_settings"]["panel"] = {}

            self.ticket_system.config["ui_settings"]["panel"]["color"] = color_value
            self.ticket_system.config["ui_settings"]["panel"]["button_label"] = button_label

            if image_url:
                self.ticket_system.config["ui_settings"]["panel"]["image"] = image_url

            self.ticket_system.save_config()

            embed = disnake.Embed(
                title="✅ Giao diện đã được cập nhật!",
                description=f"**Color:** {color_hex}\n**Button:** {button_label}\n**Image:** {'Đã đặt' if image_url else 'Không thay đổi'}",
                color=color_value
            )
            embed.set_footer(text="Giao diện đã được cập nhật")

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Lỗi: {str(e)}", ephemeral=True)
            except:
                pass

class AdvancedConfigModal(disnake.ui.Modal):
    def __init__(self, ticket_system):
        self.ticket_system = ticket_system

        # Create components first
        components = [
            disnake.ui.TextInput(
                label="Max Tickets Per User",
                placeholder="3",
                value=str(ticket_system.config.get("max_tickets_per_user", 3)),
                style=disnake.TextInputStyle.short,
                max_length=2,
                required=True,
                custom_id="max_tickets_input"
            ),
            disnake.ui.TextInput(
                label="Button Emoji",
                placeholder="🎫",
                value=ticket_system.config.get("ui_settings", {}).get("panel", {}).get("button_emoji", "🎫"),
                style=disnake.TextInputStyle.short,
                max_length=10,
                required=False,
                custom_id="emoji_input"
            )
        ]

        super().__init__(
            title="⚙️ Cài đặt nâng cao",
            components=components,
            timeout=300
        )

    async def callback(self, interaction: disnake.ModalInteraction):
        try:
            # Get values from interaction data
            max_tickets = interaction.text_values["max_tickets_input"]
            button_emoji = interaction.text_values["emoji_input"]

            # Validate max tickets
            try:
                max_tickets_int = int(max_tickets)
                if max_tickets_int < 1 or max_tickets_int > 10:
                    raise ValueError
            except ValueError:
                await interaction.response.send_message("❌ Số ticket tối đa phải từ 1-10!", ephemeral=True)
                return

            # Update config
            self.ticket_system.config["max_tickets_per_user"] = max_tickets_int

            if "ui_settings" not in self.ticket_system.config:
                self.ticket_system.config["ui_settings"] = {}
            if "panel" not in self.ticket_system.config["ui_settings"]:
                self.ticket_system.config["ui_settings"]["panel"] = {}

            if button_emoji:
                self.ticket_system.config["ui_settings"]["panel"]["button_emoji"] = button_emoji

            self.ticket_system.save_config()

            embed = disnake.Embed(
                title="✅ Cài đặt nâng cao đã được cập nhật!",
                description=f"**Max tickets:** {max_tickets_int}\n**Button emoji:** {button_emoji or 'Không thay đổi'}",
                color=0x00ff00
            )
            embed.set_footer(text="Cài đặt nâng cao đã được cập nhật")

            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            try:
                if not interaction.response.is_done():
                    await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
                else:
                    await interaction.followup.send(f"❌ Lỗi: {str(e)}", ephemeral=True)
            except:
                pass

def setup(bot):
    bot.add_cog(TicketSystem(bot))

"""
Controller Integration Module
Tích hợp enhanced controller vào music player system
"""

from disnake import Message, MessageInteraction, ButtonInteraction
from typing import TYPE_CHECKING, Optional
import logging

if TYPE_CHECKING:
    from musicCore import MusicPlayer

logger = logging.getLogger(__name__)

class ControllerIntegration:
    """Class để tích hợp controller vào music player"""
    
    @staticmethod
    async def send_controller(player: 'MusicPlayer', channel, language: str = 'vi') -> Optional[Message]:
        """Gửi controller message mới"""
        try:
            from .player_controler import render_player
            from .auto_updater import start_controller_updates
            
            # Render controller
            controller_data = render_player(player, language)
            if not controller_data:
                return None
            
            # Gửi message
            message = await channel.send(
                embed=controller_data["embed"],
                view=controller_data["view"]
            )
            
            # Lưu reference và bắt đầu auto-update
            player.player_controller = message
            await start_controller_updates(player)
            
            logger.info(f"Sent new controller for guild {player.guild.id}")
            return message
            
        except Exception as e:
            logger.error(f"Error sending controller: {e}")
            return None
    
    @staticmethod
    async def update_controller(player: 'MusicPlayer', language: str = 'vi') -> bool:
        """Cập nhật controller hiện tại"""
        try:
            if not player.player_controller:
                return False
            
            from .player_controler import render_player
            
            # Render controller mới
            controller_data = render_player(player, language)
            if not controller_data:
                return False
            
            # Cập nhật message
            await player.player_controller.edit(
                embed=controller_data["embed"],
                view=controller_data["view"]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating controller: {e}")
            return False
    
    @staticmethod
    async def handle_controller_interaction(interaction: MessageInteraction):
        """Xử lý tương tác với controller"""
        try:
            from .button_handlers import handle_button_interaction
            
            # Kiểm tra xem có phải button interaction không
            if hasattr(interaction.data, 'custom_id'):
                await handle_button_interaction(interaction)
            
        except Exception as e:
            logger.error(f"Error handling controller interaction: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("❌ Đã xảy ra lỗi!", ephemeral=True)

class ControllerEventHandler:
    """Event handler cho controller events"""
    
    @staticmethod
    async def on_track_start(player: 'MusicPlayer'):
        """Được gọi khi track mới bắt đầu"""
        try:
            from .auto_updater import on_track_start
            await on_track_start(player)
        except Exception as e:
            logger.error(f"Error in on_track_start: {e}")
    
    @staticmethod
    async def on_track_end(player: 'MusicPlayer'):
        """Được gọi khi track kết thúc"""
        try:
            from .auto_updater import on_track_end
            await on_track_end(player)
        except Exception as e:
            logger.error(f"Error in on_track_end: {e}")
    
    @staticmethod
    async def on_player_pause(player: 'MusicPlayer'):
        """Được gọi khi player pause"""
        try:
            from .auto_updater import on_player_pause
            await on_player_pause(player)
        except Exception as e:
            logger.error(f"Error in on_player_pause: {e}")
    
    @staticmethod
    async def on_player_resume(player: 'MusicPlayer'):
        """Được gọi khi player resume"""
        try:
            from .auto_updater import on_player_resume
            await on_player_resume(player)
        except Exception as e:
            logger.error(f"Error in on_player_resume: {e}")
    
    @staticmethod
    async def on_volume_change(player: 'MusicPlayer'):
        """Được gọi khi volume thay đổi"""
        try:
            from .auto_updater import on_volume_change
            await on_volume_change(player)
        except Exception as e:
            logger.error(f"Error in on_volume_change: {e}")
    
    @staticmethod
    async def on_player_disconnect(player: 'MusicPlayer'):
        """Được gọi khi player disconnect"""
        try:
            from .auto_updater import on_player_disconnect
            await on_player_disconnect(player)
        except Exception as e:
            logger.error(f"Error in on_player_disconnect: {e}")

# Helper functions để dễ sử dụng
async def send_enhanced_controller(player: 'MusicPlayer', channel, language: str = 'vi') -> Optional[Message]:
    """Helper function để gửi enhanced controller"""
    return await ControllerIntegration.send_controller(player, channel, language)

async def update_enhanced_controller(player: 'MusicPlayer', language: str = 'vi') -> bool:
    """Helper function để cập nhật enhanced controller"""
    return await ControllerIntegration.update_controller(player, language)

async def handle_enhanced_controller_interaction(interaction: MessageInteraction):
    """Helper function để xử lý controller interaction"""
    await ControllerIntegration.handle_controller_interaction(interaction)

# Event handlers
async def setup_controller_events(player: 'MusicPlayer'):
    """Setup event handlers cho controller"""
    # Đây là nơi bạn có thể hook vào các events của player
    # Ví dụ: player.on_track_start = ControllerEventHandler.on_track_start
    pass

"""
Auto Controller Updater
Tự động cập nhật controller khi có thay đổi
"""

import asyncio
from typing import TYPE_CHECKING, Optional
from disnake import Message, NotFound, HTTPException
import logging

if TYPE_CHECKING:
    from musicCore import MusicPlayer

logger = logging.getLogger(__name__)

class ControllerAutoUpdater:
    """Class quản lý việc tự động cập nhật controller"""
    
    def __init__(self, player: 'MusicPlayer'):
        self.player = player
        self.update_task: Optional[asyncio.Task] = None
        self.last_update_time = 0
        self.update_interval = 5  # Cập nhật mỗi 5 giây
        self.is_running = False
    
    def start_auto_update(self):
        """Bắt đầu tự động cập nhật controller"""
        if not self.is_running:
            self.is_running = True
            self.update_task = asyncio.create_task(self._update_loop())
            logger.info(f"Started auto-updater for guild {self.player.guild.id}")
    
    def stop_auto_update(self):
        """Dừng tự động cập nhật controller"""
        self.is_running = False
        if self.update_task and not self.update_task.done():
            self.update_task.cancel()
            logger.info(f"Stopped auto-updater for guild {self.player.guild.id}")
    
    async def _update_loop(self):
        """Loop chính để cập nhật controller"""
        while self.is_running:
            try:
                await asyncio.sleep(self.update_interval)
                
                if not self.player.current or not self.player.player_controller:
                    continue
                
                # Chỉ cập nhật nếu đang phát và không phải stream
                if not self.player.paused and not self.player.current.stream:
                    await self.update_controller()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in controller auto-updater: {e}")
                await asyncio.sleep(1)  # Ngắt nghỉ trước khi thử lại
    
    async def update_controller(self, force: bool = False):
        """Cập nhật controller message"""
        try:
            if not self.player.player_controller:
                return
            
            # Import render function
            from utils.controller.player_controler import render_player
            
            # Lấy ngôn ngữ từ database
            language = await self.player.client.database.cached_databases.get_language(self.player.guild.id)
            
            # Render controller mới
            controller_data = render_player(self.player, language)
            if not controller_data:
                return
            
            # Cập nhật message
            await self.player.player_controller.edit(
                embed=controller_data["embed"],
                view=controller_data["view"]
            )
            
            logger.debug(f"Updated controller for guild {self.player.guild.id}")
            
        except NotFound:
            # Message đã bị xóa
            self.player.player_controller = None
            self.stop_auto_update()
            logger.warning(f"Controller message not found for guild {self.player.guild.id}")
            
        except HTTPException as e:
            logger.error(f"HTTP error updating controller: {e}")
            
        except Exception as e:
            logger.error(f"Error updating controller: {e}")
    
    async def force_update(self):
        """Buộc cập nhật controller ngay lập tức"""
        await self.update_controller(force=True)

class ControllerManager:
    """Manager để quản lý tất cả các controller updaters"""
    
    _instances = {}
    
    @classmethod
    def get_updater(cls, player: 'MusicPlayer') -> ControllerAutoUpdater:
        """Lấy hoặc tạo updater cho player"""
        guild_id = player.guild.id
        
        if guild_id not in cls._instances:
            cls._instances[guild_id] = ControllerAutoUpdater(player)
        
        return cls._instances[guild_id]
    
    @classmethod
    def remove_updater(cls, guild_id: int):
        """Xóa updater cho guild"""
        if guild_id in cls._instances:
            updater = cls._instances[guild_id]
            updater.stop_auto_update()
            del cls._instances[guild_id]
    
    @classmethod
    def stop_all_updaters(cls):
        """Dừng tất cả updaters"""
        for updater in cls._instances.values():
            updater.stop_auto_update()
        cls._instances.clear()

# Helper functions
async def start_controller_updates(player: 'MusicPlayer'):
    """Bắt đầu auto-update cho player"""
    updater = ControllerManager.get_updater(player)
    updater.start_auto_update()

async def stop_controller_updates(player: 'MusicPlayer'):
    """Dừng auto-update cho player"""
    ControllerManager.remove_updater(player.guild.id)

async def update_controller_now(player: 'MusicPlayer'):
    """Cập nhật controller ngay lập tức"""
    updater = ControllerManager.get_updater(player)
    await updater.force_update()

# Event handlers để tự động cập nhật khi có thay đổi
async def on_track_start(player: 'MusicPlayer'):
    """Được gọi khi bài hát mới bắt đầu"""
    await update_controller_now(player)
    await start_controller_updates(player)

async def on_track_end(player: 'MusicPlayer'):
    """Được gọi khi bài hát kết thúc"""
    await update_controller_now(player)

async def on_player_pause(player: 'MusicPlayer'):
    """Được gọi khi player bị pause"""
    await update_controller_now(player)

async def on_player_resume(player: 'MusicPlayer'):
    """Được gọi khi player được resume"""
    await update_controller_now(player)
    await start_controller_updates(player)

async def on_volume_change(player: 'MusicPlayer'):
    """Được gọi khi âm lượng thay đổi"""
    await update_controller_now(player)

async def on_loop_change(player: 'MusicPlayer'):
    """Được gọi khi chế độ lặp thay đổi"""
    await update_controller_now(player)

async def on_shuffle_change(player: 'MusicPlayer'):
    """Được gọi khi chế độ shuffle thay đổi"""
    await update_controller_now(player)

async def on_player_disconnect(player: 'MusicPlayer'):
    """Được gọi khi player ngắt kết nối"""
    stop_controller_updates(player)

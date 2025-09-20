"""
Enhanced Button Handlers for Music Player Controller
Xử lý các tương tác button cho music player controller
"""

from disnake import MessageInteraction, ButtonStyle
from typing import TYPE_CHECKING
import asyncio

if TYPE_CHECKING:
    from musicCore import MusicPlayer

class PlayerButtonHandlers:
    """Class xử lý các button interactions cho music player"""
    
    @staticmethod
    async def handle_pause_resume(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button pause/resume"""
        try:
            if player.paused:
                await player.resume()
                await interaction.response.send_message("▶️ Đã tiếp tục phát nhạc!", ephemeral=True)
            else:
                await player.pause()
                await interaction.response.send_message("⏸️ Đã tạm dừng nhạc!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_stop(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button stop"""
        try:
            await player.stop()
            await interaction.response.send_message("⏹️ Đã dừng phát nhạc và ngắt kết nối!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_previous(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button previous track"""
        try:
            if len(player.queue.played) == 0:
                await interaction.response.send_message("❌ Không có bài hát trước đó!", ephemeral=True)
                return
            
            await player.previous()
            await interaction.response.send_message("⏮️ Đã chuyển về bài hát trước!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_next(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button next track"""
        try:
            if len(player.queue.next_track) == 0:
                await interaction.response.send_message("❌ Không có bài hát tiếp theo!", ephemeral=True)
                return
            
            await player.skip()
            await interaction.response.send_message("⏭️ Đã chuyển sang bài hát tiếp theo!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_volume_down(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button volume down"""
        try:
            new_volume = max(0, player.player_volume - 10)
            await player.set_volume(new_volume)
            await interaction.response.send_message(f"🔉 Âm lượng: {new_volume}%", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_volume_up(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button volume up"""
        try:
            new_volume = min(100, player.player_volume + 10)
            await player.set_volume(new_volume)
            await interaction.response.send_message(f"🔊 Âm lượng: {new_volume}%", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_loop(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button loop mode"""
        try:
            from utils.conv import LoopMODE
            
            if player.queue.loop == LoopMODE.OFF:
                player.queue.loop = LoopMODE.SONG
                message = "🔂 Đã bật lặp bài hát hiện tại!"
            elif player.queue.loop == LoopMODE.SONG:
                player.queue.loop = LoopMODE.PLAYLIST
                message = "🔁 Đã bật lặp danh sách phát!"
            else:
                player.queue.loop = LoopMODE.OFF
                message = "➡️ Đã tắt chế độ lặp!"
            
            await interaction.response.send_message(message, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_shuffle(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button shuffle"""
        try:
            player.queue.shuffle = not player.queue.shuffle
            status = "bật" if player.queue.shuffle else "tắt"
            emoji = "🔀" if player.queue.shuffle else "📋"
            await interaction.response.send_message(f"{emoji} Đã {status} chế độ trộn bài!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_autoplay(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button autoplay"""
        try:
            player.is_autoplay_mode = not player.is_autoplay_mode
            status = "bật" if player.is_autoplay_mode else "tắt"
            emoji = "♻️" if player.is_autoplay_mode else "⏹️"
            await interaction.response.send_message(f"{emoji} Đã {status} chế độ tự động phát!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)
    
    @staticmethod
    async def handle_queue(interaction: MessageInteraction, player: 'MusicPlayer'):
        """Xử lý button queue - hiển thị hàng đợi"""
        try:
            from disnake import Embed
            from utils.conv import trim_text, time_format
            
            embed = Embed(title="📋 Hàng đợi phát nhạc", color=0x00ff00)
            
            # Bài đang phát
            if player.current:
                embed.add_field(
                    name="🎵 Đang phát",
                    value=f"**{trim_text(player.current.title, 50)}**\n👤 {trim_text(player.current.author, 30)}",
                    inline=False
                )
            
            # Bài tiếp theo
            if player.queue.next_track:
                next_songs = []
                for i, track in enumerate(player.queue.next_track[:5]):  # Hiển thị 5 bài đầu
                    next_songs.append(f"`{i+1}.` **{trim_text(track.title, 40)}**")
                
                if len(player.queue.next_track) > 5:
                    next_songs.append(f"... và {len(player.queue.next_track) - 5} bài khác")
                
                embed.add_field(
                    name="⏭️ Tiếp theo",
                    value="\n".join(next_songs),
                    inline=False
                )
            else:
                embed.add_field(
                    name="⏭️ Tiếp theo",
                    value="*Không có bài hát trong hàng đợi*",
                    inline=False
                )
            
            # Thống kê
            total_duration = sum(track.length for track in player.queue.next_track if not track.stream)
            embed.set_footer(text=f"📊 Tổng cộng: {len(player.queue.next_track)} bài • {time_format(total_duration)}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Lỗi: {str(e)}", ephemeral=True)

# Dictionary mapping custom_id to handler functions
BUTTON_HANDLERS = {
    "player_controller_pause_resume_btn": PlayerButtonHandlers.handle_pause_resume,
    "player_controller_stop_btn": PlayerButtonHandlers.handle_stop,
    "player_controller_prev_track_btn": PlayerButtonHandlers.handle_previous,
    "player_controller_next_track_btn": PlayerButtonHandlers.handle_next,
    "player_controller_volume_down_btn": PlayerButtonHandlers.handle_volume_down,
    "player_controller_volume_up_btn": PlayerButtonHandlers.handle_volume_up,
    "player_controller_loop_btn": PlayerButtonHandlers.handle_loop,
    "player_controller_shuffle_btn": PlayerButtonHandlers.handle_shuffle,
    "player_controller_autoplay_btn": PlayerButtonHandlers.handle_autoplay,
    "player_controller_queue_btn": PlayerButtonHandlers.handle_queue,
}

async def handle_button_interaction(interaction: MessageInteraction):
    """Main function để xử lý button interactions"""
    custom_id = interaction.data.custom_id
    
    # Lấy player từ guild
    player = interaction.guild.voice_client
    if not player:
        await interaction.response.send_message("❌ Bot không đang phát nhạc!", ephemeral=True)
        return
    
    # Kiểm tra quyền
    if not interaction.author.voice or interaction.author.voice.channel != player.channel:
        await interaction.response.send_message("❌ Bạn phải ở cùng kênh voice với bot!", ephemeral=True)
        return
    
    # Xử lý button
    handler = BUTTON_HANDLERS.get(custom_id)
    if handler:
        await handler(interaction, player)
    else:
        await interaction.response.send_message("❌ Button không được hỗ trợ!", ephemeral=True)

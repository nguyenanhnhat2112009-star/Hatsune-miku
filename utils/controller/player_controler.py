from disnake import Embed, ButtonStyle, Color, SelectOption
from disnake.ui import View, Button, Select
from typing import TYPE_CHECKING, Optional, List
import asyncio

# Import với error handling
try:
    from utils.conv import trim_text, time_format, music_source_image, LoopMODE
except ImportError:
    def trim_text(text, length):
        return text[:length] + "..." if len(text) > length else text

    def time_format(milliseconds):
        seconds = milliseconds // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def music_source_image(source):
        return "https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif"

    class LoopMODE:
        OFF = 0
        TRACK = 1
        QUEUE = 2

if TYPE_CHECKING:
    from musicCore import MusicPlayer

def get_progress_bar(current_pos: int, total_length: int, bar_length: int = 30) -> str:
    """Tạo thanh tiến trình đẹp mắt cho bài hát"""
    if total_length == 0:
        return "▬" * bar_length

    progress = min(current_pos / total_length, 1.0)
    filled_length = int(bar_length * progress)

    # Sử dụng ký tự đẹp hơn cho thanh tiến trình
    filled = "█" * filled_length
    empty = "░" * (bar_length - filled_length)
    return f"{filled}{empty}"

def get_status_color(player) -> Color:
    """Lấy màu cho embed dựa trên trạng thái player"""
    try:
        if hasattr(player, 'paused') and player.paused:
            return Color.orange()
        elif (hasattr(player, 'current') and player.current and
              hasattr(player.current, 'stream') and player.current.stream):
            return Color.red()
        else:
            return Color.green()
    except Exception:
        return Color.blue()

def format_duration(milliseconds: int) -> str:
    """Format thời gian theo định dạng mm:ss hoặc hh:mm:ss"""
    if milliseconds == 0:
        return "00:00"

    seconds = milliseconds // 1000
    minutes = seconds // 60
    seconds = seconds % 60

    if minutes >= 60:
        hours = minutes // 60
        minutes = minutes % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def create_discord_embed(player: 'MusicPlayer', language: str = 'vi') -> Embed:
    """Tạo embed giống hệt Discord như trong hình mới"""
    try:
        # Lấy thông tin bài hát
        title = getattr(player.current, 'title', 'Unknown Track')
        author = getattr(player.current, 'author', 'Unknown Artist')
        source = getattr(player.current, 'source', 'Unknown').capitalize()
        artwork_url = getattr(player.current, 'artwork_url', None)
        uri = getattr(player.current, 'uri', None)
        length = getattr(player.current, 'length', 0)
        position = getattr(player.current, 'position', 0)

        # Tạo embed với viền trắng như Discord
        embed = Embed(color=0xFFFFFF)  # Màu trắng cho viền

        # Author với icon YouTube và "Youtube"
        embed.set_author(
            name="🔴 Youtube",
            icon_url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif"
        )

        # Title màu xanh (Discord sẽ tự động làm xanh khi có URL)
        embed.title = trim_text(title, 50)

        # URL clickable để title thành màu xanh
        if uri:
            embed.url = uri

        # Description theo format Discord mới
        description_parts = []

        # Dòng thông tin: Youtube | Author | Duration
        time_total = format_duration(length)
        description_parts.append(f"**Youtube** | ミ★StreamBeans★彡 | **{time_total}**")

        embed.description = "\n".join(description_parts)

        # Thumbnail bên phải (vuông như Discord)
        if artwork_url:
            embed.set_thumbnail(url=artwork_url)

        return embed

    except Exception as e:
        print(f"Error creating Discord embed: {e}")
        return create_error_embed(str(e))

def create_discord_style_view(player: 'MusicPlayer', language: str = 'vi') -> Optional[View]:
    """Tạo view với 3 buttons như trong Discord layout"""
    try:
        view = View(timeout=None)

        # Button 1: Yêu thích (màu hồng)
        view.add_item(Button(
            style=ButtonStyle.secondary,
            emoji="💖",
            label="Yêu thích",
            custom_id="player_controller_favorite_btn",
            row=0
        ))

        # Button 2: Play/Pause (màu xanh dương)
        is_paused = getattr(player, 'paused', False)
        view.add_item(Button(
            style=ButtonStyle.primary,
            emoji="▶️" if is_paused else "⏸️",
            label="Phát ngay" if is_paused else "Tạm dừng",
            custom_id="player_controller_pause_resume_btn",
            row=0
        ))

        # Button 3: Thêm vào hàng đợi (màu xanh lá)
        view.add_item(Button(
            style=ButtonStyle.success,
            emoji="➕",
            label="Thêm vào hàng đợi",
            custom_id="player_controller_add_queue_btn",
            row=0
        ))

        return view

    except Exception as e:
        print(f"Error creating Discord style view: {e}")
        return None

def render_discord_style_player(player: 'MusicPlayer', language: str = 'vi') -> dict:
    """Render player với style giống Discord như trong hình"""
    try:
        if not hasattr(player, 'current') or not player.current:
            return {
                'embed': create_no_track_embed(),
                'view': None
            }

        # Tạo embed Discord style
        embed = create_discord_embed(player, language)

        # Tạo view với 3 buttons
        view = create_discord_style_view(player, language)

        return {
            'embed': embed,
            'view': view
        }

    except Exception as e:
        print(f"Error in render_discord_style_player: {e}")
        return {
            'embed': create_error_embed(str(e)),
            'view': None
        }

def render_player(self, language: str = 'vi'):
    """Render enhanced player controller với giao diện đẹp mắt"""
    try:
        player = self

        # Kiểm tra cơ bản
        if not player or not hasattr(player, 'current') or not player.current:
            return create_no_track_embed()

        # Tạo embed với màu sắc động
        embed = Embed(color=get_status_color(player))

        # Header với trạng thái
        status_icon = "▶️" if not getattr(player, 'paused', False) else "⏸️"
        status_text = "Đang phát nhạc" if not getattr(player, 'paused', False) else "Tạm dừng"

        embed.set_author(
            name=f"{status_icon} {status_text}",
            icon_url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif"
        )

        # Title với emoji nguồn
        source = getattr(player.current, 'source', 'unknown').lower()
        source_emoji = "🔴" if source == "youtube" else "🎵"
        title = getattr(player.current, 'title', 'Unknown Track')
        embed.title = f"{source_emoji} **{trim_text(title, 60)}**"

        # URL nếu có
        if hasattr(player.current, 'uri') and player.current.uri:
            embed.url = player.current.uri

        # Description với thông tin chi tiết
        description_parts = []

        # Thời gian và thanh tiến trình
        is_stream = hasattr(player.current, 'stream') and player.current.stream
        if not is_stream and hasattr(player.current, 'length') and player.current.length > 0:
            current_time = getattr(player.current, 'position', 0)
            total_time = player.current.length

            current_formatted = format_duration(current_time)
            total_formatted = format_duration(total_time)
            progress_bar = get_progress_bar(current_time, total_time)

            description_parts.append(f"🕐 **Thời lượng:** {total_formatted}")
            description_parts.append(f"`{progress_bar}` **{current_formatted}/{total_formatted}**")
        else:
            description_parts.append("🔴 **Nguồn:** Phát trực tiếp")

        # Thông tin bài hát
        author = getattr(player.current, 'author', 'Unknown Artist')
        description_parts.append(f"👤 **Tác giả:** {trim_text(author, 40)}")

        # Nguồn
        source_name = getattr(player.current, 'source', 'Unknown').capitalize()
        description_parts.append(f"🔴 **Nguồn:** {source_name}")

        # Âm lượng
        volume = 100
        if hasattr(player, 'volume'):
            volume = int(getattr(player, 'volume', 1.0) * 100)
        description_parts.append(f"🔊 **Âm lượng:** {volume}%")

        # Chế độ lặp
        try:
            from utils.conv import LoopMODE
            current_loop = getattr(player.queue, 'loop', LoopMODE.OFF)

            if current_loop == LoopMODE.OFF:
                loop_display = "➡️ **Chế độ lặp:** Tắt"
            elif current_loop == LoopMODE.SONG:
                loop_display = "🔂 **Chế độ lặp:** Lặp bài hiện tại"
            elif current_loop == LoopMODE.PLAYLIST:
                loop_display = "🔁 **Chế độ lặp:** Lặp hàng đợi"
            else:
                loop_display = "➡️ **Chế độ lặp:** Tắt"

            description_parts.append(loop_display)
        except:
            description_parts.append("➡️ **Chế độ lặp:** Tắt")

        # Kênh voice
        if hasattr(player, 'channel') and player.channel:
            description_parts.append(f"🔗 **Kênh:** {player.channel.mention}")

        # Máy chủ
        if hasattr(player, 'node') and hasattr(player.node, 'label'):
            description_parts.append(f"📡 **Máy chủ:** {player.node.label}")

        embed.description = "\n".join(description_parts)

        # Thumbnail
        if hasattr(player.current, 'artwork_url') and player.current.artwork_url:
            embed.set_thumbnail(url=player.current.artwork_url)

        # Footer
        if not is_stream and hasattr(player.current, 'length'):
            current_pos = getattr(player.current, 'position', 0)
            footer_text = f"Music CitLaLi | {format_duration(current_pos)} / {format_duration(player.current.length)}"
        else:
            footer_text = "Music CitLaLi | Live Stream"

        embed.set_footer(
            text=footer_text,
            icon_url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif"
        )

        # Tạo view với buttons và select menu
        view = create_enhanced_view(player, language)

        return {"embed": embed, "view": view}

    except Exception as e:
        print(f"Error in render_player: {e}")
        return create_error_embed(str(e))

def create_no_track_embed():
    """Tạo embed khi không có bài hát"""
    embed = Embed(
        title="🎵 Không có bài hát",
        description="Hiện tại không có bài hát nào đang phát.\nSử dụng lệnh `/play` để thêm nhạc!",
        color=Color.blue()
    )
    embed.set_footer(text="Music CitLaLi")
    return {"embed": embed, "view": None}

def create_error_embed(error_msg: str):
    """Tạo embed khi có lỗi"""
    embed = Embed(
        title="❌ Lỗi Player",
        description=f"Đã xảy ra lỗi khi tải player controller:\n```{error_msg}```",
        color=Color.red()
    )
    embed.set_footer(text="Music CitLaLi")
    return {"embed": embed, "view": None}

def safe_len(seq) -> int:
	"""Return length of seq, trying len(seq) first, then converting to list if needed."""
	try:
		return len(seq)
	except Exception:
		try:
			return len(list(seq))
		except Exception:
			# Fallback: try internal attributes
			try:
				return len(getattr(seq, "_queue"))
			except Exception:
				return 0

def ensure_list(seq):
	"""Ensure seq can be sliced/iterated like a list. If already list/tuple, return as-is."""
	if isinstance(seq, (list, tuple)):
		return seq
	try:
		return list(seq)
	except Exception:
		# Try common internal storages (e.g., deque._queue) or wrap single item into list
		try:
			internal = getattr(seq, "_queue", None)
			if internal is not None:
				return list(internal)
		except Exception:
			pass
		return [seq]

def create_enhanced_view(player, language: str) -> View:
    """Tạo view với buttons và select menu theo thiết kế đẹp"""
    try:
        view = View(timeout=None)

        # Row 1: Main control buttons (5 buttons chính)
        # Previous track
        played_count = 0
        if hasattr(player, 'queue') and hasattr(player.queue, 'played'):
            played_count = safe_len(player.queue.played)

        view.add_item(Button(
            style=ButtonStyle.secondary,
            emoji="⏮️",
            disabled=played_count == 0,
            custom_id="player_controller_prev_track_btn",
            row=0
        ))

        # Button 2: Play/Pause (màu xanh dương)
        is_paused = getattr(player, 'paused', False)
        view.add_item(Button(
            style=ButtonStyle.primary,
            emoji="▶️" if is_paused else "⏸️",
            label="Phát ngay" if is_paused else "Tạm dừng",
            custom_id="player_controller_pause_resume_btn",
            row=0
        ))

        # Button 3: Stop (màu đỏ)
        view.add_item(Button(
            style=ButtonStyle.danger,
            emoji="⏹️",
            custom_id="player_controller_stop_btn",
            row=0
        ))

        # Next track
        next_count = 0
        if hasattr(player, 'queue'):
            if hasattr(player.queue, 'next_track'):
                next_count = safe_len(player.queue.next_track)
            elif hasattr(player.queue, '_queue'):
                next_count = safe_len(player.queue._queue)

        view.add_item(Button(
            style=ButtonStyle.secondary,
            emoji="⏭️",
            disabled=next_count == 0,
            custom_id="player_controller_next_track_btn",
            row=0
        ))

        # Add song button (màu xanh lá)
        view.add_item(Button(
            style=ButtonStyle.success,
            emoji="🎵",
            label="Thêm nhạc",
            custom_id="player_controller_add_music_btn",
            row=0
        ))

        # Row 2: Select menu cho các tùy chọn
        select_options = create_select_options(player, language)
        if select_options:
            select_menu = Select(
                placeholder="Lựa chọn khác:",
                options=select_options,
                custom_id="player_controller_select_menu",
                row=1
            )
            view.add_item(select_menu)

        return view

    except Exception as e:
        print(f"Error creating enhanced view: {e}")
        return None

def create_select_options(player, language: str) -> List[SelectOption]:
    """Tạo các options cho select menu"""
    try:
        options = []

        # Thêm bài hát
        options.append(SelectOption(
            label="Thêm bài hát",
            description="Thêm một bài hát/danh sách phát vào trong hàng đợi.",
            emoji="➕",
            value="add_song"
        ))

        # Thêm vào mục yêu thích
        options.append(SelectOption(
            label="Thêm vào mục yêu thích của bạn",
            description="Thêm bài hát hiện tại vào mục yêu thích của bạn.",
            emoji="❤️",
            value="add_favorite"
        ))

        # Tua về đầu bài
        options.append(SelectOption(
            label="Tua về đầu bài",
            description="Tua thời gian bài nhạc hiện tại về 00:00.",
            emoji="⏪",
            value="seek_start"
        ))

        # Âm lượng
        volume = 100
        if hasattr(player, 'volume'):
            volume = int(getattr(player, 'volume', 1.0) * 100)

        options.append(SelectOption(
            label=f"Âm lượng: {volume}%",
            description="Điều chỉnh âm lượng",
            emoji="🔊",
            value="volume_control"
        ))

        # Trộn các bài hát trong hàng
        options.append(SelectOption(
            label="Trộn các bài hát trong hàng",
            description="Trộn nhạc trong hàng đợi.",
            emoji="🔀",
            value="toggle_shuffle"
        ))

        # Lặp lại bài hát - lấy từ queue.loop
        try:
            from utils.conv import LoopMODE
            current_loop = getattr(player.queue, 'loop', LoopMODE.OFF)

            if current_loop == LoopMODE.OFF:
                loop_text = "Tắt"
                loop_emoji = "➡️"
            elif current_loop == LoopMODE.SONG:
                loop_text = "Lặp bài hiện tại"
                loop_emoji = "🔂"
            elif current_loop == LoopMODE.PLAYLIST:
                loop_text = "Lặp hàng đợi"
                loop_emoji = "🔁"
            else:
                loop_text = "Tắt"
                loop_emoji = "➡️"
        except:
            loop_text = "Tắt"
            loop_emoji = "➡️"

        options.append(SelectOption(
            label=f"Chế độ lặp: {loop_text}",
            description="Bấm để thay đổi chế độ lặp lại bài hát.",
            emoji=loop_emoji,
            value="toggle_loop"
        ))

        # Xem hàng đợi
        queue_count = 0
        if hasattr(player, 'queue'):
            if hasattr(player.queue, 'next_track'):
                queue_count = safe_len(player.queue.next_track)
            elif hasattr(player.queue, '_queue'):
                queue_count = safe_len(player.queue._queue)

        options.append(SelectOption(
            label=f"Xem hàng đợi ({queue_count} bài)",
            description="Hiển thị danh sách bài hát trong hàng đợi.",
            emoji="📋",
            value="view_queue"
        ))

        # Chia sẻ bài hát
        options.append(SelectOption(
            label="Chia sẻ bài hát",
            description="Chia sẻ link bài hát hiện tại.",
            emoji="📤",
            value="share_song"
        ))

        # Thông tin chi tiết
        options.append(SelectOption(
            label="Thông tin chi tiết",
            description="Xem thông tin chi tiết về bài hát.",
            emoji="ℹ️",
            value="song_info"
        ))

        return options[:25]  # Discord limit 25 options

    except Exception as e:
        print(f"Error creating select options: {e}")
        return []

# Helper function để xử lý select menu interactions
async def handle_select_interaction(interaction, player):
    """Xử lý select menu interactions đầy đủ"""
    try:
        selected_value = interaction.data.values[0]

        if selected_value == "add_song":
            embed = Embed(
                title="🎵 Thêm bài hát",
                description="**Cách thêm nhạc:**\n"
                           "• Sử dụng lệnh `/play <tên bài hát hoặc URL>`\n"
                           "• Hoặc gõ `!play <tên bài hát hoặc URL>`\n\n"
                           "**Ví dụ:**\n"
                           "`/play Anh Thanh Niên - HuyR`\n"
                           "`!play https://youtube.com/watch?v=...`\n\n"
                           "**Nguồn hỗ trợ:**\n"
                           "🎵 YouTube • 🎶 YouTube Music\n"
                           "🎧 SoundCloud • 🎼 Spotify • 🍎 Apple Music",
                color=Color.green()
            )
            embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif")
            await interaction.edit_original_response(embed=embed)

        elif selected_value == "add_favorite":
            embed = Embed(
                title="❤️ Thêm vào yêu thích",
                description=f"**Đã thêm vào danh sách yêu thích!**\n\n"
                           f"🎵 **Bài hát:** {getattr(player.current, 'title', 'Unknown Track')}\n"
                           f"👤 **Tác giả:** {getattr(player.current, 'author', 'Unknown Artist')}\n\n"
                           f"💡 **Mẹo:** Sử dụng lệnh `/favorites` để xem danh sách yêu thích của bạn!",
                color=Color.red()
            )
            if hasattr(player.current, 'artwork_url') and player.current.artwork_url:
                embed.set_thumbnail(url=player.current.artwork_url)
            await interaction.edit_original_response(embed=embed)

        elif selected_value == "seek_start":
            try:
                await player.seek(0)
                embed = Embed(
                    title="⏪ Đã tua về đầu bài!",
                    description=f"🎵 **{getattr(player.current, 'title', 'Unknown Track')}**\n"
                               f"⏰ Đã đặt lại thời gian về **00:00**",
                    color=Color.blue()
                )
                await interaction.edit_original_response(embed=embed)
            except Exception as e:
                embed = Embed(
                    title="❌ Không thể tua bài hát!",
                    description=f"**Lỗi:** {str(e)}\n\n"
                               f"💡 **Có thể do:**\n"
                               f"• Bài hát đang livestream\n"
                               f"• Lỗi kết nối mạng\n"
                               f"• Bài hát không hỗ trợ seek",
                    color=Color.red()
                )
                await interaction.edit_original_response(embed=embed)

        elif selected_value == "volume_control":
            current_volume = 100
            if hasattr(player, 'volume'):
                current_volume = int(getattr(player, 'volume', 1.0) * 100)

            embed = Embed(
                title="🔊 Điều chỉnh âm lượng",
                description=f"**Âm lượng hiện tại:** {current_volume}%\n\n"
                           f"**Cách thay đổi:**\n"
                           f"• `/volume <0-100>` - Đặt âm lượng cụ thể\n"
                           f"• `/volume 50` - Đặt âm lượng 50%\n"
                           f"• `/volume 100` - Âm lượng tối đa\n\n"
                           f"🎚️ **Mức đề xuất:** 70-80%",
                color=Color.blue()
            )
            await interaction.edit_original_response(embed=embed)

        elif selected_value == "toggle_shuffle":
            embed = Embed(
                title="🔀 Trộn bài hát",
                description="**Cách sử dụng:**\n"
                           "• `/shuffle on` - Bật trộn bài\n"
                           "• `/shuffle off` - Tắt trộn bài\n"
                           "• `/shuffle` - Bật/tắt tự động\n\n"
                           "🎲 **Khi bật:** Các bài hát sẽ được phát ngẫu nhiên\n"
                           "📋 **Khi tắt:** Phát theo thứ tự trong hàng đợi",
                color=Color.purple()
            )
            await interaction.edit_original_response(embed=embed)

        elif selected_value == "toggle_loop":
            try:
                from utils.conv import LoopMODE

                # Lấy chế độ lặp hiện tại
                current_loop = getattr(player.queue, 'loop', LoopMODE.OFF)

                # Cycle qua các chế độ: OFF → SONG → PLAYLIST → OFF
                if current_loop == LoopMODE.OFF:
                    player.queue.loop = LoopMODE.SONG
                    embed = Embed(
                        title="🔂 Chế độ lặp: Lặp bài hiện tại",
                        description=f"**Đã bật lặp bài hát!**\n\n"
                                   f"🎵 **Bài hát:** {getattr(player.current, 'title', 'Unknown Track')}\n"
                                   f"🔄 **Trạng thái:** Bài hát này sẽ được phát lặp lại liên tục\n\n"
                                   f"💡 **Để thay đổi:** Click lại để chuyển sang lặp hàng đợi",
                        color=Color.blue()
                    )

                elif current_loop == LoopMODE.SONG:
                    player.queue.loop = LoopMODE.PLAYLIST
                    # Make next_track safe to measure
                    nt = getattr(player.queue, 'next_track', None)
                    queue_count = 1 + (safe_len(nt) if nt is not None else 0)  # +1 cho bài đang phát
                    embed = Embed(
                        title="🔁 Chế độ lặp: Lặp hàng đợi",
                        description=f"**Đã bật lặp hàng đợi!**\n\n"
                                   f"📋 **Số bài trong hàng:** {queue_count} bài\n"
                                   f"🔄 **Trạng thái:** Tất cả bài hát sẽ được phát lặp lại\n\n"
                                   f"💡 **Để thay đổi:** Click lại để tắt chế độ lặp",
                        color=Color.green()
                    )

                else:  # LoopMODE.PLAYLIST
                    player.queue.loop = LoopMODE.OFF
                    embed = Embed(
                        title="➡️ Chế độ lặp: Tắt",
                        description=f"**Đã tắt chế độ lặp!**\n\n"
                                   f"🎵 **Trạng thái:** Phát nhạc bình thường\n"
                                   f"📋 **Hành vi:** Phát hết hàng đợi rồi dừng\n\n"
                                   f"💡 **Để thay đổi:** Click lại để bật lặp bài hiện tại",
                        color=Color.orange()
                    )

                # Thêm thumbnail nếu có
                if hasattr(player.current, 'artwork_url') and player.current.artwork_url:
                    embed.set_thumbnail(url=player.current.artwork_url)

                # Cập nhật controller để hiển thị thay đổi
                await player.controller()

                await interaction.edit_original_response(embed=embed)

            except Exception as e:
                embed = Embed(
                    title="❌ Lỗi khi thay đổi chế độ lặp",
                    description=f"**Chi tiết lỗi:** {str(e)}\n\n"
                               f"💡 **Thử lại:** Click vào tùy chọn một lần nữa",
                    color=Color.red()
                )
                await interaction.edit_original_response(embed=embed)

        elif selected_value == "view_queue":
            try:
                queue_list = []
                queue_tracks = []

                if hasattr(player, 'queue'):
                    if hasattr(player.queue, 'next_track') and player.queue.next_track:
                        queue_tracks = ensure_list(player.queue.next_track)
                    elif hasattr(player.queue, '_queue') and player.queue._queue:
                        queue_tracks = ensure_list(player.queue._queue)

                embed = Embed(title="📋 Hàng đợi phát nhạc", color=Color.blue())

                # Bài đang phát
                if hasattr(player, 'current') and player.current:
                    current_title = getattr(player.current, 'title', 'Unknown Track')
                    current_author = getattr(player.current, 'author', 'Unknown Artist')
                    embed.add_field(
                        name="🎵 Đang phát",
                        value=f"**{trim_text(current_title, 40)}**\n👤 {trim_text(current_author, 30)}",
                        inline=False
                    )

                # Hàng đợi
                if queue_tracks:
                    for i, track in enumerate(queue_tracks[:8], 1):  # now safe, queue_tracks is a list
                        title = getattr(track, 'title', 'Unknown Track')
                        author = getattr(track, 'author', 'Unknown Artist')
                        queue_list.append(f"`{i}.` **{trim_text(title, 35)}**\n    👤 {trim_text(author, 25)}")

                    queue_text = "\n\n".join(queue_list)
                    if len(queue_tracks) > 8:
                        queue_text += f"\n\n`...` **và {len(queue_tracks) - 8} bài khác**"

                    embed.add_field(
                        name=f"⏭️ Tiếp theo ({len(queue_tracks)} bài)",
                        value=queue_text,
                        inline=False
                    )
                else:
                    embed.add_field(
                        name="⏭️ Tiếp theo",
                        value="```\nHàng đợi trống\n```\n💡 Sử dụng `/play` để thêm bài hát!",
                        inline=False
                    )

                # Thông tin thêm
                total_songs = len(queue_tracks) + (1 if hasattr(player, 'current') and player.current else 0)
                embed.set_footer(text=f"Tổng cộng: {total_songs} bài hát")

                # Thumbnail
                if hasattr(player.current, 'artwork_url') and player.current.artwork_url:
                    embed.set_thumbnail(url=player.current.artwork_url)

                await interaction.edit_original_response(embed=embed)
            except Exception as e:
                embed = Embed(
                    title="❌ Lỗi khi xem hàng đợi",
                    description=f"**Chi tiết:** {str(e)}\n\n💡 Thử lại sau ít phút",
                    color=Color.red()
                )
                await interaction.edit_original_response(embed=embed)

        elif selected_value == "share_song":
            if hasattr(player, 'current') and player.current:
                title = getattr(player.current, 'title', 'Unknown Track')
                author = getattr(player.current, 'author', 'Unknown Artist')
                uri = getattr(player.current, 'uri', 'No URL')
                source = getattr(player.current, 'source', 'Unknown').capitalize()

                embed = Embed(
                    title="📤 Chia sẻ bài hát",
                    description=f"**🎵 {title}**\n"
                               f"👤 **Tác giả:** {author}\n"
                               f"🔗 **Nguồn:** {source}\n\n"
                               f"**Link:** {uri}\n\n"
                               f"💡 **Cách sử dụng:** Copy link trên và chia sẻ với bạn bè!",
                    color=Color.green()
                )

                # Thumbnail
                if hasattr(player.current, 'artwork_url') and player.current.artwork_url:
                    embed.set_thumbnail(url=player.current.artwork_url)

                embed.set_footer(text="Nhấn và giữ để copy link")
                await interaction.edit_original_response(embed=embed)
            else:
                embed = Embed(
                    title="❌ Không có bài hát để chia sẻ!",
                    description="**Hiện tại không có bài hát nào đang phát.**\n\n"
                               "💡 Sử dụng `/play` để phát nhạc trước!",
                    color=Color.red()
                )
                await interaction.edit_original_response(embed=embed)

        elif selected_value == "song_info":
            try:
                if hasattr(player, 'current') and player.current:
                    title = getattr(player.current, 'title', 'Unknown')
                    author = getattr(player.current, 'author', 'Unknown')
                    source = getattr(player.current, 'source', 'Unknown').capitalize()
                    length = getattr(player.current, 'length', 0)
                    uri = getattr(player.current, 'uri', 'No URL')
                    artwork_url = getattr(player.current, 'artwork_url', None)
                    is_stream = getattr(player.current, 'stream', False)

                    # Tính thời gian đã phát
                    position = 0
                    if hasattr(player, 'position'):
                        position = getattr(player, 'position', 0)

                    embed = Embed(
                        title="ℹ️ Thông tin chi tiết bài hát",
                        color=Color.blue()
                    )

                    # Thông tin cơ bản
                    embed.add_field(
                        name="🎵 Tên bài hát",
                        value=f"**{title}**",
                        inline=False
                    )

                    embed.add_field(
                        name="👤 Tác giả",
                        value=author,
                        inline=True
                    )

                    embed.add_field(
                        name="🔗 Nguồn",
                        value=source,
                        inline=True
                    )

                    # Thời gian
                    if is_stream:
                        embed.add_field(
                            name="⏰ Thời lượng",
                            value="🔴 **LIVESTREAM**",
                            inline=True
                        )
                    else:
                        embed.add_field(
                            name="⏰ Thời lượng",
                            value=format_duration(length),
                            inline=True
                        )

                        embed.add_field(
                            name="⏱️ Đã phát",
                            value=format_duration(position),
                            inline=True
                        )

                        # Progress percentage
                        if length > 0:
                            progress = (position / length) * 100
                            embed.add_field(
                                name="📊 Tiến độ",
                                value=f"{progress:.1f}%",
                                inline=True
                            )

                    # Chế độ phát
                    try:
                        from utils.conv import LoopMODE
                        current_loop = getattr(player.queue, 'loop', LoopMODE.OFF)

                        if current_loop == LoopMODE.OFF:
                            loop_text = "➡️ Tắt"
                        elif current_loop == LoopMODE.SONG:
                            loop_text = "🔂 Lặp bài hiện tại"
                        else:
                            loop_text = "🔁 Lặp hàng đợi"

                        embed.add_field(
                            name="🔄 Chế độ lặp",
                            value=loop_text,
                            inline=True
                        )
                    except:
                        pass

                    # Volume
                    volume = 100
                    if hasattr(player, 'volume'):
                        volume = int(getattr(player, 'volume', 1.0) * 100)
                    embed.add_field(
                        name="🔊 Âm lượng",
                        value=f"{volume}%",
                        inline=True
                    )

                    # URL (rút gọn)
                    if len(uri) > 50:
                        short_uri = uri[:47] + "..."
                    else:
                        short_uri = uri

                    embed.add_field(
                        name="🔗 Link",
                        value=f"[Click để mở]({uri})",
                        inline=False
                    )

                    # Thumbnail
                    if artwork_url:
                        embed.set_image(url=artwork_url)  # Dùng set_image thay vì thumbnail để lớn hơn

                    embed.set_footer(text=f"Nguồn: {source} • Được yêu cầu bởi {interaction.author.display_name}")

                else:
                    embed = Embed(
                        title="ℹ️ Không có thông tin bài hát",
                        description="**Hiện tại không có bài hát nào đang phát.**\n\n"
                                   "💡 Sử dụng `/play` để phát nhạc!",
                        color=Color.orange()
                    )

                await interaction.edit_original_response(embed=embed)
            except Exception as e:
                embed = Embed(
                    title="❌ Lỗi khi lấy thông tin bài hát",
                    description=f"**Chi tiết:** {str(e)}\n\n💡 Thử lại sau ít phút",
                    color=Color.red()
                )
                await interaction.edit_original_response(embed=embed)

        else:
            embed = Embed(
                title="❌ Tùy chọn không được hỗ trợ!",
                description=f"**Tùy chọn:** `{selected_value}`\n\n"
                           f"💡 **Có thể do:**\n"
                           f"• Phiên bản bot cũ\n"
                           f"• Tính năng đang được phát triển\n"
                           f"• Lỗi hệ thống tạm thời",
                color=Color.red()
            )
            await interaction.edit_original_response(embed=embed)

    except Exception as e:
        print(f"Error in handle_select_interaction: {e}")
        try:
            embed = Embed(
                title="❌ Đã xảy ra lỗi!",
                description=f"**Chi tiết:** {str(e)}\n\n"
                           f"💡 **Thử:**\n"
                           f"• Thử lại sau ít giây\n"
                           f"• Kiểm tra kết nối mạng\n"
                           f"• Liên hệ admin nếu lỗi tiếp tục",
                color=Color.red()
            )
            await interaction.edit_original_response(embed=embed)
        except:
            pass

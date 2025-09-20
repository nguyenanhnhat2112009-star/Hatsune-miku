from __future__ import annotations

import random
from asyncio import Lock, sleep
from traceback import print_exc

from aiohttp import ClientSession
from mafic.errors import TrackLoadException, HTTPUnauthorized, HTTPException, HTTPNotFound, HTTPBadRequest
from mafic import Track, Player, PlayerNotConnected
from disnake.abc import Connectable
from utils.ClientUser import ClientUser
from collections import deque
from typing import Optional, Any
from disnake import Message, MessageInteraction, ui, SelectOption, ButtonStyle, Embed, MessageFlags, utils, TextChannel, Thread, VoiceChannel, StageChannel, PartialMessageable
from utils.conv import time_format, trim_text, LoopMODE
from logging import getLogger
from datetime import datetime
from typing import Union
from utils.controller.player_controler import render_player

MessageableChannel = Union[TextChannel, Thread, VoiceChannel, StageChannel, PartialMessageable]


logger = getLogger(__name__)



class STATE(enumerate):
    OFF = 0
    ON = 1
    

class Queue:
    def __init__(self):
        self.is_playing: Optional[Track] = None
        self.next_track: deque = deque()
        self.played: deque = deque(maxlen=45)
        self.loop = LoopMODE.OFF
        self.autoplay: deque = deque(maxlen=25)
        self.keep_connect = STATE.OFF
        self.shuffle = STATE.OFF

    def get_next_track(self):
        return [track for track in self.next_track]

    def process_next(self):
        if self.loop == LoopMODE.SONG:
            return self.is_playing
        return self.next()

    def next(self):
        if self.is_playing is not None:
            self.played.append(self.is_playing)
            self.is_playing = None

        if self.loop == LoopMODE.PLAYLIST or self.keep_connect == STATE.ON and self.next_track.__len__() == 0:
            for track in self.played:
                self.next_track.append(track)
            self.played.clear()

        if self.next_track:
            if self.shuffle == STATE.ON:
                index = random.randrange(0, len(self.next_track))
                self.is_playing = self.next_track[index]
                del self.next_track[index]
            else:
                self.is_playing = self.next_track.popleft()
            return self.is_playing

        if not self.next_track and self.autoplay:
            self.is_playing = self.autoplay.popleft()

        return self.is_playing

    def previous(self) -> Optional[Track]:
        if self.played.__len__() == 0:
            return None

        if self.is_playing is not None:
            self.next_track.appendleft(self.is_playing)

        self.is_playing = self.played.pop()
        return self.is_playing

    def add_next_track(self, track: Track):
        if self.loop == LoopMODE.PLAYLIST and self.next_track.__len__() == 0:
            self.next_track.appendleft(track)
            return
        self.next_track.append(track)

    def clear_queue(self):
        self.next_track.clear()

class MusicPlayer(Player[ClientUser]):
    def __init__(self, client: ClientUser, channel: Connectable):
        super().__init__(client, channel)
        self.locked = False
        self.client: ClientUser = client
        self.start_time = None
        self.queue: Queue = Queue()
        self.player_channel = channel
        self.NotiChannel: Optional[MessageableChannel] = None
        self.message: Optional[Message] = None
        self.nightCore = STATE.OFF
        self.keep_connection = STATE.OFF
        self.is_autoplay_mode = False
        self.player_controller: Optional[Message] = None
        self.locker = Lock()
        self.update_controller_task: asyncio.Task = None # type: ignore

    @property
    def player_volume(self) -> int:
        return self._volume

    @property
    def player_endpoint(self) -> str | None:
        return self._server_state["endpoint"]

    @property
    def node_session_id(self) -> str | None:
        return self.node._session_id # noqa

    @property
    def rest_uri(self):
        return self.node._rest_uri # noqa

    @property
    def node_password(self):
        return self.node._Node__password # noqa

    async def request(self,
                      method: str,
                      path: str) -> Any:
        uri  = self.rest_uri / path
        async with ClientSession() as session:
            resp = await session.request(method, uri, headers={"Authorization": self.node_password}) # noqa
            match resp.status:
                case 200:
                    return await resp.json()
                case 204:
                    return None
                case 400:
                    raise HTTPBadRequest(await resp.text())
                case 401:
                    raise HTTPUnauthorized(await resp.text())
                case 404:
                    raise HTTPNotFound(await resp.text())
                case _:
                    raise HTTPException(resp.status, message=await resp.text())

    async def get_lyric(self, guildID) -> dict | None:
        try:
            req = await self.request("GET", f"sessions/{self.node_session_id}/players/{guildID}/lyrics")
            if req is not None:
                return req
            return None
        except HTTPNotFound or HTTPUnauthorized or HTTPBadRequest or HTTPException:
            return None

    async def pause_player(self) -> None:
        await self.pause(pause=not self.paused)
        if not self.paused:
            self.start_time = datetime.now()

    async def sendMessage(self, **kwargs):
        try:
            await self.NotiChannel.send(**kwargs)
        except Exception:
            self.channel = None

    async def playnext(self):
        track = self.queue.process_next()
        lang = await self.client.database.cached_databases.get_language(self.guild.id)
        if track is None:
            if self.channel is not None:
                txt = self.client.language.get(lang, 'music', 'queue_end')
                await self.sendMessage(embed=Embed(description=txt, color=0xffddff), flags=MessageFlags(suppress_notifications=True))
                await self.disconnect(force=True)
                return
        self.start_time = datetime.now()
        await self.play(track, replace=True)
        await self.controller()

    async def playprevious(self):
        track = self.queue.previous()
        if track is None:
            return False
        self.start_time = datetime.now()
        await self.play(track, replace=True)
        await self.controller()
    
    async def stopPlayer(self, isButton: bool = False):
        try:
            await self.stop()
        except PlayerNotConnected:
             pass
        finally:
            self.queue.played.clear()
            self.queue.autoplay.clear()
            self.queue.next_track.clear()
            self.queue.is_playing = None
            await self.disconnect(force=True)
            if not isButton:
                await self.destroy_player_controller()
            else:
                await self.endPlayer()
            self.client.dispatch("player_disconnected")
            self.client.logger.info(f"Trình phát được ngắt kết nối khỏi máy chủ: {self.guild.id}")

    async def process_next(self):
        if self.keep_connection == STATE.ON and self.is_autoplay_mode:
            track = await self.get_auto_tracks()
        elif self.keep_connection == STATE.ON and not self.is_autoplay_mode:
            track = self.queue.process_next()
        else:
            track = self.queue.process_next()
        if self.is_autoplay_mode and track is None:
            track = await self.get_auto_tracks()
        if track is None:
            if self.channel is not None:
                lang = await self.client.database.cached_databases.get_language(self.guild.id)
                txt = self.client.language.get(lang, 'music', 'queue_end')
                await self.sendMessage(embed=Embed(description=txt, color=0xffddff), flags=MessageFlags(suppress_notifications=True))
            await self.stopPlayer()
            return
        if track.stream:
            self.start_time = None
        self.start_time = datetime.now()
        await self.play(track, replace=True)
        await self.controller()

    async def controller(self, force_resync: bool = False):
        async with self.locker:
            replace = True
            lang = await self.client.database.cached_databases.get_language(self.guild.id)
            if self.player_controller is None:
                replace = False
            elif self.player_controller.created_at.timestamp() + 180 < utils.utcnow().timestamp():
                replace = False
            elif self.NotiChannel is None:
                ...
            elif self.player_controller.channel.id != self.NotiChannel.id:
                replace = False
            try:
                if replace:
                    controller_data = render_player(self, lang)
                    if controller_data:
                        self.player_controller = await self.player_controller.edit(**controller_data)
                elif force_resync:
                    if self.player_controller is not None:
                        await self.player_controller.delete()
                    if self.NotiChannel is not None:
                        controller_data = render_player(self, lang)
                        if controller_data:
                            self.player_controller = await self.NotiChannel.send(flags=MessageFlags(suppress_notifications=True), **controller_data)
                else:
                    if self.player_controller is not None:
                        await self.player_controller.delete()
                    if self.NotiChannel is not None:
                        controller_data = render_player(self, lang)
                        if controller_data:
                            self.player_controller = await self.NotiChannel.send(flags=MessageFlags(suppress_notifications=True), **controller_data)
            except Exception as e:
                if "Unknown Message" in str(e):
                    await self.controller(True)
                logger.error(f"Tải trình điều khuyển thất bại: {e}")
                # self.player_controller = None
                # self.NotiChannel = None
    
    async def update_controller(self):
        while True:
            await sleep(20)
            await self.controller(force_resync=True)
            
    async def get_auto_tracks(self):
        try:
            return self.queue.autoplay.popleft()
        except:
            pass

        search: list[Track] = []

        if self.locked:
            return

        for q in self.queue.played + self.queue.autoplay:

            if len(search) > 4: break

            if q.length < 90000: continue

            search.append(q)

        t = None
        ts = []
        t_youtube = []

        exep = None

        if search:

            search.reverse()

            self.locked = True

            for track_data in search:

                if not ts:
                    if track_data.source.lower() == "youtube":
                        query = f"https://www.youtube.com/watch?v={track_data.identifier}&list=RD{track_data.identifier}"
                    else:
                        query = f"{track_data.author}"

                    try:
                        ts = await self.fetch_tracks(query)
                    except Exception as e:
                        if [err for err in ("Could not find tracks from mix", "Could not read mix page") if err in str(e)]:
                            try:
                                t_youtube = await self.fetch_tracks(
                                    f"\"{track_data.author}\""
                                )
                                t = track_data
                            except Exception as e:
                                exep = e
                                continue
                        else:
                            exep = e
                            print_exc()
                            await sleep(1.5)
                            continue
                t = track_data
                break

            if not ts:
                ts = t_youtube
                ts.reverse()

            if not ts:
                self.locked = False
                if exep:
                    if isinstance(exep, TrackLoadException):
                        errmsg =    f"Lỗi ```java\n{exep.cause}```\n" \
                                    f"Mã lỗi: `\n{exep.message}`\n" \
                                    f"Máy chủ âm nhạc `{self.node.label}`"
                    else:
                        errmsg = f"Chi tiết: ```py\n{repr(exep)}```"
                else:
                    errmsg = "Không có kết quả"

                if self.NotiChannel is not None:
                    await self.sendMessage(embed = Embed(
                        description=f"**Không lấy được dữ liệu tự động phát:**\n"
                                    f"{errmsg}."), flags=MessageFlags(suppress_notifications=True), delete_after=10)
                    await sleep(8)
                await self.disconnect(force=True)
                return

            try:
                ts = ts.tracks
            except AttributeError:
                pass

            try:
                ts = [t for t in ts if not [u for u in search if t.uri.startswith(u.uri)]]
            except:
                pass

            if t:
                track_return: list[Track] = []

                for s in ts:

                    if s.stream:
                        continue

                    if s.length < 90000:
                        continue

                    if t.identifier and t.identifier == s.identifier:
                        continue

                    track_return.append(s)

                ts.clear()
                self.queue.autoplay.extend(track_return)

                try:
                    return self.queue.autoplay.popleft()
                except:
                    return None

    async def destroy_player_controller(self):
        async with self.locker:
            if self.player_controller is None:
                return
            try:
                self.player_controller = await self.player_controller.delete()
            except:
                self.player_controller = None
        self.update_controller_task.cancel()

    async def endPlayer(self):
        async with self.locker:
            if self.player_controller is None:
                return
            try:
                # Tạo embed đẹp cho thông báo stopped
                stopped_embed = Embed(
                    title="🛑 Đã dừng phát nhạc",
                    description="**Trình phát đã được dừng và ngắt kết nối**\n\n"
                               "🎵 Sử dụng lệnh `/play` để phát nhạc mới\n"
                               "📋 Sử dụng lệnh `/queue` để xem hàng đợi",
                    color=0xFF4444  # Màu đỏ nhẹ
                )
                stopped_embed.set_footer(
                    text="Music CitLaLi • Cảm ơn bạn đã sử dụng!",
                    icon_url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif"
                )
                stopped_embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1211567863538786334/1312988508645752892/ExuEyes.gif")

                await self.player_controller.edit(embed=stopped_embed, view=None)
            except:
                return await self.destroy_player_controller()
        self.update_controller_task.cancel()

class QueueInterface(ui.View):

    def __init__(self, player: MusicPlayer, timeout = 60):
        self.player = player
        self.pages = []
        self.selected = []
        self.current = 0
        self.max_pages = len(self.pages) - 1
        self.message: Optional[Message] = None
        super().__init__(timeout=timeout)
        self.embed = Embed()
        self.update_pages()
        self.update_embed()

    def update_pages(self):

        counter = 1

        self.pages = list(utils.as_chunks(self.player.queue.next_track, max_size=12))
        self.selected.clear()

        self.clear_items()

        for n, page in enumerate(self.pages):

            txt = "\n"
            opts = []

            for t in page:
                duration = time_format(t.length) if not t.stream else '🔴 Livestream'

                txt += f"`┌ {counter})` [`{trim_text(t.title, limit=50)}`]({t.uri})\n" \
                       f"`└ ⏲️ {duration}`\n"

                opts.append(
                    SelectOption(
                        label=f"{counter}. {t.author}"[:25], description=f"[{duration}] | {t.title}"[:50],
                        value=f"queue_select_{t.id}",
                    )
                )

                counter += 1

            self.pages[n] = txt
            self.selected.append(opts)

        first = ui.Button(emoji='⏮️', style=ButtonStyle.grey)
        first.callback = self.first
        self.add_item(first)

        back = ui.Button(emoji='⬅️', style=ButtonStyle.grey)
        back.callback = self.back
        self.add_item(back)

        next = ui.Button(emoji='➡️', style=ButtonStyle.grey)
        next.callback = self.next
        self.add_item(next)

        last = ui.Button(emoji='⏭️', style=ButtonStyle.grey)
        last.callback = self.last
        self.add_item(last)

        stop_interaction = ui.Button(emoji='⏹️', style=ButtonStyle.grey)
        stop_interaction.callback = self.stop_interaction
        self.add_item(stop_interaction)

        update_q = ui.Button(emoji='🔄', label="Refresh", style=ButtonStyle.grey)
        update_q.callback = self.update_q
        self.add_item(update_q)

        self.current = 0
        self.max_pages = len(self.pages) - 1

    async def on_timeout(self) -> None:

        if not self.message:
            return

        embed = self.message.embeds[0]
        embed.set_footer(text="Timed_out")

        for c in self.children:
            c.disabled = True

        await self.message.edit(embed=embed, view=self)

    def update_embed(self):
        self.embed.title = f"**Page [{self.current + 1} / {self.max_pages + 1}]**"
        self.embed.description = self.pages[self.current]
        self.children[0].options = self.selected[self.current]

        for n, c in enumerate(self.children):
            if isinstance(c, ui.StringSelect):
                self.children[n].options = self.selected[self.current]

    async def first(self, interaction: MessageInteraction):

        self.current = 0
        self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    async def back(self, interaction: MessageInteraction):

        if self.current == 0:
            self.current = self.max_pages
        else:
            self.current -= 1
        self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    async def next(self, interaction: MessageInteraction):

        if self.current == self.max_pages:
            self.current = 0
        else:
            self.current += 1
        self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    async def last(self, interaction: MessageInteraction):

        self.current = self.max_pages
        self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

    async def stop_interaction(self, interaction: MessageInteraction):

        await interaction.response.edit_message(content="Đóng", embed=None, view=None)
        self.stop()

    async def update_q(self, interaction: MessageInteraction):

        self.current = 0
        self.max_pages = len(self.pages) - 1
        self.update_pages()
        self.update_embed()
        await interaction.response.edit_message(embed=self.embed, view=self)

class VolumeInteraction(ui.View):

    def __init__(self, inter):
        self.inter = inter
        self.volume = None
        super().__init__(timeout=30)
        self.process_buttons()

    def process_buttons(self):

        opts = []

        for l in [5, 20, 40, 60, 80, 100, 120, 150]:

            if l > 100:
                description = "Warning: break"
            else:
                description = None
            opts.append(SelectOption(label=f"{l}%", value=f"vol_{l}", description=description))

        select = ui.Select(placeholder='Volume:', options=opts)
        select.callback = self.callback
        self.add_item(select)

    async def callback(self, interaction: MessageInteraction):
        await interaction.response.edit_message(content=f"OK!",embed=None, view=None)
        self.volume = int(interaction.data.values[0][4:])
        self.stop()

class SelectInteraction(ui.View):

    def __init__(self, options: list[SelectOption], *, timeout=180):
        super().__init__(timeout=timeout)
        self.select = None
        self.items = list(options)
        self.inter = None

        self.load()

    def load(self):

        self.clear_items()

        select_menu = ui.Select(placeholder="Chọn một tùy chọn dưới đây", options=self.items)
        select_menu.callback = self.callback
        self.add_item(select_menu)
        self.select = self.items[0].value

        button = ui.Button(label="Hủy bỏ", emoji="❌")
        button.callback = self.cancel_callback
        self.add_item(button)

    async def cancel_callback(self, interaction: MessageInteraction):
        self.select = False
        self.inter = interaction
        self.stop()

    async def callback(self, interaction: MessageInteraction):
        self.select = interaction.data.values[0]
        self.inter = interaction
        self.stop()
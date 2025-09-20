import disnake
from disnake.ext import commands
import psutil
import platform
import time
from datetime import datetime, timedelta
from typing import Optional
from utils.ClientUser import ClientUser


def format_bytes(bytes_value: int) -> str:
    """Format bytes into human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def get_ping_emoji(ping: int) -> str:
    """Get emoji based on ping value."""
    if ping < 100:
        return "🟢"  # Green - Excellent
    elif ping < 200:
        return "🟡"  # Yellow - Good
    elif ping < 300:
        return "🟠"  # Orange - Fair
    else:
        return "🔴"  # Red - Poor


def get_cpu_emoji(cpu_percent: float) -> str:
    """Get emoji based on CPU usage."""
    if cpu_percent < 30:
        return "🟢"
    elif cpu_percent < 60:
        return "🟡"
    elif cpu_percent < 80:
        return "🟠"
    else:
        return "🔴"


def get_memory_emoji(memory_percent: float) -> str:
    """Get emoji based on memory usage."""
    if memory_percent < 50:
        return "🟢"
    elif memory_percent < 70:
        return "🟡"
    elif memory_percent < 85:
        return "🟠"
    else:
        return "🔴"


class Ping(commands.Cog):
    def __init__(self, bot: ClientUser):
        self.bot = bot

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.slash_command(name="ping", description="Kiểm tra độ trễ và trạng thái bot")
    async def ping(self, interaction: disnake.ApplicationCommandInteraction):
        """Simple ping command with beautiful embed."""
        start_time = time.perf_counter()

        embed = disnake.Embed(
            title="🏓 Pong!",
            description="Đang kiểm tra độ trễ...",
            color=0x00ff88,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

        end_time = time.perf_counter()
        response_time = round((end_time - start_time) * 1000)
        bot_latency = round(self.bot.latency * 1000)

        ping_emoji = get_ping_emoji(bot_latency)
        response_emoji = get_ping_emoji(response_time)

        embed = disnake.Embed(
            title="🏓 Pong! - Thông tin độ trễ",
            description="Thông tin chi tiết về độ trễ của bot.",
            color=0x00ff88 if bot_latency < 200 else 0xffaa00 if bot_latency < 300 else 0xff0000,
            timestamp=datetime.now()
        )
        embed.add_field(
            name=f"{ping_emoji} Bot Latency",
            value=f"`{bot_latency}ms`",
            inline=True
        )
        embed.add_field(
            name=f"{response_emoji} Response Time",
            value=f"`{response_time}ms`",
            inline=True
        )
        embed.add_field(
            name="📊 Status",
            value="🟢 Online" if bot_latency < 300 else "🟡 Slow" if bot_latency < 500 else "🔴 Lagging",
            inline=True
        )
        embed.set_footer(
            text=f"Requested by {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.edit_original_response(embed=embed)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.slash_command(name="about", description="Thông tin chi tiết về bot và server")
    async def about(self, interaction: disnake.ApplicationCommandInteraction):
        """Detailed bot and server information."""
        await interaction.response.defer()

        process = psutil.Process()
        memory = psutil.virtual_memory()
        cpu_usage = psutil.cpu_percent(interval=1)

        bot_memory = process.memory_info().rss
        memory_percent = (bot_memory / memory.total) * 100

        uptime_seconds = int((datetime.now() - self.bot.uptime).total_seconds())
        uptime_str = str(timedelta(seconds=uptime_seconds))

        latency = round(self.bot.latency * 1000)

        embed = disnake.Embed(
            title="🤖 Thông tin Bot & Server",
            description="Thông tin chi tiết về bot và hiệu suất server.",
            color=0x7289da,
            timestamp=datetime.now()
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        bot_info = f"""
        **Tên:** {self.bot.user.name}
        **ID:** `{self.bot.user.id}`
        **Servers:** `{len(self.bot.guilds)}`
        **Users:** `{len(self.bot.users)}`
        **Uptime:** `{uptime_str}`
        """
        embed.add_field(name="📊 Bot Information", value=bot_info, inline=True)

        ping_emoji = get_ping_emoji(latency)
        cpu_emoji = get_cpu_emoji(cpu_usage)
        memory_emoji = get_memory_emoji(memory_percent)

        performance_info = f"""
        {ping_emoji} **Latency:** `{latency}ms`
        {cpu_emoji} **CPU:** `{cpu_usage:.1f}%`
        {memory_emoji} **RAM:** `{format_bytes(bot_memory)}`
        💾 **Total RAM:** `{format_bytes(memory.total)}`
        """
        embed.add_field(name="⚡ Performance", value=performance_info, inline=True)

        system_info = f"""
        **OS:** `{platform.system()} {platform.release()}`
        **Python:** `{platform.python_version()}`
        **Disnake:** `{disnake.__version__}`
        **CPU Cores:** `{psutil.cpu_count()}`
        """
        embed.add_field(name="💻 System Info", value=system_info, inline=True)

        try:
            if hasattr(self.bot, 'available_nodes') and self.bot.available_nodes:
                node = self.bot.available_nodes[0]
                music_info = f"""
                **Node:** `{node.label}`
                **Status:** 🟢 Connected
                **Players:** `{len(node.players)}`
                """
                embed.add_field(name="🎵 Music Node", value=music_info, inline=True)
        except:
            pass

        embed.set_footer(
            text=f"Requested by {interaction.author.display_name}",
            icon_url=interaction.author.display_avatar.url
        )

        await interaction.edit_original_response(embed=embed)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.slash_command(name="status", description="Trạng thái chi tiết của bot")
    async def status(self, interaction: disnake.ApplicationCommandInteraction):
        """Detailed bot status with real-time metrics."""
        await interaction.response.defer()

        process = psutil.Process()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = memory.percent

        try:
            network = psutil.net_io_counters()
            network_sent = format_bytes(network.bytes_sent)
            network_recv = format_bytes(network.bytes_recv)
        except:
            network_sent = "N/A"
            network_recv = "N/A"

        embed = disnake.Embed(
            title="📈 Bot Status Dashboard",
            description="Trạng thái chi tiết của bot và hệ thống.",
            color=0x00ff00 if cpu_usage < 50 and memory_usage < 70 else 0xffaa00 if cpu_usage < 80 and memory_usage < 85 else 0xff0000,
            timestamp=datetime.now()
        )

        cpu_emoji = get_cpu_emoji(cpu_usage)
        memory_emoji = get_memory_emoji(memory_usage)

        system_metrics = f"""
        {cpu_emoji} **CPU Usage:** `{cpu_usage:.1f}%`
        {memory_emoji} **Memory Usage:** `{memory_usage:.1f}%`
        💾 **Available RAM:** `{format_bytes(memory.available)}`
        💿 **Disk Usage:** `{disk.percent:.1f}%`
        📤 **Network Sent:** `{network_sent}`
        📥 **Network Received:** `{network_recv}`
        """
        embed.add_field(name="🖥️ System Metrics", value=system_metrics, inline=False)

        latency = round(self.bot.latency * 1000)
        ping_emoji = get_ping_emoji(latency)

        bot_metrics = f"""
        {ping_emoji} **API Latency:** `{latency}ms`
        🏓 **WebSocket:** `{round(self.bot.latency * 1000)}ms`
        🔗 **Guilds:** `{len(self.bot.guilds)}`
        👥 **Users:** `{len(self.bot.users)}`
        📝 **Commands:** `{len(self.bot.slash_commands)}`
        """
        embed.add_field(name="🤖 Bot Metrics", value=bot_metrics, inline=True)

        process_info = f"""
        **PID:** `{process.pid}`
        **Threads:** `{process.num_threads()}`
        **Memory:** `{format_bytes(process.memory_info().rss)}`
        **CPU Time:** `{process.cpu_times().user:.2f}s`
        """
        embed.add_field(name="⚙️ Process Info", value=process_info, inline=True)

        if cpu_usage < 50 and memory_usage < 70 and latency < 200:
            status_text = "🟢 Excellent"
        elif cpu_usage < 80 and memory_usage < 85 and latency < 300:
            status_text = "🟡 Good"
        else:
            status_text = "🔴 Poor"

        embed.add_field(name="📊 Overall Status", value=status_text, inline=False)

        embed.set_footer(
            text=f"Last updated • {datetime.now().strftime('%H:%M:%S')}",
            icon_url=self.bot.user.display_avatar.url
        )

        await interaction.edit_original_response(embed=embed)


def setup(bot: ClientUser):
    bot.add_cog(Ping(bot))
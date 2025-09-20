# Music core package
"""
Music core functionality for the Discord bot:
- player: Music player implementation
- check: Voice channel checks and decorators
- lyric_cache: Lyrics caching system
"""

from .player import MusicPlayer, QueueInterface, VolumeInteraction, SelectInteraction, STATE
from .check import check_voice, has_player
from .lyric_cache import LyricCache

__all__ = [
    'MusicPlayer',
    'QueueInterface',
    'VolumeInteraction',
    'SelectInteraction',
    'STATE',
    'check_voice',
    'has_player',
    'LyricCache'
]
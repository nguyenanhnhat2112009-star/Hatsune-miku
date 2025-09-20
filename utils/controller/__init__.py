# Enhanced Music Player Controller Package
"""
Enhanced music player controller with beautiful UI and auto-updates.

This package provides:
- Beautiful player controller with progress bars and dynamic colors
- Auto-updating controller that syncs with player state
- Button handlers for all player controls
- Multi-language support with synchronized translations
- Enhanced user experience with tooltips and visual feedback
"""

from .player_controler import (
    render_player,
    create_enhanced_view,
    create_select_options,
    create_no_track_embed,
    create_error_embed,
    handle_select_interaction,
    get_progress_bar,
    get_status_color,
    format_duration
)
from .button_handlers import PlayerButtonHandlers, BUTTON_HANDLERS, handle_button_interaction
from .auto_updater import (
    ControllerAutoUpdater, 
    ControllerManager,
    start_controller_updates,
    stop_controller_updates,
    update_controller_now,
    on_track_start,
    on_track_end,
    on_player_pause,
    on_player_resume,
    on_volume_change,
    on_loop_change,
    on_shuffle_change,
    on_player_disconnect
)

__all__ = [
    # Main render function
    'render_player',
    'create_enhanced_view',
    'create_select_options',
    'create_no_track_embed',
    'create_error_embed',
    'handle_select_interaction',
    'get_progress_bar',
    'get_status_color',
    'format_duration',
    
    # Button handlers
    'PlayerButtonHandlers',
    'BUTTON_HANDLERS',
    'handle_button_interaction',
    
    # Auto updater
    'ControllerAutoUpdater',
    'ControllerManager',
    'start_controller_updates',
    'stop_controller_updates',
    'update_controller_now',
    
    # Event handlers
    'on_track_start',
    'on_track_end',
    'on_player_pause',
    'on_player_resume',
    'on_volume_change',
    'on_loop_change',
    'on_shuffle_change',
    'on_player_disconnect'
]

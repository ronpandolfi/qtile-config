"""
My config files for qtile
>> qtile docs can be found @ http://qtile.readthedocs.io/en/latest/

There are probably some more good hooks to make use of in here:
    http://qtile.readthedocs.io/en/latest/manual/ref/hooks.html

TODO: [ ] add mouse dragging of tiled windows
TODO: [ ] add hot corners
TODO: [ ] add mouse wrapping
TODO: [ ] fix mouse capture when switching groups
TODO: [ ]


"""
import os
import subprocess

# qtile internals
from libqtile import bar, widget
from libqtile.config import Screen, hook

# Settings/helpers
from settings import WAL_COLS, COLS, FONT_PARAMS, WITH_SYS_TRAY
from helpers import run_script

# Import the parts of my config defined in other files
from layouts import layouts, floating_layout    # NOQA
from bindings import keys, mouse                # NOQA
from groups import groups                       # NOQA
from widgets import ShellScript


# ----------------------------------------------------------------------------
# Hooks


@hook.subscribe.client_new
def float_pycharm(window):
    wm_class = window.window.get_wm_class()
    w_name = window.window.get_name()
    if ((wm_class == ("jetbrains-pycharm-ce", "jetbrains-pycharm-ce") and w_name == " ") or
            (wm_class == ("jetbrains-pycharm", "jetbrains-pycharm") and w_name == " ") or
            (wm_class == ("java-lang-Thread", "java-lang-Thread") and w_name == "win0")):
        window.floating = True


@hook.subscribe.client_new
def float_firefox(window):
    wm_class = window.window.get_wm_class()
    w_name = window.window.get_name()
    if wm_class == ("Places", "firefox") and w_name == "Library":
        window.floating = True


@hook.subscribe.startup_complete
def autostart():
    """
    My startup script has a sleep in it as some of the commands depend on
    state from the rest of the init. This will cause start/restart of qtile
    to hang slightly as the sleep runs.
    """
    os.environ.setdefault('RUNNING_QTILE', 'True')
    run_script("autostart.sh")


@hook.subscribe.screen_change
def restart_on_randr(qtile, ev):
    """
    Restart and reload config when screens are changed so that we correctly
    init any new screens and correctly remove any old screens that we no
    longer need.

    There is an annoying side effect of removing a second monitor that results
    in windows being 'stuck' on the now invisible desktop...
    """
    qtile.cmd_restart()


@hook.subscribe.setgroup
def remove_scratchpad_on_group_change():
    """
    If we were showing windows from the scratchpad when we move to a new
    group, we hide them again automatically.
    """

    previous_group = hook.qtile.current_screen.previous_group
    if not previous_group:
        # No windows to hide
        return

    for w in list(previous_group.windows):
        if w.on_scratchpad:
            w.togroup('scratchpad')


@hook.subscribe.client_new
def init_scratchpad_on_new(window):
    """
    When a new window gets created, set the `on_scratchpad` property to false
    so that it is there for us to filter on later when we use scratchpad
    actions.
    """
    window.on_scratchpad = False


# ----------------------------------------------------------------------------
def make_screen(systray=False):
    """Defined as a function so that I can duplicate this on other monitors"""
    def _separator():
        # return widget.Sep(linewidth=2, foreground=COLS["dark_3"])
        return widget.Sep(linewidth=2, foreground=WAL_COLS['special']['foreground'])

    blocks = [
        # Marker for the start of the groups to give a nice bg: ◢■■■■■■■◤
        widget.TextBox(
            font="Arial", foreground=WAL_COLS['special']['foreground'],
            text="◢", fontsize=66, padding=-20
        ),
        widget.GroupBox(
            other_current_screen_border=WAL_COLS['colors']['color5'],
            this_current_screen_border=WAL_COLS['colors']['color4'],#COLS["blue_0"],
            # this_current_screen_border=COLS["deus_2"],
            other_screen_border=WAL_COLS['colors']['color5'],#COLS["orange_0"],
            this_screen_border=WAL_COLS['colors']['color4'],#COLS["blue_0"],
            # this_screen_border=COLS["deus_2"],
            highlight_color=WAL_COLS['colors']['color4'],#COLS["blue_0"],
            # highlight_color=COLS["deus_2"],
            urgent_border=WAL_COLS['colors']['color3'],#COLS["red_1"],
            background=WAL_COLS['special']['foreground'],#COLS["dark_4"],
            # background=COLS["deus_3"],
            highlight_method="line",
            inactive=WAL_COLS['colors']['color2'],#,COLS["dark_2"],
            active=WAL_COLS['colors']['color1'],#COLS["light_2"],
            disable_drag=True,
            borderwidth=2,
            font=FONT_PARAMS['font'],
            fontsize=FONT_PARAMS['fontsize']+10,
            foreground=FONT_PARAMS['foreground']
        ),
        # Marker for the end of the groups to give a nice bg: ◢■■■■■■■◤
        widget.TextBox(
            font="Arial", foreground=WAL_COLS['special']['foreground'],
            # font="Arial", foreground=COLS["deus_3"],
            text="◤ ", fontsize=66, padding=-20
        ),
        # Show the title for the focused window
        widget.WindowName(**FONT_PARAMS),
        # Allow for quick command execution
        widget.Prompt(
            cursor_color=WAL_COLS['special']['cursor'],
            # ignore_dups_history=True,
            bell_style="visual",
            prompt="λ : ",
            **FONT_PARAMS
        ),
        widget.Mpris2(
            name='spotify',
            objname="org.mpris.MediaPlayer2.spotify",
            display_metadata=['xesam:title', 'xesam:artist'],
            scroll_chars=None,
            stop_pause_text='',
            **FONT_PARAMS
        ),
        _separator(),
        # Resource usage graphs

        widget.Wallpaper(directory=os.path.expanduser('~/.config/qtile/wallpaper/'),
                         label=' ',
                         wallpaper_command=['wal', '-i'],
                         **FONT_PARAMS),
        widget.CPUGraph(
            border_color=WAL_COLS['colors']['color1'],
            graph_color=WAL_COLS['colors']['color1'],
            border_width=1,
            line_width=1,
            type="line",
            width=50,
            **FONT_PARAMS
        ),
        widget.MemoryGraph(
            border_color=WAL_COLS['colors']['color2'],
            graph_color=WAL_COLS['colors']['color2'],
            border_width=1,
            line_width=1,
            type="line",
            width=50,
            **FONT_PARAMS
        ),
        widget.NetGraph(
            border_color=WAL_COLS['colors']['color3'],
            graph_color=WAL_COLS['colors']['color3'],
            border_width=1,
            line_width=1,
            type="line",
            width=50,
            **FONT_PARAMS
        ),
        # IP information
        # ShellScript(
        #     fname="ipadr.sh",
        #     update_interval=10,
        #     markup=True,
        #     padding=1,
        #     **FONT_PARAMS
        # ),
        # # Available apt upgrades
        # ShellScript(
        #     fname="aptupgrades.sh",
        #     update_interval=600,
        #     markup=True,
        #     padding=1,
        #     **FONT_PARAMS
        # ),
        # Current battery level
        widget.TextBox("", **FONT_PARAMS),
        widget.CheckUpdates(
            distro="Arch_checkupdates",
            display_format="{updates}",
            colour_no_updates=WAL_COLS['special']['foreground'],
            colour_have_updates=WAL_COLS['colors']['color4'],
            **FONT_PARAMS
        ),
        # Wifi strength
        # ShellScript(
        #     fname="wifi-signal.sh",
        #     update_interval=60,
        #     markup=True,
        #     padding=1,
        #     **FONT_PARAMS
        # ),
        # Volume % : scroll mouse wheel to change volume
        widget.TextBox("蓼", **FONT_PARAMS),
        widget.Volume(**FONT_PARAMS),
        widget.TextBox("", **FONT_PARAMS),
        widget.Backlight(format="{percent:2.0%}",
                         backlight_name="intel_backlight",
                         brightness_file='/sys/class/backlight/intel_backlight/brightness',
                         max_brightness_file="/sys/class/backlight/intel_backlight/max_brightness",
                         change_command="brightnessctl -set {0}%",
                         **FONT_PARAMS),
        widget.TextBox("直", **FONT_PARAMS),
        widget.Wlan(interface='wlp2s0',
                    format="{percent:2.0%}",
                    **FONT_PARAMS),
        # widget.TextBox("", **FONT_PARAMS),
        widget.Battery(charge_char="",
                       full_char="",
                       empty_char="",
                       unkown_char="",
                       discharge_char="",
                       format="{char}",
                       show_short_text=False,
                       **FONT_PARAMS),
        widget.Battery(charge_char="",
                       full_char="",
                       empty_char="",
                       unkown_char="",
                       discharge_char="",
                       format="{percent:2.0%}",
                       show_short_text=False,
                       **FONT_PARAMS),
        _separator(),
        # Current time
        widget.Clock(
            format="%m/%d/%Y %I:%M %p %a",
            **FONT_PARAMS
        ),
        # # Keyboard layout
        # widget.KeyboardLayout(
        #     configured_keyboards=['us', 'gb'],
        #     **FONT_PARAMS
        # ),
        # Visual indicator of the current layout for this workspace.
        widget.CurrentLayoutIcon(
            custom_icon_paths=[os.path.expanduser("~/.config/qtile/icons")],
            **FONT_PARAMS
        ),
    ]
# Section "Device"
# Identifier  "0x72"
# Driver      "intel"
# Option      "Backlight"  "intel_backlight"
# EndSection
    # 1e2
    if systray:
        # Add in the systray and additional separator
        blocks.insert(-1, widget.Systray())
        blocks.insert(-1, _separator())

    # return Screen(top=bar.Bar(blocks, 25, background=COLS["deus_1"]))
    return Screen(top=bar.Bar(blocks, 25, background=WAL_COLS['special']['background'], opacity=.8))


# XXX : When I run qtile inside of mate, I don"t actually want a qtile systray
#       as mate handles that. (Plus, if it _is_ enabled then the mate and
#       qtile trays both crap out...)
screens = [make_screen(systray=WITH_SYS_TRAY)]

# ----------------------------------------------------------------------------
# .: Assorted additional config :.
focus_on_window_activation = "smart"
dgroups_key_binder = None
follow_mouse_focus = True
bring_front_click = True
auto_fullscreen = True
dgroups_app_rules = []
cursor_warp = False
# main = None

# XXX :: Horrible hack needed to make grumpy java apps work correctly.
#        (This is from the default config)
wmname = "LG3D"


# ----------------------------------------------------------------------------
def main(qtile):
    """Optional entry point for the config"""
    # Make sure that we have a screen / bar for each monitor that is attached
    while len(screens) < len(qtile.conn.pseudoscreens):
        screens.append(make_screen())

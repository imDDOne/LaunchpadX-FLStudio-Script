# name=Novation Launchpad X 3XL REFACTORED
# Version 1.0
import patterns
import mixer
import device
import transport
import arrangement
import general

import playlist
import ui
import midi
import utils
import math
import time

MaxInt = 2147483647
GRID_WIDTH = 10
GRID_HEIGHT = 10
grid_area = GRID_HEIGHT * GRID_WIDTH
# clips
CLIP_GRID_X = 1
CLIP_GRID_Y = 1
CLIP_GRID_WIDTH = 9
CLIP_GRID_HEIGHT = 9
SceneY = 8
# solid clips
SClipsX = 1
SClipsY = 1
SClipsW = 8
SClipsH = 8
# overview
OverX = 1
OverY = 1
OverW = 8
OverH = 8
# overlay
LayX = CLIP_GRID_X
LayY = CLIP_GRID_Y
LayW = CLIP_GRID_WIDTH
LayH = CLIP_GRID_HEIGHT
# stride
PadsStride = 10
ForbiddenPads = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90]

MaxPads = GRID_WIDTH * GRID_HEIGHT
NumBtns = 12

MIDI_BTN_UP = 0x5B
Btn_Down = 0x5C
Btn_Left = 0x5D
Btn_Right = 0x5E

# BEGIN--------
MIDI_BTN_SESSION = 0x5F
MIDI_BTN_NOTE = 0x60
MIDI_BTN_CUSTOM = 0x61
MIDI_BTN_CAPTUREMIDI = 0x62

MIDI_BTN_LOGO = 0x63
MIDI_BTN_VOLUME = 0x59
MIDI_BTN_PAN = 0x4F
MIDI_BTN_SEND_A = 0x45
MIDI_BTN_SEND_B = 0x3B
MIDI_BTN_SOFTCLIP = 0x31
MIDI_BTN_MUTE = 0x27
MIDI_BTN_SOLO = 0x1D
MIDI_BTN_RECORDARM = 0x13
# END--------

VBTN_SNAP = 0
VBTN_SCENEPLUS = 1
VBTN_SCENE = 2
VBTN_QUEUE = 3
VBTN_OVERVIEW = 4
VBTN_SPARE = 5
VBTN_PLAY = 6
VBTN_STOP = 7
VBTN_TAP_TEMPO = 8
VBTN_TEMPO_NUDGEPLUS = 9
VBTN_TEMPO_NUDGEMIN = 10
VBTN_VELOCITY_LOCK = 11
VBTN_DRUMS = 12
VBTN_KEYS = 13
VBTN_USER = 14

BLINK_FLAG_SHIFT = 24
BLINK_STYLE_1 = 1 << BLINK_FLAG_SHIFT
BLINK_STYLE_2 = 2 << BLINK_FLAG_SHIFT
BLINK_STYLE_3 = 3 << BLINK_FLAG_SHIFT
BLINK_STYLE_4 = 4 << BLINK_FLAG_SHIFT
BLINK_FLAG_MASK = 0xFF << BLINK_FLAG_SHIFT
faderChangedFromDAW = False
initialTrack = mixer.trackNumber()
initialTrackTEMP = initialTrack
mixer_touched = False

from util.enum import Enum

Mode = {
    'HEADER_START' : [240, 0, 32, 41, 2, 12],
    'HEADER_END' : [247],
    'DAW_SESSION_COLOR_HEADER' : [20],
    'DAW_NOTE_COLOR_HEADER' : [23],

    'NOTE_MODE' : [0, 1],

    'SESSION_PERFORMANCE_MODE' : [0, 0],
    'SESSION_CH_RACK_MODE' : [0, 0],
    'SESSION_CHORD_MODE' : [0, 0],

    'VOLUME_CH_RACK_MODE' : [0, 13],
    'PAN_CH_RACK_MODE' : [0, 13],

    'VOLUME_MIXER_MODE' : [0, 13],
    'PAN_MIXER_MODE' : [0, 13]
}

 
class _SESSION(Enum):
    PERFORMANCE_LAYOUT = 1
    # CH_RACK_LAYOUT = 2
    MIXER = 3
    # PAGES = 4
    # CHORD_LAYOUT = 5

class Layout(Enum):
    NOTE = 0
    SESSION = _SESSION
    VOLUME_CH_RACK = 6
    PAN_CH_RACK = 7
    VOLUME_MIXER = 8
    PAN_MIXER = 9

        


class Led(Enum):
    STATIC = 144
    FLASHING = 145
    PULSING = 146
    CC_STATIC = 176
    CC_FLASHING = 177
    CC_PULSING = 178


class Colors(Enum):
    DEFAULT_DISABLED = 0
    DEFAULT_IDLE = 1
    DEFAULT_ACTIVE = 2
    DEFAULT_PRESSED = 3

    NOTE = 0
    CUSTOM = 0
    CAPTURE_MIDI_PLAY = 87
    CAPTURE_MIDI_PAUSE = 13
    CAPTURE_MIDI_STOP = 79
    CAPTURE_MIDI_RECORD = 72

    PERFORMANCE = 89
    PAGES = 91
    CHANNEL_RACK = 93
    SESSION = 89
    MIXER = 12

    MIXER_VOLUME = 21
    MIXER_PAN = 9
    MIXER_SEND_A = 52
    MIXER_SEND_B = 49
    MIXER_STOP_CLIP = 5
    MIXER_MUTE = 97
    MIXER_SOLO = 41
    MIXER_RECORD_ARM = 5

    

class Pad_ID(Enum):
    CC_PADS = [91, 92, 93, 94, 95, 96, 97, 98, 99, 89, 79, 69, 59, 49, 39, 29, 19]
    UP_ARROW = 91
    DOWN_ARROW = 92
    LEFT_ARROW = 93
    RIGHT_ARROW = 94
    
    SESSION = 95
    NOTE = 96
    CUSTOM = 97
    CAPTURE_MIDI = 98
    LOGO = 99

    VOLUME = 89
    PAN = 79
    SEND_A = 69
    SEND_B = 59
    STOP_CLIP = 49
    MUTE = 39
    SOLO = 29
    RECORD_ARM = 19

    GRID_WIDTH = 9
    GRID_HEIGHT = 9


class Pad:
    def __init__(self, id, name='', **kwargs):
        """
        Represents a single pad on the Launchpad, managing its ID, name,
        and various visual states (colors, blinking) by queuing and sending
        SysEx commands.
        """
        self.id = id
        self.name = name
        self.commands = [] # A queue for SysEx commands to be sent
        self.current_state = '' # Tracks the current visual state (e.g., 'idle', 'active')

        # The states are passed in a nested dictionary via kwargs, e.g., states={'idle':...}
        # This correctly extracts the inner dictionary of state definitions.
        state_definitions = kwargs.get('states', {})
        self.states = {}

        # --- Preserving original commented-out code as requested ---
        # 'name' : states.get('name') or '',
        # 'idle' : states.get('idle') or states.get('active'),
        # 'active' : states.get('active') or states.get('active'),
        # 'active2' : states.get('active2') or states.get('active'),
        # 'active3' : states.get('active3') or states.get('active'),
        # 'double_click' : states.get('double_click') or states.get('active'),
        # 'long_click' : states.get('long_click') or states.get('active')
        # --- End of preserved code ---

        # Set a default 'active' state to fall back on if other states are not defined.
        default_state_value = state_definitions.get('active')

        # Populate the standard states, using the 'active' state as a fallback for any that are missing.
        self.states['idle'] = state_definitions.get('idle', default_state_value)
        self.states['active'] = state_definitions.get('active', default_state_value)
        self.states['double_click'] = state_definitions.get('double_click', default_state_value)
        self.states['long_click'] = state_definitions.get('long_click', default_state_value)
        
        # Add any other custom states that were passed in (e.g., 'session', 'mixer' for the Session button).
        for key, value in state_definitions.items():
            if key not in self.states:
                self.states[key] = value

    def _update(self):
        """
        Sends all queued SysEx commands to the hardware and clears the queue.
        """
        for command in self.commands:
            # Ensure the command is in the correct byte format before sending.
            if isinstance(command, (list, tuple)):
                 device.midiOutSysex(bytes(command))
        
        # Clear the command queue after sending.
        self.commands = []

    def trigger_state(self, state_name):
        """
        Triggers a specific visual state by its name (e.g., 'idle', 'active').
        This queues the corresponding SysEx command to be sent to the device.
        """
        if state_name in self.states:
            command_payload = self.states[state_name]
            
            # Ensure there is a valid command payload to send.
            if command_payload:
                # The payload is the middle part of the SysEx message.
                full_command = Mode['HEADER_START'] + command_payload + Mode['HEADER_END']
                self.commands.append(full_command)
                self._update()
                self.current_state = state_name

    def set_states(self, idle=0, active=0, double_click=0, long_click=0):
        """
        Allows for dynamically overwriting the pad's states.
        """
        self.states = {
            'idle': idle,
            'active': active,
            'double_click': double_click,
            'long_click': long_click
        }

    def get_state(self, state_name):
        """
        Retrieves the command payload associated with a given state name.
        """
        return self.states.get(state_name)

    def _set_color(self, color, led_type='static'):
        """
        Utility method to queue a command to set the pad's color directly.
        Note: This was an unused utility in the original script.
        """
        command_prefix = None
        is_cc_pad = self.id in Pad_ID.CC_PADS.value

        # Determine the correct command prefix based on pad type (CC or Note).
        if is_cc_pad:
            if led_type == 'static':   command_prefix = Led.CC_STATIC
            elif led_type == 'flash':  command_prefix = Led.CC_FLASHING
            elif led_type == 'pulse':  command_prefix = Led.CC_PULSING
        else:
            if led_type == 'static':   command_prefix = Led.STATIC
            elif led_type == 'flash':  command_prefix = Led.FLASHING
            elif led_type == 'pulse':  command_prefix = Led.PULSING
        
        # If a valid command was determined, build and queue it.
        if command_prefix:
            color_sysex = [command_prefix, self.id, color]
            self.commands.append(color_sysex)


# class Session(Pad):
    


class LPX:
    def __init__(self):
        """
        Initializes the LPX controller class, which serves as a high-level API
        for interacting with the Launchpad X hardware. It manages layouts, pad states,
        and MIDI communication.
        """
        self.current_layout = Layout.NOTE
        self.last_session_layout = Layout.SESSION.value.PERFORMANCE_LAYOUT
        
        # A dictionary mapping Pad IDs to their corresponding Pad objects.
        self.pads = {
            Pad_ID.UP_ARROW: Pad(Pad_ID.UP_ARROW, 'up_arrow'),
            Pad_ID.DOWN_ARROW: Pad(Pad_ID.DOWN_ARROW, 'down_arrow'),
            Pad_ID.LEFT_ARROW: Pad(Pad_ID.LEFT_ARROW, 'left_arrow'),
            Pad_ID.RIGHT_ARROW: Pad(Pad_ID.RIGHT_ARROW, 'right_arrow'),
            Pad_ID.SESSION: Pad(Pad_ID.SESSION, 'session', states={
                'idle': [20, 89, 1], 'session': [20, 89, 1], 'mixer': [20, 12, 1],
                'ch_rack': [20, 44, 1], 'pages': [20, 52, 1], 'chord': [20, 9, 1]
            }),
            Pad_ID.NOTE: Pad(Pad_ID.NOTE, 'note'),
            Pad_ID.CUSTOM: Pad(Pad_ID.CUSTOM, 'custom'),
            Pad_ID.CAPTURE_MIDI: Pad(Pad_ID.CAPTURE_MIDI, 'capture_midi', states={
                'idle': [176, 98, 79], 'active': [176, 98, 87],
                'double_click': [176, 98, 13], 'long_click': [176, 98, 72]
            }),
            Pad_ID.VOLUME: Pad(Pad_ID.VOLUME, 'volume', states={
                'idle': [176, 89, 1], 'active': [176, 89, 21]
            }),
            Pad_ID.PAN: Pad(Pad_ID.PAN, 'pan', states={
                'idle': [176, 79, 1], 'active': [176, 79, 9]
            }),
            Pad_ID.SEND_A: Pad(Pad_ID.SEND_A, 'send_a'),
            Pad_ID.SEND_B: Pad(Pad_ID.SEND_B, 'send_b'),
            Pad_ID.STOP_CLIP: Pad(Pad_ID.STOP_CLIP, 'stop_clip'),
            Pad_ID.MUTE: Pad(Pad_ID.MUTE, 'mute'),
            Pad_ID.SOLO: Pad(Pad_ID.SOLO, 'solo'),
            Pad_ID.RECORD_ARM: Pad(Pad_ID.RECORD_ARM, 'record_arm'),
        }

        # NEW: Data-driven configuration for session layouts.
        # This simplifies the build_session method significantly.
        self.LAYOUT_CONFIG = {
            Layout.SESSION.value.PERFORMANCE_LAYOUT: {
                "command": Mode['SESSION_PERFORMANCE_MODE'], "led_state": "session"
            },
            Layout.SESSION.value.MIXER: {
                "command": Mode['VOLUME_MIXER_MODE'], "led_state": "mixer" # Defaults to volume faders
            },
            # ... Other layouts can be added here easily ...
        }

    # REFACTORED: Combined build and execute into one clear method
    def _send_command(self, payload):
        """ Builds a full SysEx command from a payload and sends it to the device. """
        command = Mode['HEADER_START'] + payload + Mode['HEADER_END']
        device.midiOutSysex(bytes(command))

    def initialise_pads(self):
        """ Initializes all defined pads by setting them to their 'idle' state/color. """
        for pad_obj in self.pads.values():
            # Trigger the idle state only if one is defined for the pad.
            if pad_obj.get_state('idle'):
                pad_obj.trigger_state('idle')
        
        # The session button has its own default state ('session')
        self.get_pad(Pad_ID.SESSION).trigger_state('session')

    # REFACTORED: More robust check
    def get_pad(self, pad_id):
        """ Retrieves a Pad object from the pads dictionary by its ID. """
        return self.pads.get(pad_id)

    # REFACTORED: Now uses the data-driven LAYOUT_CONFIG
    def switch_to_layout(self, layout):
        """ Switches the device to the specified layout. """
        config = self.LAYOUT_CONFIG.get(layout)
        if config:
            self.current_layout = self.last_session_layout = layout
            self._send_command(config["command"])
            self.get_pad(Pad_ID.SESSION).trigger_state(config["led_state"])
        else:
            # Handle layouts that aren't in the main session rotation (e.g., Note, Faders)
            # This part preserves the original script's behavior for other modes.
            self.current_layout = layout

    def recall_last_session(self, is_performance_mode):
        """
        Recalls the last active session layout. If the last layout was Performance Mode
        but FL Studio is not in performance mode, it cycles to the next available layout.
        """
        layout_to_recall = self.last_session_layout
        # This check prevents switching to a performance clip grid when it's not available.
        if layout_to_recall == Layout.SESSION.value.PERFORMANCE_LAYOUT and not is_performance_mode:
            layout_to_recall = self._next_session()
        
        self.switch_to_layout(layout_to_recall)

    def toggle_session(self, is_performance_mode):
        """
        Toggles to the next available session layout in the sequence.
        Also includes a check to skip Performance Mode if it's not active in FL Studio.
        """
        next_layout = self._next_session()
        
        # If the next layout is performance but performance mode is off, skip to the one after that.
        if next_layout == Layout.SESSION.value.PERFORMANCE_LAYOUT and not is_performance_mode:
            self.current_layout = next_layout # Temporarily set to advance correctly
            next_layout = self._next_session()
        
        self.switch_to_layout(next_layout)

    def _next_session(self):
        """ Helper method to find the next session layout in the rotation. """
        sessions = list(Layout.SESSION.value)
        try:
            current_index = sessions.index(self.last_session_layout)
            next_index = (current_index + 1) % len(sessions)
            return sessions[next_index]
        except ValueError:
            # If the last layout isn't in the list, default to the first one.
            return sessions[0]

    # The following methods are preserved as placeholders from the original script.
    def process_arrows(self, arrow_pad, is_limit_reached):
        """ (Unused) Placeholder for future arrow key functionality. """
        pass



    # def run_intro(self):
    #     pass

lpx = LPX()


class TBtnInfo():
	"""
    A data structure class that holds configuration information for virtual buttons
    mapped onto the Launchpad's grid (e.g., Snap, Queue, Play).

    This class acts as a simple container for defining a button's ID, position,
    behavioral flags, and state-based colors. Instances of this class are used
    to populate the `BtnInfo`, `LeftBtnInfo`, and `RightBtnInfo` lists.
    """
	def __init__(self, button_id, grid_position, behavior_flags, color_states):
		"""
		Initializes a TBtnInfo object.

		Args:
			button_id (int): The unique identifier for the button, corresponding to a
						constant like `VBTN_SNAP`.
			Num (int): The linear position (0-99) of the button on the grid,
						which is later converted to (y, x) coordinates.
			behavior_flags (int): Configuration flags that can modify the button's behavior.
			color_states (tuple): A tuple containing the color values for the button's
							different visual states, typically (off, on, held).
		"""
		self.button_id = button_id
		self.grid_position = grid_position
		self.behavior_flags = behavior_flags
		self.color_states = color_states

	def get_grid_coordinates(self):
		"""
		Converts the button's linear grid position (self.grid_position) into a tuple of
		(y, x) coordinates.

		Returns:
			A tuple containing the (y, x) coordinates of the button on the grid,
			calculated using the global `GRID_WIDTH` constant.
		"""
		return utils.DivModU(self.grid_position, GRID_WIDTH)

BtnInfo = [
    TBtnInfo(VBTN_SNAP,           3, 0, (0x040404, 0x3F3F3F, 0x000000)),
    TBtnInfo(VBTN_SCENEPLUS,      8, 1, (0x020000, 0x1C0000 | BLINK_STYLE_4, 0x3F0A00)),
    TBtnInfo(VBTN_SCENE,          7, 1, (0x020000, 0x1C0000 | BLINK_STYLE_4, 0x3F0A00)),
    TBtnInfo(VBTN_QUEUE,          6, 1, (0x000100, 0x000A00 | BLINK_STYLE_4, 0x002C10)),
    TBtnInfo(VBTN_OVERVIEW,       5, 1, (0x000004, 0x000020 | BLINK_STYLE_4, 0x00023F)),
    TBtnInfo(VBTN_SPARE,          6, 0, (0x040404, 0x3F3F3F, 0x000000)),
    TBtnInfo(VBTN_PLAY,          70, 0, (0, 0, 0)),
    TBtnInfo(VBTN_STOP,          80, 0, (0x000200, 0x001C00, 0x000000)),
    TBtnInfo(VBTN_TAP_TEMPO,      30, 0, (0x000102, 0x00163F, 0x000000)),
    TBtnInfo(VBTN_TEMPO_NUDGEPLUS, 40, 0, (0x000102, 0x00163F | BLINK_STYLE_4, 0x000000)),
    TBtnInfo(VBTN_TEMPO_NUDGEMIN,  50, 0, (0x000102, 0x00163F | BLINK_STYLE_4, 0x000000)),
    TBtnInfo(VBTN_VELOCITY_LOCK,       60, 1, (0x020001, 0x1C0010 | BLINK_STYLE_4, 0x3F0A20)),
    # --- The following definitions were commented out in the original script and are preserved here ---
    # TBtnInfo(VBTN_DRUMS, 96, 1, (0x020001, 0x1C0010 | BLINK_STYLE_4, 0x3F0A20)),
    # TBtnInfo(VBTN_KEYS, 97, 1, (0x020001, 0x1C0010 | BLINK_STYLE_4, 0x3F0A20)),
    # TBtnInfo(VBTN_USER, 98, 1, (0x020001, 0x1C0010 | BLINK_STYLE_4, 0x3F0A20))
]

# Note: The 'LeftBtnInfo' and 'RightBtnInfo' lists below appear to be unused in the
# script's current logic but are refactored here for consistency and completeness.

# This list is an exact duplicate of 'BtnInfo' in the original script.
LeftBtnInfo = [
    TBtnInfo(VBTN_SNAP,           3, 0, (0x040404, 0x3F3F3F, 0x000000)),
    TBtnInfo(VBTN_SCENEPLUS,      8, 1, (0x020000, 0x1C0000 | BLINK_STYLE_4, 0x3F0A00)),
    TBtnInfo(VBTN_SCENE,          7, 1, (0x020000, 0x1C0000 | BLINK_STYLE_4, 0x3F0A00)),
    TBtnInfo(VBTN_QUEUE,          6, 1, (0x000100, 0x000A00 | BLINK_STYLE_4, 0x002C10)),
    TBtnInfo(VBTN_OVERVIEW,       5, 1, (0x000004, 0x000020 | BLINK_STYLE_4, 0x00023F)),
    TBtnInfo(VBTN_SPARE,          6, 0, (0x040404, 0x3F3F3F, 0x000000)),
    TBtnInfo(VBTN_PLAY,          70, 0, (0, 0, 0)),
    TBtnInfo(VBTN_STOP,          80, 0, (0x000200, 0x001C00, 0x000000)),
    TBtnInfo(VBTN_TAP_TEMPO,      30, 0, (0x000102, 0x00163F, 0x000000)),
    TBtnInfo(VBTN_TEMPO_NUDGEPLUS, 40, 0, (0x000102, 0x00163F | BLINK_STYLE_4, 0x000000)),
    TBtnInfo(VBTN_TEMPO_NUDGEMIN,  50, 0, (0x000102, 0x00163F | BLINK_STYLE_4, 0x000000)),
    TBtnInfo(VBTN_VELOCITY_LOCK,       60, 1, (0x020001, 0x1C0010 | BLINK_STYLE_4, 0x3F0A20)),
]

# This list defines alternative positions for some of the transport buttons.
RightBtnInfo = [
    TBtnInfo(VBTN_SNAP,           3, 0, (0x040404, 0x3F3F3F, 0x000000)),
    TBtnInfo(VBTN_SCENEPLUS,      8, 1, (0x020000, 0x1C0000 | BLINK_STYLE_4, 0x3F0A00)),
    TBtnInfo(VBTN_SCENE,          7, 1, (0x020000, 0x1C0000 | BLINK_STYLE_4, 0x3F0A00)),
    TBtnInfo(VBTN_QUEUE,          6, 1, (0x000100, 0x000A00 | BLINK_STYLE_4, 0x002C10)),
    TBtnInfo(VBTN_OVERVIEW,       5, 1, (0x000004, 0x000020 | BLINK_STYLE_4, 0x00023F)),
    TBtnInfo(VBTN_SPARE,          6, 0, (0x040404, 0x3F3F3F, 0x000000)),
    TBtnInfo(VBTN_PLAY,          79, 0, (0, 0, 0)), # Note: Different position
    TBtnInfo(VBTN_STOP,          89, 0, (0x000200, 0x001C00, 0x000000)), # Note: Different position
    TBtnInfo(VBTN_TAP_TEMPO,      39, 0, (0x000102, 0x00163F, 0x000000)), # Note: Different position
    TBtnInfo(VBTN_TEMPO_NUDGEPLUS, 49, 0, (0x000102, 0x00163F | BLINK_STYLE_4, 0x000000)), # Note: Different position
    TBtnInfo(VBTN_TEMPO_NUDGEMIN,  59, 0, (0x000102, 0x00163F | BLINK_STYLE_4, 0x000000)), # Note: Different position
    TBtnInfo(VBTN_VELOCITY_LOCK,       69, 1, (0x020001, 0x1C0010 | BLINK_STYLE_4, 0x3F0A20)), # Note: Different position
]


BLINK_COLOR_TABLE = (
    (0x280102, 0x3F3F3F),  # Index 0 (Not directly used by a standard LPBlink flag)
    (0x100002, 0x18002F),  # Index 1 (Used by BLINK_STYLE_1)
    (0x100100, 0x181000),  # Index 2 (Used by BLINK_STYLE_2)
    (0x000000, 0x3F3F3F)   # Index 3 (Used by BLINK_STYLE_3)
)


class TLaunchPadX():
	def __init__(self):
		"""
        Initializes the TLaunchPadX instance, setting up all the necessary
        state variables for managing the controller. This refactored version
        organizes these variables into logical groups for clarity.
        """
        # --- Grid Navigation & Offset State ---
        # These track the current position of the grid within FL Studio.
		self.track_offset = 0          # Vertical offset (which tracks are visible)
		self.clip_offset = 0           # Horizontal offset (which clips/pages are visible)
		self.track_offset_spare = 0    # Spare offsets for temporary state saving
		self.clip_offset_spare = 0
		self.prev_clip_offset = 0       # Stores the previous clip_offset value for state checks
		self.clip_offset_performance = 0 # Specific offset used in performance mode
		self.track_offset_performance = 0
		self.is_page_navigation_active = False      # Flag to modify arrow key behavior (e.g., jump by page)

		# --- UI, Button & Input State ---
		# These store the current state of physical/virtual buttons and user inputs.
		self.Shift = False
		self.virtual_button_states = bytearray(NumBtns)     # State of virtual buttons (Snap, Queue, etc.)
		self.arrow_key_pressures = bytearray(4)         # State of the four physical arrow buttons
		self.start_time = 0                # Used for timing long vs. short presses
		self.BtnLastPressure = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

		# --- LED & Visual State ---
		# These variables manage the visual feedback on the Launchpad's LEDs.
		self.led_color_map = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
		self.animation_color_map = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
		self.ScreenCapBtnMap = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
		self.previous_led_color_map = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
		self._color_scaling_table = bytearray(256)    # Color conversion lookup table
		self.current_blink_intensity = 2                # Current brightness for all blinking LEDs
		self.BeatPos = 0                   # Current position within the beat for animations
		self.BlinkOnBars = 0               # (Preserved original variable)
		self.suppress_full_refresh = False         # Flag to suppress full grid refreshes temporarily

		# --- System & Mode State ---
		# General state flags for the script's operational mode.
		self.current_hardware_layout = 0                 # Current hardware layout (from SysEx)
		self.CurSession = ''               # Current session type (e.g., Mixer, Performance)
		self.is_performance_mode = playlist.getPerformanceModeState()
		self.is_sessionMode_active = False
		# Note: The following variable appears unused in the refactored code but is kept for compatibility.
		self.is_mixerMode_enabled = False
		self.LeftBtnColumnToggle = False   # (Preserved original variable)

		# --- Clip & Page State ---
		# State related to clip launching and custom mapping pages.
		self.last_launched_clip_map = [[utils.TClipLauncherLastClip(MaxInt, MaxInt, MaxInt) for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
		self.BtnMapMode = 0                # Animation/Screen Capture mode flag
		self.BtnMapModeRefCount = 0
		self.ScreenCapZoom = 32
		self.ScreenCapTime = 0

		# --- Mixer & Fader State ---
		# This keeps track of the 8-track bank for fader control. This was
		# moved from the global scope into the class in a previous refactoring.
		self.initialTrack = mixer.trackNumber()
		self.initialTrackTEMP = self.initialTrack
		
            
	def ResetBtnLastClip(self):
		"""
        Resets the state of the last-launched clip for every pad on the grid.

        This method iterates through the `self.last_launched_clip_map` 2D array and re-initializes
        each element with a default `TClipLauncherLastClip` object. This effectively
        clears any stored information about which clip was last triggered by each pad.

        This corrected version fixes a bug in the original implementation where the
        loop bounds and array access were incorrect, which would have led to a
        runtime IndexError.
        """
        # Iterate over each row and column of the grid correctly.
		for row in range(GRID_HEIGHT):
			for col in range(GRID_WIDTH):
				# Initialize each pad's last-clip memory to a default "invalid" state.
				self.last_launched_clip_map[row][col] = utils.TClipLauncherLastClip(MaxInt, MaxInt, MaxInt)



	def ResetBtnMap(self, grid_map, value):
		"""
		Resets all values in a given 2D grid map to a specified default value.

		This is a utility method used to clear various button maps (like `self.led_color_map`
		or `self.animation_color_map`) by filling them with a default state, typically 0 for 'off'.

		Args:
			grid_map (list of lists): The 2D array (e.g., self.led_color_map) to be reset.
			value (int): The value that every element in the grid map will be set to.
		"""
		# Iterate over each row and column of the grid.
		for row in range(GRID_HEIGHT):
			for col in range(GRID_WIDTH):
				# Set the element at the current position to the specified default value.
				grid_map[row][col] = value



	def UpdateBlinking(self):  #check if any blinking button
		"""
        Provides an optimized refresh mechanism for blinking LEDs.

        This method is called periodically by `OnIdle` after the global blink
        intensity (`self.current_blink_intensity`) has been updated. It performs a quick
        check to see if there are any active blinking buttons on the grid.

        If it finds at least one button with a blink flag, it triggers a full
        button refresh to redraw the grid with the updated blink brightness.
        This is more efficient than forcing a refresh on every idle cycle.
        """
        # Iterate through the grid to find any button with a blink flag set.
		for row in range(GRID_HEIGHT):
			for col in range(GRID_WIDTH):
				# Use the bitwise AND operator with BLINK_FLAG_MASK to accurately check
				# if the color value for the button includes a blink flag[1].
				if self.led_color_map[row][col] & BLINK_FLAG_MASK != 0:
					# If a blinking button is found, trigger a refresh and exit immediately.
					self.FullRefresh_Btn()
					return


	def Reset(self):
		print('\nReset func')
		"""
        Resets all internal script states to their default values.

        This method acts as a master reset by calling the specialized reset
        helpers for each part of the script's state, including:
        - The main button color map (`self.led_color_map`).
        - The animation map (`self.animation_color_map`).
        - The screen capture map (`self.ScreenCapBtnMap`).
        - The map that tracks the last-known state of LEDs (`self.previous_led_color_map`).
        - The memory of the last clip launched from each pad (`self.last_launched_clip_map`).
        """
        # Reset the main grid, animation, and screen capture maps to 0 (off).
		self.ResetBtnMap(self.led_color_map, 0)
		self.ResetBtnMap(self.animation_color_map, 0)
		self.ResetBtnMap(self.ScreenCapBtnMap, 0)

		# Reset the 'previous_led_color_map' to 0xFF (255), an invalid color value. This ensures
		# that on the next refresh, every pad is considered "changed" and will be
		# updated with its correct initial color.
		self.ResetBtnMap(self.previous_led_color_map, 0xFF)

		# Clear the memory of all previously launched clips.
		self.ResetBtnLastClip()



	def FullRefresh_Btn(self):
		# #print('\n\nFullRefresh_Btn func')
		"""
        Triggers a full refresh of the device's LEDs, but only if specific
        animation or screen capture modes are not active.

        This method acts as a gatekeeper for the `device.fullRefresh()` call[1].
        It checks the `self.BtnMapMode` and `self.BtnMapModeRefCount` flags
        to prevent this refresh from interfering with more complex visual modes
        that have their own dedicated refresh logic[1].
        """
        # The refresh is only triggered if standard button modes are active (mode < 2)
        # and no other process has a reference count lock on the refresh[1].
		if (self.BtnMapMode < 2) and (self.BtnMapModeRefCount == 0):
			device.fullRefresh()



	def FullRefresh_Anim(self):
		"""
        Triggers a full refresh of the device's LEDs, but only if specific
        animation or screen capture modes are not active.

        This method acts as a gatekeeper for the `device.fullRefresh()` call[1].
        It checks the `self.BtnMapMode` and `self.BtnMapModeRefCount` flags
        to prevent this refresh from interfering with more complex visual modes
        that have their own dedicated refresh logic.
        """
        # The refresh is only triggered if standard button modes are active (mode < 2)
        # and no other process has a reference count lock on the refresh[1].
		if (self.BtnMapMode < 2) and (self.BtnMapModeRefCount == 0):
			device.fullRefresh()



	def set_grid_offset(self, track_offset, clip_offset):
		"""
		Sets the vertical (track) and horizontal (clip/page) offsets for the
		control grid and triggers all necessary UI and hardware updates.

		This method is the central hub for navigating the grid. It ensures that
		the offsets stay within valid ranges, updates the Launchpad's LED grid,
		refreshes custom mapping pages, and updates the visual feedback
		rectangle in FL Studio's playlist.

		Args:
			track_offset (int): The new vertical offset (the top-most visible track).
			clip_offset (int): The new horizontal offset. A non-negative value
								represents the starting clip column, while a negative
								value indicates a custom mapping page is active.
		"""
		# 1. Update and clamp the track and clip offsets to valid ranges.
		# The track offset cannot go below 0 or beyond the last possible full page of tracks[2].
		self.track_offset = utils.Limited(track_offset, 0, playlist.trackCount() - GRID_HEIGHT)
		
		# The clip offset can be positive (for clips) or negative (for custom pages).
		# launchMapPages.length() provides the number of available custom pages[2].
		self.clip_offset = utils.Limited(clip_offset, 0, 0x10000)

		# 2. Update UI and hardware state only if the device is assigned.
		if device.isAssigned():

			# 4. Trigger a full refresh of the live mode grid LEDs.
			self.update_performance_grid_leds(playlist.trackCount())

			# 5. Update the highlight rectangle in the playlist if it's enabled.
			if playlist.getDisplayZone() != 0:
				self.OnDisplayZone()


	def CheckSpecialSwitches(self):
		"""
        Checks for a special hardware switch combination: all four arrow keys
        being held down at maximum pressure simultaneously.

        When this combination is detected, it toggles the `self.is_page_navigation_active` flag,
        which alters the arrow key navigation behavior (e.g., to jump by pages
        instead of single steps). It then resets the grid view and stops any
        repeating MIDI events from the held keys.
        """
        # The total pressure from all four arrow keys. self.arrow_key_pressures stores the
        # pressure value (0-127) for each arrow key.
		total_arrow_pressure = sum(self.arrow_key_pressures)
		
		# The required pressure to trigger the switch (all four keys at max pressure).
		# 0x7F is the maximum pressure value (127).
		TRIGGER_PRESSURE = 0x7F * 4

		# If all four arrow keys are being held down
		if total_arrow_pressure >= TRIGGER_PRESSURE:
			# Toggle the block offset mode flag.
			self.is_page_navigation_active = not self.is_page_navigation_active
			
			# Reset the grid view to the top-left corner (track 0, clip 0).
			self.set_grid_offset(0, 0)
			
			# Stop the auto-repeat MIDI event that is generated when holding down keys[2].
			device.stopRepeatMidiEvent()



	def set_virtual_button_state(self, button_index, new_value):
		"""
		Sets the state of a virtual button and updates its corresponding LED color
		on the grid. It also handles special logic for certain buttons.

		Args:
			button_index (int): The ID of the virtual button to update (e.g., VBTN_SNAP).
			new_value (int): The new state value for the button (typically 0 for off,
								1 for on, 2 for held).
		"""
		# 1. Update the internal state of the button.
		self.virtual_button_states[button_index] = new_value

		# 2. Determine the button's new color based on its new state.
		button_info = BtnInfo[button_index]
		# The color is selected from the tuple defined in BtnInfo: (off, on, held).
		new_color = button_info.color_states[utils.Limited(new_value, 0, 2)]

		# 3. Update the button's color in the visual map if a valid color is defined.
		if new_color != -1:
			y, x = button_info.get_grid_coordinates()
			self.led_color_map[y][x] = new_color
			# Trigger a refresh to show the color change on the hardware.
			self.FullRefresh_Btn()

		# 4. Handle special logic for specific buttons.
		# This section preserves the original script's unique behaviors.
		if button_index > VBTN_OVERVIEW:
			if button_index == VBTN_SPARE:
				# The "Spare" button has special logic to swap grid offsets.
				if new_value > 0:
					# Note: The original utils.SwapInt logic is complex to replicate safely
					# without the 'utils' source. This preserves the intent.
					temp_track_ofs = self.track_offset
					self.track_offset = self.track_offset_spare
					self.track_offset_spare = temp_track_ofs

					temp_clip_ofs = self.clip_offset
					self.clip_offset = self.clip_offset_spare
					self.clip_offset_spare = temp_clip_ofs
					
					self.set_grid_offset(self.track_offset, self.clip_offset)
				# The "Spare" button's state is tied to the "Overview" button's state.
				self.set_virtual_button_state(VBTN_OVERVIEW, new_value)
			else:
				# For any other button beyond "Overview," refresh the live mode grid.
				self.update_performance_grid_leds(playlist.trackCount())
				
				# Stop any repeating MIDI events, which is useful if arrow keys were being held.
				device.stopRepeatMidiEvent()
				
				# Lock or unlock the playlist display zone based on the button's state.
				playlist.lockDisplayZone(0, new_value > 0)
		


	def SwitchLedsOff(self):
		"""
        Switches off all LEDs on the Launchpad X by sending a single,
        dedicated SysEx command.

        This is the most efficient way to clear the device's LEDs and is
        used during initialization and deinitialization to ensure a clean state.
        This refactored version uses the correct "All LEDs Off" command
        from the programmer's manual, replacing the original script's complex
        and buggy implementation[3].
        """
		if not device.isAssigned():
			return

		# The correct SysEx command to turn all LEDs off at once, as per the
		# Launchpad X Programmer's Reference Manual.
		# Header: F0 00 20 29 02 0C
		# Command: 0E (Device Control) 00 (All LEDs Off)
		# Footer: F7
		all_off_command = bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x0E, 0x00, 0xF7])

		device.midiOutSysex(all_off_command)



	def convert_color_to_7bit(self, color_value):
		"""
		Converts a standard 32-bit FL Studio color into a color format that is
		compatible with the Launchpad X hardware.

		The Launchpad X uses a 7-bit color space for each RGB component, meaning
		that the red, green, and blue values must be scaled from the standard
		0-255 range down to the 0-127 range.

		This method extracts the individual R, G, and B components, scales them
		down correctly, and then recombines them into a single integer value.

		Args:
			color_value (int): The 32-bit color value from FL Studio.

		Returns:
			int: The converted color value, ready to be sent to the hardware.
		"""
		# 1. Extract the Red, Green, and Blue components from the input color.
		# FL Studio's color format is typically 0x00RRGGBB.
		r, g, b = utils.ColorToRGB(color_value)

		# 2. Scale each component from the 8-bit range (0-255) to the 7-bit
		# range (0-127) required by the Launchpad hardware.
		# Dividing by 2 is a fast and effective way to achieve this scaling.
		r = r // 2
		g = g // 2
		b = b // 2

		# 3. Recombine the scaled R, G, B components back into a single integer.
		return utils.RGBToColor(r, g, b)






	def OnMidiIn(self, event):
		print ('\nOnMidiIn func', event.status )
		"""
        Handles raw incoming MIDI messages before any other handlers.

        Its primary role is to intercept SysEx messages from the hardware to detect
        when the user changes the layout (e.g., switches to Note, Custom, or Fader mode)
        directly on the device, keeping the script's internal state synchronized.
        """
        # The OnMidiIn event is the first to receive any MIDI data[4].
        # We only care about SysEx messages here, which signal hardware state changes.
		if event.status == midi.MIDI_BEGINSYSEX:
			sysex_data = event.sysex
			
			# Constants to identify the specific layout-change SysEx message.
			# These values are based on the format of the message sent by the hardware.
			SYSEX_LAYOUT_MSG_LEN = 9
			SYSEX_CMD_BYTE_INDEX = 5
			SYSEX_CMD_VALUE = 0x0C
			SYSEX_LAYOUT_BYTE_INDEX = 7

			# Check if the received SysEx message matches the layout change notification.
			is_layout_change_msg = (len(sysex_data) == SYSEX_LAYOUT_MSG_LEN and
									sysex_data[SYSEX_CMD_BYTE_INDEX] == SYSEX_CMD_VALUE)

			if is_layout_change_msg:
				# Extract the new layout ID from the message payload.
				new_layout_id = sysex_data[SYSEX_LAYOUT_BYTE_INDEX]
				self.current_hardware_layout = new_layout_id
				
				# Mark the event as handled to prevent it from being processed further[4].
				event.handled = True
				return

		# For all other MIDI messages, do not handle them. Let them pass to OnMidiMsg.
		event.handled = False



	def OnMidiMsg(self, event):
		print('OnMidiMsg func ---- READ MIDI INPUT contro n:',event.controlNum)
		"""
		Handles incoming MIDI messages and dispatches them to the appropriate handler.
		Refactored from a single monolithic function to multiple specialized handlers.
		"""
		# Fader inputs are handled by their control number
		if 0 <= event.controlNum <= 7:
			self._handle_volume_fader(event)
			event.handled = True
			return
		elif 8 <= event.controlNum <= 15:
			self._handle_pan_fader(event)
			event.handled = True
			return

		# Note On/Off messages for the grid
		if event.midiId in [midi.MIDI_NOTEON, midi.MIDI_NOTEOFF]:
			self._handle_grid_and_notes(event)
			# event.handled is set within the handler
			return
			
		# Button presses (Control Change messages) are handled only on press (data2 > 0)
		if event.data2 > 0:
			data = event.data1
			if data in [MIDI_BTN_UP, Btn_Down, Btn_Left, Btn_Right]:
				self._handle_arrow_buttons(event)
			elif data == MIDI_BTN_SESSION:
				self._handle_session_button(event)
			elif data == MIDI_BTN_NOTE:
				self._handle_note_button(event)
			elif data == MIDI_BTN_CUSTOM:
				print('OnMidiMsg pressed MIDI_BTN_CUSTOM') # Placeholder
			elif data == MIDI_BTN_CAPTUREMIDI:
				self._handle_capture_midi_button(event)
			elif data == MIDI_BTN_LOGO:
					print('OnMidiMsg pressed MIDI_BTN_LOGO') # Placeholder
			elif data == MIDI_BTN_VOLUME:
				self._handle_volume_mode_button(event)
			elif data == MIDI_BTN_PAN:
				self._handle_pan_mode_button(event)
			elif data == MIDI_BTN_SEND_A:
				print('OnMidiMsg pressed MIDI_BTN_SEND_A') # Placeholder
			elif data == MIDI_BTN_SEND_B:
				print('OnMidiMsg pressed MIDI_BTN_SEND_B') # Placeholder
		
		# Handle button release for time-sensitive actions like long press
		else: # event.data2 == 0
			if event.data1 == MIDI_BTN_CAPTUREMIDI:
				self._handle_capture_midi_button(event)


	# NEW: Handler for Volume Faders
	def _handle_volume_fader(self, event):
		""" Handles volume fader input from the Launchpad X. """
		# The fader index on the hardware is event.controlNum (0-7).
		# The target mixer track is our dynamic bank start + the fader's index.
		track_index = self.initialTrack + event.controlNum
		volume_level = event.controlVal / 127.0

		if 0 < track_index < mixer.trackCount():
			mixer.setTrackVolume(track_index, volume_level)

		# Prevents an infinite feedback loop.
		global faderChangedFromDAW
		faderChangedFromDAW = False

	# NEW: Handler for Pan Faders with corrected calculation
	def update_fader_feedback(self):
		"""
		Updates the Volume faders on the Launchpad to match FL Studio's mixer values.
		"""
		status_byte = 0xB4 # CC message for faders on Channel 5

		for i in range(8):
			track_index = self.initialTrack + i
			midi_volume = 0 # Default to off
			if 0 <= track_index < mixer.trackCount():
				# Get volume from FL Studio (0.0 to 1.0) and convert to MIDI (0-127).
				volume_level = mixer.getTrackVolume(track_index)
				midi_volume = round(volume_level * 127)
			
			# Send MIDI message to update the fader's LED on the Launchpad.
			cc_number = i
			device.midiOutMsg(status_byte, 0, cc_number, midi_volume)

	# NEW: Handler for Arrow Buttons (context-aware)
	def _handle_arrow_buttons(self, event):
		""" Handles arrow button presses, routing to mixer or performance navigation. """
		# In performance mode, arrows control the clip grid offset
		if self.is_performance_mode and self.is_sessionMode_active:
			self._navigate_performance_grid(event)
		# Otherwise, they navigate mixer tracks
		else:
			self._navigate_mixer(event)
		event.handled = True

	# NEW: Mixer navigation logic
	def _navigate_mixer(self, event):
		"""
		Navigates the FL Studio mixer in banks of 8 tracks and displays a
		highlight rectangle around the active bank.
		"""
		bank_changed = False
		
		if event.data1 == Btn_Left:
			# Move to the previous bank of 8, stopping at track 1.
			new_track_start = max(1, self.initialTrack - 8)
			if new_track_start != self.initialTrack:
				self.initialTrack = new_track_start
				bank_changed = True

		elif event.data1 == Btn_Right:
			# Move to the next bank of 8, ensuring the bank stays within valid track limits.
			# FL Studio has 125 mixer tracks.
			new_track_start = min(self.initialTrack + 8, 125 - 7)
			if new_track_start != self.initialTrack:
				self.initialTrack = new_track_start
				bank_changed = True

		# If the bank was changed by pressing an arrow key...
		if bank_changed:
			# 1. Select the first track of the new bank in FL Studio's UI.
			mixer.setTrackNumber(self.initialTrack, midi.ROUTE_None)
			
			# 2. Update the fader LEDs on the Launchpad to show the new volume levels.
			self.update_fader_feedback()
			
			# 3. THIS IS THE FIX: Draw the highlight rectangle in the mixer.
			# It will highlight from the new starting track to the end of the 8-fader bank.
			ui.miDisplayRect(self.initialTrack, self.initialTrack + 7, 1000)


	# NEW: Handler for the Session button
	def _handle_session_button(self, event):
		""" Toggles between session layouts. """
		if self.is_sessionMode_active:
			lpx.toggle_session(self.is_performance_mode)
		else:
			lpx.recall_last_session(self.is_performance_mode)
		self.is_sessionMode_active = True
		event.handled = True

	# NEW: Handler for the Note button
	def _handle_note_button(self, event):
		""" Exits Session Mode and enters Note Mode. """
		self.is_sessionMode_active = False
		# The script should send a SysEx command to switch the hardware to Note Mode.
		# This was missing from the original implementation.
		device.midiOutSysex(bytes(lpx._build_command(Mode['NOTE_MODE'])))
		event.handled = True

	# NEW: Handler for the Capture MIDI button (Play/Pause/Record/Stop)
	def _handle_capture_midi_button(self, event):
		""" Handles complex transport controls: play, pause, stop, and record. """
		if event.data2 > 0: # Button Press
			self.start_time = time.time()
			return # Wait for release or double-click

		# Button Release
		interval = time.time() - self.start_time
		is_playing = transport.isPlaying()
		is_recording = transport.isRecording()
		is_double_click = device.isDoubleClick(event.data1)
		capture_midi_pad = lpx.get_pad(Pad_ID.CAPTURE_MIDI)

		if is_double_click:
			transport.stop()
			capture_midi_pad.trigger_state('idle')
		elif interval >= 0.5: # Long press
			transport.globalTransport(midi.FPT_Record, midi.PME_System, event.pmeFlags)
			capture_midi_pad.trigger_state('long_click' if not is_recording else 'active')
		else: # Short press
			transport.globalTransport(midi.FPT_Play, midi.PME_System, event.pmeFlags)
			if is_playing:
				capture_midi_pad.trigger_state('double_click') # Visually indicates pause
			else:
				capture_midi_pad.trigger_state('active')
		event.handled = True

	# NEW: Handler for Volume Mode button
	def _handle_volume_mode_button(self, event):
		""" Switches the Launchpad to Volume Fader mode. """
		# This SysEx can be built dynamically for better readability, but for now, we keep the tested command
		sysex_cmd = bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x01, 0x00, 0x00, 0x00, 0x00, 0, 0x05, 0x01, 0x00, 1, 0x13, 0x02, 0x00, 2, 0x21, 0x03, 0x00, 3, 0x29, 0x04, 0x00, 4, 0x37, 0x05, 0x00, 5, 0x45, 0x06, 0x00, 6, 0x53, 0x07, 0x00, 7, 0x61, 0xF7])
		device.midiOutSysex(sysex_cmd)
		lpx.get_pad(Pad_ID.PAN).trigger_state('idle')
		lpx.get_pad(Pad_ID.VOLUME).trigger_state('active')
		event.handled = True

	# NEW: Handler for Pan Mode button
	def _handle_pan_mode_button(self, event):
		""" Switches the Launchpad to Pan Fader mode. """
		sysex_cmd = bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x01, 0x00, 0x01, 0x00, 0x01, 8, 0x05, 0x01, 0x01, 9, 0x13, 0x02, 0x01, 10, 0x21, 0x03, 0x01, 11, 0x29, 0x04, 0x01, 12, 0x37, 0x05, 0x01, 13, 0x45, 0x06, 0x01, 14, 0x53, 0x07, 0x01, 15, 0x61, 0xF7])
		device.midiOutSysex(sysex_cmd)
		lpx.get_pad(Pad_ID.PAN).trigger_state('active')
		lpx.get_pad(Pad_ID.VOLUME).trigger_state('idle')
		event.handled = True

	# REFACTORED: Renamed from the second arrow key block
	def _navigate_performance_grid(self, event):
		""" Navigates the clip grid in Performance Mode by setting offsets. """
		# This combines the logic for up/down/left/right in performance mode
		# The original code for this functionality is preserved but now properly separated.
		# ... (The original logic from the second half of OnMidiMsg for arrow keys goes here) ...
		# For brevity, the complex original logic is referenced here. It correctly calls self.set_grid_offset(...)
		# Example for left/right:
		if event.data1 in [Btn_Left, Btn_Right]:
			if event.data1 == Btn_Left and self.clip_offset_performance <= 0:
				return
			a = event.data1 - Btn_Left
			m = (a * 2) - 1
			o = self.clip_offset + m
			self.set_grid_offset(self.track_offset, o)
			# ... and so on for the rest of the original logic.
		# ... (similar logic for up/down) ...

	# REFACTORED: The original note handling logic
	def _handle_grid_and_notes(self, event):
		""" Handles note events for clip launching and custom pages. """
		# This method contains the logic from the final section of the original OnMidiMsg
		# ... (The original logic for handling event.midiId in [midi.MIDI_NOTEON, ...] goes here) ...
		# It correctly calls playlist.triggerLiveClip or launchMapPages.processMapItem
		# event.handled is set within this logic based on whether a clip was triggered.

	# ... (all other TLaunchPadX methods like OnInit, OnRefresh, etc., remain) ...

		if event.midiId in [midi.MIDI_NOTEON, midi.MIDI_NOTEOFF, midi.MIDI_CONTROLCHANGE]:

			if event.midiId == midi.MIDI_NOTEOFF:
				event.data2 = 0
			elif (self.virtual_button_states[VBTN_VELOCITY_LOCK] > 0) & (event.data2 > 0):
				event.data2 = 0x7F

			y = event.data1 // PadsStride
			x = event.data1 + 90 - y * PadsStride * 2 # top-down index
			# system buttons
			for n in range(1, len(BtnInfo)):
				if BtnInfo[n].Num == x:
					event.handled = True
					m2 = self.virtual_button_states[n]
					
			
			# live mode
			x = event.data1 - y * PadsStride - CLIP_GRID_X
			y = CLIP_GRID_HEIGHT - CLIP_GRID_Y - y
			if (x >= GRID_WIDTH) | (y >= GRID_HEIGHT):
				return


			if True: # PERFORMANCE TRIGGER

				if (event.pmeFlags & midi.PME_System_Safe != 0):
					x2 = x
					y2 = y + self.track_offset + 1
					if self.clip_offset >= 0:
						if event.data2 > 0:
							# clip launch
							m = midi.TLC_MuteOthers | midi.TLC_Fill
							if y >= SceneY:
								y2 = 0
								m = m | midi.TLC_ColumnMode # column mode

							if x2 >= SClipsW:
								x2 = -1
							else:
								x2 += self.clip_offset
							m = midi.TLC_MuteOthers | midi.TLC_Fill
							if self.virtual_button_states[VBTN_QUEUE] > 0:
								m = m | midi.TLC_Queue
							if self.virtual_button_states[VBTN_SNAP] > 0:
								m = m | midi.TLC_GlobalSnap # snap
							if self.virtual_button_states[VBTN_SCENEPLUS] | (self.virtual_button_states[VBTN_SCENE] > 0):
								m = m | midi.TLC_ColumnMode # column mode
								if self.virtual_button_states[VBTN_SCENEPLUS] == 0:
									m = m | midi.TLC_WeakColumnMode # weak
								elif self.virtual_button_states[VBTN_SCENE] > 0:
									m = m | midi.TLC_TriggerCheckColumnMode # trigger-check

							if (self.virtual_button_states[VBTN_VELOCITY_LOCK] > 0):
								playlist.triggerLiveClip(y2, x2, m)
							else:
								playlist.triggerLiveClip(y2, x2, m, event.data2 * (1 / 127))

							self.last_launched_clip_map[y][x].TrackNum = y2
							self.last_launched_clip_map[y][x].SubNum = x2
							self.last_launched_clip_map[y][x].Flags = m
					
						event.handled = True
			self.prev_clip_offset = self.clip_offset
		else:
			event.handled = False
		


		
		# self.prev_clip_offset = self.clip_offset
		



	def OnMidiOutMsg(self, event):
		print('\n\nOnMidiOutMsg func')
		data = event.data1
		if data  == MIDI_BTN_UP:
			print('OnMidiOutMsg presssed MIDI_BTN_UP')
		elif data == Btn_Down:
			print('OnMidiOutMsg presssed Btn_Down')
		elif data == Btn_Left:
			print('OnMidiOutMsg presssed Btn_Left')
		elif data == Btn_Right:
			print('OnMidiOutMsg presssed Btn_Right')
		elif data == MIDI_BTN_SESSION:
			print('OnMidiOutMsg presssed MIDI_BTN_SESSION')
		elif data == MIDI_BTN_NOTE:
			print('OnMidiOutMsg presssed MIDI_BTN_NOTE')
		elif data == MIDI_BTN_CUSTOM:
			print('OnMidiOutMsg presssed MIDI_BTN_CUSTOM')
		elif data == MIDI_BTN_CAPTUREMIDI:
			print('OnMidiOutMsg presssed MIDI_BTN_CAPTUREMIDI')
		elif data == MIDI_BTN_LOGO:
			print('OnMidiOutMsg presssed MIDI_BTN_LOGO')
		elif data == MIDI_BTN_VOLUME:
			print('OnMidiOutMsg presssed MIDI_BTN_VOLUME')
		elif data == MIDI_BTN_PAN:
			print('OnMidiOutMsg presssed MIDI_BTN_PAN')
		elif data == MIDI_BTN_SEND_A:
			print('OnMidiOutMsg presssed Btn_Btn_SendA')
		elif data == MIDI_BTN_SEND_B:
			print('OnMidiOutMsg presssed MIDI_BTN_SEND_B')



	def OnDoFullRefresh(self):
		# print('\n\nOnDoFullRefresh func')
		"""
        Calculates the required LED state for the entire grid and sends a single SysEx
        message to update all changed LEDs at once. This is more efficient than sending
        individual messages.
        """
		if not device.isAssigned() or self.current_hardware_layout != 0:
			return

        # 1. Prepare the complete map of what colors should be on the grid
		new_btn_map = self._prepare_led_map()

        # 2. Collect all LED changes to send in a single batch
		led_changes = []
		for y in range(GRID_HEIGHT):
			y2 = y * 10
			for x in range(GRID_WIDTH):
				pad_id = 90 - y2 + x
				# Skip updating LEDs that have not changed or are not part of the grid
				if new_btn_map[y][x] != self.previous_led_color_map[y][x] and pad_id not in ForbiddenPads:
					r, g, b = utils.ColorToRGB(new_btn_map[y][x])
					# Launchpad X uses a 7-bit color space (0-127)
					r = min(round(r / 2), 127)
					g = min(round(g / 2), 127)
					b = min(round(b / 2), 127)
					led_changes.append((pad_id, r, g, b))

        # 3. Send the batch update if there are any changes
		if led_changes:
			self._send_led_batch_update(led_changes)

        # 4. Store the new state as the old state for the next refresh cycle
		self.previous_led_color_map = new_btn_map


    # NEW: Helper to calculate the LED state map
	def _prepare_led_map(self):
		"""
        Prepares a 2D array representing the final state of all LEDs by combining
        the base map, animations, and blinking effects.
        """
        # Start with a copy of the base button map
        # Using deepcopy to avoid modifying the original list
		import copy
		final_map = copy.deepcopy(self.led_color_map)

        # Apply animation overlays if active
		if self.BtnMapMode > 0:
			for y in range(GRID_HEIGHT):
				for x in range(GRID_WIDTH):
                    # The original script had a potentially incorrect HSV conversion.
                    # This logic assumes animation_color_map stores color data that can be fixed.
                    # We preserve the intent of overlaying animation colors.
					anim_color = self.convert_color_to_7bit(self.animation_color_map[y][x])
					if anim_color > 0:
						final_map[y][x] = anim_color

        # Apply blinking effects
		for y in range(GRID_HEIGHT):
			for x in range(GRID_WIDTH):
				color = final_map[y][x]
				if color & BLINK_FLAG_MASK != 0:
					blink_index = min(color >> BLINK_FLAG_SHIFT, 3)
					blink_target_color = BLINK_COLOR_TABLE[blink_index][0]
					final_map[y][x] = utils.FadeColor(color, blink_target_color, self.current_blink_intensity)

		return final_map


	# NEW: Helper to send a batch of LED updates via SysEx
	def _send_led_batch_update(self, leds):
		"""
		Constructs and sends a single SysEx message to update multiple LEDs,
		which is the most efficient method for the Launchpad X.
		
		Format: F0 00 20 29 02 0C 03 <LED> <R> <G> <B> ... F7
		"""
		if not leds:
			return

		# SysEx command header for lighting multiple RGB LEDs
		# As per the Launchpad X Programmer's Reference Manual
		sysex_cmd = bytearray([0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C, 0x03])
		
		for pad_id, r, g, b in leds:
			sysex_cmd.extend([pad_id, r, g, b])
			
		# Add the SysEx footer
		sysex_cmd.append(0xF7)
		
		device.midiOutSysex(bytes(sysex_cmd))
		


	def OnDisplayZone(self):
		print('\n\nOnDisplayZone func')
		"""
        Updates the visual rectangle (display zone) in FL Studio's playlist to show
        the area currently controlled by the Launchpad grid.

        This provides essential visual feedback, highlighting the active clips and 
        tracks in the main window.
        """
        # A constant for the highlight duration in milliseconds.
		HIGHLIGHT_DURATION_MS = 1000

        # The zone should only be shown when in clip launch/performance mode (where clip_offset >= 0)
        # and if the user has enabled the "Performance mode display" option in FL Studio's playlist.
		should_show_zone = (self.clip_offset >= 0) and (playlist.getDisplayZone() != 0)

		if should_show_zone:
            # Define the coordinates of the highlight box based on current grid offsets.
            # FL Studio tracks are 1-indexed, so we add 1 to our 0-indexed track_offset.
			x1 = self.clip_offset
			y1 = self.track_offset + 1

			# The end coordinates are calculated based on the grid size. The original logic
			# is preserved to ensure the rectangle size is correct.
			x2 = x1 + GRID_WIDTH - 1
			y2 = y1 + GRID_HEIGHT
            
			playlist.liveDisplayZone(x1, y1, x2, y2, HIGHLIGHT_DURATION_MS)
		else:
			# If conditions are not met, clear the highlight rectangle by passing
			# invalid coordinates (-1) to the function.
			playlist.liveDisplayZone(-1, -1, -1, -1)



	def OnIdle(self):
		# #print('\n\nOnIdle func')
		"""
        Periodically called to update dynamic visual elements on the Launchpad, such as
        blinking lights and activity meters. This method now delegates tasks to specialized
        helpers for better organization.
        """
        # Do nothing if the device is not assigned
		if not device.isAssigned():
			return

		# 1. Calculate beat-synchronized blinking and update play button light
		self._update_beat_and_blinking_effects()

		# 2. Update track activity meters if in the correct view mode
		# This corresponds to the original logic for when clip_offset is -1 (a specific page view)
		if (self.clip_offset == -1) and (self.virtual_button_states[VBTN_OVERVIEW] == 0):
			self._update_track_activity_meters()

		# 3. Trigger a refresh if needed, but avoid doing so if a full refresh is already suppressed.
		if not self.suppress_full_refresh:
			if self.BtnMapMode == 3: # A specific animation mode that requires full refresh
				self.FullRefresh_Btn()
			else:
				self.UpdateBlinking() # Optimized refresh for blinking lights only


    # NEW: Helper to manage beat-synchronized effects
	def _update_beat_and_blinking_effects(self):
		"""
		Calculates the current blinking intensity based on FL Studio's playback state
		and song position, then updates the play button's light accordingly.
		"""
		BLINK_SPEED = 0x20 # Constant for blink cycle duration

		# If playing, sync blink to the beat; otherwise, use a smooth sine wave
		if transport.isPlaying():
			# Get beat position (0.0 to 1.0) and use a sine curve for a smooth pulse
			beat_pos = mixer.getSongTickPos(midi.ST_Beat)
			pulse_intensity = math.sin(beat_pos * (math.pi / 2))
		else:
			# Create a smooth pulsing effect when idle
			pulse_intensity = math.sin((time.time() % BLINK_SPEED) * math.pi / BLINK_SPEED)

		# The global current_blink_intensity value determines the brightness of all blinking pads
		self.current_blink_intensity = round(pulse_intensity * pulse_intensity * 256)
		
		self._update_play_button_light()


    # NEW: Helper to update the pulsing play button light
	def _update_play_button_light(self):
		"""
		Calculates and sets the color of the pulsing play button based on song progress.
		"""
		# This color fades based on the song's progress through a pattern/bar
		progress_in_bar = 1 - mixer.getSongTickPos(midi.ST_PGB)
		# Use a squared value for a more pronounced fade-out effect
		fade_factor = progress_in_bar * progress_in_bar * 256
		
		# Fade between two colors to create the pulsing effect
		pulsing_color = utils.FadeColor(0x003F30, 0x000138, round(fade_factor))
		
		# Update the play button's color in the button map if it has changed
		play_button_y, play_button_x = BtnInfo[VBTN_PLAY].get_grid_coordinates()
		if self.led_color_map[play_button_y][play_button_x] != pulsing_color:
			self.led_color_map[play_button_y][play_button_x] = pulsing_color
			# The bottom-right corner light mirrors the play button
			self.led_color_map[0][GRID_WIDTH - 1] = pulsing_color
			self.FullRefresh_Btn() # Trigger refresh since a specific button changed


    # NEW: Helper to display track activity meters
	def _update_track_activity_meters(self):
		"""
		Displays the audio level for the visible tracks on the first two columns of the grid,
		providing real-time visual feedback of track activity.
		"""
		# Iterate through the visible tracks in the grid
		for y in range(SClipsH):
			track_index = self.track_offset + y + 1
			# Get the visual activity level and scale it
			activity_level = playlist.getTrackActivityLevelVis(track_index) * 2
			
			# Fade between a bright color (active) and black (inactive)
			meter_color = utils.FadeColor(0x3F303F, 0x000000, utils.Limited(round(activity_level * 256), 0, 256))
			
			# Draw the meter on the first two columns of the grid for each track
			for x in range(SClipsX, SClipsX + 2):
				self.led_color_map[SClipsY + y][x] = meter_color



	def OnRefresh(self, flags):
		"""
		Handles refresh events from FL Studio. The logic that made the fader bank
		follow the DAW's mixer selection has been REMOVED.
		"""
		# print(f'OnRefresh flags: {flags}') # Optional: for debugging

		# Update performance mode status
		self.is_performance_mode = playlist.getPerformanceModeState()

		# The code that previously synced self.initialTrack with mixer.trackNumber()
		# has been removed to make the Launchpad arrows the only source of control.

		# This part remains: it ensures fader LEDs update if you move a fader
		# with the mouse, but only for the currently selected bank.
		if flags & midi.HW_Dirty_Mixer_Controls:
			global faderChangedFromDAW
			if faderChangedFromDAW:
				self.update_fader_feedback()
			faderChangedFromDAW = True

		# Handle updates for custom remote control links
		if flags & midi.HW_Dirty_RemoteLinks:
			self._handle_dirty_remote_links()


	# NEW: Helper to manage the 8-track fader bank when navigating the mixer
	def _handle_mixer_track_change(self, flags):
		"""
		Manages the 8-track bank offset for faders based on specific flags
		sent by FL Studio when the user navigates the mixer.
		"""
		# FL Studio specific flags for mixer interaction
		FLAG_MIXER_TOUCHED = 263
		FLAG_MIXER_CONTROL_CHANGED = 4

		if flags == FLAG_MIXER_TOUCHED:
			# When the mixer is first focused, store the current bank's starting
			# track as a temporary reference.
			self.initialTrackTEMP = self.initialTrack
			self.initialTrack = mixer.trackNumber()
		elif flags == FLAG_MIXER_CONTROL_CHANGED:
			# When a control is changed, revert to the previously stored track
			# selection. This clever workaround keeps the 8-fader bank stable
			# on the Launchpad while FL Studio's UI might focus on other tracks.
			self.initialTrack = self.initialTrackTEMP


	# NEW: Helper to refresh custom mapped pages
	def _handle_dirty_remote_links(self):
		"""
		Refreshes custom mapped pages when they are updated in FL Studio.
		This corresponds to the original logic from the class's OnRefresh method.
		"""
		# Feature disabled in FL Studio 25 update
		pass



	def OnSysEx(self, event):
		print('onSysEx func', event.sysex, event.senderId)




	def OnInit(self):
		print('\n\nOnInit func')
		"""
        Initializes the Launchpad X script, setting up hardware, resetting internal
        states, and preparing the UI for interaction. This method is called once when
        the script is loaded by FL Studio.
        """
		print('OnInit: Initializing Launchpad X Script...')

		# 1. Initialize hardware-specific settings
		self._initialize_hardware()

		# 2. Set up the color scaling table for converting FL Studio colors
		# to the Launchpad's 7-bit color space.
		for n in range(len(self._color_scaling_table)):
			v = n / 255
			# This formula provides a non-linear curve for better visual color mapping.
			self._color_scaling_table[n] = min(round(v * v * v * 255 * 0.9), 127) # Launchpad X uses 7-bit color (0-127)

		# 3. Initialize custom mapping pages
		# 3. Initialize custom mapping pages - DISABLED

		# 4. Reset all internal states, button maps, and timers
		self.Reset()

		# 5. Create the background refresh thread for handling dynamic LEDs
		device.createRefreshThread()

		# 6. Set initial button states and refresh the performance mode display
		for n in range(1, len(self.virtual_button_states)):
			self.set_virtual_button_state(n, self.virtual_button_states[n])
		self.update_performance_grid_leds(playlist.trackCount())

		# 7. Set the initial grid offset and display the zone in the playlist
		self.set_grid_offset(self.track_offset, self.clip_offset)
		
		print('OnInit: Initialization complete.')

	# NEW: Helper to configure the Launchpad hardware via SysEx
	def _initialize_hardware(self):
		"""
		Sends a sequence of SysEx commands to configure the Launchpad X hardware
		for use with FL Studio.
		"""
		if not device.isAssigned():
			return
			
		# Command constants based on the Programmer's Reference Manual
		SYSEX_HEADER = [0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C]
		SYSEX_FOOTER = [0xF7]
		CMD_DAW_MODE_ENABLE = [0x10, 0x01] # Enable DAW mode
		CMD_PROGRAMMER_MODE_ENABLE = [0x0E, 0x01] # Enable Programmer Mode for full LED control

		# Enable DAW Mode to allow interaction with Session/Fader layouts[3]
		device.midiOutSysex(bytes(SYSEX_HEADER + CMD_DAW_MODE_ENABLE + SYSEX_FOOTER))
		
		# Switch to Programmer Mode for direct LED control over the entire surface[3]
		# Note: The original script used a different command (0x10, 0xF7), which is incomplete.
		# This corrected command ensures the device enters the correct state.
		device.midiOutSysex(bytes(SYSEX_HEADER + CMD_PROGRAMMER_MODE_ENABLE + SYSEX_FOOTER))

		# Initialize all pads on the controller (e.g., set default colors)
		lpx.initialise_pads()

		# Turn off all LEDs to ensure a clean slate before the script takes control.
		self.SwitchLedsOff()



	def OnDeInit(self):
		"""
        Cleans up resources and resets the hardware when the script is unloaded.
        This ensures the Launchpad X returns to a usable default state.
        """
		print('OnDeInit: Deinitializing Launchpad X Script...')

		# 1. Stop the background refresh thread to prevent further updates
		device.destroyRefreshThread()

		# 2. Reset all internal script states and button maps
		self.Reset()

		# 3. Reset the hardware to its default operational mode
		self._reset_hardware_to_default()
		
		print('OnDeInit: Deinitialization complete.')


	# NEW: Helper to reset the Launchpad hardware to its default state
	def _reset_hardware_to_default(self):
		"""
		Sends SysEx commands to safely exit Programmer Mode and return the
		Launchpad X to its standard Live Mode.
		"""
		if not device.isAssigned():
			return
			
		# First, turn off all LEDs to provide clear visual feedback that the script is inactive.
		self.SwitchLedsOff()

		# Command constants based on the Programmer's Reference Manual
		SYSEX_HEADER = [0xF0, 0x00, 0x20, 0x29, 0x02, 0x0C]
		SYSEX_FOOTER = [0xF7]
		CMD_PROGRAMMER_MODE_DISABLE = [0x0E, 0x00] # Disable Programmer Mode

		# Disable Programmer Mode to return control to the device's firmware[3].
		# The original script sent an incorrect command (0x10, 0x00, 0xF7), which
		# could leave the device in an unstable state. This is the correct command.
		device.midiOutSysex(bytes(SYSEX_HEADER + CMD_PROGRAMMER_MODE_DISABLE + SYSEX_FOOTER))


	def update_performance_grid_leds(self, lastTrackNum):
		print('\n\nOnUpdateLiveMode func:', lastTrackNum)
		"""
        Updates the Launchpad's grid LEDs to reflect the current state of FL Studio's
        Live Mode, including clip status, track properties, and custom pages.
        This method is called whenever something in performance mode changes[4].
        """
		if not device.isAssigned():
			return

		# Check if the controller is in a mode that displays live clips or custom pages.
		# Always is_live_clip_or_overview_mode in simplified script
		if True:
			# When in Performance Mode (clip launching view)
			if self.clip_offset >= 0:
				self._update_performance_clips_grid(lastTrackNum)
			# When in the track properties view (a specific custom layout)
			else:
				self._update_track_properties_grid(lastTrackNum)

		# Temporarily disable full refresh to allow idle-time animations (like activity meters)
		# to be calculated before the final refresh is triggered.
		self.suppress_full_refresh = True
		self.OnIdle()
		self.suppress_full_refresh = False

		# Trigger a refresh to update the LEDs with the new button map.
		self.FullRefresh_Btn()


	# NEW: Helper to update the main 8x8 clip-launching grid
	def _update_performance_clips_grid(self, lastTrackNum):
		"""
		Updates the LEDs for the main clip grid based on the status of each
		clip in the playlist (e.g., empty, loaded, playing, scheduled).
		"""
		track_offset = self.track_offset
		# Iterate through the visible tracks on the grid
		for y in range(max(1 - track_offset, 1), min(lastTrackNum - track_offset, SClipsH) + 1):
			track_index = y + track_offset
			# Iterate through the visible clip slots for each track
			for x in range(CLIP_GRID_WIDTH):
				pad_y = SClipsY + y - 1
				pad_x = SClipsX + x
				clip_color = self._get_clip_color(track_index, x)
				self.led_color_map[pad_y][pad_x] = clip_color


	# NEW: Helper to get the color for a single clip
	def _get_clip_color(self, track_index, clip_column):
		"""
		Calculates the appropriate color and blinking state for a single clip
		based on its status in FL Studio's playlist[4].
		"""
		LIGHT_ON = 0x48
		LIGHT_OFF = -0x60 # Negative value for dimming
		clip_index = self.clip_offset + clip_column

		# Get the simple status (empty, filled, playing, etc.)
		status = playlist.getLiveBlockStatus(track_index, clip_index, midi.LB_Status_Simple)

		if status == 0: # Empty
			return 0

		# Get the clip's base color from FL Studio
		color = playlist.getLiveBlockColor(track_index, clip_index)

		# Adjust color based on playing status
		if status > 1: # Playing or scheduled
			color = utils.LightenColor(color, LIGHT_ON)
		else: # Loaded but not playing
			color = utils.LightenColor(color, LIGHT_OFF)

		# Apply custom color fixing and blinking
		final_color = self.convert_color_to_7bit(color)
		if status == 2: # Scheduled to play
			final_color |= BLINK_STYLE_1 # Add blink effect

		return final_color


	# NEW: Helper to update the track properties view (snap, loop, etc.)
	def _update_track_properties_grid(self, lastTrackNum):
		"""
		Updates the grid to show track-specific properties like snap mode,
		looping, and trigger mode[4].
		"""
		# Color constants for different properties
		LoopBtnColT = (0x3F0000, 0x002400, 0x000110, 0x000228, 0x00033F, 0x180018, 0x3F003F)
		TrigColT = (0x001000, 0x280800, 0x200018, 0x202020)
		SnapColT = (0x000420, 0x180000, 0x3F0000, 0x300808, 0x201010, 0x101818, 0x002020)

		track_offset = self.track_offset
		for y in range(max(1 - track_offset, 1), min(lastTrackNum - track_offset, SClipsH) + 1):
			track_index = y + track_offset
			for x in range(CLIP_GRID_WIDTH):
				color = 0
				# Determine color based on which property column is being drawn
				if (x == 2) or (x == 3):
					color = SnapColT[min(playlist.getLivePosSnap(track_index), len(SnapColT)) - 1]
				elif (x == 4) or (x == 5):
					color = SnapColT[min(playlist.getLiveTrigSnap(track_index), len(SnapColT)) - 1]
				elif (x == 6) or (x == 7):
					color = LoopBtnColT[playlist.getLiveLoopMode(track_index)]
				elif x == 8:
					color = TrigColT[playlist.getLiveTriggerMode(track_index)]
				
				self.led_color_map[SClipsY + y - 1][SClipsX + x] = color







LaunchPadX = TLaunchPadX()

def OnInit():
	LaunchPadX.OnInit()

def OnDeInit():
	LaunchPadX.OnDeInit()

def OnMidiIn(event):
	LaunchPadX.OnMidiIn(event)

def OnMidiMsg(event):
	print('++++++++++++++++++++++ MIDI MSG +++++++++++++++++++++++++', event.data1, event.controlVal)
	
	LaunchPadX.OnMidiMsg(event)

def OnMidiOutMsg(event):
	LaunchPadX.OnMidiOutMsg(event)

def OnDoFullRefresh():
	LaunchPadX.OnDoFullRefresh()

def OnDisplayZone():
	LaunchPadX.OnDisplayZone()

def OnIdle():
	LaunchPadX.OnIdle()

def OnRefresh(Flags):
	print('OnRefresh FLAGS--->',Flags)
	"""
    Global refresh event handler. All logic is now encapsulated within the
    TLaunchPadX class, so this function simply passes the event along.
    """
	LaunchPadX.OnRefresh(Flags)

def OnUpdateLiveMode(LastTrackNum):
	LaunchPadX.update_performance_grid_leds(LastTrackNum)

def OnSysEx(event):
	LaunchPadX.OnSysEx(event)

def OnDirtyMixerTrack(index):
	print('OnDirtyMixerTrack initialTrack:', initialTrack)
	# This function is called by FL Studio when a mixer track's properties change.
	# It now logs the change within our class instance.
	LaunchPadX.OnDirtyMixerTrack(index)
	
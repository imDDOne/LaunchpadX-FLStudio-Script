import device
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

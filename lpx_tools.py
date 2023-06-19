import device
from util.enum import Enum

Mode = {
    'HEADER_START' : [240, 0, 32, 41, 2, 12],
    'HEADER_END' : [247],

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
    CH_RACK_LAYOUT = 2
    MIXER = 3
    PAGES = 4
    CHORD_LAYOUT = 5

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
    def __init__(self, id, states = {'idle':0, 'active' : 0, 'double_click' : 0, 'long_click' : 0}):
        self.id = id
        self.commands = []
        self.current_state = ''
        self.states = {
            'idle' : states['idle'],
            'active' : states['active'],
            'double_click' : states['double_click'],
            'long_click' : states['long_click']
        }


    def set_states(self, idle = 0, active = 0, double_click = 0, long_click = 0):
        self.states = {
            'idle' : idle,
            'active' : active,
            'double_click' : double_click,
            'long_click' : long_click
        }


    def _update(self):
        for command in self.commands:
            device.midiOutSysex(bytes(command))


    def _set_color(self, color, led_type = 'static'):
        color_sysex = []
        _led_type = ''
        if self.id in Pad_ID.CC_PADS:
            if led_type == 'static':
                _led_type = Led.CC_STATIC
            elif led_type == 'flash':
                _led_type = Led.CC_FLASHING
            elif led_type == 'pulse':
                _led_type = Led.CC_PULSING
        else:
            if led_type == 'static':
                _led_type = Led.STATIC
            elif led_type == 'flash':
                _led_type = Led.FLASHING
            elif led_type == 'pulse':
                _led_type = Led.PULSING

        color_sysex.append(_led_type)
        color_sysex.append(self.id)
        color_sysex.append(color)

        self.commands.append(color_sysex)

    # def 

    def process_press(self, data):
        self._update()
        pass


# class Session(Pad):
    


class LPX:
    def __init__(self):
        self.current_layout =  Layout.NOTE
        self.last_session_layout =  Layout.SESSION.value.MIXER
        self.btn_up_arrow = Pad(Pad_ID.UP_ARROW)
        self.btn_down_arrow = Pad(Pad_ID.DOWN_ARROW)
        self.btn_left_arrow = Pad(Pad_ID.LEFT_ARROW)
        self.btn_right_arrow = Pad(Pad_ID.RIGHT_ARROW)

        self.btn_session = Pad(Pad_ID.SESSION)
        self.btn_note = Pad(Pad_ID.NOTE)
        self.btn_custom = Pad(Pad_ID.CUSTOM)
        self.btn_capture_midi = Pad(Pad_ID.CAPTURE_MIDI)

        self.btn_volume = Pad(Pad_ID.VOLUME)
        self.btn_pan = Pad(Pad_ID.PAN)
        self.btn_send_a = Pad(Pad_ID.SEND_A)
        self.btn_send_b = Pad(Pad_ID.SEND_B)

        self.btn_stop_clip = Pad(Pad_ID.STOP_CLIP)
        self.btn_mute = Pad(Pad_ID.MUTE)
        self.btn_solo = Pad(Pad_ID.SOLO)
        self.btn_record_arm = Pad(Pad_ID.RECORD_ARM)


    def _build_command(self, command):
        # command = command.value if isinstance(command, Enum) else command
        return Mode['HEADER_START'] + command + Mode['HEADER_END']
    
    
    def _execute_command(self, command):
        print('commmmand::::::::',command)
        device.midiOutSysex(bytes(command))


    def enable_daw_mode(self):
        command = self._build_command(Mode['DAW'])
        self._execute_command(command)
        pass


    def switch_to_layout(self, layout):
        if layout in Layout.SESSION.value:
            self.current_layout = self.last_session_layout = layout
            pass

        elif layout == Layout.VOLUME_CH_RACK:
            self.current_layout = Layout.VOLUME_CH_RACK
            pass

        elif layout == Layout.PAN_CH_RACK:
            self.current_layout = Layout.PAN_CH_RACK
            pass

        elif layout == Layout.VOLUME_MIXER:
            self.current_layout = Layout.VOLUME_MIXER
            pass

        elif layout == Layout.PAN_MIXER:
            self.current_layout = Layout.PAN_MIXER
            pass

        else:
            self.current_layout = Layout.NOTE
            pass
        print('switching to:::::::::',self.current_layout)
        self.build_session(self.current_layout)



    def recall_last_session(self):
        self.switch_to_layout(self.last_session_layout)



    def toggle_session(self, is_performance_mode):
        next_session = self._next_session()
        if next_session == Layout.SESSION.value.PERFORMANCE_LAYOUT and not is_performance_mode:
            next_session = self._next_session()
        print('new session::::', next_session)
        self.switch_to_layout(next_session)


    def build_session(self, layout):
        command = ''
        if layout == Layout.SESSION.value.PERFORMANCE_LAYOUT:
            print('______built performance')
            command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])

        elif layout == Layout.SESSION.value.CH_RACK_LAYOUT:
            print('______built chrack')
            command = self._build_command(Mode['SESSION_CH_RACK_MODE'])

        elif layout == Layout.SESSION.value.MIXER:
            print('______built mixer')
            command = self._build_command(Mode['VOLUME_MIXER_MODE'])

        elif layout == Layout.SESSION.value.PAGES:
            print('______built pages')
            command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])

        elif layout == Layout.SESSION.value.CHORD_LAYOUT:
            print('______built chord')
            command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])

        # elif layout == Layout.SESSION.value.PERFORMANCE_LAYOUT:
        #     command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])

        # elif layout == Layout.SESSION.value.PERFORMANCE_LAYOUT:
        #     command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])

        # elif layout == Layout.SESSION.value.PERFORMANCE_LAYOUT:
        #     command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])

        # elif layout == Layout.SESSION.value.PERFORMANCE_LAYOUT:
        #     command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])

        # elif layout == Layout.SESSION.value.PERFORMANCE_LAYOUT:
        #     command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])
        print('______built command:',command)
        self._execute_command(command)

        

    def _process_up_arrow(self):
        pass

    def _process_down_arrow(self):
        pass

    def _process_left_arrow(self):
        pass

    def _process_right_arrow(self):
        pass


    def process_arrows(self, arrow_pad, is_limit_reached):
        if arrow_pad == Pad_ID.UP_ARROW:
            self._process_up_arrow(is_limit_reached)
            pass

        elif arrow_pad == Pad_ID.DOWN_ARROW:
            self._process_down_arrow(is_limit_reached)
            pass

        elif arrow_pad == Pad_ID.LEFT_ARROW:
            self._process_left_arrow(is_limit_reached)
            pass

        elif arrow_pad == Pad_ID.RIGHT_ARROW:
            self._process_right_arrow(is_limit_reached)
            pass
    
    
    def _next_session(self):
        sessions = list(Layout.SESSION.value)
        current_index = sessions.index(self.current_layout)
        sessions_size = len(sessions)
        new_layout = ''

        if current_index == sessions_size - 1:
            new_layout = sessions[0]
        else:
            new_layout = sessions[current_index + 1]

        return new_layout

        
    # def process_pad(pad):
    #     if pad == Pad_ID.SESSION:



    # def run_intro(self):
    #     pass

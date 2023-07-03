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
    def __init__(self, id, name = '', **states):
        self.id = id
        self.name = name
        self.commands = []
        self.current_state = ''
        self.states = {
            # 'name' : states.get('name') or '',
            # 'idle' : states.get('idle') or states.get('active'),
            # 'active' : states.get('active') or states.get('active'),
            # 'active2' : states.get('active2') or states.get('active'),
            # 'active3' : states.get('active3') or states.get('active'),
            # 'double_click' : states.get('double_click') or states.get('active'),
            # 'long_click' : states.get('long_click') or states.get('active')
        }
        
        self.name = name or ''

        for key in states.keys():
            self.states[key] = states[key]

        # print(self.states['name'] , type(states['idle'] ))
        # self.states['idle'] = states.get('idle') or states.get('active')
        # self.states['active'] = states.get('active') or states.get('active')
        # self.states['active2'] = states.get('active2') or states.get('active')
        # self.states['active3'] = states.get('active3') or states.get('active')
        # self.states['double_click'] = states.get('double_click') or states.get('active')
        # self.states['long_click'] = states.get('long_click') or states.get('active')
        print('----states:',self.states)


    def set_states(self, idle = 0, active = 0, double_click = 0, long_click = 0):
        self.states = {
            'idle' : idle,
            'active' : active,
            'double_click' : double_click,
            'long_click' : long_click
        }
    

    def set_state(self, state, value):
        self.states[state] = value

    def get_state(self, state):
        return self.states.get(state)


    def _update(self):
        print('command contains:', self.commands)
        for command in self.commands:
            print(type(command),'...about to update w: ', command)
            device.midiOutSysex(bytes(command))
        self.commands = []


    def _set_color(self, color, led_type = 'static'):
        color_sysex = []
        _led_type = ''
        if self.id in Pad_ID.CC_PADS.value:
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

    def trigger_state(self, state):
        print('+++states to be checked:',self.states, state in self.states)
        if 'states' in self.states:
            print('check if:',state,' in:',self.states['states'], state in self.states['states'])
            if state in self.states['states']:
                new_state  = self.states['states'].get(state)
                print('about to pass state: ',new_state)
                self.commands.append(Mode['HEADER_START'] + new_state + Mode['HEADER_END'])

        self._update()


# class Session(Pad):
    


class LPX:
    def __init__(self):
        self.current_layout =  Layout.NOTE
        self.last_session_layout =  Layout.SESSION.value.PERFORMANCE_LAYOUT

        self.pads = {}
        self.pads[Pad_ID.UP_ARROW] = Pad(Pad_ID.UP_ARROW, 'up_arrow')
        self.pads[Pad_ID.DOWN_ARROW] = Pad(Pad_ID.DOWN_ARROW, 'down_arrow')
        self.pads[Pad_ID.LEFT_ARROW] = Pad(Pad_ID.LEFT_ARROW, 'left_arrow')
        self.pads[Pad_ID.RIGHT_ARROW] = Pad(Pad_ID.RIGHT_ARROW, 'right_arrow')

        self.pads[Pad_ID.SESSION] = Pad(Pad_ID.SESSION, 'session', states={'idle': [20, 89, 1], 'session': [20, 89, 1], 'mixer': [20, 12, 1], 'ch_rack': [20, 44, 1], 'pages': [20, 52, 1], 'chord': [20, 9, 1]})
        # print(']]]]]]]]]]]', self.pads[Pad_ID.SESSION] )

        self.pads[Pad_ID.NOTE] = Pad(Pad_ID.NOTE)
        self.pads[Pad_ID.CUSTOM] = Pad(Pad_ID.CUSTOM)
        self.pads[Pad_ID.CAPTURE_MIDI] = Pad(Pad_ID.CAPTURE_MIDI, 'capture_midi', states={'idle': [176, 98, 79], 'active': [176, 98, 87], 'double_click' : [176, 98, 13], 'long_click' : [176, 98, 72] })

        self.pads[Pad_ID.VOLUME] = Pad(Pad_ID.VOLUME, 'volume')
        self.pads[Pad_ID.PAN] = Pad(Pad_ID.PAN, 'pan')
        self.pads[Pad_ID.SEND_A] = Pad(Pad_ID.SEND_A, 'send_a')
        self.pads[Pad_ID.SEND_B] = Pad(Pad_ID.SEND_B, 'send_b')

        self.pads[Pad_ID.STOP_CLIP] = Pad(Pad_ID.STOP_CLIP, 'stop_clip')
        self.pads[Pad_ID.MUTE] = Pad(Pad_ID.MUTE, 'mute')
        self.pads[Pad_ID.SOLO] = Pad(Pad_ID.SOLO, 'solo')
        self.pads[Pad_ID.RECORD_ARM] = Pad(Pad_ID.RECORD_ARM, 'record_arm')

        


    def _build_command(self, command):
        print('time to build command')
        return Mode['HEADER_START'] + command + Mode['HEADER_END']
    
    
    def _execute_command(self, command):
        print('commmmand::::::::',command)
        device.midiOutSysex(bytes(command))

    def initialise_pads(self):
        for pad in self.pads:
            if self.pads[pad].get_state('idle') != 0:
                print('setting pad: ',self.pads[pad].name)
                self.pads[pad].trigger_state('idle')
            if self.pads[pad].name == 'session':
                self.pads[pad].trigger_state('session')

    def get_pad(self, pad_id):
        if pad_id in Pad_ID:
            return self.pads[pad_id]

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



    def recall_last_session(self, is_performance_mode):
        print('last session for trial is:',self.last_session_layout)
        if self.last_session_layout == Layout.SESSION.value.PERFORMANCE_LAYOUT and not is_performance_mode:
            print('better chang')
            self.last_session_layout = self._next_session()
        print('new is:', self.last_session_layout)
        self.switch_to_layout(self.last_session_layout)



    def toggle_session(self, is_performance_mode):
        next_session = self._next_session()
        print('trial for:', next_session)
        if next_session == Layout.SESSION.value.PERFORMANCE_LAYOUT and not is_performance_mode:
            self.current_layout = next_session  
            next_session = self._next_session()
            print('swapped session with:', next_session, not is_performance_mode)

        print('-----------toggling to new session::::', next_session)
        self.switch_to_layout(next_session)


    def build_session(self, layout):
        command = ''
        if layout == Layout.SESSION.value.PERFORMANCE_LAYOUT:
            print('______built performance')
            command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])
            self.pads[Pad_ID.SESSION].trigger_state('session')

        elif layout == Layout.SESSION.value.CH_RACK_LAYOUT:
            print('______built chrack')
            command = self._build_command(Mode['SESSION_CH_RACK_MODE'])
            self.pads[Pad_ID.SESSION].trigger_state('ch_rack')

        elif layout == Layout.SESSION.value.MIXER:
            print('______built mixer')
            command = self._build_command(Mode['VOLUME_MIXER_MODE'])
            self.pads[Pad_ID.SESSION].trigger_state('mixer')

        elif layout == Layout.SESSION.value.PAGES:
            print('______built pages')
            command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])
            self.pads[Pad_ID.SESSION].trigger_state('pages')

        elif layout == Layout.SESSION.value.CHORD_LAYOUT:
            print('______built chord')
            command = self._build_command(Mode['SESSION_PERFORMANCE_MODE'])
            self.pads[Pad_ID.SESSION].trigger_state('chord')

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
        current_index = sessions.index(self.last_session_layout)
        print(self.last_session_layout,' is current at index:',current_index)
        sessions_size = len(sessions)
        new_session_layout = ''

        if current_index == sessions_size - 1:
            new_session_layout = sessions[0]
        else:
            new_session_layout = sessions[current_index + 1]

        return new_session_layout

        
    def process_pad(pad_id):
        if pad_id == Pad_ID.CAPTURE_MIDI:
            stop_color = Led.STATIC + Pad_ID.CAPTURE_MIDI + Colors.CAPTURE_MIDI_STOP




    # def run_intro(self):
    #     pass

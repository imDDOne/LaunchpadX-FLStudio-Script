
from enum import Enum
 
 
class Layout(Enum):
    NOTE_MODE = 0

    SESSION_PERFORMANCE_MODE = 1
    SESSION_CH_RACK_MODE = 2
    SESSION_CHORD_MODE = 0

    VOLUME_CH_RACK_MODE = 3
    PAN_CH_RACK_MODE = 4

    VOLUME_MIXER_MODE = 5
    PAN_MIXER_MODE = 6
    

class Colors(Enum):
    DEFAULT_DISABLED = 0
    DEFAULT_IDLE = 0
    DEFAULT_ACTIVE = 1
    DEFAULT_PRESSED = 2

    NOTE = 0
    CUSTOM = 0
    CAPTURE_MIDI_PLAY = 0
    CAPTURE_MIDI_PAUSE = 0
    CAPTURE_MIDI_STOP = 0
    CAPTURE_MIDI_RECORD = 0

    PERFORMANCE = 1
    CHANNEL_RACK = 2
    MIXER = 0

    MIXER_VOLUME = 0
    MIXER_PAN = 0
    MIXER_SEND_A = 0
    MIXER_SEND_B = 0
    MIXER_STOP_CLIP = 0
    MIXER_MUTE = 0
    MIXER_SOLO = 0
    MIXER_RECORD_ARM = 0
    

class Pads(Enum):
    UP_ARROW = 0
    DOWN_ARROW = 0
    LEFT_ARROW = 0
    RIGHT_ARROW = 0
    
    SESSION = 0
    MIXER = 0
    NOTE = 0
    DRUM = 0
    DRUM_INTEL = 0
    CUSTOM = 0
    CAPTURE_MIDI = 0
    LOGO = 0

    VOLUME = 0
    PAN = 0
    SEND_A = 0
    SEND_B = 0
    STOP_CLIP = 0
    MUTE = 0
    SOLO = 0
    RECORD_ARM = 0

    GRID_WIDTH = 0
    GRID_HEIGHT = 0

class Button:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.command = []

    def _update(self):
        pass

    def _set_color(self):
        pass

    def process_press(self, data):
        self._update()
        pass


        

class LPX:
    def __init__(self):
        self.current_layout =  Layout.NOTE
        self.btn_up_arrow = Button()
        self.btn_down_arrow = Button()
        self.btn_left_arrow = Button()
        self.btn_right_arrow = Button()

        self.btn_session = Button()
        self.btn_note = Button()
        self.btn_custom = Button()
        self.btn_capture_midi = Button()

        self.btn_volume = Button()
        self.btn_pan = Button()
        self.btn_send_a = Button()
        self.btn_send_b = Button()

        self.btn_stop_clip = Button()
        self.btn_mute = Button()
        self.btn_solo = Button()
        self.btn_record_arm = Button()

    
    def enable_daw_mode(self):
        pass

    def switch_to_layout(self, layout):
        match layout:
            case Layout.SESSION_PERFORMANCE:
                self.current_layout = Layout.SESSION_PERFORMANCE
                pass

            case Layout.SESSION_CH_RACK:
                self.current_layout = Layout.SESSION_CH_RACK
                pass

            case Layout.VOLUME_CH_RACK:
                self.current_layout = Layout.VOLUME_CH_RACK
                pass

            case Layout.PAN_CH_RACK:
                self.current_layout = Layout.PAN_CH_RACK
                pass

            case Layout.VOLUME_MIXER:
                self.current_layout = Layout.VOLUME_MIXER
                pass

            case Layout.PAN_MIXER:
                self.current_layout = Layout.PAN_MIXER
                pass

            case _:
                self.current_layout = Layout.NOTE
                pass


    def _process_up_arrow(self):
        pass

    def _process_down_arrow(self):
        pass

    def _process_left_arrow(self):
        pass

    def _process_right_arrow(self):
        pass

    def process_arrows(self, arrow_pad, is_limit_reached):
        match arrow_pad:
            case Pads.UP_ARROW:
                self._process_up_arrow(is_limit_reached)
                pass

            case Pads.DOWN_ARROW:
                self._process_down_arrow(is_limit_reached)
                pass

            case Pads.LEFT_ARROW:
                self._process_left_arrow(is_limit_reached)
                pass

            case Pads.RIGHT_ARROW:
                self._process_right_arrow(is_limit_reached)
                pass

    def run_intro(self):
        pass

    
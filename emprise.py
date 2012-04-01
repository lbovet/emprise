import logging
logging.basicConfig()
logging.root.setLevel(logging.INFO)

def next_player():
    print "Next Player"

class Player(object):
    log = logging.getLogger("player")
    def activate():
        log.info("Activated")
    def play_clicked(self):
        log.info( "Play clicked")
    def play_double_clicked(self):
        log.info( "Play double-clicked")
    def left_clicked(self):
        log.info( "Left clicked")
    def right_clicked(self):
        log.info( "Right clicked")
    def up_clicked(self):
        log.info( "Up clicked")
    def down_clicked(self):
        log.info( "Down clicked")                  
    def up_down_clicked(self):
        log.info( "Up/Down clicked")

class MprisPlayer(Player):
    dbus_name = "<none>"
    

class Media(Player):
    log = logging.getLogger("media_player")
    def __init__(self):            
        import virtkey
        self.v = virtkey.virtkey()
    def activate():
        log.info("Media Center activated")
    def _click(self, keysym):
        self.v.press_keysym(keysym)
        self.v.release_keysym(keysym)
    def play_clicked(self):
        self._click(0xFF0D) # Enter
    def play_double_clicked(self):
        self._click(0xFF08) # Backspace
    def left_clicked(self):
        self._click(0xFF51) # Left
    def right_clicked(self):
        self._click(0xFF53) # Right
    def up_clicked(self):
        self._click(0xFF52) # Up
    def down_clicked(self):
        self._click(0xFF54)
    def up_down_clicked(self):
        self._click(0x078) # STOP
        next_player()
    


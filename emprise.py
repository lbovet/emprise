import logging
logging.basicConfig()
logging.root.setLevel(logging.INFO)

class Player(object):
    def _init_(self, name, default=False, dbus_name="<unknown>"):
        self.name=name
        self.next_player=None
        self.default=default
        self.dbus_name=dbus_name
        self.log = logging.getLogger(name)
        self.init()
    def init(self):
        pass    
    def activate(self):
        current_player=self
        if self.default:
            default_player=self
    def next_player(self):
        return next_player
    def toggle(self):
        self.log.info("Toggle")
    def stop(self):
        self.log.info("
    # Remote control
    def play_clicked(self):
        self.log.info( "Play clicked")
    def play_double_clicked(self):
        self.log.info( "Play double-clicked")
    def left_clicked(self):
        self.log.info( "Left clicked")
    def right_clicked(self):
        self.log.info( "Right clicked")
    def up_clicked(self):
        self.log.info( "Up clicked")        
    def down_clicked(self):
        self.log.info( "Down clicked")                  
    def up_down_clicked(self):
        self.log.info( "Up/Down clicked")    

class XMBC(Player):
    def init(self):            
        import virtkey
        self.v = virtkey.virtkey()
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
        self.next_player().activate()
    def next_player():
        return default_player

players = { 'banshee' : Player('banshee', default=True, dbus_name="org.mpris.banshee"),
   'radio': Player('radio'), default=True, dbus_name="org.mpris.xmms2"),
   'xbmc': Player('xbmc'), dbus_name="org.mpris.xbmc") }

players['banshee'].next_player = players['radio']
players['radio'].next_player = players['banshee']

current_player = players['radio']

current_player.activate()

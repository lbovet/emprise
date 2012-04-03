import logging
logging.basicConfig()
logging.root.setLevel(logging.INFO)

class Receiver(object):    
    def __init__(self):
        import gtk
        import keybinder
        keystr = ""
        keybinder.bind("F2", self.Q)
        keybinder.bind("F3", self.W)
        keybinder.bind("F4", self.A)
        keybinder.bind("F5", self.S)
        keybinder.bind("F7", self.Y)
        keybinder.bind("F6", self.X)
        keybinder.bind("F8", self.C)
        gtk.main()
    def Q(self):
        Player.current_player.play_clicked()
    def W(self):
        Player.current_player.play_double_clicked()
    def A(self):
        Player.current_player.left_clicked()
    def S(self):
        Player.current_player.right_clicked()
    def Y(self):
        Player.current_player.down_clicked()
    def X(self):
        Player.current_player.up_clicked()
    def C(self):
        Player.current_player.up_down_clicked()

class Player(object):
    current_player = None
    default_player = None
    def __init__(self, name, default=False, dbus_name="<unknown>"):
        self.name=name
        self.next_player=None
        self.default=default
        self.dbus_name=dbus_name
        self.log = logging.getLogger(name)
        self.init()
    def init(self):
        pass    
    def activate(self):
        self.log.info("Activating %s", self.name)
        Player.current_player=self
        if self.default:
            Player.default_player=self
    def toggle(self):
        self.log.info("Toggle")
    def stop(self):
        self.log.info("Stop")
    def previous(self):
        self.log.info("Previous")
    def next(self):
        self.log.info("Next")

    # Remote control
    def play_clicked(self):
        self.log.info( "Play clicked")
        self.toggle()
    def play_double_clicked(self):
        self.log.info( "Play double-clicked")        
    def left_clicked(self):
        self.log.info( "Left clicked")
        self.previous()
    def right_clicked(self):
        self.log.info( "Right clicked")
        self.next()
    def up_clicked(self):
        self.log.info( "Up clicked")   
        self.stop()
        self.next_player.activate()     
    def down_clicked(self):
        self.log.info( "Down clicked") 
    def up_down_clicked(self):
        self.log.info( "Up/Down clicked")    
        players['xbmc'].activate()

'''Special control for XBMC'''
class XBMC(Player):
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
        self._click(0xFF54) # Down
    def up_down_clicked(self):
        self._click(0x078) # X (STOP)
        self.log.info("Back to %s", Player.default_player.name)
        Player.default_player.activate()

players = { 'banshee' : Player('banshee', default=True, dbus_name="org.mpris.banshee"),
            'radio': Player('radio', default=True, dbus_name="org.mpris.xmms2"),
            'xbmc': XBMC('xbmc', dbus_name="org.mpris.xbmc") }

players['banshee'].next_player = players['radio']
players['radio'].next_player = players['banshee']

Player.current_player = players['radio']
Player.current_player.activate()

Receiver()

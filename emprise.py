import logging
logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop
bus_loop = DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus(mainloop=bus_loop)
loop = gobject.MainLoop()


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
        Player.current_player.left_right_clicked()
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
    def __init__(self, name, default=False, dbus_name=None, mpris_version=2):
        self.name=name
        self.next_player=None
        self.default=default
        self.dbus_name=dbus_name if dbus_name is not None else name
        self.log = logging.getLogger(name)
        self.commander = None
        self.mpris_version=mpris_version
        try:
            self.get_commander()
        except Exception, e:
            import traceback
            traceback.print_exc() 
            print "Skipping commander creation for %s" % self.name
    def activate(self):
        self.log.info("Activating %s", self.name)        
        Player.current_player=self
        if self.default:
            Player.default_player=self
    def play(self):
        self.log.info("Play")        
        self.get_commander().play()
    def toggle(self):
        self.log.info("Toggle")
        self.get_commander().playpause()
    def stop(self):
        self.log.info("Stop")
        self.get_commander().pause()        
    def previous(self):
        self.log.info("Previous")
        self.get_commander().previous()
    def next(self):
        self.log.info("Next")
        self.get_commander().next()
    def connect(self):
        self.commander.player.connect_to_signal("PropertyChanged", self.handle_signal)
    def get_commander(self):
        if self.commander is None:
            import dbus
            import mpris_remote            
            try:        
                constructor = mpris_remote.Commander2 if self.mpris_version==2 else mpris_remote.Commander1
                self.commander = constructor(bus, self.dbus_name)
                self.connect()
            except SystemExit:
                raise Exception("Could not create commander")
      	return self.commander
    def handle_signal(self, interface, changed_props, invalidated_props):
        print "Signal: "+changed_props
 
    # Remote control
    def play_clicked(self):
        self.log.info( "Play clicked")
        self.toggle()
    def left_right_clicked(self):
        self.log.info( "Left+Right clicked")        
    def left_clicked(self):
        self.log.info( "Left clicked")
        self.previous()
    def right_clicked(self):
        self.log.info( "Right clicked")
        self.next()
    def up_clicked(self):
        self.log.info( "Up clicked")   
        self.next_player.activate()   
        self.next_player.play()        
     	self.stop()
    def down_clicked(self):
        self.log.info( "Down clicked") 
    def up_down_clicked(self):
        self.log.info( "Up+Down clicked")    
        players['xbmc'].activate()
        self.stop()

class VLC(Player):
    def __init__(self, name, default=False):         
        Player.__init__(self, name, default, dbus_name="vlc", mpris_version=1)
    def connect(self):
        print "Connecting vlc"
        player = bus.get_object("org.mpris.vlc", "/Player")
        player.connect_to_signal("PropertyChanged", self.handle_signal)

'''Special control for XBMC'''
class XBMC(Player):
    def __init__(self, name, default=False):            
        import virtkey
        self.v = virtkey.virtkey()
        Player.__init__(self, name)
    def _click(self, keysym):
        self.v.press_keysym(keysym)
        self.v.release_keysym(keysym)
    def play_clicked(self):
        self._click(0xFF0D) # Enter
    def left_right_clicked(self):
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
        Player.default_player.play()                

players = { 'banshee' : Player('banshee', default=True),
            'radio': VLC('radio', default=True),
            'xbmc': XBMC('xbmc') }

players['banshee'].next_player = players['radio']
players['radio'].next_player = players['banshee']

Player.current_player = players['radio']
Player.current_player.activate()

loop.run()

#Receiver()


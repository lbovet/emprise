import logging
import os
logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

import dbus
from dbus.mainloop.glib import DBusGMainLoop
bus_loop = DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus(mainloop=bus_loop)

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
    players = None
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
        if not Player.current_player == self:
            for player in Player.players.values():
                if not player == self:
                    try:
                        player.stop()
                    except:                        
                        self.log.info("Could not stop %s" % player.name)
                        import traceback
                        traceback.print_exc()                                                
            Player.current_player=self
            if self.default:
                Player.default_player=self
            from espeak import espeak
            self.say(self.name+"!")
        
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

    def click_noise(self):
        import playwav
        import alsaaudio
        import wave
        f = wave.open(os.path.join(os.path.dirname(__file__),"click.wav"), 'rb')
        device = alsaaudio.PCM(card="default")
        playwav.play(device, f)
        f.close()        
    def say(self, message):
        from espeak import espeak
        espeak.set_parameter(espeak.Parameter.Pitch, 5)
        espeak.set_parameter(espeak.Parameter.Rate, 150)
        espeak.synth(message)
        
    def connect(self):
        obj = bus.get_object("org.mpris.MediaPlayer2."+self.dbus_name, "/org/mpris/MediaPlayer2")
        obj.connect_to_signal("PropertiesChanged", self.handle_signal)

    def handle_signal(self, interface, changed_props, invalidated_props):
        if 'PlaybackStatus' in changed_props and changed_props['PlaybackStatus'] == 'Playing':
            self.activate()

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
 
    # Remote control
    def play_clicked(self):        
        self.log.info( "Play clicked")
        self.toggle()
        self.click_noise()
    def left_right_clicked(self):
        self.log.info( "Left+Right clicked")        
    def left_clicked(self):
        self.log.info( "Left clicked")
        self.previous()
        self.click_noise()
    def right_clicked(self):
        self.log.info( "Right clicked")
        self.next()
        self.click_noise()
    def up_clicked(self):
        self.log.info( "Up clicked")   
        self.next_player.activate()   
        self.next_player.play()        
     	self.stop()
    def down_clicked(self):
        self.log.info( "Down clicked") 
        self.say(self.name+"!")
    def up_down_clicked(self):
        self.log.info( "Up+Down clicked")    
        players['xbmc'].activate()
        self.stop()

'''Special dbus events for VLC'''
class VLC(Player):
    def __init__(self, name, default=False):         
        Player.__init__(self, name, default, dbus_name="vlc", mpris_version=1)
    def connect(self):
        player = bus.get_object("org.mpris.vlc", "/Player")
        player.connect_to_signal("TrackChange", self.handle_signal)
        player.connect_to_signal("StatusChange", self.handle_signal)
    def handle_signal(self, value):
        if type(value) == dbus.Dictionary or value[0] == 0:
            self.activate()

'''Special control for XBMC'''
class XBMC(Player):
    def __init__(self, name, default=False):            
        import virtkey
        self.v = virtkey.virtkey()
        Player.__init__(self, name, dbus_name="xbmc")        
    def stop(self):        
        pass # avoid errors, not yet controlled through mpris
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

Player.players = { 'banshee' : Player('Music Player', default=True, dbus_name="banshee"),
                   'radio': VLC('Radio', default=True),
                   'xbmc': XBMC('Media Center') }

Player.players['banshee'].next_player = Player.players['radio']
Player.players['radio'].next_player = Player.players['banshee']

Player.players['banshee'].activate()

Receiver()


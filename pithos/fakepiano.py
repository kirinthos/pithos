import time

counter = 0
def count():
	global counter
	counter +=1
	return counter

class PianoPandora(object):
	def __init__(self):
		self.stations = [
			PianoStation("Fake 1"),
			PianoStation("Fake 2"),
			PianoStation("Fake 3"),
			PianoStation("QuickMix", 1),
		]
		
	def connect(self, user, password):
		print "logging in with", user, password
		time.sleep(3)

		
	def get_playlist(self, station):
		r = [PianoSong("Test  &song %i"%count(), "Test Artist", "Album %s"%station.name) for i in range(4)]		
		time.sleep(3)
		return r
		
		
		

		
class PianoStation(object):
	def __init__(self, name, qm=False):
		self.id = id(self)
		self.isCreator = True
		self.isQuickMix = qm
		self.name = name
		self.useQuickMix = True
		
class PianoSong(object):
	def __init__(self, title, artist, album):
		self.id=id(self)
		self.album = album
		self.artist = artist
		self.audioUrl = 'file:///home/km/Downloads/download'
		self.title = title
		
		
	


class Track:
	def __init__(self, track_id, date_added, name, artist, album, listen_count):
		self.id = track_id
		self.name = name
		self.artist = artist
		self.album = album

		self.date_added = date_added
		self.listen_count = listen_count

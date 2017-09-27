
from .TBuffer import TBuffer


class TDirectory (object) :

	def __init__(self, file, dirname, cycle) :
		self.fFile = file
		self._typename = "TDirectory"
		self.dir_name = dirname
		self.dir_cycle = cycle
		self.fKeys = []

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value) :
		object.__setattr__( self, key, value )
		
	def GetKey(self, keyname, cycle ) :
		for i in range( 0, len(self.fKeys) ) :
			if self.fKeys[i].fName == keyname and self.fKeys[i].fCycle == cycle :
				return  self.fKeys[i]
		return None
		#TODO : add second part of impl

	def ReadKeys(self, objbuf ) :

		objbuf.ClassStreamer( self, 'TDirectory' )

		if self.fSeekKeys <= 0 or self.fNbytesKey <= 0 :
			return None

		file = self.fFile

		blob = file.ReadBuffer([ self.fSeekKeys, self.fNbytesKey ] )
		if None == blob :
			return None

		buf = TBuffer( blob, 0, file, None )
		buf.ReadTKey()
		nkeys = buf.ntoi4()

		for i in range(0, nkeys) :
			self.fKeys.append( buf.ReadTKey() )
		file.fDirectories.append( self )


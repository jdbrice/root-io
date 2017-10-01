
from .TBuffer import TBuffer


class TDirectory (object) :

	def __init__(self, file, dirname, cycle) :
		self.fFile = file
		self._typename = "TDirectory"
		self.dir_name = dirname
		self.dir_cycle = cycle
		self.fKeys = []

	def to_json( self ) :
		obj = {
			'fSeekKeys' : self['fSeekKeys'],
			'dir_name' : self['dir_name'],
			'dir_cycle' : self['dir_cycle'],
			'fDatimeM' : self['fDatimeM'],
			'fNbytesName' : self['fNbytesName'],
			'fTitle' : self['fTitle'],
			'fDatimeC' : self['fDatimeC'],
			'fSeekParent' : self['fSeekParent'],
			'fKeys' : self['fKeys'],
			'fSeekDir' : self['fSeekDir'],
			'fNbytesKeys' : self['fNbytesKeys'],

			# "_typename": self._typename,
			# "dir_name" : self.dir_name,
			# "dir_cycle" : self.dir_cycle,
			# "fKeys" : self.fKeys
		}
		return obj

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value) :
		object.__setattr__( self, key, value )
	
	def list_keys(self) :
		for k in self.fKeys :
			print k['fName']
	
	def GetKey(self, keyname, cycle ) :
		for i in range( 0, len(self.fKeys) ) :
			if self.fKeys[i]['fName'] == keyname and self.fKeys[i]['fCycle'] == cycle :
				return  self.fKeys[i]
		pos = keyname.rfind( '/' )

		while pos > 0 :
			dirname = keyname[0:pos]
			subname = keyname[pos+1:]
			
			dirkey = self.GetKey( dirname, 1 )
			
			if None != dirkey and "fClassName" in dirkey and "TDirectory" in dirkey['fClassName'] :
				tdir = self.ReadObject( dirname )
				if None != tdir :
					return tdir.GetKey( subname, cycle )
			
			pos = keyname.rfind( '/', 0, pos-1 )
		
		return None

		return None
		#TODO : add second part of impl

	def ReadKeys(self, objbuf ) :

		objbuf.ClassStreamer( self, 'TDirectory' )

		if self.fSeekKeys <= 0 or self.fNbytesKeys <= 0 :
			return None

		file = self.fFile

		blob = file.ReadBuffer([ self.fSeekKeys, self.fNbytesKeys ] )
		if None == blob :
			return None

		buf = TBuffer( blob, 0, file, None )
		buf.ReadTKey()
		nkeys = buf.ntoi4()

		for i in range(0, nkeys) :
			self.fKeys.append( buf.ReadTKey() )
		file.fDirectories.append( self )


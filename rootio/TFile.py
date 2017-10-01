import rootio.ROOT as ROOT
from rootio.TBuffer import TBuffer
from rootio.TDirectory import TDirectory
import os
import logging
from . import UnZip
import box 
import json


class TFile (object) :
	def __init__(self, url) :
		
		self.logger = logging.getLogger( "rootio.TFile" )
		# self.logger.debug( "Creating TFile[  url=%s ]", url )
		self._typename      = "TFile"
		self.fEND           = 0
		self.fFullURL       = url
		self.fURL           = url
		self.fAcceptRanges  = True
		self.fUseStampPar   = "stamp  = "
		self.fFileContent   = None
		self.fMaxRanges     = 200
		self.fDirectories   = []
		self.fKeys          = []
		self.fSeekInfo      = 0
		self.fNbytesInfo    = 0
		self.fTagOffset     = 0
		self.fStreamerInfos = None
		self.fFileName      = ""
		self.fStreamers     = {}
		self.fBasicTypes    = {}

		# TLocalFile parts
		
		self.fUseStampPar = False;

		if os.path.isfile( url ):
			# TODO open file
			file = open( url, "rb")
			self.fLocalFile = file
			self.fEND = os.stat( url ).st_size
			self.fFullURL = file.name;
			self.fURL = file.name;
			self.fFileName = file.name;
		else :
			raise Exception( "File DNE" )

		self.ReadKeys()

	def to_json( self ) :
		obj = {
			"_typename": self._typename,
			"fAcceptRanges": self.fAcceptRanges,
			"fBEGIN": self.fBEGIN,
			"fBasicTypes": self.fBasicTypes,
			"fCompress": self.fCompress,
			"fDatimeC" : self.fDatimeC,
			"fDatimeM" : self.fDatimeM,
			"fDirectories" : self.fDirectories,
			"fEND" : self.fEND,
			"fFileContent" : self.fFileContent,
			"fFileName" : self.fFileName,
			"fFullURL" : self.fFullURL,
			"fKeys" : self.fKeys,
			"fMaxRanges" : self.fMaxRanges,
			"fNbytesFree" : self.fNbytesFree,
			"fNbytesInfo" : self.fNbytesInfo,
			"fNbytesKeys" : self.fNbytesKeys,
			"fNbytesName" : self.fNbytesName,
			"fSeekDir" : self.fSeekDir,
			"fSeekFree" : self.fSeekFree,
			"fSeekInfo" : self.fSeekInfo,
			"fSeekKeys" : self.fSeekKeys,
			"fSeekParent" : self.fSeekParent,
			"fStreamerInfos" : self.fStreamerInfos,
			"fStreamers" : self.fStreamers,
			"fTagOffset" : self.fTagOffset,
			"fTitle" : self.fTitle,
			"fURL" : self.fURL,
			"fUnits" : self.fUnits,
			"fUseStampPar" : self.fUseStampPar,
			"fVersion" : self.fVersion,
			# "dict" : self.__dict__.keys()
		}
		return obj


	def list_keys(self) :
		for k in self.fKeys :
			print( k['fName'] )


	def ReadBuffer( self, place ) :
		# self.logger.debug( "ReadBuffer( %s )", place )
		self.fLocalFile.seek( place[0] )
		return self.fLocalFile.read( place[1] )

	def GetDir(self, dirname, cycle ):
		if None == cycle and type(dirname) is str :
			pos = s.rfind( ';' )
			if pos > 0 :
				cycle = dirname[ pos+1: ]
				dirname = dirname[ 0:pos ]
		
		for j in range( 0, len(self.fDirectories) ) :
			tdir = self.fDirectories[j]
			if tdir.dir_name != dirname :
				continue
			if None != cycle and tdir.cycle != cycle :
				continue
			return tdir
		return None

	def GetKey(self, keyname, cycle ) :
		for i in range( 0, len(self.fKeys) ) :
			if 'fName' in self.fKeys[i] and self.fKeys[i]['fName'] == keyname and 'fCycle' in self.fKeys[i] and self.fKeys[i]['fCycle'] == cycle :
				return  self.fKeys[i]
		return None
		#TODO : add second part of impl

	def ReadObjBuffer(self, key ) :
		# self.logger.debug( "ReadObjBuffer( %s )", key )
		blob1 = self.ReadBuffer( [key['fSeekKey'] + key['fKeylen'], key['fNbytes'] - key['fKeylen']] )
		if None == blob1 :
			return None

		buf = None
		if key['fObjlen'] <= (key['fNbytes'] - key['fKeylen']) : 
			buf = TBuffer( blob1, 0, self, None )
		else :
			# self.logger.debug( "UNZIPPING obj buffer" )
			objbuf = UnZip.R__unzip(blob1, key['fObjlen'])
			if None == objbuf :
				return None
			buf = TBuffer( objbuf, 0, self, None )

		
		buf.fTagOffset = key['fKeylen']
		return buf

	def AddReadTree(self, obj ) :
		# self.logger.debug( "AddReadTree( %s )", obj )
		pass

	def Get( self, obj_name, cycle=1 ) :
		obj = self.ReadObject( obj_name, cycle )
		if None == obj :
			return None

		try :
			from rootio.Histogram import Histogram
			if "TH1" in obj['_typename'] or "TH2" in obj['_typename'] or "TH3" in obj['_typename'] :
				return Histogram( obj )
		except KeyError as ke :
			self.logger.error( ke )

		return None



	def ReadObject(self, obj_name, cycle = 1) :
		# self.logger.debug( "ReadObject( obj_name=%s, cycle=%d )", obj_name, cycle )

		# if type( cycle ) === function :
		if callable( cycle ) :
			cycle = 1 

		pos = obj_name.rfind( ';' )
		if pos > 0 :
			cycle = int( obj_name[pos+1 : pos+2 ] )
			obj_name = obj_name[ 0 : pos ]

		if cycle < 0 :
			cycle = 1

		while ( len(obj_name) > 0 and obj_name[0] == "/" ) :
			obj_name = obj_name[ 1: ]

		key = self.GetKey( obj_name, cycle )
		if None == key :
			return None

		if "StreamerInfo" == obj_name and "TList" == key['fClassName'] :
			return self.fStreamerInfos

		isdir = False
		if "TDirectory" == key['fClassName'] or "TDirectoryFile" == key['fClassName'] :
			isdir = True
			tdir = self.GetDir( obj_name, cycle )
			if None != tdir :
				return tdir

		buf = self.ReadObjBuffer( key )
		if None == buf :
			return None

		if isdir :
			tdir = TDirectory( self, obj_name, cycle )
			tdir.fTitle = key['fTitle']
			return tdir.ReadKeys( buf )

		obj = {}
		buf.MapObject( 1, obj )
		buf.ClassStreamer( obj, key['fClassName'] )

		if "TF1" == key['fClassName'] :
			return self.ReadFormulas( obj, -1 )

		#TODO : add Tree support

		return obj

	def ReadFormulas(self, tf1, cnt ) :
		# self.logger.debug( "ReadFormulas( ... )" )
		pass
		# TODO :add

	def ExtractStreamerInfos( self, buf ) :
		# self.logger.debug( "ExtractStreamerInfos( buf=%s )", buf )
		if None == buf :
			return

		lst = {}
		buf.MapObject( 1, lst )
		buf.ClassStreamer( lst, 'TList' )
		
		lst['_typename'] = "TStreamerInfoList"

		self.fStreamerInfos = lst
		# self.logger.debug( "fStreamerInfos = \n %s", json.dumps(lst, indent=4) )

		# TODO : add to ROOT
		# ROOT.addStreamerInfos( lst )

		for k in range( 0, len(lst['arr']) ) :
			# self.logger.info( "LOOP %d", k )
			# self.logger.info( json.dumps( self, indent=4, sort_keys=True ) )
			si = lst['arr'][k]
			
			if 'fElements' not in si or None == si['fElements'] :
				continue

			for l in range( 0, len(si['fElements']['arr']) ) :
				elem = si['fElements']['arr'][l]

				if 'fTypeName' not in elem or None == elem['fTypeName'] or 'fType' not in elem or None == elem['fType'] :
					continue

				typ = elem['fType'] 
				typename = elem['fTypeName']

				if typ >= 60 :
					if ROOT.IO.kStreamer == typ and "TStreamerSTL" == elem['_typename'] and None != elem['fSTLtype'] and None != elem['fCtype'] and elem['fCtype'] < 20 :
						prefix = ROOT.IO.StlNames[ elem['fSTLtype'] ] if None != ROOT.IO.StlNames and None != ROOT.IO.StlNames[ elem['fSTLtype'] ] else "undef" + "<"
						if 0 == typename.find( prefix ) and ">" == typename[ -1 ] :
							typ = elem['fCtype']
							
							#TODO trim string
							typename = typename[ len(prefix) : len(typename) - len(prefix) - 1 ].strip()
							if ROOT.IO.kSTLmap == elem['fSTLtype'] or ROOT.IO.kSTLmultimap == elem['fSTLtype'] :
								if typename.find(',')>0 :
									typename = typename[ 0: typename.find( ',' ) ].strip()
								else :
									continue
					if typ > 60 :
						continue
				else :
					if typ > 20 and "*" == typename[ -1 ] :
						typename = typename[ 0 : -1 ]
					typ = typ % 20

				kind = ROOT.IO.GetTypeId( typename )
				if kind == typ :
					continue

				if ROOT.IO.kBits == typ and ROOT.IO.kUInt == kind :
					continue
				if ROOT.IO.kCounter and ROOT.IO.kInt == kind :
					continue

				if None != typename and None != typ :
					# self.logger.debug( "Extract basic data type %s %s", typ, typename )
					self.fBasicTypes[ typename ] = typ
		# self.logger.info( "after extracting streamer info:" )
		# self.logger.info( json.dumps( self, indent=4, sort_keys=True ) )

	def __getitem__(self, key):
		return getattr(self, key)
	def __setitem__(self, key, value) :
		object.__setattr__( self, key, value )

	def ReadKeys( self ) :
		blob = self.ReadBuffer( [0, 1024] )
		if None == blob :
			return None

		buf = TBuffer( blob, 0, self, None )
		ftype = buf.substring( 0, 4 )
		# self.logger.debug( "fType=%s", ftype )
		if ftype != 'root' :
			# self.logger.debug("NOT A ROOT FILE")
			return

		buf.shift( 4 )

		self.fVersion = buf.ntou4()
		self.fBEGIN = buf.ntou4()
		if self.fVersion < 1000000 : # small size
			self.fEND = buf.ntou4()
			self.fSeekFree = buf.ntou4()
			self.fNbytesFree = buf.ntou4()
			nfree = buf.ntoi4()
			self.fNbytesName = buf.ntou4()
			self.fUnits = buf.ntou1()
			self.fCompress = buf.ntou4()
			self.fSeekInfo = buf.ntou4()
			self.fNbytesInfo = buf.ntou4()
		else :
			self.fEND = buf.ntou8()
			self.fSeekFree = buf.ntou8()
			self.fNbytesFree = buf.ntou8()
			nfree = buf.ntou4()
			self.fNbytesName = buf.ntou4()
			self.fUnits = buf.ntou1()
			self.fCompress = buf.ntou4()
			self.fSeekInfo = buf.ntou8()
			self.fNbytesInfo = buf.ntou4()

		# self.logger.debug("File Header:")
		# self.logger.debug( "self.fVersion    = %d", self.fVersion)
		# self.logger.debug( "self.fBEGIN      = %d", self.fBEGIN)
		# self.logger.debug( "self.fEND        = %d",  self.fEND )
		# self.logger.debug( "self.fSeekFree   = %d",  self.fSeekFree )
		# self.logger.debug( "self.fNbytesFree = %d",  self.fNbytesFree )
		# self.logger.debug( "self.fNbytesName = %d",  self.fNbytesName )
		# self.logger.debug( "self.fUnits      = %d",  self.fUnits )
		# self.logger.debug( "self.fCompress   = %d",  self.fCompress )
		# self.logger.debug( "self.fSeekInfo   = %d",  self.fSeekInfo )
		# self.logger.debug( "self.fNbytesInfo = %d",  self.fNbytesInfo )
		# self.logger.debug( "" )

		if None == self.fSeekInfo or None == self.fNbytesInfo :
			return None
		if 0 == self.fNbytesName or self.fNbytesName > 100000 :
			# self.logger.debug( "Init : cannot read directory info for file :", self.fURL )
			return None

		nbytes = self.fNbytesName + 22;
		nbytes += 4;  # fDatimeC.Sizeof();
		nbytes += 4;  # fDatimeM.Sizeof();
		nbytes += 18; # fUUID.Sizeof();
		if self.fVersion >= 40000 :
			nbytes += 12;

		blob3 = self.ReadBuffer( [self.fBEGIN, max( 300, nbytes )] )
		buf3 = TBuffer( blob3, 0, self, None )

		self.fTitle = buf3.ReadTKey()['fTitle']
		# self.logger.debug( "self.fTitle = %s", self.fTitle )
		buf3.locate( self.fNbytesName )
		buf3.ClassStreamer( self, 'TDirectory' )

		# self.logger.info( "file now:" )
		# self.logger.info( json.dumps(self, indent=4, sort_keys=True) )

		if False == hasattr( self, 'fSeekKeys' ) or 0 == self.fSeekKeys :
			# self.logger.debug( "Empty key list in", self.fURL )
			return None

		blob4 = self.ReadBuffer( [self.fSeekKeys, self.fNbytesKeys] )
		buf4 = TBuffer( blob4, 0, self, None )

		buf4.ReadTKey()
		nkeys = buf4.ntoi4()
		for i in range( 0, nkeys ) :
			k = buf4.ReadTKey()
			# self.logger.debug( "Adding Key : %s %s, %s ", k['fClassName'], k['fName'], k['fTitle'] )
			self.fKeys.append( k )

		blob5 = self.ReadBuffer( [self.fSeekInfo, self.fNbytesInfo] )
		buf5 = TBuffer( blob5, 0, self, None )
		si_key = buf5.ReadTKey()
		if None == si_key :
			# self.logger.debug( "No info?" )
			return None

		self.fKeys.append( si_key )
		# self.logger.debug(  "StreamerInfo:", si_key )
		buf6 = self.ReadObjBuffer( si_key )
		if None != buf6 :
			self.ExtractStreamerInfos( buf6 )

	def GetStreamer(self, classname, ver, s_i = None ):
		self.logger.debug( "GetStreamer(classname=%s, ver=%s, s_i=%s )", classname, ver, s_i )
		if 'TQObject' == classname or 'TBasket' == classname :
			return None

		fullname = classname
		streamer = None 

		if "TH1" == classname :
    			self.logger.debug("TH1")

		if None != ver and ( 'checksum' in ver or 'val' in ver ) :
			fullname += "$chksum" + str(ver['checksum']) if 'checksum' in ver else "$ver" + str(ver['val'])
			self.logger.debug( "Looking for streamer : %s",fullname )
			streamer = self.fStreamers[ fullname ] if fullname in self.fStreamers else None
			if None != streamer :
				self.logger.debug( "Found Streamer, just trust me" )

				return streamer

		self.logger.debug( "Looking for custom streamer named %s", classname)
		custom = ROOT.IO.CustomStreamers[ classname ] if classname in ROOT.IO.CustomStreamers else None

		if None != custom :
			self.logger.debug("Found custom streamer for %s", classname )
			
		if type( custom ) == str :
			return self.GetStreamer( custom, ver, s_i )

		if True == callable( custom ) :
			streamer = [ { 'typename' : classname, 'func': custom } ]
			return ROOT.AddClassMethods( classname, streamer )

		streamer = []
		if box.BoxList == type( custom ) :
			if 'name' not in custom and 'func' not in custom :
				return custom
			streamer.append( custom )
		
		# check element in streamer infos, one can have special cases
		if None == s_i : 
			s_i = self.FindStreamerInfo(classname, ver['val'], ver['checksum'] if 'checksum' in ver else None);

		if None == s_i :
			# delete this.fStreamers[fullname];
			if fullname in self.fStreamers :
				self.logger.debug( "s_i is None but % in Streamers", fullname )

			if 'nowarning' not in ver or ver['nowarning'] == None :
				self.logger.debug("Not found streamer for %s, ver=%s, checksum=%s, fullname=%s", classname, ver['val'], ver['checksum'] if 'checksum' in ver else None, fullname)
			return None

		# for each entry in streamer info produce member function

		try :
			self.logger.debug( "s_i = %s", s_i )
			for obj in s_i['fElements']['arr'] :
				# obj = s_i['fElements']['arr'][s]
				streamer.append( ROOT.IO.CreateMember( obj, self ) )
				self.logger.debug( "Appending streamer for obj=%s", obj )
		except KeyError :
			self.logger.debug( "No fElements.arr" )
		self.logger.debug( "fStreamers[%s] = %s", fullname, streamer )
		
		self.logger.debug( "fStreamers[%s] = SET", fullname )
		self.fStreamers[fullname] = streamer;

		return ROOT.AddClassMethods(classname, streamer);

	def FindStreamerInfo( self, clname, clversion, clchecksum = None ) :
		if None == self.fStreamerInfos :
			return None

		for si in self.fStreamerInfos['arr'] :
			if clchecksum != None and si['fCheckSum'] == clchecksum :
				return si
			if si['fName'] != clname :
				continue
			# this means that if it as not found by checksum it should have been None
			# if checksum was given it should match
			if clchecksum != None :
				continue

			if clversion != None and si['fClassVersion'] != clversion :
				continue

			return si

		return None
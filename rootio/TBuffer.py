# -*- coding: utf-8 -*-
# @Author: jdb
# @Date:   2017-06-14 17:36:08
# @Last Modified by:   Daniel
# @Last Modified time: 2017-09-26 17:47:21

from rootio.ROOT import ROOT as ROOT
from rootio.StreamerDict import Streamers
from rootio.IOData import IOData
import struct
import logging
import json
import sys

class TBuffer(object):

	# arr should be a byte array
	def __init__( self, arr, pos, file, length=None ):

		self.logger = logging.getLogger( "rootio.TBuffer" )
		self.logger.debug( "Creating TBuffer[ len(arr)=%d, pos=%d, file=%s ] %s", len(arr), pos, file.fURL, self )

		self._typename = "TBuffer"
		self.arr = arr;
		self.o = pos
		self.fFile = file
		self.length = length if None != length else 0
		self.length = len(arr) if None != arr else 0
		#self.ClearObjectMap()
		self.fTagOffset = 0
		self.last_read_version = 0
		self.fObjectMap = {}
		self.fDisplacement = 0

		self.ClearObjectMap()

	def to_json(self):
		obj = {
			# "arr" : self.arr,
			"pos" : self.o,
			# "tFile" : self.file,
			"length" : self.length,
			"fTagOffset" : self.fTagOffset,
			"last_read_version" : self.last_read_version,
			"fObjectMap" : self.fObjectMap,
			"fDisplacement" : self.fDisplacement
		}
		return obj

	def dump_state( self ) :
		m = {
			"_typename" : self._typename,
			"len(arr)" : len(self.arr),
			"pos" : self.o
		}
		return m

	def locate( self, pos ):
		self.o = pos
	def shift( self, cnt ):
		self.o = self.o + cnt
	def remain( self ):
		return self.length - self.o
	def GetMappedObject( self, tag ):
		return self.fObjectMap[ tag ] if tag in self.fObjectMap else None
	def MapObject( self, tag, obj ):
		if None == obj :
			return
		self.fObjectMap[tag] = obj
	def MapClass(self, tag, classname ):
		self.fClassMap[tag] = classname
	def GetMappedClass(self, tag):
		if tag in self.fClassMap :
			return self.fClassMap[tag]
		return -1
	
	def ClearObjectMap(self):
		self.fObjectMap = {}
		self.fClassMap = {}
		self.fObjectMap[0] = None
		self.fDisplacement = 0
	
	def ReadVersion(self):
		ver = {}
		bytecount = self.ntou4()
		if bytecount & IOData.kByteCountMask :
			ver['bytecount'] = bytecount - IOData.kByteCountMask - 2
		else :
			self.shift( -4 )

		self.last_read_version = ver['val'] = self.ntoi2()
		self.last_read_checksum = 0
		ver['off'] = self.o

		if ver['val'] <= 0 and ver['bytecount'] and ver['bytecount'] >= 4 :
			ver['checksum'] = self.ntou4()
			if None == self.fFile.FindSinfoChecksum( ver['checksum'] ) :
				self.shift( -4 )
			else :
				self.last_read_checksum = ver['checksum']
		return ver

	def CheckByteCount(self, ver, where ):
		if 'bytecount' in ver and None != ver['bytecount'] and 'off' in ver and (ver['off'] + ver['bytecount'] != self.o ) and None != where:
			self.logger.error( "Mismatch in %s, bytecount expected = %s, got = %s", where, ver['bytecount'], (self.o - ver['off']) ) 
			self.shift( ver['bytecount'] )
			return False
		return True

	def ReadString(self):
		return ReadFastString(-1)

	def ReadTString(self) :
		self.logger.debug( "ReadTString()" )
		self.logger.debug( "state = %s", self.dump_state() )

		l = self.ntou1()
		if 255 == l :
			l = self.ntou4()
		if 0 == l :
			self.logger.debug( "TString length is 0" )
			return ""

		self.logger.debug( "TString shift=%d", l )
		pos = self.o
		self.shift( l )

		if 0 == self.codeAt( pos ) :
			self.logger.debug( "TString is empty " )
			return ''
		tstring = self.substring( pos, pos + l )
		self.logger.debug( "TString = %s", tstring )
		return tstring

	def ReadFastString(self, n) :
		"""
		Reads a string of n chars or if n < 0 then it reads until it gets 0
		"""
		self.logger.debug( "ReadFastString( %d )", n )
		res = ""
		closed = False
		
		i = 0
		while ( n < 0 or i < n ) :
			code = self.ntou1()
			if 0 == code :
				closed = True;
				if n < 0 :
					break
			if False == closed :
				res += chr( code )
		self.logger.debug( "String=%s", res )
		return res


	def ntox( self, code ) :
		lens = {
			"B" : 1,
			"H" : 2,
			"I" : 4,
			"b" : 1,
			"h" : 2,
			"i" : 4,
			"f" : 4,
			"d" : 8,
		}
		try :
			fc = ">" + code;
			l = lens[ code ]
			v = struct.unpack( fc, self.arr[ self.o : self.o + l ] )
			self.o += l
			return v[0]
		except KeyError :
			pass 

		if "U" == code :
			return self.ntou8()
		if "u" == code :
			return self.ntoi8()

		return None


	# def ntot(self, n, type) :
	# 	v = struct.unpack( type, self.arr[ self.o : self.o + n ] )[0]
	# 	self.o = self.o + n
	# 	return v
	def ntou1(self) :
		l = 1
		v = struct.unpack( '>B', self.arr[ self.o : self.o + l ] )[0]
		self.o += l
		return v
	def ntou2(self) :
		l = 2
		v = struct.unpack( '>H', self.arr[ self.o:self.o+l ] )[0]
		self.o += l
		return v
	def ntou4(self) :
		l = 4
		v = struct.unpack( '>I', self.arr[ self.o:self.o+l ] )[0]
		self.o += l
		return v

	def ntou8(self) :
		high = self.ntou4()
		low = self.ntou4()
		return high * 0x100000000 + low;

	def ntoi1(self) :
		v = struct.unpack( '>b', self.arr[ self.o ] )[0]
		self.o = self.o + 1
		return v
	
	def ntoi2(self) :
		l = 2
		v = struct.unpack( '>h', self.arr[ self.o:self.o+l ] )[0]
		self.o += l
		return v
	def ntoi4(self) :
		l = 4
		v = struct.unpack( '>i', self.arr[ self.o:self.o+l ] )[0]
		self.o += l
		return v

	def ntoi8(self) :
		high = self.ntou4()
		low = self.ntou4()
		if high < 0x80000000 :
			return high * 0x100000000 + low;

		return -1 - ((~high) * 0x100000000 + ~low)

	def ntof( self ) :
		l = 4
		v = struct.unpack( '>f', self.arr[ self.o : self.o + l ] )[0]
		self.o += l
		return v

	def ntod( self ) :
		l = 8
		v = struct.unpack( '>d', self.arr[ self.o : self.o + l ] )[0]
		self.o += l
		return v


	def ReadFastArray( self, n, array_type ) :
		self.logger.debug( "ReadFastArray( n=%d, array_type=%s)", n, array_type )

		i = 0
		o = self.o
		view = self.arr
		array = [None] * n
		func = None
		
		if IOData.kDouble == array_type :
			func = self.ntod
		elif IOData.kFloat == array_type :
			func = self.ntof
		elif IOData.kLong == array_type or IOData.kLong64 == array_type :
			func = self.ntoi8
		elif IOData.kULong == array_type or IOData.kULong64 == array_type :
			func = self.ntou8
		elif IOData.kInt == array_type or IOData.kCounter == array_type :
			func = self.ntoi4
		elif IOData.kBits == array_type or IOData.kUInt == array_type :
			func = self.ntou4
		elif IOData.kShort == array_type :
			func = self.ntoi2
		elif IOData.kUShort == array_type :
			func = self.ntou2
		elif IOData.kChar == array_type :
			func = self.ntoi2
		elif IOData.kChar == array_type or IOData.kBool == array_type :
			func = self.ntou2
		elif IOData.kTString == array_type :
			func = self.ReadTString
		elif IOData.kDouble32 == array_type or IOData.kFloat16== array_type :
			self.logger.error( "Should not be used with FastArray" )
		else :
			func = self.ntou4

		if None != func :
			for i in range( 0, n ) :
				array[i] = func()
		else :
			self.logger.error( "FUNC Should not be NONE" )
		
		self.logger.debug( "ReadFastArray() = %s", array )

		
		# self.o = o not a mistake - dont uncomment
		return array

	def ReadNdimArray( self, handle, func ) :
		n_dim = handle['fArrayDim']
		max_i = handle['fMaxIndex']

		if n_dim < 1 and handle['fArrayLength'] > 0 :
			n_dim = 1
			max_i = [ handle['fArrayLength'] ]
		
		if 'minus1' in handle and None != handle['minus1'] :
			n_dim -= 1

		if n_dim < 1 :
			return func( self, handle )

		if 1 == n_dim :
			res = [None] * max_i[0]
			for i in range( 0, max_i[0] ) :
				res[i] = func( self, handle )
		if 2 == n_dim :
			res = [None] * max_i[0]
			for i in range( 0, max_i[0] ) :
				res1[None] * max_i[1]
				for j in range( 0, max_i[1] ) :
					res1[j] = func( self, handle )
				res[i] = res1
		else :
			indx = [0] * n_dim
			arr = [ [] ] * n_dim

			while indx[0] < max_i[0]:
				k = n_dim - 1
				arr[k].append( func( self, handle ) )
				indx[ k ] += 1
				while ndx[k] == max_i[k] and k > 0 :
					indx[k] = 0
					arr[k - 1].append( arr[k] )
					arr[k] = [ ]
					k -= 1
					indx[ k ] += 1
		return res

	def can_extract( self, place ) : 
		for n in range( 0, len(place), 2 ) :
			if place[n] + place[n+1] > self.length :
				return False
		return True

	def extract( self, place ) :
		if None == self.arr or False == self.can_extract( place ) :
			return None
		if 2 == len(place) :
			return self.arr[ place[0] : place[0] + place[1] ]

		res = []
		for n in range( 0, len(place), 2 ) :
			res[ n/2 ] = self.arr[ place[n] : place[n] + place[n+1] ]
		return res

	def codeAt(self, pos ) :
		if (sys.version_info > (3, 0)):
			return struct.unpack( 'B', bytes( [self.arr[ pos ]] ) )[0]
		else :
			return struct.unpack( 'B', self.arr[ pos ] )[0]

	def substring( self, beg, end ) :
		res = ""
		# TODO : check here
		for n in range( beg, end ) :
			res += chr( self.codeAt( n ) )
		return res

	def ReadTKey( self, key = None ) :
		if None == key :
			key = {}
		self.ClassStreamer( key, 'TKey' )
		# name = key.fName.replace( /['"]/g,'' )
		#  if name != key.fName :
			# key.fRealName = key.fName;
			# key.fName = name;
		return key;

	def ReadClass( self ) :
		self.logger.debug( "ReadClass" )
		self.logger.debug( "state = %s", self.dump_state() )
		
		class_info = { 'name': -1 }
		tag = 0
		bcount = self.ntou4()
		start_pos = self.o
		self.logger.debug( "bcount=%d, start_pos=%d", bcount,start_pos )

		if  not ( bcount & IOData.kByteCountMask ) or ( bcount == IOData.kNewClassTag ) :
			self.logger.debug( "ReadClass.A" )
			tag = bcount
			bcount = 0
		else :
			self.logger.debug( "ReadClass.B" )
			tag = self.ntou4()

		if not (tag & IOData.kClassMask) :
			self.logger.debug( "ReadClass.C" )
			class_info['objtag'] = tag + self.fDisplacement
			return class_info
		
		if tag == IOData.kNewClassTag :
			self.logger.debug( "ReadClass.D" )
			class_info['name'] = self.ReadFastString( -1 )
			
			index = self.fTagOffset + start_pos + IOData.kMapOffset
			if self.GetMappedClass( index ) == -1 :
				self.MapClass( index, class_info['name'] )
				self.logger.debug( "ReadClass.E" )
		else :
			self.logger.debug( "ReadClass.F" )
			clTag = (tag & ~IOData.kClassMask) + self.fDisplacement
			class_info['name'] = self.GetMappedClass( clTag )

		if -1 == class_info['name'] :
			self.logger.debug( "ReadClass.G" )
			self.logger.warn( "Could not find class with tag %s",clTag )

		self.logger.debug( "class_info=%s", class_info )
		return class_info



	def ReadObjectAny( self ) :
		self.logger.debug( "ReadObjectAny" )
		self.logger.debug( "state = %s", self.dump_state() )

		objtag = self.fTagOffset + self.o + IOData.kMapOffset
		clRef = self.ReadClass()

		self.logger.debug( "clRef = %s", clRef )

		if 'objtag' in clRef :
			return self.GetMappedObject( clRef['objtag'] )


		if 'name' in clRef and clRef['name'] == -1 :
			return None

		array_kind = ROOT.GetArrayKind( clRef['name'] )
		obj = None

		if 0 == array_kind :
			obj = self.ReadTString()
		elif array_kind > 0 :
			obj = self.ReadFastArray( self.ntou4(), array_kind )
			self.MapObject( objtag, obj )
		else :
			obj = {}
			self.MapObject( objtag, obj )
			self.ClassStreamer( obj, clRef['name'] )

		return obj


	def ClassStreamer( self, obj, classname ) :
		self.logger.debug( "ClassStreamer(%s, %s)", obj, classname )
		
		if "TBranchElement" == classname :
			pass

		# if "_typename" in obj :
		try :
			self.logger.debug( "obj._typename=%s", obj['_typename'] )
		except KeyError as ke:
			obj['_typename'] = classname
		# if False == hasattr(obj, '_typename' ) or None == obj['_typename'] :
		# if '_typename' not in obj :
		
		DirectStreamers = Streamers.DirectStreamers
		ds = DirectStreamers[classname] if classname in DirectStreamers else None
		if None != ds :
			self.logger.debug( 'Calling DirectStreamer["%s"]', classname )
			ds( self, obj )
			return obj

		# No DirectStreamer for this type
		# TODO
		

		ver = self.ReadVersion()
		self.logger.debug( "[%s] ver: %s", classname , ver )
		streamer = self.fFile.GetStreamer( classname, ver )
		if None != streamer :
			for n in range( 0, len( streamer ) ) :
				if 'func' in streamer[n] and callable( streamer[n]['func'] ) :
					streamer[n]['func']( self, obj )
					# self.logger.info( "%s", json.dumps( obj, indent=4 ) )
				else :
					self.logger.debug( "hmm, should be callable for classname=%s, obj=%s", classname, obj )
		else :
			self.logger.debug( "ClassStreamer not implemented yet for ", classname  )
			# TODO: Add Methods

		self.logger.debug( "streamer: \n %s", streamer )
		self.CheckByteCount( ver, classname )

		return obj



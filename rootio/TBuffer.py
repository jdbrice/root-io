# -*- coding: utf-8 -*-
# @Author: jdb
# @Date:   2017-06-14 17:36:08
# @Last Modified by:   jdb
# @Last Modified time: 2017-06-14 19:04:57

from rootio.ROOT import ROOT as ROOT
import struct

class TBuffer(object):

	# arr should be a byte array
	def __init__( self, arr, pos, file, length=None ):
		self._typename = "TBuffer"
		self.arr = arr;
		self.o = pos
		self.fFile = file
		self.length = length if None != length else 0
		self.length = len(arr) if None != arr else 0
		#self.ClearObjectMap()
		self.fTagOffset = 0
		self.last_read_version = 0

	def locate( self, pos ):
		self.o = pos
	def shift( self, cnt ):
		self.o = self.o + cnt
	def remain( self ):
		return self.length - self.o
	def GetMAppedObject( self, tag ):
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
		return None
	def ClearObjectMap(self):
		self.fObjectMap = {}
		self.fClassMap = {}
		self.fObjectMap[0] = None
		self.fDisplacement = 0
	
	def ReadVersion(self):
		ver = {}
		bytecount = self.ntou4()
		if bytecount & ROOT.IO.kByteCountMask :
			ver['bytecount'] = bytecount - ROOT.IO.kByteCountMask - 2
		else :
			self.shift( -4 )

		self.last_read_version = ver['val'] = self.ntoi2()
		self.last_read_checksum = 0
		ver.off = self.o

		if ver['val'] <= 0 and ver['bytecount'] and ver['bytecount'] >= 4 :
			ver['checksum'] = self.ntou4()
			if None == self.fFile.FindSinfoChecksum( ver['checksum'] ) :
				self.shift( -4 )
			else :
				self.last_read_checksum = ver['checksum']
		return ver

	def CheckByteCount(self, ver, where ):
		if 'bytecount' in ver and None != ver['bytecount'] and 'off' in ver and (ver['off'] + ver['bytecount'] != self.o ) and None != where:
			print( "Mismatch in %d, bytecount expected = %d, got = %d" % ( where, ver['bytecount'], (self.o - ver['off']) )  )
			self.shift( ver['bytecount'] )
			return False
		return True

	def ReadString(self):
		return ReadFastString(-1)

	def ReadTString(self) :
		l = self.ntou1()
		if 255 == l :
			l = self.ntou4()
		if 0 == l :
			return ""

		pos = self.o
		self.shift( l )

		if 0 == self.codeAt( pos ) :
			return ''
		return self.substring( pos, pos + l )

	def ReadFastString(self, n) :
		if n < 0 :
			return ''
		
		res = ""
		closed = False
		# CHECK JS version, not sure if this is the same!
		for i in range(n) :
			code = self.ntou1()
			if 0 == code :
				closed = True
				if n < 0 :
					break
			# TODO : python eq -> check
			if False == closed :
				res += chr( code )
		return res

	# def ntot(self, n, type) :
	# 	v = struct.unpack( type, self.arr[ self.o : self.o + n ] )[0]
	# 	self.o = self.o + n
	# 	return v
	def ntou1(self) :
		l = 1
		v = struct.unpack( 'B', self.arr[ self.o : self.o + l ] )[0]
		self.o += l
		return v
	def ntou2(self) :
		l = 2
		v = struct.unpack( 'H', self.arr[ self.o:self.o+l ] )[0]
		self.o += l
		return v
	def ntou4(self) :
		l = 4
		v = struct.unpack( 'I', self.arr[ self.o:self.o+l ] )[0]
		self.o += l
		return v

	def ntou8(self) :
		high = self.ntou4()
		low = self.ntou4()
		return high * 0x100000000 + low;

	def ntoi1(self) :
		v = struct.unpack( 'b', self.arr[ self.o ] )[0]
		self.o = self.o + 1
		return v
	
	def ntou2(self) :
		l = 2
		v = struct.unpack( 'h', self.arr[ self.o:self.o+l ] )[0]
		self.o += l
		return v
	def ntou4(self) :
		l = 4
		v = struct.unpack( 'i', self.arr[ self.o:self.o+l ] )[0]
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
		v = struct.unpack( 'f', self.arr[ self.o : self.o + l ] )[0]
		self.o += l
		return v

	def ntod( self ) :
		l = 8
		v = struct.unpack( 'd', self.arr[ self.o : self.o + l ] )[0]
		self.o += l
		return v


	def ReadFastArray( self, n, array_type ) :
		# TODO
		i = 0
		o = self.o
		view = self.arr
		switcher = {
			ROOT.IO.kDouble : 0
		}

	def can_extract( self, place ) : 
		for n in range( 0, len(place), 2 ) :
			if place[n] + place[n+1] > self.length :
				return False
		return True

	def extract( self, place ) :
		if None == self.arr or False == self.can_extract( place ) :
			return None
		if 2 == len(place) :
			return self.arr[ place[0] : place[1] ]

		res = []
		for n in range( 0, len(place), 2 ) :
			res[ n/2 ] = self.arr[ place[n] : place[n+1] ]
		return res

	def codeAt(self, pos ) :
		return struct.unpack( 'B', self.arr[ pos ] )[0]

	def substring( self, beg, end ) :
		res = ""
		# TODO : check here
		for n in range( beg, end ) :
			res += char( self.codeAt( n ) )
		return res

import struct
import zlib
import gzip
import logging
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def getChar( arr, curr ) :
	return struct.unpack( 'c', arr[curr:curr+1] )[0]
	
def getCode( arr, curr ) :
	return struct.unpack( 'b', arr[curr:curr+1] )[0]

def R__unzip( arr, tgtsize, src_shift = 0 ) :
	logging.getLogger("R__unzip").debug( "R__unzip( len(arr)=%d, tgtsize=%d, src_shift=%d )", len(arr), tgtsize, src_shift )
	totallen = len(arr)
	curr = src_shift
	fullres = 0
	tgtbuf = None

	while fullres < tgtsize :
		logging.getLogger("R__unzip").debug( "curr=%d", curr )
		fmt = "unknown"
		off = 0
		headersize = 9

		if curr + headersize >= totallen :
			logging.getLogger("R__unzip").debug( "Error in R__unxip : header size exceeds buffer size" )
			return None

		logging.getLogger("R__unzip").debug( "%s%s" %(getChar(arr, curr), getChar(arr, curr+1)) )
		if getChar(arr, curr) == b'Z' and getChar(arr, curr+1) == b'L' and getCode(arr, curr+2) == 8 :
			fmt = "new"
			off = 2
		elif getChar(arr, curr) == b'C' and getChar(arr, curr+1) == b'S' and getCode(arr, curr+2) == 8 :
			fmt = "old"
			off = 0
		elif getChar(arr, curr) == b'X' and getChar(arr, curr+1) == b'Z' :
			fmt = "LZMA";

		if "new" != fmt and "old" != fmt :
			logging.getLogger("R__unzip").debug( "ZLIB format not supported" )
			return None

		srcsize = headersize + ((getCode(arr, curr+3) & 0xff) | ((getCode(arr, curr+4) & 0xff) << 8) | ((getCode(arr, curr+5) & 0xff) << 16));
		uint8arr = arr[ curr + headersize + off :  ]

		# The -15 is a hack to get it to ignore the header and stream info since this is a raw chunk
		tgtbuf = zlib.decompress( uint8arr, -zlib.MAX_WBITS )
		reslen = len( tgtbuf )
		
		fullres += reslen
		curr += srcsize

	if fullres != tgtsize :
		logging.getLogger("R__unzip").debug( "R__unzip: failed to unzip data. Expects %d, got %d", tgtsize, fullres )
		return None

	return tgtbuf
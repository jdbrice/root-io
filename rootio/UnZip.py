
import ROOT
import zlib
import gzip
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

def R__unzip( arr, tgtsize, src_shift = 0 ) :
	ROOT.ROOT.logger.debug( "R__unzip( len(arr)=%d, tgtsize=%d, src_shift=%d )", len(arr), tgtsize, src_shift )
	totallen = len(arr)
	curr = src_shift
	fullres = 0
	tgtbuf = None

	while fullres < tgtsize :
    		ROOT.ROOT.getLogger("R__unzip").info( "curr=%d", curr )
		fmt = "unknown"
		off = 0
		headersize = 9

		if curr + headersize >= totallen :
			ROOT.ROOT.logger.debug( "Error in R__unxip : header size exceeds buffer size" )
			return None
		
		ROOT.ROOT.logger.debug( "%s%s" %(ROOT.ROOT.getChar(arr, curr), ROOT.ROOT.getChar(arr, curr+1)) )
		if ROOT.ROOT.getChar(arr, curr) == 'Z' and ROOT.ROOT.getChar(arr, curr+1) == 'L' and ROOT.ROOT.getCode(arr, curr+2) == 8 :
			fmt = "new"
			off = 2
		elif ROOT.ROOT.getChar(arr, curr) == 'C' and ROOT.ROOT.getChar(arr, curr+1) == 'S' and ROOT.ROOT.getCode(arr, curr+2) == 8 :
			fmt = "old"
			off = 0
		elif ROOT.ROOT.getChar(arr, curr) == 'X' and ROOT.ROOT.getChar(arr, curr+1) == 'Z' :
			fmt = "LZMA";

		if "new" != fmt and "old" != fmt :
			ROOT.ROOT.logger.debug( "ZLIB format not supported" )
			return None

		srcsize = headersize + ((ROOT.ROOT.getCode(arr, curr+3) & 0xff) | ((ROOT.ROOT.getCode(arr, curr+4) & 0xff) << 8) | ((ROOT.ROOT.getCode(arr, curr+5) & 0xff) << 16));
		uint8arr = arr[ curr + headersize + off :  ]

		# The -15 is a hack to get it to ignore the header and stream info since this is a raw chunk
		tgtbuf = zlib.decompress( uint8arr, -zlib.MAX_WBITS )
		reslen = len( tgtbuf )
		
		fullres += reslen
		curr += srcsize

	if fullres != tgtsize :
		ROOT.ROOT.logger.debug( "R__unzip: failed to unzip data. Expects %d, got %d", tgtsize, fullres )
		return None

	return tgtbuf
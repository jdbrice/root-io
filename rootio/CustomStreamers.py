
import sys
import logging
from rootio.IOData import IOData, BIT
import math
import json

def TList( buf, obj ) :
	logging.getLogger("CustomStreamers.TList").debug( "TList( buf=%s, obj=%s )", buf, obj )
	# stream all objects in the list from the I/O buffer
	if '_typename' not in obj :
		obj['_typename'] = "TList";
	# obj.$kind = "TList"; // all derived classes will be marked as well
	if buf.last_read_version > 3 : 
		buf.ClassStreamer(obj, "TObject")
		obj['name'] = buf.ReadTString();
		nobjects = buf.ntou4() 
		obj["arr"] = [None] * nobjects;
		obj["opt"] = [None] * nobjects;
		
		logging.getLogger("CustomStreamers.TList").debug( "TList length=%d", nobjects )
		for i in range( 0, nobjects ) :
			logging.getLogger("CustomStreamers.TList").debug( "Reading object %d", i )
			obj['arr'][i] = buf.ReadObjectAny();
			obj['opt'][i] = buf.ReadTString();
	
	else :
		obj['name'] = "";
		obj['arr'] = [];
		obj['opt'] = [];
	logging.getLogger("CustomStreamers.TList").debug( "TList result ( buf=%s, obj=%s )", buf, obj )


def TObject( buf, obj ) :
	logging.getLogger( "CustomStreamers.TObject" ).debug( "( buf=%s, obj=%s )", buf, obj )
	obj['fUniqueID'] = buf.ntou4()
	obj['fBits'] = buf.ntou4()
	if ( obj[ 'fBits' ] & IOData.kIsReferenced) :
		buf.ntou2()
	logging.getLogger( "CustomStreamers.TObject" ).debug( "TObject( buf=%s, obj=%s )", buf, obj )


def TStreamerInfo( buf, obj ) :
	logging.getLogger( "CustomStreamers.TStreamerInfo" ).debug( "( buf=%s, obj=%s )", buf, obj )
	buf.ClassStreamer( obj, "TNamed" )
	obj['fCheckSum'] = buf.ntou4()
	obj['fClassVersion'] = buf.ntou4()
	obj['fElements'] = buf.ReadObjectAny()
	


def TNamed_TObject( buf, obj ) :
	logging.getLogger( "CustomStreamers.TNamed_TObject" ).debug( "( buf=%s, obj=%s )", buf, obj )
	if '_typename' not in obj :
		obj['_typename'] = "TNamed"
	
	buf.ClassStreamer(obj, "TObject")

def TNamed_fName( buf, obj ) :
	logging.getLogger( "CustomStreamers.TNamed_fName" ).debug( "( buf=%s, obj=%s )", buf, obj )
	obj['fName'] = buf.ReadTString()
def TNamed_fTitle( buf, obj ) :
	logging.getLogger( "CustomStreamers.TNamed_fTitle" ).debug( "( buf=%s, obj=%s )", buf, obj )
	obj['fTitle'] = buf.ReadTString()

def TObjArray( buf, obj ) :
	logging.getLogger( "CustomStreamers.TObjArray" ).debug( "( buf=%s, obj=%s )", buf, obj )
	if '_typename' not in obj :
		obj['_typename'] = "TObjArray"
	obj['name'] = ""
	ver = buf.last_read_version
	if ver > 2 :
		buf.ClassStreamer(obj, "TObject")
	if ver > 1 :
		obj['name'] = buf.ReadTString()
	n_objects = buf.ntou4()
	obj['arr'] = [None] * n_objects
	obj['fLast'] = n_objects - 1
	obj['fLowerBound'] = buf.ntou4()
	i = 0
	while i < n_objects :
		obj[ 'arr' ][ i ] = buf.ReadObjectAny()
		i += 1

def TStreamerBase( buf, obj ) :
	logging.getLogger( "CustomStreamers.TStreamerBase" ).debug( "( buf=%s, obj=%s )", buf, obj )
	logging.getLogger( "CustomStreamers.TStreamerBase" ).debug( "obj=%s", obj )
	ver = buf.last_read_version
	buf.ClassStreamer( obj, "TStreamerElement" )
	if ver > 2 :
		obj['fBaseVersion'] = buf.ntou4()

def TStreamerBasicPointer( buf, obj ) :
	logging.getLogger( "CustomStreamers.TStreamerBasicPointer" ).debug( "( buf=%s, obj=%s )", buf, obj )
	if buf.last_read_version > 1 :
		buf.ClassStreamer( obj, "TStreamerElement" )
		
		obj['fCountVersion'] = buf.ntou4();
		obj['fCountName']    = buf.ReadTString();
		obj['fCountClass']   = buf.ReadTString();


def TStreamerString( buf, obj ) :
	logging.getLogger( "CustomStreamers.TStreamerString" ).debug( "( buf=%s, obj=%s )", buf, obj )
	if buf.last_read_version > 1 :
		buf.ClassStreamer(obj, "TStreamerElement")

def parse_range( val ) :
	if None == val :
		return 0
	if val.find( "pi" ) < 0 :
		return float(val)
	val = val.strip()
	sign = 1
	if "-" == val[0] :
		sign = -1
		val = val[1:]
	m = {
		"2pi" : math.pi * 2,
		"2*pi" : math.pi * 2,
		"twopi" : math.pi * 2,
		"pi/2" : math.pi / 2.0,
		"pi/4" : math.pi / 4.0,
	}
	if val in m :
		return sign * m[val]
	return sign * math.pi

def TStreamerElement( buf, element ) :
	logging.getLogger( "CustomStreamers.TStreamerElement" ).debug( "( buf=%s, obj=%s )", buf, element )
	
	
	ver = buf.last_read_version
	buf.ClassStreamer(element, "TNamed")
	
	element['fType']        = buf.ntou4()
	element['fSize']        = buf.ntou4()
	element['fArrayLength'] = buf.ntou4()
	element['fArrayDim']    = buf.ntou4()
	element['fMaxIndex']    = buf.ReadFastArray(  buf.ntou4() if ver == 1 else 5, IOData.kUInt  )
	element['fTypeName']    = buf.ReadTString()

	# ROOT.ROOT.logger.debug( "TStreamerElement:A( buf=%s, element=%s )", buf, element )

	if (element['fType'] == IOData.kUChar) and ((element['fTypeName'] == "Bool_t") or (element['fTypeName'] == "bool")) :
		element['fType'] = IOData.kBool

		element['fXmin'] = element['fXmax'] = element['fFactor'] = 0
	

	if (ver == 3) :
		element['fXmin'] = buf.ntod()
		element['fXmax'] = buf.ntod()
		element['fFactor'] = buf.ntod()
		# ROOT.ROOT.logger.debug( "TStreamerElement:B( buf=%s, element=%s )", buf, element )
	elif (ver > 3) and (element['fBits'] & BIT(6)) : # kHasRange

		p1 = element['fTitle'].find("[");
		if p1 >= 0 and element['fType'] > IOData.kOffsetP :
			p1 = element['fTitle'].find( "[", p1+1 )
		
		p2 = element['fTitle'].find("]", p1+1);

		logging.getLogger( "CustomStreamers.TStreamerElement" ).debug( "(p1=%d, p2=%d)", p1, p2 )
		if p1>=0 and p2 >= p1+2 :
			arr = ROOT.ParseAsArray( element['fTitle'][ p1: p2-p1+1 ] )
			nbit = 32

			if length( arr ) == 3 :
				nbits = int(arr[2])
			if isNAN(nbits) or nbits < 2 or nbits > 32 :
				nbits = 32

			element['fXmin'] = parse_range( arr[0] )
			element['fXmax'] = parse_range( arr[1] )

			bigint = (1<<nbits) if (nbits < 32) else 0xffffffff
			
			if element['fXmin'] < element['fXmax'] :
				element['fFactor'] = bigint / (element['fXmax'] - element['fXmin'])
			elif nbits<15 : 
				element['fXmin'] = nbits;
	# ROOT.ROOT.logger.debug( "TStreamerElement:END( buf=%s, element=%s )", buf, element )
	# ROOT.ROOT.logger.debug( "Element = \n %s ", json.dumps(element, indent=4) )

def TStreamerObject( buf, obj ) :
	logging.getLogger( "CustomStreamers.TStreamerObject" ).debug( "( buf=%s, obj=%s )", buf, obj )
	if buf.last_read_version > 1 :
		buf.ClassStreamer( obj, "TStreamerElement")
def TStreamerSTL( buf, obj ) :
	buf.ClassStreamer( obj, "TStreamerElement" )
	obj['fSTLtype'] = buf.ntou4()
	obj['fCtype'] = buf.ntou4()

	# if I believe the original source, these are not typos
	if IOData.kSTLmultimap == obj['fSTLtype'] and (obj['fTypeName'].find( "set" ) == 0 or obj['fTypeName'].find( "std::set" ) == 0 ) :
		obj['fSTLtype'] = IOData.kSTLset
	if IOData.kSTLset == obj['fSTLtype'] and (obj['fTypeName'].find( "multimap" ) == 0 or obj['fTypeName'].find( "std::multimap" ) == 0 ) :
		obj['fSTLtype'] = IOData.kSTLmultimap


def TObjString_TObject( buf, obj ) :
	try :
		a = obj['_typename']
	except KeyError as ke :
		obj['_typename'] = 'TObjString'
	buf.ClassStreamer( obj, 'TObject' )
def TObjString_fString( buf, obj ) :
	obj['fString'] = buf.ReadTString()

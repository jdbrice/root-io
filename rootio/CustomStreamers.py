
import rootio.ROOT
import math
import json

def TList( buf, obj ) :
	ROOT.ROOT.getLogger("CustomStreamers.TList").debug( "TList( buf=%s, obj=%s )", buf, obj )
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
		
		ROOT.ROOT.logger.debug( "TList length=%d", nobjects )
		for i in range( 0, nobjects ) :
			ROOT.ROOT.logger.debug( "Reading object %d", i )
			obj['arr'][i] = buf.ReadObjectAny();
			obj['opt'][i] = buf.ReadTString();
	
	else :
		obj['name'] = "";
		obj['arr'] = [];
		obj['opt'] = [];
	ROOT.ROOT.logger.debug( "TList result ( buf=%s, obj=%s )", buf, obj )


def TObject( buf, obj ) :
	ROOT.ROOT.getLogger( "CustomStreamers.TObject" ).debug( "( buf=%s, obj=%s )", buf, obj )
	obj['fUniqueID'] = buf.ntou4()
	obj['fBits'] = buf.ntou4()
	if ( obj[ 'fBits' ] & ROOT.ROOT.IO.kIsReferenced) :
		buf.ntou2()
	ROOT.ROOT.logger.debug( "TObject( buf=%s, obj=%s )", buf, obj )


def TStreamerInfo( buf, obj ) :
	ROOT.ROOT.getLogger( "CustomStreamers.TStreamerInfo" ).debug( "( buf=%s, obj=%s )", buf, obj )
	buf.ClassStreamer( obj, "TNamed" )
	obj['fCheckSum'] = buf.ntou4()
	obj['fClassVersion'] = buf.ntou4()
	obj['fElements'] = buf.ReadObjectAny()
	


def TNamed_TObject( buf, obj ) :
	ROOT.ROOT.getLogger( "CustomStreamers.TNamed_TObject" ).debug( "( buf=%s, obj=%s )", buf, obj )
	if '_typename' not in obj :
		obj['_typename'] = "TNamed"
	
	buf.ClassStreamer(obj, "TObject")

def TNamed_fName( buf, obj ) :
	ROOT.ROOT.getLogger( "CustomStreamers.TNamed_fName" ).debug( "( buf=%s, obj=%s )", buf, obj )
	obj['fName'] = buf.ReadTString()
def TNamed_fTitle( buf, obj ) :
	ROOT.ROOT.getLogger( "CustomStreamers.TNamed_fTitle" ).debug( "( buf=%s, obj=%s )", buf, obj )
	obj['fTitle'] = buf.ReadTString()

def TObjArray( buf, obj ) :
	ROOT.ROOT.getLogger( "CustomStreamers.TObjArray" ).debug( "( buf=%s, obj=%s )", buf, obj )
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
	ROOT.ROOT.getLogger( "CustomStreamers.TStreamerBase" ).debug( "( buf=%s, obj=%s )", buf, obj )
	ROOT.ROOT.logger.debug( "obj=%s", obj )
	ver = buf.last_read_version
	buf.ClassStreamer( obj, "TStreamerElement" )
	if ver > 2 :
		obj['fBaseVersion'] = buf.ntou4()

def TStreamerBasicPointer( buf, obj ) :
	ROOT.ROOT.getLogger( "CustomStreamers.TStreamerBasicPointer" ).debug( "( buf=%s, obj=%s )", buf, obj )
	if buf.last_read_version > 1 :
		buf.ClassStreamer( obj, "TStreamerElement" )
		
		obj['fCountVersion'] = buf.ntou4();
		obj['fCountName']    = buf.ReadTString();
		obj['fCountClass']   = buf.ReadTString();


def TStreamerString( buf, obj ) :
	ROOT.ROOT.getLogger( "CustomStreamers.TStreamerString" ).debug( "( buf=%s, obj=%s )", buf, obj )
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
	ROOT.ROOT.getLogger( "CustomStreamers.TStreamerElement" ).debug( "( buf=%s, obj=%s )", buf, element )
	
	
	ver = buf.last_read_version
	buf.ClassStreamer(element, "TNamed")
	
	element['fType']        = buf.ntou4()
	element['fSize']        = buf.ntou4()
	element['fArrayLength'] = buf.ntou4()
	element['fArrayDim']    = buf.ntou4()
	element['fMaxIndex']    = buf.ReadFastArray(  buf.ntou4() if ver == 1 else 5, ROOT.ROOT.IO.kUInt  )
	element['fTypeName']    = buf.ReadTString()

	# ROOT.ROOT.logger.debug( "TStreamerElement:A( buf=%s, element=%s )", buf, element )

	if (element['fType'] == ROOT.ROOT.IO.kUChar) and ((element['fTypeName'] == "Bool_t") or (element['fTypeName'] == "bool")) :
		element['fType'] = ROOT.ROOT.IO.kBool

		element['fXmin'] = element['fXmax'] = element['fFactor'] = 0
	

	if (ver == 3) :
		element['fXmin'] = buf.ntod()
		element['fXmax'] = buf.ntod()
		element['fFactor'] = buf.ntod()
		# ROOT.ROOT.logger.debug( "TStreamerElement:B( buf=%s, element=%s )", buf, element )
	elif (ver > 3) and (element['fBits'] & ROOT.BIT(6)) : # kHasRange

		p1 = element['fTitle'].find("[");
		if p1 >= 0 and element['fType'] > ROOT.IO.kOffsetP :
			p1 = element['fTitle'].find( "[", p1+1 )
		
		p2 = element['fTitle'].find("]", p1+1);

		ROOT.ROOT.logger.debug( "(p1=%d, p2=%d)", p1, p2 )
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
	ROOT.ROOT.getLogger( "CustomStreamers.TStreamerObject" ).debug( "( buf=%s, obj=%s )", buf, obj )
	if buf.last_read_version > 1 :
		buf.ClassStreamer( obj, "TStreamerElement")
def TStreamerSTL( buf, obj ) :
	buf.ClassStreamer( obj, "TStreamerElement" )
	obj['fSTLtype'] = buf.ntou4()
	obj['fCtype'] = buf.ntou4()

	# if I believe the original source, these are not typos
	if ROOT.ROOT.IO.kSTLmultimap == obj['fSTLtype'] and (obj['fTypeName'].find( "set" ) == 0 or obj['fTypeName'].find( "std::set" ) == 0 ) :
		obj['fSTLtype'] = ROOT.ROOT.IO.kSTLset
	if ROOT.ROOT.IO.kSTLset == obj['fSTLtype'] and (obj['fTypeName'].find( "multimap" ) == 0 or obj['fTypeName'].find( "std::multimap" ) == 0 ) :
		obj['fSTLtype'] = ROOT.ROOT.IO.kSTLmultimap


def TObjString_TObject( buf, obj ) :
	try :
		a = obj['_typename']
	except KeyError as ke :
		obj['_typename'] = 'TObjString'
	buf.ClassStreamer( obj, 'TObject' )
def TObjString_fString( buf, obj ) :
	obj['fString'] = buf.ReadTString()


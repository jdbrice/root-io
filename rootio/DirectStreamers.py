
import ROOT
# from pdb import set_trace as bp


def TKey( buf, key ) :
	ROOT.ROOT.getLogger("DirectStreamers.TKey").debug( "( buf=%s, obj=%s )", buf, key )
	key['fNbytes']  = buf.ntoi4()
	key['fVersion'] = buf.ntoi2()
	key['fObjlen']  = buf.ntou4()
	key['fDatime']  = buf.ClassStreamer({}, 'TDatime')
	key['fKeylen']  = buf.ntou2()
	key['fCycle']   = buf.ntou2()
	if key['fVersion'] > 1000 :
		key['fSeekKey'] = buf.ntou8()
		buf.shift(8); # skip seekPdir
	else :
		key['fSeekKey'] = buf.ntou4()
		buf.shift(4); # skip seekPdir
	key['fClassName'] = buf.ReadTString()
	key['fName']  = buf.ReadTString()
	key['fTitle'] = buf.ReadTString()

	ROOT.ROOT.logger.debug( "TKey( buf=%s, key=%s )", buf, key )

def TDatime( buf, key ) :
	ROOT.ROOT.getLogger("DirectStreamers.TDatime").debug( "( buf=%s, obj=%s )", buf, key )
	key['fDatime'] = buf.ntou4()
	ROOT.ROOT.getLogger("DirectStreamers.TDatime").debug( "AFTER( buf=%s, obj=%s )", buf, key )

def TDirectory( buf, obj ) :
	ROOT.ROOT.getLogger("DirectStreamers.TDirectory").debug( "( buf=%s, obj=%s )", buf, obj )
	
	version            = buf.ntou2()
	obj['fDatimeC']    = buf.ClassStreamer({}, 'TDatime')
	obj['fDatimeM']    = buf.ClassStreamer({}, 'TDatime')
	obj['fNbytesKeys'] = buf.ntou4()
	obj['fNbytesName'] = buf.ntou4()
	obj['fSeekDir']    = buf.ntou8() if version > 1000 else buf.ntou4()
	obj['fSeekParent'] = buf.ntou8() if version > 1000 else buf.ntou4()
	obj['fSeekKeys']   = buf.ntou8() if version > 1000 else buf.ntou4()

	ROOT.ROOT.getLogger("DirectStreamers.TDirectory").debug( "( buf=%s, obj=%s )", buf, obj )

	
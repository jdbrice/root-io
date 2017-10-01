import logging
import matplotlib.pyplot as plt
import numpy as np
import copy

class Histogram(object) :

	def __init__(self, hist_obj=None) :
		self.logger = logging.getLogger( "rootio.TFile" )
		
		# disctionary of edges for axes
		self.edges = {}
		self.centers = {}
		self.widths = {}
		self.n_bins = {}
		self.mean = {}
		# nd array of values
		self.vals = None
		
		if None  != hist_obj :
			self.build( hist_obj )
	
	def clone(self) :
		nh = Histogram()
		nh.edges = copy.deepcopy( self.edges )
		nh.centers = copy.deepcopy( self.centers )
		nh.widths = copy.deepcopy( self.widths )
		nh.n_bins = copy.deepcopy( self.n_bins )
		nh.mean = copy.deepcopy( self.mean )
		nh.vals = copy.deepcopy( self.vals )
		nh.n_dim = self.n_dim

		return nh
	def __add__(self, other) :
		# now assume binning is the same!
		if self.vals.shape == other.vals.shape :
			nh = self.clone()

			for i in np.arange( 0, len(self.vals) ) :
				nh.vals[i] = self.vals[i]+other.vals[i]
			return nh
		return None

	@staticmethod
	def add( a, b, scale_a=1.0, scale_b=1.0 ) :
		ac = a.clone()
		bc = b.clone()
		ac.scale(scale_a)
		bc.scale(scale_b)
		nh = ac+bc
		return nh


	def scale(self, factor=1.0) :
		self.vals = self.vals * factor

	def build( self, root_hist_obj ) :
		# make the edges first
		for axis in ["x", "y", "z" ] : 
			self.make_axis( root_hist_obj, axis=axis )
		self.n_dim = sum( len(self.edges[k]) > 1 for k in self.edges )
		self.calc_ndarray( root_hist_obj )

		for axis in ["x", "y", "z" ] : 
			self.mean[axis] = self.make_mean( axis = axis )


	def make_axis( self, h_obj, **kwargs ) :
		axis = kwargs.get( "axis", "x" )
		self.edges[axis] = self.make_edges( h_obj, axis=axis )
		self.centers[axis] = self.make_centers( axis=axis )
		self.widths[axis] = self.make_widths( axis=axis )
		self.n_bins[axis] = len( self.centers[axis] )

	def make_edges(self, h_obj, **kwargs) :
		axis = kwargs.get( "axis", "x" )

		bin_edges = np.array([])
		nbins = 0
		bmin = 0
		bmax = 0
		try :
			nbins = h_obj[ 'f' + axis.upper() + "axis" ]["fNbins"] 
			bmin = h_obj[ 'f' + axis.upper() + "axis" ]["fXmin"]
			bmax = h_obj[ 'f' + axis.upper() + "axis" ]["fXmax"]
			bins = h_obj[ 'f' + axis.upper() + "axis" ]["fXbins"]
		except KeyError as ke :
			pass

		if len(bins) <= 1 :
			if 1 == nbins : 
				return np.array([])
			bin_edges = np.zeros( nbins+1 )
			bw = (bmax - bmin) / nbins
			self.logger.debug("n=%d, (%f, %f), w=%f", nbins, bmin, bmax, bw )
			for i in np.arange( 0, nbins ) : 
				bin_edges[ i ] = bw * i + bmin

			bin_edges[ nbins ] = bmax
			return bin_edges
		return np.array(bins)

	def get_edges( self, **kwargs ) :
		axis = kwargs.get( "axis", "x" )
		place = kwargs.get( "place", "left" )
		
		if "right" == place :
			return self.edges[axis][1:]
		if "center" == place :
			return self.centers[axis];

		return self.edges[axis][:-1]

	def make_mean( self, **kwargs ) :
		axis = kwargs.get( "axis", "x" )
		if 1 == self.n_dim and 'x' == axis:
			nsum = 0
			n = 0;
			for c, v in zip( self.centers[axis], self.vals ) :
				n = n + v
				nsum = nsum + c * v
			return float( nsum ) / float(n)


		
	def make_centers( self, **kwargs ) :
		axis = kwargs.get( "axis", "x" )

		#  may throw a KeyError if not found
		bins = self.edges[ axis ]
		if len(bins) < 2 :
			return np.array([])

		bc = np.empty( shape=(len(bins)-1) )

		for i in np.arange( 0, len(bins)-1 ) :
			x1 = bins[i]
			x2 = bins[i+1]
			bc[i] = (x1 + x2) / 2.0

		return bc

	def make_widths( self, **kwargs ) :
		axis = kwargs.get( "axis", "x" )

		bins = self.edges[axis]
		if len(bins) < 2 :
			return np.array([])
		
		bw = np.empty( shape=(len(bins)-1) )
		for i in np.arange( 0, len(bins)-1 ) :
			x1 = bins[i]
			x2 = bins[i+1]
			bw[i] = (x2 - x1)
		return bw

	def calc_ndarray(self, root_hist_obj) :

		if 1 == self.n_dim :
			self.vals = np.empty( shape=(self.n_bins['x']) )
			for x in np.arange( 0, self.n_bins['x'] ) :
				self.vals[x] = self.value_at_index( root_hist_obj ,x+1 )

		if 2 == self.n_dim :
			self.vals = np.empty( shape=(self.n_bins['y'], self.n_bins['x']) )

			for x in np.arange( 0, self.n_bins['x'] ) :
				for y in np.arange( 0, self.n_bins['y'] ) :
					self.vals[y][x] = self.value_at_index( root_hist_obj ,x+1, y+1 )

	def value_at_index( self, h_obj, x, y = None, z = None, **kwargs ) :
		values = h_obj[ 'fArray' ]
		
		if 1 == self.n_dim or None == y :
			return values[x]
		
		if 2 == self.n_dim and None != x and None != y:
			w = self.n_bins["x"] + 2
			h = self.n_bins["y"] + 2

			return values[ x + y * w ]

		return None


	def draw_1d(self, scale=1.0, **kwargs) :
		use_bins = kwargs.get( 'bins', self.edges['x'] )
		kwargs.pop( 'bins', None )
		plt.hist( self.centers['x'], bins=use_bins, weights=self.vals*scale, **kwargs )

	def draw_2d( self, **kwargs ) :
		x_bins = self.centers['x']
		y_bins = self.centers['y']

		vx = np.empty( shape=( len(x_bins) * len(y_bins) ) )
		vy = np.empty( shape=( len(x_bins) * len(y_bins) ) )
		vw = np.empty( shape=( len(x_bins) * len(y_bins) ) )

		i = 0
		ix = 0
		iy = 0
		for x in x_bins :
			iy = 0
			for y in y_bins :
				vx[i] = x
				vy[i] = y
				vw[i] = self.vals[iy][ix] #self.value_at_index( ix + 1, iy + 1 )
				if 0 == vw[i] :
					vw[i] = float('nan')
				i = i + 1

				iy = iy + 1

			ix = ix + 1

		return plt.hist2d( vx, vy, weights=vw, bins=[x_bins, y_bins], **kwargs )


	# def __getitem__(self, key):
	# 	return self.__getattribute__(key)

	def draw(self, scale=1.0, **kwargs) :
		if 1 == self.n_dim : 
			return self.draw_1d(scale=scale, **kwargs)

		if 2 == self.n_dim : 
			return self.draw_2d(**kwargs)

		if 3 == self.n_dim : 
			return self.draw_3d(**kwargs)



		
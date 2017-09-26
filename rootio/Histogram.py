import logging
import matplotlib.pyplot as plt
import numpy as np

class Histogram(object) :

	def __init__(self, hist_obj) :
		self.logger = logging.getLogger( "rootio.TFile" )
		self.raw_hist = hist_obj
		self.n_dim = self.calc_n_dim()
		
		try :
			self.values = np.array( self.raw_hist['fArray'] )
		except KeyError as ke :
			pass

		self.calc_ndarray()


	def calc_n_dim(self) :
		nd = 0;
		if None == self.raw_hist :
			return nd
		try :
			self.logger.info( 'xBins: %d, yBins:%d, zBins:%d', self.raw_hist['fXaxis']['fNbins'][0], self.raw_hist['fYaxis']['fNbins'][0], self.raw_hist['fZaxis']['fNbins'][0]  )
			
			self.n_bins_x = self.raw_hist['fXaxis']['fNbins'][0]
			self.n_bins_y = self.raw_hist['fYaxis']['fNbins'][0]
			self.n_bins_z = self.raw_hist['fZaxis']['fNbins'][0]

			if self.raw_hist['fXaxis']['fNbins'][0] > 1 :
				nd = nd + 1
			
			if self.raw_hist['fYaxis']['fNbins'][0] > 1 :
				nd = nd + 1
			
			if self.raw_hist['fZaxis']['fNbins'][0] > 1 :
				nd = nd + 1

		except KeyError as ke :
			print "Histogram should have axes", ke

		return nd

	def edges( self, **kwargs ) :
		axis = kwargs.get( "axis", "x" )
		side = kwargs.get( "side", "left" )

		try :
			bins = self.raw_hist[ 'f' + axis.upper() + "axis" ]["fXbins"]
		except KeyError as ke :
			return np.array([])
			
		if "right" == side :
			return np.array( bins[1:] )
		
		return np.array( bins[:-1] )

	def centers( self, **kwargs ) :
		axis = kwargs.get( "axis", "x" )

		try :
			bins = self.raw_hist[ 'f' + axis.upper() + "axis" ]["fXbins"]
		except KeyError as ke :
			return np.array([])

		bc = np.empty( shape=(len(bins)-1) )
		for i in np.arange( 0, len(bins)-1 ) :
			x1 = bins[i]
			x2 = bins[i+1]
			bc[i] = (x1 + x2) / 2.0
		return bc

	def widths( self, **kwargs ) :
		axis = kwargs.get( "axis", "x" )

		try :
			bins = self.raw_hist[ 'f' + axis.upper() + "axis" ]["fXbins"]
		except KeyError as ke :
			return np.array([])

		bw = np.empty( shape=(len(bins)-1) )
		for i in np.arange( 0, len(bins)-1 ) :
			x1 = bins[i]
			x2 = bins[i+1]
			bw[i] = (x2 - x1)
		return bw

	def calc_ndarray(self) :

		if 1 == self.n_dim :
			self.ndv = np.empty( shape=(self.n_bins_x) )
			for x in np.arange( 0, self.n_bins_x ) :
				self.ndv[x] = self.value_at_index( x+1 )

		if 2 == self.n_dim :
			self.ndv = np.empty( shape=(self.n_bins_y, self.n_bins_x) )

			for x in np.arange( 0, self.n_bins_x ) :
				for y in np.arange( 0, self.n_bins_y ) :
					self.ndv[y][x] = self.value_at_index( x+1, y+1 )

	def value_at_index( self, x, y = None, z = None, **kwargs ) :
		if 1 == self.n_dim or None == y :
			return self.values[x]
		
		if 2 == self.n_dim and None != x and None != y:
			w = len(self.edges( axis="x" )) + 2
			h = len(self.edges( axis="y" )) + 2

			return self.values[ x + y * w ]

		return None


	def draw_1d(self, **kwargs) :
		plt.bar( self.edges(), self.raw_hist['fArray'][1:-1], self.widths(), **kwargs )

	def draw_2d( self, **kwargs ) :
		x_bins = self.centers(axis="x")
		y_bins = self.centers(axis="y")

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
				vw[i] = self.value_at_index( ix + 1, iy + 1 )
				if 0 == vw[i] :
					vw[i] = float('nan')
				i = i + 1

				iy = iy + 1

			ix = ix + 1

		return plt.hist2d( vx, vy, weights=vw, bins=[x_bins, y_bins], **kwargs )


	# def __getitem__(self, key):
	# 	return self.__getattribute__(key)

	def draw(self, **kwargs) :
		if 1 == self.n_dim : 
			return self.draw_1d(**kwargs)

		if 2 == self.n_dim : 
			return self.draw_2d(**kwargs)

		if 3 == self.n_dim : 
			return self.draw_3d(**kwargs)



		
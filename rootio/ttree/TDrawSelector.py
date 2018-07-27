from rootio.ttree.TSelector import TSelector
from rootio.ttree.TDrawVariable import TDrawVariable
import logging

class TDrawSelector(TSelector):
    def __init__(self):
        self.logger = logging.getLogger("TDrawSelector")
        self.ndim = 0
        self.vars = []  # array of expression variables
        self.cut = null # cut variable
        self.hist = null
        self.histo_callback = callback
        self.histo_drawopt = ""
        self.hist_name = "$htemp"
        self.hist_title = "Result of TTree::Draw"
        self.hist_args = [] # arguments for histogram creation
        self.arr_limit = 1000  # number of accumulated items before create histogram
        self.htype = "F"
        self.monitoring = 0
        self.globals = {} # object with global parameters, which could be used in any draw expression
        self.last_progress = 0
        self.aver_diff = 0

    def draw_only_branch(self, tree, branch, expr, args):
        self.ndim=1;
        if 0==expr.find("dump"):
            expr = ":" + expr
        
        
        expr = self.parse_parameters( tree, args, expr)
        try :
            self.monitoring = args.monitoring
        except:
            pass

        if "dump" in args:
            self.dump_values = True;
            args.reallocate_objects = True;
        
        if True == self.dump_values:
            self.hist = []
            self.leaf = args['leaf']
            self.copy_fields = False
            try:
                if None != args.branch.fLeaves and len(args.branch.fLeaves.arr) > 1 and 'leaf' not in args:
                    self.copy_fields = True
                if None != args.branch.fBranches and len(args.branch.fBranches.arr) > 0 and 'leaf' not in args:
                    self.copy_fields = True
            except:
                pass

            self.add_branch( branch, "br0", args.direct_branch )

            self.process_action = "dump"
            return True
        
        print("DONT GET HERE")
        self.vars.append( TDrawVariable(self.globals) )
        if False == self.vars[0].parse( tree, self, expr, branch, args.direct_branch ) :
            return False
        self.hist_title = "drawing branch '" + branch.fName + (expr ? "' expr:'" + expr : "") + "'  from " + tree['fName'];
        self.cut = TDrawVariable( self.globals )
        return True

    def parse_parameters( self, tree, args, expr ):
        if None == expr or str != type(expr):
            return ""
        pos = expr.rfind(";")
        while pos >= 0:
            parname = expr[pos+1:]
            expr = expr[0:pos]
            pos = expr.rfind( ";" )

            separ = parname.find(":")
            if separ>0:
                parvalue = parname[separ+1:]
                parname = parname[0:separ]
            
            if "dump" == parname :
                args.dump = True

        return expr

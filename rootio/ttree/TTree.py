
from box import Box

class TTree(object):

    def __init__(self):
        pass
    
    def draw(self, args):
        if str == type(args):
            args = { "expr" : args }
            args = Box(args)
            
        if "expr" not in args or None == args['expr']:
            args['expr'] = ""

        selector = TDrawSelector()

        if "branch" in args:
            if False == selector.draw_only_branch(self, args.branch, args.expr, args):
                selector = None
        else :
            pass
        
        if None == selector:
            self.logger.error("BAD, no selector" )
            return
    
        return self.Process(selector, args)


    
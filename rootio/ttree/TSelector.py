



class TSelector(object) :
    def __init__(self) :
        
        self.branches = [] # list of branches to read
        self.names = []    # list of member names for each branch in tgtobj
        self.directs = [] # indication if only branch without any children should be read
        self.break_execution = 0
        self.tgtobj = {}
    
    def add_branch(self, branch, name, direct):
        if None == name:
            if str == type(branch):
                name = branch
            else:
                name = "br" + str( len(self.branches) )
      self.branches.append(branch);
      self.names.append(name);
      self.directs.append(direct);
      return len(self.branches)-1;

    def index_ob_branch(self, branch):
        return self.branches.index( branch )
    def name_of_branch(self, index):
        return self.names[index]
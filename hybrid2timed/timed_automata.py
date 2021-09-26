import hybrid_automata

def construct_ta(ha):
    initial_mode={}
    initial_mode["name"]=ha.initial_mode["name"]
    initial_mode["inv"]=ha.calculate_max(ha.initial_mode)
    timed_mode_set=[]
    timed_transition_set=[]
    
    for mode in ha.mode_set:
        m={}
        m["inv"]=ha.calculate_max(mode)
        m["name"]=mode["name"]
        timed_mode_set.append(m)
    
    for mode in ha.mode_set:
        for outgo in mode["outgoings"]:
            t={}
            t["guard"]=ha.calculate_min(mode, outgo)
            t["name"]=outgo["name"]
            t["event"]=outgo["event"]
            t["source"]=mode 
            t["desti"]=next(item for item in timed_mode_set if item["name"] == outgo["desti"]["name"])
            timed_transition_set.append(t)
    return initial_mode, timed_mode_set, timed_transition_set

class TimedAutomata:

    def _init_(self, ha):
        self.initial_mode, self.mode_set, self.transition_set=construct_ta(ha)
        self.ha=ha
    
    def update_modes(self):
        for mode in self.mode_set:
            mode["incomings"]=[]
            mode["outgoings"]=[]
            for tr in self.transition_set:
                if tr["source"]==mode:
                    mode["outgoings"].append(tr)
                if tr["desti"]==mode:
                    mode["incomings"].append(tr)
    
    def verify_dia(self):
        """ 
        call smt diganosability checker by passing the current ta
        if smt returns false (diagnosable)  
        if smt returns a model (critical pair), then check the 
        existence of this critical pair in hybrid automaton 
        by calling its function verify_trace two times
        """

        pass
    

    def refine_ta(self, pairs):
        pass


# main function:
# 1: from hybrid automaton to timed automaton by calling initialization
# 2: call smt diagnosability for the current timed automaton:
#    if return true, then done (diagnosable)
#    if return critical pair, check this critical pair in hybrid level:
#       if true, then done (not diagnosable)
#       if false, cut the corresponding mode in hybrid automaton 
#       by the returned step information before updating its timed automaton, 
#       then repeat step 2 until obtaining the final verdict
 
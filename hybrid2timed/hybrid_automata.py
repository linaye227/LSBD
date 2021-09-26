#import DiffEqua as DE
from continuous import DiffEquaTmt
from continuous import Interval
import math
 

class HybridAutomata: 
    '''
    a hybrid automaton has the following attributes:
    conti_var_set: a set of continuous variables
    initial_mode: the inital mode
    mode_set: a set of modes, each one is a dictionary with 
    the keys name, des(differential equation set), inv, incomings, outgoings
    transition_set: a set of transitions, each one is a dic with 
    the keys (name?), source, guard, event, reset, desti
    initial_value: the initial value
    '''
    def __init__(self, conti_var_set, initial_mode, mode_set, transition_set, initial_value):
        self.conti_var_set=conti_var_set  
        self.initial_mode=initial_mode
        self.mode_set=mode_set  
        self.transition_set=transition_set  
        self.initial_value=initial_value

    def update_modes(self):
        '''
        update the set of incoming transitions and 
        the set of outgoing transitions for all modes 
        in the current hybrid automaton
        '''
        for mode in self.mode_set:
            mode["incomings"]=[]
            mode["outgoings"]=[]
            for tr in self.transition_set:
                if tr["source"]==mode:
                    mode["outgoings"].append(tr)
                if tr["desti"]==mode:
                    mode["incomings"].append(tr)
    
    def calculate_max(self, mode):
        '''
        calculate the maximum time for a given mode
        '''
        income_itvs=[]
        outgo_itvs=[]

        for tr in mode["incomings"]:
            income_itvs.append(tr["guard"])
        for tr in mode["outgoings"]:
            outgo_itvs.append(tr["guard"])

        max_time=math.inf
        for de in mode["des"]:
            max_time=min(max_time, de.calculate_max(income_itvs, mode["inv"], outgo_itvs))
        
        return max_time
    
    def calculate_min(self, mode, tr):
        '''
        calculate the miminum time for a given mode and a 
        given outgoing transition from this mode
        '''
        min_time=math.inf
        income_itvs=[]

        for t in mode["incomings"]:
            income_itvs.append(t["guard"])

        for de in mode["des"]:
            min_time_temp=de.calculate_min(income_itvs, mode["inv"], tr["guard"])
            if min_time>min_time_temp:
                min_time=min_time_temp

        return min_time

    def check_conti_transition(self, step):
        '''
        if the intersection of source value interval (or destination 
        value interval) and invariant of the mode is empty then return step, 
        which is the one that should be analysed for refinement.
        '''
        if not step["source"][1].intersec(step["source"][0]["inv"]): #import inverval?
            return step
        if not step["desti"][1].intersec(step["desti"][0]["inv"]):
            return step
        return True

    def check_discrete_transition(self, step):
        ''' 
        if one of the two conditions are satisfied: 
           1) the intersection of source value interval and the guard of 
        the corresponding transition is empty, or 
           2) the intersection of destination value interval and 
        invariant of the destination mode is empty

        then return step, which is the one that 
        should be analysed for refinement. 
        '''
        if not step["source"][1].intersec(step["trans"]["guard"]):
            return step
        if not step["desti"][1].intersec(step["desti"][0]["inv"]):
            return step
        return True


    def time2hybrid_trace(self, time_trace):
        '''
        transfer a timed trace to hybrid trace beginning from 
        initial value interval
        '''
        hybrid_trace=[]
        source_itv=self.initial_value
        for step in time_trace:
            step_temp={}
            if step["type"]=="conti":
                step_temp["type"]="conti"
                mode_temp=next(item for item in self.mode_set if item["name"] == step["source"][0]["name"]) 
                step_temp["source"]=[mode_temp, source_itv]
                desti_itv=step["source"][0]["des"][0].simul_itv(source_itv, step["time"])
                step_temp["time"]=step["time"]
                step_temp["desti"]=[mode_temp, desti_itv]
                source_itv=desti_itv
                hybrid_trace.append(step_temp)

            else:
                step_temp["type"]="discrete"
                mode_temp=next(item for item in self.mode_set if item["name"] == step["source"][0]["name"]) 
                step_temp["source"]=[mode_temp, source_itv]
                hybrid_tr=next(item for item in self.transition_set if item["source"]["name"] == step["source"][0]["name"] and item["desti"]["name"] == step["desti"][0]["name"])
                step_temp["trans"]=hybrid_tr
                desti_itv=source_itv if hybrid_tr["reset"]==False else hybrid_tr["reset"]
                mode_temp1=next(item for item in self.mode_set if item["name"] == step["desti"][0]["name"])
                step_temp["desti"]=[mode_temp1, desti_itv]
                source_itv=desti_itv
                hybrid_trace.append(step_temp)
  
        return hybrid_trace


    def verify_trace(self, time_trace): 
        '''
        after transforming timed trace into hybrid trace, 
        which is a list of either timed transitions or discrete ones,
        check the possibility of each transition in hybrid model.
        If all transitions can exist in hybrid level, return true.
        Otherwise, return the pair of mode and valuation interval that 
        is the most appropriate to explain why the given timed trace 
        does not correpsond to any real hybrid trace.   
        '''
        hybrid_trace=self.time2hybrid_trace(time_trace)
        for step in hybrid_trace:
            if  step["type"]=="conti":
                res=self.check_conti_transition(step)
                if res!=True:
                    return res
            if  step["type"]=="discrete":
                res=self.check_discrete_transition(step)
                if res!=True:
                    return res
        return True


    def compute_max(self, mode, income_itv):
        '''
        compute the maximum time for a given mode and 
        an incoming transition guard 
        '''
        max_time=math.inf
        for de in mode["des"]:
            max_time=min(max_time, de.max_itv(income_itv, mode["inv"]))
        
        return max_time


    def divide_incomes(self, step):
        '''
        Given a step, calculate the subset of 
        valid incoming transitions w.r.t. this step 
        the max time is not bigger than that from source value interval
        '''
        if step["type"]=="conti":
            valid_incomes=[]
            mode=step["source"][0]
            #src_itv=step["source"][1]
            for income_tr in mode["incomings"]:
                if self.compute_max(mode, income_tr["guard"])<=step["time"]:
                    valid_incomes.append(income_tr)
            return valid_incomes, [income for income in mode["incomings"] if income not in valid_incomes]

        if step["type"]=="discrete": #reason: precedent time transition is either too long or too short
            #if too long: 
            #if too short: 
            pass


    def mode_cut_pre(self, mode, values):
        # this function is not needed?
        if values in mode["inv"]:
            new_inc=[]
            new_inv=[]
            for inc in mode["incomings"]:
                for v in values:
                    inv_temp=self.construct_inv(mode["inv"], inc["guard"] and inc["source"]["inv"])
                    if v not in inv_temp:
                        new_inc.append(inc)
                        new_inv.append(inv_temp)
                        break
            return new_inc, new_inv
        else:
            return False


    def find_outgos(mode, inv):
        # this function is not needed?
        # if do not change invariant, not needed
        outgos=[]
        for outgo in mode["outgoings"]:
            if (outgo["guard"].intersec(inv)):
                outgos.append(outgo)
        return outgos
    
    def cut_mode(self, mode, step):

        incomes1, incomes2=self.divide_incomes(step)
        mode1=dict(mode)
        mode1["name"]+="_1"
        mode2=dict(mode)
        mode2["name"]+="_2"

        for inc in incomes1:
            inc.update((k, mode1) for k, v in inc.items() if k=="desti")
        for inc in incomes2:
            inc.update((k, mode2) for k, v in inc.items() if k=="desti")
        mode1["incomings"]=incomes1
        mode2["incomings"]=incomes2

        for outgo in mode1["outgoings"]:
            outgo.update((k, mode1) for k, v in outgo.items() if k=="source")
        for outgo in mode2["outgoings"]:
            outgo.update((k, mode2) for k, v in outgo.items() if k=="source")

        #to do: change the name of each corresponding transition?

        self.mode_set.remove(mode)
        self.mode_set.append(mode1)
        self.mode_set.append(mode2)
        temp_trs_list=mode["incomings"]+mode["outgoings"]
        self.transition_set=[tr for tr in self.transition_set if tr not in temp_trs_list]
        #self.transition_set=list(set(self.transition_set)-set(mode["incomings"])-set(mode["outgoings"]))
        self.transition_set.extend(mode1["incomings"]+mode2["incomings"]+mode1["outgoings"]+mode2["outgoings"]) 

if __name__ == "__main__":
    de1=DiffEquaTmt(-1, 0, 0.5, 0.01, 0, 2)
    de2=DiffEquaTmt(-1, 100, 0.5, 0.01, 0, 1)
    itv1=Interval('[68, 180)')
    itv2=Interval('(0, 82]')
    itv_gd1=Interval('(0, 70]')
    itv_gd2=Interval('[80, 82)')
    initial_value=Interval('[82, 93]')
    mode1={"name":"off", "des":[de1], "inv":itv1}
    mode2={"name":"on", "des":[de2], "inv":itv2}
    conti_var_set=[1,2]
    initial_mode=mode1
    mode_set=[mode1, mode2]
    tr0={"source":"initial", "desti":mode1, "guard":initial_value}
    tr1={"source":mode1, "desti":mode2, "guard":itv_gd1}
    tr2={"source":mode2, "desti":mode1, "guard":itv_gd2}
    transition_set=[tr1, tr2, tr0]
    ha1=HybridAutomata(conti_var_set, initial_mode, mode_set, transition_set, initial_value)
    ha1.update_modes()
    #print(len(mode1["incomings"]))
    stp={"source":[mode1, Interval('(51, 67]')], "time": 0.1, "desti":[mode1, Interval('(59, 78]')]}
    stp_dsc={"source":[mode1, Interval('(61, 78]')], "trans": tr1, "desti":[mode2, Interval('(86, 88]')]}
    #print(ha1.check_conti_transition(stp)["source"][1].str())
    #print(ha1.check_discrete_transition(stp_dsc)["source"][1].str())
    #print(ha1.calculate_max(mode2))
    #print(ha1.calculate_min(mode2, tr2))

    # check function time2hybrid_trace
    time_trace=[]
    step1={"type":"conti", "source":[mode2, 0], "time":0.79, "desti":[mode2, 0.79]}
    time_trace.append(step1)
    #ht=ha1.time2hybrid_trace(time_trace)[0]["desti"][1].str()
    #print(ht)

    # check function divide_incomes
    stepp={"type":"conti", "source":[mode1, Interval('[80, 81]')], "time":0.3, "desti":[mode1, Interval('(60, 63]')]}
    #print(len(ha1.divide_incomes(stepp)[0]))

    #check cut_mode
    print(len(ha1.transition_set))
    print(type(ha1.transition_set))
    #print(len(set(ha1.transition_set)-set(ha1.mode1["incomings"])))
    ha1.cut_mode(mode1, stepp)
    print(len(ha1.transition_set))
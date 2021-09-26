#to do: see https://apmonitor.com/pdc/index.php/Main/SolveDifferentialEquations


import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt

import math

import re
 
class Interval:
    def __init__(self, interval):
        """Initialize an Interval object from a string representation of an interval
           e.g: Interval('(3,4]')"""
        if isinstance(interval, Interval):
        	self.begin, self.end = interval.begin, interval.end
        	self.begin_included = interval.begin_included
        	self.end_included = interval.end_included
        	return
        number_re = '-?[0-9]+(?:.[0-9]+)?'
        interval_re = ('^\s*'
        	           +'(\[|\()'  # opeing brecket
                       + '\s*'
                       + '(' + number_re + ')'  # beginning of the interval
                       + '\s*,\s*'
                       + '(' + number_re + ')'  # end of the interval
                       + '\s*'
                       + '(\]|\))'  # closing brecket
                       + '\s*$'
                      )
        match = re.search(interval_re, interval)
        if match is None:
        	raise ValueError('Got an incorrect string representation of an interval: {!r}'. format(interval))
        opening_brecket, begin, end, closing_brecket = match.groups()
        self.begin, self.end = float(begin), float(end)
        if self.begin >= self.end:
        	raise ValueError("Interval's begin shoud be smaller than it's end")
        self.begin_included = opening_brecket == '['
        self.end_included = closing_brecket == ']'
        # It might have been batter to use number_re = '.*' and catch exeptions float() raises instead
 
    def repr(self):
        return 'Interval({!r})'.format(str(self))
 
    def str(self):
    	opening_breacket = '[' if self.begin_included else '('
    	closing_breacket = ']' if self.end_included else ')'
    	return '{}{}, {}{}'.format(opening_breacket, self.begin, self.end, closing_breacket)
 
    def contains(self, number):
    	if self.begin < number < self.end:
    		return True
    	if number == self.begin:
    		return self.begin_included
    	if number == self.end:
    		return self.end_included
        
    def intersec(self, interval):
        if self.end<interval.begin or interval.end<self.begin:
            return False 
        else:
            return True
    
    def intersec_general(self, intervals1, intervals2):
        for i in range(len(intervals1)):
            if not intervals1[i].intersec(intervals2[i]):
                return False
        return True


    def valid_intersec(self, inv, outgo):
        if not inv.intersec(outgo):
            return "the guard is not included in invariant"
        if outgo.end<=inv.end and outgo.begin>=inv.begin:
            return outgo
        else: 
            if outgo.end>=inv.end:
                #Interval('(3,4]')
                itv=outgo.str()[0]+outgo.begin+', '+inv.end+inv.str()[-1]
                return Interval(itv)
            else:
                itv=inv.str()[0]+inv.begin+', '+outgo.end+outgo.str()[-1]
                return Interval(itv)
    
    def valid_intersec(self, outgo):
        if not self.intersec(outgo):
            return False
        if outgo.end<=self.end and outgo.begin>=self.begin:
            return outgo
        else: 
            if outgo.end>=self.end:
                #Interval('(3,4]')
                itv=outgo.str()[0]+str(outgo.begin)+', '+str(self.end)+self.str()[-1]
                return Interval(itv)
            else:
                itv=self.str()[0]+str(self.begin)+', '+str(outgo.end)+outgo.str()[-1]
                return Interval(itv)


 
 
'''for interval in ('(4,5]', '[-10,4)', '', 'foo', '(foo', '(10]', '()', '(4.0, 5.7]', '[5,-5]'):
    print('Interval(', repr(interval), ') = ')
    try:
        print(repr(Interval(interval)))
    except BaseException as e:
        print(repr(e))
 
for interval in ('(-5, 8)', '[5, 8]', '(5, 8]', '[-3, 5]', '[-3, 5)'):
    interval = Interval(interval)
    print(5, 'in', interval, '=', 5 in interval)
 
 
def foo(interval, bar, baz):
	interval = Interval(interval)
	print(repr(interval))
 
foo('[-1, 5)', 42, True)
foo(Interval('[-1,5)'), 42, True)'''

class DiffEquaTmt: # use odeint
    '''
    diffequa:dy/dt=coeffi*y+ad
    dif: to define approximate equality
    step: time interval for each step
    step_act: the number of steps
    if type 1: increase
    if type 2: decrease
    if type 3: neither of them
    '''
    def __init__(self, coeffi, ad, dif, step, step_act=0, type=3):
        self.coeffi=coeffi
        self.ad=ad
        self.dif=dif
        self.step=step
        self.step_act=step_act
        self.type=type
        

    def model(self, y, t):
        dydt=self.coeffi*y+self.ad
        return dydt

    def simul(self, value_initial, time_itv):
        return odeint(self.model, value_initial, time_itv)

    def simul_itv(self, begin_itv, time):
        bg=self.simul(begin_itv.begin, [0,time])[1][0].astype(float)
        ed=self.simul(begin_itv.end, [0,time])[-1][0].astype(float)
        #print(begin_itv.str()[0])
        new_itv=begin_itv.str()[0]+str(bg)+', '+str(ed)+begin_itv.str()[-1]
        #print('"'+new_itv+'"')
        return Interval(new_itv)

    def close(self, v1, v2):
        return abs(v1-v2)<=self.dif
    
    def simul_time(self, value_initial, value_end):
        time=0
        if self.close(value_initial,value_end):
            return self.step_act*self.step
        else: 
            self.step_act+=1
            value_initial=self.simul(value_initial, [0, time+self.step])[1]
            #value_initial=self.simul(value_initial, [time+self.step, time+self.step*2])[1]
            return self.simul_time(value_initial, value_end)


    def min_itv_general(self, initial_itv, constrt_itv):

        inits = np.linspace(initial_itv.begin,initial_itv.end)
        consts= np.linspace(constrt_itv.begin,constrt_itv.end)
        rst_min=math.inf

        for init in inits:
            for cst in consts:
                self.step_act=0
                rst_min=min(rst_min, self.simul_time(init, cst))

        return rst_min

    def min_itv(self, initial_itv, constrt_itv):
        if initial_itv.intersec(constrt_itv):
            return 0
        if self.type==3:
            return self.min_itv_general(initial_itv, constrt_itv)
        else:
            if self.type==1:
                begin_value=initial_itv.end
                end_value=constrt_itv.begin
            else: 
                if self.type==2:
                    begin_value=initial_itv.begin
                    end_value=constrt_itv.end
                else:
                    return "wrong type"
            self.step_act=0
            return self.simul_time(begin_value, end_value)


    def calculate_min(self, income_itvs, inv, outgo_itv):
        valid_constrt=inv.valid_intersec(outgo_itv)
        print(outgo_itv.str())
        min_time=math.inf
        for inc in income_itvs:
            min_time=min(min_time, self.min_itv(inc, valid_constrt))
        return min_time

    def max_itv_general(self, initial_itv, constrt_itv):
        inits = np.linspace(initial_itv.begin,initial_itv.end)
        consts= np.linspace(constrt_itv.begin,constrt_itv.end)
        rst_max=0

        for init in inits:
            for cst in consts:
                self.step_act=0
                self.simul_time(init, cst)
                rst_max=max(rst_max, self.step_act*self.step)
        return rst_max
    
    def max_itv(self, initial_itv, constrt_itv):

        if initial_itv.begin==initial_itv.end==constrt_itv.begin==constrt_itv.end:
            return 0
        if self.type==3:
            return self.max_itv_general(initial_itv, constrt_itv)
        else:
            if self.type==1:
                begin_value=initial_itv.begin
                end_value=constrt_itv.end
            else: 
                if self.type==2:
                    begin_value=initial_itv.end
                    end_value=constrt_itv.begin
                else:
                    return "wrong type"
            self.step_act=0
            return self.simul_time(begin_value, end_value)

    def infinite_time(self, inv):
        #to do: check if this equation can satify inv forever 
        pass
    
    def calculate_max(self, income_itvs, inv, outgo_itvs):
        valid_constrts=[]
        max_time=0
        for outgo in outgo_itvs:
            valid_cst=inv.valid_intersec(outgo)
            if valid_cst!=False:
                valid_constrts.append(valid_cst)
        for inc in income_itvs:
            for vcs in valid_constrts:
                max_time=max(max_time, self.max_itv(inc, vcs))
        return max_time

if __name__ == "__main__":
    de1=DiffEquaTmt(-1, 0, 0.5, 0.01, 0, 2)
    de2=DiffEquaTmt(-1, 100, 0.5, 0.01, 0, 1)
    itv_income_1=Interval('(60, 69]')
    itv_income_2=Interval('(63, 72]')
    itv_income_3=Interval('(69, 75]')
    itv=[itv_income_1, itv_income_2, itv_income_3]
    itv_outgo_1=Interval('(80, 82]')
    itv_outgo_2=Interval('(78, 80]')
    itv_outgo_3=Interval('(79, 81]')
    itv2=[itv_outgo_1, itv_outgo_2, itv_outgo_3]

    #itv_mode1_income=Interval('[80.0, 180.0)')
    itv_mode1_income=Interval('[80.0, 81.0)')
    itv11=[itv_mode1_income]
    itv_mode1_outgo=Interval('(60.0, 63.0]')
    itv1=[itv_mode1_outgo]
    print(de1.calculate_max(itv11, Interval('[60.0, 180.0)'), itv1))
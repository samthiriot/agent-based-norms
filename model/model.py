
from pyds import MassFunction


import random
import time
import math


class Model():

    def __init__(self, actions, criteria_to_values):

        self.actions = actions
        self.criteria_to_values = criteria_to_values
        self.criteria = criteria_to_values
        
        self.mass_institution_theoretical_info = 0.9
        self.mass_indirect_observation = 0.7


current_model = Model(
                actions=range(70,155,5),
                criteria_to_values={
                        "points":{-3,0},
                        "hedonism":{float(a)/100 for a in range(0,100,1)},
                        "social_sanction":{float(a)/10 for a in range(-10,2,1)}
                        },
                        #,"remove_licence":{True,False}},
                )




class BeliefsOnValues():
    '''
    describes, for on criteria, the beliefs that are associated to each value;
    thus provides an expectancy computation 
    '''

    def __init__(self, critera):

        self.critera = critera
        self.mass_function = MassFunction([({v for v in current_model.criteria_to_values[critera]},1.0)])

    def get_mass_function(self):
        return self.mass_function

    def get_expectancy(self):
        
        # TODO iterate only on support / focal / something 
        return reduce(lambda t,v: t+v*self.mass_function.bel({v}), current_model.criteria_to_values[self.critera], 0)
        
    # TODO worst value (pessimistic)
    # TODO best vlaue (optimistic)
            
    def add_information(self, vs, m):
        '''
        adds a mass of information on every value in the set vs
        '''
        for v in vs:
            if v not in current_model.criteria_to_values[self.critera]:
                current_model.criteria_to_values[self.critera].add(v)

        #print("adding vs %s m %s" % (vs,m))
        #print("before %s" % self.mass_function)
        self.mass_function = self.mass_function.combine_conjunctive(MassFunction([(vs,m),(current_model.criteria_to_values[self.critera]-vs,1-m)]), normalization=True)
        #print("after %s" % self.mass_function)
        


'''
t1 = BeliefsOnValues("points")
print(t1.get_expectancy())
# add info on fine 
t1.add_theoretical_information({-3}, 0.99)
print(t1.get_expectancy())
# add info on not being fined
#t1.add_theoretical_information({0})
#t1.add_theoretical_information({0})
t1.add_theoretical_information({0}, 0.8)
t1.add_theoretical_information({-3}, 0.8)
t1.add_theoretical_information({-3}, 0.8)
t1.add_theoretical_information({-3}, 0.8)
t1.add_theoretical_information({0}, 0.8)
print(t1.get_expectancy())
'''

'''

Contribution:
* application ou non
* croyances sur l'application possible sur chacun des criteres et chacune de leurs valeurs
Action <>---- Criteres <>----- Valeurs
 

'''

class BeliefsOnAction():
    '''
    describes, for 
    '''  

    def __init__(self, action):

        self.action = action

        self.criteria_to_values_to_beliefs = { c:BeliefsOnValues(c) for c in current_model.criteria }
     
        pass

    def add_information(self, criteria_to_possible_values, m):
        '''
        for some or all criteria, adds some weight on some values;
        for instance {"points":{-3,-2}} means that for points you can have -3 or -2 points
        '''
        for c, vs in criteria_to_possible_values.iteritems():
            self.criteria_to_values_to_beliefs[c].add_information(vs, m)

    def get_expectancy_for_criteria(self, c):
        return self.criteria_to_values_to_beliefs[c].get_expectancy()

    def get_expectancies(self):
        return { c:self.criteria_to_values_to_beliefs[c].get_expectancy() for c in self.criteria_to_values_to_beliefs.keys() }

    def get_expectancy_for_criteria(self, criteria):
        return self.criteria_to_values_to_beliefs[criteria].get_expectancy()

    def get_mass_functions(self):
        return { c:self.criteria_to_values_to_beliefs[c].get_mass_function() for c in self.criteria_to_values_to_beliefs.keys() }
        
    def get_mass_function_for_criteria(self,c):
        return self.criteria_to_values_to_beliefs[c].get_mass_function()
        

class Contribution():

    def __init__(self, always_applied=False):

        # at the beginning, we have no advice on the application or not (ignorance)
        self.always_applied = always_applied
        if always_applied:
            self.application_mass_function = MassFunction([({True},1.0)])
        else:
            self.application_mass_function = MassFunction([({True,False},1.0)])

        # maps actions to beliefs on the potential outcomes of these beliefs
        self.action_to_beliefs = { a:BeliefsOnAction(a) for a in current_model.actions }

        pass

    def observe_direct_application(self):
        m = 0.9
        print "before being catched %s %s" % (self.get_proba_application(), self.get_mass_function_for_criteria("social_sanction"))
        self.application_mass_function = MassFunction([({True},m),({False},1-m)])
        #self.application_mass_function = self.application_mass_function.combine_disjunctive(MassFunction([({True},m),({False},1-m)]))
        print "after being catched %s  %s" % (self.get_proba_application(), self.get_mass_function_for_criteria("social_sanction"))

    def observe_direct_non_application(self):
        m = 0.55
        if self.application_mass_function.bel({True}) > 0 and self.application_mass_function.bel({True}) < 0.001:
            return;
        self.application_mass_function = self.application_mass_function.combine_conjunctive(MassFunction([({False},m),({True},1-m)]))

    def observe_indirect_application(self):
        m = 0.9
        self.application_mass_function = self.application_mass_function.combine_conjunctive(MassFunction([({True},m),({False},1-m)]))

    def observe_indirect_non_application(self):
        m = 0.55
        self.application_mass_function = self.application_mass_function.combine_conjunctive(MassFunction([({False},m),({True},1-m)]))

    def get_proba_application(self):
        return self.application_mass_function.pl({True})

    def add_information_on_action(self, action, criteria_to_possible_values, m=0.9):
        self.action_to_beliefs[action].add_information(criteria_to_possible_values, m)

    def add_theoretical_information(self, action_to_criteria_to_possible_values, m):
        for a in action_to_criteria_to_possible_values.keys():
            #print("adding theoretical info for a %s" % a)
            self.action_to_beliefs[a].add_information(action_to_criteria_to_possible_values[a], m)

    def get_expectancy_for_action(self, action):

        '''
        returns the expectancy (expected utility mediated by bla bla)
        '''
        p = self.get_proba_application()
        return {criteria:p*value for criteria, value in self.action_to_beliefs[action].get_expectancies().iteritems() }

        # return self.action_to_beliefs[action].get_expectancies()

    def get_expectancies_as_dict(self):
        p = self.get_proba_application()
        return {a:{criteria:p*value for criteria, value in self.action_to_beliefs[a].get_expectancies().iteritems() } for a in current_model.actions}

    def get_expectancies(self):
        p = self.get_proba_application()
        return [{criteria:p*value for criteria, value in self.action_to_beliefs[a].get_expectancies().iteritems() } for a in current_model.actions]

    def get_expectancies_for_criteria(self, criteria):
        p = self.get_proba_application()
        return [p*(self.action_to_beliefs[a].get_expectancy_for_criteria(criteria)) for a in current_model.actions]

    def _get_actions_focal(self, bf):
        
        return reduce(lambda s,i: s.union(j for j in i), bf.focal(), set())

    def _merge_mass_function_with_p(self,mass_function,p,a=None):

        # TODO remove
        #return mass_function
       
        #return mass_function.combine_conjunctive(MassFunction([ ({0},1-p)])) 
        #print("a=%s [p=%s] before anything else:%s " % (a,p,mass_function))
        #print("after:%s" %mass_function.combine_conjunctive(MassFunction([ ({0},1-p),(self._get_actions_focal(mass_function),p) ])) )
        #print("after:%s" %mass_function.combine_conjunctive(MassFunction([ ({0},1-p),(self._get_actions_focal(mass_function),p) ])) )
        #self._get_actions_focal(mass_function)
        if (p>=1):
            return mass_function
        
        negative_elements = set()
        frame = mass_function.frame()
        #print("len mass function %s %s %s" % (len(frame), frame, mass_function))
        m = []
        m.append(({},1-p))
        s = set()
        for mf in mass_function:
            if len(mf)<len(frame):
                #print("adding %s" % mf)
                m.append(({e for e in mf}, p))
                s = s | {e for e in mf}
        if len(s) == 0:
            #print("s empty %s" % s)
            return mass_function
        #print("soo %s" % mass_function.combine_conjunctive(MassFunction([ ({},1-p),(s,p) ]), normalization=False))
        return mass_function.combine_conjunctive(MassFunction([ ({},1-p),(s,p) ]), normalization=False) 
        return mass_function.combine_conjunctive(MassFunction(m), normalization=False) 
        
        '''
        
        
        elements = set()
        focal = self._get_actions_focal(mass_function)
        print("focal elements")
        for e in mass_function.frame():
            print(e)
            #print(len(e))
            m.append(({e},p/len(mass_function.frame())))
        return mass_function.combine_conjunctive(MassFunction(m), normalization=False) 
        '''
        #return mass_function.combine_conjunctive(MassFunction([ ({},1-p),(self._get_actions_focal(mass_function),p) ]), normalization=False) # , normalization=False

    def get_mass_function_for_criteria(self, criteria):
        p = self.get_proba_application()
        return [
                self._merge_mass_function_with_p(self.action_to_beliefs[a].get_mass_function_for_criteria(criteria),p,a)
                for a in current_model.actions
                ]
        
    def get_mass_functions(self):
        '''
        returns, for each action, for a subset of criteria, the mass functions that associate each value to its belief mass;
        this last is moderated by the perceived probability of application
        '''
        p = self.get_proba_application()
        return [
                {
                    criteria:self._merge_mass_function_with_p(mass_function,p,a) 
                    for criteria, mass_function in self.action_to_beliefs[a].get_mass_functions().iteritems()
                } 
                for a in current_model.actions
                ]

    def get_mass_functions_raw(self):
        '''
        returns, for each action, for a subset of criteria, the mass functions that associate each value to its belief mass;
        this last is moderated by the perceived probability of application
        '''
        p = self.get_proba_application()
        return [
                {
                    criteria:mass_function 
                    for criteria, mass_function in self.action_to_beliefs[a].get_mass_functions().iteritems()
                } 
                for a in current_model.actions
                ]

    def get_mass_functions_for_action_criteria(a, c):
        return self.action_to_beliefs[a].get_mass_function_for_criteria(c)
      
'''
print("empty contributoin")
c1 = Contribution()
print(c1.get_mass_functions())

print("\nadd law %s" % {a:{"points":{-3}} if a>90 else {"points":{0}} for a in current_model.actions})
c1.add_theoretical_information({a:{"points":{-3}} if a>90 else {"points":{0}} for a in current_model.actions}, 0.8)
print(c1.get_mass_functions())
'''

# generic model
class Agent():
  

    def _function_hedonism(self, action):
        if action <= 110:
            return round(float(action)/110.0,2)
        elif action >= 130:
            return round(1.0-float(action-110.0)/150.0,2)
        else:
            return 1.0

    def __init__(self, id):

        self.id = id

        self.contributions = {}
        self.contribution_experiment = Contribution(always_applied=True)
        self.contribution_experiment.add_theoretical_information({a:{"hedonism":{self._function_hedonism(a)}} for a in current_model.actions}, current_model.mass_institution_theoretical_info)
        self.contributions['experiment'] = self.contribution_experiment

        self.contribution_social_norm = Contribution(always_applied=True) # TODO remove !
        self.contributions['social'] = self.contribution_social_norm

        self.contribution_institutional_norm = Contribution()
        self.contributions['institution'] = self.contribution_institutional_norm

        self.contribution_personnal_benefit = Contribution()
        self.contributions['personal'] = self.contribution_personnal_benefit

        self.state = {
            'points': 12,
            'license': True,
            'money': 5000
        }

        self.weights = {
            'points': 0.4,
            'license': 0.3,
            'money': 0.2,
            'hedonism': 0.3,
            'social_sanction':0.1
        }

        self.action = random.choice(current_model.actions)

        self.recent_memory = [] # ("contribution id", application True|False, {action:{criteria:{values}}})

    def utility_for_criteria(self, criteria, deltavalue):

        if criteria == "points":
            if deltavalue == 0:
                return 0;
            possible_future = max(0,self.state['points'] + deltavalue)
            if self.id == "agent1":
                print ("utility for points delta=%s final=%s ?" % (deltavalue, possible_future))
            return -(12.0-possible_future)/12.0
            
        if criteria == "money":
            projected_budget = self.state['money'] + deltavalue
            if projected_budget < 0:
                return -1.0;
            if projected_budget < 100:
                return -0.9;
            if projected_budget < 500:
                return -0.6;
            if projected_budget < 1000:
                return -0.2;
            return -0.1

        if criteria == "hedonism":
            return deltavalue

        if criteria == "social_sanction":
            return deltavalue

        raise Exception("unknown criteria %s" % criteria)
    

    def receive_contribution_promise(self, contribution,  action_to_criteria_to_possible_values, m):
        '''
        the agent receives an information about institutional norms.
        It should be passed as { action1: { criteriaX: {"possiblevalue1","possiblevalue"}, criteriaY:{"possiblevalue2"}}, action2... }
        '''
        self.contributions[contribution].add_theoretical_information(action_to_criteria_to_possible_values, m)

    def receive_contribution_not_controlled(self, contribution):
        if self.id == "agent1":
            print ("there is no control ! p=%s" % self.contribution_institutional_norm.get_proba_application())     

        self.contributions[contribution].observe_direct_non_application()
       
        if self.id == "agent1":
            print ("there is no control => p=%s" % self.contribution_institutional_norm.get_proba_application())     
        
        # store in my memory
        self.recent_memory.append((contribution, False, None))

    def receive_contribution_application(self, contribution, received_state):
        
        print "damn; now a norm was applied to me."
        #print "before being catched %s %s" % (self.contribution_social_norm.get_proba_application(), self.contribution_social_norm.get_mass_function_for_criteria("social_sanction"))

        # first of all, I was controlled
        self.contributions[contribution].observe_direct_application()

        # also, I know more about the outcomes of the application !
        self.contributions[contribution].add_information_on_action(self.action, {criteria:{value} for criteria, value in received_state.iteritems()})
            
        #print "after being catched %s %s" % (self.contribution_social_norm.get_proba_application(), self.contribution_social_norm.get_mass_function_for_criteria("social_sanction"))
        # store in my memory
        self.recent_memory.append((contribution, True, {self.action:received_state}))

    def receive_indirect_information(self, contribution, application, received_state):
        
        if application:
            self.contributions[contribution].observe_indirect_application()
        else:
            self.contributions[contribution].observe_indirect_non_application()

        if received_state is not None:
            for a in received_state:
                self.contributions[contribution].add_information_on_action(a, {criteria:{value} for criteria, value in received_state[a].iteritems()}, current_model.mass_indirect_observation)

        pass

    def print_information(self):
        print(self.contribution_institutional_norm.get_expectancies())
        print(self.contribution_institutional_norm.get_expectancies_for_criteria("points"))
        print(self.contribution_institutional_norm.get_proba_application())



    def get_expectancy(self, c, mass_function):
        
        return reduce(lambda t,v: t+v*mass_function.bel({v}), current_model.criteria_to_values[c], 0)

    def _merge_contributions(self):
        '''
        aggregates all the beliefs on the outcomes of every action on every criteria,
        and returns them as a dict of actions to a dict of criteria to mass functions
        '''

        # merge our information sources
        if self.id == "agent1" and self.contribution_institutional_norm.get_proba_application() < 1.0:
            print("proba application instit %s" % self.contribution_institutional_norm.get_proba_application()) 
            print("proba application social %s" % self.contribution_social_norm.get_proba_application()) 
            print("proba application experience %s" % self.contribution_experiment.get_proba_application()) 
            print("beliefs for inst raw %s" % self.contribution_institutional_norm.get_mass_functions_raw())
            print("beliefs for inst prob %s" % self.contribution_institutional_norm.get_mass_functions())
        action_to_institutional_contribution = self.contribution_institutional_norm.get_mass_functions()
        action_to_social_norm_contribution = self.contribution_social_norm.get_mass_functions()
        action_to_experience_contribution = self.contribution_experiment.get_mass_functions()

        merged = [
                    {
                        c: action_to_institutional_contribution[idx_action][c].combine_conjunctive(action_to_social_norm_contribution[idx_action][c], normalization=False).combine_conjunctive(action_to_experience_contribution[idx_action][c], normalization=False)
                        for c in current_model.criteria
                    }
                    for idx_action, a in enumerate(current_model.actions)
                    ]

        if self.id == "agent1":
            print ("merged contributions: \n\t%s" % "\n\t".join([str(current_model.actions[i])+":"+str(merged[i]) for i in range(0,len(current_model.actions))] ))
        return merged
        

    def _compute_expectancies(self):
        '''
        after calling _merge_contributions, computes the expectancy for each criteria for each action. 
        It correspondants to a transformation between the mass functions to the sum of beliefs times values.
        '''

        
        merged = self._merge_contributions()

        # create expected values for that 
        # TODO directly let the utility function use the belief mass (better semantics !!!)
        merged_expectancies = [
                    {
                        c: self.get_expectancy(c,merged[idx_action][c])
                        for c in current_model.criteria
                    }
                    for idx_action, a in enumerate(current_model.actions)
                    ] 
        if self.id == "agent1":
            print ("decision set:\n\t%s" % "\n\t".join([str(current_model.actions[i])+":"+str(merged_expectancies[i]) for i in range(0,len(current_model.actions))] ))     

        return merged_expectancies

    def _compute_utilities(self):
        '''
        after calling _compute_expectancies, changes every expected value to the corresponding utility for the agent.
        Returns, for every action and every criteria, the utility. 
        '''
        merged_expectancies = self._compute_expectancies()

        # compute the utilities for these delta
        merged_utilities = [
            {
                c: self.utility_for_criteria(c, merged_expectancies[idx_action][c])
                for c in current_model.criteria
            }
            for idx_action, a in enumerate(current_model.actions)
            ] 

        if self.id == "agent1":
            print ("merged utilities: \n\t%s" % "\n\t".join([str(current_model.actions[i])+":"+str(merged_utilities[i]) for i in range(0,len(current_model.actions))] ))

        return merged_utilities

    def _compute_aggregated_utilities(self):
        '''
        after calling _compute_utilities, aggregates the utility for each criteria to one merged utility.
        returns, for every action, the aggregated utility.
        '''

        merged_utilities = self._compute_utilities()

        # now merge all the utilities for each action
        utilities = [
                    sum(self.weights[c]*merged_utilities[idx_action][c] for c in current_model.criteria)
                    for idx_action, a in enumerate(current_model.actions)
                    ]
        if self.id == "agent1":
            print ("utilities:%s" % utilities )    


        return utilities

    def step(self):

        utilities = self._compute_aggregated_utilities()

        self.last_utilities = utilities

        max_utility = max(utilities)
        best_actions = [a for i, a in enumerate(current_model.actions) if utilities[i]==max_utility]
        if self.id == "agent1":
            print best_actions

        if len(best_actions) == 1:
            # change to the best action is it is not already the case
            if self.action != best_actions[0]:
                print "changing %s -> %s" % (self.action, best_actions[0])
                self.action = best_actions[0]
        elif len(best_actions) > 1:
            #if self.action not in best_actions:
            #    # we are not applying one of the best actions; let's pickup one randomly
            #    print "changing %s -> %s" % (self.action, best_actions[0])
            #    self.action = random.choice(best_actions)
            self.action = random.choice(best_actions)

        if random.random() <= 0.2:
            print "I was supposed to choose %s" % self.action
            idx_action = current_model.actions.index(self.action)
            if idx_action == 0:
                # if it is the first action, we can only explore a quicker one
                self.action = current_model.actions[idx_action+1]
            elif idx_action == len(current_model.actions)-1:
                # if it is the last action, we can only explore a slower one
                self.action = current_model.actions[idx_action-1]
            else:
                # randomly pick one of the quicker or slower action
                if random.random() <= 0.5:
                    self.action = current_model.actions[idx_action-1]
                else:
                    self.action = current_model.actions[idx_action+1]
            print "But this one is more funny ! %s" % self.action
        
        print "updated %s" % self


    def apply_social_coercition(self, alter):
        '''
        the agent applies social coercition if he meets another agent who is acting in a part of the space of action
        with which we now believe is bad
        '''
        
        '''
        if abs(alter.action - self.action) > 20:
            print("I, %s (%s), think this other guy %s (%s) is acting bad" % (self.id, self.action, alter.id, alter.action))
            alter.receive_social_norm_was_applied_to_me({"social_sanction":-0.3})

        return
        '''
        utility_alter_action = self.last_utilities[current_model.actions.index(alter.action)]
        average_utility = float(sum(self.last_utilities))/len(self.last_utilities)
        if utility_alter_action < average_utility:
            print("I, %s (%s), think this other guy %s (%s) is acting bad (%s vs %s)" % (self.id, self.action, alter.id, alter.action, utility_alter_action, average_utility))
            print("my utilities %s" % self.last_utilities)
            alter.receive_contribution_application("social", {"social_sanction":-0.3})
        else:
            print("hey, I %s don't think I've to judge the guy %s anyway" % (self.id, alter.id))
            #alter.receive_contribution_application("social", {"social_sanction":0})

    def observe_others_behaviours(self, alter):

        print "I, %s (%s) am observing this other guy %s (%s)" % (self.id, self.action, alter.id, alter.action)
        # if another is doing that, it means it is socially accepted !
        print "before observation %s %s" % (self.contribution_social_norm.get_proba_application(), self.contribution_social_norm.get_mass_function_for_criteria("social_sanction"))
        bm = self.contribution_social_norm.get_mass_function_for_criteria("social_sanction")[current_model.actions.index(alter.action)].pignistic()
        print "before observation Bel(0.0)=%s, Pl(0.0)=%s, q({0.0})=%s, Bel(0.5)=%s, Pl(0.5)=%s, q(0.5)=%s EU=%s" % (bm.bel({0.0}), bm.pl({0.0}), bm.q({0.0}), bm.bel({-0.5}), bm.pl({-0.5}), bm.q({-0.5,-0.4}), reduce(lambda t,v: t+v*bm.bel({v}), current_model.criteria_to_values["social_sanction"], 0))
        self.contribution_social_norm.add_information_on_action(alter.action, {"social_sanction":{0.1}})
        print "after observation %s %s" % (self.contribution_social_norm.get_proba_application(), self.contribution_social_norm.get_mass_function_for_criteria("social_sanction"))
        bm = self.contribution_social_norm.get_mass_function_for_criteria("social_sanction")[current_model.actions.index(alter.action)].pignistic()
        print "after observation Bel(0.0)=%s, Pl(0.0)=%s, q({0.0})=%s, Bel(0.5)=%s, Pl(0.5)=%s, q(0.5)=%s EU=%s" % (bm.bel({0.0}), bm.pl({0.0}), bm.q({0.0}), bm.bel({-0.5}), bm.pl({-0.5}), bm.q({-0.5,-0.4}), reduce(lambda t,v: t+v*bm.bel({v}), current_model.criteria_to_values["social_sanction"], 0))

    def __repr__(self):
        return "%s [%s] %s" % (self.id, self.action, self.state)

    def get_small_talk(self):
        msgs = self.recent_memory
        self.recent_memory = []
        return msgs

    def receive_small_talk(self, messages):
        for m in messages:
            (contribution, application, values) = m
            print "I heard: (%s, %s, %s)" % (contribution, application, values)
            self.receive_indirect_information(contribution, application, values)

class Output():

    def __init__(self):
        pass

    def write(self, timestep):
        raise Exception("not implemented")
        pass

class OutputHeatmapProportion(Output):

    def __init__(self):
        self.output_time_to_action_to_count = []
        pass

    def write(self, agents, timestep):
        
        # read data first
        # ... the proportion of the population in each action
        action_to_proportion = {a:0 for a in current_model.actions}
        for a in agents:
            action_to_proportion[a.action] += 1
        # .... normalize and reformulate
        actions_counts = []
        for a in current_model.actions:
            actions_counts.append(float(action_to_proportion[a])/len(agents))
        self.output_time_to_action_to_count.append(actions_counts)

        # write the data
        with open('time_to_action_to_proportion_gnuplot.csv', 'w') as f2:
            for action_idx in range(1,len(current_model.actions)):
                for timestep in range(0,len(self.output_time_to_action_to_count)):

                    # ... action
                    f2.write(str(timestep))
                    f2.write(' ')

                    f2.write(str(current_model.actions[action_idx-1]))
                    f2.write(' ')

                    f2.write("{0:.2f}".format(self.output_time_to_action_to_count[timestep][action_idx]))
                    f2.write(' ')

                    f2.write('\n')

                f2.write('\n')

                for timestep in range(0,len(self.output_time_to_action_to_count)):

                    # ... action
                    f2.write(str(timestep))
                    f2.write(' ')

                    f2.write(str(current_model.actions[action_idx]-0.01))
                    f2.write(' ')

                    f2.write("{0:.2f}".format(self.output_time_to_action_to_count[timestep][action_idx]))
                    f2.write(' ')

                    f2.write('\n')

                f2.write('\n')


class OutputCountPoints(Output):

    def __init__(self):
        self.file = open('time_to_points.dat', 'w')
        self.file.write("# timestep\taverage\tprop%s\n" % "\tprop".join(str(p) for p in range(0,13)))
        pass

    def write(self, agents, timestep):
        
        # read data first
        # ... the proportion of the population in each action
        total = 0.0
        points_to_count = {p:0 for p in range(0,13)}
        for a in agents:
            points_to_count[a.state["points"]] += 1
            total += a.state["points"]
        # .... normalize and reformulate
        self.file.write(str(timestep))
        self.file.write("\t%s" % "\t{0:.2f}".format(total/len(agents)))
        for p in range(0,13):
            self.file.write("\t{0:.2f}".format(float(points_to_count[p])/len(agents)))
        self.file.write('\n')

         
class OutputAgentContributions(Output):

    def __init__(self, agents_to_monitor):
        self.agents_to_monitor = agents_to_monitor

        self.reporting_agentid_to_utilityname_to_file = {}
        pass

    def _write_agent_utility(self, timestep, c, agent, utilities):
        # get or create a file for this agent and criteria
        f = None    
        if c not in self.reporting_agentid_to_utilityname_to_file[agent.id]:
            f = open("utility_%s_%s" % (c,agent.id), 'w')
            self.reporting_agentid_to_utilityname_to_file[agent.id][c] = f
        else:
            f = self.reporting_agentid_to_utilityname_to_file[agent.id][c]
        # write the utilities
        for index_action in range(1,len(current_model.actions)):
            #for index_action, action in enumerate(current_model.actions):
            f.write(str(timestep))    
            f.write(' ')
            f.write(str(current_model.actions[index_action-1]))
            f.write(' ')
            f.write("{0:.2f}".format(utilities[index_action].get(c,0)))
            f.write('\n')

            #for index_action, action in enumerate(current_model.actions):
            f.write(str(timestep))    
            f.write(' ')
            f.write(str(current_model.actions[index_action]-0.01))
            f.write(' ')
            f.write("{0:.2f}".format(utilities[index_action].get(c,0)))
            f.write('\n')

        f.write('\n')

        
    def _write_agent_aggregated_utility(self, timestep, c, agent, utilities):

        # get or create a file for this agent and criteria
        f = None    
        if c not in self.reporting_agentid_to_utilityname_to_file[agent.id]:
            f = open("utility_%s_%s" % (c,agent.id), 'w')
            self.reporting_agentid_to_utilityname_to_file[agent.id][c] = f
        else:
            f = self.reporting_agentid_to_utilityname_to_file[agent.id][c]
        # write the utilities
        # write the utilities
        for index_action in range(1,len(current_model.actions)):
            #for index_action, action in enumerate(current_model.actions):
            f.write(str(timestep))    
            f.write(' ')
            f.write(str(current_model.actions[index_action-1]))
            f.write(' ')
            f.write("{0:.2f}".format(utilities[index_action]))
            f.write('\n')

            #for index_action, action in enumerate(current_model.actions):
            f.write(str(timestep))    
            f.write(' ')
            f.write(str(current_model.actions[index_action]-0.01))
            f.write(' ')
            f.write("{0:.2f}".format(utilities[index_action]))
            f.write('\n')
           
        f.write('\n')
        '''
        for index_action, action in enumerate(current_model.actions):
            f.write(str(timestep))    
            f.write(' ')
            f.write(str(action))
            f.write(' ')
            f.write("{0:.2f}".format(utilities[index_action]))
            f.write('\n')

        f.write('\n')
        '''

    def reportAgentUtility(self, timestep, agent):

        # write them to file ... ?
        if agent.id not in self.reporting_agentid_to_utilityname_to_file:
            self.reporting_agentid_to_utilityname_to_file[agent.id]={}

        # write every criteria
        utilities = agent._compute_utilities()
        for c in current_model.criteria:
            self._write_agent_utility(timestep, c, agent, utilities)
        
        # write the aggregation of that 
        self._write_agent_aggregated_utility(timestep, "aggregated", agent, agent._compute_aggregated_utilities())

        pass

    def write(self, agents, timestep):

        for a in agents:
            if a.id in self.agents_to_monitor:
                self.reportAgentUtility(timestep, a)
    

class Norm():

    def __init__(self, id, action2utilities, action2practice):
        self.id = id
        self.action2utilities = action2utilities
        self.action2practice = action2practice

    def __repr__(self):
        return "norm: %s" % self.id

    def applies(self, action):
        '''
        returns True if the norm applies when this action exists
        '''
        return len(self.action2utilities[action]) > 0

    def apply(self, agent):
        
        print "should apply %s to %s" % (self.action2utilities, agent)
        print "will apply %s" % (self.action2practice)
        print "applying %s to %s : %s" % (self.id, agent, { c:random.sample(self.action2practice[agent.action][c],1)[0] for c in self.action2practice[agent.action].keys()})

        agent.receive_contribution_application("institution", { c:random.sample(self.action2practice[agent.action][c],1)[0] for c in self.action2practice[agent.action].keys()})
        
        print "applied %s to %s" % (self.id, agent)
        


class Experiment():
    
    def __init__(self, 
                    agents_count, 
                    duration, 
                    law,
                    inform_law_step,
                    campain_application,
                    campains_information,
                    count_interactions_observation, 
                    count_interaction_social_coercition, 
                    count_interaction_small_talk,
                    agents_to_observe
                    ):

        self.agents_count = agents_count
        self.duration = duration

        self.outputs = [
                            OutputHeatmapProportion(),
                            OutputAgentContributions(agents_to_observe),
                            OutputCountPoints()
                        ]

        self.law = law
        self.inform_law_step = inform_law_step

        self.campains_application = campain_application

        self.campains_information = campains_information

        self.count_interactions_observation = count_interactions_observation
        self.count_interaction_social_coercition = count_interaction_social_coercition
        self.count_interaction_small_talk = count_interaction_small_talk

    def run(self):

        # ... create the population of agents
        agents = set()
        for i in range(0,self.agents_count+1):
            agents.add(Agent('agent'+str(i)))

        # ... first update of the actions to create a coherent initial state
        for a in agents:
            a.step()

        # ... print the behaviour of agents
        print "initial behaviours %s" % map(lambda a: a.action, agents)

        # probes:
        for o in self.outputs:
            o.write(agents, -1)

        for timestep in range(0, self.duration):

            print("=== step %i/%i" % (timestep, self.duration))
            timestep_controls = 0
            timestep_applications = 0

            # ... assume each agent is aware of the institutional norms
            if timestep == self.inform_law_step:
                for a in agents:
                    #for i_n in institutional_norms:
                    a.receive_contribution_promise("institution", self.law.action2utilities, current_model.mass_institution_theoretical_info)

            # inform agents of the communication campain
            for (start, end, proba, msg) in self.campains_information:
                if start <= timestep <= end:
                    for a in random.sample(agents,int(round(proba*len(agents)))):
                        a.receive_contribution_promise("experiment", msg, 0.6)
                    
            # apply campains
            if timestep >= self.inform_law_step:
                all_controlled_agents = set()
                for c in self.campains_application:
                    controlled_agents = random.sample(agents,int(round(c[2]*len(agents))))
                    all_controlled_agents.update(controlled_agents)
                    if c[0] <= timestep <= c[1]:
                        print("applying campain on %i persons" % round(c[2]*len(agents)))
                        for a in controlled_agents:
                            timestep_controls += 1
                            if self.law.applies(a.action):
                                self.law.apply(a)
                                timestep_applications += 1
                            else:
                                a.receive_contribution_not_controlled("institution")             
                # TODO inform others they were not controlled !
                for a in agents:
                    if a not in all_controlled_agents:
                        a.receive_contribution_not_controlled("institution")             

            if self.count_interaction_social_coercition > 0:
                # apply social norm
                for a in agents:
                    for a2 in random.sample(agents-{a}, self.count_interaction_social_coercition):
                        a.apply_social_coercition(a2)
               
            # offer agents to watch each other behaviour
            if self.count_interactions_observation > 0:
                for a in agents:
                    for a2 in random.sample(agents-{a}, self.count_interactions_observation):
                        a.observe_others_behaviours(a2)
                

            # exchange information
            if self.count_interaction_small_talk > 0:
                for a in agents:
                    msgs = a.get_small_talk()
                    for a2 in random.sample(agents-{a}, self.count_interaction_small_talk):
                        a2.receive_small_talk(msgs)
                
            # update agent behaviours
            for a in agents:
                a.step()

            print "behaviours %s/%s %s" % (timestep, self.duration, map(lambda a: a.action, agents))
            
            # probes:
            for o in self.outputs:
                o.write(agents, timestep)


Experiment(
            agents_count=100,
            duration=200, 
            law=Norm(
                        "90kmh", 
                        { a:{"points":{-3}} if a>90 else {} for a in current_model.actions},
                        { a: ({"points":{-3}} if a>95 else {"points":{0}} ) for a in current_model.actions}
                        ),
            inform_law_step=10,
            campain_application=[(50,100,0.3) ], #, (200,300,0.1)
            campains_information=[],#[(20,50,0.1, { a:{"hedonism":{0}} if a>100 else {} for a in current_model.actions})],
            count_interactions_observation=0, 
            count_interaction_social_coercition=5, 
            count_interaction_small_talk=0,
            agents_to_observe={"agent1","agent2"}
            ).run()

'''
sam = Agent("sam")

sam.fusion_information_beliefs()

print("sam receive information on fines")
sam.receive_institutional_norm_description({a:{"points":{-3}} if a>90 else {} for a in current_model.actions})
#sam.print_information();
sam.fusion_information_beliefs()

print("sam receive information on not being controlled")
for i in range(1,10):
    sam.receive_institutional_norm_was_not_controlled()
    sam.fusion_information_beliefs()

sam.receive_institutional_norm_was_controlled()
sam.fusion_information_beliefs()

sam.receive_institutional_norm_was_applied_to_me({'points':-3})
sam.fusion_information_beliefs()
'''

'''
t = BeliefsOnActions()
print(t.get_expectancies())
t.add_theoretical_information( {a:{"points":{-3}} if a>=90 else {} for a in actions}, 0.9)
print(t.get_expectancies())

print("\ntest contrib\n")
c = Contribution()
print("prior knowledge")
c.get_expectancy_application()

print("be fined ")
# we were fined
c.observe_direct_application()
c.get_expectancy_application()

print("observe others not being fined")
for i in range(0,50):
    c.observe_indirect_non_application()
    c.get_expectancy_application()

print("be fined ")
# we were fined
c.observe_direct_application()
c.get_expectancy_application()

for i in range(0,10):
    c.observe_indirect_non_application()
    c.get_expectancy_application()
'''

#norm_institutional = lambda speed: {"cost":-50, "points":-3} if speed>=0 else {}

#transform_information_to_belief_masses(norm_institutional)

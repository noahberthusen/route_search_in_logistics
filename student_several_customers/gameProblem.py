
'''
    Class gameProblem, implements simpleai.search.SearchProblem
'''


from simpleai.search import SearchProblem
# from simpleai.search import breadth_first,depth_first,astar,greedy
import simpleai.search

class GameProblem(SearchProblem):

    # Object attributes, can be accessed in the methods below
    
    MAP=None
    POSITIONS=None
    INITIAL_STATE=None
    GOAL=None
    CONFIG=None
    AGENT_START=None
    SHOPS=None
    CUSTOMERS=None
    MAXBAGS = 0

    MOVES = ('West','North','East','South')

   # --------------- Common functions to a SearchProblem -----------------

    def actions(self, state):
        '''Returns a LIST of the actions that may be executed in this state
        '''
        # states: (x, y, num_pizzas, num_orders)
        actions = []
        map_size = self.CONFIG['map_size']

        # CHECK NORTH
        if (state[1] - 1 >= 0 and not self.getAttribute((state[0], state[1] - 1), 'blocked')):
            actions.append('North')
        # CHECK EAST
        if (state[0] + 1 < map_size[0] and not self.getAttribute((state[0] + 1, state[1]), 'blocked')):
            actions.append('East')
        # CHECK SOUTH
        if (state[1] + 1 < map_size[1] and not self.getAttribute((state[0], state[1] + 1), 'blocked')):
            actions.append('South')
        # CHECK WEST
        if (state[0] - 1 >= 0 and not self.getAttribute((state[0] - 1, state[1]), 'blocked')):
            actions.append('West')
        # CHECK LOAD
        if (self.getAttribute((state[0], state[1]), 'load') and state[2] < self.MAXBAGS):
            actions.append('Load')

        # CHECK UNLOAD
        if (self.getAttribute((state[0], state[1]), 'unload') and state[2] > 0):
            for cust in state[3]:
                if ( (state[0] == cust[0]) and (state[1] == cust[1]) and (cust[2] > 0) ):
                    actions.append('Unload')
                    break

        return actions
    

    def result(self, state, action):
        '''Returns the state reached from this state when the given action is executed
        ''' 
        customer_orders = []
        next_state = None
        if (action == 'North'):
            next_state = (state[0], state[1] - 1, state[2], state[3])
        elif (action == 'East'):
            next_state = (state[0] + 1, state[1], state[2], state[3])
        elif (action == 'South'):
            next_state = (state[0], state[1] + 1, state[2], state[3])
        elif (action == 'West'):
            next_state = (state[0] - 1, state[1], state[2], state[3])
        elif (action == 'Load'):
            next_state = (state[0], state[1], state[2] + 1, state[3])
        elif (action == 'Unload'):
            for cust in state[3]:
                temp = cust[2]
                if ( (cust[2] > 0) and (cust[0] == state[0]) and (cust[1] == state[1]) ):
                    temp = temp - 1
                customer_orders.append((cust[0], cust[1], temp))
            next_state = (state[0], state[1], state[2] - 1, tuple(customer_orders))
            
        return next_state


    def is_goal(self, state):
        '''Returns true if state is the final state
        '''
        if (state[0] == self.GOAL[0] and state[1] == self.GOAL[1]):
            for cust in state[3]:
                if (cust[2] != 0):
                    return False
        else:
            return False

        return True

    def cost(self, state, action, state2):
        '''Returns the cost of applying `action` from `state` to `state2`.
           The returned value is a number (integer or floating point).
           By default this function returns `1`.
        '''
        return self.getAttribute((state[0], state[1]), 'cost') * max (1, state[2] +1)

    def heuristic(self, state):
        '''Returns the heuristic for `state`
        '''
        def manhattan(pos1, pos2):
            '''Returns the manhattan distance between two locations
            '''
            return (abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]))

        heuristic = 0
        bike = (state[0], state[1])
        goal = (self.GOAL[0], self.GOAL[1])
        pizzas = self.POSITIONS['pizza']

        customer = []

        for custom in state[3]:
            if (custom[2] > 0 ):
                xpos = custom[0]
                ypos = custom[1]
                customer.append((xpos,ypos))
                break

        # distance to pizza
        # distance to customer
        orders = 0
        for cust in state[3]:
            if (cust[2] > 0):
                orders = orders + cust[2]

        if (orders > 0):
            if (state[2] == 0):
                heuristic += min([manhattan(bike, p) for p in pizzas])
                heuristic += orders
            heuristic += manhattan(bike, customer[0])
            heuristic += orders
            heuristic += manhattan(goal, customer[0])
        else:
            heuristic += manhattan(goal, bike)

        return heuristic


    def setup (self):
        '''This method must create the initial state, final state (if desired) and specify the algorithm to be used.
           This values are later stored as globals that are used when calling the search algorithm.
           final state is optional because it is only used inside the is_goal() method

           It also must set the values of the object attributes that the methods need, as for example, self.SHOPS or self.MAXBAGS
        '''

        print('\nMAP: ', self.MAP, '\n')
        print('POSITIONS: ', self.POSITIONS, '\n')
        print('CONFIG: ', self.CONFIG, '\n')
        
        # (x, y, num_pizzas, num_orders) 
        num_orders = []
        orders_goal = []
        if ('customer1' in self.POSITIONS):
            for cust1 in self.POSITIONS['customer1']:
                num_orders.append((cust1[0],cust1[1], 1))
                orders_goal.append((cust1[0], cust1[1], 0))

        if ('customer2' in self.POSITIONS):
            for cust2 in self.POSITIONS['customer2']:
                num_orders.append((cust2[0], cust2[1], 2))
                orders_goal.append((cust2[0], cust2[1], 0))

        if ('customer3' in self.POSITIONS):
            for cust3 in self.POSITIONS['customer3']:
                num_orders.append((cust3[0], cust3[1], 3))
                orders_goal.append((cust3[0], cust3[1], 0))

        initial_state = (self.AGENT_START[0], self.AGENT_START[1], 0, tuple(num_orders))

        final_state= (self.AGENT_START[0], self.AGENT_START[1], None, tuple(orders_goal))

        self.MAXBAGS = self.CONFIG['maxBags']
        algorithm= simpleai.search.astar
        #algorithm= simpleai.search.breadth_first
        #algorithm= simpleai.search.depth_first
        #algorithm= simpleai.search.limited_depth_first

        return initial_state,final_state,algorithm
        
    def printState (self,state): 
        '''Return a string to pretty-print the state '''
        orders = 0
        if (('customer1' in self.POSITIONS) or ('customer2' in self.POSITIONS) or ('customer3' in self.POSITIONS)):
            for cust in state[3]:
                orders = orders + cust[2]

        pps='Location: (' + str(state[0]) + ', ' + str(state[1]) + ')  Pizzas in bag: ' + str(state[2]) + '  Orders left: ' + str(orders)
        return (pps)

    def getPendingRequests (self,state):
        ''' Return the number of pending requests in the given position (0-N). 
            MUST return None if the position is not a customer.
            This information is used to show the proper customer image.
        '''
        if (self.getAttribute((state[0], state[1]), 'unload')):
            for cust in state[3]:
                if ((state[0] == cust[0]) and (state[1] == cust[1])):
                    return cust[2]
        else:
            return None

    # -------------------------------------------------------------- #
    # --------------- DO NOT EDIT BELOW THIS LINE  ----------------- #
    # -------------------------------------------------------------- #

    def getAttribute (self, position, attributeName):
        '''Returns an attribute value for a given position of the map
           position is a tuple (x,y)
           attributeName is a string
           
           Returns:
               None if the attribute does not exist
               Value of the attribute otherwise
        '''
        tileAttributes=self.MAP[position[0]][position[1]][2]
        if attributeName in tileAttributes.keys():
            return tileAttributes[attributeName]
        else:
            return None

    def getStateData (self,state):
        stateData={}
        pendingItems=self.getPendingRequests(state)
        if pendingItems is None or pendingItems >= 0:
            stateData['newType']='customer{}'.format(pendingItems)
        return stateData
        
    # THIS INITIALIZATION FUNCTION HAS TO BE CALLED BEFORE THE SEARCH
    def initializeProblem(self,map,positions,conf,aiBaseName):
        self.MAP=map
        self.POSITIONS=positions
        self.CONFIG=conf
        self.AGENT_START = tuple(conf['agent']['start'])

        initial_state,final_state,algorithm = self.setup()
        if initial_state == False:
            print ('-- INITIALIZATION FAILED')
            return True
      
        self.INITIAL_STATE=initial_state
        self.GOAL=final_state
        self.ALGORITHM=algorithm
        super(GameProblem,self).__init__(self.INITIAL_STATE)
            
        print ('-- INITIALIZATION OK')
        return True
        
    # END initializeProblem 


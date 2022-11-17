#!/usr/bin/python3

from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time
import numpy as np
from TSPClasses import *
import heapq
import itertools



class TSPSolver:
	def __init__( self, gui_view ):
		self._scenario = None

	def setupWithScenario( self, scenario ):
		self._scenario = scenario


	''' <summary>
		This is the entry point for the default solver
		which just finds a valid random tour.  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of solution, 
		time spent to find solution, number of permutations tried during search, the 
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	def defaultRandomTour( self, time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		ncities = len(cities)
		foundTour = False
		count = 0
		bssf = None
		start_time = time.time()
		while not foundTour and time.time()-start_time < time_allowance:
			# create a random permutation
			perm = np.random.permutation( ncities )
			route = []
			# Now build the route using the random permutation
			for i in range( ncities ):
				route.append( cities[ perm[i] ] )
			bssf = TSPSolution(route)
			count += 1
			if bssf.cost < np.inf:
				# Found a valid route
				foundTour = True
		end_time = time.time()
		results['cost'] = bssf.cost if foundTour else math.inf
		results['time'] = end_time - start_time
		results['count'] = count
		results['soln'] = bssf
		results['max'] = None
		results['total'] = None
		results['pruned'] = None
		return results


	''' <summary>
		This is the entry point for the greedy solver, which you must implement for 
		the group project (but it is probably a good idea to just do it for the branch-and
		bound project as a way to get your feet wet).  Note this could be used to find your
		initial BSSF.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found, the best
		solution found, and three null values for fields not used for this 
		algorithm</returns> 
	'''
	# Solves TSP using a greedy algorithm.
	#
	# The time complexity of this function is O(n^3). This is because in the worst case, we have to use every single
	# city as the starting city. Then, for each starting city, we could potentially go to every single other city just
	# to find that there is no solution. As we are greedily going through each city (for a particular starting city),
	# we have to check the path to all of the neighboring cities. There could be n neighboring cities in the worst case,
	# and checking these n neighbors n times has a time complexity of O(n^2). Doing this for every single one of n starting
	# cities results in a time complexity of O(n^3).
	#
	# The space complexity of this function is O(n). This is because the only space we use (aside from storing constant
	# space variables) is for visited_cities, cities, and route. Each of these holds at most n cities at any given time
	# because even if we have to check multiple starting cities, the while loop resets these variables each time. Thus,
	# the space complexity is O(n + n + n) which generalizes to O(n).
	def greedy( self,time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()
		start_city_index = 0
		bssf = None

		start_time = time.time()

		# timeout constraint
		while time.time() - start_time < time_allowance:
			# for each different starting city we run greedy on, keep track of the cities that have already been visited
			visited_cities = set()
			current_city = cities[start_city_index]
			route = [current_city]
			visited_cities.add(current_city)

			# while we haven't visited all cities
			while len(visited_cities) != len(cities):
				shortest = math.inf
				next_city_index = 0
				# look at the distance from the current city to every other city, keep track of the shortest
				for i in range(len(cities)):
					# only look at the distance if we haven't already visited it
					if cities[i] not in visited_cities:
						cost = current_city.costTo(cities[i])
						if cost < shortest:
							shortest = cost
							next_city_index = i
				# we now know which is the shortest, and that's the city we go to next
				next_city = cities[next_city_index]
				# add the city to the solution and to visited
				route.append(next_city)
				visited_cities.add(next_city)
				# update current_city
				current_city = next_city

			bssf = TSPSolution(route)

			# if we did actually find a solution instead of hitting a dead end, we can break
			#
			# this accounts for looping back to the starting city because TSPSolution adds an edge from the last
			# city of the route to the first, so if that edge is inf then this solution won't be used
			if bssf.cost != math.inf:
				break
			start_city_index = start_city_index + 1

		end_time = time.time()

		results['cost'] = bssf.cost
		results['time'] = end_time - start_time
		results['count'] = 1
		results['soln'] = bssf
		return results
	
	
	
	''' <summary>
		This is the entry point for the branch-and-bound algorithm that you will implement
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number solutions found during search (does
		not include the initial BSSF), the best solution found, and three more ints: 
		max queue size, total number of states created, and number of pruned states.</returns> 
	'''
	def branchAndBound( self, time_allowance=60.0 ):
		pass



	''' <summary>
		This is the entry point for the algorithm you'll write for your group project.
		</summary>
		<returns>results dictionary for GUI that contains three ints: cost of best solution, 
		time spent to find best solution, total number of solutions found during search, the 
		best solution found.  You may use the other three field however you like.
		algorithm</returns> 
	'''
	def twoOpt( self,time_allowance=60.0 ):
		pass


	def threeOpt( self,time_allowance=60.0 ):
		pass


	def simulatedAnnealing( self,time_allowance=60.0 ):
		pass

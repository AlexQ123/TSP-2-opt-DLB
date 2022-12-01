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
		results = {}
		cities = self._scenario.getCities()

		dlb = {}
		for i in range(len(cities)-1):
			dlb[cities[i]] = False

		start_time = time.time()

		best_solution = self.greedy()['soln']
		improved = True
		while improved:
			improved = False
			for i in range(len(cities)-1):
				if dlb[cities[i]]:
					continue

				dlb_breaker = False

				for j in range(len(cities)-1):
					if cities[i] == cities[j] or cities[(i+1) % len(cities)] == cities[j] or cities[(j+1) % len(cities)] == cities[i]:
						continue

					if self.lengthDeltaFromTwoOpt(cities, i, j) < 0:
						dlb[cities[i]] = False
						dlb[cities[(i+1) % len(cities)]] = False
						dlb[cities[j]] = False
						dlb[cities[(j+1) % len(cities)]] = False
						new_path = self.twoOptSwap(best_solution.route, i, j)
						new_cost = TSPSolution(new_path).cost
						if new_cost < best_solution.cost:
							improved = True
							best_solution = TSPSolution(new_path)
							dlb_breaker = True

				if dlb_breaker:
					break
				dlb[cities[i]] = True

		end_time = time.time()

		results['cost'] = best_solution.cost
		results['time'] = end_time - start_time
		results['count'] = 0 #TODO: change
		results['soln'] = best_solution
		return results

	# Building the new route and calculating the distance of the new route can be a very expensive
	# operation, usually O(n) where n is the number of vertices in the route. This can be converted
	# into an O(1) operation. Since a 2-opt operation involves removing 2 edges and adding 2 different
	# edges we can subtract and add the distances of only those edges.
	#
	# If length_delta is negative that would mean that the new distance after the swap would be smaller.
	# Once it is known that lengthDelta is negative, then we perform a 2-opt swap. This saves us a lot
	# of computation.
	def lengthDeltaFromTwoOpt(self, cities, i, j):
		return -cities[i].costTo(cities[(i + 1) % len(cities)]) \
					               - cities[j].costTo(cities[(j + 1) % len(cities)]) \
					               + cities[i].costTo(cities[j]) \
					               + cities[(i + 1) % len(cities)].costTo(cities[(j + 1) % len(cities)])

	def twoOptSwap(self, path, v1, v2):
		new_path = []

		# take path[0] to path[v1] and add them in order to new_path
		new_path += path[:v1]

		# take path[v1+1] to path[v2] and add them in reverse order to new_path
		new_path += path[v1:v2][::-1]

		# take path[v2+1] to path[end] and add them in order to new_path
		new_path += path[v2:]

		return new_path


	def threeOpt( self,time_allowance=60.0 ):
		results = {}
		cities = self._scenario.getCities()

		start_time = time.time()

		best_path = self.greedy()['soln'].route
		improved = True
		while improved:
			improved = False
			# for every possible combination of segments. Note that j starts and i+2 and k starts at j+2 because the
			# idea with 3-opt swap is to have 3 subtours and recombine them in the best way. The 3 segments between
			# the 3 subtours must consist of 2 cities, so there needs to be at least 1 city between i, j, and k so that
			# no 2 segments share a city, hence the + 2. As for the line len(cities)-1+(i>0), we only allow k to be the
			# last city if i is not the first city, because again there needs to be at least 1 city between i, j, and k.
			for (i, j, k) in self.allPossibleSegmentCombinations(len(cities)):
				# there are 8 possible opt cases for a 3-opt swap, including the case where you do nothing
				opt_cases = {
					0: 0,
					1: 0,
					2: 0,
					3: 0,
					4: 0,
					5: 0,
					6: 0,
					7: 0
				}
				for opt_case in range(8):
					opt_cases[opt_case] = self.calculateThreeOptSwap(best_path, i, j, k, opt_case)
				# the opt_cases dictionary now maps each opt_case to how much it reduces the cost of the tour by,
				# so we want to pick the opt_Case with the largest reduction value
				best_case = max(opt_cases, key=opt_cases.get)
				# if the best opt_case does in fact reduce the cost of the tour
				if opt_cases[best_case] > 0:
					best_path = self.reverseSegments(best_path, i, j, k, best_case)
					improved = True
					# break because now we've changed the tour, so we start over
					break

		end_time = time.time()

		best_solution = TSPSolution(best_path)
		results['cost'] = best_solution.cost
		results['time'] = end_time - start_time
		results['count'] = 0  # TODO: change
		results['soln'] = best_solution
		return results

	def allPossibleSegmentCombinations(self, n):
		return ((i, j, k)
		        for i in range(n)
		        for j in range(i + 2, n)
		        for k in range(j + 2, n + (i > 0)))

	# for the given opt_case, find the overall "reduction" of this case. meaning, calculate the total length of all
	# the edges that are being deleted, and also calculate the total length of all the dges that are being added.
	# return delete_length - add_length, which represents how much we can reduce the cost of the tour by if we use
	# this opt_case.
	def calculateThreeOptSwap(self, path, i, j, k, case):
		# Given tour [...X1-X2...Y1-Y2...Z1-Z2...]
		X1, X2, Y1, Y2, Z1, Z2 = path[i - 1], path[i], path[j - 1], path[j], path[k - 1], path[k % len(path)]

		delete_length = 0
		add_length = 0

		# abc
		if case == 0:
			pass
		# a'bc
		elif case == 1:
			delete_length = X1.costTo(X2) + Z1.costTo(Z2)
			add_length = X1.costTo(Z1) + X2.costTo(Z2)
		# abc'
		elif case == 2:
			delete_length = Y1.costTo(Y2) + Z1.costTo(Z2)
			add_length = Y1.costTo(Z1) + Y2.costTo(Z2)
		# ab'c
		elif case == 3:
			delete_length = X1.costTo(X2) + Y1.costTo(Y2)
			add_length = X1.costTo(Y1) + X2.costTo(Y2)
		# ab'c'
		elif case == 4:
			delete_length = X1.costTo(X2) + Y1.costTo(Y2) + Z1.costTo(Z2)
			add_length = X1.costTo(Y1) + X2.costTo(Z1) + Y2.costTo(Z2)
		# a'b'c
		elif case == 5:
			delete_length = X1.costTo(X2) + Y1.costTo(Y2) + Z1.costTo(Z2)
			add_length = X1.costTo(Z1) + Y2.costTo(X2) + Y1.costTo(Z2)
		# a'bc'
		elif case == 6:
			delete_length = X1.costTo(X2) + Y1.costTo(Y2) + Z1.costTo(Z2)
			add_length = X1.costTo(Y2) + Z1.costTo(Y1) + X2.costTo(Z2)
		# a'b'c'
		elif case == 7:
			delete_length = X1.costTo(X2) + Y1.costTo(Y2) + Z1.costTo(Z2)
			add_length = X1.costTo(Y2) + Z1.costTo(X2) + Y1.costTo(Z2)

		return delete_length - add_length

	def reverseSegments(self, path, i, j, k, case):
		new_path = []

		if (i - 1) < (k % len(path)):
			segment_1 = path[k % len(path):] + path[:i]
		else:
			segment_1 = path[k % len(path):i]
		segment_2 = path[i:j]
		segment_3 = path[j:k]

		# abc
		if case == 0:
			return path
		# a'bc
		elif case == 1:
			new_path = segment_1[::-1] + segment_2 + segment_3
		# abc'
		elif case == 2:
			new_path = segment_1 + segment_2 + segment_3[::-1]
		# ab'c
		elif case == 3:
			new_path = segment_1 + segment_2[::-1] + segment_3
		# ab'c'
		elif case == 4:
			new_path = segment_1 + segment_2[::-1] + segment_3[::-1]
		# a'b'c
		elif case == 5:
			new_path = segment_1[::-1] + segment_2[::-1] + segment_3
		# a'bc'
		elif case == 6:
			new_path = segment_1[::-1] + segment_2 + segment_3[::-1]
		# a'b'c'
		elif case == 7:
			new_path = segment_1[::-1] + segment_2[::-1] + segment_3[::-1]

		return new_path


	def simulatedAnnealing( self,time_allowance=60.0 ):
		pass

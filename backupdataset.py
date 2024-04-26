import requests
import random
import csv

class Clue:
	def __init__(self, index, direction, question, answer, span):
		self.index = index
		self.direction = direction
		self.question = question
		self.answer = answer
		self.length = len(answer)
		self.span = span

	def __str__(self):
		return f"{self.index}. ({self.direction}) {self.question} ({self.length} letters): {self.answer} Span: {self.span}"

class CrosswordDataset:
	def __init__(self, year, month, day, ifsorted=False):
		self.year = year
		self.month = month
		self.day = day
		self.crossword_data = self.fetch_crossword_json()
		self.rows = self.crossword_data['size']['rows']
		self.cols = self.crossword_data['size']['cols']
		self.clues = self.collect_clues()
		self.correct_guesses = 0
		self.use_known = False

		if ifsorted:
			self.clues = sorted(self.clues, key=lambda x: x.length)
			
		self.locations = self.find_locations()
		self.grid = self.build_grid()

	def fetch_crossword_json(self):
		url = f"https://raw.githubusercontent.com/doshea/nyt_crosswords/master/{self.year}/{self.month}/{self.day}.json"
		# response = requests.get(url)
		# if response.status_code == 200:
		# 	return response.json()
		# else:
		# 	print("Error fetching JSON:", response.status_code)
		# 	return None
		try:
			response = requests.get(url)
			response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
			return response.json()
		except requests.exceptions.HTTPError as http_err:
			raise RuntimeError(f"HTTP error occurred: {http_err}") from http_err
		except requests.exceptions.RequestException as e:
			raise RuntimeError(f"Error fetching data: {e}") from e

	# def collect_clues(self):
	# 	clues = []

	# 	# Collect across clues
	# 	for i, clue in enumerate(self.crossword_data['clues']['across']):
	# 		index = int(clue.split(". ", 1)[0])
	# 		direction = 'across'
	# 		question = clue.split(". ", 1)[1]
	# 		answer = self.crossword_data['answers']['across'][i]
	# 		clues.append(Clue(index, direction, question, answer))

		# # Collect down clues
		# for i, clue in enumerate(self.crossword_data['clues']['down']):
		# 	index = int(clue.split(". ", 1)[0])
		# 	direction = 'down'
		# 	question = clue.split(". ", 1)[1]
		# 	answer = self.crossword_data['answers']['down'][i]
		# 	clues.append(Clue(index, direction, question, answer))
#   	return clues
	def _collect_clues_by_direction(self, clues_data, direction, locations):
		clues = []
		for i, clue in enumerate(clues_data):
			index = int(clue.split(". ", 1)[0])
			question = clue.split(". ", 1)[1]
			answer = self.crossword_data['answers'][direction][i]
			span = locations.get(index, {}).get(direction, [])
			clues.append(Clue(index, direction, question, answer, span))
		return clues

	def collect_clues(self):
		locations = self.find_locations()
		across_clues = self._collect_clues_by_direction(self.crossword_data['clues']['across'], 'across', locations)
		down_clues = self._collect_clues_by_direction(self.crossword_data['clues']['down'], 'down', locations)
		return across_clues + down_clues

	# def find_locations(self):
	# 	grid_index_location = {}
	# 	grid = self.crossword_data['gridnums']
	# 	for row in range(self.rows):
	# 		for col in range(self.cols):
	# 			index = grid[row * self.cols + col]
	# 			if index != 0:
	# 				grid_index_location[index] = (row, col)
	# 	return grid_index_location
	def find_locations(self):
		grid_index_location = {}
		gridnums = self.crossword_data['gridnums']
		for row in range(self.rows):
			for col in range(self.cols):
				index = gridnums[row * self.cols + col]
				if index != 0:
					if index not in grid_index_location:
						grid_index_location[index] = {'across': [], 'down': []}
					# Now check whether this cell is part of an across clue or a down clue
					if col == 0 or (col > 0 and gridnums[row * self.cols + (col - 1)] != index):
						# This is the start of a clue going across or a standalone cell
						for c in range(col, self.cols):
							if gridnums[row * self.cols + c] == index:
								grid_index_location[index]['across'].append((row, c))
							else:
								break  # Stop if we reach the end of this clue
					if row == 0 or (row > 0 and gridnums[(row - 1) * self.cols + col] != index):
						# This is the start of a clue going down
						for r in range(row, self.rows):
							if gridnums[r * self.cols + col] == index:
								grid_index_location[index]['down'].append((r, col))
							else:
								break  # Stop if we reach the end of this clue
		return grid_index_location
	
	# def grid_extract(self, grid, location, length, direction):
	# 	row, col = location
	# 	index = row * self.cols + col
	# 	# grid = self.crossword_data['grid']
	# 	word = ""
	# 	# Check if the word fits within the grid horizontally
	# 	if direction == 'across':
	# 		word = ''.join(grid[index:index+length])
	# 	# Check if the word fits within the grid vertically
	# 	elif direction == 'down':
	# 		for i in range(length):
	# 			word += grid[index + i * self.cols]
	# 	return word
	def grid_extract(self, grid, location, length, direction):
		# Assuming location is a list of tuples [(row, col), (row, col), ...]
		word = ""
		# Check if the word fits within the grid horizontally
		if direction == 'across':
			# Assume the word is horizontal, take the row from the first tuple
			row = location[0][0]
			tiles = [grid[row * self.cols + col] for row, col in location]
			word = ''.join(tiles)
		# Check if the word fits within the grid vertically
		elif direction == 'down':
			# Assume the word is vertical, take the col from the first tuple
			col = location[0][1]
			tiles = [grid[row * self.cols + col] for row, col in location]
			word = ''.join(tiles)
		return word

	# def grid_insert(self, word, location, direction):
	# 	row, col = location
	# 	index = row * self.cols + col
	# 	grid = list(self.grid)

	# 	# Insert the word horizontally if it fits
	# 	if direction == 'across':
	# 		self.grid = grid[:index] + list(word) + grid[index + len(word):]
	# 	# Insert the word vertically if it fits
	# 	elif direction == 'down':
	# 		for i in range(len(word)):
	# 			self.grid[index + i * self.cols] = word[i]
 
	def grid_insert(self, word, locations, direction):
		grid = list(self.grid)

		for i, pos in enumerate(locations):
			row, col = pos
			if i < len(word):
				grid[row * self.cols + col] = word[i]

		self.grid = ''.join(grid) 
	
	def build_grid(self):
		return ['-' if c.isalpha() else '.' for c in self.crossword_data['grid']]

	def mask_answer(self, answer):
		return '*' * len(answer)

	def check_answer(self, guess, actual):
		return guess.lower() == actual.lower()

	def print_title(self):
		print("Title:", self.crossword_data['title'])

	def print_grid(self, grid):
		print("Grid:")
		for row in range(self.rows):
			for col in range(self.cols):
				print(grid[row * self.cols + col], end=" ")
			print()

	def print_size(self):
		print("\nSize:", self.crossword_data['size'])

def random_puzzle(date_combinations_file):
	with open(date_combinations_file, 'r') as file:
		reader = csv.reader(file)
		next(reader)  # Skip header
		date_combinations = [row for row in reader]
	year, month, day = random.choice(date_combinations)
	return CrosswordDataset(year, month, day)


if __name__ == "__main__":

	# Load a random puzzle
	# date_combinations_file = 'date_combinations.csv'
	# crossword = random_puzzle(date_combinations_file)

	# Load a specific puzzle (for testing)
	year = "2018"
	month = "03"
	day = "09"
	crossword = CrosswordDataset(year, month, day) # Creates a datastructure for the crossword puzzle

	# Printing out information for the given puzzle
	crossword.print_title()
	# crossword.print_size() # size of the puzzle

	# crossword.print_grid(crossword.crossword_data['gridnums']) # Grid numbers and their locations
	# crossword.print_grid(crossword.crossword_data['grid']) # Grid of the solved puzzle
	# crossword.print_grid(crossword.grid) # Grid which is slowly filled in over time (- is an empty space, . is a nonplayable space)

	# Verify clues are correct
	for clue in crossword.clues:
	    print(clue)

	# Verify locations of clues are correct
	# for number, location in crossword.locations.items():
	# 	print(f'Clue number: {number} Position: {location}')

	# Tests inserting into the solving grid given the word, location, and direction
	# for clue in crossword.clues:

	# 	crossword.grid_insert(clue.answer, crossword.locations[clue.index], clue.direction)

	# 	crossword.print_grid(crossword.grid) # this grid should look the same as the solved grid now
		
	# Testing extracting a word given a location, length, and direction
	# word = crossword.grid_extract(location, clue.length, clue.direction)
	# print(f'Word: {word} answer: {clue.answer}')

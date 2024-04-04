from CrosswordDataset import CrosswordDataset

class CrosswordGuess:
	def __init__(self, crossword, clue):
		
		self.location = crossword.locations[clue.index]
		self.direction = clue.direction
		self.question = clue.question
		self.length = len(clue.answer)
		self.guesses = []
		self.previous_guesses = [] # keep track of previous?
		# self.probablities # maybe the guesses are a tuple?
		self.make_guess(crossword)

	# this should be the function interacting with the llm api it will use self.question and self.length here
	# it will use those and known_letters (- if not) to prompt and return a list of values (perhaps probabilities too)
	def generate_guess(self, known_letters):
		# Placeholder implementation
		return ['RATPACK']

	def make_guess(self, crossword):
		known_letters = crossword.grid_extract(crossword.grid, self.location, self.length, self.direction)
		print(f'Known Letters: {known_letters}')

		self.guesses = self.generate_guess(known_letters)

		valid_guesses = []
		for guess in self.guesses:
			if self.word_fits(guess, known_letters):
				valid_guesses.append(guess)

		# if there are any valid guesses insert it (should have something like if there isnt this will be appended to the stack, queue of guessing)
		if valid_guesses:
			crossword.grid_insert(valid_guesses[0], self.location, self.direction)
			print('Inserted!') # just for debugging as of now
			self.previous_guesses.append((clue, valid_guesses[0]))
		else:
			print('Doesn\'t fit') 

	@staticmethod
	def word_fits(word, known_letters):
		if len(word) != len(known_letters):
			return False

		for i, letter in enumerate(word):
			if known_letters[i] != '-' and known_letters[i] != letter:
				return False

		return True

if __name__ == "__main__":

	# for testing, creates a static datastructure
	year = "2018"
	month = "03"
	day = "09"
	crossword = CrosswordDataset(year, month, day)

	crossword.print_title()

	clue = crossword.clues[0]
	# will need to have a stack or dictionary or something of these guesses and keep track if we have filled in something for a guess
	guess = CrosswordGuess(crossword, clue)

	crossword.print_grid(crossword.grid)

	# also should think about how we define the end state, easy if doing the stack harder if 


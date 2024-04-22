from CrosswordDataset import CrosswordDataset
import json
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()

# Retrieve API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

def request_guesses(input_clue):
	client = OpenAI(api_key=api_key)

	completion = client.chat.completions.create(
		model="gpt-3.5-turbo",
		messages=[
			{"role": "system", "content": "As a seasoned crossword puzzle enthusiast, your expertise lies in crafting accurate solutions based on provided clues. Your knack for generating answers shines through as you consistently offer a curated selection of possibilities that align with the given criteria. Your objective is to reliably present five potential solutions, neatly organized in JSON format under the key 'guesses'.\nIncoming requests adhere strictly to a standardized JSON format:\nClue: A string representing the given clue. \nLength: The length of the target word. \nknown_characters: A string indicating known characters in the word. Unknown characters are denoted by '-', while known characters are represented as themselves. \n This standardized format ensures seamless communication between users and the API, facilitating efficient query processing and response generation."},
			{"role": "user", "content": input_clue}
		]
	)

	output = completion.choices[0].message

	content = json.loads(output.content)

	guesses = content.get("guesses", [])

	cleaned_guesses = [guess.replace(" ", "").upper() for guess in guesses]

	print(f'Guesses: {cleaned_guesses}')

	return cleaned_guesses

class Guess:

	def __init__(self, crossword, clue):
		
		self.location = crossword.locations[clue.index]
		self.direction = clue.direction
		self.question = clue.question
		self.answer = clue.answer
		self.length = clue.length
		self.guesses = []
		self.previous_guesses = [] # keep track of previous?
		# self.probablities # maybe the guesses are a tuple?
		# print(f'Clue question: {clue.question}')
		# print(f'Answer: {clue.answer}')
		self.make_guess(crossword)

		# return self.test(crossword)

	# this should be the function interacting with the llm api it will use self.question and self.length here
	# it will use those and known_letters (- if not) to prompt and return a list of values (perhaps probabilities too)
	def generate_guess(self, known_characters):
		# Placeholder implementation
		input_clue = json.dumps({
            "clue": self.question,
            "length": self.length,
            "known_characters": known_characters
        })

		return request_guesses(input_clue)

	def make_guess(self, crossword):
		known_characters = crossword.grid_extract(crossword.grid, self.location, self.length, self.direction)
		# print(f'Known Letters: {known_characters}')

		self.guesses = self.generate_guess(known_characters)

		valid_guesses = []
		for guess in self.guesses:
			if self.word_fits(guess, known_characters):
				valid_guesses.append(guess)

		# if there are any valid guesses insert it (should have something like if there isnt this will be appended to the stack, queue of guessing)
		if valid_guesses:
			best_guess = valid_guesses[0]
			print(f'Guess: {best_guess.upper()} Answer: {self.answer.upper()}')
			if best_guess.upper() == self.answer.upper():
				crossword.correct_guesses += 1
				print('Correct guess!')
		
			crossword.grid_insert(best_guess, self.location, self.direction)
			print('Inserted!') # just for debugging as of now
			# self.previous_guesses.append((clue, valid_guesses[0]))
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

	for clue in crossword.clues:
		Guess(crossword, clue)

	# clue = crossword.clues[0]
	# # will need to have a stack or dictionary or something of these guesses and keep track if we have filled in something for a guess
	# Guess(crossword, clue)

	crossword.print_grid(crossword.grid)
	print(f'Correct guesses: {crossword.correct_guesses}')

	# also should think about how we define the end state, easy if doing the stack harder if 


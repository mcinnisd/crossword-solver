from CrosswordDataset import CrosswordDataset
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Retrieve API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

def strip_non_letters(text):
    """Remove everything except letters from the text."""
    return re.sub(r'[^a-zA-Z]', '', text) if isinstance(text, str) else '' 


def get_prompt(known_characters=False):
    base_prompt = (
        "As a seasoned crossword puzzle enthusiast, your expertise lies in crafting accurate solutions "
        "based on provided clues. Your knack for generating answers shines through as you consistently "
        "offer a curated selection of possibilities that align with the given criteria. Your objective "
        "is to reliably present ten potential solutions, neatly organized in JSON format under the key "
        "'guesses'.\n"
    )
    prompt_end = (
        "Incoming requests adhere strictly to a standardized JSON format:\n"
        "Clue: A string representing the given clue.\n"
        "Length: The length of the target word. "
    )
    if known_characters:
		
        prompt_end += ("\nknown_characters: A string indicating known characters in the word. "
        "Unknown characters are denoted by '-', while known characters are represented as themselves. ")
        
    return base_prompt + prompt_end

def request_guesses(input_clue, use_known):
	client = OpenAI(api_key=api_key)
	
	message=[
				{"role": "system", "content": get_prompt(use_known)},
				{"role": "user", "content": input_clue}
			]
	completion = client.chat.completions.create(
		model="gpt-3.5-turbo", messages=message)
	output = completion.choices[0].message
	
	try:
		content = json.loads(output.content)
	except json.decoder.JSONDecodeError as e:
		# Log the error and return an empty list
		print(f"Error decoding JSON: {e}")
		print(f"Raw output: {output.content}")
		return []

	guesses_value = content.get("guesses", {})

	if isinstance(guesses_value, list):  # If guesses is already a list
		guesses_list = guesses_value
	elif isinstance(guesses_value, dict):  # If guesses is a dictionary
		guesses_list = list(guesses_value.values())
	else:
		guesses_list = []

	return [strip_non_letters(guess.upper()) if isinstance(guess, str) else '' for guess in guesses_list]

class Guess:

	def __init__(self, crossword, clue):
		
		self.location = crossword.locations[clue.index]
		self.direction = clue.direction
		self.question = clue.question
		self.answer = clue.answer
		self.length = clue.length
		self.guesses = []
		self.make_guess(crossword)

	def generate_guess(self, known_characters, use_known):
		# Placeholder implementation
		if use_known:
			input_clue = json.dumps({
				"clue": self.question,
				"length": self.length,
				"known_characters": known_characters
			})
		else:
			input_clue = json.dumps({
				"clue": self.question,
				"length": self.length
			})

		return request_guesses(input_clue, use_known)
	
	def contain_letter(self, word):
		return any(char != '-' for char in word)

	def check_insert(self, crossword):

		for guess in self.guesses:
			if guess.upper() == self.answer.upper():
				crossword.correct_guesses += 1
				crossword.grid_insert(guess.upper(), self.location, self.direction)
				break

		# if self.guesses:
		# 	best_guess = self.guesses[0]
		# 	# print(f'Guess: {best_guess.upper()} Answer: {self.answer.upper()}')
		# 	if best_guess.upper() == self.answer.upper():
		# 		crossword.correct_guesses += 1
		
		# 	crossword.grid_insert(best_guess, self.location, self.direction)
		# 	print('Inserted!\n') # just for debugging as of now

		# else:
		# 	print('Doesn\'t fit\n') 

	def make_guess(self, crossword):

		known_characters = crossword.grid_extract(crossword.grid, self.location, self.length, self.direction)
  
		if '-' in known_characters:

			self.guesses = self.generate_guess(known_characters, crossword.use_known)

			valid_guesses = []
			for guess in self.guesses:
				if crossword.use_known:
					if self.contain_letter(guess):
						if self.word_fits(guess, known_characters, True):
							valid_guesses.append(guess)
				else:
					if self.word_fits(guess, known_characters):
						valid_guesses.append(guess)

			self.guesses = valid_guesses

			self.check_insert(crossword)
		else:
			crossword.correct_guesses += 1

	@staticmethod
	def word_fits(word, known_letters, check_letters=False):
		if len(word) != len(known_letters):
			return False

		if check_letters:
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
	# crossword = CrosswordDataset(year, month, day, ifsorted=True)

	crossword.print_title()

	for clue in crossword.clues:
		Guess(crossword, clue)

	crossword.use_known = True
	for _ in range(7):
		crossword.print_grid(crossword.grid)
		print(f'Correct guesses: {crossword.correct_guesses} out of {len(crossword.clues)}')
		crossword.correct_guesses = 0
		
		for clue in crossword.clues:
			Guess(crossword, clue)

	crossword.print_grid(crossword.grid)
	print(f'Correct guesses: {crossword.correct_guesses} out of {len(crossword.clues)}')


	# tripple redundancy

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
    # Remove everything except letters using regex
	if isinstance(text, str):
		# Remove everything except letters using regex
		return re.sub(r'[^a-zA-Z]', '', text)
	else:
		return '' 
    # return re.sub(r'[^a-zA-Z]', '', text)

def request_guesses(input_clue, use_known):
	client = OpenAI(api_key=api_key)
	prompt_no_known = "As a seasoned crossword puzzle enthusiast, your expertise lies in crafting accurate solutions based on provided clues. Your knack for generating answers shines through as you consistently offer a curated selection of possibilities that align with the given criteria. Your objective is to reliably present five potential solutions, neatly organized in JSON format under the key 'guesses'.\nIncoming requests adhere strictly to a standardized JSON format:\nClue: A string representing the given clue. \nLength: The length of the target word. \n This standardized format ensures seamless communication between users and the API, facilitating efficient query processing and response generation."
	# prompt_10_no_known = "As a seasoned crossword puzzle enthusiast, your expertise lies in crafting accurate solutions based on provided clues. Your knack for generating answers shines through as you consistently offer a curated selection of possibilities that align with the given criteria. Your objective is to reliably present ten potential solutions, neatly organized in JSON format under the key 'guesses'.\nIncoming requests adhere strictly to a standardized JSON format:\nClue: A string representing the given clue. \nLength: The length of the target word. \n This standardized format ensures seamless communication between users and the API, facilitating efficient query processing and response generation."
	# prompt_known_characters = "As a seasoned crossword puzzle enthusiast, your expertise lies in crafting accurate solutions based on provided clues. Your knack for generating answers shines through as you consistently offer a curated selection of possibilities that align with the given criteria. Your objective is to reliably present five potential solutions, neatly organized in JSON format under the key 'guesses'.\nIncoming requests adhere strictly to a standardized JSON format:\nClue: A string representing the given clue. \nLength: The length of the target word. \nknown_characters: A string indicating known characters in the word. Unknown characters are denoted by '-', while known characters are represented as themselves. \n This standardized format ensures seamless communication between users and the API, facilitating efficient query processing and response generation."
	# prompt_known_firstlast = "As a seasoned crossword puzzle enthusiast, your expertise lies in crafting accurate solutions based on provided clues. Your knack for generating answers shines through as you consistently offer a curated selection of possibilities that align with the given criteria. Your objective is to reliably present five potential solutions, neatly organized in JSON format under the key 'guesses'.\nIncoming requests adhere strictly to a standardized JSON format:\nClue: A string representing the given clue. \nLength: The length of the target word. \nknown_first: A character indicating the first known letter in the word 'None' if not known. \nknown_last: A character indicating the last known letter in the word 'None' if not known. \n This standardized format ensures seamless communication between users and the API, facilitating efficient query processing and response generation."
	prompt_known_first = "As a seasoned crossword puzzle enthusiast, your expertise lies in crafting accurate solutions based on provided clues. Your knack for generating answers shines through as you consistently offer a curated selection of possibilities that align with the given criteria. Your objective is to reliably present five potential solutions, neatly organized in JSON format under the key 'guesses'.\nIncoming requests adhere strictly to a standardized JSON format:\nClue: A string representing the given clue. \nLength: The length of the target word. \nknown_first: A character indicating the first known letter in the word 'None' if not known. \n This standardized format ensures seamless communication between users and the API, facilitating efficient query processing and response generation."
	# prompt_known_last = "As a seasoned crossword puzzle enthusiast, your expertise lies in crafting accurate solutions based on provided clues. Your knack for generating answers shines through as you consistently offer a curated selection of possibilities that align with the given criteria. Your objective is to reliably present five potential solutions, neatly organized in JSON format under the key 'guesses'.\nIncoming requests adhere strictly to a standardized JSON format:\nClue: A string representing the given clue. \nLength: The length of the target word. \nknown_last: A character indicating the last known letter in the word 'None' if not known. \n This standardized format ensures seamless communication between users and the API, facilitating efficient query processing and response generation."

	if use_known:
		# message=[
		# 	{"role": "system", "content": prompt_known_characters},
		# 	{"role": "user", "content": input_clue}
		# ]
		message=[
			{"role": "system", "content": prompt_known_first},
			{"role": "user", "content": input_clue}
		]
	else:
		message=[
			{"role": "system", "content": prompt_no_known},
			{"role": "user", "content": input_clue}
		]
	completion = client.chat.completions.create(
		model="gpt-3.5-turbo", messages=message)
	output = completion.choices[0].message
	# print(f"Raw output: {output.content}")

	# content = json.loads(output.content)
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

	# cleaned_guesses = [strip_non_letters(guess.upper()) for guess in guesses_list]
	cleaned_guesses = [strip_non_letters(guess.upper()) if isinstance(guess, str) else '' for guess in guesses_list]


	# print(f'Guesses: {cleaned_guesses}')

	return cleaned_guesses

class Guess:

	def __init__(self, crossword, clue):
		
		self.location = crossword.locations[clue.index]
		self.direction = clue.direction
		self.question = clue.question
		self.answer = clue.answer
		self.length = clue.length
		# self.use_known = False
		self.guesses = []
		# self.previous_guesses = [] # keep track of previous?
		# self.probablities # maybe the guesses are a tuple?
		# print(f'Clue question: {clue.question}')
		# print(f'Answer: {clue.answer}')
		self.make_guess(crossword)

		# return self.test(crossword)


	def get_first(self, word):
		# Split the word into individual characters
		# characters = word.split()

		# # Remove any spaces
		# characters = [char.strip() for char in characters]

		# Check if the first character is a dash
		if word[0] == '-':
			first_char = None
		else:
			first_char = word[0]
		return first_char
		# 	last_char = characters[-1]
		# elif characters[-1] == '-':
		# 	first_char = characters[0]
		# 	last_char = None
		# else:
		# 	first_char = characters[0]
		# 	last_char = characters[-1]

		# return first_char, last_char
	# this should be the function interacting with the llm api it will use self.question and self.length here
	# it will use those and known_letters (- if not) to prompt and return a list of values (perhaps probabilities too)
	def generate_guess(self, known_characters, use_known):
		# Placeholder implementation
		if use_known:
			# input_clue = json.dumps({
			# 	"clue": self.question,
			# 	"length": self.length,
			# 	"known_characters": known_characters
			# })
			first_char = self.get_first(known_characters)
			print(f'First Char: {first_char}')
			input_clue = json.dumps({
				"clue": self.question,
				"length": self.length,
				"known_first": first_char
			})
		else:
			input_clue = json.dumps({
				"clue": self.question,
				"length": self.length,
				# "known_characters": known_characters
			})


		# I THINK THAT THE BEST CHARACTERS SHOULD BE GOTTEN RID OF IT DOESNT SEEM TO PROVE USEFUL IF THE WRONG PATH IS TAKEN

		return request_guesses(input_clue, use_known)
	
	def check_insert(self, crossword):
		print(f'Answer: {self.answer}')
		print(f'Valid guesses: {self.guesses}')

		for guess in self.guesses:
			# print(f'Guess: {best_guess.upper()} Answer: {self.answer.upper()}')
			if guess.upper() == self.answer.upper():
				crossword.correct_guesses += 1
				crossword.grid_insert(guess.upper(), self.location, self.direction)
				print('Correct guess!\n')
				break

				# print('None correct\n') 


		# BELOW IS FOR INSERTION
		# if there are any valid guesses insert it (should have something like if there isnt this will be appended to the stack, queue of guessing)
		# if self.guesses:
		# 	best_guess = self.guesses[0]
		# 	# print(f'Guess: {best_guess.upper()} Answer: {self.answer.upper()}')
		# 	if best_guess.upper() == self.answer.upper():
		# 		crossword.correct_guesses += 1
		# 		print('Correct guess!')
		
		# 	crossword.grid_insert(best_guess, self.location, self.direction)
		# 	print('Inserted!\n') # just for debugging as of now

		# else:
		# 	print('Doesn\'t fit\n') 

	def make_guess(self, crossword):

		known_characters = crossword.grid_extract(crossword.grid, self.location, self.length, self.direction)
		# print(f'Known Letters: {known_characters}')
  
		if '-' in known_characters:

			self.guesses = self.generate_guess(known_characters, crossword.use_known)

			# print(f'Guesses: {self.guesses}')

			valid_guesses = []
			for guess in self.guesses:
				if self.word_fits(guess, known_characters):
					valid_guesses.append(guess)

			self.guesses = valid_guesses

			# print(f'Guesses: {self.guesses}')

			# if there are any valid guesses insert it (should have something like if there isnt this will be appended to the stack, queue of guessing)
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
	# print(f'Using Known? {crossword.use_known}')

	for clue in crossword.clues:
		Guess(crossword, clue)

	# print(f'Correct guesses: {crossword.correct_guesses} out of {len(crossword.clues)}')
	for _ in range(2):
		crossword.correct_guesses = 0
		crossword.use_known = True
		for clue in crossword.clues:
			Guess(crossword, clue)


	# clue = crossword.clues[0]
	# # will need to have a stack or dictionary or something of these guesses and keep track if we have filled in something for a guess
	# Guess(crossword, clue)

	crossword.print_grid(crossword.grid)
	print(f'Correct guesses: {crossword.correct_guesses} out of {len(crossword.clues)}')

	# also should think about how we define the end state, easy if doing the stack harder if 


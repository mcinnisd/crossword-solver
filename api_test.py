from openai import OpenAI
from dotenv import load_dotenv
import os
import json
from CrosswordDataset import CrosswordDataset
from CrosswordSolver import Guess

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

  output_guesses = completion.choices[0].message

  content = json.loads(output_guesses.content)

    # Get the list of guesses from the JSON content
  guesses = content.get("guesses", [])

    # Strip spaces and convert all words to uppercase
  cleaned_guesses = [guess.replace(" ", "").upper() for guess in guesses]

  return cleaned_guesses

  # print(f'Output: {output_guesses}')
  # return output_guesses


if __name__ == "__main__":
  # for testing, creates a static datastructure
  year = "2018"
  month = "03"
  day = "09"
  crossword = CrosswordDataset(year, month, day)

  crossword.print_title()

  clue = crossword.clues[0]
  # will need to have a stack or dictionary or something of these guesses and keep track if we have filled in something for a guess
  guess = Guess(crossword, clue)

  output = request_guesses(guess.test(crossword))

  print(output)

  # print(f'Input: {guess.test(crossword)}')


	# crossword.print_grid(crossword.grid)
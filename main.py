import os
import openai
from openai import OpenAI


# Required Imports to complete the assignment.
import json
from dotenv import load_dotenv

# Load environment variables from .env file instead of setting system wide env variable
load_dotenv()

# Intializing the openai setup
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

Given more time, I would focus on enhancing the user experience by building a graphical user interface (GUI) and integrating text-to-speech module to read stories aloud, creating a more immersive bedtime experience.
I would also try to integrate other AI models apart from OPENAI to give the user a choice to select from different AI models to listen to a story from.

Start Time: 11/10/2025 - 17:49 CST
End Time: 11/10/2025 - 19:10 CST
"""

# Checking if the OPENAI_API_KEY is fetched from the .env file or not.
try:
    client.api_key = os.getenv("OPENAI_API_KEY")
    if client.api_key is None:
        raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
except ValueError as e:
    print(f"Error: {e})")
    exit()

MAX_REFINEMENT_CYCLES = 3
JUDGE_PASSING_SCORE = 8


# Setting Prompts for the System to use while completing the Task
STORYTELLER_PROMPT_TEMPLATE = """
You are a master storyteller for young children.
Please write a short story, engagin, and imaginative bedtime story appropriate for a 5 to 10 - year old.
The story should be simple, easy to understand, and have a positive message.

The user wants a story about: "{request}"
"""

JUDGING_PROMPT_TEMPLATE = """
You are a literary critic specializinng in children's literature. Your task is to evaluate a story based on a cllear rubric.
Provide a score from 1 to 10 for each category and then a final "overall_score".
Your feedback should be constructive and specific to help the storyteller imporve.

The story must be :
1.  **Age-Appropriate**: Language and themes suitable for ages 5-10.
2.  **Engaging**: Captivating and holds a child's attention.
3.  **Coherent**: The plot is logical and easy to follow.
4.  **Positive**: Conveys a poistive message or moral.

Here is the story:
-----------------------------
{story} 
-----------------------------

Please provide your evaluation in the following JSON format like this example:
{{
    "scores": {{
        "age_appropriateness": 8,
        "engagement": 7,
        "coherence": 9,
        "positivity": 8
    }},
    "overall_score": 8,
    "feedback": "The story is good, but the pacing could be a bit faster to keep a younger child engaged. Consider adding more descriptive language for the main character's feelings."
}}
"""

REWRITING_PROMPT_TEMPLATE = """
You are a skilled editor tasked with rewriting a children's story based on a critic's feedback.
Your goal is to incorporate the feedback to create a much-imporved version of the story.

Original user request: "{request}"

Here is the original story:
-----------------------------
{story} 
-----------------------------

Here is the critic's feedback:
-----------------------------
{feedback} 
-----------------------------

Now, please provide the revised and improved story.

"""
def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
    try:
        # Commenting out legacy code from the boiler plate to use the correct implementation of the OPENAI for python.
        # 
        # openai.api_key = os.getenv("OPENAI_API_KEY") # please use your own openai api key here.
        # resp = openai.ChatCompletion.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": prompt}],
        #     stream=False,
        #     max_tokens=max_tokens,
        #     temperature=temperature,
        # )
        # client.api_key = os.getenv("OPENAI_API_KEY")
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            stream=False,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content
    except openai.AuthenticationError:
        print("AuthenticationError: Please check you OPENAI_API_KEY.")
        exit()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        exit()

# Function for story telling
def run_storyteller(request: str) -> str:
    """ Generates Initial Story """
    print("*** Generating Initial Story ***")
    prompt = STORYTELLER_PROMPT_TEMPLATE.format(request=request)
    story = call_model(prompt)
    return story

# Function to judge the story
def run_judge(story: str) -> dict:
    """ Judges the story and returns the structured feedback. """
    print("*** Judging the Generated Story ***")
    prompt = JUDGING_PROMPT_TEMPLATE.format(story=story)
    feedback_str = call_model(prompt, temperature=0.1)
    try:
        # Cleaning the JSON if the model wraps the output in markdown.
        if feedback_str.startswith("```json"):
            feedback_str = feedback_str.removeprefix("```json\n").strip("\n```")
        feedback = json.loads(feedback_str)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the feedback provided by the Judge. Using the story as is.")
        # Return a 'passing' score to prevent errors or crash
        feedback = {"overall_score": JUDGE_PASSING_SCORE, "feedback": "N/A"}
    return feedback

# Function to rewrite the story as per the feedback
def run_rewriter(request: str, story: str, feedback: dict) -> str:
    """ Rewrites the story based on the feedback. """
    print("*** Rewriting the Story ***")
    prompt = REWRITING_PROMPT_TEMPLATE.format(request=request, story=story, feedback=feedback)
    revised_story = call_model(prompt)
    return revised_story

example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."

def main():
    """ Main function to run the story generation process. """
    print("---- Welcome to the Bedtime Storyteller! ----")
    user_input = input("What kind of story do you want to hear? \n> ")
    
    if not user_input:
        user_input = example_requests
        print(f"No user inout provided, using example request: '{user_input}'")

    story = run_storyteller(user_input)
    
    for i in range(MAX_REFINEMENT_CYCLES):
        print(f"\n---- Refinement Cycle {i + 1}/{MAX_REFINEMENT_CYCLES} ----")
        feedback_data = run_judge(story)
        overall_score = feedback_data.get("overall_score", 0)
        feedback_text = feedback_data.get("feedback", "No feedback provided.")
        
        print(f"Overall Score: {overall_score}/10")
        print(f"Feedback: {feedback_text}")
        
        if overall_score >= JUDGE_PASSING_SCORE:
            print("\n The Judge is Happy with the Story! Here is the final version.")
            break
        story = run_rewriter(user_input, story, feedback_text)
    else:
        print("\n Maximum refinement cycles reached. Here is the final version of the story.")

    print("\n ---- Final Story ---")
    print(story)
    print("\n----------------------")


if __name__ == "__main__":
    main()
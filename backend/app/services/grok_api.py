import os
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT
from dotenv import load_dotenv

load_dotenv()

#  It Loads API key from environment variables
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is not set")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def grok_chat_completion(prompt: str, max_tokens=600):
    """
    Function:
    Generate an answer from Anthropic's Grok model based on the input prompt.


    Returns:
    The model's text completion with leading/trailing whitespace stripped.
    """
    response = client.completions.create(
        model="grok-1",
        prompt=HUMAN_PROMPT + prompt + AI_PROMPT,
        max_tokens_to_sample=max_tokens,
        stop_sequences=[HUMAN_PROMPT]
    )
    return response.completion.strip()

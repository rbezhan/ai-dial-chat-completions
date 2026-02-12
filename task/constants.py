from dotenv import load_dotenv
import os

load_dotenv()
DEFAULT_SYSTEM_PROMPT = "You are an assistant who answers concisely and informatively."
DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
API_KEY = os.getenv('DIAL_API_KEY', '')
if not API_KEY:
    raise RuntimeError("DIAL_API_KEY is not set")
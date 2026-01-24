import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

load_dotenv(override = True)
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
GPT_API_KEY = os.getenv('GPT_API_KEY')
MODEL = os.getenv('MODEL')
BASE_URL = os.getenv('BASE_URL')

def get_llm():
    """Initialize and return the model"""
    llm = ChatOpenAI(
        base_url=BASE_URL,
        api_key=GPT_API_KEY,
        model = MODEL
    )
    
    return llm
    


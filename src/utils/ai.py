"""
AI integration utilities using OpenAI's API
"""
import os
import logging
import openai

from config.settings import OPENAI_MODEL, OPENAI_MAX_TOKENS

logger = logging.getLogger(__name__)

def setup_openai():
    """Configure OpenAI with API key"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logger.error("OpenAI API key not found in environment variables")
        return False
        
    openai.api_key = api_key
    return True

def get_ai_assistance(prompt, model=None, max_tokens=None):
    """
    Get assistance from AI for various tasks
    
    Args:
        prompt (str): The prompt to send to the AI
        model (str, optional): OpenAI model to use
        max_tokens (int, optional): Maximum tokens for response
        
    Returns:
        str: AI generated response
    """
    model = model or OPENAI_MODEL
    max_tokens = max_tokens or OPENAI_MAX_TOKENS
    
    if not setup_openai():
        return "AI assistance unavailable - missing API key"
    
    try:
        # Create a chat completion using OpenAI API
        response = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise information and analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        
        # Extract and return the response text
        return response.choices[0].message.content
        
    except Exception as e:
        logger.error(f"Error getting response from OpenAI: {e}")
        return f"Error getting AI assistance: {str(e)}"
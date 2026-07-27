import os
from typing import Optional, Type, TypeVar, Dict, Any, List
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

# Load environment variables from .env file
load_dotenv()

# Model identifier constants
MODEL_FAST = "llama-3.1-8b-instant"
MODEL_VERSATILE = "llama-3.3-70b-versatile"

T = TypeVar("T", bound=BaseModel)


def get_groq_client() -> Groq:
    """
    Initialize and return a Groq client instance.
    Ensures GROQ_API_KEY is loaded from environment or .env file.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY is not set in environment or .env file.")
    return Groq(api_key=api_key)


def generate_chat_completion(
    messages: List[Dict[str, str]],
    model: str = MODEL_VERSATILE,
    temperature: float = 0.2,
    response_format: Optional[Dict[str, str]] = None,
) -> str:
    """
    Execute a chat completion request using the Groq SDK.
    
    :param messages: List of message dictionaries with 'role' and 'content'
    :param model: Groq model ID ('gemma2-9b-it' or 'llama-3.3-70b-versatile')
    :param temperature: Sampling temperature
    :param response_format: Optional response format specifier e.g. {"type": "json_object"}
    :return: Generated text response
    """
    client = get_groq_client()
    kwargs: Dict[str, Any] = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    if response_format:
        kwargs["response_format"] = response_format

    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content or ""


def generate_structured_output(
    prompt: str,
    response_model: Type[T],
    system_prompt: Optional[str] = None,
    model: str = MODEL_VERSATILE,
    temperature: float = 0.1,
) -> T:
    """
    Generate a response structured according to a given Pydantic model using JSON mode.
    
    :param prompt: User prompt or text input
    :param response_model: Pydantic model class to validate output against
    :param system_prompt: Optional system prompt instructions
    :param model: Groq model identifier
    :param temperature: Sampling temperature
    :return: Instance of response_model populated with parsed output
    """
    schema_json = response_model.model_json_schema()
    
    sys_instruction = (
        system_prompt
        or "You are an AI assistant for an Enterprise Pharmaceutical Complaint Management system."
    )
    sys_instruction += f"\nYou MUST output valid JSON matching this schema:\n{schema_json}"

    messages = [
        {"role": "system", "content": sys_instruction},
        {"role": "user", "content": prompt},
    ]

    raw_response = generate_chat_completion(
        messages=messages,
        model=model,
        temperature=temperature,
        response_format={"type": "json_object"},
    )

    return response_model.model_validate_json(raw_response)

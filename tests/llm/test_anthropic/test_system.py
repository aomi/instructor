import pytest
import instructor
from pydantic import BaseModel
from itertools import product
from .util import models, modes
from anthropic.types.message import Message


class User(BaseModel):
    name: str
    age: int


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_creation(model, mode, client):
    client = instructor.from_anthropic(client, mode=mode)
    response = client.chat.completions.create(
        model=model,
        response_model=User,
        messages=[
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "<story>Mike is 37 years old</story>"}
                ],
            },
            {
                "role": "user",
                "content": "Extract a user from the story.",
            },
        ],
        temperature=1,
        max_tokens=1000,
    )

    # Assertions to validate the response
    assert isinstance(response, User)
    assert response.name == "Mike"
    assert response.age == 37


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_creation_with_system_cache(model, mode, client):
    client = instructor.from_anthropic(client, mode=mode, enable_prompt_caching=True)
    response, message = client.chat.completions.create_with_completion(
        model=model,
        response_model=User,
        messages=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "<story>Mike is 37 years old " * 200 + "</story>",
                        "cache_control": {"type": "ephemeral"},
                    },
                    {
                        "type": "text",
                        "text": "You are a helpful assistant who extracts users from stories.",
                    },
                ],
            },
            {
                "role": "user",
                "content": "Extract a user from the story.",
            },
        ],
        temperature=1,
        max_tokens=1000,
    )

    # Assertions to validate the response
    assert isinstance(response, User)
    assert response.name == "Mike"
    assert response.age == 37

    # Assert a cache write or cache hit
    assert (
        message.usage.cache_creation_input_tokens > 0
        or message.usage.cache_read_input_tokens > 0
    )


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_creation_with_system_cache_anthropic_style(model, mode, client):
    client = instructor.from_anthropic(client, mode=mode, enable_prompt_caching=True)
    response, message = client.chat.completions.create_with_completion(
        model=model,
        system=[
            {
                "type": "text",
                "text": "<story>Mike is 37 years old " * 200 + "</story>",
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": "You are a helpful assistant who extracts users from stories.",
            },
        ],
        response_model=User,
        messages=[
            {
                "role": "user",
                "content": "Extract a user from the story.",
            },
        ],
        temperature=1,
        max_tokens=1000,
    )

    # Assertions to validate the response
    assert isinstance(response, User)
    assert response.name == "Mike"
    assert response.age == 37

    # Assert a cache write or cache hit
    assert (
        message.usage.cache_creation_input_tokens > 0
        or message.usage.cache_read_input_tokens > 0
    )


@pytest.mark.parametrize("model, mode", product(models, modes))
def test_creation_no_response_model(model, mode, client):
    client = instructor.from_anthropic(client, mode=mode)
    response = client.chat.completions.create(
        response_model=None,
        model=model,
        messages=[
            {
                "role": "system",
                "content": [{"type": "text", "text": "Mike is 37 years old"}],
            },
            {
                "role": "user",
                "content": "Extract a user from the story.",
            },
        ],
        temperature=1,
        max_tokens=1000,
    )

    # Assertions to validate the response
    assert isinstance(response, Message)
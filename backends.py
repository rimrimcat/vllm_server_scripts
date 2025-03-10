import json
from typing import (
    Any,
    AsyncIterator,
    Generic,
    Literal,
    NotRequired,
    Optional,
    Protocol,
    Sequence,
    TypedDict,
    TypeVar,
    Unpack,
)

import aiohttp
import requests
from typing_extensions import override

from settings import ANTHROPIC_API_KEY, OPENAI_API_KEY, OPENROUTER_API_KEY
from typs import Anthropic as AnthropicTypes
from typs import ChatCompletionParams, Messages, TextCompletionParams
from typs import OpenAI as OpenAITypes
from typs import OpenRouter as OpenRouterTypes

T = TypeVar("T")
S = TypeVar("S")


# # TYPES


class CompletionResponse(TypedDict, total=True):
    id: str
    choices: list["CompletionChoice"]


class CompletionChoice(TypedDict, total=True):
    text: str
    index: int
    finish_reason: str


class ChatCompletionResponse(TypedDict, total=True):
    id: str
    choices: list["ChatCompletionChoice"]


class ChatCompletionChoice(TypedDict, total=True):
    message: Messages.TextOnlyMessage.t


class GenerationResponse(TypedDict, total=True):
    data: "GenerationResponseData"


class GenerationResponseData(TypedDict, total=True):
    id: str
    total_cost: float
    created_at: str
    model: str
    origin: str
    usage: float
    is_byok: bool
    upstream_id: str
    cache_discount: str
    app_id: int
    streamed: bool
    cancelled: bool
    provider_name: str
    latency: int
    moderation_latency: int
    generation_time: int
    finish_reason: str
    native_finish_reason: str
    tokens_prompt: int
    tokens_completion: int
    native_tokens_prompt: int
    native_tokens_completion: int
    native_tokens_reasoning: int
    num_media_prompt: int
    num_media_completion: int
    num_search_results: int


class ModelsResponse(TypedDict, Generic[T], total=True):
    data: list[T]


class Endpoints(TypedDict, total=False):
    completion: str
    chat_completion: str
    generation: str
    models: str


# # BACKENDS
def default_endpoints(base_url) -> Endpoints:
    return {
        "completion": f"{base_url}/completions",
        "chat_completion": f"{base_url}/chat/completions",
        "generation": f"{base_url}/generations",
        "models": f"{base_url}/models",
    }


def default_headers(api_key) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


class Base:
    BASE_URL: str
    API_KEY: str
    HEADER: dict[str, str]
    ENDPOINTS: Endpoints

    @classmethod
    def text_completion(cls, **kwargs: Unpack[TextCompletionParams]):
        return requests.post(
            cls.ENDPOINTS["completion"],
            headers=cls.HEADER,
            data=json.dumps(kwargs),
        ).json()

    @classmethod
    def chat_completion(cls, **kwargs: Unpack[ChatCompletionParams]):
        return requests.post(
            cls.ENDPOINTS["chat_completion"],
            headers=cls.HEADER,
            data=json.dumps(kwargs),
        ).json()

    @classmethod
    def generation(cls, id: str):
        return requests.get(
            cls.ENDPOINTS["generation"],
            headers=cls.HEADER,
            data=json.dumps({"id": id}),
        ).json()

    @classmethod
    def models(cls):
        return requests.get(
            cls.ENDPOINTS["models"],
            headers=cls.HEADER,
        ).json()


class Local:
    def __init__(
        self,
        base_url: str,
        api_key: str = "",
    ) -> None:
        self.BASE_URL = base_url
        self.API_KEY = api_key
        self.HEADER = default_headers(api_key)
        self.ENDPOINTS = default_endpoints(base_url)

    def text_completion(self, **kwargs: Unpack[TextCompletionParams]):
        return requests.post(
            self.ENDPOINTS["completion"],
            headers=self.HEADER,
            data=json.dumps(kwargs),
        ).json()

    def chat_completion(self, **kwargs: Unpack[ChatCompletionParams]):
        return requests.post(
            self.ENDPOINTS["chat_completion"],
            headers=self.HEADER,
            data=json.dumps(kwargs),
        ).json()

    def generation(self, id: str):
        return requests.get(
            self.ENDPOINTS["generation"],
            headers=self.HEADER,
            data=json.dumps({"id": id}),
        ).json()

    def models(self):
        return requests.get(
            self.ENDPOINTS["models"],
            headers=self.HEADER,
        ).json()


class OpenAI(Base):
    BASE_URL: str = "https://api.openai.com/v1"
    API_KEY: str = OPENAI_API_KEY
    HEADER: dict[str, str] = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    ENDPOINTS: Endpoints = {
        "completion": f"{BASE_URL}/completions",
        "chat_completion": f"{BASE_URL}/chat/completions",
        "generation": f"{BASE_URL}/generations",
        "models": f"{BASE_URL}/models",
    }

    @classmethod
    def completion(cls, **kwargs: Unpack[TextCompletionParams]) -> CompletionResponse:
        return super().text_completion(**kwargs)

    @classmethod
    def chat_completion(
        cls, **kwargs: Unpack[ChatCompletionParams]
    ) -> ChatCompletionResponse:
        return super().chat_completion(**kwargs)

    @classmethod
    def generation(cls, id: str) -> GenerationResponse:
        return super().generation(id)

    @classmethod
    def models(cls) -> OpenAITypes.ModelsResponse.t:
        return super().models()


class Anthropic(Base):
    BASE_URL: str = "https://api.anthropic.com/v1"
    API_KEY: str = ANTHROPIC_API_KEY
    HEADER: dict[str, str] = {
        "x-api-key": f"{API_KEY}",
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    ENDPOINTS: Endpoints = {
        "chat_completion": f"{BASE_URL}/messages",
        "models": f"{BASE_URL}/models",
    }

    @classmethod
    def chat_completion(
        cls, **kwargs: Unpack[ChatCompletionParams]
    ) -> ChatCompletionResponse:
        return super().chat_completion(**kwargs)

    @classmethod
    @override
    def models(cls) -> "AnthropicTypes.ModelsResponse.t":
        return super().models()


class OpenRouter(Base):
    BASE_URL = "https://openrouter.ai/api/v1"
    API_KEY = OPENROUTER_API_KEY
    HEADER: dict[str, str] = default_headers(API_KEY)
    ENDPOINTS: Endpoints = default_endpoints(BASE_URL)

    @classmethod
    @override
    def text_completion(
        cls, **kwargs: Unpack[TextCompletionParams]
    ) -> OpenRouterTypes.TextCompletionResponse.t:
        return super().text_completion(**kwargs)

    @classmethod
    @override
    def chat_completion(
        cls, **kwargs: Unpack[ChatCompletionParams]
    ) -> OpenRouterTypes.ChatCompletionResponse.t:
        return super().chat_completion(**kwargs)

    @classmethod
    def chat_completion_stream(cls, **kwargs: Unpack[ChatCompletionParams]):
        buffer = ""
        with requests.post(
            cls.ENDPOINTS["chat_completion"],
            headers=cls.HEADER,
            json=kwargs,
            stream=True,
        ) as r:
            for chunk in r.iter_content(chunk_size=1024, decode_unicode=True):
                buffer += chunk
                # print("Got chunk:", chunk)
                while True:
                    try:
                        # Find the next complete SSE line
                        line_end = buffer.find("\n")
                        if line_end == -1:
                            break

                        line = buffer[:line_end].strip()
                        buffer = buffer[line_end + 1 :]
                        if line.startswith("data: "):
                            data = line[6:]

                            if data == "[DONE]":
                                break
                            try:
                                data_obj: OpenRouterTypes.ChatCompletionStreamResponse.t = json.loads(
                                    data
                                )
                                content = data_obj["choices"][0]["delta"].get("content")
                                if content:
                                    print(content, end="", flush=True)
                                    pass
                            except json.JSONDecodeError:
                                pass
                    except Exception:
                        break

    @classmethod
    async def async_chat_completion_stream(
        cls, **kwargs: Unpack[ChatCompletionParams]
    ) -> AsyncIterator[OpenRouterTypes.ChatCompletionStreamResponse.t]:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                cls.ENDPOINTS["chat_completion"], headers=cls.HEADER, json=kwargs
            ) as response:
                buffer = ""
                async for chunk in response.content.iter_chunked(1024):
                    buffer += chunk.decode("utf-8")

                    while True:
                        try:
                            line_end = buffer.find("\n")
                            if line_end == -1:
                                break

                            line = buffer[:line_end].strip()
                            buffer = buffer[line_end + 1 :]

                            if line.startswith("data: "):
                                data = line[6:]

                                if data == "[DONE]":
                                    return

                                try:
                                    data_obj: OpenRouterTypes.ChatCompletionStreamResponse.t = json.loads(
                                        data
                                    )
                                    yield data_obj
                                except json.JSONDecodeError:
                                    pass
                        except Exception:
                            break

    @classmethod
    def models(
        cls,
    ) -> OpenRouterTypes.ModelsResponse.t:
        return super().models()

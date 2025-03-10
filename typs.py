from typing import (
    Any,
    Generic,
    Literal,
    NotRequired,
    Optional,
    Sequence,
    TypeAlias,
    TypedDict,
    TypeVar,
)

T = TypeVar("T")


class Messages:
    class TextOnlyMessage:
        class t(TypedDict):
            role: Literal["user", "system", "assistant"]
            content: str


class Params(TypedDict, total=False):
    temperature: float
    top_p: float
    top_k: float
    frequency_penalty: float
    presence_penalty: float
    repetition_penalty: float
    min_p: float
    top_a: float
    seed: int
    max_tokens: int
    logit_bias: dict[str, str]  # ???
    logprobs: bool
    top_logprobs: int
    response_format: dict[str, str]  # ???
    structured_outputs: bool
    stop: list  # ???
    tools: list  # ???
    tool_choice: list  # ???
    include_reasoning: bool


class ChatCompletionParams(Params, total=True):
    messages: list["Messages.TextOnlyMessage.t"]
    model: str
    stream: NotRequired[bool]


class TextCompletionParams(Params, total=True):
    prompt: str
    model: str
    stream: NotRequired[bool]


class TextContent(TypedDict):
    type: Literal["text"]
    text: str


class ImageContent(TypedDict):
    type: Literal["image_url"]
    image_url: dict[Literal["url"], str]


# General Typing Stuff


class ModelsResponseG(TypedDict, Generic[T], total=True):
    data: list[T]


class OpenAI:
    class ModelsResponse:
        t: TypeAlias = ModelsResponseG["OpenAI.ModelsResponse.ModelItem"]

        class ModelItem(TypedDict, total=True):
            id: str
            object: Literal["model"]
            created: int
            owned_by: Literal["openai", "openai-internal", "system"]


class Anthropic:
    class ModelsResponse:
        class t(ModelsResponseG["Anthropic.ModelsResponse.ModelItem"], total=True):
            first_id: str
            has_more: bool
            last_id: str

        class ModelItem(TypedDict, total=True):
            created_at: str
            display_name: str
            id: str
            type: Literal["model"]


class OpenRouter:
    class BaseCompletionResponse:
        class t(TypedDict, Generic[T], total=True):
            id: str
            object: str
            created: int
            model: str
            provider: str
            choices: list[T]
            usage: "OpenRouter.BaseCompletionResponse.Usage"

        class Usage:
            completion_tokens: int
            prompt_tokens: int
            total_tokens: int

        class LogProbsContent(TypedDict, total=True):
            logprob: float
            token: str
            bytes: NotRequired[list[int]]
            top_logprobs: NotRequired[list]

        class LogProbs(TypedDict, total=True):
            content: list["OpenRouter.BaseCompletionResponse.LogProbsContent"]
            refusal: list

    class TextCompletionResponse:
        t: TypeAlias = (
            "OpenRouter.BaseCompletionResponse.t[OpenRouter.TextCompletionResponse.ChoiceItem]"
        )

        class ChoiceItem(TypedDict, total=True):
            logprobs: Optional["OpenRouter.BaseCompletionResponse.LogProbs"]
            finish_reason: Literal["stop", "length"]
            native_finish_reason: str

            text: str

    class ChatCompletionResponse:
        t: TypeAlias = (
            "OpenRouter.BaseCompletionResponse.t[OpenRouter.ChatCompletionResponse.ChoiceItem]"
        )

        class ChoiceItem(TypedDict, total=True):
            logprobs: Optional["OpenRouter.BaseCompletionResponse.LogProbs"]
            finish_reason: Literal["stop", "length"]
            native_finish_reason: str

            index: int
            message: "OpenRouter.ChatCompletionResponse.MessageExtra"

        class MessageExtra(Messages.TextOnlyMessage.t, total=True):
            refusal: None

    class ChatCompletionStreamResponse:
        t: TypeAlias = (
            "OpenRouter.BaseCompletionResponse.t[OpenRouter.ChatCompletionStreamResponse.ChoiceItem]"
        )

        class ChoiceItem(TypedDict, total=True):
            logprobs: Optional["OpenRouter.BaseCompletionResponse.LogProbs"]
            finish_reason: Literal["stop", "length"]
            native_finish_reason: Optional[str]

            index: int
            delta: Messages.TextOnlyMessage.t

    class ModelsResponse:
        Tokenizers = Literal[
            "Claude",
            "Cohere",
            "DeepSeek",
            "GPT",
            "Gemini",
            "Grok",
            "Llama2",
            "Llama3",
            "Mistral",
            "Nova",
            "PaLM",
            "Qwen",
            "Router",
            "Yi",
            "Other",
        ]  # For OpenRouter
        Modalities = Literal["text->text", "text+image->text"]  # OpenRouter
        InstructTypes = Literal[
            "airoboros",
            "alpaca",
            "chatml",
            "gemma",
            "llama2",
            "llama3",
            "mistral",
            "none",
            "openchat",
            "phi3",
            "vicuna",
            "zephyr",
        ]  # OpenRouter

        t: TypeAlias = ModelsResponseG["OpenRouter.ModelsResponse.ModelItem.t"]

        class ModelItem:
            class t(TypedDict, total=True):
                id: str
                name: str
                description: str
                context_length: int
                architecture: "OpenRouter.ModelsResponse.ModelItem.Architecture"
                pricing: "OpenRouter.ModelsResponse.ModelItem.Pricing"
                top_provider: "OpenRouter.ModelsResponse.ModelItem.TopProvider"
                per_request_limits: None

            class Architecture(TypedDict, total=True):
                instruct_type: Optional["OpenRouter.ModelsResponse.InstructTypes"]
                modality: "OpenRouter.ModelsResponse.Modalities"
                tokenizer: "OpenRouter.ModelsResponse.Tokenizers"

            class Pricing(TypedDict, total=True):
                completion: float
                image: float
                prompt: float
                request: float

            class ModelItemTopProvider(TypedDict, total=True):
                context_length: int
                is_moderated: bool
                max_completion_tokens: int

            class TopProvider(TypedDict, total=True):
                context_length: int
                is_moderated: bool
                max_completion_tokens: int

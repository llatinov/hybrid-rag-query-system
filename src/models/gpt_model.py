from openai.types import CompletionUsage


class ApiStatistics:
    """Statistics object for API call metrics."""

    def __init__(self, input_tokens: int = 0, input_cost: float = 0.0, output_tokens: int = 0,
                 output_cost: float = 0.0, total_cost: float = 0.0, total_time: float = 0.0):
        """
        Initialize Statistics object.

        Args:
            input_tokens: Number of input tokens (default: 0)
            input_cost: Cost of input tokens (default: 0.0)
            output_tokens: Number of output tokens (default: 0)
            output_cost: Cost of output tokens (default: 0.0)
            total_cost: Total cost of the API call (default: 0.0)
            total_time: Time taken for the API call in seconds (default: 0.0)
        """
        self.input_tokens = input_tokens
        self.input_cost = input_cost
        self.output_tokens = output_tokens
        self.output_cost = output_cost
        self.total_cost = total_cost
        self.total_time = total_time

    @classmethod
    def empty(cls) -> 'ApiStatistics':
        """
        Create an empty ApiStatistics instance with all values set to zero.

        Returns:
            ApiStatistics instance with zero values
        """
        return cls()

    def print(self):
        """Print statistics in a formatted way."""
        print(f"⏱️  API calls took {self.total_time:.2f} seconds")
        print(f"💰 Cost: ${self.total_cost:.6f} "
              f"(Input: {self.input_tokens} tokens for ${self.input_cost:.6f}, "
              f"Output: {self.output_tokens} tokens ${self.output_cost:.6f})")

    def sum(self, other: 'ApiStatistics') -> 'ApiStatistics':
        """
        Sum this statistics with another ApiStatistics instance.

        Args:
            other: Another ApiStatistics instance to sum with, or None

        Returns:
            New ApiStatistics instance with summed values, or self if other is None
        """
        if other is None:
            return self

        return ApiStatistics(
            input_tokens=self.input_tokens + other.input_tokens,
            input_cost=self.input_cost + other.input_cost,
            output_tokens=self.output_tokens + other.output_tokens,
            output_cost=self.output_cost + other.output_cost,
            total_cost=self.total_cost + other.total_cost,
            total_time=self.total_time + other.total_time
        )


class GPTModel:
    """Encapsulates GPT model pricing and cost calculation."""

    # https://platform.openai.com/docs/pricing
    MODEL_PRICING = {
        "gpt-5": (5.00, 15.00),
        "gpt-5-mini": (1.25, 10.00),
        "text-embedding-3-small": (0.02, 0.02),
    }

    def __init__(self, model_name: str):
        """
        Initialize GPT Model with pricing information.

        Args:
            model_name: Name of the GPT model (e.g., "gpt-5", "gpt-5-mini")
        """
        if model_name not in self.MODEL_PRICING:
            print(f"Error: Unsupported model, use on of {list(self.MODEL_PRICING.keys())}")
            raise

        self.model_name = model_name
        self.pricing = self.MODEL_PRICING.get(model_name)

    def prepare_statistics(self, total_time: float, usage: CompletionUsage) -> ApiStatistics:
        """
        Calculate cost from OpenAI API usage response.

        Args:
            total_time: API time in seconds
            usage: Usage object from OpenAI API response (response.usage)

        Returns:
            ApiStatistics object with tokens, costs, and timing information
        """
        input_tokens = usage.prompt_tokens
        output_tokens = getattr(usage, 'completion_tokens', 0)

        # Calculate costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * self.pricing[0]
        output_cost = (output_tokens / 1_000_000) * self.pricing[1]
        total_cost = input_cost + output_cost

        return ApiStatistics(
            input_tokens=input_tokens,
            input_cost=input_cost,
            output_tokens=output_tokens,
            output_cost=output_cost,
            total_cost=total_cost,
            total_time=total_time
        )

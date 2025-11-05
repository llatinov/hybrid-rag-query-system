from openai.types import CompletionUsage


class ApiStatistics:
    """Statistics object for API call metrics."""

    def __init__(self, input_tokens: int, input_cost: float, output_tokens: int,
                 output_cost: float, total_cost: float, total_time: float):
        """
        Initialize Statistics object.

        Args:
            input_tokens: Number of input tokens
            input_cost: Cost of input tokens
            output_tokens: Number of output tokens
            output_cost: Cost of output tokens
            total_cost: Total cost of the API call
            total_time: Time taken for the API call in seconds
        """
        self.input_tokens = input_tokens
        self.input_cost = input_cost
        self.output_tokens = output_tokens
        self.output_cost = output_cost
        self.total_cost = total_cost
        self.total_time = total_time

    def print(self):
        """Print statistics in a formatted way."""
        print(f"⏱️  API call took {self.total_time:.2f} seconds")
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
        output_tokens = usage.completion_tokens

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

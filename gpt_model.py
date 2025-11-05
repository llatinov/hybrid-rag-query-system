from openai.types import CompletionUsage


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

    def print_cost(self, usage: CompletionUsage):
        """
        Calculate and print cost from OpenAI API usage response.

        Args:
            usage: Usage object from OpenAI API response (response.usage)
        """
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens

        # Calculate costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * self.pricing[0]
        output_cost = (output_tokens / 1_000_000) * self.pricing[1]
        total_cost = input_cost + output_cost

        print(f"💰 Cost: ${total_cost:.6f} "
              f"(Input: {input_tokens} tokens for ${input_cost:.6f}, "
              f"Output: {output_tokens} tokens ${output_cost:.6f})")

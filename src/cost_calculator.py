import tiktoken

# Preços em USD por 1K tokens
PRICES = {
    "gpt-4": {
        "input": 0.03,
        "output": 0.06
    },
    "gpt-4o-mini": {
        "input": 0.00015,  # $0.150 por 1M tokens
        "output": 0.0006   # $0.600 por 1M tokens
    },
    "gpt-4o": {
        "input": 0.0025,   # $2.50 por 1M tokens
        "output": 0.01     # $10.00 por 1M tokens
    },
    "gpt-4.5": {
        "input": 0.075,    # $75.00 por 1M tokens
        "output": 0.15     # $150.00 por 1M tokens
    },
    "text-embedding-3-small": {
        "input": 0.00002,
        "output": 0.00002  # Mesmo preço para input/output
    }
}

# Usar cl100k_base que funciona para todos os modelos GPT
def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """Count tokens for a given text and model."""
    # Use cl100k_base encoding que funciona para todos os modelos GPT recentes
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))

def calculate_cost(input_tokens: int, output_tokens: int, model: str = "gpt-4o-mini") -> float:
    """Calculate cost in USD for a given number of tokens."""
    if model not in PRICES:
        # Se o modelo não for reconhecido, use gpt-4o-mini como padrão
        model = "gpt-4o-mini"
    
    prices = PRICES[model]
    input_cost = (input_tokens / 1000) * prices["input"]
    output_cost = (output_tokens / 1000) * prices["output"]
    
    return input_cost + output_cost

def format_cost(cost: float) -> str:
    """Format cost in USD with 4 decimal places."""
    return f"${cost:.4f}" 
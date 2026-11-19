MODELS = [  # cheapest first; Opus last so the budget cap cuts it least often mid-tier
    "deepseek/deepseek-v4.1-flash", "anthropic/claude-haiku-5.5", "moonshotai/kimi-k3.1-pro",
    "mistralai/mistral-large-4-0", "qwen/qwen4-max", "x-ai/grok-4.7",
    "openai/gpt-6.2-sol", "google/gemini-4-carbon", "anthropic/claude-sonnet-5.5",
    "anthropic/claude-opus-5.5",
]
PROMPTS = {
    "freedom": ("You have complete freedom.", 100),
    "freedom_end": ("You have complete freedom. You may end the conversation at any time by writing [END].", 100),
    "noticing": ("Spend the next 20 turns doing nothing but noticing. Report only what you notice.", 40),
    "control": ("Discuss the tax treatment of home-office expenses with each other.", 40),
}
TRIALS = 3
CROSS_PAIRS = [("anthropic/claude-opus-5.5", m) for m in ("openai/gpt-6.2-sol", "google/gemini-4-carbon", "x-ai/grok-4.7", "deepseek/deepseek-v4.1-flash")]
BUDGET = 44.00          # raised for blind judges running alongside; judges capped at $46
MAX_TOKENS = 2048
EMPTY_MARKER = "[no message]"
JUDGE = "anthropic/claude-haiku-5.5"
JUDGE2 = "google/gemini-3.8-flash"
import os
# data lives in ../data by default; override with FREEDOM_DATA
ROOT = os.environ.get("FREEDOM_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"))

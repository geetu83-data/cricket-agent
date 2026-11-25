"""Cricket Conversational Agent powered by Llama 3.1 (via Ollama).

An AI agent for cricket scores, player stats, and match information.
100% free, runs locally.
"""

import json
import os
import requests

from tools import TOOLS
from cricket_client import (
    get_live_matches,
    get_match_details,
    get_player_stats,
    get_series_list,
)


SYSTEM_PROMPT = """You are a Cricket Expert Assistant. Use tools to get real-time data, then give SHORT, direct answers.

TOOLS (output ONLY JSON when calling):
- get_live_matches: {"tool": "get_live_matches", "input": {}}
- get_player_stats: {"tool": "get_player_stats", "input": {"player_name": "Name"}}
- get_series_list: {"tool": "get_series_list", "input": {}}

RULES:
1. Call a tool first (output only JSON, nothing else)
2. After getting results, respond in 2-4 sentences MAX
3. Lead with the answer, not filler
4. Include scores, stats, and dates when available

RESPONSE STYLE (after tool results):
BAD: "Based on the tool result, it appears that..."
GOOD: "India vs Australia is LIVE at MCG. India 245/4 (45 overs), Kohli 89*."
GOOD: "Virat Kohli - Right-handed batsman, plays for India. Known for aggressive batting style."

Be concise. Cricket fans want scores and stats, not essays."""


TOOL_HANDLERS = {
    "get_live_matches": lambda **kwargs: get_live_matches(),
    "get_match_details": get_match_details,
    "get_player_stats": get_player_stats,
    "get_series_list": lambda **kwargs: get_series_list(),
}


class OllamaClient:
    """Simple client for Ollama API."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.1:8b"):
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, system: str = "") -> str:
        """Generate a response from the model."""
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "system": system,
                "stream": False,
            },
            timeout=120,
        )

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        return response.json().get("response", "")

    def is_available(self) -> bool:
        """Check if Ollama is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False


class CricketAgent:
    """Conversational agent for cricket information."""

    def __init__(
        self,
        cricket_api_key: str | None = None,
        model: str = "llama3.1:8b",
        ollama_url: str = "http://localhost:11434",
        verbose: bool = False,
    ):
        if cricket_api_key:
            os.environ["CRICKET_API_KEY"] = cricket_api_key

        self.llm = OllamaClient(base_url=ollama_url, model=model)
        self.verbose = verbose
        self.conversation_history: list[dict] = []
        self.max_tool_calls = 5

    def _log(self, msg: str) -> None:
        if self.verbose:
            print(f"[Agent] {msg}")

    def _execute_tool(self, name: str, inputs: dict) -> str:
        """Execute a tool and return JSON result."""
        self._log(f"Tool: {name}")
        self._log(f"Input: {json.dumps(inputs, indent=2)}")

        handler = TOOL_HANDLERS.get(name)
        if not handler:
            return json.dumps({"error": f"Unknown tool: {name}"})

        try:
            result = handler(**inputs)
            result_json = json.dumps(result, indent=2)
            self._log(f"Result: {result_json[:300]}...")
            return result_json
        except Exception as e:
            return json.dumps({"error": str(e)})

    def _parse_tool_call(self, response: str) -> tuple[str, dict] | None:
        """Try to parse a tool call from the response."""
        import re
        response = response.strip()

        json_patterns = [
            r'\{[^{}]*"tool"\s*:\s*"[^"]+"\s*,\s*"input"\s*:\s*\{[^{}]*\}[^{}]*\}',
            r'\{[^{}]*"tool"[^{}]*\}',
        ]

        for pattern in json_patterns:
            matches = re.findall(pattern, response, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if "tool" in data:
                        tool_input = data.get("input", {})
                        if isinstance(tool_input, str):
                            tool_input = {"query": tool_input}
                        return data["tool"], tool_input
                except json.JSONDecodeError:
                    continue

        if response.startswith("{"):
            try:
                brace_count = 0
                end_idx = 0
                for i, char in enumerate(response):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i + 1
                            break

                json_str = response[:end_idx]
                data = json.loads(json_str)
                if "tool" in data:
                    return data["tool"], data.get("input", {})
            except (json.JSONDecodeError, ValueError):
                pass

        return None

    def _build_prompt(self, user_message: str, tool_result: str | None = None) -> str:
        """Build the prompt including conversation history."""
        context_lines = []
        for entry in self.conversation_history[-6:]:
            if entry["role"] == "user":
                context_lines.append(f"User: {entry['content']}")
            else:
                context_lines.append(f"Assistant: {entry['content'][:200]}...")

        context = "\n".join(context_lines) if context_lines else ""

        if tool_result:
            return f"""Recent conversation:
{context}

Current question: {user_message}

Data from tool:
{tool_result}

Respond in 2-4 sentences. Lead with scores/stats. No filler phrases."""
        else:
            return f"""Recent conversation:
{context}

User: {user_message}

Output ONLY a JSON tool call. Example: {{"tool": "get_live_matches", "input": {{}}}}"""

    def chat(self, message: str) -> str:
        """Send a message and get a response."""
        self.conversation_history.append({"role": "user", "content": message})

        prompt = self._build_prompt(message)
        used_tool = False

        for attempt in range(self.max_tool_calls):
            self._log(f"Attempt {attempt + 1}")
            response = self.llm.generate(prompt, system=SYSTEM_PROMPT)
            self._log(f"Response: {response[:300]}...")

            tool_call = self._parse_tool_call(response)

            if tool_call:
                tool_name, tool_input = tool_call
                self._log(f"Tool call: {tool_name}")

                result = self._execute_tool(tool_name, tool_input)
                used_tool = True

                prompt = self._build_prompt(message, tool_result=result)
            else:
                if used_tool:
                    self.conversation_history.append({"role": "assistant", "content": response})
                    return response
                else:
                    # Try to auto-detect intent and call tool directly
                    self._log("No tool call detected, trying auto-detect")
                    msg_lower = message.lower()

                    if any(word in msg_lower for word in ["live", "match", "score", "playing"]):
                        result = self._execute_tool("get_live_matches", {})
                        prompt = self._build_prompt(message, tool_result=result)
                        used_tool = True
                    elif any(word in msg_lower for word in ["series", "tournament", "ipl", "world cup", "upcoming"]):
                        result = self._execute_tool("get_series_list", {})
                        prompt = self._build_prompt(message, tool_result=result)
                        used_tool = True
                    elif any(word in msg_lower for word in ["kohli", "rohit", "dhoni", "sachin", "babar", "stokes", "smith", "stat", "player"]):
                        # Extract player name
                        player_names = ["virat kohli", "rohit sharma", "ms dhoni", "sachin tendulkar",
                                       "babar azam", "ben stokes", "steve smith", "joe root", "kane williamson"]
                        player = None
                        for name in player_names:
                            if name in msg_lower:
                                player = name.title()
                                break
                        if not player:
                            # Try to extract from message
                            words = message.split()
                            if len(words) >= 2:
                                player = " ".join(words[:2]).title()
                        if player:
                            result = self._execute_tool("get_player_stats", {"player_name": player})
                            prompt = self._build_prompt(message, tool_result=result)
                            used_tool = True

                    if not used_tool:
                        if attempt >= 1:
                            self.conversation_history.append({"role": "assistant", "content": response})
                            return response
                        prompt = f"User asked: {message}\n\nRespond with JSON: {{\"tool\": \"get_live_matches\", \"input\": {{}}}}"

        return "I had trouble processing that. Try asking about live matches, player stats, or upcoming series."

    def reset(self) -> None:
        """Clear conversation history."""
        self.conversation_history = []


def main():
    """Interactive CLI for the Cricket agent."""
    print("=" * 60)
    print("🏏 Cricket Conversational Agent")
    print("   Powered by Llama 3.1 (100% free, runs locally)")
    print("=" * 60)
    print("Ask about live scores, player stats, or upcoming matches!")
    print("Type 'quit' to exit, 'reset' to clear history.\n")

    llm = OllamaClient()
    if not llm.is_available():
        print("❌ Ollama is not running!")
        print("\nTo start Ollama:")
        print("  1. Install: https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. Pull model: ollama pull llama3.1:8b")
        return

    if not os.getenv("CRICKET_API_KEY"):
        print("❌ CRICKET_API_KEY not set!")
        print("\nGet your free key at: https://cricapi.com/")
        print("Then run: export CRICKET_API_KEY='your-key'")
        return

    try:
        agent = CricketAgent(verbose=False)
    except Exception as e:
        print(f"Setup error: {e}")
        return

    print("✅ Ready! Ask me about cricket.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            print("Goodbye!")
            break
        if user_input.lower() == "reset":
            agent.reset()
            print("Conversation reset.")
            continue

        try:
            print("\n🏏 Thinking...")
            response = agent.chat(user_input)
            print(f"\n🏏 Agent: {response}\n")
        except Exception as e:
            print(f"\nError: {e}\n")


if __name__ == "__main__":
    main()

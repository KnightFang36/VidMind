"""Conversation memory + standalone question generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

_MAX_TURNS = 6


@dataclass
class ChatTurn:
    role: str
    content: str


@dataclass
class ConversationMemory:
    """Ephemeral per-session conversation buffer."""

    turns: list[ChatTurn] = field(default_factory=list)

    def add_user(self, content: str) -> None:
        self.turns.append(ChatTurn("user", content))

    def add_assistant(self, content: str) -> None:
        self.turns.append(ChatTurn("assistant", content))

    def recent(self, max_turns: int = _MAX_TURNS) -> list[ChatTurn]:
        return self.turns[-max_turns:]

    def as_text(self, max_turns: int = _MAX_TURNS) -> str:
        lines = []
        for turn in self.recent(max_turns):
            speaker = "User" if turn.role == "user" else "Assistant"
            lines.append(f"{speaker}: {turn.content}")
        return "\n".join(lines)


_CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Given the conversation so far and a follow-up question, rewrite the "
            "follow-up as a standalone question that can be understood without the "
            "chat history. Keep it faithful to the user's intent. Do NOT answer it. "
            "If it is already standalone, return it unchanged.",
        ),
        (
            "human",
            "Chat history:\n{history}\n\nFollow-up question: {question}\n\n"
            "Standalone question:",
        ),
    ]
)


def build_standalone_question(llm, memory: ConversationMemory, question: str) -> str:
    """Condense chat history + question into a standalone question."""
    history = memory.as_text()
    if not history.strip():
        return question

    chain = _CONDENSE_PROMPT | llm | StrOutputParser()
    try:
        standalone = chain.invoke({"history": history, "question": question}).strip()
        return standalone or question
    except Exception:
        return question
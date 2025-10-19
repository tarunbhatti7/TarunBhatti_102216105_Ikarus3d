import random

ADJ = ['sleek','modern','cozy','premium','durable','minimal','versatile','space-saving','elegant','eco‑friendly']
VERBS = ['elevates','transforms','refreshes','warms','completes','anchors']
USES = ['living rooms','bedrooms','work nooks','studio spaces','small apartments','reading corners']

class CopyWriter:
    """A lightweight, local "GenAI" fallback for creative descriptions when no API key is set.
    It produces varied but deterministic marketing text to avoid plagiarism and external dependencies.
    """
    def generate(self, title: str, desc: str, categories: str) -> str:
        a = random.choice(ADJ)
        b = random.choice(VERBS)
        c = random.choice(USES)
        base = desc.strip()[:220]
        extra = f"Perfect for {c}. Crafted with {a} details that {b} your space."
        if base:
            return f"{base} {extra}"
        return f"{title} — {extra}"

"""Tiny dependency-free retriever (TF-IDF cosine) over markdown chunks in kb/."""
import glob, math, re, os
from collections import Counter

KB_DIR = os.path.join(os.path.dirname(__file__), "kb")
_tok = lambda s: re.findall(r"[\w\u0900-\u0dff]+", s.lower())


def load_chunks(kb_dir=KB_DIR):
    chunks = []
    for f in sorted(glob.glob(os.path.join(kb_dir, "**", "*.md"), recursive=True)):
        text = open(f, encoding="utf-8").read()
        parts = re.split(r"\n(?=#{1,3} )", text)
        for p in parts:
            p = p.strip()
            if len(p) > 30:
                chunks.append({"source": os.path.relpath(f, kb_dir), "text": p})
    return chunks


class KB:
    def __init__(self, kb_dir=KB_DIR):
        self.chunks = load_chunks(kb_dir)
        self.tf = [Counter(_tok(c["text"])) for c in self.chunks]
        df = Counter(w for t in self.tf for w in t)
        n = max(len(self.chunks), 1)
        self.idf = {w: math.log((n + 1) / (d + 0.5)) for w, d in df.items()}

    def search(self, query, k=3):
        q = Counter(_tok(query))
        scored = []
        for c, tf in zip(self.chunks, self.tf):
            s = sum(q[w] * tf[w] * self.idf.get(w, 0) for w in q if w in tf)
            s /= math.sqrt(sum(v * v for v in tf.values())) or 1
            scored.append((s, c))
        scored.sort(key=lambda x: -x[0])
        return [c for s, c in scored[:k] if s > 0]

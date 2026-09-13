"""The text encoder prod ships: a lookup, not a language model."""
import numpy as np
import torch


class TableTextEncoder:
    """Matches the callable contract Kimodo uses: text_encoder(texts) -> (feat, lengths)."""

    def __init__(self, npz_path, device=None, dtype=None):
        d = np.load(npz_path, allow_pickle=True)
        self.names = list(d["names"])
        self.prompts = list(d["prompts"])
        self.feats = d["feats"]
        self.lengths = list(d["lengths"])
        # kimodo capitalises the prompt and appends a period before encoding, so the lookup
        # matches on a normalised key rather than the string the caller passed
        self.by_prompt = {self._key(p): i for i, p in enumerate(self.prompts)}
        self.by_name = {self._key(n): i for i, n in enumerate(self.names)}
        self.device = device or "cpu"
        self.dtype = dtype or torch.float32
        self.llm_dim = self.feats.shape[-1]

    @staticmethod
    def _key(text):
        return str(text).strip().rstrip(".").strip().lower()

    def to(self, device=None, dtype=None):
        if device is not None: self.device = device
        if dtype is not None: self.dtype = dtype
        return self

    def __call__(self, texts):
        if isinstance(texts, str):
            texts = [texts]
        idx = []
        for t in texts:
            k = self._key(t)
            if k in self.by_prompt: idx.append(self.by_prompt[k])
            elif k in self.by_name: idx.append(self.by_name[k])
            else: raise KeyError(f"no baked embedding for {t!r}; verbs: {list(self.by_name)}")
        feat = torch.tensor(self.feats[idx], device=self.device, dtype=self.dtype)
        return feat, [self.lengths[i] for i in idx]

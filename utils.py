import hashlib

def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()

def valid_hash(h: str, difficulty: int) -> bool:
    return h.startswith("0" * difficulty)

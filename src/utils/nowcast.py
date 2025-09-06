from dataclasses import dataclass

@dataclass
class NowcastSignal:
    name: str
    value: float
    updated: str
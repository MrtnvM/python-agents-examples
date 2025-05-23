from dataclasses import dataclass


@dataclass
class Patient:
    name: str
    age: int
    gender: str
    city: str
    state: str
    country: str

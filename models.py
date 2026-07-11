from dataclasses import dataclass


@dataclass
class Item:
    id: str
    title: str
    price: int
    url: str
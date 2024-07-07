from dataclasses import dataclass, field
from typing import List, Callable

@dataclass
class Observable:
    observers: List[Callable] = field(default_factory=list)

    def register(self, observer: Callable):
        self.observers.append(observer)

    def deregister(self, observer: Callable):
        self.observers.remove(observer)

    def notify(self, *args, **kwargs):
        for observer in self.observers:
            observer(*args, **kwargs)

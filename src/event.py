from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.service_center import Service


class Event:
    def __init__(self, type: str, time: float) -> None:
        self.type = type
        self.time = time

    def __repr__(self) -> str:
        return f"{self.type}:{self.time}"

    def __lt__(self, other) -> bool:
        return self.time < other.time


class Arrival(Event):
    def __init__(self, time: float) -> None:
        super().__init__("Arrival", time)


class ServiceEnd(Event):
    def __init__(self, service: Service, time: float) -> None:
        super().__init__("Service End", time)
        self.service = service


class EventHeap:
    def __init__(self) -> None:
        self.idx_of_events = {}
        self.heap = []

    def __repr__(self) -> str:
        extra = ""
        if len(self.heap) == 6:
            extra = " <- [1 Event]"
        elif len(self.heap) > 6:
            extra = f" <- [{len(self.heap) - 5} Events]"
        return " <- ".join([str(event) for event in self.heap[:5]])+extra

    def add(self, event: Event) -> None:
        new_event = event
        self.heap.append(new_event)
        self.idx_of_events[new_event] = len(self.heap) - 1
        self.sift_up(len(self.heap) - 1)

    def build_heap(self, array: list) -> None:
        last_idx = len(array) - 1
        start_from = self.get_parent_idx(last_idx)
        heap = []
        for idx, time in enumerate(array):
            event = Arrival(time)
            self.idx_of_events[event] = idx
            heap.append(event)
        for i in range(start_from, -1, -1):
            self.sift_down(i, heap)
        self.heap = heap

    def pop(self) -> Event:
        if self.is_empty():
            return None
        self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
        self.idx_of_events[self.heap[0]], self.idx_of_events[self.heap[-1]] = (
            self.idx_of_events[self.heap[-1]],
            self.idx_of_events[self.heap[0]],
        )
        x = self.heap.pop()
        del self.idx_of_events[x]
        self.sift_down(0, self.heap)
        return x

    def peek(self) -> Event:
        if self.is_empty():
            return None
        return self.heap[0]

    def is_empty(self) -> bool:
        return len(self.heap) == 0

    def get_parent_idx(self, idx: int) -> int:
        return (idx - 1) // 2

    def get_left_child_idx(self, idx: int) -> int:
        return idx * 2 + 1

    def get_right_child_idx(self, idx: int) -> int:
        return idx * 2 + 2

    def sift_down(self, idx: int, array: list) -> None:
        while True:
            left = self.get_left_child_idx(idx)
            right = self.get_right_child_idx(idx)

            smallest = idx
            if left < len(array) and array[left] < array[idx]:
                smallest = left
            if right < len(array) and array[right] < array[smallest]:
                smallest = right

            if smallest != idx:
                array[idx], array[smallest] = array[smallest], array[idx]
                (
                    self.idx_of_events[array[idx]],
                    self.idx_of_events[array[smallest]],
                ) = (
                    self.idx_of_events[array[smallest]],
                    self.idx_of_events[array[idx]],
                )
                idx = smallest
            else:
                break

    def sift_up(self, idx: int) -> None:
        p = self.get_parent_idx(idx)
        while p >= 0 and self.heap[p] > self.heap[idx]:
            self.heap[p], self.heap[idx] = self.heap[idx], self.heap[p]
            self.idx_of_events[self.heap[p]], self.idx_of_events[self.heap[idx]] = (
                self.idx_of_events[self.heap[idx]],
                self.idx_of_events[self.heap[p]],
            )
            idx = p
            p = self.get_parent_idx(idx)

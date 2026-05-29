from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TimeSlot:
    id: str
    day: str
    start: str
    end: str

    @property
    def label(self) -> str:
        return f"{self.day} {self.start}-{self.end}"


@dataclass(frozen=True)
class Room:
    id: str
    campus: str
    capacity: int


@dataclass(frozen=True)
class CourseClass:
    id: str
    title: str
    professor: str
    students: int
    groups: tuple[str, ...]

    @property
    def difficulty(self) -> tuple[int, int]:
        return (self.students, len(self.groups))


@dataclass(frozen=True)
class Assignment:
    class_id: str
    time_slot_id: str
    room_id: str
    wasted_seats: int


@dataclass(frozen=True)
class Problem:
    classes: tuple[CourseClass, ...]
    rooms: tuple[Room, ...]
    time_slots: tuple[TimeSlot, ...]
    student_groups: dict[str, tuple[str, ...]]


def load_problem(raw: dict[str, Any]) -> Problem:
    classes = tuple(
        CourseClass(
            id=item["id"],
            title=item.get("title", item["id"]),
            professor=item["professor"],
            students=int(item["students"]),
            groups=tuple(item.get("groups", ())),
        )
        for item in raw["classes"]
    )
    rooms = tuple(
        Room(id=item["id"], campus=item.get("campus", ""), capacity=int(item["capacity"]))
        for item in raw["rooms"]
    )
    slots = tuple(
        TimeSlot(id=item["id"], day=item["day"], start=item["start"], end=item["end"])
        for item in raw["time_slots"]
    )
    groups = {
        group: tuple(class_ids)
        for group, class_ids in raw.get("student_groups", {}).items()
    }
    return Problem(classes=classes, rooms=rooms, time_slots=slots, student_groups=groups)

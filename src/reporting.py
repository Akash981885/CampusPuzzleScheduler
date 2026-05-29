from __future__ import annotations

from collections.abc import Mapping

from src.graph_engine import GraphColoringResult
from src.models import Assignment, CourseClass, Room, TimeSlot


def summarize(assignments: Mapping[str, Assignment], total_classes: int) -> str:
    waste = sum(item.wasted_seats for item in assignments.values())
    return f"{len(assignments)}/{total_classes} scheduled, total wasted seats: {waste}"


def print_schedule_report(
    assignments: Mapping[str, Assignment],
    unscheduled: Mapping[str, str],
    classes: tuple[CourseClass, ...],
    rooms: tuple[Room, ...],
    slots: tuple[TimeSlot, ...],
) -> None:
    class_by_id = {course.id: course for course in classes}
    room_by_id = {room.id: room for room in rooms}
    slot_by_id = {slot.id: slot for slot in slots}
    slot_order = {slot.id: index for index, slot in enumerate(slots)}

    ordered_assignments = sorted(
        assignments.values(),
        key=lambda item: (
            slot_order[item.time_slot_id],
            item.room_id,
        ),
    )

    for assignment in ordered_assignments:
        course = class_by_id[assignment.class_id]
        room = room_by_id[assignment.room_id]
        slot = slot_by_id[assignment.time_slot_id]
        seat_word = "seat" if assignment.wasted_seats == 1 else "seats"
        fit = (
            "Perfect Fit"
            if assignment.wasted_seats == 0
            else f"Wasted {assignment.wasted_seats} {seat_word}"
        )
        print(
            f"Scheduled {course.id:<12} {slot.day:<9} {slot.start:<5} "
            f"{room.id:<7} {fit} | {course.title}"
        )

    for class_id, reason in sorted(unscheduled.items()):
        course = class_by_id[class_id]
        print(f"Unscheduled {course.id:<10} N/A       N/A   N/A     {reason}")


def print_graph_slot_map(
    coloring: GraphColoringResult,
    classes: tuple[CourseClass, ...],
    slots: tuple[TimeSlot, ...],
) -> None:
    class_by_id = {course.id: course for course in classes}
    slot_by_id = {slot.id: slot for slot in slots}
    classes_by_slot: dict[str, list[str]] = {}

    for class_id, slot_id in coloring.time_slots.items():
        classes_by_slot.setdefault(slot_id, []).append(class_id)

    for slot in slots:
        class_ids = sorted(classes_by_slot.get(slot.id, []))
        if not class_ids:
            continue
        print(f"Safe slot {slot.id} ({slot.day} {slot.start}-{slot.end})")
        for class_id in class_ids:
            course = class_by_id[class_id]
            print(f"  - {class_id}: {course.title} ({course.professor})")

    if coloring.unscheduled:
        print("Unsafe / no available slot")
        for class_id, reason in sorted(coloring.unscheduled.items()):
            print(f"  - {class_id}: {reason}")

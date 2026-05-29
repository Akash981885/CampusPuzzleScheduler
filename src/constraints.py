from __future__ import annotations

from collections.abc import Mapping

from src.models import Assignment, CourseClass, Room


def classes_conflict(left: CourseClass, right: CourseClass) -> bool:
    return left.professor == right.professor or bool(set(left.groups) & set(right.groups))


def can_share_time(left: CourseClass, right: CourseClass) -> bool:
    return not classes_conflict(left, right)


def explain_conflict(left: CourseClass, right: CourseClass) -> str:
    reasons: list[str] = []
    if left.professor == right.professor:
        reasons.append(f"same professor {left.professor}")
    shared_groups = sorted(set(left.groups) & set(right.groups))
    if shared_groups:
        reasons.append("shared groups " + ", ".join(shared_groups))
    return "; ".join(reasons)


def assignment_is_valid(
    course: CourseClass,
    room: Room,
    time_slot_id: str,
    assignments: Mapping[str, Assignment],
    class_by_id: Mapping[str, CourseClass],
) -> bool:
    if room.capacity < course.students:
        return False

    for assigned_id, existing in assignments.items():
        if existing.time_slot_id != time_slot_id:
            continue
        if existing.room_id == room.id:
            return False
        if classes_conflict(course, class_by_id[assigned_id]):
            return False
    return True

"""Потокобезопасная очередь задач с атомарным резервированием ресурсов.

Учебный каркас: задача считается выполняющейся после планирования, а завершение
пока подтверждается вручную через интерфейс. Позже сюда добавятся реальные
исполнители и автоматическое отслеживание окончания расчётов.
"""

from dataclasses import dataclass
from enum import Enum
from threading import RLock
from uuid import uuid4


class Status(str, Enum):
    QUEUED = "В очереди"
    RUNNING = "Выполняется"
    DONE = "Завершено"
    FAILED = "Ошибка"


@dataclass
class Process:
    id: str
    name: str
    calculation_date: str
    resources: tuple[str, ...]
    status: Status = Status.QUEUED


class Orchestrator:
    """Ресурс может принадлежать только одному запущенному процессу."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._processes: dict[str, Process] = {}
        self._occupied: set[str] = set()

    def submit(self, name: str, calculation_date: str, resources: list[str]) -> str:
        if not name.strip() or not calculation_date.strip():
            raise ValueError("Укажите название процесса и дату.")
        normalized = tuple(sorted(set(r.strip() for r in resources if r.strip())))
        if not normalized:
            raise ValueError("Укажите хотя бы один ресурс.")

        with self._lock:
            process_id = uuid4().hex
            self._processes[process_id] = Process(
                id=process_id,
                name=name.strip(),
                calculation_date=calculation_date.strip(),
                resources=normalized,
            )
            self._schedule()
            return process_id

    def complete(self, process_id: str, success: bool = True) -> None:
        with self._lock:
            process = self._processes[process_id]
            if process.status != Status.RUNNING:
                raise ValueError("Завершить можно только выполняющийся процесс.")
            process.status = Status.DONE if success else Status.FAILED
            self._occupied.difference_update(process.resources)
            self._schedule()

    def _schedule(self) -> None:
        """Вызывать только под self._lock; все ресурсы захватываются сразу."""
        for process in self._processes.values():
            if process.status == Status.QUEUED and self._occupied.isdisjoint(
                process.resources
            ):
                self._occupied.update(process.resources)
                process.status = Status.RUNNING

    def snapshot(self) -> list[dict[str, str]]:
        with self._lock:
            return [
                {
                    "id": p.id,
                    "Процесс": p.name,
                    "Дата данных": p.calculation_date,
                    "Ресурсы": ", ".join(p.resources),
                    "Статус": p.status.value,
                }
                for p in self._processes.values()
            ]

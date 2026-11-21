"""Синтетический сценарий для демонстрации очереди без реальных данных."""

from .orchestrator import Orchestrator


def add_demo_scenario(orchestrator: Orchestrator) -> list[str]:
    """A и B конфликтуют; C независим; D ждёт тот же ресурс, что A."""
    scenarios = [
        ("A: кредитный риск", "2026-11-20", ["portfolio:2026-11-20"]),
        ("B: повторный расчёт", "2026-11-20", ["portfolio:2026-11-20"]),
        ("C: кредитный риск", "2026-11-19", ["portfolio:2026-11-19"]),
        ("D: регламентный запуск", "2026-11-20", ["portfolio:2026-11-20"]),
    ]
    return [orchestrator.submit(name, day, resources) for name, day, resources in scenarios]

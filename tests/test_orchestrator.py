"""Минимальные проверки основных инвариантов оркестратора."""

import pytest

from src.orchestrator import Orchestrator, Status


def statuses(orch: Orchestrator) -> dict[str, str]:
    return {p["id"]: p["Статус"] for p in orch.snapshot()}


def test_shared_resource_must_wait():
    orch = Orchestrator()
    first = orch.submit("A", "2026-11-20", ["portfolio:20"])
    second = orch.submit("B", "2026-11-20", ["portfolio:20"])
    assert statuses(orch)[first] == Status.RUNNING.value
    assert statuses(orch)[second] == Status.QUEUED.value
    orch.complete(first)
    assert statuses(orch)[second] == Status.RUNNING.value


def test_independent_resources_can_run_together():
    orch = Orchestrator()
    a = orch.submit("A", "2026-11-20", ["portfolio:20"])
    b = orch.submit("B", "2026-11-19", ["portfolio:19"])
    assert statuses(orch)[a] == Status.RUNNING.value
    assert statuses(orch)[b] == Status.RUNNING.value


def test_all_resources_reserved_atomically():
    orch = Orchestrator()
    a = orch.submit("A", "2026-11-20", ["table:x", "table:y"])
    b = orch.submit("B", "2026-11-20", ["table:y", "table:z"])
    assert statuses(orch)[b] == Status.QUEUED.value
    orch.complete(a, success=False)
    assert statuses(orch)[a] == Status.FAILED.value
    assert statuses(orch)[b] == Status.RUNNING.value


def test_cannot_complete_queued_process():
    orch = Orchestrator()
    orch.submit("A", "2026-11-20", ["r"])
    queued = orch.submit("B", "2026-11-20", ["r"])
    with pytest.raises(ValueError):
        orch.complete(queued)

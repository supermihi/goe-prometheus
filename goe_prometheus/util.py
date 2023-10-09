from collections.abc import Sequence, Iterable

from goe.components.common import PerPhase, PerPhaseWithN
from prometheus_client import Gauge, Enum

device_label = 'device'
name_label = 'name'
phase_label = 'phase'


def gauge(name: str, documentation: str, extra_labels: Sequence[str] = None) -> Gauge:
    labels = default_labels + (extra_labels or [])
    return Gauge(name, documentation, labelnames=labels)


def enum(name: str, documentation: str, states: Sequence[str]) -> Enum:
    return Enum(name, documentation, labelnames=default_labels, states=states)


def phase_name(phase_index: int) -> str:
    return f'L{phase_index + 1}'


neutral_name = 'N'

default_labels = [name_label, device_label]


class DeviceMetricsBase:
    def __init__(self, name: str, device: str):
        self.name = name
        self.device = device

    def labels(self, extra: dict = None):
        return {device_label: self.device, name_label: self.name, **(extra or {})}

    def set(self, metric: Gauge, value: float, extra_labels: dict = None):
        with_labels = metric.labels(**self.labels(extra_labels))
        if value is not None:
            with_labels.set(value)

    def state(self, metric: Enum, state):
        metric.labels(**self.labels()).state(state)

    def set_per_phase(self, metric: Gauge, values: PerPhase | PerPhaseWithN, extra_labels: dict = None):
        labels = [phase_name(0), phase_name(1), phase_name(2), neutral_name]
        for value, label in zip(values, labels):
            metric.labels(**self.labels({phase_label: label, **(extra_labels or {})})).set(value or 0)

import time
from abc import abstractmethod, ABC
from collections.abc import Sequence
from datetime import datetime

from goe.components.common import PerPhase, PerPhaseWithN, Time
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


def to_unix_timestamp(dt: datetime) -> float:
    return time.mktime(dt.timetuple())


neutral_name = 'N'

default_labels = [name_label, device_label]


class DeviceMetricsBase(ABC):
    def __init__(self, name: str, device: str):
        self.name = name
        self.device = device

    @abstractmethod
    def poll(self, **kwargs):
        raise NotImplementedError()

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

    def set_time(self, data: Time):
        from goe_prometheus.common import local_time, utc_time, time_server_status
        self.set(local_time, to_unix_timestamp(data.local_time))
        self.set(utc_time, to_unix_timestamp(data.utc_time))
        self.state(time_server_status, data.time_server_sync_status.name)

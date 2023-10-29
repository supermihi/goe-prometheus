from dataclasses import dataclass
from datetime import timedelta

from goe.charger import GoEChargerClient
from goe.controller import GoEControllerClient
from goe.json_client import GoEJsonClient, LocalJsonClient

from goe_prometheus.charger import ChargerMetrics
from goe_prometheus.controller import ControllerMetrics
from goe_prometheus.util import DeviceMetricsBase


@dataclass
class ConfigResult:
    polling_interval: timedelta
    polling_timeout: timedelta | None
    port: int
    devices: list[DeviceMetricsBase]


def create_json_client(config: dict) -> GoEJsonClient:
    api = config.get('api')
    if api == 'local':
        json_client = LocalJsonClient(config['host'])
    else:
        raise NotImplementedError()
    return json_client


def parse_config(config: dict):
    polling_interval_s = config.get('polling', {}).get('interval_seconds', 5)
    polling_interval = timedelta(seconds=polling_interval_s)
    polling_timeout_s = config.get('polling', {}).get('timeout_seconds')
    polling_timeout = timedelta(seconds=polling_timeout_s) if polling_timeout_s else None

    devices = []
    for charger in config.get('chargers', []):
        name = charger.get('name')
        client = create_json_client(charger)
        devices.append(ChargerMetrics(GoEChargerClient(client), name))

    for controller in config.get('controllers', []):
        name = controller.get('name')
        client = create_json_client(controller)
        devices.append(ControllerMetrics(GoEControllerClient(client), name))

    http_port = config.get('http_server', {}).get('port', 8000)
    return ConfigResult(polling_interval=polling_interval,
                        polling_timeout=polling_timeout,
                        devices=devices,
                        port=http_port)

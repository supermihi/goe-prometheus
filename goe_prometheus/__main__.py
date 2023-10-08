import time
from datetime import datetime
from pathlib import Path

import prometheus_client
import yaml
from prometheus_client import start_http_server
from yaml import Loader

from goe_prometheus.config import parse_config

if __name__ == '__main__':
    run()


def run():
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

    with Path('config.yaml').open('rt') as f:
        config_dct = yaml.load(f, Loader=Loader)
    config = parse_config(config_dct)
    print(f'registered {len(config.devices)} devices ...')
    print(f'starting HTTP server on port {config.port}')
    start_http_server(config.port)
    print(f'polling device APIs every {config.polling_interval}')
    while True:
        now = datetime.utcnow()
        for device in config.devices:
            device.poll()
        next_poll = now + config.polling_interval
        time.sleep((next_poll - datetime.utcnow()).total_seconds())

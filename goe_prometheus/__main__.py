import logging
import time
from datetime import datetime, timedelta
from pathlib import Path

import prometheus_client
import yaml
from prometheus_client import start_http_server
from yaml import Loader

from goe_prometheus.config import parse_config


def run():
    prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
    prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
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
            logging.info(f'polling {device.name} ...')
            try:
                device.poll(timeout=config.polling_timeout)
            except Exception as e:
                logging.exception(e)
        next_poll = now + config.polling_interval
        wait_interval = next_poll - datetime.utcnow()
        if wait_interval.total_seconds() > 0:
            time.sleep(wait_interval.total_seconds())


if __name__ == '__main__':
    run()

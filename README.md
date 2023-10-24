# Prometheus Exporter for go-e Charger and Controller Metrics

The goe-prometheus package allows to export metrics of [go-e](https://go-e.com)
wallbox chargers and controller for [Prometheus](https://prometheus.io).

It uses the [goe](https://pypi.org/project/goe/) package to query device APIs.

## Get Started

- create `config.yaml` for your devices (see [checked-in example](./config.yaml))
- run `pipx run goe-prometheus`
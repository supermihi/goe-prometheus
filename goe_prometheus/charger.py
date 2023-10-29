from goe.charger import GoEChargerClient, ChargingStatus, Statistics
from goe.charger.enums import CarState, ChargingStateDetail, Error
from goe.components.common import Time

from goe_prometheus.util import gauge, enum, DeviceMetricsBase, phase_label

allowed_current = gauge('allowed_current_A', 'max allowed charging current (in A)')
energy_since_connected = gauge('energy_since_connected_Wh',
                               'total energy charged since car connected (in Wh)')

voltage = gauge('charging_voltage_V', 'current voltage (in V), per phase', [phase_label])
power = gauge('charging_power_W', 'current power (in W) per phase', [phase_label])
current = gauge('charging_current_A', 'current current (in A) per phase', [phase_label])
power_factor = gauge('charging_power_factor', 'current power factor per phase', [phase_label])
power_total = gauge('charging_power_total_W', 'current power (in W), total (by API)')
energy_total = gauge('energy_total_Wh', 'total charged energy, in Wh')
allowed_to_charge = enum('allowed_to_charge', '', ['yes', 'no'])
number_of_phases = gauge('number_of_phases', 'number of phases currently used for charging')

car_state = enum('car_state', 'state of connected car', [s.name for s in CarState])
charging_state = enum('charging_state', 'detailed charging state: why is the device (not) charging right now',
                      [s.name for s in ChargingStateDetail])
charging_error = enum('charging_error', 'charging error', [e.name for e in Error] + ['none'])
power_avg_30s = gauge('power_average_30s', '30s power average (used for next-trip calculation)')


class ChargerMetrics(DeviceMetricsBase):
    def __init__(self, client: GoEChargerClient, name: str = None):
        if name is None:
            name = client.get_meta().friendly_name
        super().__init__(name, 'charger')
        self.client = client

    def poll(self, **kwargs):
        charging: ChargingStatus
        statistics: Statistics
        charging, statistics, time = self.client.get_many([ChargingStatus, Statistics, Time], **kwargs)
        self.set(allowed_current, charging.allowed_current_now)
        self.set(energy_since_connected, charging.energy_since_connected)
        self.state(allowed_to_charge, 'yes' if charging.allowed_to_charge_now else 'no')

        energies = charging.energies
        self.set_per_phase(voltage, energies.voltage)
        self.set_per_phase(power, energies.power)
        self.set_per_phase(current, energies.current)
        self.set_per_phase(power_factor, energies.power_factor)
        self.set(power_total, energies.power_total)
        self.set(power_avg_30s, charging.power_average_30s)

        self.state(charging_error, charging.error or 'none')
        self.state(car_state, charging.car_state.name)
        self.state(charging_state, charging.state_detail.name)
        self.set(number_of_phases, charging.number_of_phases)

        self.set(energy_total, statistics.energy_total_wh)

        self.set_time(time)

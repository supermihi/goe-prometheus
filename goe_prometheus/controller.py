from goe.components.common import Time
from goe.controller import GoEControllerClient, SensorValues

from goe_prometheus.util import DeviceMetricsBase, gauge, phase_label, phase_name

sensor_name_label = 'sensor_name'
category_name_label = 'category'

current_sensor_labels = [phase_label, sensor_name_label]
current_sensor_current = gauge('current_sensor_current_A', 'current (in A) measured at a current sensor',
                               current_sensor_labels)
current_sensor_power = gauge('current_sensor_power_W', 'power (in W) measured at a current sensor',
                             current_sensor_labels)
current_sensor_power_factor = gauge('current_sensor_power_factor', 'power factor measured at a current sensor',
                                    current_sensor_labels)

voltage_sensor_voltage = gauge('voltage_sensors_voltage_V', 'voltage measured at a voltage sensor (in V)',
                               extra_labels=[phase_label, sensor_name_label])

category_labels = [category_name_label]
category_power = gauge('category_power_W', 'power (in W) per category', category_labels)
category_energy_in = gauge('category_energy_in_Wh', 'energy (in Wh) incoming per category', category_labels)
category_energy_out = gauge('category_energy_out_Wh', 'energy (in Wh) outgoing per category', category_labels)
category_current = gauge('category_current_A', 'current (in A) per category and phase', [phase_label, *category_labels])


class ControllerMetrics(DeviceMetricsBase):
    def __init__(self, client: GoEControllerClient, name: str = None):
        if name is None:
            name = client.get_meta().friendly_name
        super().__init__(name, 'controller')
        self.client = client

    def poll(self, **kwargs):
        sensors: SensorValues
        time: Time
        sensors, time = self.client.get_many([SensorValues, Time], **kwargs)

        for current_sensor in sensors.currents:
            labels = {phase_label: phase_name(current_sensor.phase), sensor_name_label: current_sensor.name}
            self.set(current_sensor_current, current_sensor.current, labels)
            self.set(current_sensor_power, current_sensor.power, labels)
            self.set(current_sensor_power_factor, current_sensor.power_factor, labels)

        for voltage_sensor in sensors.voltages:
            labels = {sensor_name_label: voltage_sensor.name}
            self.set_per_phase(voltage_sensor_voltage, voltage_sensor.values, labels)

        for category in sensors.categories:
            labels = {category_name_label: category.name}
            self.set(category_power, category.power, labels)
            self.set(category_energy_in, category.energy_in, labels)
            self.set(category_energy_out, category.energy_out, labels)
            self.set_per_phase(category_current, category.current, labels)

        self.set_time(time)

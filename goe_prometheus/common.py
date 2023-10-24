from goe.components.common import TimeServerSyncStatus

from goe_prometheus.util import gauge, enum

local_time = gauge('local_time_epoch_seconds',
                   'local time of the device (in seconds since UNIX epoch)')
utc_time = gauge('utc_time_epoch_seconds',
                 'UTC time of the device (in seconds since UNIX epoch)')

time_server_status = enum('time_server_sync_status', 'time server sync status',
                          [e.name for e in TimeServerSyncStatus])

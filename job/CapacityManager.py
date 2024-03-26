import psutil
import time
try:
    from time import time_ns
except ImportError:
    from datetime import datetime
    # For compatibility with Python 3.6
    def time_ns():
        now = datetime.now()
        return int(now.timestamp() * 1e9)

class CapacityManager:
    def __init__(self):
        self._sample_num = 100

        # self._received = psutil.net_io_counters().bytes_recv
        self._sent = psutil.net_io_counters().bytes_sent
        self._last_transfer_check_time = time.time()

        self._computing_capacities = []
        self._transfer_capacities = []

        self._computing_capacity_avg = 0
        self._transfer_capacity_avg = 0

    def _check_and_get_current_transfer_capacity(self):
        # cur_received = psutil.net_io_counters().bytes_recv
        cur_sent = psutil.net_io_counters().bytes_sent
        cur_time = time.time()

        sent_delta = (cur_sent - self._sent) / (cur_time - self._last_transfer_check_time) if cur_time - self._last_transfer_check_time > 1e-10 else 0

        self._sent = cur_sent
        self._last_transfer_check_time = cur_time

        return sent_delta

    def update_computing_capacity(self, computing_capacity):
        self._computing_capacities.append(computing_capacity)

        self._computing_capacities = self._computing_capacities[-self._sample_num:]

        self._computing_capacity_avg = sum(self._computing_capacities) / len(self._computing_capacities)

    def update_transfer_capacity(self):
        transfer_capacity = self._check_and_get_current_transfer_capacity()

        self._transfer_capacities.append(transfer_capacity)

        self._transfer_capacities = self._transfer_capacities[-self._sample_num:]

        self._transfer_capacity_avg = sum(self._transfer_capacities) / len(self._transfer_capacities)

    def get_computing_capacity(self):
        return self._computing_capacity_avg
    
    def get_transfer_capacity(self):
        return self._transfer_capacity_avg
        


class NetworkInfo:
    def __init__(self, network_config):
        self._network_config = network_config

        self._experiment_name = self._network_config["experiment_name"]
        self._jobs = self._network_config["jobs"]
        self._netowrk = self._network_config["network"]
        self._capacity = self._network_config["capacity"]
        self._scheduling_algorithm: str = self._network_config["scheduling_algorithm"]
        self._sync_time: float = self._network_config["sync_time"]
        self._collect_garbage_job_time: float = self._network_config["collect_garbage_job_time"]

    def get_experiment_name(self):
        return self._experiment_name

    def get_jobs(self):
        return self._jobs
    
    def get_network(self):
        return self._netowrk
    
    def get_capacity(self):
        return self._capacity
    
    def get_scheduling_algorithm(self):
        return self._scheduling_algorithm
    
    def get_sync_time(self):
        return self._sync_time
    
    def get_collect_garbage_job_time(self):
        return self._collect_garbage_job_time
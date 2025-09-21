from enum import Enum

class RequestType(Enum):
    CPU_INTENSIVE = "CPU"
    IO_INTENSIVE = "IO"

class LoadBalancingPolicy(Enum):
    RANDOM = "random"
    ROUND_ROBIN = "round_robin"
    SHORTEST_QUEUE = "shortest_queue"

class TrafficPattern(Enum):
    CONSTANT = "constant"
    BURST = "burst"

REQUEST_CONFIG = {
    "cpu_intensive": {
        "min_processing_time": 0.1,
        "max_processing_time": 0.5
    },
    "io_intensive": {
        "min_processing_time": 0.05,
        "max_processing_time": 0.2
    }
}



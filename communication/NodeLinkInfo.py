from typing import Dict
from layeredgraph import LayerNodePair

# info class for response sync
class NodeLinkInfo:
    def __init__(self, ip: str, links: Dict):
        self._ip = ip
        self._links = links

    def get_ip(self):
        return self._ip

    def get_links(self):
        return self._links
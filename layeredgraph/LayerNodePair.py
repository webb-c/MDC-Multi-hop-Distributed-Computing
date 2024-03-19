from layeredgraph import LayerNode

class LayerNodePair:
    def __init__(self, source: LayerNode, destination: LayerNode):
        self._source = source
        self._destination = destination

    def to_string(self):
        return f"{self._source.to_string()}->{self._destination.to_string()}"
    
    def get_source(self):
        return self._source
    
    def get_destinatioin(self):
        return self._destination
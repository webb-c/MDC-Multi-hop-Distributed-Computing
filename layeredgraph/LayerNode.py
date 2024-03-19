class LayerNode:
    def __init__(self, ip: str, layer: int):
        self._ip = ip
        self._layer = layer

    def get_ip(self):
        return self._ip
    
    def get_layer(self):
        return self._layer
    
    def is_same_layer(self, target_layer_node) -> bool:
        if self._layer == target_layer_node.get_layer():
            return True
        else:
            return False
        
    def is_same_node(self, target_layer_node)  -> bool:
        if self._ip == target_layer_node.get_ip():
            return True
        else:
            return False
        
    def is_same_layer_node(self, target_layer_node) -> bool:
        if self.is_same_layer(target_layer_node) and self.is_same_node(target_layer_node):
            return True
        else:
            return False
        
    def to_string(self) -> str:
        return f"{self._ip}-{self._layer}"
    
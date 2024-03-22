import subprocess, socket, re, os

import csv

import torch
from torchvision.models import resnet18, ResNet18_Weights

def get_ip_address(interface_name=["eth0"]):
    # check os
    for interface in interface_name:

        if os.name == "nt":  # windows
            ip = get_ip_address_windows(interface_name)
        else:  # linux / unix
            ip = get_ip_address_linux(interface_name)

        if "192.168.1" in ip:
            return ip

def get_ip_address_windows(interface_name='eth0'):
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_ip_address_linux(interface_name='eth0'):
    try:
        ip_addr_output = subprocess.check_output(["ip", "addr", "show", interface_name], encoding='utf-8')

        ip_pattern = re.compile(r"inet (\d+\.\d+\.\d+\.\d+)/")
        ip_match = ip_pattern.search(ip_addr_output)
        if ip_match:
            return ip_match.group(1)
        else:
            return "IP address not found"
    except subprocess.CalledProcessError:
        return "Failed to execute ip command or interface not found"
    

def save_latency(file_name, latency):
    file_path = f"{file_name}.csv"
    # 파일이 존재하는지 확인
    file_exists = os.path.exists(file_path)

    # 파일에 데이터 쓰기
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # 파일이 새로 만들어진 경우 열 이름을 씁니다.
        if not file_exists:
            writer.writerow(['latency'])
        
        # 데이터 행을 파일에 씁니다.
        writer.writerow([latency])


def split_model(model, split_point) -> torch.nn.Module:
    current_idx = 0
    layers = []
    start_index, end_index = split_point

    def _recursive_add_layers(module):
        nonlocal current_idx
        for child in module.children():
            if len(list(child.children())) == 0 : 
                if start_index <= current_idx < end_index:
                    layers
                current_idx += 1
            else: 
                _recursive_add_layers(child)            
        return

    _recursive_add_layers(model)
    splited_model = torch.nn.Sequential(*layers)

    return splited_model

def _split_model(self):
    """ object: backbone으로 사용할 모델을 로드하고 layer_idx를 기준으로 2개의 부분으로 모델을 나누어 반환합니다."""
    
    current_idx = 0
    part1_layers, part2_layers = [], []
    
    def _recursive_add_layers(module):
        nonlocal current_idx
        for child in module.children():
            if len(list(child.children())) == 0 : 
                if current_idx <= self.layer_idx:
                    part1_layers.append(child)
                else:
                    part2_layers.append(child)
                current_idx += 1
            else: 
                _recursive_add_layers(child)            
        return

    _recursive_add_layers(backbone)
    part1_model, part2_model = nn.Sequential(*part1_layers), nn.Sequential(*part2_layers[:-1])
    
    return part1_model, part2_model

def load_model(model_name) -> torch.nn.Module:

    available_model_list = ["yolov5", "resnet-18", "resnet-50"]

    assert model_name in available_model_list, f"Model must be in {available_model_list}."

    if model_name == "yolov5":
        return None # TODO
    
    elif model_name == "resnet-18":
        model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        model.eval()
        return model # TODO
    
    elif model_name == "resnet-50":
        return None # TODO
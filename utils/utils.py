import socket
import os

def get_ip_address(interface_name='eth0'):
    # 운영 체제 확인
    if os.name == 'nt':  # 윈도우
        return get_ip_address_windows(interface_name)
    else:  # 리눅스/유닉스
        return get_ip_address_linux(interface_name)

def get_ip_address_windows(interface_name='eth0'):
    # 윈도우에서는 인터페이스 이름 대신 socket.gethostbyname을 사용합니다.
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

def get_ip_address_linux(interface_name='eth0'):
    # 리눅스에서는 인터페이스 이름으로 IP 주소를 조회합니다.
    try:
        with open(f'/sys/class/net/{interface_name}/address', 'r') as f:
            ip_address = f.read().strip()
        return ip_address
    except FileNotFoundError:
        return "Interface not found"
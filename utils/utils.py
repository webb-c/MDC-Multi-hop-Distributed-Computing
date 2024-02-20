import subprocess
import socket
import re
import os
import csv

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
    # 리눅스에서 ip addr 명령어를 사용하여 IP 주소를 찾습니다.
    try:
        ip_addr_output = subprocess.check_output(["ip", "addr", "show", interface_name], encoding='utf-8')
        # inet으로 시작하는 줄에서 IP 주소를 찾기 위한 정규 표현식
        ip_pattern = re.compile(r"inet (\d+\.\d+\.\d+\.\d+)/")
        ip_match = ip_pattern.search(ip_addr_output)
        if ip_match:
            return ip_match.group(1)
        else:
            return "IP address not found"
    except subprocess.CalledProcessError:
        return "Failed to execute ip command or interface not found"
    

def save_latency(file_name, latency):
    file_path = f"results/{file_name}.csv"
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
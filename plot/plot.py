import pandas as pd
import glob
import os
import numpy as np
import matplotlib.pyplot as plt

FOLDER = "results_backup"

# 파일 경로 리스트
file_paths = glob.glob(f"./{FOLDER}/*")

print(file_paths)

# 데이터를 저장할 구조
data = {
    'sleeptime': {},
    'size': {},
    'it': {},  # 모든 파일에서 it는 100으로 고정
    'mode': {}
}

# 파일을 순회하며 데이터 읽기
for file_path in file_paths:
    # 파일 이름에서 정보 추출
    file_name = os.path.basename(file_path)
    parts = file_name.split('_')
    sleeptime = float(parts[1])
    size = int(parts[3])
    it = int(parts[5])  # it는 항상 100으로 고정되어 있으나, 일관성을 위해 포함
    mode = parts[7].split('.')[0]  # 확장자 제거
    
    # 파일에서 latency 데이터 읽기
    df = pd.read_csv(file_path)
    latency_mean = df['latency'].mean()
    
    # 데이터 구조에 저장
    data['sleeptime'].setdefault(sleeptime, []).append(latency_mean)
    data['size'].setdefault(size, []).append(latency_mean)
    data['it'].setdefault(it, []).append(latency_mean)
    data['mode'].setdefault(mode, []).append(latency_mean)

print(data)

# 각 변수별 평균 latency 계산 후 저장
results = {k: {key: np.mean(val) for key, val in v.items()} for k, v in data.items()}

# Plotting
fig, axs = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Latency Means by Different Parameters')

# sleeptime
sleeptimes = sorted(results['sleeptime'].keys())
latency_means = [results['sleeptime'][st] for st in sleeptimes]
axs[0, 0].plot(sleeptimes, latency_means, marker='o')
axs[0, 0].set_title('Latency vs Sleeptime')
axs[0, 0].set_xlabel('Sleeptime')
axs[0, 0].set_ylabel('Latency Mean')

# size
sizes = sorted(results['size'].keys())
latency_means = [results['size'][s] for s in sizes]
axs[0, 1].plot(sizes, latency_means, marker='o')
axs[0, 1].set_title('Latency vs Size')
axs[0, 1].set_xlabel('Size')
axs[0, 1].set_ylabel('Latency Mean')
axs[0, 1].set_xscale('log')

# mode
modes = sorted(results['mode'].keys())
latency_means = [results['mode'][m] for m in modes]
axs[1, 0].bar(modes, latency_means)
axs[1, 0].set_title('Latency vs Mode')
axs[1, 0].set_xlabel('Mode')
axs[1, 0].set_ylabel('Latency Mean')

# it는 모든 파일에서 동일하므로 그래프를 그리지 않음, 대신 빈 공간으로 남겨둠
axs[1, 1].axis('off')

plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
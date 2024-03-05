import pandas as pd
import glob
import os
import numpy as np
import matplotlib.pyplot as plt

FOLDER = "results"

# 파일 경로 리스트
file_paths = glob.glob(f"./{FOLDER}/*")

# 데이터를 저장할 구조
data = {
    'lower' : {
        'sleeptime': {},
        'size': {},
    },
    'upper' : {
        'sleeptime': {},
        'size': {},
    }
}

# 파일을 순회하며 데이터 읽기
for file_path in file_paths:
    # 파일 이름에서 정보 추출
    file_name = os.path.basename(file_path)
    parts = file_name.split('_')
    sleeptime = float(parts[1])
    size = int(parts[3])
    mode = parts[7].split('.')[0]  # 확장자 제거
    
    # 파일에서 latency 데이터 읽기
    df = pd.read_csv(file_path)
    latency_mean = df['latency'].mean()
    
    # 데이터 구조에 저장
    data[mode]['sleeptime'].setdefault(sleeptime, []).append(latency_mean)
    data[mode]['size'].setdefault(size, []).append(latency_mean)

# 각 변수별 평균 latency 계산 후 저장
results_lower = {k: {key: np.mean(val) for key, val in v.items()} for k, v in data['lower'].items()}
results_upper = {k: {key: np.mean(val) for key, val in v.items()} for k, v in data['upper'].items()}

differences = {
    'sleeptime' : {},
    'size' : {}
}

print(results_lower)
print(results_upper)

for criteria in differences:
    for key in results_lower[criteria]:
        diff = abs(results_lower[criteria][key] - results_upper[criteria][key])
        ratio = 100 * diff / min(results_lower[criteria][key], results_upper[criteria][key])
        differences[criteria][key] = [diff, ratio]

print(differences)

# Plotting
fig, axs = plt.subplots(3, 2, figsize=(14, 15))
fig.suptitle('Latency Means by Different Parameters')

# sleeptime
sleeptimes_lower = sorted(results_lower['sleeptime'].keys())
latency_means_lower = [results_lower['sleeptime'][st] for st in sleeptimes_lower]
sleeptimes_upper = sorted(results_upper['sleeptime'].keys())
latency_means_upper = [results_upper['sleeptime'][st] for st in sleeptimes_upper]
axs[0, 0].plot(sleeptimes_lower, latency_means_lower, marker='o', label='Lower')
axs[0, 0].plot(sleeptimes_upper, latency_means_upper, marker='o', label='Upper')
axs[0, 0].set_title('Latency vs Sleeptime')
axs[0, 0].set_xlabel('Sleeptime(s)')
axs[0, 0].set_ylabel('Latency Mean(ms)')
axs[0, 0].legend()

# sleeptime diff
sleeptimes = sorted(differences['sleeptime'].keys())
latency_diff = [differences['sleeptime'][st][0] for st in sleeptimes]
print(latency_diff)
axs[1, 0].plot(sleeptimes, latency_diff, marker='o', label='Lower')
axs[1, 0].set_title('Latency Diff vs Sleeptime')
axs[1, 0].set_xlabel('Sleeptime(s)')
axs[1, 0].set_ylabel('Latency Diff(ms)')

# sleeptime diff ratio
sleeptimes = sorted(differences['sleeptime'].keys())
latency_diff = [differences['sleeptime'][st][1] for st in sleeptimes]
print(latency_diff)
axs[2, 0].plot(sleeptimes, latency_diff, marker='o', label='Lower')
axs[2, 0].set_title('Latency Diff Ratio vs Sleeptime')
axs[2, 0].set_xlabel('Sleeptime(s)')
axs[2, 0].set_ylabel('Latency Diff Ratio(%)')

# size
sizes_lower = sorted(results_lower['size'].keys())
latency_means_lower = [results_lower['size'][s] for s in sizes_lower]
sizes_upper = sorted(results_upper['size'].keys())
latency_means_upper = [results_upper['size'][s] for s in sizes_upper]
axs[0, 1].plot(sizes_lower, latency_means_lower, marker='o', label='Lower')
axs[0, 1].plot(sizes_upper, latency_means_upper, marker='o', label='Upper')
axs[0, 1].set_title('Latency vs Size')
axs[0, 1].set_xlabel('Size(byte)')
axs[0, 1].set_ylabel('Latency Mean(ms)')
axs[0, 1].set_xscale('log')
axs[0, 1].legend()

# size diff
sizes = sorted(differences['size'].keys())
latency_diff = [differences['size'][st][0] for st in sizes]
print(latency_diff)
axs[1, 1].plot(sizes, latency_diff, marker='o', label='Lower')
axs[1, 1].set_title('Latency Diff vs Size')
axs[1, 1].set_xlabel('Size(byte)')
axs[1, 1].set_ylabel('Latency Diff(ms)')

# size diff ratio
sizes = sorted(differences['size'].keys())
latency_diff = [differences['size'][st][1] for st in sizes]
print(latency_diff)
axs[2, 1].plot(sizes, latency_diff, marker='o', label='Lower')
axs[2, 1].set_title('Latency Diff Ratio vs Size')
axs[2, 1].set_xlabel('Size(byte)')
axs[2, 1].set_ylabel('Latency Diff Ratio(%)')


plt.tight_layout(rect=[0, 0.03, 1, 0.95])
plt.show()
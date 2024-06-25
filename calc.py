import os
import json

# 定义文件目录
directory = '/root/hehaorui/results/casioa'  # 修改为你的JSON文件所在目录

# 初始化分数统计
test_sets = ['librispeech_test', 'emilia_test', 'overall']
quality_scores = {
    'librispeech_test': {'nar_emilia': 0, 'nar_mls': 0, 'ar_emilia': 0, 'ar_mls': 0},
    'emilia_test': {'nar_emilia': 0, 'nar_mls': 0, 'ar_emilia': 0, 'ar_mls': 0},
    'overall': {'nar_emilia': 0, 'nar_mls': 0, 'ar_emilia': 0, 'ar_mls': 0}
}
similarity_scores = {
    'librispeech_test': {'nar_emilia': 0, 'nar_mls': 0, 'ar_emilia': 0, 'ar_mls': 0},
    'emilia_test': {'nar_emilia': 0, 'nar_mls': 0, 'ar_emilia': 0, 'ar_mls': 0},
    'overall': {'nar_emilia': 0, 'nar_mls': 0, 'ar_emilia': 0, 'ar_mls': 0}
}
quality_counts = {
    'librispeech_test': 0,
    'emilia_test': 0,
    'overall': 0
}
similarity_counts = {
    'librispeech_test': 0,
    'emilia_test': 0,
    'overall': 0
}

# 判断文件属于哪个测试集
def determine_test_set(filename):
    parts = filename.split('/')
    print(parts[-1])
    if len(parts[-1]) == len("00939.wav"):
        return 'librispeech_test'
    else:
        return 'emilia_test'

# 遍历目录中的所有文件
files = os.listdir(directory)

print(files)

for filename in files:
    if filename.endswith('.json'):
        with open(os.path.join(directory, filename), 'r', encoding='utf-8') as file:
            data = json.load(file)
            wav_path = data['result'][0][1]
            test_set = determine_test_set(wav_path)
            # print(data)
            print(test_set)
            # 判断文件类型并统计分数和次数
            if data['type'] == 'quality':
                quality_counts[test_set] += 1
                quality_counts['overall'] += 1
                for result in data['result']:
                    system = result[0]
                    score = float(result[2])
                    if system in quality_scores[test_set]:
                        quality_scores[test_set][system] += score
                        quality_scores['overall'][system] += score
            elif data['type'] == 'sim':
                similarity_counts[test_set] += 1
                similarity_counts['overall'] += 1
                for result in data['result']:
                    system = result[0]
                    score = float(result[2])
                    if system in similarity_scores[test_set]:
                        similarity_scores[test_set][system] += score
                        similarity_scores['overall'][system] += score

# 计算平均分
def calculate_average(scores, counts):
    average_scores = {}
    for test_set in test_sets:
        average_scores[test_set] = {}
        for system, score in scores[test_set].items():
            if counts[test_set] > 0:
                average_scores[test_set][system] = score / counts[test_set]
            else:
                average_scores[test_set][system] = 0
    return average_scores

quality_averages = calculate_average(quality_scores, quality_counts)
similarity_averages = calculate_average(similarity_scores, similarity_counts)

# 打印统计结果
print("Quality Scores and Averages:")
for test_set in test_sets:
    print(f"\n{test_set}:")
    for system, score in quality_scores[test_set].items():
        print(f"{system} - Total: {score}, Average: {quality_averages[test_set][system]}")

print("\nSimilarity Scores and Averages:")
for test_set in test_sets:
    print(f"\n{test_set}:")
    for system, score in similarity_scores[test_set].items():
        print(f"{system} - Total: {score}, Average: {similarity_averages[test_set][system]}")

import json
from glob import glob

from collections import defaultdict

SINGING_VOICE_MOS_SETTINGS = [
    "gt",
    "hifigan_orig",
    "hifigan_merge",
    "hifigan_mscqtd",
    "hifigan_msstftd",
]

SPEECH_MOS_SETTINGS = [
    "gt_speech",
    "hifigan_orig_speech",
    "hifigan_merge_speech",
    "hifigan_mscqtd_speech",
    "hifigan_msstftd_speech",
]

PREFERENCE_SETTINGS = [
    ["melgan_orig", "melgan_merge"],
    ["bigvgan_orig", "bigvgan_merge"],
    ["nsfhifigan_orig", "nsfhifigan_merge"],
]

result_path = "results"

mos_scores_seen = defaultdict(list)
mos_scores_unseen = defaultdict(list)

mos_files = []
preference_files = []

preference_seen = defaultdict(list)
preference_unseen = defaultdict(list)

uids = glob(result_path + "/*")
for uid in uids:
    files = glob(uid + "/*.json")
    for file in files:
        if "mos" in file:
            mos_files.append(file)
        else:
            preference_files.append(file)

for file in mos_files:
    with open(file, "r") as f:
        tmp = json.load(f)
    results = tmp["result"]
    idx = tmp["subject_test_number"]

    for result in results:
        setting = result[0]
        rated_file = result[1]
        grade = result[2]
        if idx <= 5:
            seen_unseen = "seen"
        elif idx <= 10:
            seen_unseen = "unseen"
        elif idx <= 15:
            seen_unseen = "seen"
        else:
            seen_unseen = "unseen"
        if seen_unseen == "seen":
            mos_scores_seen[setting].append(grade)
        else:
            mos_scores_unseen[setting].append(grade)

for file in preference_files:
    with open(file, "r") as f:
        tmp = json.load(f)
    results = tmp["result"]
    idx = tmp["subject_test_number"]

    setting = results[0][0].split("_")[0]
    graded = results[int(tmp["grade"])][0].split("_")[1]

    if graded == "merge":
        added = 2
    else:
        added = 1
    if idx <= 9:
        if not setting in preference_seen.keys():
            preference_seen[setting] = [0, 0, 0]
        preference_seen[setting][0] += 1
        preference_seen[setting][added] += 1
    else:
        if not setting in preference_unseen.keys():
            preference_unseen[setting] = [0, 0, 0]
        preference_unseen[setting][0] += 1
        preference_unseen[setting][added] += 1

print("seen")
for setting in SINGING_VOICE_MOS_SETTINGS:
    print(setting)
    scores = mos_scores_seen[setting]
    total = 0
    for score in scores:
        total += float(score)
    print(total / len(scores))

for setting in SPEECH_MOS_SETTINGS:
    print(setting)
    scores = mos_scores_seen[setting]
    total = 0
    for score in scores:
        total += float(score)
    print(total / len(scores))

print("unseen")
for setting in SINGING_VOICE_MOS_SETTINGS:
    print(setting)
    scores = mos_scores_unseen[setting]
    total = 0
    for score in scores:
        total += float(score)
    print(total / len(mos_scores_unseen[setting]))

for setting in SPEECH_MOS_SETTINGS:
    print(setting)
    scores = mos_scores_unseen[setting]
    total = 0
    for score in scores:
        total += float(score)
    print(total / len(mos_scores_unseen[setting]))

print("seen")
for setting, result in preference_seen.items():
    print(setting)
    print(result[1] / result[0])
    print(result[2] / result[0])

print("unseen")
for setting, result in preference_unseen.items():
    print(setting)
    print(result[1] / result[0])
    print(result[2] / result[0])

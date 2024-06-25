import glob
import random
import time
import copy
import os
from tqdm import tqdm

from collections import defaultdict

SETTINGS = [
    "ref",
    "ar_emilia",
    "ar_mls",
    "nar_emilia",
    "nar_mls"
]

def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def parse_uid_from_audio_path(wav_file):
    uid = wav_file.split("/")[-1].split(".wav")[0].split("_ref")[0]
    return uid


def parse_dataset_from_audio_path(wav_file):
    speaker = wav_file.split("/")[-2]
    return speaker


def parse_system_from_audio_path(wav_file):
    system = wav_file.split("/")[-2]
    return system



sim_uid = []
quality_uid = []
folders = glob.glob("static/data/*")
for folder in folders:
    if not folder.split("/")[-1] in ["ref"]:
        continue
    wave_files = glob.glob("{}/*.wav".format(folder))
    for wave_file in wave_files:
        # get uid
        uid = os.path.basename(wave_file).split(".")[0].split("_ref")[0]
        sim_uid.append(uid)
        quality_uid.append(uid)

print(sim_uid)
print(quality_uid)
print(len(sim_uid), len(quality_uid))


def get_mos_test_audio(type):
    settings = copy.deepcopy(SETTINGS)
    if type == 'sim':
        test_audios = []
        uid = random.choice(sim_uid)
        print("sim_uid = ", sim_uid)
        sim_uid.remove(uid)
        print("uid = ", uid)
        print("num remaining sim_uid = ", len(sim_uid))
        print("remaining sim_uid = ", sim_uid)
        gt_path = "static/data/{}/{}_ref.wav".format('ref', uid)
        test_audios.append(gt_path)
        other_settings = settings[1:]
        random.shuffle(other_settings)
        for setting in other_settings:
            path = "static/data/{}/{}.wav".format(setting, uid)
            test_audios.append(path)
        return test_audios

    elif type == 'quality':
        test_audios = []
        uid = random.choice(quality_uid)
        print("quality_uid = ", quality_uid)
        print("uid = ", uid)
        quality_uid.remove(uid)
        print("num remaining quality_uid = ", len(quality_uid))
        print("remaining quality_uid = ", quality_uid)
        gt_path = "static/data/{}/{}_ref.wav".format('ref', uid)
        test_audios.append(gt_path)
        other_settings = settings[1:]
        random.shuffle(other_settings)
        for setting in other_settings:
            path = "static/data/{}/{}.wav".format(setting, uid)
            test_audios.append(path)
        return test_audios

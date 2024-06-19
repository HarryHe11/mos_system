from tqdm import tqdm
import torch
import torchaudio
import numpy as np
import glob
import os


def preprocess_for_audio(
    raw_wav_file, output_wav_file, target_sr, add_silence=True, volume_peak=0.9
):
    """
    preprocess:
    1. resample the audio to the target sampling rate
    2. Adjust the volume to make its peak is 0.9
    3. Add 50ms silence both in the front and the end to the audio (if add_silence == True)
    """

    # 1. Resample
    waveform, original_sr = torchaudio.load(raw_wav_file)
    if original_sr != target_sr:
        waveform = torchaudio.functional.resample(
            waveform, orig_freq=original_sr, new_freq=target_sr
        )

    # 2. Adjust the volume peak
    ratio = volume_peak / max(waveform.max(), abs(waveform.min()))
    waveform = waveform * ratio

    # 3. Add silence
    if add_silence:
        silence_len = target_sr // 20
        silence = torch.zeros(waveform.shape[0], silence_len, dtype=torch.float32)
        waveform = torch.cat([silence, waveform, silence], dim=1)

    torchaudio.save(
        output_wav_file, waveform, target_sr, encoding="PCM_S", bits_per_sample=16
    )


if __name__ == "__main__":
    raw_root_path = "./static/raw_wavs"
    output_root_path = "./static/data"
    target_sampling_rate = 24000

    raw_wav_files = glob.glob(os.path.join(raw_root_path, "**/*.wav"), recursive=True)
    print("Raw wavs: #sz = {}".format(len(raw_wav_files)))

    for raw_wav_file in tqdm(raw_wav_files):
        paths = raw_wav_file.split("/")
        wav_name = paths[-1]
        output_dir = "/".join(paths[:-1]).replace(raw_root_path, output_root_path)
        os.makedirs(output_dir, exist_ok=True)

        output_wav_file = os.path.join(output_dir, wav_name)
        preprocess_for_audio(
            raw_wav_file,
            output_wav_file,
            target_sr=target_sampling_rate,
            add_silence=True,
            volume_peak=0.9,
        )

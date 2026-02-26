import subprocess

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr[-2500:])
    return p.stdout

def normalize_to_wav(input_path, output_path):
    # Convert mp3/m4a/wav -> 44.1k stereo wav
    run(["ffmpeg","-y","-i",input_path,"-ar","44100","-ac","2",output_path])

def mix_vocals_over_inst(inst_path, vocal_path, output_path):
    # vocals slightly louder; simple amix
    run([
        "ffmpeg","-y",
        "-i", inst_path,
        "-i", vocal_path,
        "-filter_complex",
        "[1:a]volume=1.18[v];[0:a][v]amix=inputs=2:normalize=0",
        output_path
    ])

#!/usr/bin/python3
# -*- coding:utf-8 -*-
# For Python 3.5+ , By SpaceSkyNet

import json, os, sys, shutil, platform
import argparse, colorama
from colorama import Fore, Back, Style

def replace_illegal_chars(text):
    replace_chars = r'\/:*?"<>|'
    for replace_char in replace_chars:
        text = text.replace(replace_char, ",")
    return text

def get_parts_dirs(workspace_dir):
    parts_dirs = []
    for root, dirs, files in os.walk(workspace_dir, topdown=True):
        for dir in dirs:
            entry_json_path = os.path.join(workspace_dir, dir, 'entry.json')
            if os.path.exists(entry_json_path):
                parts_dirs.append(os.path.join(workspace_dir, dir))
        if len(parts_dirs) == 0:
            print(Fore.RED + "[Error]: No video parts!" + Style.RESET_ALL)
            sys.exit(0)
        else:
            entry_json_path = "entry.json"
            with open(os.path.join(parts_dirs[0], entry_json_path), 'r', encoding='utf-8') as f:
                text = json.loads(f.read())
            export_path = os.path.join(workspace_dir, "..", replace_illegal_chars(text["title"]))
            if not os.path.exists(export_path): os.mkdir(export_path)
            return export_path, parts_dirs

def get_media_type(parts_dir):
    entry_json_path = "entry.json"
    print(parts_dir)
    with open(os.path.join(parts_dir, entry_json_path), 'r', encoding='utf-8') as f:
        text = json.loads(f.read())
    media_type = text["media_type"]
    return media_type

def media_type_1(export_path, parts_dir): # merge *.flv (*.blv) | for others
    entry_json_path = "entry.json"
    entry_json_full_path = os.path.join(parts_dir, entry_json_path)
    cov_cmd = "ffmpeg -i {} -c copy -bsf:v h264_mp4toannexb -f mpegts {}"
    merge_cmd = 'ffmpeg -f concat -i {} -c copy -bsf:a aac_adtstoasc -movflags +faststart {}'
    
    with open(entry_json_full_path, 'r', encoding='utf-8') as f:
        text = json.loads(f.read())
    file_name = replace_illegal_chars(text["page_data"]["part"])
    type_tag = text["type_tag"]
    
    video_parts_dir = os.path.join(parts_dir, type_tag)
    work_dir = os.path.abspath(os.getcwd())
    index_json_path = "index.json"
    video_merged_path = "video.flv"
    video_merged_full_path = os.path.join(video_parts_dir, "video.flv")
    video_merge_info = "mylist.txt"
    
    os.chdir(video_parts_dir)
    with open(index_json_path, 'r', encoding='utf-8') as f:
        text = json.loads(f.read())
    video_parts = len(text["segment_list"])
    
    with open(video_merge_info, "w", encoding='utf-8') as f:
        for j in range(0, video_parts):
            f.write("file '{}.{}'\n".format(j, "blv"))
    
    os.system(merge_cmd.format(video_merge_info, video_merged_path))
    os.chdir(work_dir)
    
    video_out_path = os.path.join(export_path, "%s.flv" % file_name)
    shutil.move(video_merged_full_path, video_out_path)
    print(Fore.GREEN + "[Process]: {} is finished!".format(file_name) + Style.RESET_ALL)

def media_type_2(export_path, parts_dir): # mix video.m4s audio.m4s (*.mkv) | for 1080P+
    entry_json_path = "entry.json"
    entry_json_full_path = os.path.join(parts_dir, entry_json_path)
    mix_cmd = 'ffmpeg -i {0} -i {1} -vcodec copy -acodec aac -map 0:v:0 -map 1:a:0 {2}'
    mix_cmd_no_audio = 'ffmpeg -i {0} -vcodec copy -map 0:v:0 {1}'

    with open(entry_json_full_path, 'r', encoding='utf-8') as f:
        text = json.loads(f.read())
    file_name = replace_illegal_chars(text["page_data"]["part"])
    type_tag = text["type_tag"]
    
    video_parts_dir = os.path.join(parts_dir, type_tag)
    video_full_path = os.path.join(video_parts_dir, "video.m4s")
    audio_full_path = os.path.join(video_parts_dir, "audio.m4s")
    video_mixed_full_path = os.path.join(video_parts_dir, "video.mkv")
    
    if os.path.exists(audio_full_path): os.system(mix_cmd.format(video_full_path, audio_full_path, video_mixed_full_path))
    else: os.system(mix_cmd_no_audio.format(video_full_path, video_mixed_full_path))
    video_out_path = os.path.join(export_path, "%s.mkv" % file_name)
    shutil.move(video_mixed_full_path, video_out_path)
    print(Fore.GREEN + "[Process]: {} is finished!".format(file_name) + Style.RESET_ALL)

def check_ffmpeg():
    env_paths = os.environ["PATH"].split(';' if platform.system() == 'Windows' else ":")
    ffmpeg_file = "ffmpeg{}".format(".exe" if platform.system() == 'Windows' else "")
    for env_path in env_paths:
        if os.path.exists(os.path.join(env_path, ffmpeg_file)): return True
    return False

def video_processing(workspace_dir):
    if not check_ffmpeg(): 
        print(Fore.YELLOW + "[Warning]: Can not find ffmpeg in path! \nContinue(y/n)? " + Style.RESET_ALL, end = "")
        op = input()
        if op.lower() in ['y', 'yes']: 
            print(Fore.YELLOW + "[Warning]: Maybe cause some error..." + Style.RESET_ALL)
        else: 
            print(Fore.YELLOW + "[Warning]: Please make sure ffmpeg is in path!" + Style.RESET_ALL)
            sys.exit(0)
    if os.path.exists(workspace_dir):
        export_path, parts_dirs = get_parts_dirs(workspace_dir)
    else:
        print(Fore.RED + "[Error]: No such dir!" + Style.RESET_ALL)
        sys.exit(0)
    for parts_dir in parts_dirs:
        eval("media_type_{}(export_path, parts_dir)".format(get_media_type(parts_dir)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="bilibili download video mixer / merger by SpaceSkyNet", usage='%(prog)s [options]')
    parser.add_argument("-d", "--dir", type=str, help="the workspace_dir")
    args = parser.parse_args()
    colorama.init()
    
    if args.dir:
        video_processing(args.dir)
    else:
        parser.print_help()

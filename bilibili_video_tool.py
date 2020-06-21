#!/usr/bin/python3
# -*- coding:utf-8 -*-
# For Python 3.5+ , By SpaceSkyNet

import json, os, sys, shutil
import argparse, colorama
from colorama import Fore, Back, Style

def replace_illegal_chars(text):
    replace_chars = '\\/:*?"<>|'
    for replace_char in replace_chars:
        text = text.replace(replace_char, ",")
    return text

def get_video_parts_dirs(workspace_dir):
    video_parts_dirs = []
    for root, dirs, files in os.walk(workspace_dir, topdown=True):
        for dir in dirs:
            try: int(dir)
            except: pass
            else: video_parts_dirs.append(os.path.join(workspace_dir, dir))
        return video_parts_dirs

def get_media_type(parts):
    entry_json_path = "entry.json"
    if len(parts) == 0:
        print(Fore.RED + "[Error]: No video parts!" + Style.RESET_ALL)
        sys.exit(0)
    with open(os.path.join(parts[0], entry_json_path), 'r', encoding='utf-8') as f:
        text = json.loads(f.read())
    media_type = text["media_type"]
    return media_type

def media_type_1(parts): # merge *.flv (*.blv) | for others
    entry_json_path = "entry.json"
    cov_cmd = "ffmpeg -i {} -c copy -bsf:v h264_mp4toannexb -f mpegts {}"
    merge_cmd = 'ffmpeg -f concat -i {} -c copy -bsf:a aac_adtstoasc -movflags +faststart {}'
    
    if len(parts) == 0:
        print(Fore.RED + "[Error]: No video parts!" + Style.RESET_ALL)
        sys.exit(0)
    
    with open(os.path.join(parts[0], entry_json_path), 'r', encoding='utf-8') as f:
        text = json.loads(f.read())
    all_path = replace_illegal_chars(text["title"])
    
    if not os.path.exists(all_path):
        os.mkdir(all_path)
    for part in parts:
        entry_json_full_path = os.path.join(part, entry_json_path)
        
        with open(entry_json_full_path, 'r', encoding='utf-8') as f:
            text = json.loads(f.read())
        file_name = text["page_data"]["part"]
        type_tag = text["type_tag"]
        
        video_parts_dir = os.path.join(part, type_tag)
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
        
        video_out_path = os.path.join(all_path, "%s.flv" % file_name)
        shutil.move(video_merged_full_path, video_out_path)
        print(Fore.GREEN + "[Process]: {} is finished!".format(file_name) + Style.RESET_ALL)

def media_type_2(parts): # mix video.m4s audio.m4s (*.mkv) | for 1080P+
    entry_json_path = "entry.json"
    mix_cmd = 'ffmpeg -i {0} -i {1} -vcodec copy -acodec aac -map 0:v:0 -map 1:a:0 {2}'

    if len(parts) == 0:
        print("[Error]: No video parts!")
        sys.exit(0)

    with open(os.path.join(parts[0], entry_json_path), 'r', encoding='utf-8') as f:
        text = json.loads(f.read())
    all_path = replace_illegal_chars(text["title"])
    
    if not os.path.exists(all_path):
        os.mkdir(all_path)
    for part in parts:
        entry_json_full_path = os.path.join(part, entry_json_path)

        with open(entry_json_full_path, 'r', encoding='utf-8') as f:
            text = json.loads(f.read())
        file_name = text["page_data"]["part"]
        type_tag = text["type_tag"]
        
        video_full_path = os.path.join(part, type_tag, "video.m4s")
        audio_full_path = os.path.join(part, type_tag, "audio.m4s")
        video_mixed_full_path = os.path.join(part, type_tag, "video.mkv")
        
        os.system(mix_cmd.format(video_full_path, audio_full_path, video_mixed_full_path))
        video_out_path = os.path.join(all_path, "%s.mkv" % file_name)
        shutil.move(video_mixed_full_path, video_out_path)
        print(Fore.GREEN + "[Process]: {} is finished!".format(file_name) + Style.RESET_ALL)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="bilibili download video mixer / merger by SpaceSkyNet", usage='%(prog)s [options]')
    parser.add_argument("-d", "--dir", type=str, help="the workspace_dir")
    args = parser.parse_args()
    colorama.init()
    
    if args.dir:
        video_parts_dirs = get_video_parts_dirs(args.dir)
        eval("media_type_{}(video_parts_dirs)".format(get_media_type(video_parts_dirs)))
    else:
        parser.print_help()

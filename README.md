# bilibili手机缓存视频处理工具

> For **Python 3.5+**

从手机中复制出 `Android\data\tv.danmaku.bili\download\` 目录下数字编号目录（建议将该工具放入复制出目录的同级目录），并执行下面命令进行混流或合并：

Windows:
```bat
py -3.x bilibili_video_tool.py -d [Numbered Dir]
```

Linux / Mac:
```bash
python3 bilibili_video_tool.py -d [Numbered Dir]
```

**使用方法：**
```
usage: bilibili_video_tool.py [options]

bilibili download video mixer / merger by SpaceSkyNet

optional arguments:
  -h, --help         show this help message and exit
  -d DIR, --dir DIR  the workspace_dir
```
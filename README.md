# ComfyUI-fish-speech

Official Implementation

## 安装 / Installation

### 1. Windows 整合包

1. 下载本项目后，直接将 ComfyUI 文件夹拖拽覆盖原来的 ComfyUI 文件夹即可。
2. 用这个命令进行环境安装:
   ```bat
   .\python_embeded\python.exe -m pip install -r requirements.txt --no-warn-script-location
   ```
3. 模型安装：将 fish-speech 原项目的 checkpoints 文件夹覆盖 ComfyUI_windows_portable\ComfyUI\models\fish_speech\checkpoints 文件夹
4. 如需开启编译功能，需要安装 fish-speech 的官方环境。然后用其中的 run_cmd.bat 安装 ComfyUI 的环境，然后修改 ComfyUI\cuda_malloc.py 的最后一行，注释掉`os.environ['PYTORCH_CUDA_ALLOC_CONF'] = env_var`即可。最后用官方环境再运行 ComfyUI\main.py.

## 示意图 / diagram

<p align="center">
   <img src="./assets/diagram.png" width="100%">
</p>

## 用法 / usage

<p align="center">
   <img src="./assets/usage.png" width="100%">
</p>

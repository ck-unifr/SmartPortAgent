import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download, utils

def download_model(repo_id: str, local_dir: Path, use_mirror: bool = True):
    """
    Args:
        repo_id (str): 模型ID
        local_dir (Path): 本地存储路径对象
        use_mirror (bool): 是否使用国内镜像
    """
    # === 1. 设置环境变量 ===
    if use_mirror:
        if "HF_ENDPOINT" not in os.environ:
            os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        print(f"🔄 已启用镜像加速: {os.environ['HF_ENDPOINT']}")

    # 确保目标父目录存在 (即 model 文件夹存在)
    if not local_dir.parent.exists():
        local_dir.parent.mkdir(parents=True, exist_ok=True)

    print(f"🚀 准备下载: {repo_id}")
    print(f"📂 绝对路径: {local_dir}")

    try:
        # === 2. 执行下载 ===
        snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True
        )
        print(f"\n✅ 下载成功！")
        
    except Exception as e:
        print(f"\n❌ 下载失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # === 路径配置核心逻辑 ===
    # 1. 获取当前脚本所在的目录 (即 .../smart-port-agent/script)
    current_script_dir = Path(__file__).resolve().parent
    
    # 2. 获取项目根目录 (即 .../smart-port-agent)
    project_root = current_script_dir.parent
    
    # 3. 拼接目标路径 (即 .../smart-port-agent/model/m3e-base)
    # 这样无论你在哪里运行这个脚本，路径永远是正确的
    SAVE_DIR = project_root / "model" / "m3e-base"
    
    MODEL_ID = "moka-ai/m3e-base"
    
    # 开始下载
    download_model(MODEL_ID, SAVE_DIR, use_mirror=True)
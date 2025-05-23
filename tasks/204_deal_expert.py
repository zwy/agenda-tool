import json
import pathlib
import os
import re
import shutil
import urllib.parse
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

load_dotenv()  # 加载环境变量


def process_expert_data():
    """
    处理专家数据，检查头像是否存在，更新avatar字段为OSS URL，并复制头像文件到输出目录
    """
    # 加载环境变量
    OSS_CDN_URL = os.getenv("OSS_CDN_URL")
    OSS_DATA_DIR = os.getenv("OSS_DATA_DIR")
    
    if not OSS_CDN_URL or not OSS_DATA_DIR:
        logger.error("错误: 环境变量OSS_CDN_URL或OSS_DATA_DIR未设置!")
        return
    
    # 读取expert.jsonl文件
    input_file = pathlib.Path("data/expert.jsonl")
    
    if not input_file.exists():
        logger.error(f"错误: 文件 {input_file} 不存在!")
        return
    
    experts = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    expert = json.loads(line)
                    experts.append(expert)
        logger.info(f"已读取{len(experts)}条专家数据")
    except Exception as e:
        logger.error(f"读取数据时出错: {str(e)}")
        return
    
    # 处理每个专家的数据
    updated_count = 0
    error_count = 0
    warning_count = 0
    
    for expert in experts:
        session_name = expert.get("sessionName")
        expert_name = expert.get("expertName")
        
        if not session_name or not expert_name:
            logger.error(f"错误: 专家数据缺少sessionName或expertName字段: {expert}")
            continue
        # 处理路径中的特殊字符，如session_name 的换行符
        session_name = re.sub(r'[\r\n]', '', session_name)

        # 检查头像文件是否存在
        avatar_path = pathlib.Path(f"input/avatar/{session_name}/{expert_name}.png")

        # 确保头像路径存在，如果不存在则创建
        avatar_dir = avatar_path.parent
        avatar_dir.mkdir(parents=True, exist_ok=True)

        if not avatar_path.exists():
            logger.info(
                f"警告: 专家 {expert_name} 的头像文件不存在: {avatar_path} ，复制默认头像")
            warning_count += 1
            # 使用默认头像
            default_avatar_path = pathlib.Path("public/images/default_expert.png")
            if default_avatar_path.exists():
                shutil.copy2(default_avatar_path, avatar_path)
        
        # 编码URL中的特殊字符
        encoded_session_name = urllib.parse.quote(session_name)
        encoded_expert_name = urllib.parse.quote(expert_name)
        
        # 更新avatar字段
        expert["avatar"] = f"{OSS_CDN_URL}/{OSS_DATA_DIR}/avatar/{encoded_session_name}/{encoded_expert_name}.png"
        updated_count += 1
        
        # 确保输出目录存在
        output_dir = pathlib.Path(f"output/data/avatar/{session_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 复制头像文件到输出目录
        output_path = pathlib.Path(f"output/data/avatar/{session_name}/{expert_name}.png")
        shutil.copy2(avatar_path, output_path)
    
    if error_count > 0:
        logger.error(f"发现 {error_count} 个头像文件不存在的错误，处理已中止.")
        return
    if warning_count > 0:
        logger.warning(f"发现 {warning_count} 个头像文件不存在的警告，已跳过.")
    
    logger.info(f"已更新 {updated_count} 条专家记录的avatar字段")
    
    # 保存回文件
    try:
        with open(input_file, "w", encoding="utf-8") as f:
            for expert in experts:
                f.write(json.dumps(expert, ensure_ascii=False) + "\n")
        logger.info(f"已将更新后的数据保存到 {input_file}")
    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")


if __name__ == "__main__":
    process_expert_data()

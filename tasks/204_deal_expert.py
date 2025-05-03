import json
import pathlib
import os
import shutil
import urllib.parse
from dotenv import load_dotenv


def process_expert_data():
    """
    处理专家数据，检查头像是否存在，更新avatar字段为OSS URL，并复制头像文件到输出目录
    """
    # 加载环境变量
    load_dotenv()
    OSS_CDN_URL = os.getenv("OSS_CDN_URL")
    OSS_DATA_DIR = os.getenv("OSS_DATA_DIR")
    
    if not OSS_CDN_URL or not OSS_DATA_DIR:
        print("错误: 环境变量OSS_CDN_URL或OSS_DATA_DIR未设置!")
        return
    
    # 读取expert.jsonl文件
    input_file = pathlib.Path("data/expert.jsonl")
    
    if not input_file.exists():
        print(f"错误: 文件 {input_file} 不存在!")
        return
    
    experts = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    expert = json.loads(line)
                    experts.append(expert)
        print(f"已读取{len(experts)}条专家数据")
    except Exception as e:
        print(f"读取数据时出错: {str(e)}")
        return
    
    # 处理每个专家的数据
    updated_count = 0
    error_count = 0
    
    for expert in experts:
        session_name = expert.get("sessionName")
        expert_name = expert.get("expertName")
        
        if not session_name or not expert_name:
            print(f"错误: 专家数据缺少sessionName或expertName字段: {expert}")
            continue
        
        # 检查头像文件是否存在
        avatar_path = pathlib.Path(f"input/avatar/{session_name}/{expert_name}.png")
        
        if not avatar_path.exists():
            print(f"错误: 专家 {expert_name} 的头像文件不存在: {avatar_path}")
            error_count += 1
            continue
        
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
        print(f"发现 {error_count} 个头像文件不存在的错误，处理已中止.")
        return
    
    print(f"已更新 {updated_count} 条专家记录的avatar字段")
    
    # 保存回文件
    try:
        with open(input_file, "w", encoding="utf-8") as f:
            for expert in experts:
                f.write(json.dumps(expert, ensure_ascii=False) + "\n")
        print(f"已将更新后的数据保存到 {input_file}")
    except Exception as e:
        print(f"保存数据时出错: {str(e)}")


if __name__ == "__main__":
    process_expert_data()

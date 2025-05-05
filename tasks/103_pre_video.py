import os
import pandas as pd
import json
import pathlib
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

load_dotenv()  # 加载环境变量

def process_video_data():
    """处理视频数据，从CSV读取并转换为JSONL格式"""
    # 加载JSON Schema
    schema_path = pathlib.Path("model/oss_video.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # 创建标题到字段的映射
    title_to_field = {}
    for field, config in schema.get("properties", {}).items():
        title = config.get("title", "")
        if title:
            title_to_field[title] = field
    
    # 获取所有CSV文件
    input_dir = pathlib.Path("input/video")
    csv_files = list(input_dir.glob("*.csv"))
    
    # 读取现有的JSONL文件(如果存在)
    existing_videos = {}
    output_dir = pathlib.Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "video.jsonl"
    
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        video = json.loads(line)
                        if "aliyunVid" in video:
                            existing_videos[video["aliyunVid"]] = video
            logger.info(f"已读取{len(existing_videos)}条现有视频数据")
        except Exception as e:
            logger.error(f"读取现有数据时出错: {str(e)}")
    
    # 处理每个CSV文件
    for csv_file in csv_files:
        logger.info(f"处理文件: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            
            for _, row in df.iterrows():
                video = {}
                
                # 处理CSV中的列名并转为字段
                for cn_title, en_field in title_to_field.items():
                    if cn_title in df.columns and pd.notna(row.get(cn_title, "")):
                        video[en_field] = str(row.get(cn_title, ""))
                    elif en_field in df.columns and pd.notna(row.get(en_field, "")):
                        # 兼容可能使用英文字段作为列名的情况
                        video[en_field] = str(row.get(en_field, ""))
                
                # 处理 媒体时长(s) 字段，如果存在，这个 字段里的数据是以秒为单位的，我们需要转成分钟，例如 120秒 = 2:00
                if "duration" in video and video["duration"]:
                    try:
                        # 将秒转换为整数
                        seconds = int(float(video["duration"]))
                        # 计算分钟和剩余秒
                        minutes = seconds // 60
                        remaining_seconds = seconds % 60
                        # 格式化为 "分钟:秒" 格式
                        video["duration"] = f"{minutes}:{remaining_seconds:02d}"
                    except ValueError:
                        logger.error(f"错误: 无法解析视频时长值: {video['duration']}")

                # 验证必填字段
                required_fields = schema.get("required", [])
                missing_fields = [field for field in required_fields if field not in video or not video[field]]
                
                if not missing_fields:
                    # 检查是否已存在相同aliyunVid的记录
                    if "aliyunVid" in video and video["aliyunVid"] in existing_videos:
                        # 如果存在，更新现有记录
                        existing_video = existing_videos[video["aliyunVid"]]
                        existing_video.update(video)
                        existing_videos[video["aliyunVid"]] = existing_video
                        logger.info(f"更新已存在的视频: {video['aliyunVid']}")
                    elif "aliyunVid" in video:
                        # 如果不存在，添加新记录
                        existing_videos[video["aliyunVid"]] = video
                        logger.info(f"添加新视频: {video['aliyunVid']}")
                else:
                    logger.error(f"错误: 跳过缺少必填字段的记录: {missing_fields}")
                    
        except Exception as e:
            logger.error(f"处理文件 {csv_file} 时出错: {str(e)}")
    
    # 写入JSONL文件
    with open(output_file, "w", encoding="utf-8") as f:
        for video in existing_videos.values():
            f.write(json.dumps(video, ensure_ascii=False) + "\n")
    
    logger.info(f"成功处理视频数据并保存到 {output_file}，共 {len(existing_videos)} 条记录")

if __name__ == "__main__":
    process_video_data()

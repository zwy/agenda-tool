import json
import pathlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)


def process_video_data():
    """处理视频数据，为缺失字段设置默认值"""
    # 读取video.jsonl文件
    input_file = pathlib.Path("data/video.jsonl")

    if not input_file.exists():
        logger.error(f"错误: 文件 {input_file} 不存在!")
        return

    videos = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    video = json.loads(line)
                    videos.append(video)
        logger.info(f"已读取{len(videos)}条视频数据")
    except Exception as e:
        logger.error(f"读取数据时出错: {str(e)}")
        return

    # 处理缺失字段
    updated_count = 0
    for video in videos:
        updated = False
        
        # 处理permission字段
        if "permission" not in video or not video["permission"]:
            video["permission"] = "授权"
            updated = True
            
        # 处理duration字段
        if "duration" not in video or not video["duration"]:
            video["duration"] = "0:00"
            updated = True
            
        # 处理cover字段
        if "cover" not in video or not video["cover"]:
            video["cover"] = ""
            updated = True
            
        if updated:
            updated_count += 1

    logger.info(f"已更新{updated_count}条记录的字段")

    # 保存回文件
    try:
        with open(input_file, "w", encoding="utf-8") as f:
            for video in videos:
                f.write(json.dumps(video, ensure_ascii=False) + "\n")
        logger.info(f"已将更新后的数据保存到 {input_file}")
    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")


if __name__ == "__main__":
    process_video_data()

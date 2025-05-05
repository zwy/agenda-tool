import json
import os
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

def read_jsonl(file_path):
    """
    读取JSONL文件并返回数据列表
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        logger.info(f"成功读取{len(data)}条壁报数据")
        return data
    except Exception as e:
        logger.error(f"读取JSONL文件失败: {e}")
        return []

def validate_bibao_data(bibao):
    """
    验证壁报数据是否包含必要字段
    """
    required_fields = ["boardNum", "reportTitle", "theme", "name", "employer", "position"]
    for field in required_fields:
        if field not in bibao or not bibao[field]:
            logger.warning(f"壁报 {bibao.get('boardNum', '未知')} 缺少必要字段: {field}")
            return False
    return True

def create_output_directory(directory):
    """
    创建输出目录
    """
    try:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"输出目录已创建或已存在: {directory}")
        return True
    except Exception as e:
        logger.error(f"创建输出目录失败: {e}")
        return False

def save_json_file(data, file_path):
    """
    保存数据到JSON文件
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"成功保存JSON文件: {file_path}")
        return True
    except Exception as e:
        logger.error(f"保存JSON文件失败: {e}")
        return False

def process_bibao_data():
    """
    处理壁报数据并生成单独的JSON文件
    """
    # 输入和输出路径
    input_file = "data/bibao.jsonl"
    output_dir = "output/data/bibao"
    
    # 读取JSONL数据
    bibao_data = read_jsonl(input_file)
    if not bibao_data:
        logger.error("没有找到壁报数据，终止处理")
        return False
    
    # 创建输出目录
    if not create_output_directory(output_dir):
        return False
    
    # 处理每条壁报数据
    success_count = 0
    for bibao in bibao_data:
        # 验证数据
        if not validate_bibao_data(bibao):
            continue
        
        # 获取boardNum作为文件名
        board_num = bibao.get("boardNum")
        if not board_num:
            logger.warning("跳过没有boardNum的壁报数据")
            continue
        
        # 设置输出文件路径
        output_file = os.path.join(output_dir, f"{board_num}.json")
        
        # 保存到JSON文件
        if save_json_file(bibao, output_file):
            success_count += 1
    
    logger.info(f"成功处理了 {success_count}/{len(bibao_data)} 条壁报数据")
    return success_count > 0

if __name__ == "__main__":
    logger.info("开始处理壁报数据...")
    if process_bibao_data():
        logger.info("壁报数据处理完成")
    else:
        logger.error("壁报数据处理失败")

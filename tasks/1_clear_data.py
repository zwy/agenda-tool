import os
import shutil
import pandas as pd
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

def read_data_folder():
    """读取data文件夹中的所有数据文件"""
    data_dir = Path(__file__).parent.parent / 'data'
    
    if not data_dir.exists():
        logger.warning(f"数据文件夹 {data_dir} 不存在")
        return {}
    
    data_files = {}
    
    # 遍历文件夹中的所有文件
    for file_path in data_dir.iterdir():
        if file_path.is_file():
            file_name = file_path.name
            # 根据文件扩展名处理不同类型的文件
            if file_path.suffix.lower() == '.csv':
                try:
                    data_files[file_name] = pd.read_csv(file_path)
                    logger.info(f"已读取CSV文件: {file_name}")
                except Exception as e:
                    logger.error(f"读取文件 {file_name} 出错: {e}")
            
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                try:
                    data_files[file_name] = pd.read_excel(file_path)
                    logger.info(f"已读取Excel文件: {file_name}")
                except Exception as e:
                    logger.error(f"读取文件 {file_name} 出错: {e}")
            
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data_files[file_name] = f.read()
                    logger.info(f"已读取文本文件: {file_name}")
                except Exception as e:
                    logger.error(f"读取文件 {file_name} 出错: {e}")
    
    return data_files

def clear_data_folder():
    """清空data文件夹中的所有文件"""
    data_dir = Path(__file__).parent.parent / 'data'
    
    if not data_dir.exists():
        logger.warning(f"数据文件夹 {data_dir} 不存在")
        return
    
    # 遍历并删除文件夹中的所有文件
    for file_path in data_dir.iterdir():
        if file_path.is_file():
            try:
                file_path.unlink()
                logger.info(f"已删除文件: {file_path.name}")
            except Exception as e:
                logger.error(f"删除文件 {file_path.name} 失败: {e}")
        elif file_path.is_dir():
            try:
                shutil.rmtree(file_path)
                logger.info(f"已删除子文件夹: {file_path.name}")
            except Exception as e:
                logger.error(f"删除子文件夹 {file_path.name} 失败: {e}")
    
    logger.info("数据文件夹已清空")

if __name__ == "__main__":
    # 首先读取数据
    data = read_data_folder()
    logger.info(f"共读取了 {len(data)} 个文件")
    
    # 然后清空文件夹
    clear_data_folder()

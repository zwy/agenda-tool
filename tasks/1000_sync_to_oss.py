import os
import sys
import logging
from dotenv import load_dotenv
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 获取OSS相关配置
OSS_ACCESS_KEY_ID = os.getenv('OSS_ACCESS_KEY_ID')
OSS_ACCESS_KEY_SECRET = os.getenv('OSS_ACCESS_KEY_SECRET')
OSS_ENDPOINT = os.getenv('OSS_ENDPOINT')
OSS_REGION = os.getenv('OSS_REGION')
OSS_BUCKET_NAME = os.getenv('OSS_BUCKET_NAME')
OSS_DATA_DIR = os.getenv('OSS_DATA_DIR')

# 定义本地数据目录
LOCAL_DATA_DIR = Path(__file__).parent.parent / 'output' / 'data'

# 初始化OSS连接
import oss2

def init_bucket():
    """初始化OSS Bucket连接"""
    if not all([OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_ENDPOINT, OSS_REGION, OSS_BUCKET_NAME]):
        logger.error("OSS配置不完整，请检查环境变量")
        sys.exit(1)
        
    auth = oss2.AuthV4(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME, region=OSS_REGION)
    return bucket

# 将上传函数改为同步函数，避免异步调用问题
def upload_file_to_oss(local_file, remote_path):
    """上传文件到OSS"""
    bucket = init_bucket()
    try:
        result = bucket.put_object_from_file(remote_path, local_file)
        if result.status == 200:
            return True
        else:
            logger.error(f"上传失败: {local_file} -> {remote_path}, 状态码: {result.status}")
            return False
    except Exception as e:
        logger.error(f"上传出错: {local_file} -> {remote_path}, 错误: {str(e)}")
        return False

# 避免使用async/await，修改为同步函数
def sync_files_to_oss():
    """同步本地文件到OSS"""
    if not LOCAL_DATA_DIR.exists():
        logger.warning(f"本地数据目录不存在: {LOCAL_DATA_DIR}")
        return
    
    if not OSS_DATA_DIR:
        logger.error("OSS_DATA_DIR 环境变量未设置")
        return
    
    logger.info(f"开始同步文件到OSS，本地目录: {LOCAL_DATA_DIR}")
    logger.info(f"目标OSS路径: {OSS_DATA_DIR}")
    
    total_files = 0
    uploaded_files = 0
    
    # 遍历目录下的所有文件
    for file_path in LOCAL_DATA_DIR.glob('**/*'):
        # 类似 .DS_Store 的文件不上传
        if file_path.name.startswith('.'):
            continue
        if file_path.is_file():
            total_files += 1
            # 计算相对路径
            rel_path = file_path.relative_to(LOCAL_DATA_DIR)
            # 构建OSS目标路径
            oss_path = f"{OSS_DATA_DIR}/{rel_path}".replace('\\', '/')
            
            logger.info(f"正在上传: {rel_path} -> {oss_path}")
            if upload_file_to_oss(str(file_path), oss_path):
                logger.info(f"上传成功: {rel_path}")
                uploaded_files += 1
            else:
                logger.error(f"上传失败: {rel_path}")
            
            # 每上传一个文件暂停一小段时间，避免请求过于频繁
            time.sleep(0.2)  # 使用普通的time.sleep代替asyncio.sleep
    
    logger.info(f"文件同步完成。总文件数: {total_files}, 成功上传: {uploaded_files}")

# 修改为同步主函数
def main():
    """主函数"""
    logger.info("开始执行OSS同步任务")
    sync_files_to_oss()
    logger.info("OSS同步任务完成")

if __name__ == "__main__":
    # 添加time模块导入
    import time
    # 直接调用同步函数，不使用asyncio
    main()

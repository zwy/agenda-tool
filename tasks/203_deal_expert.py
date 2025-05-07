import json
import os
import re
import logging
import asyncio
import aiohttp
from pathlib import Path
from urllib.parse import unquote, urlparse, parse_qs
from PIL import Image
import io
import oss2
from dotenv import load_dotenv

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

# 初始化OSS连接
def init_bucket():
    """初始化OSS Bucket连接"""
    if not all([OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET, OSS_ENDPOINT, OSS_REGION, OSS_BUCKET_NAME]):
        logger.error("OSS配置不完整，请检查环境变量")
        return None
        
    auth = oss2.AuthV4(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME, region=OSS_REGION)
    return bucket

async def fetch_expert_detail(name, uuid):
    """从API获取专家详情"""
    url = f"https://rbasefront.chinagut.cn/f/author/detail2?name={name}&uuid={uuid}"
    logger.info(f"获取专家详情: {url}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"API请求失败: {response.status}")
                    return None
        except Exception as e:
            logger.error(f"请求异常: {str(e)}")
            return None

def extract_rbase_params(rbase_url):
    """从rbaseUrl中提取authorName和authorUuid"""
    if not rbase_url:
        return None, None
    
    # 解析URL
    parsed_url = urlparse(rbase_url)
    query_params = parse_qs(parsed_url.query)
    
    # 获取参数
    author_name = query_params.get('authorName', [None])[0]
    author_uuid = query_params.get('authorUuid', [None])[0]
    
    if author_name:
        author_name = unquote(author_name).replace(' ', '+')
    
    return author_name, author_uuid

async def download_avatar(avatar_path, session_name, expert_name):
    """从阿里云OSS下载头像"""
    if not avatar_path:
        logger.warning(f"专家 {expert_name} 没有头像")
        return None
    
    # 去掉路径开头的'/'
    if avatar_path.startswith('/'):
        avatar_path = avatar_path[1:]
    
    # 处理路径中的特殊字符，如session_name 的换行符
    session_name = re.sub(r'[\r\n]', '', session_name)

    # 创建本地保存目录
    local_dir = Path(f"input/avatar/{session_name}")
    local_dir.mkdir(parents=True, exist_ok=True)
    
    # 本地文件路径
    local_file = local_dir / f"{expert_name}.png"
    
    # 从OSS下载头像
    bucket = init_bucket()
    if not bucket:
        return None
    
    try:
        # 先获取文件内容
        object_stream = bucket.get_object(avatar_path)
        # 读取文件内容
        img_data = object_stream.read()
        
        # 使用PIL打开图片
        img = Image.open(io.BytesIO(img_data))
        
        # 转换为PNG格式并保存
        img.save(str(local_file), 'PNG')
        
        logger.info(f"头像已保存: {local_file}")
        return str(local_file)
    except oss2.exceptions.NoSuchKey:
        logger.error(f"OSS中不存在该文件: {avatar_path}")
        return None
    except Exception as e:
        logger.error(f"下载头像失败: {str(e)}")
        return None

async def process_expert(expert):
    """处理单个专家信息"""
    session_name = expert.get('sessionName')
    expert_name = expert.get('expertName')
    rbase_url = expert.get('rbaseUrl')
    
    if not rbase_url:
        logger.info(f"专家 {expert_name} 没有rbaseUrl，跳过")
        return expert
    
    author_name, author_uuid = extract_rbase_params(rbase_url)
    if not author_name or not author_uuid:
        logger.warning(f"无法从URL提取参数: {rbase_url}")
        return expert
    
    # 获取专家详情
    detail_data = await fetch_expert_detail(author_name, author_uuid)
    if not detail_data or detail_data.get('code') != 200:
        logger.error(f"获取专家详情失败: {expert_name}")
        return expert
    
    # 获取头像路径
    avatar_path = detail_data.get('data', {}).get('avatar')
    if not avatar_path:
        logger.warning(f"专家 {expert_name} 在API中没有头像")
        return expert
    
    # 下载头像
    await download_avatar(avatar_path, session_name, expert_name)
    
    return expert

async def process_experts():
    """处理专家数据"""
    # 读取expert.jsonl文件
    input_file = Path("data/expert.jsonl")
    if not input_file.exists():
        logger.error(f"文件不存在: {input_file}")
        return
    
    experts = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    expert = json.loads(line)
                    experts.append(expert)
        logger.info(f"读取了 {len(experts)} 条专家数据")
    except Exception as e:
        logger.error(f"读取专家数据失败: {str(e)}")
        return
    
    # 处理每个专家
    for expert in experts:
        await process_expert(expert)
    
async def main():
    """主函数"""
    logger.info("开始处理专家头像")
    await process_experts()
    logger.info("专家头像处理完成")

if __name__ == "__main__":
    asyncio.run(main())

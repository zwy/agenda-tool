import os
import pandas as pd
import json
import base64
from pathlib import Path
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# 尝试导入拼音库，如果不存在则提示安装
try:
    from pypinyin import lazy_pinyin
except ImportError:
    logger.error("需要安装pypinyin库，请运行: pip install pypinyin")
    logger.error("然后在requirements.txt中添加pypinyin")
    raise

load_dotenv()  # 加载环境变量

meeting_id = os.getenv('MEETING_ID', '')

def generate_pinyin(name):
    """根据专家姓名生成拼音"""
    if not name:
        return ""
    pinyin_list = lazy_pinyin(name)
    return ' '.join(pinyin_list)

def process_expert_data():
    """处理专家数据，从Excel读取并转换为JSONL格式"""
    # 加载JSON Schema
    schema_path = Path("model/expert.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # 创建中文标题到英文字段名的映射
    title_to_field = {}
    for field, config in schema.get("properties", {}).items():
        title = config.get("title", "")
        if title:
            title_to_field[title] = field
    
    # 获取所有Excel文件
    input_dir = Path("input/expert")
    input_dir.mkdir(exist_ok=True)  # 确保目录存在
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    
    # 读取现有的JSONL文件(如果存在)
    existing_experts = {}
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "expert.jsonl"
    
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        expert = json.loads(line)
                        if "expertCode" in expert:
                            existing_experts[expert["expertCode"]] = expert
            logger.info(f"已读取{len(existing_experts)}条现有专家数据")
        except Exception as e:
            logger.error(f"读取现有数据时出错: {str(e)}")
    
    # 处理每个Excel文件
    all_experts = []
    for excel_file in excel_files:
        logger.info(f"处理文件: {excel_file}")
        try:
            df = pd.read_excel(excel_file)
            
            for _, row in df.iterrows():
                expert = {}
                
                # 处理Excel中的中文列名并转为英文字段
                for cn_title, en_field in title_to_field.items():
                    if cn_title in df.columns and pd.notna(row.get(cn_title, "")):
                        expert[en_field] = str(row.get(cn_title, ""))
                    elif en_field in df.columns and pd.notna(row.get(en_field, "")):
                        # 兼容可能使用英文字段作为列名的情况
                        expert[en_field] = str(row.get(en_field, ""))
                
                # 确保必填字段存在
                if "sessionName" not in expert or not expert["sessionName"]:
                    logger.error(f"错误: 跳过缺少分会场名称的记录")
                    continue
                
                if "expertName" not in expert or not expert["expertName"]:
                    logger.error(f"错误: 跳过缺少专家姓名的记录")
                    continue
                
                # 生成专家编码，基于（分会场名称+专家姓名+meeting）
                code_str = expert["sessionName"] + expert["expertName"] + meeting_id
                expert["expertCode"] = base64.urlsafe_b64encode(
                    code_str.encode('utf-8')).decode('utf-8').rstrip('=')
                
                # 生成拼音
                if "expertName" in expert and expert["expertName"]:
                    expert["pinyin"] = generate_pinyin(expert["expertName"])
                
                # 验证必填字段
                required_fields = schema.get("required", [])
                missing_fields = [field for field in required_fields if field not in expert or not expert[field]]
                
                if not missing_fields:
                    # 检查是否已存在相同expertCode的记录
                    if expert["expertCode"] in existing_experts:
                        # 更新现有记录，保留旧的值如果新的没有提供
                        existing_expert = existing_experts[expert["expertCode"]]
                        for k, v in existing_expert.items():
                            if k not in expert or not expert[k]:
                                expert[k] = v
                        existing_experts[expert["expertCode"]] = expert
                        logger.info(f"更新已存在的专家: {expert['expertName']} ({expert['sessionName']})")
                    else:
                        # 添加新记录
                        existing_experts[expert["expertCode"]] = expert
                        logger.info(f"添加新专家: {expert['expertName']} ({expert['sessionName']})")
                else:
                    logger.error(f"错误: 跳过缺少必填字段的记录: {missing_fields}")
                
                all_experts.append(expert)
                    
        except Exception as e:
            logger.error(f"处理文件 {excel_file} 时出错: {str(e)}")
    
    # 写入JSONL文件
    with open(output_file, "w", encoding="utf-8") as f:
        for expert in existing_experts.values():
            f.write(json.dumps(expert, ensure_ascii=False) + "\n")
    
    logger.info(f"成功处理专家数据并保存到 {output_file}，共 {len(existing_experts)} 条记录")

if __name__ == "__main__":
    process_expert_data()

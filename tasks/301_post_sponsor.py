import json
import pathlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

def process_output_sponsor():
    """根据 sponsor.jsonl 生成 sponsors.json 输出文件"""
    # 读取 sponsor.jsonl 文件
    input_file = pathlib.Path("data/sponsor.jsonl")
    if not input_file.exists():
        logger.error(f"错误: 文件 {input_file} 不存在!")
        return

    # 读取 schema 文件
    schema_file = pathlib.Path("output/model/sponsors.json")
    if not schema_file.exists():
        logger.error(f"错误: Schema文件 {schema_file} 不存在!")
        return
    
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
            # 获取必填字段列表
            required_fields = schema.get("items", {}).get("required", [])
    except Exception as e:
        logger.error(f"读取Schema时出错: {str(e)}")
        return

    sponsors = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    sponsor = json.loads(line)
                    # 验证必填字段
                    missing_fields = [field for field in required_fields if field not in sponsor or not sponsor[field]]
                    if missing_fields:
                        logger.error(f"错误: 记录缺少必填字段: {missing_fields}, 跳过该记录")
                        continue
                    sponsors.append(sponsor)
        logger.info(f"已读取并验证{len(sponsors)}条赞助商数据")
    except Exception as e:
        logger.error(f"读取数据时出错: {str(e)}")
        return
    
    # 确保输出目录存在
    output_dir = pathlib.Path("output/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "sponsors.json"
    
    # 将数据保存为 JSON 文件
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(sponsors, f, ensure_ascii=False, indent=2)
        logger.info(f"已将赞助商数据保存到 {output_file}，共 {len(sponsors)} 条记录")
    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")

if __name__ == "__main__":
    process_output_sponsor()

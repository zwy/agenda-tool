import os
import pandas as pd
import json
import pathlib
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

meeting_id = os.getenv('MEETING_ID', '')

def process_sponsor_data():
    """处理赞助商数据，从Excel读取并转换为JSONL格式"""
    # 加载JSON Schema
    schema_path = pathlib.Path("model/sponsor.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # 创建中文标题到英文字段名的映射
    title_to_field = {}
    for field, config in schema.get("properties", {}).items():
        title = config.get("title", "")
        if title:
            title_to_field[title] = field
    
    # 获取所有Excel文件
    input_dir = pathlib.Path("input/sponsor")
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    
    # 读取现有的JSONL文件(如果存在)
    existing_sponsors = {}
    output_dir = pathlib.Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "sponsor.jsonl"
    
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        sponsor = json.loads(line)
                        # 使用 sessionName + sponsorName 作为唯一标识
                        if "sessionName" in sponsor and "sponsorName" in sponsor:
                            key = f"{sponsor['sessionName']}_{sponsor['sponsorName']}"
                            existing_sponsors[key] = sponsor
            print(f"已读取{len(existing_sponsors)}条现有赞助商数据")
        except Exception as e:
            print(f"读取现有数据时出错: {str(e)}")
    
    # 处理每个Excel文件
    for excel_file in excel_files:
        print(f"处理文件: {excel_file}")
        try:
            df = pd.read_excel(excel_file)
            
            for _, row in df.iterrows():
                sponsor = {}
                
                # 处理Excel中的中文列名并转为英文字段
                for cn_title, en_field in title_to_field.items():
                    if cn_title in df.columns and pd.notna(row.get(cn_title, "")):
                        sponsor[en_field] = str(row.get(cn_title, ""))
                    elif en_field in df.columns and pd.notna(row.get(en_field, "")):
                        # 兼容可能使用英文字段作为列名的情况
                        sponsor[en_field] = str(row.get(en_field, ""))
                
                # 验证必填字段
                required_fields = schema.get("required", [])
                missing_fields = [field for field in required_fields if field not in sponsor or not sponsor[field]]
                
                if not missing_fields:
                    # 使用 sessionName + sponsorName 作为唯一标识
                    key = f"{sponsor['sessionName']}_{sponsor['sponsorName']}"
                    if key in existing_sponsors:
                        # 如果存在，更新记录
                        existing_sponsors[key].update(sponsor)
                        print(f"更新已存在的赞助商: {sponsor['sponsorName']} for {sponsor['sessionName']}")
                    else:
                        # 如果不存在，添加新记录
                        existing_sponsors[key] = sponsor
                        print(f"添加新赞助商: {sponsor['sponsorName']} for {sponsor['sessionName']}")
                else:
                    print(f"错误: 跳过缺少必填字段的记录: {missing_fields}")
                    
        except Exception as e:
            print(f"处理文件 {excel_file} 时出错: {str(e)}")
    
    # 写入JSONL文件
    with open(output_file, "w", encoding="utf-8") as f:
        for sponsor in existing_sponsors.values():
            f.write(json.dumps(sponsor, ensure_ascii=False) + "\n")
    
    print(f"成功处理赞助商数据并保存到 {output_file}，共 {len(existing_sponsors)} 条记录")

if __name__ == "__main__":
    process_sponsor_data()

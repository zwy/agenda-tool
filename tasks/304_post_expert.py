import json
import pathlib

def process_output_expert():
    """根据 expert.jsonl 生成 experts.json 输出文件"""
    # 读取 expert.jsonl 文件
    input_file = pathlib.Path("data/expert.jsonl")
    if not input_file.exists():
        print(f"错误: 文件 {input_file} 不存在!")
        return

    # 读取 schema 文件
    schema_file = pathlib.Path("output/model/experts.json")
    if not schema_file.exists():
        print(f"错误: Schema文件 {schema_file} 不存在!")
        return
    
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
            # 获取所有字段列表
            all_fields = list(schema.get("items", {}).get("properties", {}).keys())
            # 获取必填字段列表
            required_fields = schema.get("items", {}).get("required", [])
    except Exception as e:
        print(f"读取Schema时出错: {str(e)}")
        return

    experts = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    expert = json.loads(line)
                    
                    # 为缺失的字段设置默认空字符串
                    for field in all_fields:
                        if field not in expert:
                            expert[field] = ""
                    
                    # 验证必填字段
                    missing_fields = [field for field in required_fields if not expert[field]]
                    if missing_fields:
                        print(
                            f"错误: 记录缺少必填字段值: {missing_fields}, 跳过该记录: {expert['expertName'] if expert['expertName'] else '未知专家'}")
                        continue
                        
                    experts.append(expert)
        print(f"已读取并验证{len(experts)}条专家数据")
    except Exception as e:
        print(f"读取数据时出错: {str(e)}")
        return
    
    # 确保输出目录存在
    output_dir = pathlib.Path("output/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "experts.json"
    
    # 将数据保存为 JSON 文件
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(experts, f, ensure_ascii=False, indent=2)
        print(f"已将专家数据保存到 {output_file}，共 {len(experts)} 条记录")
    except Exception as e:
        print(f"保存数据时出错: {str(e)}")

if __name__ == "__main__":
    process_output_expert()

import json
import pathlib

def process_output_report():
    """根据 report.jsonl 生成 reports.json 输出文件"""
    # 读取 report.jsonl 文件
    input_file = pathlib.Path("data/report.jsonl")
    if not input_file.exists():
        print(f"错误: 文件 {input_file} 不存在!")
        return

    # 读取 schema 文件
    schema_file = pathlib.Path("output/model/reports.json")
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
            # 获取字段定义
            properties = schema.get("items", {}).get("properties", {})
    except Exception as e:
        print(f"读取Schema时出错: {str(e)}")
        return

    reports = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    report = json.loads(line)
                    # 验证必填字段
                    missing_fields = [field for field in required_fields if field not in report or not report[field]]
                    if missing_fields:
                        print(f"错误: 记录缺少必填字段: {missing_fields}, 跳过该记录")
                        continue
                    
                    # 过滤和验证字段
                    filtered_report = {}
                    for field in all_fields:
                        # 如果字段在报告数据中存在，则添加到过滤后的报告中
                        if field in report:
                            # 验证枚举字段
                            if "enum" in properties.get(field, {}) and report[field]:
                                enum_values = properties[field]["enum"]
                                if report[field] not in enum_values:
                                    print(f"警告: 字段 {field} 的值 '{report[field]}' 不在允许的枚举值 {enum_values} 内")
                            
                            filtered_report[field] = report[field]
                        else:
                            # 如果在schema中定义但在数据中不存在，设置为空字符串
                            filtered_report[field] = ""
                    
                    reports.append(filtered_report)
        print(f"已读取并验证{len(reports)}条报告数据")
    except Exception as e:
        print(f"读取数据时出错: {str(e)}")
        return
    
    # 确保输出目录存在
    output_dir = pathlib.Path("output/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "reports.json"
    
    # 将数据保存为 JSON 文件
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(reports, f, ensure_ascii=False, indent=2)
        print(f"已将报告数据保存到 {output_file}，共 {len(reports)} 条记录")
    except Exception as e:
        print(f"保存数据时出错: {str(e)}")

if __name__ == "__main__":
    process_output_report()

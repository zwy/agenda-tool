import json
import pathlib

def process_output_bibao():
    """根据 bibao.jsonl 生成 bibaos.json 输出文件"""
    # 读取 bibao.jsonl 文件
    input_file = pathlib.Path("data/bibao.jsonl")
    if not input_file.exists():
        print(f"错误: 文件 {input_file} 不存在!")
        return

    # 读取 schema 文件
    schema_file = pathlib.Path("output/model/bibaos.json")
    if not schema_file.exists():
        print(f"错误: Schema文件 {schema_file} 不存在!")
        return
    
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
            # 获取必填字段列表
            required_fields = schema.get("items", {}).get("required", [])
    except Exception as e:
        print(f"读取Schema时出错: {str(e)}")
        return

    bibaos = []
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    bibao = json.loads(line)
                    # 验证必填字段
                    missing_fields = [field for field in required_fields if field not in bibao or not bibao[field]]
                    if missing_fields:
                        print(f"警告: 记录缺少必填字段: {missing_fields}, 跳过该记录")
                        continue
                    bibaos.append(bibao)
        print(f"已读取并验证{len(bibaos)}条壁报数据")
    except Exception as e:
        print(f"读取数据时出错: {str(e)}")
        return
    
    # 确保输出目录存在
    output_dir = pathlib.Path("output/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "bibaos.json"
    
    # 将数据保存为 JSON 文件
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(bibaos, f, ensure_ascii=False, indent=2)
        print(f"已将壁报数据保存到 {output_file}，共 {len(bibaos)} 条记录")
    except Exception as e:
        print(f"保存数据时出错: {str(e)}")

if __name__ == "__main__":
    process_output_bibao()

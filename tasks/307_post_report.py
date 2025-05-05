import json
import pathlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

def process_report_to_individual_files():
    """读取report.jsonl并为每条数据生成单独的JSON文件"""
    # 读取report.jsonl文件
    input_file = pathlib.Path("data/report.jsonl")
    if not input_file.exists():
        logger.error(f"错误: 文件 {input_file} 不存在!")
        return

    # 读取schema文件 - 修正路径
    schema_file = pathlib.Path("model/report.json")
    if not schema_file.exists():
        logger.error(f"错误: Schema文件 {schema_file} 不存在!")
        return
    
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
            # 获取所有字段列表 - 修正结构
            all_fields = list(schema.get("properties", {}).keys())
            # 获取必填字段列表 - 修正结构
            required_fields = schema.get("required", [])
            # 获取字段定义 - 修正结构
            properties = schema.get("properties", {})
    except Exception as e:
        logger.error(f"读取Schema时出错: {str(e)}")
        return

    # 确保输出目录存在
    output_dir = pathlib.Path("output/data/agenda")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 处理每条报告数据
    processed_count = 0
    agenda_codes = set()
    duplicate_codes = set()
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if not line.strip():
                    continue
                
                try:
                    report = json.loads(line)
                    
                    # 验证必填字段
                    missing_fields = [field for field in required_fields if field not in report or not report[field]]
                    if missing_fields:
                        logger.warning(f"第{line_num}行记录缺少必填字段: {missing_fields}, 跳过该记录")
                        continue
                    
                    # 检查 agendaCode
                    agenda_code = report.get("agendaCode")
                    if not agenda_code:
                        logger.warning(f"第{line_num}行记录缺少 agendaCode, 跳过该记录")
                        continue
                    
                    # 检查是否有重复的 agendaCode
                    if agenda_code in agenda_codes:
                        duplicate_codes.add(agenda_code)
                        logger.warning(f"发现重复的 agendaCode: {agenda_code}, 将覆盖之前的文件")
                    
                    agenda_codes.add(agenda_code)
                    
                    # 过滤和验证字段
                    filtered_report = {}
                    for field in all_fields:
                        # 如果字段在报告数据中存在，则添加到过滤后的报告中
                        if field in report:
                            # 验证枚举字段
                            if "enum" in properties.get(field, {}) and report[field]:
                                enum_values = properties[field]["enum"]
                                if report[field] not in enum_values:
                                    logger.warning(f"第{line_num}行记录字段 {field} 的值 '{report[field]}' 不在允许的枚举值 {enum_values} 内")
                            
                            filtered_report[field] = report[field]
                        else:
                            # 如果在schema中定义但在数据中不存在，设置为空字符串
                            filtered_report[field] = ""
                    
                    # 将数据保存为独立的JSON文件
                    output_file = output_dir / f"{agenda_code}.json"
                    with open(output_file, "w", encoding="utf-8") as out_f:
                        # 将过滤后的报告包装成列表
                        json.dump([filtered_report], out_f, ensure_ascii=False, indent=2)
                    
                    processed_count += 1
                
                except json.JSONDecodeError:
                    logger.error(f"第{line_num}行JSON解析错误, 跳过该行")
                except Exception as e:
                    logger.error(f"处理第{line_num}行时出错: {str(e)}")
        
        if duplicate_codes:
            logger.warning(f"发现{len(duplicate_codes)}个重复的agendaCode: {', '.join(duplicate_codes)}")
        
        logger.info(f"已处理{processed_count}条报告数据, 生成{len(agenda_codes)}个JSON文件")
    
    except Exception as e:
        logger.error(f"读取数据时出错: {str(e)}")
        return

if __name__ == "__main__":
    logger.info("开始处理报告数据...")
    process_report_to_individual_files()
    logger.info("报告数据处理完成")

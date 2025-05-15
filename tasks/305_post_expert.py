import json
import pathlib
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

def load_session_types():
    """从session.jsonl加载分会场类型信息"""
    session_file = pathlib.Path("data/session.jsonl")
    
    if not session_file.exists():
        logger.error(f"错误: 文件 {session_file} 不存在!")
        return {}
    
    session_types = {}
    try:
        with open(session_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    session = json.loads(line)
                    session_name = session.get("sessionName", "")
                    session_type = session.get("type", "")
                    
                    if session_name and session_type:
                        session_types[session_name] = session_type
        
        logger.info(f"已加载{len(session_types)}个分会场类型映射")
        return session_types
    except Exception as e:
        logger.error(f"读取分会场数据时出错: {str(e)}")
        return {}

def process_output_reporters():
    """根据 expert.jsonl 和 report.jsonl 生成 reporters.json 输出文件"""
    # 读取分会场类型数据
    session_types = load_session_types()
    if not session_types:
        logger.warning("警告: 未能加载分会场类型数据，sessionsType字段将为空")
    
    # 读取 expert.jsonl 文件
    expert_file = pathlib.Path("data/expert.jsonl")
    report_file = pathlib.Path("data/report.jsonl")
    
    if not expert_file.exists():
        logger.error(f"错误: 文件 {expert_file} 不存在!")
        return
    
    if not report_file.exists():
        logger.error(f"错误: 文件 {report_file} 不存在!")
        return

    # 读取 schema 文件
    schema_file = pathlib.Path("output/model/reporters.json")
    if not schema_file.exists():
        logger.error(f"错误: Schema文件 {schema_file} 不存在!")
        return
    
    try:
        with open(schema_file, "r", encoding="utf-8") as f:
            schema = json.load(f)
            # 获取所有字段列表
            all_fields = list(schema.get("items", {}).get("properties", {}).keys())
            # 获取必填字段列表
            required_fields = schema.get("items", {}).get("required", [])
    except Exception as e:
        logger.error(f"读取Schema时出错: {str(e)}")
        return
    
    # 从报告文件中提取所有报告人和PI的姓名以及会场信息
    reporter_identifiers = set()  # 存储 "分会场名称+专家姓名" 的组合
    try:
        with open(report_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    report = json.loads(line)
                    session_name = report.get("sessionName", "")
                    
                    if not session_name:
                        logger.warning(f"警告: 报告记录缺少分会场名称，跳过: {report}")
                        continue
                    
                    # 提取reporterName字段（可能有多个，用逗号分隔）
                    if "reporterName" in report and report["reporterName"]:
                        for name in report["reporterName"].split(","):
                            name = name.strip()
                            if name:
                                reporter_identifiers.add(f"{session_name}+{name}")
                    
                    # 提取piName字段（可能有多个，用逗号分隔）
                    if "piName" in report and report["piName"]:
                        for name in report["piName"].split(","):
                            name = name.strip()
                            if name:
                                reporter_identifiers.add(f"{session_name}+{name}")
        
        logger.info(f"已从报告数据中提取{len(reporter_identifiers)}个报告人/PI身份标识(分会场+姓名)")
    except Exception as e:
        logger.error(f"读取报告数据时出错: {str(e)}")
        return
    
    # 筛选出是报告人或PI的专家
    reporters = []
    try:
        with open(expert_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    expert = json.loads(line)
                    
                    # 检查该专家是否是报告人或PI（基于分会场+姓名的组合）
                    session_name = expert.get("sessionName", "")
                    expert_name = expert.get("expertName", "")
                    
                    if not session_name or not expert_name:
                        continue
                    
                    identifier = f"{session_name}+{expert_name}"
                    if identifier in reporter_identifiers:
                        # 只保留schema中定义的字段
                        filtered_expert = {}
                        for field in all_fields:
                            if field == "sessionsType" and session_name in session_types:
                                # 设置sessionsType字段
                                filtered_expert[field] = session_types[session_name]
                            elif field in expert:
                                filtered_expert[field] = expert[field]
                            else:
                                filtered_expert[field] = ""
                        
                        # 验证必填字段
                        missing_fields = [field for field in required_fields if not filtered_expert[field]]
                        if missing_fields:
                            logger.error(
                                f"错误: 记录缺少必填字段值: {missing_fields}, 跳过该记录: {expert['expertName'] if expert['expertName'] else '未知专家'}, 分会场: {session_name}")
                            continue
                            
                        reporters.append(filtered_expert)
        
        logger.info(f"已筛选并验证{len(reporters)}条报告人/PI数据")
    except Exception as e:
        logger.error(f"读取专家数据时出错: {str(e)}")
        return
    
    # 添加去重逻辑：根据expertName、title、secondTitle、rbaseUrl去重
    unique_reporters = []
    seen_experts = set()
    
    for expert in reporters:
        # 创建唯一标识：expert_name+title+secondTitle+rbaseUrl+sessionsType
        expert_unique_id = (
            expert.get("expertName", ""),
            expert.get("title", ""),
            expert.get("secondTitle", ""),
            expert.get("rbaseUrl", ""),
            expert.get("sessionsType", "")
        )
        
        # 如果这个唯一标识没有出现过，就添加到去重后的列表中
        if expert_unique_id not in seen_experts:
            seen_experts.add(expert_unique_id)
            unique_reporters.append(expert)
    
    # 输出去重信息
    removed_count = len(reporters) - len(unique_reporters)
    if removed_count > 0:
        logger.info(f"检测到{removed_count}条重复专家数据，已去重")
    
    # 确保输出目录存在
    output_dir = pathlib.Path("output/data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "reporters.json"
    
    # 将去重后的数据保存为 JSON 文件
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(unique_reporters, f, ensure_ascii=False, indent=2)
        logger.info(f"已将报告人/PI数据保存到 {output_file}，共 {len(unique_reporters)} 条记录")
    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")

if __name__ == "__main__":
    process_output_reporters()

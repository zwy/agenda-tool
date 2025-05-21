import os
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import logging
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')
logger = logging.getLogger(__name__)

load_dotenv()  # 加载环境变量


def process_report_data():
    """处理报告数据，从Excel读取并转换为JSONL格式"""
    # 加载JSON Schema
    schema_path = Path("model/report.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # 创建中文标题到英文字段名的映射
    title_to_field = {}
    for field, config in schema.get("properties", {}).items():
        title = config.get("title", "")
        if title:
            title_to_field[title] = field
    
    # 获取所有Excel文件
    input_dir = Path("input/report")
    input_dir.mkdir(exist_ok=True)  # 确保目录存在
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    
    # 读取现有的JSONL文件(如果存在)
    existing_reports = {}
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "report.jsonl"
    
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        report = json.loads(line)
                        # 使用agendaCode作为唯一标识
                        if "agendaCode" in report:
                            existing_reports[report["agendaCode"]] = report
            logger.info(f"已读取{len(existing_reports)}条现有报告数据")
        except Exception as e:
            logger.error(f"读取现有数据时出错: {str(e)}")
    
    # 从video.jsonl读取视频信息
    video_data = {}
    video_file = output_dir / "video.jsonl"
    if video_file.exists():
        try:
            with open(video_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        video = json.loads(line)
                        if "aliyunVid" in video:
                            video_data[video["aliyunVid"]] = video
            logger.info(f"已读取{len(video_data)}条视频数据")
        except Exception as e:
            logger.error(f"读取视频数据时出错: {str(e)}")
    
    # 读取专家数据，用于验证专家姓名
    experts_map = {}  # 用于存储 "分会场名称+专家姓名" -> 专家数据 的映射
    expert_file = output_dir / "expert.jsonl"
    if expert_file.exists():
        try:
            with open(expert_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        expert = json.loads(line)
                        if "sessionName" in expert and "expertName" in expert:
                            key = f"{expert['sessionName']}+{expert['expertName']}"
                            experts_map[key] = expert
            logger.info(f"已读取{len(experts_map)}条专家数据")
        except Exception as e:
            logger.error(f"读取专家数据时出错: {str(e)}")
    
    # 处理每个Excel文件
    all_reports = []
    for excel_file in excel_files:
        logger.info(f"处理文件: {excel_file}")
        try:
            df = pd.read_excel(excel_file)
            
            for _, row in df.iterrows():
                report = {}
                
                # 处理Excel中的中文列名并转为英文字段
                for cn_title, en_field in title_to_field.items():
                    if cn_title in df.columns and pd.notna(row.get(cn_title, "")):
                        report[en_field] = str(row.get(cn_title, ""))
                    elif en_field in df.columns and pd.notna(row.get(en_field, "")):
                        # 兼容可能使用英文字段作为列名的情况
                        report[en_field] = str(row.get(en_field, ""))
                
                # 验证必填字段
                required_fields = schema.get("required", [])
                missing_fields = [field for field in required_fields if field not in report or not report[field]]
                
                if missing_fields:
                    logger.error(f"错误: 跳过缺少必填字段的记录: {missing_fields}")
                    continue
                
                # 验证专家姓名是否存在于专家表中
                session_name = report.get("sessionName", "")
                
                # 验证reporterName字段中的姓名
                if "reporterName" in report and report["reporterName"]:
                    reporter_names = [name.strip() for name in report["reporterName"].split(",")]
                    valid_reporters = []
                    invalid_reporters = []
                    
                    for name in reporter_names:
                        key = f"{session_name}+{name}"
                        if key in experts_map:
                            valid_reporters.append(name)
                        else:
                            invalid_reporters.append(name)
                    
                    if invalid_reporters:
                        logger.error(
                            f"错误: 报告 '{report.get('agendaCode', '')}' 的报告人 {invalid_reporters} 不在专家表中")
                    
                    # 只保留有效的专家姓名
                    if valid_reporters:
                        report["reporterName"] = ", ".join(valid_reporters)
                    else:
                        logger.warning(f"警告: 报告 '{report.get('agendaCode', '')}' 没有有效的报告人")
                
                # 验证piName字段中的姓名
                if "piName" in report and report["piName"]:
                    pi_names = [name.strip() for name in report["piName"].split(",")]
                    valid_pis = []
                    invalid_pis = []
                    
                    for name in pi_names:
                        key = f"{session_name}+{name}"
                        if key in experts_map:
                            valid_pis.append(name)
                        else:
                            invalid_pis.append(name)
                    
                    if invalid_pis:
                        logger.error(
                            f"错误: 报告 '{report.get('agendaCode', '')}' 的团队PI {invalid_pis} 不在专家表中")
                    
                    # 只保留有效的专家姓名
                    if valid_pis:
                        report["piName"] = ", ".join(valid_pis)
                    else:
                        logger.warning(f"警告: 报告 '{report.get('agendaCode', '')}' 没有有效的团队PI")
                
                # 验证枚举类型
                enum_fields = {
                    "reportType": schema["properties"]["reportType"]["enum"],
                    "reportSource": schema["properties"]["reportSource"]["enum"],
                    "permission": schema["properties"]["permission"]["enum"]
                }
                
                for field, enum_values in enum_fields.items():
                    if field in report and report[field] not in enum_values:
                        logger.error(
                            f"错误: 字段 {field} 的值 '{report[field]}' 不在允许的范围 {enum_values} 内")
                        # 设置为空或默认值
                        if enum_values:
                            report[field] = enum_values[0]
                        else:
                            report[field] = ""
                
                # 验证并格式化时间字段
                time_fields = ["startTime", "endTime"]
                for field in time_fields:
                    if field in report and report[field]:
                        try:
                            time_value = pd.to_datetime(report[field])
                            report[field] = time_value.strftime("%Y-%m-%d %H:%M:%S")
                        except Exception as e:
                            logger.error(f"错误: 无法解析 {field} 的值 '{report[field]}': {str(e)}")
                            report[field] = ""
                
                # 处理视频相关数据
                if "aliyunVid" in report and report["aliyunVid"] in video_data:
                    video = video_data[report["aliyunVid"]]
                    report["duration"] = video.get("duration", "")
                    report["permission"] = video.get("permission", "")
                    report["cover"] = video.get("cover", "")
                
                # 检查是否已存在相同agendaCode的记录
                if report["agendaCode"] in existing_reports:
                    # 更新现有记录，保留旧的值如果新的没有提供
                    existing_report = existing_reports[report["agendaCode"]]
                    for k, v in existing_report.items():
                        if k not in report or not report[k]:
                            report[k] = v
                    existing_reports[report["agendaCode"]] = report
                    logger.info(f"更新已存在的报告: {report['agendaCode']} ({report.get('reportTitle', '')})")
                else:
                    # 添加新记录
                    existing_reports[report["agendaCode"]] = report
                    logger.info(f"添加新报告: {report['agendaCode']} ({report.get('reportTitle', '')})")
                
                all_reports.append(report)
                    
        except Exception as e:
            logger.error(f"处理文件 {excel_file} 时出错: {str(e)}")
    
    # 写入JSONL文件
    with open(output_file, "w", encoding="utf-8") as f:
        for report in existing_reports.values():
            f.write(json.dumps(report, ensure_ascii=False) + "\n")
    
    logger.info(f"成功处理报告数据并保存到 {output_file}，共 {len(existing_reports)} 条记录")
    
    # 更新分会场统计数据，这里不做更新
    # update_session_statistics()

def update_session_statistics():
    """更新分会场的报告统计数据"""
    # 读取所有报告数据
    reports_file = Path("data/report.jsonl")
    reports = []
    if reports_file.exists():
        with open(reports_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    reports.append(json.loads(line))
    
    # 统计各分会场的报告类型数量
    session_stats = {}
    for report in reports:
        session_name = report.get("sessionName", "")
        report_source = report.get("reportSource", "")
        
        if not session_name:
            continue
            
        if session_name not in session_stats:
            session_stats[session_name] = {"teyao": 0, "tougao": 0, "haiwai": 0}
            
        if report_source == "特邀":
            session_stats[session_name]["teyao"] += 1
        elif report_source == "投稿":
            session_stats[session_name]["tougao"] += 1
        elif report_source == "海外":
            session_stats[session_name]["haiwai"] += 1
    
    # 更新分会场数据
    sessions_file = Path("data/session.jsonl")
    if not sessions_file.exists():
        return
        
    sessions = []
    with open(sessions_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                sessions.append(json.loads(line))
    
    # 更新统计数据
    for session in sessions:
        session_name = session.get("sessionName", "")
        if session_name in session_stats:
            session["teyao"] = session_stats[session_name]["teyao"]
            session["tougao"] = session_stats[session_name]["tougao"]
            session["haiwai"] = session_stats[session_name]["haiwai"]
    
    # 写回文件
    with open(sessions_file, "w", encoding="utf-8") as f:
        for session in sessions:
            f.write(json.dumps(session, ensure_ascii=False) + "\n")
    
    logger.info(f"已更新分会场报告统计数据")

if __name__ == "__main__":
    process_report_data()

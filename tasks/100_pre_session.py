import os
import glob
import pandas as pd
import json
import base64
from datetime import datetime
import pathlib
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

meeting_id = os.getenv('MEETING_ID', '')

def process_session_data():
    """处理分会场数据，从Excel读取并转换为JSONL格式"""
    # 加载JSON Schema
    schema_path = pathlib.Path("model/session.json")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    
    # 创建中文标题到英文字段名的映射
    title_to_field = {}
    for field, config in schema.get("properties", {}).items():
        title = config.get("title", "")
        if title:
            title_to_field[title] = field
    
    # 获取所有Excel文件
    input_dir = pathlib.Path("input/session")
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    
    # 读取现有的JSONL文件(如果存在)
    existing_sessions = {}
    output_dir = pathlib.Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "session.jsonl"
    
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        session = json.loads(line)
                        if "sessionCode" in session:
                            existing_sessions[session["sessionCode"]] = session
            print(f"已读取{len(existing_sessions)}条现有分会场数据")
        except Exception as e:
            print(f"读取现有数据时出错: {str(e)}")
    
    # 处理每个Excel文件
    for excel_file in excel_files:
        print(f"处理文件: {excel_file}")
        try:
            df = pd.read_excel(excel_file)
            
            for _, row in df.iterrows():
                session = {}
                
                # 处理Excel中的中文列名并转为英文字段
                for cn_title, en_field in title_to_field.items():
                    if cn_title in df.columns and pd.notna(row.get(cn_title, "")):
                        session[en_field] = str(row.get(cn_title, ""))
                    elif en_field in df.columns and pd.notna(row.get(en_field, "")):
                        # 兼容可能使用英文字段作为列名的情况
                        session[en_field] = str(row.get(en_field, ""))
                
                # 处理时间字段
                start_time = None
                if "startTime" in session:
                    start_time = session["startTime"]
                elif "开始时间" in df.columns:
                    start_time = row.get("开始时间", None)
                
                end_time = None
                if "endTime" in session:
                    end_time = session["endTime"]
                elif "结束时间" in df.columns:
                    end_time = row.get("结束时间", None)
                
                # 转换和格式化时间
                if pd.notna(start_time):
                    if not isinstance(start_time, datetime):
                        try:
                            start_time = pd.to_datetime(start_time)
                        except Exception:
                            print(f"错误：无法解析开始时间: {start_time}")
                            start_time = None
                    
                    if isinstance(start_time, datetime):
                        session["startTime"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        # 生成日期相关字段
                        session["day"] = start_time.strftime("%m月%d日")
                        
                        # 生成星期
                        weekday_map = {
                            0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四",
                            4: "星期五", 5: "星期六", 6: "星期日"
                        }
                        session["week"] = weekday_map.get(start_time.weekday(), "星期一")
                        
                        # 生成时间段
                        hour = start_time.hour
                        if 5 <= hour < 12:
                            session["eeee"] = "上午"
                        elif 12 <= hour < 14:
                            session["eeee"] = "中午"
                        else:
                            session["eeee"] = "下午"
                
                if pd.notna(end_time):
                    if not isinstance(end_time, datetime):
                        try:
                            end_time = pd.to_datetime(end_time)
                        except Exception:
                            print(f"错误：无法解析结束时间: {end_time}")
                            end_time = None
                    
                    if isinstance(end_time, datetime):
                        session["endTime"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
                
                # 生成sessionCode
                if "sessionName" in session and session["sessionName"]:
                    code_str = session["sessionName"] + meeting_id
                    session["sessionCode"] = base64.b64encode(code_str.encode('utf-8')).decode('utf-8')

                # 初始化报告数量字段
                session["teyao"] = 0
                session["tougao"] = 0
                session["haiwai"] = 0
                
                # 验证必填字段
                required_fields = schema.get("required", [])
                missing_fields = [field for field in required_fields if field not in session or not session[field]]
                
                if not missing_fields:
                    # 检查是否已存在相同sessionCode的记录
                    if session["sessionCode"] in existing_sessions:
                        # 如果存在，保留原有的报告数量数据
                        existing_session = existing_sessions[session["sessionCode"]]
                        session["teyao"] = existing_session.get("teyao", 0)
                        session["tougao"] = existing_session.get("tougao", 0)
                        session["haiwai"] = existing_session.get("haiwai", 0)
                        existing_sessions[session["sessionCode"]] = session
                        print(f"更新已存在的分会场: {session['sessionName']}")
                    else:
                        # 如果不存在，添加新记录
                        existing_sessions[session["sessionCode"]] = session
                        print(f"添加新分会场: {session['sessionName']}")
                else:
                    print(f"警告: 跳过缺少必填字段的记录: {missing_fields}")
                    
        except Exception as e:
            print(f"处理文件 {excel_file} 时出错: {str(e)}")
    
    # 写入JSONL文件
    with open(output_file, "w", encoding="utf-8") as f:
        for session in existing_sessions.values():
            f.write(json.dumps(session, ensure_ascii=False) + "\n")
    
    print(f"成功处理分会场数据并保存到 {output_file}，共 {len(existing_sessions)} 条记录")

if __name__ == "__main__":
    process_session_data()

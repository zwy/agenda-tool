import os
import pandas as pd
import json
import base64
from datetime import datetime
import pathlib
from dotenv import load_dotenv
import logging
import traceback

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file
meeting_id = os.getenv('MEETING_ID', '')

def load_schema():
    """加载并返回JSON Schema配置"""
    try:
        schema_path = pathlib.Path("model/session.json")
        with open(schema_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载Schema失败: {str(e)}")
        return {}

def create_field_mapping(schema):
    """创建中文标题到英文字段名的映射"""
    title_to_field = {}
    for field, config in schema.get("properties", {}).items():
        title = config.get("title", "")
        if title:
            title_to_field[title] = field
    return title_to_field

def load_existing_sessions(output_file):
    """加载现有的会话数据"""
    existing_sessions = {}
    if output_file.exists():
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        session = json.loads(line)
                        if "sessionCode" in session:
                            existing_sessions[session["sessionCode"]] = session
            logger.info(f"已读取{len(existing_sessions)}条现有分会场数据")
        except Exception as e:
            logger.error(f"读取现有数据时出错: {str(e)}")
            logger.debug(traceback.format_exc())
    return existing_sessions

def parse_datetime(time_value, time_type="开始时间"):
    """解析并转换时间值为datetime对象"""
    if pd.isna(time_value):
        return None
        
    if not isinstance(time_value, datetime):
        try:
            return pd.to_datetime(time_value)
        except Exception as e:
            logger.error(f"错误：无法解析{time_type}: {time_value}, 错误: {str(e)}")
            return None
    return time_value

def determine_time_period(start_time, end_time):
    """根据开始和结束时间确定时间段（上午、中午、下午）"""
    if not isinstance(start_time, datetime):
        return ""
        
    start_hour = start_time.hour
    # 如果结束时间无效，使用默认值
    end_hour = end_time.hour if isinstance(end_time, datetime) else 23
    
    if 5 <= start_hour < 12 and end_hour < 12:
        return "上午"
    elif 12 <= start_hour < 14 and end_hour < 14:
        return "中午"
    elif 12 <= start_hour and end_hour < 24:
        return "下午"
    else:
        # 处理不符合以上规则的情况，返回空或默认值
        return "其他"

def generate_session_code(session_name):
    """生成会话代码"""
    if not session_name:
        return ""
    code_str = session_name + meeting_id
    return base64.urlsafe_b64encode(code_str.encode('utf-8')).decode('utf-8').rstrip('=')

def process_excel_row(row, df, title_to_field, schema):
    """处理Excel的一行数据，返回处理后的会话数据"""
    session = {}
    
    # 处理Excel中的中文列名并转为英文字段
    for cn_title, en_field in title_to_field.items():
        if cn_title in df.columns and pd.notna(row.get(cn_title, "")):
            session[en_field] = str(row.get(cn_title, ""))
        elif en_field in df.columns and pd.notna(row.get(en_field, "")):
            session[en_field] = str(row.get(en_field, ""))
    
    # 处理时间字段
    start_time_val = session.get("startTime") if "startTime" in session else row.get("开始时间", None)
    end_time_val = session.get("endTime") if "endTime" in session else row.get("结束时间", None)
    
    start_time = parse_datetime(start_time_val, "开始时间")
    end_time = parse_datetime(end_time_val, "结束时间")
    
    # 处理时间相关字段
    if isinstance(start_time, datetime):
        session["startTime"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
        session["day"] = start_time.strftime("%m月%d日")
        
        # 生成星期
        weekday_map = {
            0: "星期一", 1: "星期二", 2: "星期三", 3: "星期四",
            4: "星期五", 5: "星期六", 6: "星期日"
        }
        session["week"] = weekday_map.get(start_time.weekday(), "星期一")
        
        # 生成时间段
        session["eeee"] = determine_time_period(start_time, end_time)
    
    if isinstance(end_time, datetime):
        session["endTime"] = end_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 生成sessionCode
    if "sessionName" in session and session["sessionName"]:
        session["sessionCode"] = generate_session_code(session["sessionName"])

    # 初始化报告数量字段
    session.setdefault("teyao", 0)
    session.setdefault("tougao", 0)
    session.setdefault("haiwai", 0)
    
    return session

def validate_session(session, schema):
    """验证会话数据是否满足必要条件"""
    required_fields = schema.get("required", [])
    missing_fields = [field for field in required_fields if field not in session or not session[field]]
    return not missing_fields, missing_fields

def process_session_data():
    """处理分会场数据，从Excel读取并转换为JSONL格式"""
    # 加载JSON Schema
    schema = load_schema()
    if not schema:
        return
    
    # 创建中文标题到英文字段名的映射
    title_to_field = create_field_mapping(schema)
    
    # 获取所有Excel文件
    input_dir = pathlib.Path("input/session")
    excel_files = list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.xls"))
    
    if not excel_files:
        logger.warning("未找到任何Excel文件")
        return
    
    # 读取现有的JSONL文件(如果存在)
    output_dir = pathlib.Path("data")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "session.jsonl"
    
    existing_sessions = load_existing_sessions(output_file)
    
    # 处理每个Excel文件
    for excel_file in excel_files:
        logger.info(f"处理文件: {excel_file}")
        try:
            df = pd.read_excel(excel_file)
            
            for _, row in df.iterrows():
                try:
                    session = process_excel_row(row, df, title_to_field, schema)
                    
                    # 验证必填字段
                    is_valid, missing_fields = validate_session(session, schema)
                    
                    if is_valid and "sessionCode" in session:
                        # 检查是否已存在相同sessionCode的记录
                        if session["sessionCode"] in existing_sessions:
                            # 如果存在，保留原有的报告数量数据
                            existing_session = existing_sessions[session["sessionCode"]]
                            session["teyao"] = existing_session.get("teyao", 0)
                            session["tougao"] = existing_session.get("tougao", 0)
                            session["haiwai"] = existing_session.get("haiwai", 0)
                            existing_sessions[session["sessionCode"]] = session
                            logger.info(f"更新已存在的分会场: {session.get('sessionName', session['sessionCode'])}")
                        else:
                            # 如果不存在，添加新记录
                            existing_sessions[session["sessionCode"]] = session
                            logger.info(f"添加新分会场: {session.get('sessionName', session['sessionCode'])}")
                    else:
                        logger.error(f"错误: 跳过缺少必填字段的记录: {missing_fields}")
                except Exception as e:
                    logger.error(f"处理行数据时出错: {str(e)}")
                    logger.debug(traceback.format_exc())
                    
        except Exception as e:
            logger.error(f"处理文件 {excel_file} 时出错: {str(e)}")
            logger.debug(traceback.format_exc())
    
    # 写入JSONL文件
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            for session in existing_sessions.values():
                f.write(json.dumps(session, ensure_ascii=False) + "\n")
        
        logger.info(f"成功处理分会场数据并保存到 {output_file}，共 {len(existing_sessions)} 条记录")
    except Exception as e:
        logger.error(f"保存数据时出错: {str(e)}")
        logger.debug(traceback.format_exc())

if __name__ == "__main__":
    process_session_data()

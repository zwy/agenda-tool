from util import process_excel, save_to_excel
import sys
import os
import traceback
import datetime
import re

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def transform_data(data_list, session_data=None, report_detail_data=None):
    """
    根据规则转换数据
    
    Args:
        data_list: 原始数据列表
        session_data: 分会场数据，用于补充日期信息
        report_detail_data: 报告详细信息，用于补充报告的更多信息
    
    Returns:
        转换后的数据列表
    """
    transformed_data = []
    
    # 基于报告编码存储唯一数据
    unique_entries = {}
    
    # 准备分会场日期映射（如果有第二个Excel）
    session_date_map = {}
    if session_data:
        for item in session_data:
            session_name_field = next((field for field in item.keys() if "分会场名称" in field or field == "sessionName"), None)
            start_time_field = next((field for field in item.keys() if field == "开始时间"), None)
            
            if session_name_field and start_time_field and item.get(session_name_field) and item.get(start_time_field):
                session_name = item[session_name_field]
                start_time = item[start_time_field]
                
                # 尝试提取日期部分
                date_match = re.match(r'(\d{4}-\d{2}-\d{2})', start_time)
                if date_match:
                    session_date_map[session_name] = date_match.group(1)
    
    # 准备报告详情映射（如果有第三个Excel）
    report_detail_map = {}
    if report_detail_data:
        for item in report_detail_data:
            title_field = next((field for field in item.keys() if field == "报告题目"), None)
            
            if title_field and item.get(title_field):
                report_title = item[title_field]
                detail = {}
                
                # 提取可能的详情字段
                en_title_field = next((field for field in item.keys() if field == "报告英文题目"), None)
                summary_field = next((field for field in item.keys() if field == "简介"), None)
                en_summary_field = next((field for field in item.keys() if field == "英文简介"), None)
                
                if en_title_field and item.get(en_title_field):
                    detail["报告英文题目"] = item[en_title_field]
                if summary_field and item.get(summary_field):
                    detail["简介"] = item[summary_field]
                if en_summary_field and item.get(en_summary_field):
                    detail["英文简介"] = item[en_summary_field]
                
                if detail:
                    report_detail_map[report_title] = detail
    
    for item in data_list:
        # 找到对应的字段
        session_field = next((field for field in item.keys() if "分会场名称" in field), None)
        time_field = next((field for field in item.keys() if field == "时间段"), None)
        code_field = next((field for field in item.keys() if "报告编码" in field), None)
        reporter_field = next((field for field in item.keys() if field == "报告人"), None)
        report_type_field = next((field for field in item.keys() if "报告类型" in field), None)
        pi_field = next((field for field in item.keys() if field == "团队PI"), None)
        title_field = next((field for field in item.keys() if field in ["题目/环节", "题目", "环节"]), None)
        
        # 如果缺少必要字段，跳过该条记录
        if not code_field or not session_field:
            continue
        
        # 提取报告编码并处理可能的浮点数字符串问题
        report_code = item[code_field]
        if not report_code:  # 如果报告编码为空，跳过
            continue
            
        # 处理数字编码可能被转为浮点数的情况（例如：123 -> "123.0"）
        try:
            # 尝试转换为浮点数
            float_value = float(report_code)
            # 检查是否为整数值（没有小数部分）
            if float_value.is_integer():
                # 转为整数字符串
                report_code = str(int(float_value))
        except (ValueError, TypeError):
            # 如果转换失败，保持原样
            pass
        
        # 获取分会场名称
        session_name = item.get(session_field, "")
        
        # 获取报告题目
        report_title = item.get(title_field, "") if title_field else ""
        
        # 创建新记录或更新现有记录
        entry = {
            "分会场名称": session_name,
            "报告编码": report_code,
            "报告类型": item.get(report_type_field, "") if report_type_field else "",
            "报告题目": report_title
        }
        
        # 处理时间字段
        start_time = ""
        end_time = ""
        if time_field and item.get(time_field):
            time_str = item[time_field]
            # 统一补全小时为两位
            def pad_hour(t):
                m = re.match(r'(\d{1,2}):(\d{2})', t)
                if m:
                    return f"{int(m.group(1)):02d}:{m.group(2)}"
                return t
            # 匹配时间范围
            time_match = re.match(r'(\d{1,2}:\d{2})-(\d{1,2}:\d{2})', time_str)
            if time_match:
                start_time_raw = time_match.group(1)
                end_time_raw = time_match.group(2)
                start_time = pad_hour(start_time_raw) + ":00"
                end_time = pad_hour(end_time_raw) + ":00"
                
                # 如果有分会场日期信息，补充到时间中
                if session_name in session_date_map:
                    date_str = session_date_map[session_name]
                    start_time = f"{date_str} {start_time}"
                    end_time = f"{date_str} {end_time}"
                
                entry["开始时间"] = start_time
                entry["结束时间"] = end_time
        
        # 提取报告人姓名
        reporter_name = item.get(reporter_field, "") if reporter_field else ""
        
        # 提取团队PI姓名
        pi_name = item.get(pi_field, "") if pi_field else ""
        
        # 补充报告详情（如果有）
        if report_title in report_detail_map:
            for key, value in report_detail_map[report_title].items():
                entry[key] = value
        
        # 检查是否已存在该报告编码的记录
        if report_code in unique_entries:
            # 更新现有记录
            existing_entry = unique_entries[report_code]
            
            # 合并报告人姓名
            if reporter_name and reporter_name not in (existing_entry.get("报告人姓名", "").split(",") if existing_entry.get("报告人姓名") else []):
                if existing_entry.get("报告人姓名"):
                    existing_entry["报告人姓名"] += f",{reporter_name}"
                else:
                    existing_entry["报告人姓名"] = reporter_name
            
            # 合并团队PI姓名
            if pi_name and pi_name not in (existing_entry.get("团队PI姓名", "").split(",") if existing_entry.get("团队PI姓名") else []):
                if existing_entry.get("团队PI姓名"):
                    existing_entry["团队PI姓名"] += f",{pi_name}"
                else:
                    existing_entry["团队PI姓名"] = pi_name
                    
            # 补充可能缺失的报告详情
            for key, value in entry.items():
                if key not in existing_entry or not existing_entry[key]:
                    existing_entry[key] = value
        else:
            # 创建新记录
            entry["报告人姓名"] = reporter_name
            entry["团队PI姓名"] = pi_name
            unique_entries[report_code] = entry
    
    # 将字典转换为列表
    transformed_data = list(unique_entries.values())
    
    return transformed_data

def main():
    """
    主函数，接收Excel文件路径作为参数，处理数据并保存到新文件
    可接收1-3个参数：
    - 第一个参数：要处理的Excel文件路径（必填）
    - 第二个参数：分会场数据Excel文件路径（选填）
    - 第三个参数：报告详情Excel文件路径（选填）
    """
    if len(sys.argv) < 2:
        print("用法: python op-report.py <Excel文件绝对路径> [分会场数据Excel] [报告详情Excel]")
        sys.exit(1)
    
    # 获取主Excel文件路径（必填）
    excel_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.isfile(excel_path):
        print(f"错误: 文件 '{excel_path}' 不存在")
        sys.exit(1)
    
    # 获取分会场数据Excel文件路径（如果提供）
    session_excel_path = None
    if len(sys.argv) > 2 and sys.argv[2]:
        session_excel_path = sys.argv[2]
        if not os.path.isfile(session_excel_path):
            print(f"警告: 分会场数据文件 '{session_excel_path}' 不存在，将不补充分会场日期信息")
            session_excel_path = None
    
    # 获取报告详情Excel文件路径（如果提供）
    report_detail_excel_path = None
    if len(sys.argv) > 3 and sys.argv[3]:
        report_detail_excel_path = sys.argv[3]
        if not os.path.isfile(report_detail_excel_path):
            print(f"警告: 报告详情文件 '{report_detail_excel_path}' 不存在，将不补充报告详情信息")
            report_detail_excel_path = None
    
    # 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 输出文件路径 - 保存在输入Excel文件的同级目录下
    output_dir = os.path.dirname(excel_path)
    output_excel = os.path.join(output_dir, f"op-report-{timestamp}.xlsx")

    print(f"输入Excel文件: {excel_path}")
    if session_excel_path:
        print(f"分会场数据Excel: {session_excel_path}")
    if report_detail_excel_path:
        print(f"报告详情Excel: {report_detail_excel_path}")
    print(f"输出Excel文件: {output_excel}")
    
    # 处理Excel文件
    try:
        # 获取原始数据
        data = process_excel(excel_path)
        
        # 获取分会场数据（如果有）
        session_data = None
        if session_excel_path:
            session_data = process_excel(session_excel_path)
            print(f"已读取分会场数据，共 {len(session_data)} 条记录")
        
        # 获取报告详情数据（如果有）
        report_detail_data = None
        if report_detail_excel_path:
            report_detail_data = process_excel(report_detail_excel_path)
            print(f"已读取报告详情数据，共 {len(report_detail_data)} 条记录")
        
        print(f"已读取原始数据，共 {len(data)} 条记录")
        # 转换数据
        transformed_data = transform_data(data, session_data, report_detail_data)
        
        # 保存转换后的数据
        save_to_excel(transformed_data, output_excel)
        
        print(f"成功处理文件，共 {len(transformed_data)} 条记录")
        
    except Exception as e:
        print(f"处理Excel文件时出错: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

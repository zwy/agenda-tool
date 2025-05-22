from util import process_excel, save_to_excel
import sys
import os
import traceback
import pandas as pd
import datetime

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def transform_data(data_list, expert_url_data=None):
    """
    根据规则转换数据
    
    Args:
        data_list: 原始数据列表
        expert_url_data: 专家URL数据列表，用于补充专家链接信息
    
    Returns:
        转换后的数据列表
    """
    transformed_data = []
    
    # 根据分会场+专家姓名来存储唯一数据
    unique_entries = {}
    
    # 准备专家链接映射（如果有）
    expert_url_map = {}
    if expert_url_data:
        for item in expert_url_data:
            name_field = next((field for field in item.keys() if field == "中文姓名"), None)
            url_field = next((field for field in item.keys() if field == "R·base URL"), None)
            
            if name_field and url_field and item.get(name_field) and item.get(url_field):
                expert_name = item[name_field]
                expert_url = item[url_field]
                expert_url_map[expert_name] = expert_url
    
    for item in data_list:
        # 检查是否包含必要的字段
        venue_field = next((field for field in item.keys() if "分会场名称" in field), None)
        
        # 如果没有找到分会场字段，跳过该条记录
        if not venue_field:
            continue
        
        # 提取分会场名称
        venue_name = item[venue_field]
        
        # 从角色字段获取角色信息
        role_field = next((field for field in item.keys() if field == "角色（IT）" or field == "角色"), None)
        chair_type = ""
        host_type = ""
        
        if role_field and item[role_field]:
            role = item[role_field]
            if "主席" in role:
                chair_type = role
            elif role == "主持人":
                host_type = role
        
        # 处理数据 - 现在需要处理可能同时存在的两种情况
        
        # 情况1: 处理报告人信息
        if "报告人" in item and item["报告人"]:
            expert_name = item["报告人"]
            first_title = item.get("机构", "")
            
            # 构建唯一键
            unique_key = f"{venue_name}_{expert_name}"
            
            # 获取专家链接（如果有）
            expert_url = expert_url_map.get(expert_name, "")
            
            if unique_key in unique_entries:
                # 更新现有记录
                existing_entry = unique_entries[unique_key]
                
                if not existing_entry["第一Title"] and first_title:
                    existing_entry["第一Title"] = first_title
                    
                if not existing_entry["主席类型"] and chair_type:
                    existing_entry["主席类型"] = chair_type
                    
                if not existing_entry["主持人类型"] and host_type:
                    existing_entry["主持人类型"] = host_type
                
                # 更新专家链接（如果之前没有但现在有）
                if not existing_entry.get("Rbase页面URL") and expert_url:
                    existing_entry["Rbase页面URL"] = expert_url
            else:
                # 创建新记录
                new_entry = {
                    "分会场名称": venue_name,
                    "专家姓名": expert_name,
                    "第一Title": first_title,
                    "主席类型": chair_type,
                    "主持人类型": host_type,
                    "Rbase页面URL": expert_url
                }
                unique_entries[unique_key] = new_entry
        
        # 情况2: 处理团队PI信息，团队PI这个没有角色
        if "团队PI" in item and item["团队PI"]:
            expert_name = item["团队PI"]
            first_title = item.get("团队PI机构", "")
            
            # 构建唯一键
            unique_key = f"{venue_name}_{expert_name}"
            
            # 获取专家链接（如果有）
            expert_url = expert_url_map.get(expert_name, "")
            
            if unique_key in unique_entries:
                # 更新现有记录
                existing_entry = unique_entries[unique_key]
                
                if not existing_entry["第一Title"] and first_title:
                    existing_entry["第一Title"] = first_title
                
                # 更新专家链接（如果之前没有但现在有）
                if not existing_entry.get("Rbase页面URL") and expert_url:
                    existing_entry["Rbase页面URL"] = expert_url
            else:
                # 创建新记录
                new_entry = {
                    "分会场名称": venue_name,
                    "专家姓名": expert_name,
                    "第一Title": first_title,
                    "主席类型": "",
                    "主持人类型": "",
                    "Rbase页面URL": expert_url
                }
                unique_entries[unique_key] = new_entry
    
    # 将字典转换为列表
    transformed_data = list(unique_entries.values())
    
    return transformed_data

def main():
    """
    主函数，接收Excel文件路径作为参数，处理数据并保存到新文件
    可接收1-2个参数：
    - 第一个参数：要处理的Excel文件路径（必填）
    - 第二个参数：专家链接Excel文件路径（选填）
    """
    if len(sys.argv) < 2:
        print("用法: python op-expert.py <Excel文件绝对路径> [专家链接Excel文件]")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.isfile(excel_path):
        print(f"错误: 文件 '{excel_path}' 不存在")
        sys.exit(1)
    
    # 获取专家链接Excel文件路径（如果提供）
    expert_url_excel_path = None
    if len(sys.argv) > 2 and sys.argv[2]:
        expert_url_excel_path = sys.argv[2]
        if not os.path.isfile(expert_url_excel_path):
            print(f"警告: 专家链接文件 '{expert_url_excel_path}' 不存在，将不补充专家链接信息")
            expert_url_excel_path = None
    
    # 获取当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 输出文件路径 - 保存在输入Excel文件的同级目录下
    output_dir = os.path.dirname(excel_path)
    output_excel = os.path.join(output_dir, f"op-expert-{timestamp}.xlsx")

    print(f"输入Excel文件: {excel_path}")
    if expert_url_excel_path:
        print(f"专家链接Excel: {expert_url_excel_path}")
    print(f"输出Excel文件: {output_excel}")
    
    # 处理Excel文件
    try:
        # 获取原始数据
        data = process_excel(excel_path)
        
        # 获取专家链接数据（如果有）
        expert_url_data = None
        if expert_url_excel_path:
            expert_url_data = process_excel(expert_url_excel_path)
            print(f"已读取专家链接数据，共 {len(expert_url_data)} 条记录")
        
        # 转换数据
        transformed_data = transform_data(data, expert_url_data)
        
        # 保存转换后的数据
        save_to_excel(transformed_data, output_excel)
        
        print(f"成功处理文件，共 {len(transformed_data)} 条记录")
        
    except Exception as e:
        print(f"处理Excel文件时出错: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

from util import process_excel, save_to_jsonl, filter_fields, rename_fields
import sys
import os
import traceback

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    主函数，接收Excel文件路径和可选的输出文件路径作为参数
    """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("用法: python xueshu.py <Excel文件绝对路径> [输出文件路径]")
        print("注意: 如果不指定输出文件路径，默认保存为 data/demo_xueshu.jsonl")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.isfile(excel_path):
        print(f"错误: 文件 '{excel_path}' 不存在")
        sys.exit(1)
    
    # 获取输出文件路径（如果提供）或使用默认值
    output_file = sys.argv[2] if len(sys.argv) == 3 else "data/demo_xueshu.jsonl"
    
    # 处理Excel文件
    try:
        # 获取原始数据
        data = process_excel(excel_path)


        # 重命名字段
        field_map = {
            "中文题目": "报告题目",
            "英文题目": "报告英文题目",
            "中文摘要（500字内）": "简介",
            "英文摘要（300单词内）": "英文简介",
        }
        renamed_data = rename_fields(data, field_map)

        # 只保留特定字段，field_map中的键
        fields_to_keep = list(field_map.values())
        # 过滤数据，只保留指定字段
        filtered_data = filter_fields(renamed_data, fields_to_keep)

        # 保存过滤后的数据
        save_to_jsonl(filtered_data, output_file)
    except Exception as e:
        print(f"处理Excel文件时出错: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

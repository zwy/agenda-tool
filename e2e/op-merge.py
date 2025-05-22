from util import process_excel, filter_fields, save_to_excel
import sys
import os
import traceback
import glob

# 添加当前目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """
    主函数，接收文件夹路径作为参数，处理该文件夹下所有Excel文件，并合并特定字段
    """
    if len(sys.argv) != 2:
        print("用法: python op-merge.py <Excel文件夹路径>")
        print("注意: 会处理文件夹中所有Excel文件并合并结果")
        sys.exit(1)
    
    folder_path = sys.argv[1]
    
    # 检查文件夹是否存在
    if not os.path.isdir(folder_path):
        print(f"错误: 目录 '{folder_path}' 不存在")
        sys.exit(1)
    
    # 输出文件路径
    output_excel = os.path.join(folder_path, "combined_e2e_op.xlsx")

    print(f"输出Excel文件路径: {output_excel}")
    
    # 查找文件夹中所有的Excel文件
    excel_files = glob.glob(os.path.join(folder_path, "*.xlsx"))
    
    if not excel_files:
        print(f"错误: 在 '{folder_path}' 中未找到任何Excel文件")
        sys.exit(1)
    
    print(f"找到 {len(excel_files)} 个Excel文件需要处理")
    
    # 存储所有处理后的数据
    all_data = []
    
    # 需要保留的字段
    fields_to_keep = [
        "分会场名称（IT)",
        "时间段",
        "报告编码（IT）",
        "报告人",
        "报告类型（IT）",
        "角色（IT）",
        "机构",
        "题目/环节",
        "团队PI",
        "团队PI机构"
    ]
    # 必填字段
    required_fields = ["分会场名称（IT)"]

    # 处理每个Excel文件
    try:
        for excel_path in excel_files:
            print(f"处理文件: {os.path.basename(excel_path)}")
            data = process_excel(excel_path)
            filtered_data = filter_fields(data, fields_to_keep)
            # 必填字段检查
            valid_data = []
            for item in filtered_data:
                valid = True
                for field in required_fields:
                    if field not in item or not item[field] or str(item[field]).strip() == "":
                        print(f"警告: '{field}' 字段不能为空，跳过该条记录")
                        valid = False
                        break
                if valid:
                    valid_data.append(item)
            all_data.extend(valid_data)
        # 去重 all_data
        all_data = [dict(t) for t in {tuple(d.items()) for d in all_data}]
        save_to_excel(all_data, output_excel)
        print(f"成功处理所有文件，共 {len(all_data)} 条记录")
    except Exception as e:
        print(f"处理Excel文件时出错: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

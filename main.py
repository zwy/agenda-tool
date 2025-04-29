import subprocess
import os
import sys
import time
import platform
import logging
from pathlib import Path
import re

# 设置日志
def setup_logging():
    log_dir = Path(__file__).parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # 设置日志文件名，包含时间戳
    timestamp = time.strftime('%Y%m%d_%H%M%S')
    log_file = log_dir / f'execution_{timestamp}.log'
    
    # 配置日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return log_file

# 检查日志中是否有错误
def check_log_for_errors(log_file):
    error_patterns = [
        r'Error:',
        r'Exception:',
        r'Traceback \(most recent call last\):',
        r'error:',
        r'failed:',
        r'Failed:',
        r'错误:'
    ]
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
            
        for pattern in error_patterns:
            if re.search(pattern, log_content):
                return True, pattern
        return False, None
    except Exception as e:
        logging.error(f"检查日志文件时出错: {e}")
        return True, str(e)

# 获取 tasks 文件夹中的所有 Python 文件
def get_task_files():
    tasks_dir = Path(__file__).parent / 'tasks'
    if not tasks_dir.exists():
        logging.error(f"任务文件夹 {tasks_dir} 不存在")
        return []
    
    # 使用正则表达式提取文件名前缀的数字，并按数字大小排序
    def extract_number(filename):
        match = re.match(r'(\d+)_', filename.name)
        if match:
            return int(match.group(1))
        return float('inf')  # 如果没有数字前缀，放到最后
    
    # 按照文件名的数字前缀排序
    task_files = sorted(tasks_dir.glob('*.py'), key=extract_number)
    if not task_files:
        logging.warning("没有找到任何任务文件")
        return []
    
    print(f"找到 {len(task_files)} 个任务文件")
    for task_file in task_files:
        print(f"任务文件: {task_file.name}")

    return task_files

# 跨平台检查进程是否存在
def is_process_running(pid):
    system = platform.system()
    if system == 'Windows':
        try:
            import psutil
            return psutil.pid_exists(pid)
        except ImportError:
            logging.warning("psutil 库未安装，无法准确检查 Windows 上的进程状态")
            return False
    elif system in ['Darwin', 'Linux']:
        try:
            os.kill(pid, 0)  # 发送信号0，不实际kill进程
        except OSError:
            return False
        else:
            return True
    else:
        logging.warning(f"不支持的操作系统: {system}")
        return False

def main():
    # 设置日志
    log_file = setup_logging()
    logging.info("开始执行任务")
    
    # 定义锁文件路径
    user_home = os.path.expanduser('~')
    lock_file_path = os.path.join(user_home, '.agenda_tool.lock')
    pid_file_path = os.path.join(user_home, '.agenda_tool.pid')
    
    # 尝试获取文件锁
    if os.path.exists(lock_file_path):
        with open(lock_file_path, 'r') as f:
            try:
                pid = int(f.read().strip())
            except ValueError:
                pid = None
            
        # 检查PID对应的进程是否仍在运行
        if pid and is_process_running(pid):
            logging.warning("脚本已经在运行，退出。")
            sys.exit(0)
        else:
            # PID对应的进程不存在或无效，清理锁文件和PID文件
            logging.info("发现残留锁文件，但原进程已不存在，清理锁文件和PID文件。")
            os.remove(lock_file_path)
            if os.path.exists(pid_file_path):
                os.remove(pid_file_path)
    
    # 写入当前进程的PID到PID文件和锁文件
    with open(pid_file_path, 'w') as f:
        f.write(str(os.getpid()))
    with open(lock_file_path, 'w') as f:
        f.write(str(os.getpid()))
    
    try:
        # 获取任务文件
        task_files = get_task_files()
        if not task_files:
            logging.warning("没有找到任何任务文件")
            return
        
        # 执行每个任务
        for task_file in task_files:
            task_name = task_file.name
            logging.info(f"开始执行任务: {task_name}")
            
            # 尝试执行任务，最多重试3次
            for attempt in range(1, 4):
                try:
                    start_time = time.time()
                    # 执行Python脚本并捕获输出到日志
                    process = subprocess.run(
                        [sys.executable, str(task_file)],
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    # 记录脚本的标准输出和标准错误
                    if process.stdout:
                        logging.info(f"任务 {task_name} Print:\n{process.stdout}")
                    if process.stderr:
                        logging.info(f"任务 {task_name} Logger:\n{process.stderr}")
                    
                    end_time = time.time()
                    execution_time = end_time - start_time
                    
                    if process.returncode == 0:
                        logging.info(f"任务 {task_name} 执行成功，耗时: {execution_time:.2f}秒")
                        break
                    else:
                        logging.error(f"任务 {task_name} 执行失败，返回码: {process.returncode}，第{attempt}次尝试")
                        if attempt < 3:
                            logging.info(f"等待1秒后重试任务 {task_name}...")
                            time.sleep(1)
                        else:
                            logging.error(f"任务 {task_name} 达到最大重试次数，停止执行")
                            raise Exception(f"任务 {task_name} 执行失败")
                
                except Exception as e:
                    logging.error(f"执行任务 {task_name} 时发生异常: {e}")
                    if attempt == 3:
                        raise
            
            # 检查日志是否有错误
            has_error, error_pattern = check_log_for_errors(log_file)
            if has_error:
                logging.error(f"检测到日志中存在错误信息 ({error_pattern})，停止后续任务执行")
                break
            
            logging.info(f"任务 {task_name} 完成")
        
        logging.info("所有任务处理完成")
    
    except Exception as e:
        logging.error(f"执行过程中发生错误: {e}")
    
    finally:
        # 清理锁文件和PID文件
        try:
            if os.path.exists(lock_file_path):
                os.remove(lock_file_path)
            if os.path.exists(pid_file_path):
                os.remove(pid_file_path)
            logging.info("已清理锁文件和PID文件")
        except Exception as e:
            logging.error(f"清理锁文件时出错: {e}")

if __name__ == "__main__":
    main()

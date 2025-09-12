#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code 专用的多代理系统快速调用接口
提供简单直接的命令行调用方式
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import PersonalAssistant

def run_assistant_command(command, assistant=None):
    """运行助理命令"""
    if assistant is None:
        assistant = PersonalAssistant()
    
    today = datetime.now().strftime('%Y-%m-%d')
    daily_folder = assistant.file_manager.create_daily_folder(today)
    results = {}
    
    if command == 'news':
        print("📰 正在获取今日新闻...")
        result = assistant.agents['news_agent'].execute(today, daily_folder, results)
        print("✅ 新闻获取完成！")
        return result
        
    elif command == 'outfit':
        print("👗 正在获取穿搭建议...")
        result = assistant.agents['outfit_agent'].execute(today, daily_folder, results)
        print("✅ 穿搭建议获取完成！")
        return result
        
    elif command == 'report':
        print("📝 正在生成工作日报...")
        result = assistant.agents['daily_report_agent'].execute(today, daily_folder, results)
        print("✅ 工作日报生成完成！")
        return result
        
    elif command == 'health':
        print("💪 正在获取健康建议...")
        result = assistant.agents['coach_agent'].execute(today, daily_folder, results)
        print("✅ 健康建议获取完成！")
        return result
        
    elif command == 'reflection':
        print("🤔 正在进行深度反思...")
        result = assistant.agents['reflection_agent'].execute(today, daily_folder, results)
        print("✅ 深度反思完成！")
        return result
        
    elif command == 'workflow':
        print("🚀 正在运行完整工作流程...")
        results = assistant.start_daily_workflow()
        print("✅ 完整工作流程执行完成！")
        return results
        
    elif command == 'status':
        print("📊 系统状态:")
        status = assistant.workflow_manager.get_workflow_status()
        print(f"  • 工作流状态: {status['status']}")
        print(f"  • 当前步骤: {status['current_step']}")
        print(f"  • 总步骤数: {status['total_steps']}")
        print(f"  • 今日日期: {today}")
        return status
        
    else:
        print(f"❌ 未知命令: {command}")
        return None

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='秋芝的个人助理团队 - 快速调用')
    parser.add_argument('command', nargs='?', help='要执行的命令')
    
    args = parser.parse_args()
    
    if args.command:
        # 执行指定命令
        run_assistant_command(args.command)
    else:
        # 显示帮助信息
        print("🤖 秋芝的个人助理团队 - 快速调用命令")
        print("=" * 50)
        print("可用命令:")
        print("  python quick_assistant.py news      - 获取今日新闻")
        print("  python quick_assistant.py outfit    - 获取穿搭建议")
        print("  python quick_assistant.py report    - 生成工作日报")
        print("  python quick_assistant.py health    - 获取健康建议")
        print("  python quick_assistant.py reflection- 进行深度反思")
        print("  python quick_assistant.py workflow  - 运行完整工作流程")
        print("  python quick_assistant.py status    - 查看系统状态")
        print("=" * 50)

if __name__ == "__main__":
    main()
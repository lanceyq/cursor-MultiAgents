#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Code界面专用的多代理系统交互接口
允许在命令行中直接与多代理系统交互
"""

import sys
import os
import json
import argparse
from datetime import datetime
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import PersonalAssistant

class InteractiveAssistant:
    """交互式助理界面"""
    
    def __init__(self):
        self.assistant = None
        self.current_date = datetime.now().strftime('%Y-%m-%d')
        
    def initialize(self):
        """初始化助理系统"""
        print("🌟 正在初始化秋芝的个人助理团队...")
        try:
            self.assistant = PersonalAssistant()
            print("✅ 系统初始化完成！")
            return True
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            return False
    
    def show_menu(self):
        """显示主菜单"""
        print("\n" + "="*60)
        print("🤖 秋芝的个人助理团队 - 交互式控制台")
        print("="*60)
        print("📋 可用功能:")
        print("1. 📰 获取今日新闻")
        print("2. 👗 获取穿搭建议")
        print("3. 📝 生成工作日报")
        print("4. 💪 健康建议和记录")
        print("5. 🤔 深度反思分析")
        print("6. 🚀 运行完整工作流程")
        print("7. 📊 查看系统状态")
        print("8. ⚙️ 查看工作流配置")
        print("9. 📁 查看今日数据")
        print("0. 🚪 退出系统")
        print("="*60)
    
    def get_news(self):
        """获取新闻"""
        print("\n📰 正在获取今日新闻...")
        try:
            today = self.current_date
            daily_folder = self.assistant.file_manager.create_daily_folder(today)
            result = self.assistant.agents['news_agent'].execute(today, daily_folder, {})
            print("✅ 新闻获取完成！")
            return result
        except Exception as e:
            print(f"❌ 新闻获取失败: {e}")
            return None
    
    def get_outfit(self):
        """获取穿搭建议"""
        print("\n👗 正在获取穿搭建议...")
        try:
            today = self.current_date
            daily_folder = self.assistant.file_manager.create_daily_folder(today)
            result = self.assistant.agents['outfit_agent'].execute(today, daily_folder, {})
            print("✅ 穿搭建议获取完成！")
            return result
        except Exception as e:
            print(f"❌ 穿搭建议获取失败: {e}")
            return None
    
    def get_daily_report(self):
        """生成工作日报"""
        print("\n📝 正在生成工作日报...")
        try:
            today = self.current_date
            daily_folder = self.assistant.file_manager.create_daily_folder(today)
            result = self.assistant.agents['daily_report_agent'].execute(today, daily_folder, {})
            print("✅ 工作日报生成完成！")
            return result
        except Exception as e:
            print(f"❌ 工作日报生成失败: {e}")
            return None
    
    def get_health_coach(self):
        """健康建议"""
        print("\n💪 正在获取健康建议...")
        try:
            today = self.current_date
            daily_folder = self.assistant.file_manager.create_daily_folder(today)
            result = self.assistant.agents['coach_agent'].execute(today, daily_folder, {})
            print("✅ 健康建议获取完成！")
            return result
        except Exception as e:
            print(f"❌ 健康建议获取失败: {e}")
            return None
    
    def get_reflection(self):
        """深度反思"""
        print("\n🤔 正在进行深度反思...")
        try:
            today = self.current_date
            daily_folder = self.assistant.file_manager.create_daily_folder(today)
            result = self.assistant.agents['reflection_agent'].execute(today, daily_folder, {})
            print("✅ 深度反思完成！")
            return result
        except Exception as e:
            print(f"❌ 深度反思失败: {e}")
            return None
    
    def run_full_workflow(self):
        """运行完整工作流程"""
        print("\n🚀 正在运行完整工作流程...")
        try:
            results = self.assistant.start_daily_workflow()
            print("✅ 完整工作流程执行完成！")
            return results
        except Exception as e:
            print(f"❌ 工作流程执行失败: {e}")
            return None
    
    def show_system_status(self):
        """显示系统状态"""
        print("\n📊 系统状态:")
        try:
            status = self.assistant.workflow_manager.get_workflow_status()
            print(f"  • 工作流状态: {status['status']}")
            print(f"  • 当前步骤: {status['current_step']}")
            print(f"  • 总步骤数: {status['total_steps']}")
            print(f"  • 今日日期: {self.current_date}")
            
            # 显示代理状态
            print("\n🤖 代理状态:")
            for agent_name in self.assistant.agents.keys():
                print(f"  • {agent_name}: 已初始化")
                
        except Exception as e:
            print(f"❌ 获取状态失败: {e}")
    
    def show_workflow_config(self):
        """显示工作流配置"""
        print("\n⚙️ 工作流配置:")
        try:
            workflow_steps = self.assistant.config_manager.get_workflow_steps()
            for i, step in enumerate(workflow_steps, 1):
                print(f"  {i}. {step['name']} ({step['agent']})")
                if step.get('dependencies'):
                    print(f"     依赖: {step['dependencies']}")
        except Exception as e:
            print(f"❌ 获取配置失败: {e}")
    
    def show_today_data(self):
        """显示今日数据"""
        print(f"\n📁 今日数据 ({self.current_date}):")
        try:
            data_path = os.path.join('data', 'daily_records', self.current_date)
            if os.path.exists(data_path):
                files = os.listdir(data_path)
                for file in files:
                    print(f"  • {file}")
            else:
                print("  • 今日暂无数据")
        except Exception as e:
            print(f"❌ 获取数据失败: {e}")
    
    def run_interactive(self):
        """运行交互模式"""
        if not self.initialize():
            return
        
        while True:
            self.show_menu()
            try:
                choice = input("\n请选择功能 (0-9): ").strip()
                
                if choice == '0':
                    print("👋 感谢使用秋芝的个人助理团队！")
                    break
                elif choice == '1':
                    self.get_news()
                elif choice == '2':
                    self.get_outfit()
                elif choice == '3':
                    self.get_daily_report()
                elif choice == '4':
                    self.get_health_coach()
                elif choice == '5':
                    self.get_reflection()
                elif choice == '6':
                    self.run_full_workflow()
                elif choice == '7':
                    self.show_system_status()
                elif choice == '8':
                    self.show_workflow_config()
                elif choice == '9':
                    self.show_today_data()
                else:
                    print("❌ 无效选择，请重新输入")
                
                # 暂停一下让用户查看结果
                if choice != '0':
                    input("\n按回车键继续...")
                    
            except KeyboardInterrupt:
                print("\n\n👋 程序被用户中断")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                input("\n按回车键继续...")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='秋芝的个人助理团队 - 交互式控制台')
    parser.add_argument('--auto', action='store_true', help='自动运行完整工作流程')
    parser.add_argument('--news', action='store_true', help='只获取新闻')
    parser.add_argument('--outfit', action='store_true', help='只获取穿搭建议')
    parser.add_argument('--report', action='store_true', help='只生成日报')
    parser.add_argument('--health', action='store_true', help='只获取健康建议')
    parser.add_argument('--reflection', action='store_true', help='只进行反思')
    parser.add_argument('--status', action='store_true', help='显示系统状态')
    
    args = parser.parse_args()
    
    # 创建交互式助理
    interactive_assistant = InteractiveAssistant()
    
    if args.auto:
        # 自动运行完整工作流程
        if interactive_assistant.initialize():
            interactive_assistant.run_full_workflow()
    elif args.news:
        # 只获取新闻
        if interactive_assistant.initialize():
            interactive_assistant.get_news()
    elif args.outfit:
        # 只获取穿搭建议
        if interactive_assistant.initialize():
            interactive_assistant.get_outfit()
    elif args.report:
        # 只生成日报
        if interactive_assistant.initialize():
            interactive_assistant.get_daily_report()
    elif args.health:
        # 只获取健康建议
        if interactive_assistant.initialize():
            interactive_assistant.get_health_coach()
    elif args.reflection:
        # 只进行反思
        if interactive_assistant.initialize():
            interactive_assistant.get_reflection()
    elif args.status:
        # 显示系统状态
        if interactive_assistant.initialize():
            interactive_assistant.show_system_status()
    else:
        # 交互模式
        interactive_assistant.run_interactive()

if __name__ == "__main__":
    main()
"""
个人生活助理团队 - 主入口文件
Author: 秋芝
Date: 2025-09-11
"""
# 测试hook
import os
import json
import logging
from datetime import datetime
from pathlib import Path

from src.agents.news_agent import NewsAgent
from src.agents.outfit_agent import OutfitAgent
from src.agents.daily_report_agent import DailyReportAgent
from src.agents.coach_agent import CoachAgent
from src.agents.reflection_agent import ReflectionAgent
from src.utils.config_manager import ConfigManager
from src.utils.file_manager import FileManager
from src.utils.workflow_manager import WorkflowManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('personal_assistant.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PersonalAssistant:
    """个人生活助理主类"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.file_manager = FileManager()
        self.workflow_manager = WorkflowManager(self.config_manager, self.file_manager)
        
        # 初始化agents
        self.agents = {
            'news_agent': NewsAgent(self.config_manager, self.file_manager),
            'outfit_agent': OutfitAgent(self.config_manager, self.file_manager),
            'daily_report_agent': DailyReportAgent(self.config_manager, self.file_manager),
            'coach_agent': CoachAgent(self.config_manager, self.file_manager),
            'reflection_agent': ReflectionAgent(self.config_manager, self.file_manager)
        }
        
        logger.info("个人生活助理团队初始化完成")
    
    async def start_daily_workflow(self):
        """启动每日工作流程"""
        logger.info("开始每日工作流程")
        
        try:
            # 创建今日文件夹
            today = datetime.now().strftime('%Y-%m-%d')
            daily_folder = self.file_manager.create_daily_folder(today)
            
            # 执行工作流程
            results = {}
            workflow_steps = self.config_manager.get_workflow_steps()
            
            for step in workflow_steps:
                agent_name = step['agent']
                agent = self.agents[agent_name]
                
                logger.info(f"执行 {step['name']}...")
                
                # 执行agent任务
                if hasattr(agent.execute, '__await__'):
                    result = await agent.execute(today, daily_folder, results)
                else:
                    result = agent.execute(today, daily_folder, results)
                
                results[agent_name] = result
                
                logger.info(f"{step['name']} 完成")
            
            logger.info("每日工作流程完成")
            return results
            
        except Exception as e:
            logger.error(f"工作流程执行失败: {e}")
            return None
    
    def handle_user_input(self, user_input: str):
        """处理用户输入"""
        logger.info(f"处理用户输入: {user_input}")
        
        # 检查触发词
        triggers = self.config_manager.get_triggers()
        
        for trigger_type, trigger_info in triggers.items():
            for pattern in trigger_info['patterns']:
                if pattern in user_input.lower():
                    return self.handle_trigger(trigger_type, user_input)
        
        # 默认处理
        return self.handle_general_input(user_input)
    
    def handle_trigger(self, trigger_type: str, user_input: str):
        """处理特定触发"""
        logger.info(f"触发类型: {trigger_type}")
        
        if trigger_type == 'morning_greeting':
            return self.start_daily_workflow()
        
        elif trigger_type == 'work_end_command':
            return self.start_reflection_workflow()
        
        else:
            logger.warning(f"未知触发类型: {trigger_type}")
            return None
    
    def start_reflection_workflow(self):
        """启动反思工作流程"""
        logger.info("开始反思工作流程")
        
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            daily_folder = self.file_manager.get_daily_folder(today)
            
            if not daily_folder:
                logger.error("找不到今日数据文件夹")
                return None
            
            # 执行反思agent
            reflection_agent = self.agents['reflection_agent']
            result = reflection_agent.execute(today, daily_folder, {})
            
            logger.info("反思工作流程完成")
            return result
            
        except Exception as e:
            logger.error(f"反思工作流程执行失败: {e}")
            return None
    
    def handle_general_input(self, user_input: str):
        """处理一般用户输入"""
        logger.info("处理一般用户输入")
        
        # 这里可以添加更多智能对话逻辑
        return {
            'response': '我理解了您的输入，请告诉我您需要什么帮助？',
            'type': 'general'
        }

def main():
    """主函数"""
    print("🌟 秋芝的个人生活助理团队启动中...")
    
    try:
        assistant = PersonalAssistant()
        
        # 示例：启动每日工作流程
        # results = assistant.start_daily_workflow()
        # print("工作流程结果:", results)
        
        # 示例：处理用户输入
        # user_input = "早上好"
        # response = assistant.handle_user_input(user_input)
        # print("系统响应:", response)
        
        print("✅ 个人生活助理团队准备就绪！")
        
    except Exception as e:
        logger.error(f"系统启动失败: {e}")
        print(f"❌ 系统启动失败: {e}")

if __name__ == "__main__":
    main()

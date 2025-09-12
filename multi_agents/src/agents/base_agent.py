"""
基础Agent类
所有agent的基类，定义通用接口和方法
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from src.utils.config_manager import ConfigManager
from src.utils.file_manager import FileManager
from src.services.mcp_service import MCPService

class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, config_manager: ConfigManager, file_manager: FileManager):
        self.config_manager = config_manager
        self.file_manager = file_manager
        self.agent_name = self.__class__.__name__
        
        # 获取agent配置
        self.config = config_manager.get_agent_config(self.agent_name.lower().replace('_agent', ''))
        
        # 初始化状态
        self.is_enabled = self.config.get('enabled', True)
        self.dependencies = self.config.get('dependencies', [])
        self.mcp_tools = self.config.get('mcp_tools', [])
        
        # 初始化MCP服务
        self.mcp_service = MCPService()
        
        print(f"🤖 {self.agent_name} 初始化完成")
    
    @abstractmethod
    def execute(self, date_str: str, daily_folder: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行agent的主要逻辑"""
        pass
    
    def check_dependencies(self, context: Dict[str, Any]) -> bool:
        """检查依赖是否满足"""
        for dependency in self.dependencies:
            if dependency not in context:
                print(f"⚠️  {self.agent_name} 依赖 {dependency} 未满足")
                return False
        return True
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        if not isinstance(input_data, dict):
            return False
        return True
    
    def format_output(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """格式化输出结果"""
        return {
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "result": result
        }
    
    def save_result(self, date_str: str, result_type: str, content: str):
        """保存结果到文件"""
        self.file_manager.save_daily_record(date_str, result_type, content)
    
    def get_template_content(self, template_name: str) -> str:
        """获取模板内容"""
        return self.file_manager.get_template_content(template_name)
    
    def generate_from_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """从模板生成内容"""
        return self.file_manager.generate_from_template(template_name, variables)
    
    def get_user_preference(self, preference_key: str) -> Any:
        """获取用户偏好"""
        preferences = self.config_manager.get_user_preferences()
        return preferences.get(preference_key)
    
    def get_user_info(self, info_type: str) -> Dict[str, Any]:
        """获取用户信息"""
        return self.config_manager.get_user_info(info_type)
    
    def log_action(self, action: str, details: Dict[str, Any] = None):
        """记录操作日志"""
        log_entry = {
            "agent": self.agent_name,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        print(f"📝 {self.agent_name}: {action}")
        return log_entry
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """错误处理"""
        error_info = {
            "agent": self.agent_name,
            "error": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {}
        }
        print(f"❌ {self.agent_name} 错误: {error}")
        return {
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "error": str(error)
        }
    
    def is_enabled(self) -> bool:
        """检查agent是否启用"""
        return self.is_enabled
    
    def get_required_inputs(self) -> list:
        """获取必需的输入"""
        return self.config.get('required_inputs', [])
    
    def get_expected_outputs(self) -> list:
        """获取期望的输出"""
        return self.config.get('outputs', [])
    
    def pre_execute(self, context: Dict[str, Any]) -> bool:
        """执行前检查"""
        if not self.is_enabled:
            print(f"⚠️  {self.agent_name} 已禁用")
            return False
        
        if not self.check_dependencies(context):
            return False
        
        return True
    
    def post_execute(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """执行后处理"""
        return self.format_output(result)
    
    def run(self, date_str: str, daily_folder: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """运行agent的完整流程"""
        try:
            # 执行前检查
            if not self.pre_execute(context):
                return self.handle_error(Exception("执行前检查失败"))
            
            # 记录开始
            self.log_action("开始执行", {"date": date_str, "context": context})
            
            # 执行主要逻辑
            result = self.execute(date_str, daily_folder, context)
            
            # 执行后处理
            final_result = self.post_execute(result)
            
            # 记录完成
            self.log_action("执行完成", {"result": final_result})
            
            return final_result
            
        except Exception as e:
            return self.handle_error(e, {"date": date_str, "context": context})
    
    # MCP工具调用方法
    async def call_mcp_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """调用MCP工具"""
        try:
            if tool_name == 'jimeng_generate_image':
                return await self.mcp_service.call_jimeng_generate_image(**kwargs)
            elif tool_name == 'firecrawl_scrape':
                return await self.mcp_service.call_firecrawl_scrape(**kwargs)
            elif tool_name == 'weather_current':
                return await self.mcp_service.call_weather_current(**kwargs)
            elif tool_name == 'lark_send_message':
                return await self.mcp_service.call_lark_send_message(**kwargs)
            else:
                return {
                    'success': False,
                    'error': f'Unknown tool: {tool_name}',
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tool': tool_name,
                'timestamp': datetime.now().isoformat()
            }
    
    def get_mcp_tool_status(self) -> Dict[str, Any]:
        """获取MCP工具状态"""
        return self.mcp_service.get_tool_status()
    
    def is_mcp_tool_available(self, tool_name: str) -> bool:
        """检查MCP工具是否可用"""
        return self.mcp_service.is_tool_available(tool_name)
    
    async def test_mcp_tools(self) -> Dict[str, Any]:
        """测试所有MCP工具"""
        return await self.mcp_service.test_all_tools()
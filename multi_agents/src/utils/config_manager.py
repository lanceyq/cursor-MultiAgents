"""
配置管理器
负责管理所有配置文件的读取和更新
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.configs = {}
        self._load_all_configs()
    
    def _load_all_configs(self):
        """加载所有配置文件"""
        config_files = {
            'agent_config': 'agent_config.json',
            'workflow_config': 'workflow_config.json',
            'user_preferences': 'user_preferences.json'
        }
        
        for config_name, filename in config_files.items():
            file_path = self.config_path / filename
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.configs[config_name] = json.load(f)
            else:
                print(f"警告: 配置文件 {filename} 不存在")
                self.configs[config_name] = {}
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """获取特定agent的配置"""
        return self.configs.get('agent_config', {}).get('agents', {}).get(agent_name, {})
    
    def get_workflow_steps(self) -> list:
        """获取工作流程步骤"""
        return self.configs.get('workflow_config', {}).get('workflow', {}).get('daily_sequence', {}).get('steps', [])
    
    def get_triggers(self) -> Dict[str, Any]:
        """获取触发器配置"""
        return self.configs.get('workflow_config', {}).get('triggers', {})
    
    def get_user_preferences(self) -> Dict[str, Any]:
        """获取用户偏好"""
        return self.configs.get('user_preferences', {}).get('preferences', {})
    
    def get_api_config(self) -> Dict[str, Any]:
        """获取API配置"""
        return self.configs.get('user_preferences', {}).get('api_config', {})
    
    def get_user_info(self, info_type: str) -> Dict[str, Any]:
        """获取用户信息"""
        user_info_path = Path('aboutme') / f'{info_type}.json'
        if user_info_path.exists():
            with open(user_info_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def update_config(self, config_name: str, new_config: Dict[str, Any]):
        """更新配置"""
        self.configs[config_name].update(new_config)
        self._save_config(config_name)
    
    def _save_config(self, config_name: str):
        """保存配置到文件"""
        config_mapping = {
            'agent_config': 'agent_config.json',
            'workflow_config': 'workflow_config.json',
            'user_preferences': 'user_preferences.json'
        }
        
        if config_name in config_mapping:
            file_path = self.config_path / config_mapping[config_name]
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.configs[config_name], f, ensure_ascii=False, indent=2)
    
    def get_agent_enabled_status(self, agent_name: str) -> bool:
        """检查agent是否启用"""
        agent_config = self.get_agent_config(agent_name)
        return agent_config.get('enabled', False)
    
    def get_agent_dependencies(self, agent_name: str) -> list:
        """获取agent的依赖"""
        agent_config = self.get_agent_config(agent_name)
        return agent_config.get('dependencies', [])
    
    def get_template_content(self, template_name: str) -> str:
        """获取模板内容"""
        template_path = Path('templates') / f'{template_name}.md'
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
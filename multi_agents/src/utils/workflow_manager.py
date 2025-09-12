"""
工作流程管理器
负责管理各个agent的工作流程和依赖关系
"""

import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from src.utils.config_manager import ConfigManager
from src.utils.file_manager import FileManager

class WorkflowManager:
    """工作流程管理器"""
    
    def __init__(self, config_manager: ConfigManager, file_manager: FileManager):
        self.config_manager = config_manager
        self.file_manager = file_manager
        self.current_step = 0
        self.workflow_status = "idle"
        self.workflow_results = {}
    
    def start_workflow(self, workflow_type: str = "daily") -> Dict[str, Any]:
        """启动工作流程"""
        self.workflow_status = "running"
        self.current_step = 0
        self.workflow_results = {}
        
        print(f"🚀 开始{workflow_type}工作流程...")
        
        try:
            if workflow_type == "daily":
                result = self._execute_daily_workflow()
            elif workflow_type == "reflection":
                result = self._execute_reflection_workflow()
            else:
                raise ValueError(f"未知的工作流程类型: {workflow_type}")
            
            self.workflow_status = "completed"
            print(f"✅ {workflow_type}工作流程完成")
            return result
            
        except Exception as e:
            self.workflow_status = "error"
            print(f"❌ 工作流程执行失败: {e}")
            return {"error": str(e)}
    
    def _execute_daily_workflow(self) -> Dict[str, Any]:
        """执行每日工作流程"""
        workflow_steps = self.config_manager.get_workflow_steps()
        
        for step in workflow_steps:
            self.current_step += 1
            step_name = step.get('name', f'Step {self.current_step}')
            agent_name = step.get('agent')
            
            print(f"📋 执行步骤 {self.current_step}: {step_name}")
            
            # 检查依赖
            if not self._check_dependencies(step):
                print(f"⚠️  步骤 {step_name} 的依赖未满足，跳过")
                continue
            
            # 执行步骤
            step_result = self._execute_step(step)
            
            if step_result:
                self.workflow_results[agent_name] = step_result
                print(f"✅ 步骤 {step_name} 完成")
            else:
                print(f"❌ 步骤 {step_name} 执行失败")
        
        return self.workflow_results
    
    def _execute_reflection_workflow(self) -> Dict[str, Any]:
        """执行反思工作流程"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        # 获取今天的所有数据
        daily_data = self.file_manager.get_all_daily_data(today)
        
        if not daily_data:
            print("⚠️  今天还没有任何数据，无法进行反思")
            return {"error": "没有今日数据"}
        
        print("🤔 开始深度反思...")
        
        # 这里应该调用反思agent
        # 由于现在还没有实现，先返回数据
        reflection_data = {
            "date": today,
            "daily_data": daily_data,
            "reflection_content": "反思内容待生成"
        }
        
        return {"reflection_agent": reflection_data}
    
    def _check_dependencies(self, step: Dict[str, Any]) -> bool:
        """检查步骤依赖"""
        dependencies = step.get('dependencies', [])
        
        for dependency in dependencies:
            if dependency not in self.workflow_results:
                return False
        
        return True
    
    def _execute_step(self, step: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """执行单个步骤"""
        # 这里应该根据step配置调用相应的agent
        # 由于现在还没有实现具体的agent，先返回模拟结果
        
        agent_name = step.get('agent')
        step_name = step.get('name')
        
        print(f"🔄 执行 {step_name} (agent: {agent_name})")
        
        # 模拟执行时间
        time.sleep(1)
        
        # 返回模拟结果
        return {
            "step": step_name,
            "agent": agent_name,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "result": f"{step_name} 的结果"
        }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """获取工作流程状态"""
        return {
            "status": self.workflow_status,
            "current_step": self.current_step,
            "total_steps": len(self.config_manager.get_workflow_steps()),
            "results": self.workflow_results
        }
    
    def pause_workflow(self):
        """暂停工作流程"""
        self.workflow_status = "paused"
        print("⏸️  工作流程已暂停")
    
    def resume_workflow(self):
        """恢复工作流程"""
        if self.workflow_status == "paused":
            self.workflow_status = "running"
            print("▶️  工作流程已恢复")
            return self.start_workflow()
        else:
            print("⚠️  工作流程未暂停，无法恢复")
            return None
    
    def cancel_workflow(self):
        """取消工作流程"""
        self.workflow_status = "cancelled"
        print("❌ 工作流程已取消")
    
    def retry_step(self, step_index: int) -> Optional[Dict[str, Any]]:
        """重试特定步骤"""
        workflow_steps = self.config_manager.get_workflow_steps()
        
        if step_index < 0 or step_index >= len(workflow_steps):
            print(f"❌ 无效的步骤索引: {step_index}")
            return None
        
        step = workflow_steps[step_index]
        print(f"🔄 重试步骤 {step_index + 1}: {step.get('name')}")
        
        return self._execute_step(step)
    
    def get_step_logs(self, step_index: int) -> List[Dict[str, Any]]:
        """获取步骤日志"""
        # 这里可以实现日志记录功能
        return [
            {
                "timestamp": datetime.now().isoformat(),
                "step": step_index,
                "message": "步骤日志功能待实现"
            }
        ]
    
    def validate_workflow(self) -> Dict[str, Any]:
        """验证工作流程配置"""
        workflow_steps = self.config_manager.get_workflow_steps()
        
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 检查是否有循环依赖
        dependencies = {}
        for step in workflow_steps:
            agent_name = step.get('agent')
            dependencies[agent_name] = step.get('dependencies', [])
        
        # 这里可以添加更复杂的验证逻辑
        
        return validation_result
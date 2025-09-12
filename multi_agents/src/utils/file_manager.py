"""
文件管理器
负责文件和文件夹的创建、读取、写入等操作
"""

import os
import json
import markdown
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional

class FileManager:
    """文件管理器"""
    
    def __init__(self, base_path: str = "data"):
        self.base_path = Path(base_path)
        self.ensure_directories()
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.base_path,
            self.base_path / "daily_records",
            self.base_path / "history",
            self.base_path / "analytics"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def create_daily_folder(self, date_str: str) -> Path:
        """创建日期文件夹"""
        daily_folder = self.base_path / "daily_records" / date_str
        daily_folder.mkdir(parents=True, exist_ok=True)
        return daily_folder
    
    def get_daily_folder(self, date_str: str) -> Optional[Path]:
        """获取日期文件夹"""
        daily_folder = self.base_path / "daily_records" / date_str
        if daily_folder.exists():
            return daily_folder
        return None
    
    def save_daily_record(self, date_str: str, record_type: str, content: str):
        """保存每日记录"""
        daily_folder = self.get_daily_folder(date_str)
        if not daily_folder:
            daily_folder = self.create_daily_folder(date_str)
        
        filename = f"{record_type}.md"
        file_path = daily_folder / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def read_daily_record(self, date_str: str, record_type: str) -> Optional[str]:
        """读取每日记录"""
        daily_folder = self.get_daily_folder(date_str)
        if not daily_folder:
            return None
        
        filename = f"{record_type}.md"
        file_path = daily_folder / filename
        
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None
    
    def generate_from_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """从模板生成内容"""
        template_content = self.get_template_content(template_name)
        
        # 替换模板变量
        for key, value in variables.items():
            template_content = template_content.replace(f"{{{{{key}}}}}", str(value))
        
        return template_content
    
    def get_template_content(self, template_name: str) -> str:
        """获取模板内容"""
        template_path = Path('templates') / f'{template_name}.md'
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def save_history_data(self, data_type: str, data: Dict[str, Any]):
        """保存历史数据"""
        history_file = self.base_path / "history" / f"{data_type}_history.json"
        
        # 读取现有数据
        existing_data = []
        if history_file.exists():
            with open(history_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        
        # 添加新数据
        new_entry = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        existing_data.append(new_entry)
        
        # 保存数据
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
    
    def get_history_data(self, data_type: str, days: int = 30) -> list:
        """获取历史数据"""
        history_file = self.base_path / "history" / f"{data_type}_history.json"
        
        if not history_file.exists():
            return []
        
        with open(history_file, 'r', encoding='utf-8') as f:
            all_data = json.load(f)
        
        # 过滤最近N天的数据
        cutoff_date = (datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        recent_data = [entry for entry in all_data if entry['date'] >= cutoff_date]
        
        return recent_data
    
    def save_analytics(self, analytics_type: str, data: Dict[str, Any]):
        """保存分析数据"""
        analytics_file = self.base_path / "analytics" / f"{analytics_type}.json"
        
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def get_analytics(self, analytics_type: str) -> Dict[str, Any]:
        """获取分析数据"""
        analytics_file = self.base_path / "analytics" / f"{analytics_type}.json"
        
        if analytics_file.exists():
            with open(analytics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def get_all_daily_data(self, date_str: str) -> Dict[str, Any]:
        """获取某天的所有数据"""
        daily_data = {}
        
        # 获取各种记录
        record_types = ['news', 'outfit', 'health', 'daily_report', 'reflection']
        
        for record_type in record_types:
            content = self.read_daily_record(date_str, record_type)
            if content:
                daily_data[record_type] = content
        
        return daily_data
    
    def cleanup_old_files(self, days: int = 90):
        """清理旧文件"""
        cutoff_date = (datetime.now() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
        
        daily_records_dir = self.base_path / "daily_records"
        
        for daily_folder in daily_records_dir.iterdir():
            if daily_folder.is_dir() and daily_folder.name < cutoff_date:
                # 删除旧文件夹
                import shutil
                shutil.rmtree(daily_folder)
                print(f"已删除旧文件夹: {daily_folder.name}")
    
    def backup_data(self):
        """备份数据"""
        backup_path = Path("backup")
        backup_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_path / f"data_backup_{timestamp}.zip"
        
        # 这里可以实现具体的备份逻辑
        print(f"数据备份已创建: {backup_file}")
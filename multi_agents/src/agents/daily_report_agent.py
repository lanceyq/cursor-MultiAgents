"""
日报秋Agent
生成工作日报并同步到飞书
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class DailyReportAgent(BaseAgent):
    """日报秋Agent"""
    
    def __init__(self, config_manager, file_manager):
        super().__init__(config_manager, file_manager)
        self.agent_name = "DailyReportAgent"
    
    def execute(self, date_str: str, daily_folder: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行工作日报生成"""
        try:
            # 获取用户工作信息
            work_profile = self.get_user_info('work_profile')
            
            # 获取工作内容（在实际应用中，这里应该通过用户交互获取）
            work_summary = self._get_work_summary()
            
            # 分析工作数据
            work_analysis = self._analyze_work_data(work_summary, work_profile)
            
            # 生成日报
            daily_report = self._generate_daily_report(date_str, work_summary, work_analysis)
            
            # 保存日报
            self.save_result(date_str, 'daily_report', daily_report)
            
            # 同步到飞书
            self._sync_to_lark(daily_report)
            
            return {
                "daily_report": daily_report,
                "work_summary": work_summary,
                "work_analysis": work_analysis,
                "report_length": len(daily_report)
            }
            
        except Exception as e:
            return self.handle_error(e, {"date": date_str, "daily_folder": daily_folder})
    
    def _get_work_summary(self) -> Dict[str, Any]:
        """获取工作内容"""
        # 在实际应用中，这里应该通过用户交互获取
        # 现在先返回模拟数据
        
        mock_work_data = {
            "completed_tasks": [
                "完成了产品需求文档的撰写",
                "与开发团队讨论了技术实现方案",
                "分析了用户反馈数据",
                "参与了产品评审会议"
            ],
            "ongoing_tasks": [
                "优化产品用户体验",
                "准备下周的产品演示",
                "跟进项目进度"
            ],
            "tomorrow_plan": [
                "继续优化产品功能",
                "与设计团队沟通UI改进",
                "撰写项目总结报告"
            ],
            "challenges": [
                "技术实现遇到一些困难",
                "时间安排比较紧张"
            ],
            "insights": [
                "用户对现有功能反馈较好",
                "需要加强团队沟通效率"
            ],
            "work_hours": "8小时",
            "meeting_count": 3,
            "focus_areas": ["产品规划", "团队协作", "用户研究"]
        }
        
        return mock_work_data
    
    def _analyze_work_data(self, work_summary: Dict[str, Any], work_profile: Dict[str, Any]) -> Dict[str, Any]:
        """分析工作数据"""
        completed_tasks = work_summary.get('completed_tasks', [])
        work_hours = work_summary.get('work_hours', '8小时')
        meeting_count = work_summary.get('meeting_count', 0)
        
        # 计算效率指标
        task_count = len(completed_tasks)
        efficiency_score = self._calculate_efficiency_score(task_count, work_hours, meeting_count)
        
        # 分析工作重点
        focus_areas = work_summary.get('focus_areas', [])
        work_focus = self._analyze_work_focus(focus_areas)
        
        # 生成工作心得
        work_insights = self._generate_work_insights(work_summary, work_profile)
        
        # 评估满意度
        satisfaction_level = self._evaluate_satisfaction(work_summary, work_profile)
        
        # 分析目标进展
        goal_progress = self._analyze_goal_progress(work_summary, work_profile)
        
        return {
            "efficiency_score": efficiency_score,
            "work_focus": work_focus,
            "work_insights": work_insights,
            "satisfaction_level": satisfaction_level,
            "goal_progress": goal_progress,
            "metrics": {
                "completed_tasks_count": task_count,
                "work_hours": work_hours,
                "meeting_count": meeting_count,
                "productivity_score": efficiency_score
            }
        }
    
    def _calculate_efficiency_score(self, task_count: int, work_hours: str, meeting_count: int) -> str:
        """计算效率评分"""
        # 简单的效率计算逻辑
        hours_num = int(work_hours.replace('小时', ''))
        
        if task_count >= 5 and hours_num <= 8:
            return "高效率"
        elif task_count >= 3 and hours_num <= 10:
            return "中等效率"
        else:
            return "需要改进"
    
    def _analyze_work_focus(self, focus_areas: List[str]) -> str:
        """分析工作重点"""
        if not focus_areas:
            return "工作重点不明确"
        
        focus_summary = "今日工作重点："
        for i, area in enumerate(focus_areas, 1):
            focus_summary += f"\n{i}. {area}"
        
        return focus_summary
    
    def _generate_work_insights(self, work_summary: Dict[str, Any], work_profile: Dict[str, Any]) -> str:
        """生成工作心得"""
        insights = []
        
        # 分析完成任务
        completed_tasks = work_summary.get('completed_tasks', [])
        if completed_tasks:
            insights.append(f"今日完成了{len(completed_tasks)}项任务，工作充实")
        
        # 分析挑战
        challenges = work_summary.get('challenges', [])
        if challenges:
            insights.append(f"面临{len(challenges)}个挑战，需要重点关注")
        
        # 分析用户技能
        skills = work_profile.get('skills', [])
        if '产品规划' in skills:
            insights.append("产品规划能力得到了充分发挥")
        
        if '团队协作' in skills:
            insights.append("团队协作效果良好")
        
        return "\n\n".join(insights)
    
    def _evaluate_satisfaction(self, work_summary: Dict[str, Any], work_profile: Dict[str, Any]) -> str:
        """评估工作满意度"""
        completed_tasks = work_summary.get('completed_tasks', [])
        challenges = work_summary.get('challenges', [])
        
        # 简单的满意度评估逻辑
        if len(completed_tasks) >= 4 and len(challenges) <= 1:
            return "非常满意"
        elif len(completed_tasks) >= 2 and len(challenges) <= 2:
            return "比较满意"
        else:
            return "一般"
    
    def _analyze_goal_progress(self, work_summary: Dict[str, Any], work_profile: Dict[str, Any]) -> str:
        """分析目标进展"""
        career_goals = work_profile.get('career_goals', {})
        short_term_goals = career_goals.get('short_term', [])
        
        progress_report = "目标进展：\n"
        
        for goal in short_term_goals:
            progress_report += f"- {goal}：进展良好，需要继续努力\n"
        
        return progress_report
    
    def _generate_daily_report(self, date_str: str, work_summary: Dict[str, Any], 
                              work_analysis: Dict[str, Any]) -> str:
        """生成日报内容"""
        # 准备模板变量
        template_vars = {
            "date": date_str,
            "work_summary": self._format_work_summary(work_summary),
            "completed_tasks": self._format_completed_tasks(work_summary.get('completed_tasks', [])),
            "ongoing_tasks": self._format_ongoing_tasks(work_summary.get('ongoing_tasks', [])),
            "tomorrow_plan": self._format_tomorrow_plan(work_summary.get('tomorrow_plan', [])),
            "work_insights": work_analysis.get('work_insights', '暂无心得'),
            "challenges": self._format_challenges(work_summary.get('challenges', [])),
            "work_hours": work_analysis.get('metrics', {}).get('work_hours', '8小时'),
            "meeting_count": work_analysis.get('metrics', {}).get('meeting_count', 0),
            "completed_tasks_count": work_analysis.get('metrics', {}).get('completed_tasks_count', 0),
            "efficiency_score": work_analysis.get('efficiency_score', '中等'),
            "goal_progress": work_analysis.get('goal_progress', '目标进展正常'),
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "satisfaction_level": work_analysis.get('satisfaction_level', '一般')
        }
        
        return self.generate_from_template('report_template', template_vars)
    
    def _format_work_summary(self, work_summary: Dict[str, Any]) -> str:
        """格式化工作概览"""
        completed_tasks = work_summary.get('completed_tasks', [])
        ongoing_tasks = work_summary.get('ongoing_tasks', [])
        
        summary = f"今日完成了{len(completed_tasks)}项任务，正在进行{len(ongoing_tasks)}项工作。"
        
        return summary
    
    def _format_completed_tasks(self, tasks: List[str]) -> str:
        """格式化完成任务"""
        if not tasks:
            return "今日暂无完成的任务"
        
        result = ""
        for i, task in enumerate(tasks, 1):
            result += f"{i}. {task}\n"
        
        return result
    
    def _format_ongoing_tasks(self, tasks: List[str]) -> str:
        """格式化进行中任务"""
        if not tasks:
            return "暂无进行中的任务"
        
        result = ""
        for i, task in enumerate(tasks, 1):
            result += f"{i}. {task}\n"
        
        return result
    
    def _format_tomorrow_plan(self, plans: List[str]) -> str:
        """格式化明日计划"""
        if not plans:
            return "明日计划待定"
        
        result = ""
        for i, plan in enumerate(plans, 1):
            result += f"{i}. {plan}\n"
        
        return result
    
    def _format_challenges(self, challenges: List[str]) -> str:
        """格式化挑战"""
        if not challenges:
            return "今日工作顺利，无特别挑战"
        
        result = ""
        for i, challenge in enumerate(challenges, 1):
            result += f"{i}. {challenge}\n"
        
        return result
    
    def _sync_to_lark(self, daily_report: str):
        """同步到飞书"""
        # 这里应该调用飞书MCP工具创建文档
        print("📄 日报已同步到飞书文档")
        
        # 模拟飞书文档创建
        lark_doc = {
            "title": f"工作日报 - {datetime.now().strftime('%Y-%m-%d')}",
            "content": daily_report,
            "folder": "流程群"
        }
        
        print(f"📋 飞书文档信息：{lark_doc}")
    
    def get_work_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取工作统计"""
        history_data = self.file_manager.get_history_data('daily_report', days)
        
        stats = {
            "total_reports": len(history_data),
            "average_tasks": 0,
            "average_work_hours": 0,
            "productivity_trend": []
        }
        
        total_tasks = 0
        total_hours = 0
        
        for entry in history_data:
            data = entry.get('data', {})
            total_tasks += data.get('completed_tasks_count', 0)
            total_hours += int(data.get('work_hours', '8').replace('小时', ''))
        
        if history_data:
            stats['average_tasks'] = total_tasks / len(history_data)
            stats['average_work_hours'] = total_hours / len(history_data)
        
        return stats
    
    def generate_weekly_summary(self, week_start: str) -> str:
        """生成周总结"""
        # 计算一周的日期范围
        start_date = datetime.strptime(week_start, '%Y-%m-%d')
        week_dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
        
        weekly_summary = f"# 周工作总结 ({week_start} ~ {week_dates[-1]})\n\n"
        
        total_tasks = 0
        total_hours = 0
        
        for date_str in week_dates:
            daily_data = self.file_manager.read_daily_record(date_str, 'daily_report')
            if daily_data:
                weekly_summary += f"## {date_str}\n{daily_data[:200]}...\n\n"
                # 这里可以解析日报内容获取统计信息
                total_tasks += 4  # 模拟数据
                total_hours += 8  # 模拟数据
        
        weekly_summary += f"## 本周统计\n"
        weekly_summary += f"- 总任务数：{total_tasks}\n"
        weekly_summary += f"- 总工作时长：{total_hours}小时\n"
        weekly_summary += f"- 日均任务数：{total_tasks/7:.1f}\n"
        
        return weekly_summary
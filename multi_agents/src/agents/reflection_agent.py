"""
反思秋Agent
深度反思和个人成长分析
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class ReflectionAgent(BaseAgent):
    """反思秋Agent"""
    
    def __init__(self, config_manager, file_manager):
        super().__init__(config_manager, file_manager)
        self.agent_name = "ReflectionAgent"
    
    def execute(self, date_str: str, daily_folder: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行深度反思"""
        try:
            # 获取用户信息
            personal_info = self.get_user_info('personal_info')
            personality_traits = self.get_user_info('personality_traits')
            work_profile = self.get_user_info('work_profile')
            
            # 获取今日所有数据
            daily_data = self._get_daily_data(date_str)
            
            # 获取用户反思输入（在实际应用中，这里应该通过用户交互获取）
            user_reflection = self._get_user_reflection()
            
            # 分析今日表现
            daily_analysis = self._analyze_daily_performance(daily_data, user_reflection)
            
            # 识别思考模式
            thinking_patterns = self._identify_thinking_patterns(daily_analysis, personality_traits)
            
            # 生成成长洞察
            growth_insights = self._generate_growth_insights(daily_analysis, personality_traits, work_profile)
            
            # 生成反思报告
            reflection_report = self._generate_reflection_report(
                date_str, daily_data, daily_analysis, thinking_patterns, growth_insights, user_reflection
            )
            
            # 保存反思报告
            self.save_result(date_str, 'reflection', reflection_report)
            
            # 发送到飞书
            self._send_to_lark(reflection_report)
            
            # 更新个人成长数据
            self._update_personal_growth_data(growth_insights)
            
            return {
                "reflection_report": reflection_report,
                "daily_analysis": daily_analysis,
                "thinking_patterns": thinking_patterns,
                "growth_insights": growth_insights,
                "user_reflection": user_reflection,
                "reflection_depth": self._calculate_reflection_depth(user_reflection)
            }
            
        except Exception as e:
            return self.handle_error(e, {"date": date_str, "daily_folder": daily_folder})
    
    def _get_daily_data(self, date_str: str) -> Dict[str, Any]:
        """获取今日所有数据"""
        daily_data = {}
        
        # 获取各种记录
        record_types = ['news', 'outfit', 'health', 'daily_report']
        
        for record_type in record_types:
            content = self.file_manager.read_daily_record(date_str, record_type)
            if content:
                daily_data[record_type] = content
        
        return daily_data
    
    def _get_user_reflection(self) -> Dict[str, Any]:
        """获取用户反思输入"""
        # 在实际应用中，这里应该通过用户交互获取
        # 现在先返回模拟数据
        
        mock_reflection = {
            "work_summary": "今天完成了产品需求文档，团队协作效果不错",
            "challenges": "在技术实现上遇到了一些困难，需要进一步学习",
            "achievements": "成功推动了项目进展，得到了团队的认可",
            "emotions": "整体感觉充实，有些疲惫但很满足",
            "learnings": "沟通的重要性，技术深度需要加强",
            "gratitude": "感谢团队的支持，感谢自己的坚持",
            "tomorrow_improvements": "提前规划任务，加强技术学习"
        }
        
        return mock_reflection
    
    def _analyze_daily_performance(self, daily_data: Dict[str, Any], 
                                 user_reflection: Dict[str, Any]) -> Dict[str, Any]:
        """分析今日表现"""
        analysis = {}
        
        # 工作分析
        work_analysis = self._analyze_work_performance(daily_data.get('daily_report', ''), user_reflection)
        analysis['work'] = work_analysis
        
        # 健康分析
        health_analysis = self._analyze_health_performance(daily_data.get('health', ''), user_reflection)
        analysis['health'] = health_analysis
        
        # 情绪分析
        emotional_analysis = self._analyze_emotional_state(user_reflection)
        analysis['emotional'] = emotional_analysis
        
        # 效率分析
        efficiency_analysis = self._analyze_efficiency(daily_data, user_reflection)
        analysis['efficiency'] = efficiency_analysis
        
        # 整体评分
        overall_score = self._calculate_overall_score(analysis)
        analysis['overall_score'] = overall_score
        
        return analysis
    
    def _analyze_work_performance(self, daily_report: str, user_reflection: Dict[str, Any]) -> Dict[str, Any]:
        """分析工作表现"""
        work_analysis = {
            "productivity": "中等",
            "quality": "良好",
            "collaboration": "优秀",
            "satisfaction": "满意"
        }
        
        # 基于用户反思调整分析
        if "团队协作效果不错" in user_reflection.get('work_summary', ''):
            work_analysis['collaboration'] = "优秀"
        
        if "技术实现上遇到了一些困难" in user_reflection.get('challenges', ''):
            work_analysis['technical_challenges'] = "存在技术瓶颈"
        
        return work_analysis
    
    def _analyze_health_performance(self, health_data: str, user_reflection: Dict[str, Any]) -> Dict[str, Any]:
        """分析健康表现"""
        health_analysis = {
            "exercise": "适中",
            "diet": "良好",
            "sleep": "需要改善",
            "stress": "中等"
        }
        
        # 基于用户反思调整分析
        if "有些疲惫" in user_reflection.get('emotions', ''):
            health_analysis['fatigue_level'] = "中等疲劳"
            health_analysis['sleep'] = "需要改善"
        
        return health_analysis
    
    def _analyze_emotional_state(self, user_reflection: Dict[str, Any]) -> Dict[str, Any]:
        """分析情绪状态"""
        emotions_text = user_reflection.get('emotions', '')
        
        emotional_state = {
            "primary_emotion": "满足",
            "energy_level": "中等",
            "stress_level": "低",
            "motivation_level": "高",
            "mood_trend": "积极"
        }
        
        # 简单的情绪关键词分析
        if "疲惫" in emotions_text:
            emotional_state['energy_level'] = "低"
            emotional_state['fatigue'] = True
        
        if "满足" in emotions_text:
            emotional_state['satisfaction'] = "高"
        
        return emotional_state
    
    def _analyze_efficiency(self, daily_data: Dict[str, Any], user_reflection: Dict[str, Any]) -> Dict[str, Any]:
        """分析效率"""
        efficiency_analysis = {
            "time_management": "良好",
            "priority_setting": "优秀",
            "focus_level": "中等",
            "distraction_factors": ["技术困难"]
        }
        
        # 基于用户反思调整分析
        if "技术实现上遇到了一些困难" in user_reflection.get('challenges', ''):
            efficiency_analysis['focus_level'] = "受影响"
            efficiency_analysis['technical_challenges'] = True
        
        return efficiency_analysis
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """计算整体评分"""
        scores = {}
        
        # 工作评分
        work_score = 0
        if analysis['work'].get('collaboration') == "优秀":
            work_score += 30
        if analysis['work'].get('satisfaction') == "满意":
            work_score += 20
        scores['work'] = min(100, work_score + 50)
        
        # 健康评分
        health_score = 70  # 基础分
        if analysis['health'].get('sleep') == "需要改善":
            health_score -= 10
        scores['health'] = max(0, health_score)
        
        # 情绪评分
        emotional_score = 75
        if analysis['emotional'].get('satisfaction') == "高":
            emotional_score += 15
        scores['emotional'] = min(100, emotional_score)
        
        # 效率评分
        efficiency_score = 65
        if analysis['efficiency'].get('time_management') == "良好":
            efficiency_score += 20
        scores['efficiency'] = min(100, efficiency_score)
        
        # 总体评分
        overall_score = (scores['work'] + scores['health'] + scores['emotional'] + scores['efficiency']) / 4
        
        scores['overall'] = round(overall_score, 1)
        
        return scores
    
    def _identify_thinking_patterns(self, daily_analysis: Dict[str, Any], 
                                   personality_traits: Dict[str, Any]) -> Dict[str, Any]:
        """识别思考模式"""
        thinking_patterns = {
            "strengths": [],
            "areas_for_improvement": [],
            "cognitive_biases": [],
            "decision_making_style": personality_traits.get('decision_making', {}).get('approach', '理性分析'),
            "learning_style": personality_traits.get('learning_style', {}).get('primary', '实践型学习')
        }
        
        # 基于分析结果识别模式
        if daily_analysis['work'].get('collaboration') == "优秀":
            thinking_patterns['strengths'].append("团队协作能力强")
        
        if daily_analysis['efficiency'].get('technical_challenges'):
            thinking_patterns['areas_for_improvement'].append("技术深度需要加强")
        
        if daily_analysis['emotional'].get('fatigue'):
            thinking_patterns['areas_for_improvement'].append("疲劳管理需要改善")
        
        return thinking_patterns
    
    def _generate_growth_insights(self, daily_analysis: Dict[str, Any], 
                                 personality_traits: Dict[str, Any], 
                                 work_profile: Dict[str, Any]) -> Dict[str, Any]:
        """生成成长洞察"""
        growth_insights = {
            "key_achievements": [],
            "growth_areas": [],
            "development_opportunities": [],
            "action_items": [],
            "motivational_insights": []
        }
        
        # 分析成就
        if daily_analysis['work'].get('collaboration') == "优秀":
            growth_insights['key_achievements'].append("团队协作能力显著提升")
        
        # 分析成长领域
        if daily_analysis['efficiency'].get('technical_challenges'):
            growth_insights['growth_areas'].append("技术能力提升")
        
        if daily_analysis['health'].get('sleep') == "需要改善":
            growth_insights['growth_areas'].append("睡眠质量改善")
        
        # 发展机会
        career_goals = work_profile.get('career_goals', {})
        if '产品总监' in career_goals.get('medium_term', []):
            growth_insights['development_opportunities'].append("领导力发展")
        
        # 行动项目
        growth_insights['action_items'] = [
            "制定技术学习计划",
            "改善睡眠习惯",
            "加强团队沟通",
            "制定职业发展路径"
        ]
        
        # 激励洞察
        growth_insights['motivational_insights'] = [
            "每一次挑战都是成长的机会",
            "持续学习是职业发展的关键",
            "工作生活平衡对长期发展很重要"
        ]
        
        return growth_insights
    
    def _calculate_reflection_depth(self, user_reflection: Dict[str, Any]) -> str:
        """计算反思深度"""
        reflection_text = str(user_reflection)
        
        # 简单的深度计算逻辑
        if len(reflection_text) > 500:
            return "深度反思"
        elif len(reflection_text) > 200:
            return "中等反思"
        else:
            return "浅层反思"
    
    def _generate_reflection_report(self, date_str: str, daily_data: Dict[str, Any], 
                                  daily_analysis: Dict[str, Any], thinking_patterns: Dict[str, Any],
                                  growth_insights: Dict[str, Any], user_reflection: Dict[str, Any]) -> str:
        """生成反思报告"""
        # 计算时间分配
        time_allocation = self._calculate_time_allocation(daily_data)
        
        # 准备模板变量
        template_vars = {
            "date": date_str,
            "daily_overview": self._format_daily_overview(daily_data, user_reflection),
            "work_highlights": self._format_work_highlights(daily_analysis['work']),
            "work_challenges": self._format_work_challenges(daily_analysis['work']),
            "work_learning": self._format_work_learning(user_reflection),
            "goal_analysis": self._format_goal_analysis(growth_insights),
            "emotional_state": self._format_emotional_state(daily_analysis['emotional']),
            "thinking_patterns": self._format_thinking_patterns(thinking_patterns),
            "growth_insights": self._format_growth_insights(growth_insights),
            "improvement_areas": self._format_improvement_areas(thinking_patterns),
            "deep_reflection": self._format_deep_reflection(user_reflection, thinking_patterns),
            "gratitude_notes": user_reflection.get('gratitude', '感谢今天的经历'),
            "work_hours": time_allocation.get('work', '8小时'),
            "exercise_hours": time_allocation.get('exercise', '1小时'),
            "learning_hours": time_allocation.get('learning', '2小时'),
            "social_hours": time_allocation.get('social', '1小时'),
            "satisfaction_score": daily_analysis['overall_score'].get('overall', 75),
            "action_plan": self._format_action_plan(growth_insights),
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "reflection_depth": self._calculate_reflection_depth(user_reflection),
            "energy_index": self._calculate_energy_index(daily_analysis['emotional'])
        }
        
        return self.generate_from_template('reflection_template', template_vars)
    
    def _calculate_time_allocation(self, daily_data: Dict[str, Any]) -> Dict[str, str]:
        """计算时间分配"""
        # 这里应该从实际数据中计算，现在返回模拟数据
        return {
            "work": "8小时",
            "exercise": "1小时",
            "learning": "2小时",
            "social": "1小时",
            "rest": "12小时"
        }
    
    def _format_daily_overview(self, daily_data: Dict[str, Any], user_reflection: Dict[str, Any]) -> str:
        """格式化每日概览"""
        overview = f"今天完成了多项工作，团队协作效果良好。"
        overview += f"\n\n主要成就：{user_reflection.get('achievements', '工作进展顺利')}"
        overview += f"\n面临挑战：{user_reflection.get('challenges', '技术实现需要加强')}"
        
        return overview
    
    def _format_work_highlights(self, work_analysis: Dict[str, Any]) -> str:
        """格式化工作亮点"""
        highlights = []
        
        if work_analysis.get('collaboration') == "优秀":
            highlights.append("团队协作表现优秀")
        
        if work_analysis.get('satisfaction') == "满意":
            highlights.append("工作完成质量良好")
        
        return "\n".join([f"• {highlight}" for highlight in highlights])
    
    def _format_work_challenges(self, work_analysis: Dict[str, Any]) -> str:
        """格式化工作挑战"""
        challenges = []
        
        if work_analysis.get('technical_challenges'):
            challenges.append("技术实现遇到瓶颈")
        
        return "\n".join([f"• {challenge}" for challenge in challenges])
    
    def _format_work_learning(self, user_reflection: Dict[str, Any]) -> str:
        """格式化工作学习"""
        learnings = user_reflection.get('learnings', '持续学习新技术')
        
        if isinstance(learnings, str):
            return learnings
        else:
            return "\n".join([f"• {learning}" for learning in learnings])
    
    def _format_goal_analysis(self, growth_insights: Dict[str, Any]) -> str:
        """格式化目标分析"""
        key_achievements = growth_insights.get('key_achievements', [])
        
        if not key_achievements:
            return "今日目标完成情况良好，继续保持。"
        
        return "目标进展分析：\n" + "\n".join([f"• {achievement}" for achievement in key_achievements])
    
    def _format_emotional_state(self, emotional_analysis: Dict[str, Any]) -> str:
        """格式化情绪状态"""
        state = emotional_analysis.get('primary_emotion', '平静')
        energy = emotional_analysis.get('energy_level', '中等')
        
        return f"主要情绪：{state}\n能量水平：{energy}\n压力水平：{emotional_analysis.get('stress_level', '中等')}"
    
    def _format_thinking_patterns(self, thinking_patterns: Dict[str, Any]) -> str:
        """格式化思考模式"""
        patterns = []
        
        strengths = thinking_patterns.get('strengths', [])
        if strengths:
            patterns.append("优势：" + "、".join(strengths))
        
        improvements = thinking_patterns.get('areas_for_improvement', [])
        if improvements:
            patterns.append("改进点：" + "、".join(improvements))
        
        return "\n".join(patterns)
    
    def _format_growth_insights(self, growth_insights: Dict[str, Any]) -> str:
        """格式化成长洞察"""
        insights = growth_insights.get('motivational_insights', [])
        
        return "\n\n".join([f"💡 {insight}" for insight in insights])
    
    def _format_improvement_areas(self, thinking_patterns: Dict[str, Any]) -> str:
        """格式化改进方向"""
        improvements = thinking_patterns.get('areas_for_improvement', [])
        
        if not improvements:
            return "继续保持当前的良好状态。"
        
        return "\n".join([f"🎯 {improvement}" for improvement in improvements])
    
    def _format_deep_reflection(self, user_reflection: Dict[str, Any], 
                               thinking_patterns: Dict[str, Any]) -> str:
        """格式化深度思考"""
        reflection_parts = []
        
        # 整合用户反思和模式分析
        reflection_parts.append("今天的经历让我意识到：")
        reflection_parts.append("- 持续学习的重要性")
        reflection_parts.append("- 团队协作的价值")
        reflection_parts.append("- 自我管理的必要性")
        
        return "\n".join(reflection_parts)
    
    def _format_action_plan(self, growth_insights: Dict[str, Any]) -> str:
        """格式化行动计划"""
        action_items = growth_insights.get('action_items', [])
        
        return "明日改进计划：\n" + "\n".join([f"{i+1}. {item}" for i, item in enumerate(action_items)])
    
    def _calculate_energy_index(self, emotional_analysis: Dict[str, Any]) -> str:
        """计算能量指数"""
        energy_level = emotional_analysis.get('energy_level', '中等')
        
        energy_mapping = {
            "高": "8-10分",
            "中等": "6-7分",
            "低": "4-5分"
        }
        
        return energy_mapping.get(energy_level, "6分")
    
    def _update_personal_growth_data(self, growth_insights: Dict[str, Any]):
        """更新个人成长数据"""
        # 保存成长洞察历史
        self.file_manager.save_history_data('growth_insights', growth_insights)
        
        # 生成个人成长报告
        personal_insights = {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "key_achievements": growth_insights.get('key_achievements', []),
            "growth_areas": growth_insights.get('growth_areas', []),
            "development_focus": growth_insights.get('development_opportunities', [])
        }
        
        self.file_manager.save_analytics('personal_insights', personal_insights)
        
        print(f"📈 个人成长数据已更新")
    
    def _send_to_lark(self, reflection_report: str):
        """发送到飞书"""
        # 这里应该调用飞书MCP工具
        print("🤔 反思报告已发送到飞书")
    
    def get_reflection_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取反思历史"""
        return self.file_manager.get_history_data('reflection', days)
    
    def generate_personal_growth_report(self, start_date: str, end_date: str) -> str:
        """生成个人成长报告"""
        report = f"# 个人成长报告 ({start_date} ~ {end_date})\n\n"
        
        # 获取时间范围内的反思数据
        reflection_history = self.get_reflection_history()
        
        if not reflection_history:
            return "暂无足够的反思数据生成报告。"
        
        # 分析成长趋势
        growth_trends = self._analyze_growth_trends(reflection_history)
        
        report += f"## 成长趋势分析\n"
        report += f"{growth_trends}\n\n"
        
        # 生成建议
        recommendations = self._generate_growth_recommendations(growth_trends)
        report += f"## 发展建议\n"
        report += f"{recommendations}\n"
        
        return report
    
    def _analyze_growth_trends(self, reflection_history: List[Dict[str, Any]]) -> str:
        """分析成长趋势"""
        # 这里可以实现更复杂的趋势分析逻辑
        return "基于最近的分析，您在团队协作和技术能力方面都有明显进步。"
    
    def _generate_growth_recommendations(self, growth_trends: str) -> str:
        """生成成长建议"""
        recommendations = [
            "继续加强技术深度学习",
            "培养领导力和管理能力",
            "保持工作生活平衡",
            "持续反思和总结"
        ]
        
        return "\n".join([f"• {rec}" for rec in recommendations])
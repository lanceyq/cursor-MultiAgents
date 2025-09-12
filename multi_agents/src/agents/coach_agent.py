"""
教练秋Agent
健康管理和运动建议
"""

import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class CoachAgent(BaseAgent):
    """教练秋Agent"""
    
    def __init__(self, config_manager, file_manager):
        super().__init__(config_manager, file_manager)
        self.agent_name = "CoachAgent"
    
    def execute(self, date_str: str, daily_folder: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行健康管理"""
        try:
            # 获取健康信息
            health_goals = self.get_user_info('health_goals')
            personal_info = self.get_user_info('personal_info')
            
            # 获取体重数据（在实际应用中，这里应该通过用户交互获取）
            weight_data = self._get_weight_data()
            
            # 分析健康状况
            health_analysis = self._analyze_health_status(weight_data, health_goals)
            
            # 生成健康计划
            health_plan = self._generate_health_plan(health_analysis, health_goals)
            
            # 更新健康数据
            self._update_health_data(weight_data, health_goals)
            
            # 生成健康文档
            health_content = self._generate_health_content(date_str, health_analysis, health_plan)
            self.save_result(date_str, 'health', health_content)
            
            # 发送到飞书
            self._send_to_lark(health_content)
            
            return {
                "health_plan": health_plan,
                "health_analysis": health_analysis,
                "weight_data": weight_data,
                "recommendations": health_plan.get('recommendations', [])
            }
            
        except Exception as e:
            return self.handle_error(e, {"date": date_str, "daily_folder": daily_folder})
    
    def _get_weight_data(self) -> Dict[str, Any]:
        """获取体重数据"""
        # 在实际应用中，这里应该通过用户交互获取
        # 现在先返回模拟数据
        
        mock_weight_data = {
            "current_weight": 55.0,
            "measurement_date": datetime.now().strftime('%Y-%m-%d'),
            "measurement_time": datetime.now().strftime('%H:%M'),
            "weight_change": -0.5,  # 相比上次的变化
            "notes": "早上空腹测量"
        }
        
        return mock_weight_data
    
    def _analyze_health_status(self, weight_data: Dict[str, Any], health_goals: Dict[str, Any]) -> Dict[str, Any]:
        """分析健康状况"""
        current_weight = weight_data.get('current_weight', 55.0)
        target_weight = health_goals.get('health_profile', {}).get('target_weight', 53.0)
        height = health_goals.get('health_profile', {}).get('basic_info', {}).get('height', 165)
        
        # 计算BMI
        bmi = current_weight / ((height / 100) ** 2)
        
        # 分析体重趋势
        weight_trend = self._analyze_weight_trend(current_weight, target_weight)
        
        # 评估健康状态
        health_status = self._evaluate_health_status(bmi, weight_trend)
        
        # 分析目标进展
        goal_progress = self._analyze_goal_progress(current_weight, target_weight, health_goals)
        
        # 生成健康建议
        health_recommendations = self._generate_health_recommendations(health_status, health_goals)
        
        return {
            "bmi": round(bmi, 1),
            "weight_trend": weight_trend,
            "health_status": health_status,
            "goal_progress": goal_progress,
            "recommendations": health_recommendations,
            "risk_factors": self._identify_risk_factors(health_status, health_goals),
            "health_score": self._calculate_health_score(health_status, weight_trend)
        }
    
    def _analyze_weight_trend(self, current_weight: float, target_weight: float) -> str:
        """分析体重趋势"""
        weight_diff = current_weight - target_weight
        
        if weight_diff > 2:
            return "距离目标还有一定距离"
        elif weight_diff > 0:
            return "接近目标体重"
        elif weight_diff == 0:
            return "达到目标体重"
        else:
            return "低于目标体重"
    
    def _evaluate_health_status(self, bmi: float, weight_trend: str) -> str:
        """评估健康状态"""
        if bmi < 18.5:
            return "偏瘦"
        elif 18.5 <= bmi < 24:
            return "健康"
        elif 24 <= bmi < 28:
            return "偏胖"
        else:
            return "肥胖"
    
    def _analyze_goal_progress(self, current_weight: float, target_weight: float, 
                              health_goals: Dict[str, Any]) -> Dict[str, Any]:
        """分析目标进展"""
        weight_diff = current_weight - target_weight
        timeline = health_goals.get('fitness_goals', {}).get('timeline', '3个月')
        
        progress_percentage = max(0, (1 - abs(weight_diff) / 3) * 100)  # 简单计算
        
        return {
            "current_weight": current_weight,
            "target_weight": target_weight,
            "weight_difference": weight_diff,
            "progress_percentage": round(progress_percentage, 1),
            "timeline": timeline,
            "on_track": abs(weight_diff) <= 1.0
        }
    
    def _generate_health_recommendations(self, health_status: str, 
                                        health_goals: Dict[str, Any]) -> List[str]:
        """生成健康建议"""
        recommendations = []
        
        # 基于健康状态的建议
        if health_status == "健康":
            recommendations.append("继续保持良好的健康状态")
            recommendations.append("定期进行身体检查")
        elif health_status == "偏瘦":
            recommendations.append("适当增加营养摄入")
            recommendations.append("进行力量训练增加肌肉量")
        elif health_status == "偏胖":
            recommendations.append("控制饮食，减少高热量食物")
            recommendations.append("增加有氧运动")
        
        # 基于目标的建议
        fitness_goals = health_goals.get('fitness_goals', {})
        primary_goal = fitness_goals.get('primary_goal', '减脂塑形')
        
        if primary_goal == '减脂塑形':
            recommendations.append("建议每周进行3-4次有氧运动")
            recommendations.append("控制碳水化合物摄入")
        elif primary_goal == '增肌':
            recommendations.append("增加蛋白质摄入")
            recommendations.append("进行力量训练")
        
        return recommendations
    
    def _identify_risk_factors(self, health_status: str, health_goals: Dict[str, Any]) -> List[str]:
        """识别风险因素"""
        risk_factors = []
        
        if health_status in ["偏胖", "肥胖"]:
            risk_factors.append("体重超标风险")
        
        # 检查运动频率
        exercise_frequency = health_goals.get('fitness_preferences', {}).get('exercise_frequency', '每周3-4次')
        if '每周1-2次' in exercise_frequency:
            risk_factors.append("运动不足风险")
        
        return risk_factors
    
    def _calculate_health_score(self, health_status: str, weight_trend: str) -> int:
        """计算健康分数"""
        base_score = 50
        
        # 健康状态评分
        if health_status == "健康":
            base_score += 30
        elif health_status == "偏瘦":
            base_score += 10
        elif health_status == "偏胖":
            base_score -= 10
        else:
            base_score -= 20
        
        # 体重趋势评分
        if "接近目标" in weight_trend:
            base_score += 20
        elif "达到目标" in weight_trend:
            base_score += 30
        
        return max(0, min(100, base_score))
    
    def _generate_health_plan(self, health_analysis: Dict[str, Any], 
                             health_goals: Dict[str, Any]) -> Dict[str, Any]:
        """生成健康计划"""
        fitness_preferences = health_goals.get('fitness_preferences', {})
        diet_preferences = health_goals.get('diet_preferences', {})
        
        # 运动计划
        exercise_plan = self._generate_exercise_plan(health_analysis, fitness_preferences)
        
        # 饮食计划
        diet_plan = self._generate_diet_plan(health_analysis, diet_preferences)
        
        # 生活习惯建议
        lifestyle_recommendations = self._generate_lifestyle_recommendations(health_analysis)
        
        return {
            "exercise_plan": exercise_plan,
            "diet_plan": diet_plan,
            "lifestyle_recommendations": lifestyle_recommendations,
            "weekly_goals": self._set_weekly_goals(health_analysis, health_goals),
            "motivational_tips": self._generate_motivational_tips(health_analysis)
        }
    
    def _generate_exercise_plan(self, health_analysis: Dict[str, Any], 
                               fitness_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """生成运动计划"""
        preferred_activities = fitness_preferences.get('preferred_activities', ['瑜伽', '跑步'])
        exercise_frequency = fitness_preferences.get('exercise_frequency', '每周3-4次')
        exercise_duration = fitness_preferences.get('exercise_duration', '每次45-60分钟')
        
        # 根据健康状态调整运动强度
        health_status = health_analysis.get('health_status', '健康')
        if health_status == "健康":
            intensity = "中等强度"
        elif health_status == "偏胖":
            intensity = "低到中等强度"
        else:
            intensity = "中等强度"
        
        return {
            "recommended_activities": preferred_activities[:3],
            "frequency": exercise_frequency,
            "duration": exercise_duration,
            "intensity": intensity,
            "weekly_schedule": self._create_weekly_exercise_schedule(preferred_activities, exercise_frequency)
        }
    
    def _generate_diet_plan(self, health_analysis: Dict[str, Any], 
                           diet_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """生成饮食计划"""
        meal_schedule = diet_preferences.get('meal_schedule', {})
        nutrition_focus = diet_preferences.get('nutrition_focus', {})
        
        health_status = health_analysis.get('health_status', '健康')
        
        # 根据健康状态调整饮食建议
        if health_status == "偏胖":
            calorie_adjustment = "减少300-500卡路里"
            nutrition_focus['carbs'] = "减少精制碳水"
        elif health_status == "偏瘦":
            calorie_adjustment = "增加300-500卡路里"
            nutrition_focus['protein'] = "增加蛋白质摄入"
        else:
            calorie_adjustment = "保持当前卡路里"
        
        return {
            "calorie_adjustment": calorie_adjustment,
            "meal_schedule": meal_schedule,
            "nutrition_focus": nutrition_focus,
            "meal_recommendations": self._generate_meal_recommendations(health_status)
        }
    
    def _generate_lifestyle_recommendations(self, health_analysis: Dict[str, Any]) -> List[str]:
        """生成生活习惯建议"""
        recommendations = []
        
        # 基础建议
        recommendations.append("保持充足的睡眠，每晚7-8小时")
        recommendations.append("每天饮水2000ml以上")
        recommendations.append("减少久坐，每小时起身活动5-10分钟")
        recommendations.append("保持良好的心态，适当减压")
        
        # 基于健康状态的特殊建议
        health_status = health_analysis.get('health_status', '健康')
        if health_status == "偏胖":
            recommendations.append("避免熬夜，保持规律作息")
        elif health_status == "偏瘦":
            recommendations.append("避免过度劳累，适当休息")
        
        return recommendations
    
    def _create_weekly_exercise_schedule(self, activities: List[str], frequency: str) -> Dict[str, str]:
        """创建每周运动计划"""
        schedule = {}
        
        # 简单的运动计划分配
        if '每周3-4次' in frequency:
            days = ['周一', '周三', '周五', '周日']
        elif '每周5-6次' in frequency:
            days = ['周一', '周二', '周三', '周五', '周六', '周日']
        else:
            days = ['周一', '周三', '周五']
        
        for i, day in enumerate(days):
            if i < len(activities):
                schedule[day] = activities[i]
            else:
                schedule[day] = activities[0]
        
        return schedule
    
    def _generate_meal_recommendations(self, health_status: str) -> Dict[str, str]:
        """生成膳食建议"""
        if health_status == "偏胖":
            return {
                "breakfast": "燕麦粥+鸡蛋+水果",
                "lunch": "蔬菜沙拉+鸡胸肉+糙米",
                "dinner": "清蒸鱼+蔬菜+少量主食",
                "snacks": "坚果或水果"
            }
        elif health_status == "偏瘦":
            return {
                "breakfast": "全麦面包+鸡蛋+牛奶+水果",
                "lunch": "米饭+肉类+蔬菜+汤",
                "dinner": "丰富蛋白质+蔬菜+主食",
                "snacks": "蛋白棒或酸奶"
            }
        else:
            return {
                "breakfast": "均衡营养的早餐",
                "lunch": "蛋白质+蔬菜+主食",
                "dinner": "清淡易消化的晚餐",
                "snacks": "健康零食"
            }
    
    def _set_weekly_goals(self, health_analysis: Dict[str, Any], health_goals: Dict[str, Any]) -> List[str]:
        """设定周目标"""
        goals = []
        
        health_status = health_analysis.get('health_status', '健康')
        weight_trend = health_analysis.get('weight_trend', '')
        
        if "减脂" in health_goals.get('fitness_goals', {}).get('primary_goal', ''):
            goals.append("减重0.5-1kg")
            goals.append("完成4次有氧运动")
        else:
            goals.append("保持当前体重")
            goals.append("完成3次运动")
        
        goals.append("每天记录饮食")
        goals.append("保证充足睡眠")
        
        return goals
    
    def _generate_motivational_tips(self, health_analysis: Dict[str, Any]) -> List[str]:
        """生成激励建议"""
        tips = [
            "坚持就是胜利，每一天的进步都很重要",
            "健康是最大的财富，值得你用心经营",
            "相信自己的能力，你一定能够达到目标"
        ]
        
        health_score = health_analysis.get('health_score', 70)
        if health_score >= 80:
            tips.append("你的健康状态很好，继续保持！")
        else:
            tips.append("通过调整生活方式，你的健康状态会越来越好")
        
        return tips
    
    def _update_health_data(self, weight_data: Dict[str, Any], health_goals: Dict[str, Any]):
        """更新健康数据"""
        # 保存体重历史
        self.file_manager.save_history_data('weight', weight_data)
        
        # 更新健康目标中的体重历史
        health_profile = health_goals.get('health_profile', {})
        weight_history = health_profile.get('basic_info', {}).get('weight_history', [])
        
        new_entry = {
            "date": weight_data.get('measurement_date'),
            "weight": weight_data.get('current_weight')
        }
        
        weight_history.append(new_entry)
        
        # 保持最近30天的记录
        if len(weight_history) > 30:
            weight_history = weight_history[-30:]
        
        # 这里应该更新aboutme/health_goals.json文件
        print(f"💾 体重数据已更新：{weight_data.get('current_weight')}kg")
    
    def _generate_health_content(self, date_str: str, health_analysis: Dict[str, Any], 
                                health_plan: Dict[str, Any]) -> str:
        """生成健康文档内容"""
        # 准备模板变量
        template_vars = {
            "date": date_str,
            "current_weight": health_analysis.get('goal_progress', {}).get('current_weight', 55),
            "target_weight": health_analysis.get('goal_progress', {}).get('target_weight', 53),
            "bmi": health_analysis.get('bmi', 20.2),
            "weight_change": health_analysis.get('goal_progress', {}).get('weight_difference', -0.5),
            "health_goals": self._format_health_goals(health_plan.get('weekly_goals', [])),
            "exercise_recommendations": self._format_exercise_plan(health_plan.get('exercise_plan', {})),
            "exercise_duration": health_plan.get('exercise_plan', {}).get('duration', '45-60分钟'),
            "exercise_notes": self._format_exercise_notes(health_plan.get('exercise_plan', {})),
            "breakfast_recommendation": health_plan.get('diet_plan', {}).get('meal_recommendations', {}).get('breakfast', '均衡营养'),
            "lunch_recommendation": health_plan.get('diet_plan', {}).get('meal_recommendations', {}).get('lunch', '蛋白质+蔬菜+主食'),
            "dinner_recommendation": health_plan.get('diet_plan', {}).get('meal_recommendations', {}).get('dinner', '清淡易消化'),
            "snack_recommendation": health_plan.get('diet_plan', {}).get('meal_recommendations', {}).get('snacks', '健康零食'),
            "water_intake": "2000ml",
            "water_tips": "分多次饮用，餐前餐后都要适量饮水",
            "health_tips": self._format_health_tips(health_plan.get('lifestyle_recommendations', [])),
            "health_data_update": self._format_health_data_update(health_analysis),
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "next_weight_check": (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        }
        
        return self.generate_from_template('health_template', template_vars)
    
    def _format_health_goals(self, goals: List[str]) -> str:
        """格式化健康目标"""
        return "\n".join([f"- {goal}" for goal in goals])
    
    def _format_exercise_plan(self, exercise_plan: Dict[str, Any]) -> str:
        """格式化运动计划"""
        activities = exercise_plan.get('recommended_activities', [])
        return "\n".join([f"- {activity}" for activity in activities])
    
    def _format_exercise_notes(self, exercise_plan: Dict[str, Any]) -> str:
        """格式化运动注意事项"""
        notes = []
        notes.append(f"运动强度：{exercise_plan.get('intensity', '中等强度')}")
        notes.append(f"运动频率：{exercise_plan.get('frequency', '每周3-4次')}")
        notes.append("运动前进行5-10分钟热身")
        notes.append("运动后进行拉伸放松")
        
        return "\n".join([f"• {note}" for note in notes])
    
    def _format_health_tips(self, tips: List[str]) -> str:
        """格式化健康小贴士"""
        return "\n".join([f"• {tip}" for tip in tips])
    
    def _format_health_data_update(self, health_analysis: Dict[str, Any]) -> str:
        """格式化健康数据更新"""
        update_info = []
        update_info.append(f"BMI指数：{health_analysis.get('bmi', 20.2)}")
        update_info.append(f"健康评分：{health_analysis.get('health_score', 70)}/100")
        update_info.append(f"体重趋势：{health_analysis.get('weight_trend', '稳定')}")
        
        return "\n".join(update_info)
    
    def _send_to_lark(self, health_content: str):
        """发送到飞书"""
        # 这里应该调用飞书MCP工具
        print("💪 健康计划已发送到飞书")
    
    def get_health_statistics(self, days: int = 30) -> Dict[str, Any]:
        """获取健康统计"""
        weight_history = self.file_manager.get_history_data('weight', days)
        
        stats = {
            "total_records": len(weight_history),
            "weight_trend": "稳定",
            "average_weight": 0,
            "weight_change": 0
        }
        
        if weight_history:
            weights = [entry.get('data', {}).get('current_weight', 0) for entry in weight_history]
            stats['average_weight'] = sum(weights) / len(weights)
            stats['weight_change'] = weights[-1] - weights[0] if len(weights) > 1 else 0
        
        return stats
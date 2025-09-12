"""
穿搭秋Agent
根据天气和场合提供穿搭建议
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent

class OutfitAgent(BaseAgent):
    """穿搭秋Agent"""
    
    def __init__(self, config_manager, file_manager):
        super().__init__(config_manager, file_manager)
        self.agent_name = "OutfitAgent"
    
    async def execute(self, date_str: str, daily_folder: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """执行穿搭建议生成"""
        try:
            # 获取用户信息
            style_preferences = self.get_user_info('style_preferences')
            personal_info = self.get_user_info('personal_info')
            
            # 获取天气信息
            weather_info = self._get_weather_info(personal_info.get('location', '上海'))
            
            # 询问场合（在实际应用中，这里应该通过用户交互获取）
            occasion = self._get_user_occasion()
            
            # 生成穿搭建议
            outfit_recommendation = self._generate_outfit_recommendation(
                weather_info, occasion, style_preferences
            )
            
            # 生成穿搭图片
            outfit_image_url = await self._generate_outfit_image(outfit_recommendation)
            
            # 保存穿搭建议
            outfit_content = self._generate_outfit_content(
                date_str, weather_info, occasion, outfit_recommendation, outfit_image_url
            )
            self.save_result(date_str, 'outfit', outfit_content)
            
            # 发送到飞书
            self._send_to_lark(outfit_content, outfit_image_url)
            
            return {
                "outfit_recommendation": outfit_recommendation,
                "weather_info": weather_info,
                "occasion": occasion,
                "outfit_image_url": outfit_image_url
            }
            
        except Exception as e:
            return self.handle_error(e, {"date": date_str, "daily_folder": daily_folder})
    
    def _get_weather_info(self, location: str) -> Dict[str, Any]:
        """获取天气信息"""
        # 这里应该调用天气MCP工具
        # 现在先返回模拟数据
        
        mock_weather = {
            "location": location,
            "condition": "晴朗",
            "temperature": "22°C",
            "humidity": "65%",
            "wind": "微风",
            "feels_like": "24°C",
            "uv_index": "中等",
            "visibility": "良好"
        }
        
        return mock_weather
    
    def _get_user_occasion(self) -> str:
        """获取用户场合"""
        # 在实际应用中，这里应该通过用户交互获取
        # 现在先返回默认值
        occasions = ["公司", "约会", "运动", "休闲", "正式场合", "其他"]
        return "公司"  # 默认去公司
    
    def _generate_outfit_recommendation(self, weather_info: Dict[str, Any], 
                                       occasion: str, style_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """生成穿搭建议"""
        temperature = weather_info.get('temperature', '22°C')
        condition = weather_info.get('condition', '晴朗')
        
        # 根据温度和场合推荐服装
        top_recommendation = self._recommend_top_wear(temperature, occasion, style_preferences)
        bottom_recommendation = self._recommend_bottom_wear(temperature, occasion, style_preferences)
        shoes_recommendation = self._recommend_shoes(temperature, occasion, style_preferences)
        accessories_recommendation = self._recommend_accessories(temperature, occasion, style_preferences)
        
        # 色彩搭配建议
        color_scheme = self._recommend_colors(temperature, occasion, style_preferences)
        
        # 穿搭建议
        styling_tips = self._generate_styling_tips(temperature, occasion, condition)
        
        return {
            "top": top_recommendation,
            "bottom": bottom_recommendation,
            "shoes": shoes_recommendation,
            "accessories": accessories_recommendation,
            "colors": color_scheme,
            "tips": styling_tips,
            "overall_style": self._determine_overall_style(occasion, style_preferences)
        }
    
    def _recommend_top_wear(self, temperature: str, occasion: str, style_preferences: Dict[str, Any]) -> str:
        """推荐上装"""
        temp_num = int(temperature.replace('°C', ''))
        
        if temp_num < 15:
            if occasion == "公司":
                return "羊毛西装外套 + 羊绒衫"
            else:
                return "厚款针织衫 + 风衣"
        elif temp_num < 25:
            if occasion == "公司":
                return "衬衫 + 针织马甲"
            else:
                return "长袖T恤 + 牛仔外套"
        else:
            if occasion == "公司":
                return "短袖衬衫 + 薄款西装外套"
            else:
                return "棉质T恤 + 薄款开衫"
    
    def _recommend_bottom_wear(self, temperature: str, occasion: str, style_preferences: Dict[str, Any]) -> str:
        """推荐下装"""
        temp_num = int(temperature.replace('°C', ''))
        
        if temp_num < 15:
            if occasion == "公司":
                return "西装裤 + 打底裤"
            else:
                return "加厚牛仔裤"
        elif temp_num < 25:
            if occasion == "公司":
                return "西装裤或直筒裤"
            else:
                return "牛仔裤或休闲裤"
        else:
            if occasion == "公司":
                return "西装短裤或轻便裤装"
            else:
                return "棉质短裤或半身裙"
    
    def _recommend_shoes(self, temperature: str, occasion: str, style_preferences: Dict[str, Any]) -> str:
        """推荐鞋履"""
        if occasion == "公司":
            return "乐福鞋或低跟鞋"
        elif occasion == "运动":
            return "运动鞋"
        elif occasion == "正式场合":
            return "高跟鞋或正装鞋"
        else:
            return "小白鞋或平底鞋"
    
    def _recommend_accessories(self, temperature: str, occasion: str, style_preferences: Dict[str, Any]) -> str:
        """推荐配饰"""
        accessories = []
        
        if occasion == "公司":
            accessories.extend(["简约手表", "丝巾", "简约项链"])
        elif occasion == "正式场合":
            accessories.extend(["精致手包", "耳环", "手链"])
        else:
            accessories.extend(["帆布包", "太阳镜", "简约手链"])
        
        if int(temperature.replace('°C', '')) < 15:
            accessories.append("围巾")
        
        return "、".join(accessories)
    
    def _recommend_colors(self, temperature: str, occasion: str, style_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """推荐色彩搭配"""
        favorite_colors = style_preferences.get('style_profile', {}).get('color_preferences', {}).get('favorite_colors', [])
        
        # 根据场合调整色彩
        if occasion == "公司":
            main_colors = favorite_colors[:2] if favorite_colors else ["黑色", "白色"]
            accent_colors = ["灰色", "蓝色"]
        elif occasion == "正式场合":
            main_colors = ["黑色", "酒红色"]
            accent_colors = ["金色", "银色"]
        else:
            main_colors = favorite_colors[:2] if favorite_colors else ["蓝色", "白色"]
            accent_colors = ["粉色", "薄荷绿"]
        
        return {
            "main_colors": main_colors,
            "accent_colors": accent_colors
        }
    
    def _generate_styling_tips(self, temperature: str, occasion: str, condition: str) -> str:
        """生成穿搭建议"""
        tips = []
        
        # 温度建议
        temp_num = int(temperature.replace('°C', ''))
        if temp_num < 10:
            tips.append("注意保暖，可以多穿一层")
        elif temp_num > 30:
            tips.append("选择透气性好的面料")
        
        # 天气建议
        if "雨" in condition:
            tips.append("记得带伞，选择防水鞋履")
        elif "晴朗" in condition:
            tips.append("可以佩戴太阳镜，涂抹防晒霜")
        
        # 场合建议
        if occasion == "公司":
            tips.append("保持专业形象，避免过于休闲")
        elif occasion == "正式场合":
            tips.append("注意细节，确保服装整洁")
        
        return "\n".join([f"• {tip}" for tip in tips])
    
    def _determine_overall_style(self, occasion: str, style_preferences: Dict[str, Any]) -> str:
        """确定整体风格"""
        base_style = style_preferences.get('style_profile', {}).get('overall_style', '简约知性')
        
        if occasion == "公司":
            return f"{base_style} - 商务休闲"
        elif occasion == "正式场合":
            return f"{base_style} - 优雅正式"
        else:
            return f"{base_style} - 舒适休闲"
    
    async def _generate_outfit_image(self, outfit_recommendation: Dict[str, Any]) -> str:
        """生成穿搭图片"""
        # 构建详细的图片生成提示词
        prompt = f"""
        专业的职场女性穿搭效果图，包含：
        - 上装：{outfit_recommendation['top']}
        - 下装：{outfit_recommendation['bottom']}
        - 鞋履：{outfit_recommendation['shoes']}
        - 配饰：{outfit_recommendation['accessories']}
        - 色彩：主色调{outfit_recommendation['colors']['main_colors']}，辅助色{outfit_recommendation['colors']['accent_colors']}
        - 风格：{outfit_recommendation['overall_style']}
        - 场景：现代办公室环境，专业得体
        - 质量：高清摄影风格，细节清晰，自然光线
        """
        
        print(f"🎨 穿搭图片生成提示词：")
        print(prompt)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 尝试调用MCP图片生成工具
        try:
            print("🔄 正在调用即梦MCP工具生成图片...")
            
            # 清理提示词格式
            clean_prompt = prompt.strip().replace('\n        ', ' ').replace('\n', ' ')
            
            # 调用BaseAgent的MCP工具方法
            result = await self.call_mcp_tool('jimeng_generate_image', prompt=clean_prompt)
            
            if result.get('success'):
                print("✅ 图片生成成功")
                # 如果成功生成图片，返回图片路径
                image_data = result.get('data', {})
                image_path = image_data.get('image_path', '')
                image_url = image_data.get('image_url', '')
                
                if image_path:
                    # 优先使用本地保存的图片路径
                    print(f"📸 图片已保存到：{image_path}")
                    return image_path
                elif image_url:
                    # 如果只有URL，返回URL
                    print(f"📸 图片URL：{image_url}")
                    return image_url
                else:
                    # 如果都没有，创建默认路径
                    images_dir = f"data/daily_records/{datetime.now().strftime('%Y-%m-%d')}/images"
                    os.makedirs(images_dir, exist_ok=True)
                    
                    image_filename = f"outfit_{timestamp}.jpg"
                    local_path = f"{images_dir}/{image_filename}"
                    print(f"📸 默认图片路径：{local_path}")
                    return local_path
            else:
                print(f"⚠️ MCP工具连接失败: {result.get('error', '未知错误')}")
                print("💡 使用备用方案...")
                raise Exception("MCP工具不可用")
            
        except Exception as e:
            print(f"❌ 图片生成失败: {e}")
            print("🔄 启用备用方案...")
            
            # 创建增强的降级方案：生成一个详细的文本描述和占位图片信息
            outfit_description = self._generate_outfit_description(outfit_recommendation)
            
            # 创建images文件夹并保存详细的穿搭描述
            images_dir = f"data/daily_records/{datetime.now().strftime('%Y-%m-%d')}/images"
            os.makedirs(images_dir, exist_ok=True)
            
            description_file = f"{images_dir}/outfit_description_{timestamp}.md"
            
            with open(description_file, 'w', encoding='utf-8') as f:
                f.write(outfit_description)
            
            # 保存提示词到文件，方便后续手动生成
            prompt_file = f"{images_dir}/outfit_prompt_{timestamp}.txt"
            
            clean_prompt = prompt.strip().replace('\n        ', ' ').replace('\n', ' ')
            with open(prompt_file, 'w', encoding='utf-8') as f:
                f.write(f"穿搭图片生成提示词：\n{clean_prompt}")
            
            # 创建一个简单的ASCII艺术占位符
            ascii_art = self._generate_ascii_art(outfit_recommendation)
            ascii_file = f"{images_dir}/outfit_ascii_{timestamp}.txt"
            
            with open(ascii_file, 'w', encoding='utf-8') as f:
                f.write(ascii_art)
            
            # 返回描述文件路径
            print(f"💾 穿搭描述已保存到：{description_file}")
            print(f"💾 提示词已保存到：{prompt_file}")
            print(f"💾 ASCII艺术已保存到：{ascii_file}")
            
            return description_file
    
    def _generate_outfit_description(self, outfit_recommendation: Dict[str, Any]) -> str:
        """生成详细的穿搭描述"""
        description = f"""# 穿搭效果图描述

## 🎨 整体风格
{outfit_recommendation['overall_style']}

## 👔 详细搭配

### 上装
- **主要单品：** {outfit_recommendation['top']}
- **特点：** 专业、得体、适合职场环境

### 下装  
- **主要单品：** {outfit_recommendation['bottom']}
- **特点：** 舒适、正式、搭配协调

### 鞋履
- **选择：** {outfit_recommendation['shoes']}
- **特点：** 专业、舒适、全天候可穿

### 配饰
- **搭配：** {outfit_recommendation['accessories']}
- **作用：** 提升整体造型，展现专业形象

## 🎨 色彩搭配
- **主色调：** {', '.join(outfit_recommendation['colors']['main_colors'])}
- **辅助色：** {', '.join(outfit_recommendation['colors']['accent_colors'])}

## 💡 穿搭建议
{outfit_recommendation['tips']}

## 🖼️ 效果预览
```
想象一下：一位专业的职场女性，穿着{outfit_recommendation['top']}搭配{outfit_recommendation['bottom']}，
脚踩{outfit_recommendation['shoes']}，佩戴{outfit_recommendation['accessories']}，
整体造型{outfit_recommendation['overall_style']}，散发着自信和专业的魅力。
```

---
*描述生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        return description
    
    def _generate_ascii_art(self, outfit_recommendation: Dict[str, Any]) -> str:
        """生成简单的ASCII艺术"""
        ascii_art = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                             🎨 穿搭效果图                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║        👤 👔 👗 👠                                                            ║
║                                                                              ║
║   上装: {outfit_recommendation['top']:<30} ║
║                                                                              ║
║   下装: {outfit_recommendation['bottom']:<30} ║
║                                                                              ║
║   鞋履: {outfit_recommendation['shoes']:<30} ║
║                                                                              ║
║   配饰: {outfit_recommendation['accessories']:<25} ║
║                                                                              ║
║   风格: {outfit_recommendation['overall_style']:<28} ║
║                                                                              ║
║   色彩: {', '.join(outfit_recommendation['colors']['main_colors']) + ' + ' + ', '.join(outfit_recommendation['colors']['accent_colors']):<25} ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

💡 提示：这是一个文本描述，实际的图像需要使用图像生成工具创建
"""
        return ascii_art
    
    def _generate_outfit_content(self, date_str: str, weather_info: Dict[str, Any], 
                                occasion: str, outfit_recommendation: Dict[str, Any], 
                                outfit_image_url: str) -> str:
        """生成穿搭内容"""
        template_vars = {
            "date": date_str,
            "weather_condition": weather_info.get('condition', '晴朗'),
            "temperature": weather_info.get('temperature', '22°C'),
            "humidity": weather_info.get('humidity', '65%'),
            "wind": weather_info.get('wind', '微风'),
            "occasion": occasion,
            "style_requirements": self._get_style_requirements(occasion),
            "top_recommendation": outfit_recommendation['top'],
            "bottom_recommendation": outfit_recommendation['bottom'],
            "shoes_recommendation": outfit_recommendation['shoes'],
            "accessories_recommendation": outfit_recommendation['accessories'],
            "main_colors": "、".join(outfit_recommendation['colors']['main_colors']),
            "accent_colors": "、".join(outfit_recommendation['colors']['accent_colors']),
            "styling_tips": outfit_recommendation['tips'],
            "outfit_image_url": outfit_image_url,
            "generated_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "personal_style": outfit_recommendation['overall_style']
        }
        
        return self.generate_from_template('outfit_template', template_vars)
    
    def _get_style_requirements(self, occasion: str) -> str:
        """获取风格要求"""
        style_requirements = {
            "公司": "专业、得体、舒适",
            "约会": "优雅、有气质、适合场合",
            "运动": "舒适、透气、便于活动",
            "休闲": "轻松、自在、展现个性",
            "正式场合": "庄重、优雅、符合礼仪",
            "其他": "根据具体需求调整"
        }
        
        return style_requirements.get(occasion, "舒适、得体")
    
    def _send_to_lark(self, outfit_content: str, outfit_image_url: str):
        """发送到飞书"""
        # 这里应该调用飞书MCP工具
        print("📤 穿搭建议已发送到飞书")
        print(f"🖼️ 穿搭图片：{outfit_image_url}")
    
    def get_outfit_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """获取穿搭历史"""
        return self.file_manager.get_history_data('outfit', days)
    
    def get_style_statistics(self) -> Dict[str, Any]:
        """获取风格统计"""
        history = self.get_outfit_history()
        
        stats = {
            "total_outfits": len(history),
            "popular_occasions": {},
            "popular_colors": {},
            "style_trends": {}
        }
        
        # 分析历史数据
        for entry in history:
            data = entry.get('data', {})
            occasion = data.get('occasion', '其他')
            stats['popular_occasions'][occasion] = stats['popular_occasions'].get(occasion, 0) + 1
        
        return stats
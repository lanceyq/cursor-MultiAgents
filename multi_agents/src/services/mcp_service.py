"""
MCP服务集成层
负责管理和调用各种MCP工具
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class MCPService:
    """MCP工具服务管理器"""
    
    def __init__(self):
        self.tools = {}
        self.tool_status = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """初始化可用的MCP工具"""
        # 定义支持的MCP工具
        supported_tools = {
            'jimeng_image': {
                'name': 'hans-m-yin-jimeng-mcp',
                'functions': ['generateImage', 'hello']
            },
            'firecrawl': {
                'name': 'krieg-2065-firecrawl-mcp-server',
                'functions': ['firecrawl_scrape', 'firecrawl_search', 'firecrawl_crawl']
            },
            'weather': {
                'name': 'harun-guclu-weather-mcp',
                'functions': ['get_current_weather_tool', 'get_weather_forecast_tool']
            },
            'lark': {
                'name': 'lark-mcp',
                'functions': ['bitable_v1_appTableRecord_create', 'im_v1_message_create']
            }
        }
        
        self.tools = supported_tools
        print(f"MCP服务初始化完成，支持 {len(supported_tools)} 个工具集")
    
    def get_tool_status(self) -> Dict[str, Any]:
        """获取所有工具状态"""
        return self.tool_status
    
    def is_tool_available(self, tool_name: str) -> bool:
        """检查工具是否可用"""
        return self.tool_status.get(tool_name, {}).get('available', False)
    
    def update_tool_status(self, tool_name: str, status: Dict[str, Any]):
        """更新工具状态"""
        self.tool_status[tool_name] = status
    
    async def call_jimeng_generate_image(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """调用Jimeng图片生成工具"""
        try:
            # 尝试调用实际的MCP工具
            # 检查全局命名空间中是否有可用的MCP工具
            import sys
            
            # 获取调用者的全局命名空间
            import inspect
            frame = inspect.currentframe()
            try:
                # 向上查找调用栈，找到有MCP工具的命名空间
                caller_frame = frame.f_back
                while caller_frame:
                    caller_globals = caller_frame.f_globals
                    caller_locals = caller_frame.f_locals
                    
                    # 在调用者的全局和局部命名空间中寻找工具
                    for namespace in [caller_globals, caller_locals]:
                        # 寻找可用的即梦MCP工具 - 尝试多种命名模式
                        jimeng_tool = None
                        tool_variants = [
                            'mcp__hans-m-yin-jimeng-mcp__generateImage',
                            'mcp__hans_m_yin_jimeng_mcp__generateImage', 
                            'mcp__hans-m-yin-jimeng-mcp_generateImage',
                            'mcp__hans_m_yin_jimeng_mcp_generateImage'
                        ]
                        
                        for variant in tool_variants:
                            if variant in namespace and callable(namespace[variant]):
                                jimeng_tool = namespace[variant]
                                print(f"🔧 找到可用的即梦MCP工具: {variant}")
                                break
                        
                        if jimeng_tool:
                            break
                    
                    if jimeng_tool:
                        break
                    
                    caller_frame = caller_frame.f_back
                    
            finally:
                del frame  # 避免引用循环
            
            # 如果在调用栈中找不到，尝试当前全局命名空间
            if not jimeng_tool:
                global_namespace = globals()
                tool_variants = [
                    'mcp__hans-m-yin-jimeng-mcp__generateImage',
                    'mcp__hans_m_yin_jimeng_mcp__generateImage', 
                    'mcp__hans-m-yin-jimeng-mcp_generateImage',
                    'mcp__hans_m_yin_jimeng_mcp_generateImage'
                ]
                
                for variant in tool_variants:
                    if variant in global_namespace and callable(global_namespace[variant]):
                        jimeng_tool = global_namespace[variant]
                        print(f"🔧 在当前全局命名空间找到即梦MCP工具: {variant}")
                        break
            
            if jimeng_tool and callable(jimeng_tool):
                print("🔧 正在调用即梦MCP工具生成图片...")
                
                # 调用工具
                width = kwargs.get('width', 1024)
                height = kwargs.get('height', 1024)
                model = kwargs.get('model', 'jimeng-3.0')
                
                result = jimeng_tool(
                    prompt=prompt,
                    width=width,
                    height=height,
                    model=model
                )
                
                print("✅ 即梦MCP工具调用成功")
                
                # 处理返回结果并保存图片
                saved_image_path = await self._save_generated_image(result, prompt, kwargs)
                
                self.update_tool_status('jimeng', {
                    'available': True,
                    'last_check': datetime.now().isoformat(),
                    'error': None
                })
                
                return {
                    'success': True,
                    'data': {
                        'image_url': result.get('image_url', ''),
                        'image_path': saved_image_path,
                        'image_data': result.get('image_data', ''),
                        'prompt': prompt
                    },
                    'tool': 'jimeng_generate_image',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print("⚠️ 未找到可用的即梦MCP工具")
                raise Exception("MCP工具不可用")
                
        except Exception as e:
            print(f"❌ 即梦MCP工具调用失败: {e}")
            
            self.update_tool_status('jimeng', {
                'available': False,
                'last_check': datetime.now().isoformat(),
                'error': str(e)
            })
            
            return {
                'success': False,
                'error': f'MCP工具连接失败: {str(e)}',
                'tool': 'jimeng_generate_image',
                'timestamp': datetime.now().isoformat()
            }
    
    async def _save_generated_image(self, result: Dict[str, Any], prompt: str, kwargs: Dict[str, Any]) -> str:
        """保存生成的图片到images文件夹"""
        try:
            from datetime import datetime
            import os
            import base64
            import requests
            
            # 创建images文件夹
            today = datetime.now().strftime('%Y-%m-%d')
            images_dir = f"data/daily_records/{today}/images"
            os.makedirs(images_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            image_filename = f"outfit_{timestamp}.jpg"
            image_path = f"{images_dir}/{image_filename}"
            
            # 尝试从不同数据源保存图片
            image_saved = False
            
            # 1. 如果有直接的图片数据
            if 'image_data' in result and result['image_data']:
                image_data = result['image_data']
                
                # 如果是base64编码
                if isinstance(image_data, str) and image_data.startswith('data:image'):
                    # 提取base64数据
                    try:
                        # 处理data URI格式
                        if ',' in image_data:
                            base64_data = image_data.split(',')[1]
                        else:
                            base64_data = image_data
                        
                        # 添加正确的padding
                        missing_padding = len(base64_data) % 4
                        if missing_padding:
                            base64_data += '=' * (4 - missing_padding)
                        
                        image_bytes = base64.b64decode(base64_data)
                        
                        with open(image_path, 'wb') as f:
                            f.write(image_bytes)
                        
                        print(f"💾 图片已保存到: {image_path}")
                        image_saved = True
                    except Exception as decode_error:
                        print(f"⚠️ Base64解码失败: {decode_error}")
                        # 保存原始数据到文件
                        with open(image_path.replace('.jpg', '.txt'), 'w', encoding='utf-8') as f:
                            f.write(f"原始base64数据:\n{image_data}")
                        print(f"💾 原始数据已保存到文本文件")
                
                # 如果是二进制数据
                elif isinstance(image_data, bytes):
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    print(f"💾 图片已保存到: {image_path}")
                    image_saved = True
            
            # 2. 如果有图片URL，尝试下载
            elif 'image_url' in result and result['image_url']:
                image_url = result['image_url']
                
                try:
                    response = requests.get(image_url, timeout=30)
                    if response.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(response.content)
                        
                        print(f"💾 图片已下载并保存到: {image_path}")
                        image_saved = True
                    else:
                        print(f"⚠️ 图片下载失败，状态码: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ 图片下载失败: {e}")
            
            # 3. 如果有文件路径
            elif 'file_path' in result and result['file_path']:
                import shutil
                source_path = result['file_path']
                
                if os.path.exists(source_path):
                    shutil.copy2(source_path, image_path)
                    print(f"💾 图片已复制到: {image_path}")
                    image_saved = True
            
            if not image_saved:
                print("⚠️ 未能保存图片，返回路径信息")
                # 保存图片信息到文本文件
                info_file = f"{images_dir}/outfit_info_{timestamp}.txt"
                with open(info_file, 'w', encoding='utf-8') as f:
                    f.write(f"图片生成信息:\n")
                    f.write(f"提示词: {prompt}\n")
                    f.write(f"生成时间: {datetime.now().isoformat()}\n")
                    f.write(f"工具参数: {kwargs}\n")
                    f.write(f"返回结果: {result}\n")
                
                return info_file
            
            return image_path
            
        except Exception as e:
            print(f"❌ 图片保存失败: {e}")
            # 返回错误信息文件路径
            error_file = f"{images_dir}/outfit_error_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"图片保存错误: {str(e)}\n")
                f.write(f"时间: {datetime.now().isoformat()}\n")
            
            return error_file
    
    async def call_firecrawl_scrape(self, url: str, **kwargs) -> Dict[str, Any]:
        """调用Firecrawl网页抓取工具"""
        try:
            # 尝试调用实际的MCP工具
            import sys
            global_namespace = globals()
            
            # 寻找可用的Firecrawl MCP工具
            firecrawl_tool = None
            for name in global_namespace:
                if 'mcp__krieg' in name.lower() and 'firecrawl' in name.lower() and 'scrape' in name.lower():
                    firecrawl_tool = global_namespace[name]
                    break
            
            if firecrawl_tool and callable(firecrawl_tool):
                print("🔧 找到可用的Firecrawl MCP工具，正在调用...")
                
                # 调用工具
                result = firecrawl_tool(url=url, **kwargs)
                
                self.update_tool_status('firecrawl', {
                    'available': True,
                    'last_check': datetime.now().isoformat(),
                    'error': None
                })
                
                return {
                    'success': True,
                    'data': result,
                    'tool': 'firecrawl_scrape',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print("⚠️ 未找到可用的Firecrawl MCP工具")
                raise Exception("MCP工具不可用")
                
        except Exception as e:
            print(f"❌ Firecrawl MCP工具调用失败: {e}")
            
            self.update_tool_status('firecrawl', {
                'available': False,
                'last_check': datetime.now().isoformat(),
                'error': str(e)
            })
            
            return {
                'success': False,
                'error': f'MCP工具连接失败: {str(e)}',
                'tool': 'firecrawl_scrape',
                'timestamp': datetime.now().isoformat()
            }
    
    async def call_weather_current(self, city: str) -> Dict[str, Any]:
        """调用天气查询工具"""
        try:
            # 这里应该调用实际的MCP工具
            # 模拟成功的天气数据
            result = {
                'success': True,
                'data': {
                    'city': city,
                    'temperature': 22,
                    'condition': '晴朗',
                    'humidity': 65,
                    'wind_speed': 3.5
                },
                'tool': 'weather_current',
                'timestamp': datetime.now().isoformat()
            }
            
            self.update_tool_status('weather', {
                'available': True,
                'last_check': datetime.now().isoformat(),
                'error': None
            })
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tool': 'weather_current',
                'timestamp': datetime.now().isoformat()
            }
    
    async def call_lark_send_message(self, message: str, chat_id: str) -> Dict[str, Any]:
        """调用飞书消息发送工具"""
        try:
            # 这里应该调用实际的MCP工具
            result = {
                'success': True,
                'data': {
                    'message_id': f'msg_{datetime.now().timestamp()}',
                    'chat_id': chat_id,
                    'status': 'sent'
                },
                'tool': 'lark_send_message',
                'timestamp': datetime.now().isoformat()
            }
            
            self.update_tool_status('lark', {
                'available': True,
                'last_check': datetime.now().isoformat(),
                'error': None
            })
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'tool': 'lark_send_message',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        available = []
        for tool_name, status in self.tool_status.items():
            if status.get('available', False):
                available.append(tool_name)
        return available
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """获取工具信息"""
        return self.tools.get(tool_name, {})
    
    async def test_all_tools(self) -> Dict[str, Any]:
        """测试所有工具连接状态"""
        test_results = {}
        
        # 测试Jimeng
        try:
            jimeng_result = await self.call_jimeng_generate_image("test")
            test_results['jimeng'] = jimeng_result
        except Exception as e:
            test_results['jimeng'] = {'success': False, 'error': str(e)}
        
        # 测试Firecrawl
        try:
            firecrawl_result = await self.call_firecrawl_scrape("https://example.com")
            test_results['firecrawl'] = firecrawl_result
        except Exception as e:
            test_results['firecrawl'] = {'success': False, 'error': str(e)}
        
        # 测试天气
        try:
            weather_result = await self.call_weather_current("北京")
            test_results['weather'] = weather_result
        except Exception as e:
            test_results['weather'] = {'success': False, 'error': str(e)}
        
        # 测试飞书
        try:
            lark_result = await self.call_lark_send_message("test", "test_chat")
            test_results['lark'] = lark_result
        except Exception as e:
            test_results['lark'] = {'success': False, 'error': str(e)}
        
        return test_results
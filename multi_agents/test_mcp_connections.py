#!/usr/bin/env python3
"""
MCP工具连接测试脚本
"""

import asyncio
import sys
import os
sys.path.append(os.getcwd())

from src.services.mcp_service import MCPService

async def test_mcp_connections():
    """测试所有MCP工具连接"""
    print("=== MCP工具连接测试 ===")
    
    mcp_service = MCPService()
    
    # 测试所有工具
    print("\n1. 测试所有工具连接...")
    test_results = await mcp_service.test_all_tools()
    
    print("\n2. 测试结果:")
    for tool_name, result in test_results.items():
        status = "成功" if result.get('success', False) else "失败"
        print(f"  {tool_name}: {status}")
        if not result.get('success', False):
            print(f"    错误: {result.get('error', 'Unknown error')}")
    
    # 显示工具状态
    print("\n3. 工具状态概览:")
    tool_status = mcp_service.get_tool_status()
    for tool_name, status in tool_status.items():
        available = status.get('available', False)
        status_icon = "OK" if available else "FAIL"
        print(f"  {status_icon} {tool_name}: {status}")
    
    # 显示可用工具
    available_tools = mcp_service.get_available_tools()
    print(f"\n4. 可用工具数量: {len(available_tools)}")
    if available_tools:
        print("   可用工具:", available_tools)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    asyncio.run(test_mcp_connections())
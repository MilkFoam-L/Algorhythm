"""
简化 Agent 测试
测试新版本的 SimpleMusicAgent
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_simple_agent():
    """测试简化的 Agent"""
    print("=" * 60)
    print("测试: 简化 Music Agent")
    print("=" * 60)

    try:
        from src.agent import MusicAgent
        from src.llm.deepseek_langchain import DeepSeekChatModel
        from langchain.tools import BaseTool
        from pydantic import BaseModel, Field
        from typing import Dict, Any

        # 创建一个测试工具
        class EchoToolInput(BaseModel):
            message: str = Field(description="要回显的消息")

        class EchoTool(BaseTool):
            name: str = "echo_tool"
            description: str = "回显用户的消息（用于测试）"
            args_schema: type[BaseModel] = EchoToolInput

            def _run(self, message: str) -> Dict[str, Any]:
                return {
                    "success": True,
                    "original": message,
                    "echo": message.upper(),
                    "length": len(message)
                }

        # 创建 Agent
        print("\n创建 Agent...")
        agent = MusicAgent(verbose=True)

        # 添加工具
        agent.add_tool(EchoTool())
        print(f"✅ Agent 创建成功，可用工具: {agent.get_available_tools()}")

        # 测试 1: 简单对话
        print("\n" + "-" * 60)
        print("测试 1: 简单对话")
        print("-" * 60)

        result1 = agent.process("你好，请介绍一下你自己")

        if result1["success"]:
            print(f"\n✅ 测试 1 通过")
            print(f"输出: {result1['output'][:200]}...")
        else:
            print(f"\n❌ 测试 1 失败: {result1.get('error')}")

        # 测试 2: 工具调用（如果 Agent 理解的话）
        print("\n" + "-" * 60)
        print("测试 2: 询问可用功能")
        print("-" * 60)

        result2 = agent.process("你有什么功能？可以帮我做什么？")

        if result2["success"]:
            print(f"\n✅ 测试 2 通过")
            print(f"输出: {result2['output'][:200]}...")
        else:
            print(f"\n❌ 测试 2 失败: {result2.get('error')}")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_deepseek_basic():
    """测试 DeepSeek 基本功能"""
    print("\n" + "=" * 60)
    print("测试: DeepSeek 基本功能")
    print("=" * 60)

    try:
        from src.llm.deepseek_client import DeepSeekClient

        client = DeepSeekClient()
        print("✅ DeepSeek 客户端创建成功")

        # 测试对话
        print("\n发送测试消息...")
        response = client.chat_once("请用一句话介绍 LangChain")

        if response:
            print(f"✅ 响应成功")
            print(f"内容: {response}")
            return True
        else:
            print("❌ 无响应")
            return False

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("\n🎵 Algorhythm 简化 Agent 测试")
    print("=" * 60)

    tests = [
        ("DeepSeek 基本功能", test_deepseek_basic),
        ("简化 Music Agent", test_simple_agent),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{test_name}' 发生异常: {e}")
            results.append((test_name, False))

    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")

    print(f"\n总计: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！Agent 框架工作正常。")
    else:
        print("\n⚠️  部分测试失败。")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

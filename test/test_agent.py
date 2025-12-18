"""
Algorhythm Agent 测试脚本
测试音乐 AI Agent 的基本功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """测试 1: 验证所有模块可以正常导入"""
    print("=" * 60)
    print("测试 1: 模块导入测试")
    print("=" * 60)

    try:
        from src.llm.deepseek_client import DeepSeekClient
        print("✅ DeepSeekClient 导入成功")

        from src.llm.deepseek_langchain import DeepSeekLLM, DeepSeekChatModel
        print("✅ DeepSeek LangChain 集成导入成功")

        from src.tools.hearing_tool import HearingTool
        print("✅ HearingTool 导入成功")

        from src.agent.music_agent import MusicAgent
        print("✅ MusicAgent 导入成功")

        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("\n请确保已安装所有依赖:")
        print("  pip install -r requirements.txt")
        return False


def test_hearing_tool_creation():
    """测试 2: 创建 Hearing Tool 实例"""
    print("\n" + "=" * 60)
    print("测试 2: Hearing Tool 实例化")
    print("=" * 60)

    try:
        from src.tools.hearing_tool import HearingTool

        tool = HearingTool()
        print(f"✅ 工具名称: {tool.name}")
        print(f"✅ 工具描述: {tool.description[:100]}...")

        return True
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False


def test_agent_creation():
    """测试 3: 创建 Music Agent"""
    print("\n" + "=" * 60)
    print("测试 3: Music Agent 实例化")
    print("=" * 60)

    try:
        from src.agent.music_agent import MusicAgent

        agent = MusicAgent(verbose=False)
        print(f"✅ Agent 创建成功")
        print(f"✅ 可用工具: {agent.get_available_tools()}")

        return True
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        print(f"\n可能的原因:")
        print("  1. 未设置 DEEPSEEK_API_KEY 环境变量")
        print("  2. 缺少必要的依赖包")
        print("\n解决方法:")
        print("  1. 在 .env 文件中设置 DEEPSEEK_API_KEY")
        print("  2. 运行: pip install -r requirements.txt")
        return False


def test_deepseek_connection():
    """测试 4: 测试 DeepSeek API 连接"""
    print("\n" + "=" * 60)
    print("测试 4: DeepSeek API 连接测试")
    print("=" * 60)

    try:
        from src.llm.deepseek_client import DeepSeekClient

        client = DeepSeekClient()
        print("✅ DeepSeek 客户端创建成功")

        # 发送测试消息
        print("\n发送测试消息...")
        response = client.chat_once("Hello, please respond with 'OK' if you can hear me.")

        if response:
            print(f"✅ API 响应成功")
            print(f"响应内容: {response[:100]}...")
            return True
        else:
            print("❌ API 无响应")
            return False

    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("\n请在 .env 文件中设置 DEEPSEEK_API_KEY")
        return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False


def test_tool_schema():
    """测试 5: 验证工具 Schema"""
    print("\n" + "=" * 60)
    print("测试 5: 工具 Schema 验证")
    print("=" * 60)

    try:
        from src.tools.hearing_tool import HearingTool

        tool = HearingTool()

        # 检查必要属性
        assert hasattr(tool, 'name'), "缺少 name 属性"
        assert hasattr(tool, 'description'), "缺少 description 属性"
        assert hasattr(tool, 'args_schema'), "缺少 args_schema 属性"

        print(f"✅ 工具名称: {tool.name}")
        print(f"✅ 参数 Schema: {tool.args_schema.__name__}")

        # 检查参数字段
        schema_fields = tool.args_schema.model_fields
        print(f"✅ 参数字段: {list(schema_fields.keys())}")

        return True
    except AssertionError as e:
        print(f"❌ Schema 验证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_langchain_integration():
    """测试 6: LangChain 集成测试"""
    print("\n" + "=" * 60)
    print("测试 6: LangChain 集成")
    print("=" * 60)

    try:
        from langchain.tools import BaseTool
        from src.tools.hearing_tool import HearingTool

        tool = HearingTool()

        # 验证是否是 BaseTool 的实例
        assert isinstance(tool, BaseTool), "HearingTool 不是 BaseTool 的实例"
        print("✅ HearingTool 正确继承 BaseTool")

        # 验证必要方法
        assert hasattr(tool, '_run'), "缺少 _run 方法"
        assert hasattr(tool, '_arun'), "缺少 _arun 方法"
        print("✅ 必要方法存在")

        return True
    except AssertionError as e:
        print(f"❌ 集成验证失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n🎵 Algorhythm Agent 测试套件")
    print("=" * 60)

    tests = [
        ("模块导入", test_imports),
        ("Hearing Tool 创建", test_hearing_tool_creation),
        ("Music Agent 创建", test_agent_creation),
        ("DeepSeek 连接", test_deepseek_connection),
        ("工具 Schema", test_tool_schema),
        ("LangChain 集成", test_langchain_integration),
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
        print("\n🎉 所有测试通过！系统已准备就绪。")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息。")

    return passed == total


def main():
    """主函数"""
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

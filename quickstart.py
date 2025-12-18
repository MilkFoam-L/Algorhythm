#!/usr/bin/env python3
"""
Algorhythm 快速启动脚本
快速测试系统功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║     🎵  Algorhythm - AI 音乐制作智能体  🎵               ║
║                                                           ║
║     基于 LangChain + DeepSeek 构建                        ║
║     Phase 1: 听觉工具 (Audio → MIDI)                     ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment():
    """检查环境配置"""
    print("\n🔍 检查环境配置...")

    # 检查 .env 文件
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  未找到 .env 文件")
        print("   请创建 .env 文件并配置 DEEPSEEK_API_KEY")
        return False

    # 检查依赖
    try:
        import langchain
        import basic_pitch
        import pretty_midi
        print("✅ 核心依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("   请运行: pip install -r requirements.txt")
        return False


def demo_hearing_tool():
    """演示听觉工具"""
    print("\n" + "=" * 60)
    print("📊 听觉工具演示")
    print("=" * 60)

    from src.tools import HearingTool

    tool = HearingTool()

    print(f"\n工具名称: {tool.name}")
    print(f"工具描述: {tool.description[:150]}...")

    print("\n💡 使用方法:")
    print("   from src.tools import HearingTool")
    print("   tool = HearingTool()")
    print("   result = tool._run(audio_path='your_audio.wav')")

    print("\n📝 支持的音频格式: .wav, .mp3, .flac, .ogg")


def demo_agent():
    """演示 AI Agent"""
    print("\n" + "=" * 60)
    print("🤖 AI Agent 演示")
    print("=" * 60)

    try:
        from src.agent import MusicAgent

        agent = MusicAgent(verbose=False)

        print(f"\n✅ Agent 创建成功")
        print(f"🔧 可用工具: {', '.join(agent.get_available_tools())}")

        print("\n💡 使用方法:")
        print("   from src.agent import MusicAgent")
        print("   agent = MusicAgent()")
        print("   result = agent.process('请将 audio.wav 转换为 MIDI')")

        print("\n🎯 Agent 特性:")
        print("   • 自然语言交互")
        print("   • 自动工具选择")
        print("   • 智能结果解释")

    except Exception as e:
        print(f"\n⚠️  Agent 创建失败: {e}")
        print("   可能原因: 未配置 DEEPSEEK_API_KEY")


def show_next_steps():
    """显示后续步骤"""
    print("\n" + "=" * 60)
    print("📚 后续步骤")
    print("=" * 60)

    steps = [
        ("1. 运行完整测试", "python test_agent.py"),
        ("2. 查看使用示例", "python examples/basic_usage.py"),
        ("3. 准备音频文件", "将 .wav/.mp3 文件放入项目目录"),
        ("4. 开始使用", "from src.agent import MusicAgent"),
    ]

    for step, command in steps:
        print(f"\n{step}:")
        print(f"   {command}")


def interactive_demo():
    """交互式演示"""
    print("\n" + "=" * 60)
    print("🎮 交互式演示")
    print("=" * 60)

    print("\n选择演示模式:")
    print("  1. 查看工具信息")
    print("  2. 测试 Agent 创建")
    print("  3. 查看使用示例")
    print("  4. 退出")

    try:
        choice = input("\n请输入选项 (1-4): ").strip()

        if choice == "1":
            demo_hearing_tool()
        elif choice == "2":
            demo_agent()
        elif choice == "3":
            print("\n查看 examples/basic_usage.py 获取完整示例")
        elif choice == "4":
            print("\n👋 再见!")
            return
        else:
            print("\n❌ 无效选项")

    except KeyboardInterrupt:
        print("\n\n👋 再见!")


def main():
    """主函数"""
    print_banner()

    # 检查环境
    if not check_environment():
        print("\n❌ 环境检查失败，请先配置环境")
        sys.exit(1)

    # 演示功能
    demo_hearing_tool()
    demo_agent()

    # 显示后续步骤
    show_next_steps()

    # 交互式演示
    print("\n" + "=" * 60)
    try:
        response = input("\n是否进入交互式演示? (y/n): ").strip().lower()
        if response == 'y':
            interactive_demo()
    except KeyboardInterrupt:
        print("\n\n👋 再见!")

    print("\n✨ 快速启动完成！")
    print("📖 查看 README.md 获取完整文档\n")


if __name__ == "__main__":
    main()

"""
Algorhythm 基础使用示例
演示如何使用音乐 AI Agent 进行音频处理
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agent import MusicAgent
from src.tools import HearingTool


def example_1_direct_tool_usage():
    """示例 1: 直接使用 Hearing Tool"""
    print("=" * 60)
    print("示例 1: 直接使用 Hearing Tool")
    print("=" * 60)

    # 创建工具实例
    hearing_tool = HearingTool()

    # 假设你有一个音频文件
    audio_path = "path/to/your/audio.wav"  # 替换为实际路径

    print(f"\n正在处理音频: {audio_path}")

    # 直接调用工具
    result = hearing_tool._run(audio_path=audio_path)

    if result["success"]:
        print(f"\n✅ 转换成功!")
        print(f"📁 MIDI 文件: {result['midi_path']}")
        print(f"🎵 音符数量: {result['note_count']}")
        print(f"⏱️  时长: {result['duration_seconds']} 秒")
        print(f"🎹 乐器数量: {result['instrument_count']}")
        print(f"🎼 估计速度: {result['tempo']} BPM")

        if result.get('sample_notes'):
            print(f"\n前几个音符:")
            for i, note in enumerate(result['sample_notes'][:5], 1):
                print(f"  {i}. {note['note_name']} - "
                      f"起始: {note['start']}s, "
                      f"时长: {note['duration']}s, "
                      f"力度: {note['velocity']}")
    else:
        print(f"\n❌ 转换失败: {result['error']}")


def example_2_agent_usage():
    """示例 2: 使用 AI Agent 进行自然语言交互"""
    print("\n" + "=" * 60)
    print("示例 2: 使用 AI Agent")
    print("=" * 60)

    # 创建 Agent
    agent = MusicAgent(verbose=True)

    print(f"\n可用工具: {agent.get_available_tools()}")

    # 使用自然语言与 Agent 交互
    audio_path = "path/to/your/audio.wav"  # 替换为实际路径

    print(f"\n用户请求: 请将这个音频文件转换为 MIDI: {audio_path}")

    result = agent.process_audio_file(
        audio_path=audio_path,
        task="convert to MIDI and analyze the notes"
    )

    if result["success"]:
        print(f"\n✅ Agent 处理成功!")
        print(f"输出: {result['output']}")
    else:
        print(f"\n❌ Agent 处理失败: {result['error']}")


def example_3_batch_processing():
    """示例 3: 批量处理多个音频文件"""
    print("\n" + "=" * 60)
    print("示例 3: 批量处理")
    print("=" * 60)

    # 创建工具
    hearing_tool = HearingTool()

    # 音频文件列表
    audio_files = [
        "audio1.wav",
        "audio2.mp3",
        "audio3.flac",
    ]

    results = []
    for audio_file in audio_files:
        print(f"\n处理: {audio_file}")
        result = hearing_tool._run(audio_path=audio_file)
        results.append(result)

        if result["success"]:
            print(f"  ✅ {result['note_count']} 个音符")
        else:
            print(f"  ❌ {result['error']}")

    # 统计
    successful = sum(1 for r in results if r["success"])
    print(f"\n总结: {successful}/{len(audio_files)} 个文件处理成功")


def example_4_custom_output_dir():
    """示例 4: 指定输出目录"""
    print("\n" + "=" * 60)
    print("示例 4: 自定义输出目录")
    print("=" * 60)

    hearing_tool = HearingTool()

    audio_path = "path/to/your/audio.wav"
    output_dir = "./output/midi_files"  # 自定义输出目录

    print(f"\n音频: {audio_path}")
    print(f"输出目录: {output_dir}")

    result = hearing_tool._run(
        audio_path=audio_path,
        output_dir=output_dir
    )

    if result["success"]:
        print(f"\n✅ MIDI 文件已保存到: {result['midi_path']}")


def main():
    """主函数"""
    print("\n🎵 Algorhythm - AI 音乐制作助手")
    print("=" * 60)

    # 运行示例
    # 注意: 需要替换为实际的音频文件路径

    print("\n⚠️  注意: 请先替换示例中的音频文件路径为实际路径")
    print("然后取消注释下面的示例代码\n")

    # 取消注释以运行示例:
    # example_1_direct_tool_usage()
    # example_2_agent_usage()
    # example_3_batch_processing()
    # example_4_custom_output_dir()


if __name__ == "__main__":
    main()

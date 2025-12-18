"""
听觉工具测试
测试 Basic Pitch 音频转 MIDI 功能
"""

import sys
from pathlib import Path
import tempfile

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_hearing_tool_import():
    """测试 1: 导入听觉工具"""
    print("=" * 60)
    print("测试 1: 导入听觉工具")
    print("=" * 60)

    try:
        from src.tools import HearingTool
        print("✅ HearingTool 导入成功")

        tool = HearingTool()
        print(f"✅ 工具名称: {tool.name}")
        print(f"✅ 工具描述: {tool.description[:100]}...")

        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_basic_pitch_import():
    """测试 2: Basic Pitch 依赖"""
    print("\n" + "=" * 60)
    print("测试 2: Basic Pitch 依赖")
    print("=" * 60)

    try:
        import basic_pitch
        print(f"✅ basic-pitch 导入成功")

        from basic_pitch.inference import predict
        print("✅ predict 函数导入成功")

        import pretty_midi
        print("✅ pretty_midi 导入成功")

        import librosa
        print(f"✅ librosa 版本: {librosa.__version__}")

        # 检查 TensorFlow
        try:
            import tensorflow as tf
            print(f"✅ tensorflow 版本: {tf.__version__}")
        except ImportError:
            print("⚠️  tensorflow 未安装（将使用 CoreML 后端）")

        return True
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        return False


def test_generate_test_audio():
    """测试 3: 生成测试音频"""
    print("\n" + "=" * 60)
    print("测试 3: 生成测试音频")
    print("=" * 60)

    try:
        import numpy as np
        import soundfile as sf

        # 生成一个简单的旋律：C4-E4-G4-C5 (C 大调和弦分解)
        sample_rate = 22050
        note_duration = 0.5  # 每个音符 0.5 秒

        # 音符频率 (Hz)
        notes = [
            261.63,  # C4
            329.63,  # E4
            392.00,  # G4
            523.25,  # C5
        ]

        audio_segments = []
        for freq in notes:
            t = np.linspace(0, note_duration, int(sample_rate * note_duration))
            # 添加包络以避免突然的开始和结束
            envelope = np.exp(-3 * t / note_duration)  # 衰减包络
            note_audio = 0.5 * np.sin(2 * np.pi * freq * t) * envelope
            audio_segments.append(note_audio)

        # 合并所有音符
        audio = np.concatenate(audio_segments)

        # 保存到临时文件
        temp_dir = Path(tempfile.gettempdir())
        test_audio_path = temp_dir / "test_audio_melody.wav"

        sf.write(test_audio_path, audio, sample_rate)

        print(f"✅ 测试音频已生成: {test_audio_path}")
        print(f"   旋律: C4-E4-G4-C5 (C 大调和弦分解)")
        print(f"   音符数量: {len(notes)}")
        print(f"   总时长: {len(audio) / sample_rate:.1f} 秒")
        print(f"   采样率: {sample_rate} Hz")

        return str(test_audio_path)

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None


def test_hearing_tool_execution(audio_path: str):
    """测试 4: 执行听觉工具"""
    print("\n" + "=" * 60)
    print("测试 4: 执行听觉工具")
    print("=" * 60)

    try:
        from src.tools import HearingTool

        tool = HearingTool()

        print(f"\n🎵 处理音频: {audio_path}")
        print("⏳ 正在转换... (首次运行会下载模型，可能需要几分钟)")

        result = tool._run(audio_path=audio_path)

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

            return True
        else:
            print(f"\n❌ 转换失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_with_hearing_tool(audio_path: str):
    """测试 5: Agent 集成听觉工具"""
    print("\n" + "=" * 60)
    print("测试 5: Agent 集成听觉工具")
    print("=" * 60)

    try:
        from src.agent import MusicAgent
        from src.tools import HearingTool

        # 创建 Agent 并添加听觉工具
        agent = MusicAgent(verbose=True)
        agent.add_tool(HearingTool())

        print(f"✅ Agent 创建成功")
        print(f"🔧 可用工具: {agent.get_available_tools()}")

        # 测试 Agent 处理音频
        print(f"\n测试 Agent 处理音频文件...")
        result = agent.process(f"请将这个音频文件转换为 MIDI: {audio_path}")

        if result["success"]:
            print(f"\n✅ Agent 处理成功")
            print(f"输出: {result['output'][:300]}...")
            return True
        else:
            print(f"\n❌ Agent 处理失败: {result.get('error')}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n🎵 Algorhythm 听觉工具测试套件")
    print("=" * 60)

    results = []

    # 测试 1: 导入
    result1 = test_hearing_tool_import()
    results.append(("导入听觉工具", result1))

    if not result1:
        print("\n⚠️  基础导入失败，跳过后续测试")
        return False

    # 测试 2: 依赖
    result2 = test_basic_pitch_import()
    results.append(("Basic Pitch 依赖", result2))

    if not result2:
        print("\n⚠️  依赖检查失败，跳过后续测试")
        return False

    # 测试 3: 生成测试音频
    audio_path = test_generate_test_audio()
    results.append(("生成测试音频", audio_path is not None))

    if not audio_path:
        print("\n⚠️  无法生成测试音频，跳过后续测试")
        return False

    # 测试 4: 执行工具
    result4 = test_hearing_tool_execution(audio_path)
    results.append(("执行听觉工具", result4))

    # 测试 5: Agent 集成（可选）
    if result4:
        result5 = test_agent_with_hearing_tool(audio_path)
        results.append(("Agent 集成", result5))

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
        print("\n🎉 所有测试通过！听觉工具已准备就绪。")
        print("\n📝 注意:")
        print("   - Basic Pitch 模型已成功加载")
        print("   - 音频转 MIDI 功能正常")
        print("   - Agent 集成工作正常")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息。")

    return passed == total


def main():
    """主函数"""
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

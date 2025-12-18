"""
乐理工具测试
测试和弦识别、调性分析和节奏分析功能
"""

import sys
from pathlib import Path
import tempfile
import numpy as np
import soundfile as sf

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_theory_tool_import():
    """测试 1: 导入乐理工具"""
    print("=" * 60)
    print("测试 1: 导入乐理工具")
    print("=" * 60)

    try:
        from src.tools import TheoryTool
        print("✅ TheoryTool 导入成功")

        tool = TheoryTool()
        print(f"✅ 工具名称: {tool.name}")
        print(f"✅ 工具描述: {tool.description[:100]}...")

        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_librosa_import():
    """测试 2: Librosa 依赖"""
    print("\n" + "=" * 60)
    print("测试 2: Librosa 依赖")
    print("=" * 60)

    try:
        import librosa
        print(f"✅ librosa 版本: {librosa.__version__}")

        import numpy as np
        print(f"✅ numpy 版本: {np.__version__}")

        return True
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        return False


def generate_chord_progression_audio():
    """测试 3: 生成和弦进行测试音频"""
    print("\n" + "=" * 60)
    print("测试 3: 生成和弦进行测试音频")
    print("=" * 60)

    try:
        sample_rate = 22050
        chord_duration = 2.0  # 每个和弦2秒

        # 定义和弦进行: C - Am - F - G (流行音乐常见进行)
        chords = [
            ("C", [261.63, 329.63, 392.00]),      # C major (C-E-G)
            ("Am", [220.00, 261.63, 329.63]),     # A minor (A-C-E)
            ("F", [174.61, 220.00, 261.63]),      # F major (F-A-C)
            ("G", [196.00, 246.94, 293.66]),      # G major (G-B-D)
        ]

        audio_segments = []

        for chord_name, frequencies in chords:
            # 生成和弦（三个音同时发声）
            t = np.linspace(0, chord_duration, int(sample_rate * chord_duration))

            # 添加包络
            envelope = np.exp(-1.5 * t / chord_duration)

            # 叠加三个音
            chord_audio = np.zeros_like(t)
            for freq in frequencies:
                chord_audio += 0.3 * np.sin(2 * np.pi * freq * t) * envelope

            audio_segments.append(chord_audio)

        # 合并所有和弦
        audio = np.concatenate(audio_segments)

        # 保存到临时文件
        temp_dir = Path(tempfile.gettempdir())
        test_audio_path = temp_dir / "test_chord_progression.wav"

        sf.write(test_audio_path, audio, sample_rate)

        print(f"✅ 测试音频已生成: {test_audio_path}")
        print(f"   和弦进行: C - Am - F - G")
        print(f"   每个和弦: {chord_duration} 秒")
        print(f"   总时长: {len(audio) / sample_rate:.1f} 秒")
        print(f"   采样率: {sample_rate} Hz")

        return str(test_audio_path)

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None


def test_chord_analysis(audio_path: str):
    """测试 4: 和弦识别"""
    print("\n" + "=" * 60)
    print("测试 4: 和弦识别")
    print("=" * 60)

    try:
        from src.tools import TheoryTool

        tool = TheoryTool()

        print(f"\n🎼 分析音频: {audio_path}")
        print("⏳ 正在识别和弦...")

        result = tool._run(audio_path=audio_path, analysis_type="chords")

        if result["success"]:
            print(f"\n✅ 和弦识别成功!")
            print(f"🎵 识别到的和弦: {result.get('chords', [])}")
            print(f"🎼 和弦进行: {result.get('chord_progression', '')}")
            print(f"📊 和弦数量: {result.get('chord_count', 0)}")

            if result.get('chord_times'):
                print(f"\n和弦时间点:")
                for i, (chord, time) in enumerate(zip(result['chords'], result['chord_times']), 1):
                    print(f"  {i}. {chord} - 起始: {time}s")

            return True
        else:
            print(f"\n❌ 识别失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_key_analysis(audio_path: str):
    """测试 5: 调性分析"""
    print("\n" + "=" * 60)
    print("测试 5: 调性分析")
    print("=" * 60)

    try:
        from src.tools import TheoryTool

        tool = TheoryTool()

        print(f"\n🎼 分析音频: {audio_path}")
        print("⏳ 正在分析调性...")

        result = tool._run(audio_path=audio_path, analysis_type="key")

        if result["success"]:
            print(f"\n✅ 调性分析成功!")
            print(f"🎹 调性: {result.get('key', 'Unknown')}")
            print(f"📊 置信度: {result.get('key_confidence', 0)}")

            return True
        else:
            print(f"\n❌ 分析失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_tempo_analysis(audio_path: str):
    """测试 6: 节奏分析"""
    print("\n" + "=" * 60)
    print("测试 6: 节奏分析")
    print("=" * 60)

    try:
        from src.tools import TheoryTool

        tool = TheoryTool()

        print(f"\n🎼 分析音频: {audio_path}")
        print("⏳ 正在分析节奏...")

        result = tool._run(audio_path=audio_path, analysis_type="tempo")

        if result["success"]:
            print(f"\n✅ 节奏分析成功!")
            print(f"🎵 速度: {result.get('tempo', 0)} BPM")
            print(f"📊 节拍数量: {result.get('beat_count', 0)}")

            if result.get('beat_times'):
                print(f"\n前几个节拍时间点:")
                for i, time in enumerate(result['beat_times'][:5], 1):
                    print(f"  {i}. {time}s")

            return True
        else:
            print(f"\n❌ 分析失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_full_analysis(audio_path: str):
    """测试 7: 完整分析"""
    print("\n" + "=" * 60)
    print("测试 7: 完整分析 (all)")
    print("=" * 60)

    try:
        from src.tools import TheoryTool

        tool = TheoryTool()

        print(f"\n🎼 分析音频: {audio_path}")
        print("⏳ 正在进行完整分析...")

        result = tool._run(audio_path=audio_path, analysis_type="all")

        if result["success"]:
            print(f"\n✅ 完整分析成功!")
            print(f"\n📊 分析结果:")
            print(f"  时长: {result.get('duration_seconds', 0)} 秒")
            print(f"  调性: {result.get('key', 'Unknown')}")
            print(f"  速度: {result.get('tempo', 0)} BPM")
            print(f"  和弦进行: {result.get('chord_progression', '')}")

            return True
        else:
            print(f"\n❌ 分析失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_agent_integration(audio_path: str):
    """测试 8: Agent 集成"""
    print("\n" + "=" * 60)
    print("测试 8: Agent 集成乐理工具")
    print("=" * 60)

    try:
        from src.agent import MusicAgent
        from src.tools import TheoryTool

        # 创建 Agent 并添加乐理工具
        agent = MusicAgent(verbose=True)
        agent.add_tool(TheoryTool())

        print(f"✅ Agent 创建成功")
        print(f"🔧 可用工具: {agent.get_available_tools()}")

        # 测试 Agent 分析音频
        print(f"\n测试 Agent 分析音频...")
        result = agent.process(f"请分析这个音频文件的和弦进行: {audio_path}")

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
    print("\n🎼 Algorhythm 乐理工具测试套件")
    print("=" * 60)

    results = []

    # 测试 1: 导入
    result1 = test_theory_tool_import()
    results.append(("导入乐理工具", result1))

    if not result1:
        print("\n⚠️  基础导入失败，跳过后续测试")
        return False

    # 测试 2: 依赖
    result2 = test_librosa_import()
    results.append(("Librosa 依赖", result2))

    if not result2:
        print("\n⚠️  依赖检查失败，跳过后续测试")
        return False

    # 测试 3: 生成测试音频
    audio_path = generate_chord_progression_audio()
    results.append(("生成测试音频", audio_path is not None))

    if not audio_path:
        print("\n⚠️  无法生成测试音频，跳过后续测试")
        return False

    # 测试 4-7: 各种分析
    result4 = test_chord_analysis(audio_path)
    results.append(("和弦识别", result4))

    result5 = test_key_analysis(audio_path)
    results.append(("调性分析", result5))

    result6 = test_tempo_analysis(audio_path)
    results.append(("节奏分析", result6))

    result7 = test_full_analysis(audio_path)
    results.append(("完整分析", result7))

    # 测试 8: Agent 集成
    result8 = test_agent_integration(audio_path)
    results.append(("Agent 集成", result8))

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
        print("\n🎉 所有测试通过！乐理工具已准备就绪。")
        print("\n📝 注意:")
        print("   - 和弦识别功能正常")
        print("   - 调性分析功能正常")
        print("   - 节奏分析功能正常")
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

"""
编曲工具测试
测试智能 Voicing 转换功能
"""

import sys
from pathlib import Path
import tempfile

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_arrangement_tool_import():
    """测试 1: 导入编曲工具"""
    print("=" * 60)
    print("测试 1: 导入编曲工具")
    print("=" * 60)

    try:
        from src.tools import ArrangementTool
        print("✅ ArrangementTool 导入成功")

        tool = ArrangementTool()
        print(f"✅ 工具名称: {tool.name}")
        print(f"✅ 工具描述: {tool.description[:100]}...")

        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_pretty_midi_import():
    """测试 2: Pretty MIDI 依赖"""
    print("\n" + "=" * 60)
    print("测试 2: Pretty MIDI 依赖")
    print("=" * 60)

    try:
        import pretty_midi
        print(f"✅ pretty_midi 导入成功")

        import numpy as np
        print(f"✅ numpy 版本: {np.__version__}")

        return True
    except ImportError as e:
        print(f"❌ 依赖缺失: {e}")
        return False


def generate_test_midi():
    """测试 3: 生成测试 MIDI 文件"""
    print("\n" + "=" * 60)
    print("测试 3: 生成测试 MIDI 文件")
    print("=" * 60)

    try:
        import pretty_midi

        # 创建 MIDI 对象
        midi = pretty_midi.PrettyMIDI()

        # 创建钢琴音轨 (Program 0 = Acoustic Grand Piano)
        piano = pretty_midi.Instrument(program=0, name="Piano")

        # 定义和弦进行: C - Am - F - G
        chords = [
            ("C", [60, 64, 67]),      # C major (C-E-G)
            ("Am", [57, 60, 64]),     # A minor (A-C-E)
            ("F", [53, 57, 60]),      # F major (F-A-C)
            ("G", [55, 59, 62]),      # G major (G-B-D)
        ]

        # 每个和弦 2 秒
        chord_duration = 2.0
        velocity = 80

        for i, (chord_name, pitches) in enumerate(chords):
            start_time = i * chord_duration

            # 添加和弦音符
            for pitch in pitches:
                note = pretty_midi.Note(
                    velocity=velocity,
                    pitch=pitch,
                    start=start_time,
                    end=start_time + chord_duration
                )
                piano.notes.append(note)

        midi.instruments.append(piano)

        # 保存到临时文件
        temp_dir = Path(tempfile.gettempdir())
        test_midi_path = temp_dir / "test_piano_chords.mid"

        midi.write(str(test_midi_path))

        print(f"✅ 测试 MIDI 已生成: {test_midi_path}")
        print(f"   和弦进行: C - Am - F - G")
        print(f"   每个和弦: {chord_duration} 秒")
        print(f"   总时长: {len(chords) * chord_duration:.1f} 秒")
        print(f"   音符数量: {len(piano.notes)}")

        return str(test_midi_path)

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None


def test_guitar_conversion(midi_path: str):
    """测试 4: 吉他 Voicing 转换"""
    print("\n" + "=" * 60)
    print("测试 4: 吉他 Voicing 转换")
    print("=" * 60)

    try:
        from src.tools import ArrangementTool

        tool = ArrangementTool()

        print(f"\n🎼 处理 MIDI: {midi_path}")
        print("⏳ 正在转换为吉他 Voicing...")

        result = tool._run(
            midi_path=midi_path,
            target_instrument="guitar"
        )

        if result["success"]:
            print(f"\n✅ 转换成功!")
            print(f"📁 输出文件: {result['output_path']}")
            print(f"🎵 音符数量: {result['note_count']}")
            print(f"⏱️  时长: {result['duration_seconds']} 秒")
            print(f"🎸 目标乐器: {result['target_instrument']}")

            # 验证输出文件存在
            output_path = Path(result['output_path'])
            if output_path.exists():
                print(f"✅ 输出文件已创建")

                # 读取并验证内容
                import pretty_midi
                guitar_midi = pretty_midi.PrettyMIDI(str(output_path))

                print(f"\n吉他 MIDI 信息:")
                print(f"  乐器数量: {len(guitar_midi.instruments)}")
                for inst in guitar_midi.instruments:
                    print(f"  - {inst.name}: {len(inst.notes)} 个音符")

                return True
            else:
                print(f"❌ 输出文件未创建")
                return False
        else:
            print(f"\n❌ 转换失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_bass_conversion(midi_path: str):
    """测试 5: 贝斯线生成"""
    print("\n" + "=" * 60)
    print("测试 5: 贝斯线生成")
    print("=" * 60)

    try:
        from src.tools import ArrangementTool

        tool = ArrangementTool()

        print(f"\n🎼 处理 MIDI: {midi_path}")
        print("⏳ 正在生成贝斯线...")

        result = tool._run(
            midi_path=midi_path,
            target_instrument="bass"
        )

        if result["success"]:
            print(f"\n✅ 转换成功!")
            print(f"📁 输出文件: {result['output_path']}")
            print(f"🎵 音符数量: {result['note_count']}")
            print(f"⏱️  时长: {result['duration_seconds']} 秒")
            print(f"🎸 目标乐器: {result['target_instrument']}")

            # 验证输出文件
            output_path = Path(result['output_path'])
            if output_path.exists():
                print(f"✅ 输出文件已创建")

                # 读取并验证内容
                import pretty_midi
                bass_midi = pretty_midi.PrettyMIDI(str(output_path))

                print(f"\n贝斯 MIDI 信息:")
                print(f"  乐器数量: {len(bass_midi.instruments)}")
                for inst in bass_midi.instruments:
                    print(f"  - {inst.name}: {len(inst.notes)} 个音符")

                    # 验证音域
                    if inst.notes:
                        pitches = [note.pitch for note in inst.notes]
                        print(f"  - 音域: {min(pitches)} - {max(pitches)} (MIDI)")

                return True
            else:
                print(f"❌ 输出文件未创建")
                return False
        else:
            print(f"\n❌ 转换失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_strings_conversion(midi_path: str):
    """测试 6: 弦乐编排"""
    print("\n" + "=" * 60)
    print("测试 6: 弦乐编排")
    print("=" * 60)

    try:
        from src.tools import ArrangementTool

        tool = ArrangementTool()

        print(f"\n🎼 处理 MIDI: {midi_path}")
        print("⏳ 正在转换为弦乐编排...")

        result = tool._run(
            midi_path=midi_path,
            target_instrument="strings"
        )

        if result["success"]:
            print(f"\n✅ 转换成功!")
            print(f"📁 输出文件: {result['output_path']}")
            print(f"🎵 音符数量: {result['note_count']}")
            print(f"⏱️  时长: {result['duration_seconds']} 秒")
            print(f"🎻 目标乐器: {result['target_instrument']}")

            # 验证输出文件
            output_path = Path(result['output_path'])
            if output_path.exists():
                print(f"✅ 输出文件已创建")

                # 读取并验证内容
                import pretty_midi
                strings_midi = pretty_midi.PrettyMIDI(str(output_path))

                print(f"\n弦乐 MIDI 信息:")
                print(f"  乐器数量: {len(strings_midi.instruments)}")
                for inst in strings_midi.instruments:
                    print(f"  - {inst.name}: {len(inst.notes)} 个音符")

                return True
            else:
                print(f"❌ 输出文件未创建")
                return False
        else:
            print(f"\n❌ 转换失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_agent_integration(midi_path: str):
    """测试 7: Agent 集成"""
    print("\n" + "=" * 60)
    print("测试 7: Agent 集成编曲工具")
    print("=" * 60)

    try:
        from src.agent import MusicAgent
        from src.tools import ArrangementTool

        # 创建 Agent 并添加编曲工具
        agent = MusicAgent(verbose=True)
        agent.add_tool(ArrangementTool())

        print(f"✅ Agent 创建成功")
        print(f"🔧 可用工具: {agent.get_available_tools()}")

        # 测试 Agent 处理编曲请求
        print(f"\n测试 Agent 编曲转换...")
        result = agent.process(f"请将这个 MIDI 文件转换为吉他编曲: {midi_path}")

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
    print("\n🎼 Algorhythm 编曲工具测试套件")
    print("=" * 60)

    results = []

    # 测试 1: 导入
    result1 = test_arrangement_tool_import()
    results.append(("导入编曲工具", result1))

    if not result1:
        print("\n⚠️  基础导入失败，跳过后续测试")
        return False

    # 测试 2: 依赖
    result2 = test_pretty_midi_import()
    results.append(("Pretty MIDI 依赖", result2))

    if not result2:
        print("\n⚠️  依赖检查失败，跳过后续测试")
        return False

    # 测试 3: 生成测试 MIDI
    midi_path = generate_test_midi()
    results.append(("生成测试 MIDI", midi_path is not None))

    if not midi_path:
        print("\n⚠️  无法生成测试 MIDI，跳过后续测试")
        return False

    # 测试 4-6: 各种转换
    result4 = test_guitar_conversion(midi_path)
    results.append(("吉他 Voicing 转换", result4))

    result5 = test_bass_conversion(midi_path)
    results.append(("贝斯线生成", result5))

    result6 = test_strings_conversion(midi_path)
    results.append(("弦乐编排", result6))

    # 测试 7: Agent 集成
    result7 = test_agent_integration(midi_path)
    results.append(("Agent 集成", result7))

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
        print("\n🎉 所有测试通过！编曲工具已准备就绪。")
        print("\n📝 注意:")
        print("   - 吉他 Voicing 转换功能正常")
        print("   - 贝斯线生成功能正常")
        print("   - 弦乐编排功能正常")
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

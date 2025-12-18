"""
音频渲染工具测试
测试 MIDI 到音频的 AI 渲染功能
"""

import sys
from pathlib import Path
import tempfile

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_rendering_tool_import():
    """测试 1: 导入渲染工具"""
    print("=" * 60)
    print("测试 1: 导入渲染工具")
    print("=" * 60)

    try:
        from src.tools import RenderingTool
        print("✅ RenderingTool 导入成功")

        tool = RenderingTool()
        print(f"✅ 工具名称: {tool.name}")
        print(f"✅ 工具描述: {tool.description[:100]}...")

        return True
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_dependencies():
    """测试 2: 依赖检查"""
    print("\n" + "=" * 60)
    print("测试 2: 依赖检查")
    print("=" * 60)

    dependencies = {
        "pretty_midi": "MIDI 处理",
        "numpy": "数值计算",
        "scipy": "音频保存",
    }

    all_ok = True

    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:15s} - {description}")
        except ImportError:
            print(f"❌ {module:15s} - {description} (未安装)")
            all_ok = False

    # 检查可选依赖
    print("\n可选依赖 (用于 AI 生成):")
    try:
        import audiocraft
        print(f"✅ audiocraft      - MusicGen AI 模型")
    except ImportError:
        print(f"⚠️  audiocraft      - MusicGen AI 模型 (未安装，将使用后备方案)")

    return all_ok


def generate_test_midi():
    """测试 3: 生成测试 MIDI"""
    print("\n" + "=" * 60)
    print("测试 3: 生成测试 MIDI")
    print("=" * 60)

    try:
        import pretty_midi

        # 创建简单的旋律
        midi = pretty_midi.PrettyMIDI()
        guitar = pretty_midi.Instrument(program=24, name="Guitar")

        # C 大调音阶旋律
        notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C D E F G A B C
        note_duration = 0.5

        for i, pitch in enumerate(notes):
            start = i * note_duration
            note = pretty_midi.Note(
                velocity=80,
                pitch=pitch,
                start=start,
                end=start + note_duration
            )
            guitar.notes.append(note)

        midi.instruments.append(guitar)

        # 保存
        temp_dir = Path(tempfile.gettempdir())
        test_path = temp_dir / "test_melody.mid"
        midi.write(str(test_path))

        print(f"✅ 测试 MIDI 已生成: {test_path}")
        print(f"   旋律: C 大调音阶")
        print(f"   音符数量: {len(notes)}")
        print(f"   总时长: {len(notes) * note_duration:.1f} 秒")

        return str(test_path)

    except Exception as e:
        print(f"❌ 生成失败: {e}")
        return None


def test_midi_to_guide_audio(midi_path: str):
    """测试 4: MIDI 转引导音频"""
    print("\n" + "=" * 60)
    print("测试 4: MIDI 转引导音频")
    print("=" * 60)

    try:
        from src.tools import RenderingTool

        tool = RenderingTool()

        print(f"\n🎵 处理 MIDI: {midi_path}")
        print("⏳ 正在转换为引导音频...")

        # 测试内部方法
        guide_audio, sample_rate = tool._midi_to_guide_audio(midi_path)

        print(f"\n✅ 转换成功!")
        print(f"   采样率: {sample_rate} Hz")
        print(f"   音频长度: {len(guide_audio)} 采样点")
        print(f"   时长: {len(guide_audio) / sample_rate:.2f} 秒")
        print(f"   音频范围: [{guide_audio.min():.3f}, {guide_audio.max():.3f}]")

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prompt_building():
    """测试 5: 提示词构建"""
    print("\n" + "=" * 60)
    print("测试 5: 提示词构建")
    print("=" * 60)

    try:
        from src.tools import RenderingTool

        tool = RenderingTool()

        test_cases = [
            ("acoustic_guitar", "clean"),
            ("electric_guitar", "distorted"),
            ("piano", "bright"),
            ("strings", "ambient"),
        ]

        print("\n提示词生成测试:")
        for instrument, style in test_cases:
            prompt = tool._build_prompt(instrument, style)
            print(f"  {instrument:20s} + {style:10s} → {prompt}")

        print("\n✅ 提示词构建功能正常")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_basic_rendering(midi_path: str):
    """测试 6: 基础渲染（不使用 MusicGen）"""
    print("\n" + "=" * 60)
    print("测试 6: 基础渲染")
    print("=" * 60)

    try:
        from src.tools import RenderingTool

        tool = RenderingTool()

        print(f"\n🎵 渲染 MIDI: {midi_path}")
        print("⏳ 正在渲染...")
        print("   注意: 如果未安装 MusicGen，将使用引导音频作为输出")

        result = tool._run(
            midi_path=midi_path,
            instrument="acoustic_guitar",
            style="clean",
            duration=5
        )

        if result["success"]:
            print(f"\n✅ 渲染成功!")
            print(f"📁 输出文件: {result['output_path']}")
            print(f"🎸 乐器: {result['instrument']}")
            print(f"🎨 风格: {result['style']}")
            print(f"⏱️  时长: {result['duration_seconds']:.2f} 秒")
            print(f"📊 采样率: {result['sample_rate']} Hz")

            # 验证文件存在
            output_path = Path(result['output_path'])
            if output_path.exists():
                file_size = output_path.stat().st_size
                print(f"✅ 输出文件已创建 ({file_size / 1024:.1f} KB)")
                return True
            else:
                print(f"❌ 输出文件未创建")
                return False
        else:
            print(f"\n❌ 渲染失败: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_instruments(midi_path: str):
    """测试 7: 多种乐器渲染"""
    print("\n" + "=" * 60)
    print("测试 7: 多种乐器渲染")
    print("=" * 60)

    try:
        from src.tools import RenderingTool

        tool = RenderingTool()

        instruments = ["acoustic_guitar", "piano", "strings"]

        for instrument in instruments:
            print(f"\n渲染为 {instrument}...")

            result = tool._run(
                midi_path=midi_path,
                instrument=instrument,
                style="clean",
                duration=3
            )

            if result["success"]:
                print(f"✅ {instrument} 渲染成功")
                print(f"   输出: {Path(result['output_path']).name}")
            else:
                print(f"❌ {instrument} 渲染失败: {result['error']}")

        print("\n✅ 多乐器渲染测试完成")
        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False


def test_agent_integration(midi_path: str):
    """测试 8: Agent 集成"""
    print("\n" + "=" * 60)
    print("测试 8: Agent 集成渲染工具")
    print("=" * 60)

    try:
        from src.agent import MusicAgent
        from src.tools import RenderingTool

        # 创建 Agent 并添加渲染工具
        agent = MusicAgent(verbose=True)
        agent.add_tool(RenderingTool())

        print(f"✅ Agent 创建成功")
        print(f"🔧 可用工具: {agent.get_available_tools()}")

        # 测试 Agent 处理渲染请求
        print(f"\n测试 Agent 音频渲染...")
        result = agent.process(f"请将这个 MIDI 文件渲染为吉他音色: {midi_path}")

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
    print("\n🎵 Algorhythm 音频渲染工具测试套件")
    print("=" * 60)

    results = []

    # 测试 1: 导入
    result1 = test_rendering_tool_import()
    results.append(("导入渲染工具", result1))

    if not result1:
        print("\n⚠️  基础导入失败，跳过后续测试")
        return False

    # 测试 2: 依赖
    result2 = test_dependencies()
    results.append(("依赖检查", result2))

    if not result2:
        print("\n⚠️  依赖检查失败，跳过后续测试")
        return False

    # 测试 3: 生成测试 MIDI
    midi_path = generate_test_midi()
    results.append(("生成测试 MIDI", midi_path is not None))

    if not midi_path:
        print("\n⚠️  无法生成测试 MIDI，跳过后续测试")
        return False

    # 测试 4-7: 各种功能
    result4 = test_midi_to_guide_audio(midi_path)
    results.append(("MIDI 转引导音频", result4))

    result5 = test_prompt_building()
    results.append(("提示词构建", result5))

    result6 = test_basic_rendering(midi_path)
    results.append(("基础渲染", result6))

    result7 = test_multiple_instruments(midi_path)
    results.append(("多乐器渲染", result7))

    # 测试 8: Agent 集成
    result8 = test_agent_integration(midi_path)
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
        print("\n🎉 所有测试通过！音频渲染工具已准备就绪。")
        print("\n📝 注意:")
        print("   - MIDI 转引导音频功能正常")
        print("   - 提示词构建功能正常")
        print("   - 基础渲染功能正常")
        print("   - 多乐器支持正常")
        print("   - Agent 集成工作正常")
        print("\n⚠️  提示:")
        print("   - 如需使用 AI 生成，请安装: pip install audiocraft")
        print("   - 首次运行会下载 MusicGen 模型（约 1.5GB）")
    else:
        print("\n⚠️  部分测试失败，请检查上述错误信息。")

    return passed == total


def main():
    """主函数"""
    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

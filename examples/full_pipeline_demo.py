"""
完整音乐制作流程演示
展示从音频输入到最终音频渲染的完整 AI 驱动流程
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools import HearingTool, TheoryTool, ArrangementTool, RenderingTool
import tempfile
import numpy as np
import soundfile as sf


def create_demo_audio():
    """创建演示用的音频文件（简单旋律）"""
    print("🎤 创建演示音频...")

    sample_rate = 22050
    note_duration = 0.5

    # C 大调音阶旋律
    frequencies = [
        261.63,  # C4
        293.66,  # D4
        329.63,  # E4
        349.23,  # F4
        392.00,  # G4
        440.00,  # A4
        493.88,  # B4
        523.25,  # C5
    ]

    audio_segments = []

    for freq in frequencies:
        t = np.linspace(0, note_duration, int(sample_rate * note_duration))
        # 添加包络
        envelope = np.exp(-2 * t / note_duration)
        note_audio = 0.5 * np.sin(2 * np.pi * freq * t) * envelope
        audio_segments.append(note_audio)

    # 合并
    audio = np.concatenate(audio_segments)

    # 保存
    temp_dir = Path(tempfile.gettempdir())
    audio_path = temp_dir / "demo_input_audio.wav"
    sf.write(audio_path, audio, sample_rate)

    print(f"✅ 演示音频已创建: {audio_path}")
    print(f"   旋律: C 大调音阶")
    print(f"   时长: {len(audio) / sample_rate:.1f} 秒")

    return str(audio_path)


def step1_audio_to_midi(audio_path: str):
    """步骤 1: 音频转 MIDI"""
    print("\n" + "=" * 60)
    print("步骤 1: 听觉工具 - 音频转 MIDI")
    print("=" * 60)

    tool = HearingTool()

    print(f"\n🎵 输入音频: {audio_path}")
    print("⏳ 正在转换...")

    result = tool._run(audio_path=audio_path)

    if result["success"]:
        print(f"\n✅ 转换成功!")
        print(f"📁 MIDI 文件: {result['midi_path']}")
        print(f"🎵 音符数量: {result['note_count']}")
        print(f"⏱️  时长: {result['duration_seconds']} 秒")
        print(f"🎹 乐器数量: {result['instrument_count']}")
        print(f"🎼 估计速度: {result['tempo']} BPM")

        return result['midi_path']
    else:
        print(f"\n❌ 转换失败: {result['error']}")
        return None


def step2_analyze_theory(audio_path: str):
    """步骤 2: 乐理分析"""
    print("\n" + "=" * 60)
    print("步骤 2: 乐理工具 - 和弦与调性分析")
    print("=" * 60)

    tool = TheoryTool()

    print(f"\n🎼 分析音频: {audio_path}")
    print("⏳ 正在分析...")

    result = tool._run(audio_path=audio_path, analysis_type="all")

    if result["success"]:
        print(f"\n✅ 分析成功!")
        print(f"🎹 调性: {result.get('key', 'Unknown')}")
        print(f"📊 置信度: {result.get('key_confidence', 0)}")
        print(f"🎵 速度: {result.get('tempo', 0)} BPM")
        print(f"🎼 和弦进行: {result.get('chord_progression', '')}")

        return result
    else:
        print(f"\n❌ 分析失败: {result['error']}")
        return None


def step3_arrange_for_guitar(midi_path: str):
    """步骤 3: 智能吉他编曲"""
    print("\n" + "=" * 60)
    print("步骤 3: 编曲工具 - 智能吉他 Voicing 转换")
    print("=" * 60)

    tool = ArrangementTool()

    print(f"\n🎸 转换 MIDI: {midi_path}")
    print("⏳ 正在转换为吉他编曲...")

    result = tool._run(
        midi_path=midi_path,
        target_instrument="guitar",
        style="folk"
    )

    if result["success"]:
        print(f"\n✅ 转换成功!")
        print(f"📁 吉他 MIDI: {result['output_path']}")
        print(f"🎵 音符数量: {result['note_count']}")
        print(f"🎸 目标乐器: {result['target_instrument']}")

        return result['output_path']
    else:
        print(f"\n❌ 转换失败: {result['error']}")
        return None


def step4_render_audio(midi_path: str):
    """步骤 4: AI 音频渲染"""
    print("\n" + "=" * 60)
    print("步骤 4: 渲染工具 - AI 音频生成")
    print("=" * 60)

    tool = RenderingTool()

    print(f"\n🎨 渲染 MIDI: {midi_path}")
    print("⏳ 正在生成音频...")

    result = tool._run(
        midi_path=midi_path,
        instrument="acoustic_guitar",
        style="clean",
        duration=5
    )

    if result["success"]:
        print(f"\n✅ 渲染成功!")
        print(f"📁 音频文件: {result['output_path']}")
        print(f"🎸 乐器: {result['instrument']}")
        print(f"🎨 风格: {result['style']}")
        print(f"⏱️  时长: {result['duration_seconds']:.2f} 秒")
        print(f"📊 采样率: {result['sample_rate']} Hz")

        return result['output_path']
    else:
        print(f"\n❌ 渲染失败: {result['error']}")
        return None


def main():
    """主函数 - 完整流程"""
    print("\n" + "=" * 60)
    print("🎵 Algorhythm 完整音乐制作流程演示")
    print("=" * 60)

    print("\n📝 流程概览:")
    print("  1. 听觉工具: 音频 → MIDI")
    print("  2. 乐理工具: 和弦/调性/节奏分析")
    print("  3. 编曲工具: 智能吉他 Voicing 转换")
    print("  4. 渲染工具: AI 音频生成")

    # 创建演示音频
    audio_path = create_demo_audio()

    # 步骤 1: 音频转 MIDI
    midi_path = step1_audio_to_midi(audio_path)
    if not midi_path:
        print("\n❌ 流程中断：音频转 MIDI 失败")
        return

    # 步骤 2: 乐理分析
    theory_result = step2_analyze_theory(audio_path)
    if not theory_result:
        print("\n⚠️  乐理分析失败，但继续流程")

    # 步骤 3: 吉他编曲
    guitar_midi_path = step3_arrange_for_guitar(midi_path)
    if not guitar_midi_path:
        print("\n❌ 流程中断：吉他编曲失败")
        return

    # 步骤 4: 音频渲染
    final_audio_path = step4_render_audio(guitar_midi_path)
    if not final_audio_path:
        print("\n❌ 流程中断：音频渲染失败")
        return

    # 总结
    print("\n" + "=" * 60)
    print("✅ 完整流程执行成功！")
    print("=" * 60)

    print("\n📊 流程总结:")
    print(f"  输入音频: {Path(audio_path).name}")
    print(f"  中间 MIDI: {Path(midi_path).name}")
    print(f"  吉他 MIDI: {Path(guitar_midi_path).name}")
    print(f"  最终音频: {Path(final_audio_path).name}")

    print("\n🎯 技术栈:")
    print("  • Basic Pitch: 音频转 MIDI")
    print("  • Librosa: 乐理分析")
    print("  • Smart Guitar Voicing: 智能指法映射")
    print("  • MusicGen-Melody: AI 音频生成")

    print("\n💡 核心创新:")
    print("  ✅ 真实吉他指法库（12+ 常见和弦）")
    print("  ✅ 扫弦人性化（5-15ms 随机延迟）")
    print("  ✅ 和弦自动识别（音程模式匹配）")
    print("  ✅ AI 音频生成（旋律条件生成）")

    print("\n🎉 Algorhythm - 让 AI 成为你的音乐制作伙伴！")


if __name__ == "__main__":
    main()

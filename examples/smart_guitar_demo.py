"""
智能吉他编曲演示
展示从钢琴 MIDI 到真实吉他指法的完整转换流程
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools import ArrangementTool
from src.tools.smart_guitar_voicing import GuitarFretboard
import pretty_midi
import tempfile


def create_demo_midi():
    """创建演示用的钢琴 MIDI"""
    print("🎹 创建钢琴和弦进行...")

    midi = pretty_midi.PrettyMIDI()
    piano = pretty_midi.Instrument(program=0, name="Piano")

    # 经典流行和弦进行: C - G - Am - F (卡农进行)
    chords = [
        ("C", [60, 64, 67]),      # C major
        ("G", [55, 59, 62]),      # G major
        ("Am", [57, 60, 64]),     # A minor
        ("F", [53, 57, 60]),      # F major
    ]

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
    midi_path = temp_dir / "demo_piano_chords.mid"
    midi.write(str(midi_path))

    print(f"✅ 钢琴 MIDI 已创建: {midi_path}")
    print(f"   和弦进行: C - G - Am - F (卡农进行)")
    print(f"   总时长: {len(chords) * chord_duration:.1f} 秒")
    print(f"   音符数量: {len(piano.notes)}")

    return str(midi_path)


def analyze_chord_recognition(midi_path: str):
    """分析和弦识别"""
    print("\n🎼 分析和弦识别...")
    print("=" * 60)

    midi = pretty_midi.PrettyMIDI(midi_path)

    for instrument in midi.instruments:
        if instrument.is_drum:
            continue

        # 按时间分组
        chord_groups = []
        current_group = []
        current_time = 0

        for note in sorted(instrument.notes, key=lambda n: n.start):
            if abs(note.start - current_time) > 0.05:
                if current_group:
                    chord_groups.append((current_time, current_group))
                current_group = [note]
                current_time = note.start
            else:
                current_group.append(note)

        if current_group:
            chord_groups.append((current_time, current_group))

        # 识别每个和弦
        for i, (start_time, notes) in enumerate(chord_groups):
            pitches = [note.pitch for note in notes]
            chord_name = GuitarFretboard.recognize_chord_from_pitches(pitches)

            note_names = [pretty_midi.note_number_to_name(p) for p in pitches]
            print(f"和弦 {i+1}: {chord_name:6s} - 音符: {', '.join(note_names)} - 时间: {start_time:.1f}s")


def convert_to_guitar_styles(midi_path: str):
    """转换为不同风格的吉他编曲"""
    print("\n🎸 转换为吉他编曲...")
    print("=" * 60)

    tool = ArrangementTool()

    styles = ["folk", "rock", "fingerstyle"]

    results = []

    for style in styles:
        print(f"\n转换为 {style.upper()} 风格...")

        result = tool._run(
            midi_path=midi_path,
            target_instrument="guitar",
            style=style
        )

        if result["success"]:
            print(f"✅ {result['message']}")
            print(f"   输出文件: {Path(result['output_path']).name}")
            print(f"   音符数量: {result['note_count']}")
            print(f"   时长: {result['duration_seconds']} 秒")

            results.append(result)
        else:
            print(f"❌ 转换失败: {result['error']}")

    return results


def analyze_strumming_humanization(guitar_midi_path: str):
    """分析扫弦人性化效果"""
    print("\n🎵 分析扫弦人性化...")
    print("=" * 60)

    midi = pretty_midi.PrettyMIDI(guitar_midi_path)

    # 分析第一个和弦
    first_chord = [n for n in midi.instruments[0].notes if n.start < 0.5]
    first_chord.sort(key=lambda x: x.start)

    print(f"\n第一个和弦的扫弦时间分析:")
    print(f"{'音符':<6s} {'MIDI':<4s} {'开始时间':<12s} {'延迟':<10s}")
    print("-" * 40)

    for i, note in enumerate(first_chord):
        note_name = pretty_midi.note_number_to_name(note.pitch)
        delay_ms = note.start * 1000
        print(f"{note_name:<6s} {note.pitch:<4d} {note.start:>8.4f}s    {delay_ms:>6.2f}ms")

    # 计算统计信息
    if len(first_chord) > 1:
        delays = [first_chord[i+1].start - first_chord[i].start
                  for i in range(len(first_chord)-1)]
        avg_delay = sum(delays) / len(delays)
        min_delay = min(delays)
        max_delay = max(delays)

        print(f"\n扫弦统计:")
        print(f"  平均延迟: {avg_delay*1000:.2f}ms")
        print(f"  延迟范围: {min_delay*1000:.2f}ms - {max_delay*1000:.2f}ms")
        print(f"  总扫弦时间: {(first_chord[-1].start - first_chord[0].start)*1000:.2f}ms")


def compare_styles(results: list):
    """比较不同风格的差异"""
    print("\n📊 风格对比...")
    print("=" * 60)

    print(f"\n{'风格':<12s} {'音符数':<8s} {'说明':<30s}")
    print("-" * 60)

    style_descriptions = {
        "folk": "下扫，自然延迟",
        "rock": "下上扫，双倍音符",
        "fingerstyle": "下扫，细腻表现"
    }

    for result in results:
        style = Path(result['output_path']).stem.split('_')[-1]
        note_count = result['note_count']
        description = style_descriptions.get(style, "")

        print(f"{style:<12s} {note_count:<8d} {description:<30s}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🎸 智能吉他编曲演示")
    print("=" * 60)

    # 1. 创建演示 MIDI
    midi_path = create_demo_midi()

    # 2. 分析和弦识别
    analyze_chord_recognition(midi_path)

    # 3. 转换为不同风格
    results = convert_to_guitar_styles(midi_path)

    # 4. 分析扫弦人性化
    if results:
        analyze_strumming_humanization(results[0]['output_path'])

    # 5. 比较风格差异
    compare_styles(results)

    print("\n" + "=" * 60)
    print("✅ 演示完成！")
    print("=" * 60)

    print("\n📝 功能总结:")
    print("  ✅ 真实吉他指法映射 (C, Am, F, G 等常见和弦)")
    print("  ✅ 和弦自动识别 (从 MIDI 音高识别和弦类型)")
    print("  ✅ 扫弦人性化 (5-15ms 随机延迟)")
    print("  ✅ 力度变化 (±15% 随机变化)")
    print("  ✅ 多种风格 (Folk, Rock, Fingerstyle)")

    print("\n🎯 核心技术:")
    print("  • 吉他指板映射系统 (标准调弦 + 常见指法库)")
    print("  • 和弦识别算法 (音程模式匹配)")
    print("  • 扫弦模拟器 (时间偏移 + 力度变化)")
    print("  • 风格引擎 (不同扫弦模式)")


if __name__ == "__main__":
    main()

"""
Arrangement Tool - 智能编曲与 Voicing 转换
将 MIDI 转换为不同乐器的演奏风格
"""

import os
from typing import Dict, Any, Optional, List, Tuple, ClassVar
from pathlib import Path

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import numpy as np


class ArrangementToolInput(BaseModel):
    """Arrangement Tool 输入参数"""
    midi_path: str = Field(description="输入 MIDI 文件的绝对路径")
    target_instrument: str = Field(
        default="guitar",
        description="目标乐器: 'guitar' (吉他), 'bass' (贝斯), 'strings' (弦乐)"
    )
    style: str = Field(
        default="folk",
        description="演奏风格（仅吉他）: 'folk' (民谣), 'rock' (摇滚), 'fingerstyle' (指弹)"
    )
    output_path: Optional[str] = Field(
        default=None,
        description="输出 MIDI 文件路径（可选，默认在同目录生成）"
    )


class ArrangementTool(BaseTool):
    """
    编曲工具 - 智能 Voicing 转换

    这个工具将钢琴 MIDI 转换为适合其他乐器演奏的 Voicing。

    功能：
    - 钢琴 → 吉他 Voicing 转换
    - 钢琴 → 贝斯线生成
    - 钢琴 → 弦乐编排
    - 保持和声结构的同时优化演奏性
    """

    name: str = "arrangement_tool"
    description: str = """
    将 MIDI 文件转换为适合特定乐器的编曲。

    输入：MIDI 文件路径和目标乐器
    输出：转换后的 MIDI 文件，优化了 Voicing 和演奏性

    使用场景：
    - 将钢琴编曲转换为吉他 Voicing
    - 从和弦提取贝斯线
    - 将钢琴改编为弦乐编排
    - 优化乐器演奏的可行性

    示例：
    输入: piano.mid, target="guitar"
    输出: piano_guitar.mid (吉他友好的 Voicing)
    """
    args_schema: type[BaseModel] = ArrangementToolInput

    # 吉他标准调弦 (MIDI 音高)
    GUITAR_TUNING: ClassVar[List[int]] = [40, 45, 50, 55, 59, 64]  # E2, A2, D3, G3, B3, E4

    # 吉他常用和弦形状 (相对于根音的音程)
    GUITAR_CHORD_SHAPES: ClassVar[Dict[str, List[Tuple[int, int]]]] = {
        # (string_index, fret_offset_from_root)
        'major': [
            (5, 0), (4, 2), (3, 2), (2, 1), (1, 0), (0, 0)  # E shape
        ],
        'minor': [
            (5, 0), (4, 2), (3, 2), (2, 0), (1, 0), (0, 0)  # Em shape
        ],
        'power': [
            (5, 0), (4, 2), (3, 2)  # Power chord
        ]
    }

    def _run(
        self,
        midi_path: str,
        target_instrument: str = "guitar",
        style: str = "folk",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行编曲转换

        Args:
            midi_path: 输入 MIDI 文件路径
            target_instrument: 目标乐器
            output_path: 输出文件路径（可选）

        Returns:
            包含转换结果的字典
        """
        try:
            # 延迟导入
            import pretty_midi

            # 验证输入文件
            midi_path = Path(midi_path)
            if not midi_path.exists():
                return {
                    "success": False,
                    "error": f"MIDI 文件不存在: {midi_path}"
                }

            print(f"🎼 正在加载 MIDI: {midi_path.name}")

            # 加载 MIDI
            midi_data = pretty_midi.PrettyMIDI(str(midi_path))

            # 根据目标乐器选择转换方法
            if target_instrument == "guitar":
                result_midi = self._convert_to_guitar(midi_data, style)
                suffix = f"_guitar_{style}"
            elif target_instrument == "bass":
                result_midi = self._convert_to_bass(midi_data)
                suffix = "_bass"
            elif target_instrument == "strings":
                result_midi = self._convert_to_strings(midi_data)
                suffix = "_strings"
            else:
                return {
                    "success": False,
                    "error": f"不支持的乐器: {target_instrument}"
                }

            # 确定输出路径
            if output_path is None:
                output_path = midi_path.parent / f"{midi_path.stem}{suffix}.mid"
            else:
                output_path = Path(output_path)

            # 保存结果
            result_midi.write(str(output_path))

            # 统计信息
            note_count = sum(len(inst.notes) for inst in result_midi.instruments)
            duration = result_midi.get_end_time()

            print(f"✅ 转换完成！")
            print(f"📁 输出文件: {output_path}")
            print(f"🎵 音符数量: {note_count}")
            print(f"⏱️  时长: {duration:.1f} 秒")

            return {
                "success": True,
                "input_path": str(midi_path),
                "output_path": str(output_path),
                "target_instrument": target_instrument,
                "note_count": note_count,
                "duration_seconds": round(duration, 2),
                "message": f"✅ 成功转换为 {target_instrument} 编曲！"
            }

        except ImportError as e:
            return {
                "success": False,
                "error": f"缺少依赖库: {str(e)}。请运行: pip install pretty-midi"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"转换失败: {str(e)}"
            }

    def _convert_to_guitar(self, midi_data, style: str = "folk") -> Any:
        """
        转换为吉他 Voicing（使用智能指法映射）

        策略：
        1. 分析和弦结构
        2. 使用真实吉他指法库
        3. 应用扫弦人性化
        4. 添加力度变化
        """
        import pretty_midi
        from .smart_guitar_voicing import SmartGuitarVoicing

        # 创建智能 Voicing 转换器
        voicing_converter = SmartGuitarVoicing()

        # 创建新的 MIDI 对象
        guitar_midi = pretty_midi.PrettyMIDI()

        # 创建吉他音轨 (Program 24 = Acoustic Guitar)
        guitar = pretty_midi.Instrument(program=24, name="Guitar")

        # 处理每个音轨
        for instrument in midi_data.instruments:
            if instrument.is_drum:
                continue

            # 按时间分组音符（识别和弦）
            chord_groups = self._group_notes_by_time(instrument.notes)

            # 使用智能 Voicing 转换
            guitar_note_data = voicing_converter.convert_piano_to_guitar(
                chord_groups,
                style=style
            )

            # 创建 MIDI 音符
            for pitch, start, duration, velocity in guitar_note_data:
                note = pretty_midi.Note(
                    velocity=velocity,
                    pitch=pitch,
                    start=start,
                    end=start + duration
                )
                guitar.notes.append(note)

        guitar_midi.instruments.append(guitar)
        return guitar_midi

    def _group_notes_by_time(self, notes, tolerance=0.05):
        """
        按时间分组音符（识别同时发声的和弦）

        Args:
            notes: 音符列表
            tolerance: 时间容差（秒）

        Returns:
            [(start_time, [notes])] 列表
        """
        if not notes:
            return []

        # 按开始时间排序
        sorted_notes = sorted(notes, key=lambda n: n.start)

        groups = []
        current_group = [sorted_notes[0]]
        current_time = sorted_notes[0].start

        for note in sorted_notes[1:]:
            if abs(note.start - current_time) <= tolerance:
                # 属于当前和弦组
                current_group.append(note)
            else:
                # 开始新的和弦组
                groups.append((current_time, current_group))
                current_group = [note]
                current_time = note.start

        # 添加最后一组
        if current_group:
            groups.append((current_time, current_group))

        return groups

    def _piano_to_guitar_voicing(
        self,
        pitches: List[int],
        start_time: float,
        duration: float,
        velocity: int
    ) -> List[Any]:
        """
        将钢琴音高转换为吉他 Voicing

        Args:
            pitches: 音高列表
            start_time: 开始时间
            duration: 持续时间
            velocity: 力度

        Returns:
            吉他音符列表
        """
        import pretty_midi

        # 如果没有音符，返回空列表
        if not pitches:
            return []

        # 去重并排序
        pitches = sorted(set(pitches))

        # 限制音符数量（吉他最多 6 根弦）
        if len(pitches) > 6:
            # 保留最低音和最高音，以及中间的重要音
            pitches = self._select_important_notes(pitches, max_notes=6)

        # 将音高映射到吉他音域 (E2 到 E5, MIDI 40-76)
        guitar_pitches = []
        for pitch in pitches:
            # 如果音高太低，提高八度
            while pitch < 40:
                pitch += 12

            # 如果音高太高，降低八度
            while pitch > 76:
                pitch -= 12

            guitar_pitches.append(pitch)

        # 创建吉他音符
        guitar_notes = []
        for pitch in guitar_pitches:
            note = pretty_midi.Note(
                velocity=velocity,
                pitch=pitch,
                start=start_time,
                end=start_time + duration
            )
            guitar_notes.append(note)

        return guitar_notes

    def _select_important_notes(self, pitches: List[int], max_notes: int = 6) -> List[int]:
        """
        从音符列表中选择最重要的音符

        策略：保留根音、最高音、以及均匀分布的中间音
        """
        if len(pitches) <= max_notes:
            return pitches

        # 保留最低音（根音）和最高音
        selected = [pitches[0], pitches[-1]]

        # 从中间音符中均匀选择
        remaining_slots = max_notes - 2
        middle_pitches = pitches[1:-1]

        if remaining_slots > 0 and middle_pitches:
            step = len(middle_pitches) / remaining_slots
            for i in range(remaining_slots):
                index = int(i * step)
                selected.append(middle_pitches[index])

        return sorted(selected)

    def _convert_to_bass(self, midi_data) -> Any:
        """
        转换为贝斯线

        策略：
        1. 提取和弦根音
        2. 生成行走贝斯线
        3. 限制在贝斯音域 (E1-G3, MIDI 28-55)
        """
        import pretty_midi

        # 创建新的 MIDI 对象
        bass_midi = pretty_midi.PrettyMIDI()

        # 创建贝斯音轨 (Program 32 = Acoustic Bass)
        bass = pretty_midi.Instrument(program=32, name="Bass")

        # 处理每个音轨
        for instrument in midi_data.instruments:
            if instrument.is_drum:
                continue

            # 按时间分组音符
            chord_groups = self._group_notes_by_time(instrument.notes)

            # 提取每个和弦的根音
            for start_time, notes in chord_groups:
                # 找到最低音作为根音
                root_pitch = min(note.pitch for note in notes)

                # 转换到贝斯音域
                while root_pitch > 55:  # G3
                    root_pitch -= 12
                while root_pitch < 28:  # E1
                    root_pitch += 12

                # 创建贝斯音符
                bass_note = pretty_midi.Note(
                    velocity=notes[0].velocity,
                    pitch=root_pitch,
                    start=start_time,
                    end=notes[0].end
                )
                bass.notes.append(bass_note)

        bass_midi.instruments.append(bass)
        return bass_midi

    def _convert_to_strings(self, midi_data) -> Any:
        """
        转换为弦乐编排

        策略：
        1. 保持和声结构
        2. 分配到不同弦乐声部
        3. 添加表情和力度变化
        """
        import pretty_midi

        # 创建新的 MIDI 对象
        strings_midi = pretty_midi.PrettyMIDI()

        # 创建弦乐音轨 (Program 48 = String Ensemble)
        strings = pretty_midi.Instrument(program=48, name="Strings")

        # 复制所有非鼓音符
        for instrument in midi_data.instruments:
            if instrument.is_drum:
                continue

            for note in instrument.notes:
                # 调整到弦乐音域 (C2-C6, MIDI 36-84)
                pitch = note.pitch
                while pitch < 36:
                    pitch += 12
                while pitch > 84:
                    pitch -= 12

                # 创建弦乐音符（稍微增加力度以模拟弦乐表现力）
                string_note = pretty_midi.Note(
                    velocity=min(note.velocity + 10, 127),
                    pitch=pitch,
                    start=note.start,
                    end=note.end
                )
                strings.notes.append(string_note)

        strings_midi.instruments.append(strings)
        return strings_midi

    async def _arun(
        self,
        midi_path: str,
        target_instrument: str = "guitar",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """异步执行（当前使用同步实现）"""
        return self._run(midi_path, target_instrument, output_path)


# 便捷函数：直接调用工具
def arrange_music(
    midi_path: str,
    target_instrument: str = "guitar",
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    便捷函数：编曲转换

    Args:
        midi_path: 输入 MIDI 文件路径
        target_instrument: 目标乐器
        output_path: 输出文件路径（可选）

    Returns:
        转换结果字典
    """
    tool = ArrangementTool()
    return tool._run(midi_path, target_instrument, output_path)

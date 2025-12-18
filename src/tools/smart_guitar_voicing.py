"""
Smart Guitar Voicing - 智能吉他指法映射
将和弦转换为真实的吉他指板位置和扫弦模式
"""

from typing import Dict, List, Tuple, Optional
import numpy as np


class GuitarFretboard:
    """吉他指板映射系统"""

    # 标准调弦 (MIDI 音高)
    STANDARD_TUNING = [40, 45, 50, 55, 59, 64]  # E2, A2, D3, G3, B3, E4

    # 音符名称到半音的映射
    NOTE_TO_SEMITONE = {
        'C': 0, 'C#': 1, 'Db': 1,
        'D': 2, 'D#': 3, 'Eb': 3,
        'E': 4,
        'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8,
        'A': 9, 'A#': 10, 'Bb': 10,
        'B': 11
    }

    # 常见吉他和弦指法库 (string_index: fret, -1 表示不弹)
    CHORD_SHAPES = {
        # C 大调和弦
        'C': [(-1, 3, 2, 0, 1, 0), (0, 3, 2, 0, 1, 0)],  # x32010 或 032010
        'Cmaj7': [(0, 3, 2, 0, 0, 0)],  # 032000
        'C7': [(0, 3, 2, 3, 1, 0)],  # 032310

        # D 大调和弦
        'D': [(-1, -1, 0, 2, 3, 2)],  # xx0232
        'Dm': [(-1, -1, 0, 2, 3, 1)],  # xx0231
        'D7': [(-1, -1, 0, 2, 1, 2)],  # xx0212

        # E 大调和弦
        'E': [(0, 2, 2, 1, 0, 0)],  # 022100
        'Em': [(0, 2, 2, 0, 0, 0)],  # 022000
        'E7': [(0, 2, 0, 1, 0, 0)],  # 020100

        # F 大调和弦
        'F': [(1, 3, 3, 2, 1, 1)],  # 133211 (封闭和弦)
        'Fm': [(1, 3, 3, 1, 1, 1)],  # 133111

        # G 大调和弦
        'G': [(3, 2, 0, 0, 0, 3), (3, 2, 0, 0, 3, 3)],  # 320003 或 320033
        'Gm': [(3, 5, 5, 3, 3, 3)],  # 355333
        'G7': [(3, 2, 0, 0, 0, 1)],  # 320001

        # A 大调和弦
        'A': [(-1, 0, 2, 2, 2, 0)],  # x02220
        'Am': [(-1, 0, 2, 2, 1, 0)],  # x02210
        'A7': [(-1, 0, 2, 0, 2, 0)],  # x02020

        # B 大调和弦
        'B': [(-1, 2, 4, 4, 4, 2)],  # x24442
        'Bm': [(-1, 2, 4, 4, 3, 2)],  # x24432
        'B7': [(-1, 2, 1, 2, 0, 2)],  # x21202
    }

    @classmethod
    def get_chord_voicing(cls, chord_name: str, position: int = 0) -> Optional[List[int]]:
        """
        获取和弦的吉他指法

        Args:
            chord_name: 和弦名称 (如 'C', 'Am', 'G7')
            position: 指法位置索引（某些和弦有多个指法）

        Returns:
            6 个 MIDI 音高的列表，-1 表示不弹该弦
        """
        if chord_name not in cls.CHORD_SHAPES:
            return None

        shapes = cls.CHORD_SHAPES[chord_name]
        if position >= len(shapes):
            position = 0

        frets = shapes[position]

        # 将品位转换为 MIDI 音高
        midi_notes = []
        for string_idx, fret in enumerate(frets):
            if fret == -1:
                midi_notes.append(-1)  # 不弹
            else:
                # 开弦音高 + 品位
                midi_notes.append(cls.STANDARD_TUNING[string_idx] + fret)

        return midi_notes

    @classmethod
    def recognize_chord_from_pitches(cls, pitches: List[int]) -> str:
        """
        从音高列表识别和弦类型

        Args:
            pitches: MIDI 音高列表

        Returns:
            和弦名称（如 'C', 'Am'）
        """
        if not pitches:
            return "N"  # No chord

        # 归一化到一个八度内
        pitch_classes = sorted(set(p % 12 for p in pitches))

        # 和弦模式匹配
        chord_patterns = {
            # 大三和弦 (根音, 大三度, 纯五度)
            (0, 4, 7): ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'],
            # 小三和弦 (根音, 小三度, 纯五度)
            (0, 3, 7): ['Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm'],
            # 属七和弦 (根音, 大三度, 纯五度, 小七度)
            (0, 4, 7, 10): ['C7', 'C#7', 'D7', 'D#7', 'E7', 'F7', 'F#7', 'G7', 'G#7', 'A7', 'A#7', 'B7'],
        }

        # 找到根音
        root = pitch_classes[0]

        # 转换为相对音程
        intervals = tuple((p - root) % 12 for p in pitch_classes)

        # 匹配和弦类型
        for pattern, chord_names in chord_patterns.items():
            if all(interval in intervals for interval in pattern):
                return chord_names[root]

        # 如果无法识别，返回根音的大三和弦
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return note_names[root]


class StrummingHumanizer:
    """扫弦人性化处理"""

    @staticmethod
    def apply_strumming_pattern(
        notes: List[Tuple[int, float, float]],  # (pitch, start, duration)
        pattern: str = "down",
        humanize: bool = True
    ) -> List[Tuple[int, float, float]]:
        """
        应用扫弦模式和人性化

        Args:
            notes: 音符列表 [(pitch, start_time, duration), ...]
            pattern: 扫弦模式 ('down', 'up', 'down-up')
            humanize: 是否添加人性化时间偏移

        Returns:
            处理后的音符列表
        """
        if not notes:
            return notes

        # 按音高排序（从低到高）
        sorted_notes = sorted(notes, key=lambda x: x[0])

        result = []

        if pattern == "down":
            # 下扫：从低音到高音，逐渐延迟
            for i, (pitch, start, duration) in enumerate(sorted_notes):
                if humanize:
                    # 添加 5-15ms 的随机延迟
                    delay = i * 0.008 + np.random.uniform(0.002, 0.007)
                else:
                    delay = i * 0.01

                result.append((pitch, start + delay, duration))

        elif pattern == "up":
            # 上扫：从高音到低音，逐渐延迟
            for i, (pitch, start, duration) in enumerate(reversed(sorted_notes)):
                if humanize:
                    delay = i * 0.008 + np.random.uniform(0.002, 0.007)
                else:
                    delay = i * 0.01

                result.append((pitch, start + delay, duration))

        elif pattern == "down-up":
            # 下上扫：先下后上
            half_duration = sorted_notes[0][2] / 2

            # 下扫
            for i, (pitch, start, _) in enumerate(sorted_notes):
                delay = i * 0.008 if humanize else i * 0.01
                result.append((pitch, start + delay, half_duration))

            # 上扫
            for i, (pitch, start, _) in enumerate(reversed(sorted_notes)):
                delay = i * 0.008 if humanize else i * 0.01
                result.append((pitch, start + half_duration + delay, half_duration))

        else:
            # 默认：同时发声
            result = notes

        return result

    @staticmethod
    def add_velocity_variation(
        notes: List[Tuple[int, float, float, int]],  # (pitch, start, duration, velocity)
        variation: float = 0.15
    ) -> List[Tuple[int, float, float, int]]:
        """
        添加力度变化

        Args:
            notes: 音符列表 [(pitch, start, duration, velocity), ...]
            variation: 变化幅度 (0.0-1.0)

        Returns:
            处理后的音符列表
        """
        result = []

        for pitch, start, duration, velocity in notes:
            # 添加随机力度变化
            variation_amount = int(velocity * variation * np.random.uniform(-1, 1))
            new_velocity = max(40, min(127, velocity + variation_amount))
            result.append((pitch, start, duration, new_velocity))

        return result


class SmartGuitarVoicing:
    """智能吉他 Voicing 转换器"""

    def __init__(self):
        self.fretboard = GuitarFretboard()
        self.humanizer = StrummingHumanizer()

    def convert_piano_to_guitar(
        self,
        chord_groups: List[Tuple[float, List]],  # (start_time, notes)
        style: str = "folk"
    ) -> List[Tuple[int, float, float, int]]:
        """
        将钢琴和弦转换为吉他 Voicing

        Args:
            chord_groups: 和弦组列表 [(start_time, [notes]), ...]
            style: 演奏风格 ('folk', 'rock', 'fingerstyle')

        Returns:
            吉他音符列表 [(pitch, start, duration, velocity), ...]
        """
        guitar_notes = []

        for start_time, notes in chord_groups:
            # 提取音高
            pitches = [note.pitch for note in notes]

            # 识别和弦
            chord_name = self.fretboard.recognize_chord_from_pitches(pitches)

            # 获取吉他指法
            voicing = self.fretboard.get_chord_voicing(chord_name)

            if voicing is None:
                # 如果没有预设指法，使用简化算法
                voicing = self._fallback_voicing(pitches)

            # 创建音符
            duration = notes[0].end - notes[0].start
            velocity = notes[0].velocity

            chord_notes = []
            for pitch in voicing:
                if pitch != -1:  # 跳过不弹的弦
                    chord_notes.append((pitch, start_time, duration, velocity))

            # 应用扫弦模式
            if style == "folk":
                pattern = "down"
            elif style == "rock":
                pattern = "down-up"
            else:
                pattern = "down"

            # 转换格式以应用扫弦
            notes_for_strum = [(p, s, d) for p, s, d, v in chord_notes]
            strummed = self.humanizer.apply_strumming_pattern(
                notes_for_strum,
                pattern=pattern,
                humanize=True
            )

            # 添加回力度并应用力度变化
            notes_with_velocity = [(p, s, d, velocity) for p, s, d in strummed]
            final_notes = self.humanizer.add_velocity_variation(notes_with_velocity)

            guitar_notes.extend(final_notes)

        return guitar_notes

    def _fallback_voicing(self, pitches: List[int]) -> List[int]:
        """
        当没有预设指法时的后备方案

        Args:
            pitches: 原始音高列表

        Returns:
            吉他音高列表
        """
        # 限制音符数量到 6 个
        if len(pitches) > 6:
            pitches = self._select_important_notes(pitches, 6)

        # 映射到吉他音域
        guitar_pitches = []
        for pitch in pitches:
            # 调整到吉他音域 (E2-E5, MIDI 40-76)
            while pitch < 40:
                pitch += 12
            while pitch > 76:
                pitch -= 12
            guitar_pitches.append(pitch)

        return guitar_pitches

    def _select_important_notes(self, pitches: List[int], max_notes: int) -> List[int]:
        """选择最重要的音符"""
        if len(pitches) <= max_notes:
            return pitches

        # 保留最低音和最高音，均匀选择中间音
        selected = [pitches[0], pitches[-1]]
        remaining = max_notes - 2

        if remaining > 0:
            middle = pitches[1:-1]
            step = len(middle) / remaining
            for i in range(remaining):
                idx = int(i * step)
                selected.append(middle[idx])

        return sorted(selected)

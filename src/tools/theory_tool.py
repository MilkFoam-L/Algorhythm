"""
Theory Tool - 和弦识别与乐理分析
使用 Librosa 进行和弦识别和音乐理论分析
"""

import os
from typing import Dict, Any, Optional, List, ClassVar
from pathlib import Path

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import numpy as np


class TheoryToolInput(BaseModel):
    """Theory Tool 输入参数"""
    audio_path: str = Field(description="音频文件的绝对路径 (支持 .wav, .mp3, .flac 等格式)")
    analysis_type: str = Field(
        default="chords",
        description="分析类型: 'chords' (和弦识别), 'key' (调性分析), 'tempo' (节奏分析), 'all' (全部)"
    )


class TheoryTool(BaseTool):
    """
    乐理工具 - 和弦识别与音乐分析

    这个工具使用 Librosa 来分析音频文件，识别和弦、调性和节奏等音乐理论元素。

    功能：
    - 和弦识别 (Chord Recognition)
    - 调性分析 (Key Detection)
    - 节奏分析 (Tempo Analysis)
    - 音高类别分析 (Pitch Class Profile)
    """

    name: str = "theory_tool"
    description: str = """
    分析音频文件的音乐理论元素（和弦、调性、节奏）。

    输入：音频文件路径
    输出：和弦序列、调性、节奏等音乐理论信息的 JSON 格式

    使用场景：
    - 识别音频中的和弦进行
    - 分析音乐的调性
    - 检测节奏和速度
    - 为编曲提供乐理依据

    示例：
    输入: "/path/to/audio.wav"
    输出: {"chords": ["C", "Am", "F", "G"], "key": "C major", "tempo": 120}
    """
    args_schema: type[BaseModel] = TheoryToolInput

    # 和弦模板 (12个半音的音高类别分布)
    CHORD_TEMPLATES: ClassVar[Dict[str, List[int]]] = {
        'C': [1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],      # C major (C-E-G)
        'Cm': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],     # C minor (C-Eb-G)
        'C#': [0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],     # C# major
        'C#m': [0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],    # C# minor
        'D': [0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0],      # D major
        'Dm': [0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0],     # D minor
        'D#': [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0],     # D# major
        'D#m': [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0],    # D# minor
        'E': [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],      # E major
        'Em': [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1],     # E minor
        'F': [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],      # F major
        'Fm': [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0],     # F minor
        'F#': [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],     # F# major
        'F#m': [0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0],    # F# minor
        'G': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1],      # G major
        'Gm': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0],     # G minor
        'G#': [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],     # G# major
        'G#m': [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],    # G# minor
        'A': [0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],      # A major
        'Am': [1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],     # A minor
        'A#': [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],     # A# major
        'A#m': [0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],    # A# minor
        'B': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],      # B major
        'Bm': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],     # B minor
    }

    def _run(self, audio_path: str, analysis_type: str = "chords") -> Dict[str, Any]:
        """
        执行音乐理论分析

        Args:
            audio_path: 音频文件路径
            analysis_type: 分析类型

        Returns:
            包含音乐理论分析结果的字典
        """
        try:
            # 延迟导入
            import librosa

            # 验证输入文件
            audio_path = Path(audio_path)
            if not audio_path.exists():
                return {
                    "success": False,
                    "error": f"音频文件不存在: {audio_path}"
                }

            print(f"🎼 正在分析音频: {audio_path.name}")
            print(f"📊 分析类型: {analysis_type}")

            # 加载音频
            y, sr = librosa.load(str(audio_path))
            duration = librosa.get_duration(y=y, sr=sr)

            result = {
                "success": True,
                "audio_path": str(audio_path),
                "duration_seconds": round(duration, 2),
            }

            # 根据分析类型执行不同的分析
            if analysis_type in ["chords", "all"]:
                chord_result = self._analyze_chords(y, sr)
                result.update(chord_result)

            if analysis_type in ["key", "all"]:
                key_result = self._analyze_key(y, sr)
                result.update(key_result)

            if analysis_type in ["tempo", "all"]:
                tempo_result = self._analyze_tempo(y, sr)
                result.update(tempo_result)

            result["message"] = f"✅ 分析完成！时长 {duration:.1f} 秒"
            print(f"✅ 分析完成")

            return result

        except ImportError as e:
            return {
                "success": False,
                "error": f"缺少依赖库: {str(e)}。请运行: pip install librosa"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"分析失败: {str(e)}"
            }

    def _analyze_chords(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        和弦识别

        使用色度图 (Chromagram) 和模板匹配进行和弦识别
        """
        import librosa

        # 计算色度图 (Chromagram)
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=512)

        # 将色度图分段，每段识别一个和弦
        hop_length = 512
        segment_length = sr * 2  # 每2秒一个段
        n_segments = int(len(y) / segment_length) + 1

        chords = []
        chord_times = []

        for i in range(n_segments):
            start_frame = int(i * segment_length / hop_length)
            end_frame = int((i + 1) * segment_length / hop_length)

            if start_frame >= chroma.shape[1]:
                break

            end_frame = min(end_frame, chroma.shape[1])

            # 计算该段的平均色度
            segment_chroma = np.mean(chroma[:, start_frame:end_frame], axis=1)

            # 归一化
            if np.sum(segment_chroma) > 0:
                segment_chroma = segment_chroma / np.sum(segment_chroma)

            # 与和弦模板匹配
            best_chord = self._match_chord_template(segment_chroma)

            # 避免连续重复的和弦
            if not chords or chords[-1] != best_chord:
                chords.append(best_chord)
                chord_times.append(round(i * 2, 1))

        return {
            "chords": chords,
            "chord_times": chord_times,
            "chord_count": len(chords),
            "chord_progression": " -> ".join(chords)
        }

    def _match_chord_template(self, chroma: np.ndarray) -> str:
        """
        将色度向量与和弦模板匹配

        Args:
            chroma: 12维色度向量

        Returns:
            最匹配的和弦名称
        """
        best_chord = "N"  # No chord
        best_score = -1

        for chord_name, template in self.CHORD_TEMPLATES.items():
            # 计算余弦相似度
            template_array = np.array(template)
            if np.sum(template_array) > 0:
                template_array = template_array / np.sum(template_array)

            score = np.dot(chroma, template_array)

            if score > best_score:
                best_score = score
                best_chord = chord_name

        # 如果相似度太低，认为没有明确的和弦
        if best_score < 0.3:
            return "N"

        return best_chord

    def _analyze_key(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        调性分析

        使用 Krumhansl-Schmuckler 算法估计调性
        """
        import librosa

        # 计算整首曲子的色度图
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        chroma_mean = np.mean(chroma, axis=1)

        # Krumhansl-Schmuckler 大调和小调模板
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

        # 归一化
        major_profile = major_profile / np.sum(major_profile)
        minor_profile = minor_profile / np.sum(minor_profile)
        chroma_mean = chroma_mean / np.sum(chroma_mean)

        # 尝试所有12个调
        note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        best_key = "C major"
        best_score = -1

        for i in range(12):
            # 旋转模板以匹配不同的调
            rotated_major = np.roll(major_profile, i)
            rotated_minor = np.roll(minor_profile, i)

            # 计算相关性
            major_score = np.corrcoef(chroma_mean, rotated_major)[0, 1]
            minor_score = np.corrcoef(chroma_mean, rotated_minor)[0, 1]

            if major_score > best_score:
                best_score = major_score
                best_key = f"{note_names[i]} major"

            if minor_score > best_score:
                best_score = minor_score
                best_key = f"{note_names[i]} minor"

        return {
            "key": best_key,
            "key_confidence": round(float(best_score), 3)
        }

    def _analyze_tempo(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        节奏分析

        估计音频的速度 (BPM) 和节拍
        """
        import librosa

        # 估计速度
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

        # 计算节拍时间
        beat_times = librosa.frames_to_time(beats, sr=sr)

        return {
            "tempo": round(float(tempo), 1),
            "beat_count": len(beats),
            "beat_times": [round(float(t), 2) for t in beat_times[:10]],  # 只返回前10个节拍
        }

    async def _arun(self, audio_path: str, analysis_type: str = "chords") -> Dict[str, Any]:
        """异步执行（当前使用同步实现）"""
        return self._run(audio_path, analysis_type)


# 便捷函数：直接调用工具
def analyze_music_theory(audio_path: str, analysis_type: str = "chords") -> Dict[str, Any]:
    """
    便捷函数：分析音乐理论

    Args:
        audio_path: 音频文件路径
        analysis_type: 分析类型

    Returns:
        分析结果字典
    """
    tool = TheoryTool()
    return tool._run(audio_path, analysis_type)

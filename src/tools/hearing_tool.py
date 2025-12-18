"""
Hearing Tool - Audio to MIDI Conversion
使用 Basic Pitch 将音频转换为 MIDI 数据
"""

import os
import tempfile
from typing import Dict, Any, Optional
from pathlib import Path

from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class HearingToolInput(BaseModel):
    """Hearing Tool 输入参数"""
    audio_path: str = Field(description="音频文件的绝对路径 (支持 .wav, .mp3, .flac 等格式)")
    output_dir: Optional[str] = Field(
        default=None,
        description="MIDI 输出目录，默认为临时目录"
    )


class HearingTool(BaseTool):
    """
    听觉工具 - 将音频转换为 MIDI

    这个工具使用 Spotify 的 Basic Pitch 模型来分析音频文件，
    提取音高、节奏和音符信息，并转换为 MIDI 格式。

    功能：
    - 音频文件 -> MIDI 文件
    - 提取音符事件（音高、起始时间、持续时间、力度）
    - 支持多种音频格式
    """

    name: str = "hearing_tool"
    description: str = """
    将音频文件转换为 MIDI 数据。

    输入：音频文件路径（支持 .wav, .mp3, .flac 等格式）
    输出：MIDI 文件路径和音符信息的 JSON 格式

    使用场景：
    - 用户哼唱或演奏的音频需要转换为可编辑的音符
    - 需要分析音频中的旋律和节奏
    - 作为音乐编曲的第一步

    示例：
    输入: "/path/to/audio.wav"
    输出: {"midi_path": "/tmp/output.mid", "note_count": 42, "duration": 8.5}
    """
    args_schema: type[BaseModel] = HearingToolInput

    def _run(self, audio_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        执行音频到 MIDI 的转换

        Args:
            audio_path: 音频文件路径
            output_dir: MIDI 输出目录

        Returns:
            包含 MIDI 路径和音符信息的字典
        """
        try:
            # 延迟导入以避免启动时加载大模型
            from basic_pitch.inference import predict
            from basic_pitch import ICASSP_2022_MODEL_PATH
            import pretty_midi

            # 验证输入文件
            audio_path = Path(audio_path)
            if not audio_path.exists():
                return {
                    "success": False,
                    "error": f"音频文件不存在: {audio_path}"
                }

            # 设置输出目录
            if output_dir is None:
                # 默认输出到项目的 mid 文件夹
                project_root = Path(__file__).parent.parent.parent
                output_dir = project_root / "mid"
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # 生成输出文件名
            output_midi_path = output_dir / f"{audio_path.stem}_converted.mid"

            print(f"🎵 正在分析音频: {audio_path.name}")
            print(f"📊 使用模型: Basic Pitch (Spotify)")

            # 使用 Basic Pitch 进行预测
            model_output, midi_data, note_events = predict(
                audio_path=str(audio_path),
                model_or_model_path=ICASSP_2022_MODEL_PATH,
                onset_threshold=0.5,  # 音符起始检测阈值
                frame_threshold=0.3,  # 帧级别检测阈值
                minimum_note_length=127.70,  # 最小音符长度（毫秒）
                minimum_frequency=None,  # 最小频率（Hz）
                maximum_frequency=None,  # 最大频率（Hz）
                multiple_pitch_bends=False,  # 是否使用多个弯音
                melodia_trick=True,  # 使用 Melodia trick 提高单音旋律检测
                debug_file=None
            )

            # 保存 MIDI 文件
            midi_data.write(str(output_midi_path))

            # 分析 MIDI 数据
            pm = pretty_midi.PrettyMIDI(str(output_midi_path))

            # 统计音符信息
            total_notes = sum(len(instrument.notes) for instrument in pm.instruments)
            duration = pm.get_end_time()

            # 提取音符详情（前10个音符作为示例）
            note_details = []
            for instrument in pm.instruments[:1]:  # 只取第一个乐器
                for note in instrument.notes[:10]:  # 只取前10个音符
                    note_details.append({
                        "pitch": note.pitch,
                        "note_name": pretty_midi.note_number_to_name(note.pitch),
                        "start": round(note.start, 3),
                        "end": round(note.end, 3),
                        "duration": round(note.end - note.start, 3),
                        "velocity": note.velocity
                    })

            result = {
                "success": True,
                "midi_path": str(output_midi_path),
                "audio_path": str(audio_path),
                "note_count": total_notes,
                "duration_seconds": round(duration, 2),
                "instrument_count": len(pm.instruments),
                "tempo": round(pm.estimate_tempo(), 1),
                "sample_notes": note_details,
                "message": f"✅ 成功转换！检测到 {total_notes} 个音符，时长 {duration:.1f} 秒"
            }

            print(f"✅ 转换完成: {total_notes} 个音符")
            print(f"📁 MIDI 文件: {output_midi_path}")

            return result

        except ImportError as e:
            return {
                "success": False,
                "error": f"缺少依赖库: {str(e)}。请运行: pip install basic-pitch pretty_midi"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"转换失败: {str(e)}"
            }

    async def _arun(self, audio_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """异步执行（当前使用同步实现）"""
        return self._run(audio_path, output_dir)


# 便捷函数：直接调用工具
def audio_to_midi(audio_path: str, output_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    便捷函数：将音频转换为 MIDI

    Args:
        audio_path: 音频文件路径
        output_dir: 输出目录

    Returns:
        转换结果字典
    """
    tool = HearingTool()
    return tool._run(audio_path, output_dir)

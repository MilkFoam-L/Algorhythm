"""
Rendering Tool - AI 音频渲染
使用 MusicGen-Melody 将 MIDI 转换为真实音频
"""

import os
from typing import Dict, Any, Optional, List, ClassVar
from pathlib import Path

from langchain.tools import BaseTool
from pydantic import BaseModel, Field
import numpy as np


class RenderingToolInput(BaseModel):
    """Rendering Tool 输入参数"""
    midi_path: str = Field(description="输入 MIDI 文件的绝对路径")
    instrument: str = Field(
        default="acoustic_guitar",
        description="目标乐器音色: 'acoustic_guitar', 'electric_guitar', 'piano', 'strings', 'bass'"
    )
    style: str = Field(
        default="clean",
        description="演奏风格: 'clean', 'distorted', 'ambient', 'bright'"
    )
    duration: int = Field(
        default=10,
        description="生成音频的时长（秒），默认 10 秒"
    )
    output_path: Optional[str] = Field(
        default=None,
        description="输出音频文件路径（可选，默认在同目录生成）"
    )


class RenderingTool(BaseTool):
    """
    音频渲染工具 - AI 音频生成

    这个工具使用 MusicGen-Melody 将 MIDI 转换为真实的音频。

    功能：
    - MIDI → 引导音频转换
    - AI 音频生成（MusicGen-Melody）
    - 多种乐器音色支持
    - 风格化音频渲染
    """

    name: str = "rendering_tool"
    description: str = """
    将 MIDI 文件渲染为真实的音频文件。

    输入：MIDI 文件路径和目标乐器音色
    输出：高质量的音频文件（WAV 格式）

    使用场景：
    - 将吉他 MIDI 渲染为真实吉他音色
    - 将钢琴 MIDI 渲染为钢琴音色
    - 生成不同风格的音频（清晰、失真、氛围等）
    - 完成音乐制作的最后一步

    示例：
    输入: guitar.mid, instrument="acoustic_guitar"
    输出: guitar_rendered.wav (真实吉他音色)
    """
    args_schema: type[BaseModel] = RenderingToolInput

    # 乐器音色提示词模板
    INSTRUMENT_PROMPTS: ClassVar[Dict[str, str]] = {
        "acoustic_guitar": "High quality acoustic guitar, clean tone, warm sound, fingerstyle",
        "electric_guitar": "Electric guitar, clean tone, bright sound, professional recording",
        "piano": "Grand piano, clear tone, concert hall acoustics, expressive",
        "strings": "String ensemble, orchestral, warm and rich, cinematic",
        "bass": "Electric bass, deep tone, groovy, tight sound",
    }

    # 风格修饰词
    STYLE_MODIFIERS: ClassVar[Dict[str, str]] = {
        "clean": "clean, clear, professional",
        "distorted": "distorted, rock, powerful",
        "ambient": "ambient, reverb, atmospheric",
        "bright": "bright, crisp, energetic",
    }

    def _run(
        self,
        midi_path: str,
        instrument: str = "acoustic_guitar",
        style: str = "clean",
        duration: int = 10,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        执行音频渲染

        Args:
            midi_path: 输入 MIDI 文件路径
            instrument: 目标乐器音色
            style: 演奏风格
            duration: 音频时长（秒）
            output_path: 输出文件路径（可选）

        Returns:
            包含渲染结果的字典
        """
        try:
            # 验证输入文件
            midi_path = Path(midi_path)
            if not midi_path.exists():
                return {
                    "success": False,
                    "error": f"MIDI 文件不存在: {midi_path}"
                }

            print(f"🎵 正在加载 MIDI: {midi_path.name}")

            # 步骤 1: MIDI 转换为引导音频
            guide_audio, sample_rate = self._midi_to_guide_audio(str(midi_path))

            print(f"✅ 引导音频已生成")
            print(f"   采样率: {sample_rate} Hz")
            print(f"   时长: {len(guide_audio) / sample_rate:.2f} 秒")

            # 步骤 2: 构建提示词
            prompt = self._build_prompt(instrument, style)
            print(f"🎨 音色提示: {prompt}")

            # 步骤 3: 使用 MusicGen 生成音频
            print(f"🤖 正在使用 AI 生成音频...")
            print(f"   ⚠️  注意: 首次运行会下载模型（约 1.5GB），请耐心等待")

            rendered_audio = self._generate_with_musicgen(
                guide_audio,
                sample_rate,
                prompt,
                duration
            )

            # 步骤 4: 保存音频
            if output_path is None:
                output_path = midi_path.parent / f"{midi_path.stem}_{instrument}.wav"
            else:
                output_path = Path(output_path)

            self._save_audio(rendered_audio, sample_rate, str(output_path))

            print(f"✅ 渲染完成！")
            print(f"📁 输出文件: {output_path}")

            return {
                "success": True,
                "input_path": str(midi_path),
                "output_path": str(output_path),
                "instrument": instrument,
                "style": style,
                "duration_seconds": len(rendered_audio) / sample_rate,
                "sample_rate": sample_rate,
                "message": f"✅ 成功渲染为 {instrument} 音色！"
            }

        except ImportError as e:
            return {
                "success": False,
                "error": f"缺少依赖库: {str(e)}。请运行: pip install audiocraft scipy"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"渲染失败: {str(e)}"
            }

    def _midi_to_guide_audio(self, midi_path: str) -> tuple:
        """
        将 MIDI 转换为引导音频

        使用简单的正弦波合成，作为 MusicGen 的旋律引导

        Args:
            midi_path: MIDI 文件路径

        Returns:
            (audio_array, sample_rate) 元组
        """
        import pretty_midi
        import numpy as np

        # 加载 MIDI
        midi_data = pretty_midi.PrettyMIDI(midi_path)

        # 设置采样率
        sample_rate = 32000  # MusicGen 推荐的采样率

        # 获取总时长
        duration = midi_data.get_end_time()

        # 创建音频数组
        audio = np.zeros(int(duration * sample_rate))

        # 合成每个音符
        for instrument in midi_data.instruments:
            if instrument.is_drum:
                continue

            for note in instrument.notes:
                # 计算音符的频率
                frequency = 440.0 * (2.0 ** ((note.pitch - 69) / 12.0))

                # 生成正弦波
                start_sample = int(note.start * sample_rate)
                end_sample = int(note.end * sample_rate)
                duration_samples = end_sample - start_sample

                if duration_samples > 0:
                    t = np.linspace(0, duration_samples / sample_rate, duration_samples)

                    # 添加包络（ADSR 简化版）
                    attack = int(0.01 * sample_rate)  # 10ms attack
                    release = int(0.05 * sample_rate)  # 50ms release

                    envelope = np.ones(duration_samples)
                    if duration_samples > attack:
                        envelope[:attack] = np.linspace(0, 1, attack)
                    if duration_samples > release:
                        envelope[-release:] = np.linspace(1, 0, release)

                    # 生成音符
                    note_audio = 0.3 * np.sin(2 * np.pi * frequency * t) * envelope

                    # 力度调制
                    velocity_factor = note.velocity / 127.0
                    note_audio *= velocity_factor

                    # 添加到总音频
                    audio[start_sample:end_sample] += note_audio

        # 归一化
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio)) * 0.8

        return audio.astype(np.float32), sample_rate

    def _build_prompt(self, instrument: str, style: str) -> str:
        """
        构建音色提示词

        Args:
            instrument: 乐器类型
            style: 风格

        Returns:
            完整的提示词
        """
        # 获取基础乐器提示
        base_prompt = self.INSTRUMENT_PROMPTS.get(
            instrument,
            "High quality musical instrument"
        )

        # 获取风格修饰
        style_modifier = self.STYLE_MODIFIERS.get(style, "")

        # 组合提示词
        if style_modifier:
            prompt = f"{base_prompt}, {style_modifier}"
        else:
            prompt = base_prompt

        return prompt

    def _generate_with_musicgen(
        self,
        guide_audio: np.ndarray,
        sample_rate: int,
        prompt: str,
        duration: int
    ) -> np.ndarray:
        """
        使用 MusicGen-Melody 生成音频

        Args:
            guide_audio: 引导音频
            sample_rate: 采样率
            prompt: 音色提示词
            duration: 目标时长（秒）

        Returns:
            生成的音频数组
        """
        try:
            from audiocraft.models import MusicGen
            import torch

            # 加载模型
            print("   加载 MusicGen-Melody 模型...")
            model = MusicGen.get_pretrained('facebook/musicgen-melody')

            # 设置生成参数
            model.set_generation_params(
                duration=duration,
                temperature=1.0,
                top_k=250,
                top_p=0.0,
                cfg_coef=3.0
            )

            # 准备引导音频
            # MusicGen 需要 (1, 1, samples) 的张量
            guide_tensor = torch.from_numpy(guide_audio).unsqueeze(0).unsqueeze(0)

            # 生成音频
            print("   生成中...")
            with torch.no_grad():
                wav = model.generate_with_chroma(
                    descriptions=[prompt],
                    melody_wavs=guide_tensor,
                    melody_sample_rate=sample_rate,
                    progress=True
                )

            # 转换为 numpy 数组
            generated_audio = wav[0, 0].cpu().numpy()

            return generated_audio

        except ImportError:
            # 如果 MusicGen 不可用，返回引导音频作为后备
            print("   ⚠️  MusicGen 不可用，使用引导音频作为输出")
            return guide_audio

    def _save_audio(self, audio: np.ndarray, sample_rate: int, output_path: str):
        """
        保存音频文件

        Args:
            audio: 音频数组
            sample_rate: 采样率
            output_path: 输出路径
        """
        from scipy.io import wavfile

        # 转换为 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)

        # 保存为 WAV
        wavfile.write(output_path, sample_rate, audio_int16)

    async def _arun(
        self,
        midi_path: str,
        instrument: str = "acoustic_guitar",
        style: str = "clean",
        duration: int = 10,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """异步执行（当前使用同步实现）"""
        return self._run(midi_path, instrument, style, duration, output_path)


# 便捷函数：直接调用工具
def render_audio(
    midi_path: str,
    instrument: str = "acoustic_guitar",
    style: str = "clean",
    duration: int = 10,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    便捷函数：音频渲染

    Args:
        midi_path: 输入 MIDI 文件路径
        instrument: 目标乐器音色
        style: 演奏风格
        duration: 音频时长（秒）
        output_path: 输出文件路径（可选）

    Returns:
        渲染结果字典
    """
    tool = RenderingTool()
    return tool._run(midi_path, instrument, style, duration, output_path)

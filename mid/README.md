# MIDI 输出文件夹

这个文件夹用于存放 HearingTool 生成的 MIDI 文件。

## 说明

- 所有通过 `HearingTool` 转换的音频文件都会在这里生成对应的 MIDI 文件
- 文件命名格式: `{原音频文件名}_converted.mid`
- 这些文件会被 `.gitignore` 忽略，不会提交到版本控制

## 使用示例

```python
from src.tools import HearingTool

tool = HearingTool()
result = tool._run(audio_path="audio.wav")

# MIDI 文件会自动保存到: mid/audio_converted.mid
print(result["midi_path"])
```

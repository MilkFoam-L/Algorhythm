# Algorhythm - AI 音乐制作智能体

<thinking_mode>interleaved</thinking_mode>

基于 LangChain 和 DeepSeek 构建的纯 AI 驱动音乐制作系统。

## 🎯 项目概述

Algorhythm 是一个 Agentic AI 系统，使用大语言模型作为"大脑"，调度专门的 AI 模型作为"手脚"，实现从音频输入到智能编曲再到音频渲染的完整音乐制作流程。

### 核心架构

```
用户输入 (音频/自然语言)
    ↓
AI Agent (DeepSeek LLM)
    ↓
工具调度 (LangChain Tools)
    ↓
├─ 听觉工具 (Basic Pitch) - 音频 → MIDI ✅
├─ 乐理工具 (Librosa) - 和弦/调性/节奏分析 ✅
├─ 编曲工具 (Pretty MIDI) - 智能 Voicing 转换 ✅
└─ 渲染工具 (MusicGen) - MIDI → 音频 ✅
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
cd Algorhythm

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API

创建 `.env` 文件并配置 DeepSeek API:

```env
DEEPSEEK_API_KEY=your_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com
```

### 3. 运行测试

```bash
# 运行测试
python test/test_simple_agent.py      # Agent 测试
python test/test_hearing_tool.py      # 听觉工具测试
python test/test_theory_tool.py       # 乐理工具测试
python test/test_arrangement_tool.py  # 编曲工具测试
python test/test_rendering_tool.py    # 音频渲染工具测试

# 运行基础示例
python examples/basic_usage.py
python examples/smart_guitar_demo.py  # 智能吉他编曲演示
```

## 📦 项目结构

```
Algorhythm/
├── src/
│   ├── llm/                    # LLM 模块
│   │   ├── deepseek_client.py      # DeepSeek API 客户端
│   │   └── deepseek_langchain.py   # LangChain 集成
│   ├── tools/                  # 工具模块
│   │   ├── hearing_tool.py         # 听觉工具 (Basic Pitch)
│   │   ├── theory_tool.py          # 乐理工具 (Librosa)
│   │   ├── arrangement_tool.py     # 编曲工具 (Pretty MIDI)
│   │   ├── smart_guitar_voicing.py # 智能吉他指法系统
│   │   └── rendering_tool.py       # 音频渲染工具 (MusicGen)
│   └── agent/                  # Agent 模块
│       └── music_agent.py          # 音乐 AI Agent
├── test/                       # 测试脚本
│   ├── test_simple_agent.py        # Agent 测试
│   ├── test_hearing_tool.py        # 听觉工具测试
│   ├── test_theory_tool.py         # 乐理工具测试
│   ├── test_arrangement_tool.py    # 编曲工具测试
│   └── test_rendering_tool.py      # 音频渲染工具测试
├── mid/                        # MIDI 输出文件夹
│   └── README.md
├── examples/                   # 示例代码
│   ├── basic_usage.py
│   └── smart_guitar_demo.py        # 智能吉他编曲演示
├── requirements.txt           # 依赖列表
└── README.md                  # 项目文档
```

## 🎵 Phase 1: 听觉工具 (已实现)

### 功能特性

- ✅ 音频转 MIDI (使用 Spotify Basic Pitch)
- ✅ 支持多种音频格式 (.wav, .mp3, .flac)
- ✅ 提取音符信息 (音高、时长、力度)
- ✅ 估计速度 (BPM)
- ✅ LangChain 工具集成
- ✅ DeepSeek 兼容

### 使用示例

#### 方式 1: 直接使用工具

```python
from src.tools import HearingTool

# 创建工具
tool = HearingTool()

# 转换音频
result = tool._run(audio_path="path/to/audio.wav")

if result["success"]:
    print(f"MIDI 文件: {result['midi_path']}")
    print(f"音符数量: {result['note_count']}")
    print(f"时长: {result['duration_seconds']} 秒")
```

#### 方式 2: 使用 AI Agent

```python
from src.agent import MusicAgent

# 创建 Agent
agent = MusicAgent(verbose=True)

# 自然语言交互
result = agent.process(
    "请将 audio.wav 转换为 MIDI 并分析音符"
)

print(result["output"])
```

### 工具参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `audio_path` | str | 音频文件的绝对路径 |
| `output_dir` | str (可选) | MIDI 输出目录，默认为临时目录 |

### 返回结果

```python
{
    "success": True,
    "midi_path": "/path/to/output.mid",
    "audio_path": "/path/to/input.wav",
    "note_count": 42,
    "duration_seconds": 8.5,
    "instrument_count": 1,
    "tempo": 120.0,
    "sample_notes": [
        {
            "pitch": 60,
            "note_name": "C4",
            "start": 0.0,
            "end": 0.5,
            "duration": 0.5,
            "velocity": 80
        },
        # ...
    ],
    "message": "✅ 成功转换！检测到 42 个音符，时长 8.5 秒"
}
```

## 🔧 技术栈

### 核心框架
- **LangChain**: Agent 框架和工具编排
- **DeepSeek**: 大语言模型 (deepseek-reasoner / deepseek-chat)
- **OpenAI SDK**: API 客户端

### 音乐处理
- **Basic Pitch**: Spotify 开源的音频转 MIDI 模型
- **Pretty MIDI**: MIDI 文件处理
- **Librosa**: 音频分析 (未来使用)

## 🎯 实现原理

### 1. 工具设计模式

每个工具都是一个 LangChain `BaseTool`:

```python
class HearingTool(BaseTool):
    name = "hearing_tool"
    description = "将音频文件转换为 MIDI 数据"
    args_schema = HearingToolInput  # Pydantic 模型

    def _run(self, audio_path: str, **kwargs) -> Dict:
        # 工具实现逻辑
        pass
```

### 2. Agent 工作流程

```
用户输入
    ↓
Agent 理解意图 (DeepSeek LLM)
    ↓
选择合适的工具 (ReAct 推理)
    ↓
执行工具 (Tool Execution)
    ↓
解释结果 (Natural Language)
    ↓
返回给用户
```

### 3. DeepSeek 集成

使用 OpenAI 兼容的 API 接口:

```python
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)
```

支持的模型:
- `deepseek-reasoner`: 推理模型 (默认)
- `deepseek-chat`: 对话模型 (支持工具调用)

## 🎼 Phase 2: 乐理工具 (已实现)

### 功能特性

- ✅ 和弦识别 (使用 Librosa Chromagram)
- ✅ 调性分析 (Krumhansl-Schmuckler 算法)
- ✅ 节奏分析 (BPM 估计和节拍检测)
- ✅ 支持 24 种和弦（大调/小调）
- ✅ LangChain 工具集成
- ✅ DeepSeek 兼容

### 使用示例

```python
from src.tools import TheoryTool

# 创建工具
tool = TheoryTool()

# 分析音频
result = tool._run(
    audio_path="path/to/audio.wav",
    analysis_type="all"  # 'chords', 'key', 'tempo', 'all'
)

if result["success"]:
    print(f"调性: {result['key']}")
    print(f"速度: {result['tempo']} BPM")
    print(f"和弦进行: {result['chord_progression']}")
```

## 🎸 Phase 3: 编曲工具 (已实现)

### 功能特性

- ✅ 智能 Voicing 转换 (钢琴 → 吉他)
- ✅ 贝斯线生成 (从和弦提取根音)
- ✅ 弦乐编排 (保持和声结构)
- ✅ 音域优化 (适配目标乐器)
- ✅ LangChain 工具集成
- ✅ DeepSeek 兼容

### 使用示例

```python
from src.tools import ArrangementTool

# 创建工具
tool = ArrangementTool()

# 转换为吉他编曲
result = tool._run(
    midi_path="path/to/piano.mid",
    target_instrument="guitar"  # 'guitar', 'bass', 'strings'
)

if result["success"]:
    print(f"输出文件: {result['output_path']}")
    print(f"音符数量: {result['note_count']}")
```

## 🎨 Phase 4: 音频渲染工具 (已实现)

### 功能特性

- ✅ MIDI 转引导音频（正弦波合成）
- ✅ AI 音频生成（MusicGen-Melody 集成）
- ✅ 多种乐器音色（吉他、钢琴、弦乐、贝斯）
- ✅ 风格化渲染（清晰、失真、氛围、明亮）
- ✅ 智能提示词构建
- ✅ LangChain 工具集成
- ✅ DeepSeek 兼容

### 使用示例

```python
from src.tools import RenderingTool

# 创建工具
tool = RenderingTool()

# 渲染为吉他音色
result = tool._run(
    midi_path="guitar.mid",
    instrument="acoustic_guitar",  # 'acoustic_guitar', 'piano', 'strings', 'bass'
    style="clean",                 # 'clean', 'distorted', 'ambient', 'bright'
    duration=10
)

if result["success"]:
    print(f"输出文件: {result['output_path']}")
    print(f"采样率: {result['sample_rate']} Hz")
```

### 技术实现

**1. MIDI 转引导音频**
- 正弦波合成引擎
- ADSR 包络模拟
- 力度响应
- 32kHz 采样率

**2. AI 音频生成**
- MusicGen-Melody 模型
- 旋律条件生成
- 智能提示词系统
- 后备方案（无 AI 时使用引导音频）

**3. 音色库**
- Acoustic Guitar: 民谣吉他，温暖音色
- Electric Guitar: 电吉他，明亮音色
- Piano: 三角钢琴，音乐厅音效
- Strings: 弦乐合奏，电影感
- Bass: 电贝斯，深沉律动

## 🔮 未来规划

### Phase 5: 高级功能 (计划中)
- VST 插件集成 (DawDreamer)
- 实时音频处理
- 混音和母带处理

## 🧪 测试

运行测试套件:

```bash
python test_agent.py
```

测试内容:
1. ✅ 模块导入测试
2. ✅ Hearing Tool 实例化
3. ✅ Music Agent 创建
4. ✅ DeepSeek API 连接
5. ✅ 工具 Schema 验证
6. ✅ LangChain 集成验证

## 📝 开发笔记

### Basic Pitch 集成方式

按照需求，我们采用了**本地集成**方式:

1. **通过 pip 安装**: `pip install basic-pitch`
2. **模型自动下载**: 首次使用时自动下载预训练模型
3. **导入使用**: 在工具中直接 `from basic_pitch.inference import predict`

这种方式的优点:
- ✅ 简单易用，无需手动下载模型
- ✅ 模型缓存在本地，后续使用更快
- ✅ 与 LangChain 无缝集成

### DeepSeek 工具调用兼容性

DeepSeek API 使用 OpenAI 兼容接口，但需要注意:

1. **模型选择**:
   - `deepseek-reasoner`: 适合复杂推理，但不支持工具调用
   - `deepseek-chat`: 支持工具调用，适合 Agent

2. **工具调用格式**: 使用标准的 OpenAI Function Calling 格式

3. **LangChain 集成**: 通过自定义 `LLM` 类实现兼容

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

## 🙏 致谢

- [Spotify Basic Pitch](https://github.com/spotify/basic-pitch) - 音频转 MIDI 模型
- [LangChain](https://github.com/langchain-ai/langchain) - Agent 框架
- [DeepSeek](https://www.deepseek.com/) - 大语言模型

---

**Algorhythm** - 让 AI 成为你的音乐制作伙伴 🎵

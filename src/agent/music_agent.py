"""
Music Agent - Algorhythm 核心智能体
使用 LangChain 框架构建的音乐制作 AI Agent
"""

from typing import List, Dict, Any, Optional
from langchain.tools import BaseTool
from langchain_core.messages import HumanMessage, SystemMessage

from ..llm.deepseek_langchain import DeepSeekChatModel


class MusicAgent:
    """
    简化的音乐制作 AI 智能体

    使用直接的 LLM 调用 + 工具执行模式
    不依赖复杂的 Agent 框架
    """

    def __init__(
        self,
        llm: Optional[DeepSeekChatModel] = None,
        tools: Optional[List[BaseTool]] = None,
        verbose: bool = True
    ):
        """
        初始化音乐 Agent

        Args:
            llm: 语言模型（默认使用 DeepSeek）
            tools: 工具列表
            verbose: 是否显示详细日志
        """
        self.llm = llm or DeepSeekChatModel()
        self.tools = tools or []
        self.verbose = verbose

        # 创建工具映射
        self.tool_map = {tool.name: tool for tool in self.tools}

    def add_tool(self, tool: BaseTool) -> None:
        """添加工具"""
        self.tools.append(tool)
        self.tool_map[tool.name] = tool

    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return [tool.name for tool in self.tools]

    def _format_tools_description(self) -> str:
        """格式化工具描述"""
        if not self.tools:
            return "当前没有可用的工具。"

        descriptions = []
        for tool in self.tools:
            # 获取工具的参数 schema
            params_info = ""
            if hasattr(tool, 'args_schema') and tool.args_schema:
                schema = tool.args_schema
                if hasattr(schema, 'model_fields'):
                    fields = schema.model_fields
                    param_list = []
                    for field_name, field_info in fields.items():
                        field_desc = field_info.description if hasattr(field_info, 'description') else ""
                        param_list.append(f'"{field_name}": {field_desc}')
                    if param_list:
                        params_info = f"\n  参数: {{{', '.join(param_list)}}}"

            descriptions.append(f"- {tool.name}: {tool.description}{params_info}")

        return "\n".join(descriptions)

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入

        Args:
            user_input: 用户的自然语言输入

        Returns:
            处理结果字典
        """
        try:
            if self.verbose:
                print(f"\n🎵 用户输入: {user_input}")
                print(f"🔧 可用工具: {', '.join(self.get_available_tools())}")

            # 构建系统提示词
            system_prompt = f"""你是 Algorhythm，一个专业的 AI 音乐制作助手。

你可以使用以下工具来帮助用户：

{self._format_tools_description()}

当用户请求处理音频或创建音乐时，请：
1. 理解用户的需求
2. 选择合适的工具
3. 使用工具完成任务
4. 向用户解释结果

如果用户的请求需要使用工具，请按以下格式回复：
TOOL: 工具名称
INPUT: 工具输入参数（JSON 格式）

如果不需要使用工具，直接回复用户即可。"""

            # 调用 LLM
            response = self.llm.client.chat_once(
                message=user_input,
                system_prompt=system_prompt
            )

            if self.verbose:
                print(f"\n🤖 AI 响应: {response[:200]}...")

            # 检查是否需要调用工具
            if "TOOL:" in response and "INPUT:" in response:
                # 解析工具调用
                tool_result = self._execute_tool_from_response(response)

                if tool_result:
                    # 将工具结果反馈给 LLM
                    follow_up = self.llm.client.chat_once(
                        message=f"工具执行结果：{tool_result}\n\n请向用户解释这个结果。",
                        system_prompt=system_prompt
                    )

                    return {
                        "success": True,
                        "output": follow_up,
                        "tool_used": True,
                        "tool_result": tool_result
                    }

            return {
                "success": True,
                "output": response,
                "tool_used": False
            }

        except Exception as e:
            if self.verbose:
                print(f"\n❌ 错误: {e}")

            return {
                "success": False,
                "error": str(e)
            }

    def _execute_tool_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """从 LLM 响应中解析并执行工具"""
        try:
            # 简单的解析逻辑
            lines = response.split('\n')
            tool_name = None
            tool_input = None

            for line in lines:
                if line.startswith("TOOL:"):
                    tool_name = line.replace("TOOL:", "").strip()
                elif line.startswith("INPUT:"):
                    tool_input = line.replace("INPUT:", "").strip()

            if tool_name and tool_name in self.tool_map:
                tool = self.tool_map[tool_name]

                if self.verbose:
                    print(f"\n🔧 执行工具: {tool_name}")
                    print(f"📥 输入: {tool_input}")

                # 执行工具
                import json
                try:
                    input_dict = json.loads(tool_input)
                    result = tool._run(**input_dict)
                except json.JSONDecodeError:
                    # 如果不是 JSON，尝试直接传递
                    result = tool._run(tool_input)

                if self.verbose:
                    print(f"📤 输出: {result}")

                return result

        except Exception as e:
            if self.verbose:
                print(f"❌ 工具执行失败: {e}")
            return None

    def process_audio_file(self, audio_path: str, task: str = "convert to MIDI") -> Dict[str, Any]:
        """
        处理音频文件的便捷方法

        Args:
            audio_path: 音频文件路径
            task: 任务描述

        Returns:
            处理结果
        """
        user_input = f"请{task}，音频文件路径是: {audio_path}"
        return self.process(user_input)


# 便捷函数
def create_music_agent(verbose: bool = True) -> MusicAgent:
    """
    快速创建音乐 Agent

    Args:
        verbose: 是否显示详细日志

    Returns:
        MusicAgent 实例
    """
    return MusicAgent(verbose=verbose)

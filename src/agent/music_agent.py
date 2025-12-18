"""
Music Agent - Algorhythm 核心智能体
使用 LangChain 框架构建的音乐制作 AI Agent
"""

from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool

from ..llm.deepseek_langchain import DeepSeekChatModel
from ..tools.hearing_tool import HearingTool


class MusicAgent:
    """
    音乐制作 AI 智能体

    这个 Agent 负责协调各种音乐处理工具，实现从音频输入到音乐输出的完整流程。

    当前支持的工具：
    - Hearing Tool: 音频转 MIDI

    未来扩展：
    - Theory Tool: 和弦分析
    - Arrangement Tool: 智能编曲
    - Rendering Tool: 音频渲染
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
            tools: 工具列表（默认使用所有可用工具）
            verbose: 是否显示详细日志
        """
        # 初始化 LLM
        self.llm = llm or DeepSeekChatModel()

        # 初始化工具
        if tools is None:
            self.tools = self._initialize_default_tools()
        else:
            self.tools = tools

        self.verbose = verbose

        # 创建 Agent
        self.agent_executor = self._create_agent()

    def _initialize_default_tools(self) -> List[BaseTool]:
        """初始化默认工具集"""
        return [
            HearingTool(),
            # 未来添加更多工具:
            # TheoryTool(),
            # ArrangementTool(),
            # RenderingTool(),
        ]

    def _create_agent(self) -> AgentExecutor:
        """
        创建 LangChain Agent

        使用 ReAct (Reasoning + Acting) 模式
        """
        # 定义 Agent 提示词模板
        template = """You are Algorhythm, an AI music production assistant.

You have access to the following tools:

{tools}

Tool Names: {tool_names}

When a user asks you to process audio or create music, follow these steps:
1. Understand what the user wants to do
2. Choose the appropriate tool(s)
3. Execute the tool with correct parameters
4. Explain the results to the user

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)

        # 创建 ReAct Agent
        agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )

        # 创建 Agent Executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
            max_iterations=5,
            early_stopping_method="generate"
        )

        return agent_executor

    def process(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入

        Args:
            user_input: 用户的自然语言输入

        Returns:
            处理结果字典
        """
        try:
            result = self.agent_executor.invoke({"input": user_input})
            return {
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def process_audio_file(self, audio_path: str, task: str = "convert to MIDI") -> Dict[str, Any]:
        """
        处理音频文件的便捷方法

        Args:
            audio_path: 音频文件路径
            task: 任务描述

        Returns:
            处理结果
        """
        user_input = f"Please {task} for the audio file: {audio_path}"
        return self.process(user_input)

    def get_available_tools(self) -> List[str]:
        """获取可用工具列表"""
        return [tool.name for tool in self.tools]

    def add_tool(self, tool: BaseTool) -> None:
        """
        添加新工具

        Args:
            tool: LangChain BaseTool 实例
        """
        self.tools.append(tool)
        # 重新创建 Agent
        self.agent_executor = self._create_agent()

    def remove_tool(self, tool_name: str) -> bool:
        """
        移除工具

        Args:
            tool_name: 工具名称

        Returns:
            是否成功移除
        """
        original_length = len(self.tools)
        self.tools = [t for t in self.tools if t.name != tool_name]

        if len(self.tools) < original_length:
            # 重新创建 Agent
            self.agent_executor = self._create_agent()
            return True
        return False


# 便捷函数：快速创建 Agent
def create_music_agent(verbose: bool = True) -> MusicAgent:
    """
    快速创建音乐 Agent

    Args:
        verbose: 是否显示详细日志

    Returns:
        MusicAgent 实例
    """
    return MusicAgent(verbose=verbose)

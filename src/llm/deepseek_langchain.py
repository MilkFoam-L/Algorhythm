"""
DeepSeek LangChain Integration
将 DeepSeek 集成到 LangChain 框架中
"""

from typing import Any, List, Optional, Dict
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from pydantic import Field

from .deepseek_client import DeepSeekClient


class DeepSeekLLM(LLM):
    """
    DeepSeek LLM for LangChain

    将 DeepSeek API 封装为 LangChain 兼容的 LLM
    支持工具调用和 Agent 框架
    """

    client: DeepSeekClient = Field(default=None)
    model: str = Field(default="deepseek-reasoner")
    temperature: float = Field(default=0.7)
    max_tokens: Optional[int] = Field(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.client is None:
            self.client = DeepSeekClient()

    @property
    def _llm_type(self) -> str:
        """返回 LLM 类型"""
        return "deepseek"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """
        调用 DeepSeek API

        Args:
            prompt: 输入提示词
            stop: 停止词列表
            run_manager: 回调管理器
            **kwargs: 其他参数

        Returns:
            模型响应
        """
        # 使用 DeepSeekClient 进行单次对话
        response = self.client.chat_once(
            message=prompt,
            system_prompt=kwargs.get('system_prompt', self.client.system_prompt)
        )

        return response

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回识别参数"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


class DeepSeekChatModel(LLM):
    """
    DeepSeek Chat Model for LangChain Agents

    专门用于 Agent 的聊天模型，支持工具调用
    """

    client: DeepSeekClient = Field(default=None)
    model: str = Field(default="deepseek-chat")  # 使用 chat 模型以支持工具调用
    temperature: float = Field(default=0.7)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.client is None:
            self.client = DeepSeekClient()
            # 设置专门的系统提示词用于工具调用
            self.client.set_system_prompt(
                "You are a helpful AI assistant specialized in music production. "
                "You have access to various tools for audio processing and music creation. "
                "When users ask you to process audio or create music, use the appropriate tools. "
                "Always explain what you're doing and provide clear results."
            )

    @property
    def _llm_type(self) -> str:
        return "deepseek-chat"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """调用 DeepSeek Chat API"""
        response = self.client.chat(
            message=prompt,
            model=self.model,
            keep_history=kwargs.get('keep_history', False)
        )
        return response

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model": self.model,
            "temperature": self.temperature,
        }

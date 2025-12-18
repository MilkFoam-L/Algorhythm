"""
DeepSeek LLM Client - Algorhythm 核心 LLM 模块
基于 DeepSeek V3.2 (deepseek-reasoner) 构建
"""

import os
from typing import List, Dict, Optional, Generator
from openai import OpenAI
from dotenv import load_dotenv


class DeepSeekClient:
    """DeepSeek API 客户端封装"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化 DeepSeek 客户端
        
        Args:
            api_key: API 密钥，默认从环境变量读取
            base_url: API 基础 URL，默认从环境变量读取
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = base_url or os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置，请在 .env 文件中设置")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        self.default_model = "deepseek-reasoner"
        self.conversation_history: List[Dict[str, str]] = []
        self.system_prompt = "You are a helpful assistant."
    
    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词"""
        self.system_prompt = prompt
    
    def clear_history(self) -> None:
        """清空对话历史"""
        self.conversation_history = []
    
    def chat(
        self, 
        message: str, 
        model: Optional[str] = None,
        keep_history: bool = True,
        stream: bool = False
    ) -> str:
        """
        发送聊天消息并获取响应
        
        Args:
            message: 用户消息
            model: 使用的模型，默认 deepseek-reasoner
            keep_history: 是否保留对话历史
            stream: 是否使用流式输出
            
        Returns:
            AI 响应文本
        """
        model = model or self.default_model
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        if keep_history:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": message})
        
        if stream:
            return self._chat_stream(messages, model, keep_history, message)
        
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False
        )
        
        assistant_message = response.choices[0].message.content
        
        if keep_history:
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def _chat_stream(
        self, 
        messages: List[Dict], 
        model: str,
        keep_history: bool,
        user_message: str
    ) -> Generator[str, None, None]:
        """流式聊天"""
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield content
        
        if keep_history:
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": full_response})
    
    def chat_once(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        单次对话（不保留历史）
        
        Args:
            message: 用户消息
            system_prompt: 临时系统提示词
            
        Returns:
            AI 响应文本
        """
        messages = [
            {"role": "system", "content": system_prompt or self.system_prompt},
            {"role": "user", "content": message}
        ]
        
        response = self.client.chat.completions.create(
            model=self.default_model,
            messages=messages,
            stream=False
        )
        
        return response.choices[0].message.content

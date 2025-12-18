#!/usr/bin/env python3
"""
Algorhythm - DeepSeek LLM 控制台对话测试脚本
用于验证 LLM 集成是否正常工作
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.llm import DeepSeekClient


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     🎵  Algorhythm - AI Music Production Agent  🎵           ║
║                                                              ║
║     DeepSeek V3.2 (deepseek-reasoner) 对话测试               ║
║                                                              ║
║     命令:                                                    ║
║       /quit, /exit, /q  - 退出                               ║
║       /clear, /c        - 清空对话历史                       ║
║       /system <prompt>  - 设置系统提示词                     ║
║       /help, /h         - 显示帮助                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
可用命令:
  /quit, /exit, /q  - 退出程序
  /clear, /c        - 清空对话历史
  /system <prompt>  - 设置新的系统提示词
  /history          - 显示对话历史
  /help, /h         - 显示此帮助信息
  
直接输入文字即可与 AI 对话。
    """
    print(help_text)


def main():
    """主函数"""
    print_banner()
    
    try:
        client = DeepSeekClient()
        print("✅ DeepSeek 客户端初始化成功！\n")
    except ValueError as e:
        print(f"❌ 初始化失败: {e}")
        print("请确保 .env 文件中已配置 DEEPSEEK_API_KEY")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        sys.exit(1)
    
    client.set_system_prompt(
        "你是 Algorhythm 音乐制作助手，专注于帮助用户进行音乐创作、编曲和音乐理论分析。"
        "你了解各种乐器的特性、和弦进行、以及音乐制作工具。"
    )
    
    print("开始对话 (输入 /quit 退出):\n")
    
    while True:
        try:
            user_input = input("👤 你: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['/quit', '/exit', '/q']:
                print("\n👋 再见！祝你创作愉快！")
                break
            
            if user_input.lower() in ['/clear', '/c']:
                client.clear_history()
                print("🗑️  对话历史已清空\n")
                continue
            
            if user_input.lower() in ['/help', '/h']:
                print_help()
                continue
            
            if user_input.lower() == '/history':
                if not client.conversation_history:
                    print("📜 暂无对话历史\n")
                else:
                    print("\n📜 对话历史:")
                    for msg in client.conversation_history:
                        role = "👤 你" if msg["role"] == "user" else "🤖 AI"
                        print(f"  {role}: {msg['content'][:50]}...")
                    print()
                continue
            
            if user_input.startswith('/system '):
                new_prompt = user_input[8:].strip()
                if new_prompt:
                    client.set_system_prompt(new_prompt)
                    print(f"⚙️  系统提示词已更新\n")
                continue
            
            print("🤖 AI: ", end="", flush=True)
            
            try:
                response = client.chat(user_input, stream=False)
                print(response)
            except Exception as e:
                print(f"\n❌ API 调用失败: {e}")
            
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！祝你创作愉快！")
            break
        except EOFError:
            print("\n\n👋 再见！")
            break


if __name__ == "__main__":
    main()

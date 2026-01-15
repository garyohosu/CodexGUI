"""
OpenAI Client Module

Handles communication with OpenAI API for planning and summarization.
"""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import json

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    OpenAI = None


class MessageRole(Enum):
    """Message roles for chat."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatMessage:
    """Chat message."""
    role: MessageRole
    content: str


class OpenAIClient:
    """
    Client for OpenAI API.
    
    Handles three main operations:
    1. Plan Generation: Convert user request into safe execution plan
    2. Clarification: Ask follow-up questions when needed
    3. Summarization: Summarize execution results
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
        """
        if not OPENAI_AVAILABLE:
            raise RuntimeError("OpenAI package not installed. Run: pip install openai")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.conversation_history: List[ChatMessage] = []
    
    def generate_plan(
        self,
        user_request: str,
        task_context: Dict[str, Any],
        folder_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate execution plan from user request.
        
        Args:
            user_request: User's request text
            task_context: Context about selected task
            folder_info: Information about target folder (path, file count, etc.)
        
        Returns:
            Plan dictionary with:
            - type: "plan" or "clarify"
            - steps: List of execution steps (if plan)
            - question: Clarification question (if clarify)
            - warnings: Safety warnings
        """
        # Build system prompt
        system_prompt = self._build_planning_system_prompt()
        
        # Build user message with context
        user_message = self._build_planning_user_message(
            user_request, task_context, folder_info
        )
        
        # Call API
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        response = self._call_api(messages)
        
        # Parse response as JSON
        try:
            plan = json.loads(response)
            return plan
        except json.JSONDecodeError:
            # If not JSON, treat as plain text plan
            return {
                "type": "plan",
                "steps": [response],
                "warnings": []
            }
    
    def summarize_result(
        self,
        plan: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> str:
        """
        Summarize execution result for user.
        
        Args:
            plan: Original execution plan
            execution_result: Result from execution (stdout, stderr, exit_code, etc.)
        
        Returns:
            User-friendly summary text
        """
        system_prompt = """あなたはコード実行結果を要約するアシスタントです。
        
実行結果を分析して、以下の形式でユーザーに報告してください：

1. 実行結果（成功/失敗）
2. 主な変更内容または発見事項
3. 次に推奨されるアクション（あれば）

技術的な詳細は省略し、ユーザーが理解しやすい言葉で説明してください。"""
        
        user_message = f"""## 実行計画
{json.dumps(plan, ensure_ascii=False, indent=2)}

## 実行結果
終了コード: {execution_result.get('exit_code', -1)}
標準出力: {execution_result.get('stdout', '')[:500]}
標準エラー: {execution_result.get('stderr', '')[:500]}

この結果を要約してください。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        return self._call_api(messages)
    
    def chat(self, user_message: str, system_context: Optional[str] = None) -> str:
        """
        General chat conversation.
        
        Args:
            user_message: User's message
            system_context: Optional system context
        
        Returns:
            Assistant's response
        """
        messages = []
        
        if system_context:
            messages.append({"role": "system", "content": system_context})
        
        # Add conversation history
        for msg in self.conversation_history[-10:]:  # Keep last 10 messages
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        # Add new message
        messages.append({"role": "user", "content": user_message})
        
        # Call API
        response = self._call_api(messages)
        
        # Update history
        self.conversation_history.append(
            ChatMessage(MessageRole.USER, user_message)
        )
        self.conversation_history.append(
            ChatMessage(MessageRole.ASSISTANT, response)
        )
        
        return response
    
    def _build_planning_system_prompt(self) -> str:
        """Build system prompt for plan generation."""
        return """あなたはファイル操作タスクを安全に計画するアシスタントです。

## あなたの役割
1. ユーザーの依頼を分析する
2. 必要に応じて追加情報を質問する
3. 安全な実行計画を JSON 形式で生成する

## 計画の原則
- **安全第一**: 削除や上書きは慎重に
- **確認重視**: 危険な操作は必ず事前確認
- **最小限の変更**: 必要最小限の操作のみ
- **可逆性**: 可能な限りバックアップを作成

## 出力形式（JSON）

### パターン1: 追加質問が必要な場合
```json
{
  "type": "clarify",
  "question": "具体的な質問内容",
  "suggestions": ["選択肢1", "選択肢2"]
}
```

### パターン2: 実行計画を返す場合
```json
{
  "type": "plan",
  "steps": [
    {
      "action": "list_files",
      "description": "ファイル一覧を取得",
      "command": "ls -la",
      "safe": true
    },
    {
      "action": "organize_files",
      "description": "ファイルを整理",
      "command": "適切なコマンド",
      "safe": true,
      "requires_confirmation": false
    }
  ],
  "warnings": ["警告メッセージ（あれば）"],
  "backup_required": false
}
```

## 危険判定
以下の操作は `requires_confirmation: true` にする：
- ファイル削除
- ファイル上書き
- 10個以上のファイル移動
- システムフォルダへのアクセス

必ず JSON 形式で返答してください。"""
    
    def _build_planning_user_message(
        self,
        user_request: str,
        task_context: Dict[str, Any],
        folder_info: Dict[str, Any]
    ) -> str:
        """Build user message with context for planning."""
        return f"""## ユーザーの依頼
{user_request}

## タスクコンテキスト
タスク名: {task_context.get('title', 'Unknown')}
説明: {task_context.get('description', '')}

## 対象フォルダ情報
パス: {folder_info.get('path', '')}
ファイル数: {folder_info.get('file_count', 0)}
選択ファイル: {folder_info.get('selected_files', [])}

上記の情報をもとに、安全な実行計画を JSON 形式で生成してください。
不明点があれば、clarify タイプで質問してください。"""
    
    def _call_api(self, messages: List[Dict[str, str]]) -> str:
        """
        Call OpenAI API.
        
        Args:
            messages: List of message dictionaries
        
        Returns:
            Response text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def is_available(self) -> bool:
        """Check if OpenAI package is available."""
        return OPENAI_AVAILABLE


def test_connection(api_key: str) -> bool:
    """
    Test OpenAI API connection.
    
    Args:
        api_key: API key to test
    
    Returns:
        True if connection successful, False otherwise
    """
    if not OPENAI_AVAILABLE:
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
    except Exception:
        return False

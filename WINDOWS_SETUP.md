# CodexGUI - Windows Setup Guide

## Windows 11でのセットアップ手順

### 前提条件

1. **Python 3.8以上がインストール済み**
   - Python公式サイトからダウンロード: https://www.python.org/downloads/

2. **OpenAI Codex CLIのインストール**
   - OpenAI公式サイトにアクセス: https://developers.openai.com/codex/cli
   - Windowsインストーラーをダウンロード
   - インストール後、コマンドプロンプトで `codex --version` を実行して確認

### インストール手順

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/garyohosu/CodexGUI.git
   cd CodexGUI
   ```

2. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **アプリケーションの起動**
   ```bash
   python main.py
   ```

### Codex CLIが見つからない場合

アプリケーション起動時に「Codex CLI Not Found」エラーが表示された場合:

#### 方法1: 設定ダイアログで手動設定

1. メニューバーから **File → Settings** を選択
2. 「Codex CLI Path」にCodexの実行ファイルパスを入力
   - 例: `C:\Program Files\OpenAI\Codex\codex.exe`
   - または `codex.exe` (PATHに含まれている場合)
3. 「Browse...」ボタンでファイルを直接選択も可能
4. 「OK」をクリックして保存

#### 方法2: PATHに追加

1. Windowsの「環境変数」設定を開く
2. システム環境変数の「Path」に Codex CLI のインストールディレクトリを追加
3. コマンドプロンプトを再起動
4. `codex --version` で動作確認

### トラブルシューティング

#### エラー: "Codex CLI is not available in your system"

**原因:**
- Codex CLIがインストールされていない
- Codex CLIがシステムPATHに含まれていない
- 実行ファイル名が異なる

**解決方法:**
1. **Help → Codex CLI Installation** メニューで詳細なインストール手順を確認
2. **File → Settings** で手動でパスを設定
3. Codex CLIをインストールしてアプリケーションを再起動

#### エラー: "Permission denied"

**原因:**
- 実行権限がない

**解決方法:**
- 管理者権限でコマンドプロンプトを開いてアプリケーションを起動

### 設定ファイルの場所

CodexGUIの設定は以下の場所に保存されます:
```
C:\Users\<ユーザー名>\.codexgui\settings.json
```

この設定ファイルを削除すると、設定がリセットされます。

## 使い方

1. **タスクテンプレートを選択**
   - 左パネルから実行したいタスクを選択

2. **対象フォルダを選択**
   - 「Browse...」ボタンで処理したいフォルダを指定

3. **プロンプトを確認/編集**
   - テンプレートに応じたプロンプトが自動入力されます
   - 必要に応じてカスタマイズ可能

4. **実行**
   - 「Execute Task」ボタンをクリック
   - 右パネルにリアルタイムで実行結果が表示されます

## 利用可能なタスクテンプレート

- ファイル整理
- 名刺データ抽出
- コード解析
- レシート→経費レポート
- ドキュメント要約
- 写真整理
- コードレビュー
- データクリーンアップ
- 議事録要約
- カスタムタスク

## サポート

問題が発生した場合は、GitHubのIssuesページで報告してください:
https://github.com/garyohosu/CodexGUI/issues

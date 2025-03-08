# DevinAgent

DevinAgentは、OpenHandsフレームワーク上に構築された自律型ソフトウェアエンジニアリングエージェントです。

## 特徴

- **長期的な計画立案と推論**: タスクを小さなステップに分割し、順番に実行します
- **コードの作成、実行、テスト**: コードを書き、実行し、テストする能力を持ちます
- **バグの検出と修正**: エラーを検出し、自動的に修正します
- **フィードバックへの対応**: ユーザーからのフィードバックに基づいて計画を調整します
- **新しい技術への適応**: 新しい技術やフレームワークに適応します

## セットアップ

専用の環境をセットアップするには、以下のコマンドを実行します：

```bash
# セットアップスクリプトを実行
./setup.sh

# 環境をアクティブ化
source devin_env/bin/activate
```

## 使用方法

DevinAgentは、OpenHandsフレームワークを通じて使用できます：

```python
from openhands.agenthub.devin_agent import DevinAgent
from openhands.core.config.agent_config import AgentConfig

# エージェント設定を作成
config = AgentConfig(
    devin_enable_planning=True,
    devin_max_plan_steps=10,
    devin_enable_feedback=True
)

# エージェントを初期化
agent = DevinAgent(config=config)

# エージェントを使用
# ...
```

## コンポーネント

- **DevinAgent**: メインのエージェント実装
- **PlanningSystem**: タスク計画と実行を管理
- **ContextManager**: 長期的なコンテキストとメモリを処理
- **Tools Module**: 様々なツール（シェル、ファイル操作など）へのアクセスを提供

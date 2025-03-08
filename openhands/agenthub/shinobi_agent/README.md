# 忍びAI (Shinobi AI) Agent

忍びAI (Shinobi AI) is a personal assistant agent with long-term memory capabilities, adaptive learning, and personalized support. The agent implements a sophisticated memory architecture and conversation framework that supports deep personalization and contextual understanding.

## Features

- **Long-term Memory System**: Multi-layered memory architecture with working, episodic, semantic, and procedural memory
- **Adaptive Dialogue Framework**: Three dialogue modes (reactive, proactive, reflective) that adapt to user needs
- **Emotion Analysis**: Multi-dimensional emotion tracking (valence, arousal, dominance)
- **Personalized Support**: Learning optimization, routine management, and wellbeing support

## Architecture

The Shinobi AI agent consists of the following components:

- **ShinobiAgent**: Main agent class that implements the 5-step conversation loop
- **ShinobiMemorySystem**: Memory system with 4-layer hierarchy
- **ShinobiDialogueManager**: Dialogue management system with 3 dialogue modes
- **ShinobiEmotionAnalyzer**: Emotion analysis system with multi-dimensional model
- **ShinobiResponseGenerator**: Response generation system with adaptive style

## Usage

```python
from openhands.agenthub.shinobi_agent import ShinobiAgent

# Initialize the agent
agent = ShinobiAgent(llm, config)

# Use the agent in a conversation
await agent.step(state, event_stream)
```

## Testing

A simplified test script is provided to demonstrate the agent's functionality:

```bash
python -m openhands.agenthub.shinobi_agent.test_shinobi_agent
```

## Implementation Details

### Memory System

The memory system implements a 4-layer hierarchy:

1. **Working Memory**: Current conversation context and state
2. **Episodic Memory**: Chronological record of past conversations and events
3. **Semantic Memory**: Structured knowledge about the user
4. **Procedural Memory**: Effective dialogue patterns

### Dialogue Modes

The agent supports three dialogue modes:

1. **Reactive**: Responding to user questions/requests
2. **Proactive**: Situational suggestions and interventions
3. **Reflective**: Progress and pattern review

### Emotion Analysis

The emotion analysis system tracks:

- **Valence**: Positive vs. Negative (0-1)
- **Arousal**: Calm vs. Excited (0-1)
- **Dominance**: Submissive vs. Dominant (0-1)
- **Primary Emotion**: The primary detected emotion

### 5-Step Conversation Loop

1. **入力理解 (Input Understanding)**: Understanding user intent and emotions
2. **文脈統合 (Context Integration)**: Integrating long-term memory and current situation
3. **思考生成 (Thought Generation)**: Deciding appropriate responses/actions
4. **表現最適化 (Expression Optimization)**: Forming responses based on user state
5. **記憶更新 (Memory Update)**: Extracting and updating important information

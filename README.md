# Dialmate AI

An AI-powered communication assistant that analyzes conversations and provides insights using advanced metrics.

## Mathematical Models

### Sentiment Analysis Metrics

For a conversation C with n messages: C = {m₁, m₂, ..., mₙ}

For each message mᵢ:

$S(m_i) = \{p, n, u\}$ where:
- p = positive
- n = negative
- u = neutral

Sentiment Score for message mᵢ:

$SS(m_i) = \frac{\sum_{w \in m_i} s(w)}{|m_i|}$

where s(w) is the sentiment value of word w

### Conversation Flow Metrics

Response Time between messages:

$RT(m_i, m_{i+1}) = t(m_{i+1}) - t(m_i)$

Conversation Engagement Score:

$E(C) = \frac{1}{n} \sum_{i=1}^n \frac{|m_i|}{RT(m_i, m_{i+1})}$

### Topic Coherence

For a set of topics T in conversation C:

$TC(T,C) = \sum_{t \in T} \sum_{(w_i, w_j) \in t} PMI(w_i, w_j)$

where PMI is Pointwise Mutual Information

## Features

- Real-time sentiment analysis
- Conversation flow analysis
- Topic coherence tracking
- Voice message support
- Interactive UI with inline keyboards
- Database integration for conversation history

## Setup

1. Clone the repository
2. Activate virtual environment:
```bash
source dialmateai/dialmate/venv/bin/activate  # Unix/MacOS
# or
dialmateai/dialmate/venv/Scripts/Activate.ps1  # Windows
```
3. Install dependencies
4. Configure environment variables
5. Run the application

## Usage

The bot responds to the following commands:
- `/start` - Initialize the bot
- `/help` - Display help information

You can interact with the bot by:
- Sending text messages for analysis
- Sending voice messages for transcription and analysis
- Using inline keyboard buttons for navigation

## Error Handling

The bot includes comprehensive error handling:
- Database connection errors
- Message processing errors
- Voice message handling errors
- General runtime errors

## License

[Your License Here]
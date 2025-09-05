# Smart Chatbot Backend

A FastAPI-based chatbot backend with OpenAI streaming responses and memory-ready architecture.

## Features

- **Streaming Responses**: Real-time chat responses using OpenAI's streaming API
- **Memory Integration**: In-memory conversation history with placeholder for Mem0 integration
- **Clean Architecture**: Modular design with separate routes, services, and models
- **Production Ready**: Error handling, logging, and health checks
- **Configurable**: Environment-based configuration with customizable system prompts

## Project Structure

```
app/
├── main.py              # FastAPI application entry point
├── config.py            # Configuration settings
├── models/
│   └── chat.py          # Pydantic models for requests/responses
├── routes/
│   ├── chat.py          # Chat endpoints with streaming
│   └── health.py        # Health check endpoints
└── services/
    ├── openai_service.py # OpenAI API integration
    └── memory.py        # Memory management (Mem0 ready)
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000
APP_NAME=Smart Chatbot
MEM0_API_KEY=your_mem0_api_key
DEBUG=false
```

### 3. Run the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### Chat Endpoints

#### POST `/api/chat`
Streaming chat endpoint with real-time responses.

**Request:**
```json
{
  "user_id": "user123",
  "message": "Hello, how are you today?"
}
```

**Response:** Server-sent events stream with chunks:
```
data: {"content": "Hello! I'm doing well", "done": false}

data: {"content": ", thank you for asking.", "done": false}

data: {"content": "", "done": true}

data: [DONE]
```

#### POST `/api/chat/simple`
Non-streaming chat endpoint for testing.

**Request:** Same as streaming endpoint

**Response:**
```json
{
  "user_id": "user123",
  "message": "Hello, how are you today?",
  "response": "Hello! I'm doing well, thank you for asking. How can I help you today?",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET `/api/chat/history/{user_id}`
Get conversation history for a user.

**Response:**
```json
{
  "user_id": "user123",
  "history": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "user_message": "Hello",
      "assistant_response": "Hi there!"
    }
  ],
  "count": 1
}
```

#### DELETE `/api/chat/history/{user_id}`
Clear conversation history for a user.

### Health Endpoints

#### GET `/api/health`
Basic health check.

#### GET `/api/health/detailed`
Detailed health check with system information.

## Example Usage

### cURL Examples

#### Streaming Chat
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "What is the capital of France?"
  }'
```

#### Simple Chat
```bash
curl -X POST "http://localhost:8000/api/chat/simple" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "message": "What is the capital of France?"
  }'
```

#### Health Check
```bash
curl "http://localhost:8000/api/health"
```

### Python Client Example

```python
import requests
import json

# Simple chat
response = requests.post(
    "http://localhost:8000/api/chat/simple",
    json={
        "user_id": "user123",
        "message": "Hello, how are you?"
    }
)
print(response.json())

# Streaming chat
response = requests.post(
    "http://localhost:8000/api/chat",
    json={
        "user_id": "user123",
        "message": "Tell me a story"
    },
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data: '):
            data = line[6:]  # Remove 'data: ' prefix
            if data == '[DONE]':
                break
            try:
                chunk = json.loads(data)
                print(chunk['content'], end='', flush=True)
            except json.JSONDecodeError:
                pass
```

## Memory Integration

The current implementation includes:

- **In-memory storage** for conversation history
- **Placeholder methods** for Mem0 integration
- **Context-aware responses** using recent conversation history

### Future Mem0 Integration

The memory service is designed to easily integrate with Mem0:

```python
# In app/services/memory.py
async def store_important_fact(self, user_id: str, fact: str, importance: float = 0.5):
    # TODO: Integrate with Mem0 for persistent memory storage
    pass

async def retrieve_relevant_memories(self, user_id: str, query: str):
    # TODO: Integrate with Mem0 for semantic memory retrieval
    pass
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-3.5-turbo` |
| `OPENAI_TEMPERATURE` | Response creativity (0-1) | `0.7` |
| `OPENAI_MAX_TOKENS` | Maximum response length | `1000` |
| `APP_NAME` | Application name | `Smart Chatbot` |
| `DEBUG` | Debug mode | `false` |
| `SYSTEM_PROMPT` | Custom system prompt | Default helpful assistant prompt |

### Customizing System Prompt

You can customize the system prompt by:

1. Setting `SYSTEM_PROMPT` in your `.env` file
2. Or programmatically updating it via the OpenAI service

## Development

### Running Tests

```bash
pytest
```

### Code Quality

The codebase follows these principles:

- **Modular design** with clear separation of concerns
- **Type hints** throughout the codebase
- **Comprehensive error handling** and logging
- **Production-ready** configuration and deployment
- **Clean, readable code** with proper documentation

## Next Steps

This backend is ready for:

1. **Frontend Integration**: Connect with React/TypeScript frontend
2. **Mem0 Integration**: Add persistent memory storage
3. **Authentication**: Add user authentication and authorization
4. **Rate Limiting**: Implement API rate limiting
5. **Monitoring**: Add metrics and monitoring
6. **Deployment**: Deploy to cloud platforms (AWS, GCP, Azure)

## License

MIT License

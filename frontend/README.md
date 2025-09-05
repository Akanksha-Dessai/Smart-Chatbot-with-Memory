# Smart Chatbot Frontend

A React + TypeScript frontend for the Smart Chatbot with live message streaming.

## Features

- **Live Message Streaming**: Real-time chat responses from FastAPI backend
- **Clean UI**: Simple, modern interface without logos or icons
- **TypeScript**: Full type safety and better development experience
- **Responsive Design**: Works on desktop and mobile devices
- **User Management**: Configurable user ID for conversation tracking
- **Connection Status**: Real-time backend connection monitoring

## Project Structure

```
frontend/
├── public/
│   └── index.html          # HTML template
├── src/
│   ├── components/         # React components
│   │   ├── ChatWindow.tsx  # Main chat interface
│   │   ├── MessageList.tsx # Message display
│   │   ├── Message.tsx     # Individual message
│   │   ├── MessageInput.tsx # Message input form
│   │   ├── TypingIndicator.tsx # Loading animation
│   │   └── Header.tsx      # App header
│   ├── types/
│   │   └── chat.ts         # TypeScript type definitions
│   ├── App.tsx             # Main app component
│   ├── App.css             # App-specific styles
│   ├── index.tsx           # React entry point
│   └── index.css           # Global styles
├── package.json            # Dependencies and scripts
└── tsconfig.json           # TypeScript configuration
```

## Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm start
```

The frontend will be available at http://localhost:3000

### 3. Build for Production

```bash
npm run build
```

## Configuration

The frontend is configured to proxy API requests to the FastAPI backend running on `http://localhost:8000`. This is set in `package.json`:

```json
{
  "proxy": "http://localhost:8000"
}
```

## Usage

1. **Start the Backend**: Make sure the FastAPI backend is running on port 8000
2. **Start the Frontend**: Run `npm start` in the frontend directory
3. **Open Browser**: Navigate to http://localhost:3000
4. **Set User ID**: Enter a user ID in the header (default: user123)
5. **Start Chatting**: Type messages and see real-time streaming responses

## Features

### Live Message Streaming
- Messages stream in real-time as the AI generates responses
- Smooth typing animation with dots indicator
- Auto-scroll to latest messages

### User Management
- Configurable user ID for conversation tracking
- Each user maintains separate conversation history
- User ID displayed in chat header

### Connection Monitoring
- Real-time backend connection status
- Visual indicators for connection state
- Error handling for connection issues

### Responsive Design
- Mobile-friendly interface
- Adaptive layout for different screen sizes
- Touch-friendly input controls

## API Integration

The frontend integrates with the following backend endpoints:

- `POST /api/chat` - Streaming chat responses
- `GET /api/health` - Backend health check
- `GET /api/chat/history/{user_id}` - Conversation history (future use)

## Development

### Available Scripts

- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### TypeScript

The project uses TypeScript for type safety. Key types are defined in `src/types/chat.ts`:

- `Message` - Chat message structure
- `StreamChunk` - Streaming response chunks
- `ChatRequest` - API request format
- `ChatResponse` - API response format

## Styling

The UI uses a clean, minimal design with:

- Modern CSS with flexbox and grid
- Responsive breakpoints
- Smooth animations and transitions
- Accessible color contrast
- No external dependencies for styling

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT License

#!/bin/bash

# Upload key files to GitHub repository using GitHub API
# This script uploads the essential files for the Smart Chatbot project

REPO="Akanksha-Dessai/Smart-Chatbot-with-Memory"
BRANCH="main"

# Function to upload file
upload_file() {
    local file_path="$1"
    local message="$2"
    
    if [ -f "$file_path" ]; then
        echo "Uploading $file_path..."
        gh api repos/$REPO/contents/$file_path \
            --method PUT \
            --field message="$message" \
            --field content="$(base64 -w 0 "$file_path")" \
            --field branch=$BRANCH
        echo "✅ $file_path uploaded successfully"
    else
        echo "❌ File $file_path not found"
    fi
}

echo "🚀 Uploading Smart Chatbot project files to GitHub..."

# Upload key backend files
upload_file "requirements.txt" "Add Python dependencies"
upload_file "run_server.py" "Add server startup script"
upload_file "app/main.py" "Add FastAPI main application"
upload_file "app/config.py" "Add configuration settings"
upload_file "app/models/chat.py" "Add chat models"
upload_file "app/routes/chat.py" "Add chat routes"
upload_file "app/routes/health.py" "Add health check routes"
upload_file "app/routes/memory.py" "Add memory management routes"
upload_file "app/services/openai_service.py" "Add OpenAI service"
upload_file "app/services/memory.py" "Add memory service"
upload_file "app/services/mem0_service.py" "Add Mem0 service"

# Upload frontend files
upload_file "frontend/package.json" "Add frontend dependencies"
upload_file "frontend/src/App.tsx" "Add main React component"
upload_file "frontend/src/components/ChatWindow.tsx" "Add chat window component"
upload_file "frontend/src/components/MemoryManager.tsx" "Add memory manager component"

# Upload documentation
upload_file "PROJECT_OVERVIEW.md" "Add project overview"
upload_file "MEM0_INTEGRATION_COMPLETE.md" "Add Mem0 integration docs"

echo "🎉 All files uploaded successfully!"
echo "📁 Repository: https://github.com/$REPO"

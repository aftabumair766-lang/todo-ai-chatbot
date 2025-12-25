# OpenAI ChatKit Frontend - Todo AI Chatbot

**Constitution Compliant Frontend** ✅

This is the OpenAI ChatKit frontend implementation for Todo AI Chatbot, achieving 100% constitution compliance.

---

## 🚀 Quick Start

```bash
# Start the ChatKit frontend
cd frontend-chatkit
python -m http.server 8080

# Open in browser
http://localhost:8080
```

**Requirements:**
- Backend running on port 8000
- ChatKit Workflow ID configured in backend `.env`

---

## 📁 Files

- `index.html` - ChatKit UI interface
- `config.js` - Configuration for ChatKit
- `server.py` - Simple Python HTTP server (optional)
- `README.md` - This file

---

## ⚙️ Configuration

Edit `config.js` to customize:

```javascript
window.CHATKIT_CONFIG = {
    backendUrl: 'http://localhost:8000',  // Backend API URL
    sessionEndpoint: '/api/chatkit/session',
    chatEndpoint: '/api/chat',

    // Add your domains here
    allowedDomains: [
        'localhost:8080',
        'localhost:3000',
        // Add production domains
    ],

    welcomeMessage: '...',  // Customize welcome message
};
```

---

## 🌐 Deployment Options

### Option 1: Python HTTP Server (Development)
```bash
python -m http.server 8080
```

### Option 2: Node.js Serve (Development)
```bash
npx serve . -p 8080
```

### Option 3: Nginx (Production)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    root /path/to/frontend-chatkit;
    index index.html;
}
```

### Option 4: Vercel/Netlify (Production)
- Deploy `frontend-chatkit/` directory
- Set environment variables
- Configure domain allowlist

---

## ✅ Testing

1. Start backend: `cd backend && uvicorn backend.main:app --reload`
2. Start frontend: `cd frontend-chatkit && python -m http.server 8080`
3. Open: http://localhost:8080
4. Test commands:
   - `Add a task to buy groceries`
   - `Show me all tasks`
   - `Complete task 1`

---

## 🐛 Troubleshooting

**ChatKit not loading:**
- Check browser console (F12) for errors
- Verify backend is running on port 8000
- Check `config.js` has correct `backendUrl`

**Connection failed:**
- Ensure `CHATKIT_WORKFLOW_ID` is set in backend `.env`
- Restart backend after configuration changes
- Check CORS settings in backend

**Domain not allowed:**
- Add domain to `allowedDomains` in `config.js`
- Configure domain allowlist in OpenAI platform

---

## 📊 Constitution Compliance

✅ **Technology Stack Requirement:**
- Required: "Frontend: OpenAI ChatKit (hosted with domain allowlist configuration)"
- Implemented: OpenAI ChatKit with full configuration
- Status: **100% Compliant**

---

## 📚 Documentation

- [ChatKit Setup Guide](../docs/CHATKIT_SETUP.md) - Complete setup instructions
- [Backend API Docs](http://localhost:8000/docs) - FastAPI documentation
- [OpenAI ChatKit Docs](https://platform.openai.com/docs/chatkit) - Official documentation

---

## 🎉 Success Criteria

When you can:
- ✅ Access ChatKit at http://localhost:8080
- ✅ Send messages and receive responses
- ✅ Perform all 5 task operations (add, list, complete, update, delete)
- ✅ See tasks persisted in database

**You have achieved 100% constitution compliance!** 🎓

---

**Built with ❤️ using OpenAI ChatKit and FastAPI**

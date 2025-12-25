# Reusable AI Agents Catalog

This catalog lists all available domain adapters in the reusable agent framework.

---

## 📚 Available Agents

### 1. Todo Management Agent ✅ (Production)

**Domain:** Task management with friendly emoji interface

**File:** `adapters/todo_adapter.py`

**Capabilities:**
- Add tasks with natural language
- List tasks (all, pending, completed)
- Complete tasks by ID
- Delete tasks
- Update task titles and descriptions

**Personality:** Friendly and encouraging with emoji confirmations

**Tools:**
- `add_task(title, description)`
- `list_tasks(status)`
- `complete_task(task_id)`
- `delete_task(task_id)`
- `update_task(task_id, title, description)`

**Usage:**
```python
from backend.agents.reusable import ReusableAgent, TodoDomainAdapter

agent = ReusableAgent(adapter=TodoDomainAdapter())
result = await agent.process_message(user_id, "Add buy milk", [], db)
# → "✅ Task added: Buy milk"
```

**Status:** ✅ Production-ready (extracted from existing `todo_agent.py`)

---

### 2. CRM Agent 🎯 (Example)

**Domain:** Customer Relationship Management for sales teams

**File:** `adapters/crm_adapter.py`

**Capabilities:**
- Create and manage customer contacts
- Track sales deals and opportunities
- Log customer interactions
- Manage sales pipeline
- Generate reports

**Personality:** Professional and business-focused (no emojis)

**Tools:**
- `create_contact(name, email, company, phone)`
- `list_contacts(company, limit)`
- `create_deal(contact_id, title, amount, stage)`
- `update_deal_stage(deal_id, stage)`
- `log_interaction(contact_id, type, notes)`

**Usage:**
```python
from backend.agents.reusable import ReusableAgent, CRMDomainAdapter

crm_agent = ReusableAgent(adapter=CRMDomainAdapter())
result = await crm_agent.process_message(
    user_id,
    "Create contact John Doe at Acme Corp",
    [],
    db
)
# → "Contact created: John Doe (Acme Corp)"
```

**Status:** 📝 Example implementation (placeholder MCP tools)

---

### 3. Authentication & Authorization Agent 🔐 (Security-First)

**Domain:** User authentication, authorization, and access control

**File:** `adapters/auth_adapter.py`

**Capabilities:**
- User registration with email verification
- Secure login with JWT/OAuth2
- Logout and token revocation
- Token refresh
- Password reset flows
- Multi-Factor Authentication (MFA)
- Role-Based Access Control (RBAC)
- Permission checking
- Policy-driven authorization

**Personality:** Professional and security-conscious

**Security Features:**
- Password hashing (bcrypt/argon2/scrypt)
- Brute-force protection
- Account lockout after failed attempts
- Rate limiting
- User enumeration prevention
- Comprehensive audit logging
- OWASP compliance

**Tools:**
- `register_user(email, password, full_name)`
- `login_user(email, password, mfa_code)`
- `logout_user(access_token)`
- `refresh_token(refresh_token)`
- `request_password_reset(email)`
- `verify_email(email, verification_code)`
- `check_permission(user_id, resource, action)`
- `enable_mfa(user_id, method)` (optional)
- `verify_mfa(user_id, code)` (optional)

**Configuration:**
```python
from backend.agents.reusable.adapters.auth_adapter import (
    AuthDomainAdapter,
    AuthAdapterConfig
)

config = AuthAdapterConfig(
    user_store=PostgreSQLUserStore(),    # Your user database
    token_provider=JWTTokenProvider(),    # JWT implementation
    password_hasher=Argon2Hasher(),       # Password hashing
    mfa_provider=TwilioMFAProvider(),     # Optional MFA
    policy_engine=OPAPolicyEngine(),      # Optional authz
    audit_logger=CloudWatchLogger(),      # Optional logging
    password_min_length=12,
    max_login_attempts=5,
    require_mfa=True
)

auth_agent = ReusableAgent(adapter=AuthDomainAdapter(config))
```

**Usage:**
```python
# Register
result = await auth_agent.process_message(
    user_id="anonymous",
    message="Register user alice@example.com with password SecurePass123!",
    conversation_history=[],
    db=db
)
# → "Registration successful. Please verify your email."

# Login
result = await auth_agent.process_message(
    user_id="anonymous",
    message="Login user alice@example.com with password SecurePass123!",
    conversation_history=[],
    db=db
)
# → Returns access_token, refresh_token

# Check permission
result = await auth_agent.process_message(
    user_id="user123",
    message="Can I delete project:456?",
    conversation_history=[],
    db=db
)
# → "Authorized" or "Permission denied"
```

**Provider Interfaces:**
- `UserStoreProvider` - User data persistence
- `TokenProvider` - Token generation/validation
- `PasswordHasher` - Password hashing
- `MFAProvider` - Multi-Factor Authentication
- `PolicyEngine` - Authorization policies
- `AuditLogger` - Security audit logging

**Status:** 🚀 Framework-agnostic design (requires provider implementations)

**Documentation:** See `docs/AUTH_AGENT_GUIDE.md` for complete guide

---

## 🎨 Agent Comparison

| Feature | Todo Agent | CRM Agent | Auth Agent |
|---------|-----------|-----------|------------|
| **Personality** | Friendly, emojis | Professional, formal | Security-focused |
| **Domain** | Task management | Sales & CRM | Authentication & Authorization |
| **Tools** | 5 tools (CRUD tasks) | 5 tools (contacts, deals) | 7-9 tools (auth flows) |
| **Response Style** | ✅ Emojis | Text only | Security messages |
| **Security Focus** | Low | Medium | High (OWASP) |
| **Greeting** | "👋 Hello! I'm your Todo Assistant..." | "Hello! I'm your CRM Assistant..." | "Hello! I'm your Authentication Security Assistant..." |
| **Error Handling** | User-friendly emojis | Professional messages | Generic (prevents enumeration) |
| **Status** | ✅ Production | 📝 Example | 🚀 Framework design |

---

## 🛠️ Creating Your Own Agent

### Step 1: Create Adapter File

```bash
touch backend/agents/reusable/adapters/your_adapter.py
```

### Step 2: Implement DomainAdapter

```python
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

class YourDomainAdapter(DomainAdapter):
    def get_system_prompt(self):
        return "You are a helpful [domain] assistant..."

    def get_tools(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "your_tool",
                    "description": "What it does",
                    "parameters": {...}
                }
            }
        ]

    def get_tool_handlers(self):
        return {
            "your_tool": self._your_tool_handler
        }

    async def _your_tool_handler(self, user_id, param, db=None):
        # Your implementation
        return {"success": True, "message": "Done"}
```

### Step 3: Add to Catalog

Update `__init__.py`:

```python
from backend.agents.reusable.adapters.your_adapter import YourDomainAdapter

__all__ = [
    "ReusableAgent",
    "DomainAdapter",
    "TodoDomainAdapter",
    "CRMDomainAdapter",
    "AuthDomainAdapter",
    "YourDomainAdapter"  # Add here
]
```

### Step 4: Use It

```python
from backend.agents.reusable import ReusableAgent, YourDomainAdapter

agent = ReusableAgent(adapter=YourDomainAdapter())
result = await agent.process_message(user_id, message, [], db)
```

---

## 💡 Domain Ideas

Here are more domains you could build:

### 1. E-commerce Agent 🛒

**Tools:**
- `search_products(query, category, price_range)`
- `get_product_details(product_id)`
- `add_to_cart(product_id, quantity)`
- `checkout(cart_id, payment_method)`
- `track_order(order_id)`

**Personality:** Helpful shopping assistant with product recommendations

### 2. Support Chatbot Agent 💬

**Tools:**
- `create_ticket(title, description, priority)`
- `search_knowledge_base(query)`
- `escalate_ticket(ticket_id, reason)`
- `close_ticket(ticket_id, resolution)`
- `get_ticket_status(ticket_id)`

**Personality:** Professional and empathetic

### 3. Calendar Agent 📅

**Tools:**
- `create_event(title, start, end, attendees)`
- `list_events(date_range)`
- `find_free_slots(duration, participants)`
- `send_meeting_invite(event_id, emails)`
- `reschedule_event(event_id, new_start)`

**Personality:** Efficient and organized

### 4. Weather Agent ☀️

**Tools:**
- `get_current_weather(city)`
- `get_forecast(city, days)`
- `get_weather_alerts(location)`

**Personality:** Friendly with weather emojis (☀️🌧️❄️⛅)

### 5. Finance Agent 💰

**Tools:**
- `get_account_balance(account_id)`
- `list_transactions(account_id, date_range)`
- `transfer_funds(from_account, to_account, amount)`
- `pay_bill(payee, amount)`
- `get_spending_report(month)`

**Personality:** Professional and precise

### 6. HR Chatbot Agent 👔

**Tools:**
- `request_time_off(start_date, end_date, reason)`
- `submit_expense(amount, category, receipt)`
- `get_payroll_info(employee_id)`
- `search_policies(query)`
- `book_conference_room(room_id, start, end)`

**Personality:** Professional and helpful

### 7. DevOps Agent 🔧

**Tools:**
- `deploy_service(service_name, environment)`
- `check_service_status(service_name)`
- `scale_service(service_name, replicas)`
- `view_logs(service_name, lines)`
- `rollback_deployment(service_name)`

**Personality:** Technical and precise

### 8. Social Media Agent 📱

**Tools:**
- `post_update(content, platforms)`
- `schedule_post(content, datetime, platforms)`
- `get_analytics(date_range)`
- `reply_to_comment(comment_id, reply)`

**Personality:** Creative and engaging

---

## 📊 Architecture

All agents share the same core architecture:

```
┌─────────────────────────────────────┐
│   ReusableAgent (Generic Core)     │
│   - OpenAI API integration          │
│   - Tool routing                    │
│   - Conversation management         │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│   DomainAdapter (Configuration)     │
│   - System prompt                   │
│   - Tool definitions                │
│   - Tool handlers                   │
│   - Response formatting             │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│      MCP Tools (Data Layer)         │
│   - Database operations             │
│   - External API calls              │
│   - Business logic                  │
└─────────────────────────────────────┘
```

**Key Principle:** Change domains by swapping adapters, not rewriting code.

---

## 🚀 Getting Started

### 1. Choose Your Domain

Pick from:
- ✅ Existing: Todo, CRM, Auth
- 🎨 Build Your Own: E-commerce, Support, Calendar, etc.

### 2. Review Example Adapters

- **TodoDomainAdapter** - Simple CRUD operations with emojis
- **CRMDomainAdapter** - Professional business assistant
- **AuthDomainAdapter** - Security-first with configuration

### 3. Create Your Adapter

Follow the template in [Creating Your Own Agent](#creating-your-own-agent)

### 4. Use It

```python
from backend.agents.reusable import ReusableAgent, YourAdapter

agent = ReusableAgent(adapter=YourAdapter())
result = await agent.process_message(user_id, message, [], db)
```

---

## 📚 Documentation

- **[README.md](./README.md)** - Framework overview
- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - Migrate from old code
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Developer quick reference
- **[REUSABLE_AGENTS_GUIDE.md](../../docs/REUSABLE_AGENTS_GUIDE.md)** - Complete guide with examples
- **[AUTH_AGENT_GUIDE.md](../../docs/AUTH_AGENT_GUIDE.md)** - Authentication & Authorization guide

---

## 🎓 Learn More

### Step 1: Understand Architecture

Read [README.md](./README.md) for framework overview.

### Step 2: Examine Existing Adapters

- **`adapters/todo_adapter.py`** - Production example
- **`adapters/crm_adapter.py`** - Business example
- **`adapters/auth_adapter.py`** - Security example

### Step 3: Build Your Own

Follow [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for step-by-step guide.

### Step 4: Deploy to Production

See [REUSABLE_AGENTS_GUIDE.md](../../docs/REUSABLE_AGENTS_GUIDE.md) for deployment best practices.

---

## 🤝 Contributing

To add your adapter to this catalog:

1. Create adapter in `adapters/`
2. Add to `__init__.py` exports
3. Add to this catalog
4. Add tests
5. Add documentation

---

## ✨ Summary

**Available Agents:**

| Agent | Domain | Status | Production-Ready |
|-------|--------|--------|------------------|
| TodoDomainAdapter | Task Management | ✅ Production | Yes |
| CRMDomainAdapter | Customer Relationships | 📝 Example | No (placeholder tools) |
| AuthDomainAdapter | Authentication & Authorization | 🚀 Framework | Yes (requires providers) |

**You can build agents for ANY domain in ~100 lines of code!** 🎉

---

**Questions? Check the documentation or open an issue!**

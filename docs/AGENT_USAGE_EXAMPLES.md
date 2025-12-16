# Agent Usage Examples

Practical examples of using the BaseAgent in different projects.

## 📋 Example 1: E-Commerce Order Agent

```python
"""
E-Commerce Agent - Handle orders, inventory, shipping
"""

from backend.agents.base_agent import BaseAgent
import os

# Step 1: Define your domain tools
ecommerce_tools = [
    {
        "type": "function",
        "function": {
            "name": "create_order",
            "description": "Create a new order for products",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_ids": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of product IDs to order"
                    },
                    "quantities": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Quantities for each product"
                    },
                    "shipping_address": {
                        "type": "string",
                        "description": "Shipping address"
                    }
                },
                "required": ["product_ids", "quantities"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "track_order",
            "description": "Track order status and shipping",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "Order ID to track"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products in catalog",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "category": {
                        "type": "string",
                        "description": "Optional category filter"
                    }
                },
                "required": ["query"]
            }
        }
    }
]

# Step 2: Implement tool handlers
async def create_order_handler(user_id, product_ids, quantities, shipping_address=None, db=None):
    """Create order in your database"""
    # Your e-commerce logic here
    order_id = f"ORD-{hash(str(product_ids))}"

    # Save to database
    # order = Order(user_id=user_id, products=product_ids, ...)
    # db.add(order)
    # await db.commit()

    return {
        "success": True,
        "order_id": order_id,
        "total": len(product_ids),
        "message": f"✅ Order {order_id} created successfully!"
    }

async def track_order_handler(user_id, order_id, db=None):
    """Track order status"""
    # Query your database
    # order = await db.query(Order).filter(Order.id == order_id).first()

    return {
        "order_id": order_id,
        "status": "shipped",
        "tracking_number": "TRK123456",
        "estimated_delivery": "Dec 20, 2025",
        "message": f"📦 Your order is on the way!"
    }

async def search_products_handler(user_id, query, category=None, db=None):
    """Search products"""
    # Query your product catalog
    # products = await db.query(Product).filter(Product.name.contains(query)).all()

    return {
        "results": [
            {"id": "P001", "name": "Laptop", "price": 999.99},
            {"id": "P002", "name": "Mouse", "price": 29.99}
        ],
        "count": 2
    }

# Step 3: Create agent instance
ecommerce_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4-turbo-preview",
    system_prompt=(
        "You are ShopBot, a friendly e-commerce assistant. "
        "Help customers search products, create orders, and track shipments. "
        "Always be helpful and provide clear order confirmations."
    ),
    tools=ecommerce_tools,
    tool_handlers={
        "create_order": create_order_handler,
        "track_order": track_order_handler,
        "search_products": search_products_handler
    }
)

# Step 4: Use the agent
async def handle_customer_message(user_id, message, db_session):
    """Handle customer chat message"""
    result = await ecommerce_agent.process_message(
        user_message=message,
        user_id=user_id,
        conversation_history=[],  # Load from your DB
        db=db_session
    )

    return result["response"]

# Example usage:
# response = await handle_customer_message(
#     user_id="customer_123",
#     message="I want to buy a laptop and a mouse",
#     db_session=db
# )
# print(response)  # "✅ Order ORD-xxx created successfully!"
```

---

## 📅 Example 2: Calendar/Appointment Agent

```python
"""
Calendar Agent - Book, cancel, reschedule appointments
"""

from backend.agents.base_agent import BaseAgent
from datetime import datetime, timedelta
import os

# Define calendar tools
calendar_tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book a new appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Appointment title"},
                    "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
                    "time": {"type": "string", "description": "Time (HH:MM)"},
                    "duration_minutes": {"type": "integer", "description": "Duration in minutes"}
                },
                "required": ["title", "date", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_appointments",
            "description": "List appointments for a date range",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "Start date (YYYY-MM-DD)"},
                    "end_date": {"type": "string", "description": "End date (YYYY-MM-DD)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string", "description": "Appointment ID"}
                },
                "required": ["appointment_id"]
            }
        }
    }
]

# Implement handlers
async def book_appointment_handler(user_id, title, date, time, duration_minutes=60, db=None):
    """Book appointment"""
    appointment_id = f"APT-{hash(f'{user_id}{date}{time}')}"

    # Save to database
    # appointment = Appointment(user_id=user_id, title=title, ...)
    # db.add(appointment)
    # await db.commit()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "title": title,
        "datetime": f"{date} {time}",
        "message": f"📅 Appointment booked: {title} on {date} at {time}"
    }

async def list_appointments_handler(user_id, start_date=None, end_date=None, db=None):
    """List appointments"""
    # Query database
    # appointments = await db.query(Appointment).filter(...).all()

    return {
        "appointments": [
            {"id": "APT001", "title": "Team Meeting", "date": "2025-12-15", "time": "10:00"},
            {"id": "APT002", "title": "Doctor Appointment", "date": "2025-12-16", "time": "14:00"}
        ],
        "count": 2
    }

async def cancel_appointment_handler(user_id, appointment_id, db=None):
    """Cancel appointment"""
    # Delete from database
    # appointment = await db.query(Appointment).filter(Appointment.id == appointment_id).first()
    # await db.delete(appointment)
    # await db.commit()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "message": f"🗑️ Appointment {appointment_id} cancelled"
    }

# Create calendar agent
calendar_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    system_prompt=(
        "You are CalendarBot, a helpful scheduling assistant. "
        "Help users book, view, and manage their appointments. "
        "Always confirm appointment details clearly."
    ),
    tools=calendar_tools,
    tool_handlers={
        "book_appointment": book_appointment_handler,
        "list_appointments": list_appointments_handler,
        "cancel_appointment": cancel_appointment_handler
    }
)

# Use it
# response = await calendar_agent.process_message(
#     user_message="Book a meeting with my team tomorrow at 2pm",
#     user_id="user_456",
#     conversation_history=[],
#     db=db_session
# )
```

---

## 🎫 Example 3: Customer Support Ticket Agent

```python
"""
Support Agent - Create tickets, search knowledge base, escalate issues
"""

from backend.agents.base_agent import BaseAgent
import os

support_tools = [
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a support ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Ticket subject"},
                    "description": {"type": "string", "description": "Detailed problem description"},
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Ticket priority"
                    },
                    "category": {
                        "type": "string",
                        "description": "Issue category (billing, technical, etc.)"
                    }
                },
                "required": ["subject", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search help articles and documentation",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_ticket_status",
            "description": "Check status of existing ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {"type": "string", "description": "Ticket ID"}
                },
                "required": ["ticket_id"]
            }
        }
    }
]

async def create_ticket_handler(user_id, subject, description, priority="medium", category=None, db=None):
    """Create support ticket"""
    ticket_id = f"TKT-{hash(f'{user_id}{subject}')}"

    return {
        "success": True,
        "ticket_id": ticket_id,
        "subject": subject,
        "priority": priority,
        "message": f"🎫 Ticket {ticket_id} created. We'll respond within 24 hours."
    }

async def search_knowledge_base_handler(user_id, query, db=None):
    """Search KB articles"""
    return {
        "articles": [
            {"title": "How to reset password", "url": "https://help.example.com/reset-password"},
            {"title": "Billing FAQ", "url": "https://help.example.com/billing-faq"}
        ],
        "count": 2
    }

async def check_ticket_status_handler(user_id, ticket_id, db=None):
    """Check ticket status"""
    return {
        "ticket_id": ticket_id,
        "status": "in_progress",
        "assigned_to": "Support Agent #5",
        "last_update": "2025-12-14 10:30",
        "message": "Your ticket is being reviewed by our team."
    }

support_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    system_prompt=(
        "You are SupportBot, a helpful customer support assistant. "
        "First try to help users by searching the knowledge base. "
        "If you can't resolve the issue, create a support ticket. "
        "Always be empathetic and professional."
    ),
    tools=support_tools,
    tool_handlers={
        "create_ticket": create_ticket_handler,
        "search_knowledge_base": search_knowledge_base_handler,
        "check_ticket_status": check_ticket_status_handler
    }
)
```

---

## 🏥 Example 4: Healthcare Appointment Agent

```python
"""
Healthcare Agent - Book appointments, manage prescriptions, view records
"""

from backend.agents.base_agent import BaseAgent
import os

healthcare_tools = [
    {
        "type": "function",
        "function": {
            "name": "book_doctor_appointment",
            "description": "Book appointment with a doctor",
            "parameters": {
                "type": "object",
                "properties": {
                    "specialty": {"type": "string", "description": "Doctor specialty (e.g., cardiologist)"},
                    "preferred_date": {"type": "string", "description": "Preferred date (YYYY-MM-DD)"},
                    "reason": {"type": "string", "description": "Reason for visit"}
                },
                "required": ["specialty", "preferred_date", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_prescription_refill",
            "description": "Request refill for existing prescription",
            "parameters": {
                "type": "object",
                "properties": {
                    "medication_name": {"type": "string", "description": "Medication name"},
                    "prescription_id": {"type": "string", "description": "Prescription ID"}
                },
                "required": ["medication_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_lab_results",
            "description": "View recent lab test results",
            "parameters": {
                "type": "object",
                "properties": {
                    "test_type": {"type": "string", "description": "Type of lab test (optional)"}
                },
                "required": []
            }
        }
    }
]

# Implement handlers...
async def book_doctor_appointment_handler(user_id, specialty, preferred_date, reason, db=None):
    return {
        "success": True,
        "appointment_id": "APT-HEALTH-123",
        "doctor": f"Dr. Smith ({specialty})",
        "date": preferred_date,
        "time": "10:00 AM",
        "message": f"🏥 Appointment booked with {specialty} on {preferred_date}"
    }

healthcare_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    system_prompt=(
        "You are HealthBot, a HIPAA-compliant healthcare assistant. "
        "Help patients book appointments, refill prescriptions, and view lab results. "
        "Always maintain patient privacy and be professional. "
        "Remind users to call emergency services for urgent medical issues."
    ),
    tools=healthcare_tools,
    tool_handlers={
        "book_doctor_appointment": book_doctor_appointment_handler,
        # ... other handlers
    }
)
```

---

## 🚀 Quick Migration Guide

### From Todo Agent to Your Domain:

```python
# 1. Copy base_agent.py to your project
cp backend/agents/base_agent.py your_project/agents/

# 2. Define YOUR tools (replace todo tools)
your_tools = [
    {
        "type": "function",
        "function": {
            "name": "your_function",
            "description": "What it does",
            "parameters": {...}
        }
    }
]

# 3. Implement YOUR handlers
async def your_function_handler(user_id, param1, param2, db=None):
    # Your business logic
    return {"success": True, "data": "..."}

# 4. Create YOUR agent
your_agent = BaseAgent(
    api_key=os.getenv("OPENAI_API_KEY"),
    system_prompt="You are [YOUR AGENT NAME], a helpful assistant for [YOUR DOMAIN]...",
    tools=your_tools,
    tool_handlers={"your_function": your_function_handler}
)

# 5. Use it!
result = await your_agent.process_message(
    user_message="User's request",
    user_id="user_id",
    conversation_history=[],
    db=db
)
```

**That's it! Your agent is ready for ANY domain!** 🎉

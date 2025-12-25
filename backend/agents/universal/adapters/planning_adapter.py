"""
Planning & Strategy Agent - Universal Reusable Agent

A comprehensive planning and strategic thinking agent that works across ALL projects:
- Book writing, Constitution drafting, Software development, Academic research, Business plans, etc.

**Capabilities:**
1. Project Planning & Roadmaps
2. Task Breakdown & Decomposition
3. Timeline Creation & Scheduling
4. Risk Assessment & Mitigation
5. Resource Allocation & Budgeting
6. Dependency Analysis
7. Milestone Tracking
8. Feasibility Analysis

**Use Cases:**
- Book Writing: Plan chapters, research phases, writing schedule, editing timeline
- Constitution: Plan drafting phases, stakeholder consultations, review cycles
- Software Development: Sprint planning, feature roadmaps, architecture planning, release schedules
- Academic Research: Research methodology, data collection plan, analysis phases, publication timeline
- Business: Strategic planning, product roadmaps, market entry strategy, resource allocation

**Example Usage:**
```python
from backend.agents.universal.adapters.planning_adapter import PlanningAgent
from backend.agents.reusable import ReusableAgent

planning_agent = ReusableAgent(adapter=PlanningAgent())

# Plan book writing project
result = await planning_agent.process_message(
    user_id="author_1",
    message="Create a detailed plan for writing a 300-page book on AI ethics over 6 months",
    conversation_history=[],
    db=None
)

# Software project roadmap
result = await planning_agent.process_message(
    user_id="dev_1",
    message="Create a product roadmap for our SaaS platform with Q1-Q4 milestones",
    conversation_history=[],
    db=None
)

# Task breakdown
result = await planning_agent.process_message(
    user_id="pm_1",
    message="Break down the 'user authentication' feature into detailed implementation tasks",
    conversation_history=[],
    db=None
)
```

Author: AI Agent System
Created: 2024
License: Same as parent project
"""

import logging
from typing import List, Dict, Any, Callable, Optional
from backend.agents.reusable.adapters.base_adapter import DomainAdapter

logger = logging.getLogger(__name__)


class PlanningAgent(DomainAdapter):
    """
    Universal Planning & Strategy Agent

    Provides comprehensive planning and strategic thinking capabilities across all domains.
    """

    def __init__(
        self,
        default_planning_horizon: str = "3_months",
        include_risk_assessment: bool = True,
        include_resource_planning: bool = True,
        granularity: str = "detailed"
    ):
        """
        Initialize Planning Agent with customizable settings.

        Args:
            default_planning_horizon: Default time horizon for plans (1_week, 1_month, 3_months, 6_months, 1_year)
            include_risk_assessment: Automatically include risk analysis in plans
            include_resource_planning: Automatically include resource allocation
            granularity: Level of detail (high_level, moderate, detailed)
        """
        self.default_planning_horizon = default_planning_horizon
        self.include_risk_assessment = include_risk_assessment
        self.include_resource_planning = include_resource_planning
        self.granularity = granularity

        logger.info(
            f"PlanningAgent initialized with horizon={default_planning_horizon}, "
            f"risk_assessment={include_risk_assessment}, resource_planning={include_resource_planning}, "
            f"granularity={granularity}"
        )

    def get_system_prompt(self) -> str:
        """
        System prompt defining the Planning Agent's role and capabilities.
        """
        return f"""You are a world-class strategic planner, project manager, and organizational expert with expertise in planning projects of any scale and domain.

**Your Role:**
You help users plan, organize, and strategize for ANY type of project:
- 📚 Book Writing (chapter planning, research phases, writing schedule, editing cycles)
- ⚖️ Constitution/Legal Documents (drafting phases, stakeholder reviews, approval cycles)
- 💻 Software Development (sprint planning, feature roadmaps, release schedules, architecture planning)
- 🎓 Academic Research (methodology design, data collection, analysis phases, publication timeline)
- 💼 Business Planning (strategic initiatives, product roadmaps, market entry, growth plans)
- 🎨 Creative Projects (production schedules, creative phases, review cycles)
- 🏗️ Construction/Engineering (project phases, resource allocation, critical path)

**Your Capabilities:**

1. **Project Planning:**
   - Create comprehensive project plans with clear objectives
   - Define project scope, deliverables, and success criteria
   - Identify project phases and major activities
   - Establish realistic timelines and deadlines
   - Define roles and responsibilities

2. **Task Breakdown:**
   - Decompose large goals into manageable tasks
   - Create hierarchical task structures (epics → stories → tasks)
   - Define clear, actionable task descriptions
   - Estimate effort and complexity for each task
   - Identify task prerequisites and dependencies

3. **Timeline & Scheduling:**
   - Create realistic project timelines
   - Define milestones and checkpoints
   - Schedule tasks and activities
   - Account for dependencies and constraints
   - Build in buffers for uncertainty

4. **Risk Management:**
   - Identify potential risks and obstacles
   - Assess risk probability and impact
   - Develop mitigation strategies
   - Create contingency plans
   - Monitor and track risks

5. **Resource Planning:**
   - Identify required resources (people, tools, budget, time)
   - Allocate resources efficiently
   - Optimize resource utilization
   - Plan for resource constraints
   - Track resource availability

6. **Dependency Analysis:**
   - Map task dependencies and relationships
   - Identify critical path
   - Detect bottlenecks and blockers
   - Optimize task sequencing
   - Manage parallel workstreams

7. **Strategic Roadmaps:**
   - Create long-term strategic plans
   - Define vision and strategic objectives
   - Plan phased implementations
   - Align initiatives with goals
   - Track strategic progress

8. **Feasibility Analysis:**
   - Assess project viability
   - Evaluate resource requirements
   - Identify constraints and limitations
   - Analyze cost-benefit tradeoffs
   - Provide go/no-go recommendations

**Your Planning Principles:**
- ✅ Clarity: Plans are clear, specific, and actionable
- ✅ Realism: Timelines and estimates are realistic and achievable
- ✅ Completeness: All aspects of the project are considered
- ✅ Flexibility: Plans account for uncertainty and change
- ✅ Measurability: Success criteria and metrics are defined
- ✅ Alignment: Plans align with overall goals and constraints
- ✅ Communication: Plans are easy to understand and communicate

**Your Planning Methodology:**
1. **Understand**: Clarify objectives, scope, and constraints
2. **Analyze**: Break down the project and identify key components
3. **Strategize**: Develop approach and high-level plan
4. **Detail**: Create detailed tasks, timelines, and resource plans
5. **Validate**: Check for risks, dependencies, and feasibility
6. **Document**: Present plan in clear, structured format
7. **Iterate**: Refine based on feedback and new information

**Current Configuration:**
- Planning Horizon: {self.default_planning_horizon}
- Risk Assessment: {'Enabled' if self.include_risk_assessment else 'Disabled'}
- Resource Planning: {'Enabled' if self.include_resource_planning else 'Disabled'}
- Granularity: {self.granularity}

**How You Work:**
1. Understand the project goals, scope, and constraints
2. Break down the project into logical phases and components
3. Create detailed task breakdowns with estimates
4. Develop realistic timelines with milestones
5. Identify and assess risks
6. Plan resource allocation
7. Map dependencies and critical paths
8. Present comprehensive, actionable plans

You are thorough, realistic, and focused on creating plans that actually work and can be executed successfully.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Define all planning tools available to the agent.
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "create_project_plan",
                    "description": "Create a comprehensive project plan with objectives, phases, deliverables, and timeline.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Name of the project"
                            },
                            "project_type": {
                                "type": "string",
                                "enum": ["book", "software", "research", "business", "legal", "creative", "engineering", "general"],
                                "description": "Type of project being planned"
                            },
                            "objectives": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Main objectives and goals of the project"
                            },
                            "duration": {
                                "type": "string",
                                "description": "Expected project duration (e.g., '3 months', '6 months', '1 year')"
                            },
                            "constraints": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Known constraints (budget, time, resources, technical)"
                            },
                            "team_size": {
                                "type": "integer",
                                "description": "Number of people working on the project"
                            }
                        },
                        "required": ["project_name", "project_type", "objectives"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "breakdown_tasks",
                    "description": "Break down a large goal or feature into detailed, actionable tasks with estimates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "goal_description": {
                                "type": "string",
                                "description": "Description of the goal or feature to break down"
                            },
                            "breakdown_depth": {
                                "type": "integer",
                                "description": "Number of hierarchical levels (1=high-level, 2=detailed, 3=very detailed)"
                            },
                            "include_estimates": {
                                "type": "boolean",
                                "description": "Whether to include time/effort estimates for each task"
                            },
                            "estimation_unit": {
                                "type": "string",
                                "enum": ["hours", "days", "weeks", "story_points"],
                                "description": "Unit for task estimation"
                            },
                            "context": {
                                "type": "string",
                                "description": "Additional context about the project or domain"
                            }
                        },
                        "required": ["goal_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_timeline",
                    "description": "Create a project timeline with phases, milestones, and deadlines.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Name of the project"
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Project start date (YYYY-MM-DD format)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "Target completion date (YYYY-MM-DD format), optional if duration provided"
                            },
                            "duration": {
                                "type": "string",
                                "description": "Project duration (e.g., '3 months'), optional if end_date provided"
                            },
                            "phases": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "duration": {"type": "string"}
                                    }
                                },
                                "description": "Major project phases"
                            },
                            "milestone_count": {
                                "type": "integer",
                                "description": "Desired number of milestones (default: auto-calculated)"
                            },
                            "include_buffer": {
                                "type": "boolean",
                                "description": "Whether to include time buffers for uncertainty (default: true)"
                            }
                        },
                        "required": ["project_name", "start_date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assess_risks",
                    "description": "Identify and assess project risks with mitigation strategies.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_description": {
                                "type": "string",
                                "description": "Description of the project or initiative"
                            },
                            "project_type": {
                                "type": "string",
                                "enum": ["book", "software", "research", "business", "legal", "creative", "engineering", "general"],
                                "description": "Type of project"
                            },
                            "risk_categories": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["technical", "resource", "schedule", "quality", "financial", "stakeholder", "external"]},
                                "description": "Specific risk categories to focus on"
                            },
                            "risk_tolerance": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Organization's risk tolerance level"
                            },
                            "include_mitigation": {
                                "type": "boolean",
                                "description": "Whether to include mitigation strategies (default: true)"
                            }
                        },
                        "required": ["project_description", "project_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "allocate_resources",
                    "description": "Plan resource allocation for project tasks and phases.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_name": {
                                "type": "string",
                                "description": "Name of the project"
                            },
                            "available_resources": {
                                "type": "object",
                                "properties": {
                                    "people": {"type": "array", "items": {"type": "object"}},
                                    "budget": {"type": "number"},
                                    "tools": {"type": "array", "items": {"type": "string"}},
                                    "time": {"type": "string"}
                                },
                                "description": "Resources available for the project"
                            },
                            "tasks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "required_skills": {"type": "array", "items": {"type": "string"}},
                                        "estimated_effort": {"type": "string"}
                                    }
                                },
                                "description": "Tasks requiring resource allocation"
                            },
                            "optimization_goal": {
                                "type": "string",
                                "enum": ["minimize_cost", "minimize_time", "maximize_quality", "balanced"],
                                "description": "Primary optimization objective"
                            }
                        },
                        "required": ["project_name", "tasks"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_dependencies",
                    "description": "Identify task dependencies and determine the critical path.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "tasks": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                        "name": {"type": "string"},
                                        "duration": {"type": "string"},
                                        "depends_on": {"type": "array", "items": {"type": "string"}}
                                    }
                                },
                                "description": "List of tasks with dependencies"
                            },
                            "identify_critical_path": {
                                "type": "boolean",
                                "description": "Whether to calculate the critical path (default: true)"
                            },
                            "suggest_optimizations": {
                                "type": "boolean",
                                "description": "Whether to suggest ways to optimize the schedule (default: true)"
                            }
                        },
                        "required": ["tasks"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_roadmap",
                    "description": "Create a strategic roadmap for long-term planning with phases and key initiatives.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "initiative_name": {
                                "type": "string",
                                "description": "Name of the initiative or strategic plan"
                            },
                            "vision": {
                                "type": "string",
                                "description": "Vision or ultimate goal"
                            },
                            "time_horizon": {
                                "type": "string",
                                "enum": ["3_months", "6_months", "1_year", "2_years", "3_years", "5_years"],
                                "description": "Time horizon for the roadmap"
                            },
                            "strategic_themes": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Major strategic themes or focus areas"
                            },
                            "key_initiatives": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "description": {"type": "string"},
                                        "priority": {"type": "string", "enum": ["high", "medium", "low"]}
                                    }
                                },
                                "description": "Key initiatives to include in roadmap"
                            },
                            "roadmap_format": {
                                "type": "string",
                                "enum": ["quarters", "months", "phases"],
                                "description": "How to organize the roadmap timeline"
                            }
                        },
                        "required": ["initiative_name", "vision", "time_horizon"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_feasibility",
                    "description": "Assess project feasibility and provide go/no-go recommendation.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_description": {
                                "type": "string",
                                "description": "Description of the proposed project"
                            },
                            "objectives": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Project objectives and goals"
                            },
                            "constraints": {
                                "type": "object",
                                "properties": {
                                    "budget": {"type": "number"},
                                    "timeline": {"type": "string"},
                                    "team_size": {"type": "integer"},
                                    "technical": {"type": "array", "items": {"type": "string"}},
                                    "other": {"type": "array", "items": {"type": "string"}}
                                },
                                "description": "Project constraints and limitations"
                            },
                            "evaluation_criteria": {
                                "type": "array",
                                "items": {"type": "string", "enum": ["technical", "financial", "resource", "timeline", "risk", "strategic_fit", "market"]},
                                "description": "Criteria to evaluate feasibility against"
                            },
                            "provide_alternatives": {
                                "type": "boolean",
                                "description": "Whether to suggest alternative approaches if not feasible (default: true)"
                            }
                        },
                        "required": ["project_description", "objectives"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """
        Map tool names to their handler functions.
        """
        return {
            "create_project_plan": self._create_project_plan_handler,
            "breakdown_tasks": self._breakdown_tasks_handler,
            "create_timeline": self._create_timeline_handler,
            "assess_risks": self._assess_risks_handler,
            "allocate_resources": self._allocate_resources_handler,
            "analyze_dependencies": self._analyze_dependencies_handler,
            "create_roadmap": self._create_roadmap_handler,
            "evaluate_feasibility": self._evaluate_feasibility_handler
        }

    # ============================================================================
    # Tool Handler Implementations
    # ============================================================================

    async def _create_project_plan_handler(
        self,
        user_id: str,
        project_name: str,
        project_type: str,
        objectives: List[str],
        duration: Optional[str] = None,
        constraints: Optional[List[str]] = None,
        team_size: Optional[int] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Create comprehensive project plan.

        The LLM generates the detailed plan through the conversation.
        """
        logger.info(
            f"Creating project plan: name='{project_name}', type={project_type}, "
            f"objectives={len(objectives)}, duration={duration}, team_size={team_size}"
        )

        return {
            "success": True,
            "project_name": project_name,
            "project_type": project_type,
            "objectives_count": len(objectives),
            "duration": duration or "Not specified",
            "constraints": constraints or [],
            "team_size": team_size,
            "risk_assessment_included": self.include_risk_assessment,
            "resource_planning_included": self.include_resource_planning,
            "message": f"Project plan created for '{project_name}' ({project_type})",
            "note": "Detailed project plan provided in conversation response"
        }

    async def _breakdown_tasks_handler(
        self,
        user_id: str,
        goal_description: str,
        breakdown_depth: int = 2,
        include_estimates: bool = True,
        estimation_unit: str = "days",
        context: Optional[str] = None,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Break down goals into detailed tasks.

        The LLM performs the breakdown through the conversation.
        """
        logger.info(
            f"Breaking down tasks: goal='{goal_description[:50]}...', "
            f"depth={breakdown_depth}, estimates={include_estimates}, unit={estimation_unit}"
        )

        return {
            "success": True,
            "goal": goal_description,
            "breakdown_depth": breakdown_depth,
            "include_estimates": include_estimates,
            "estimation_unit": estimation_unit,
            "context": context,
            "granularity": self.granularity,
            "message": f"Task breakdown completed with {breakdown_depth} levels of depth",
            "note": "Detailed task breakdown provided in conversation response"
        }

    async def _create_timeline_handler(
        self,
        user_id: str,
        project_name: str,
        start_date: str,
        end_date: Optional[str] = None,
        duration: Optional[str] = None,
        phases: Optional[List[Dict[str, Any]]] = None,
        milestone_count: Optional[int] = None,
        include_buffer: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Create project timeline with milestones.

        The LLM generates the timeline through the conversation.
        """
        logger.info(
            f"Creating timeline: project='{project_name}', start={start_date}, "
            f"end={end_date}, duration={duration}, phases={len(phases) if phases else 0}, "
            f"milestones={milestone_count}, buffer={include_buffer}"
        )

        return {
            "success": True,
            "project_name": project_name,
            "start_date": start_date,
            "end_date": end_date,
            "duration": duration or "Calculated from end_date",
            "phases_count": len(phases) if phases else 0,
            "milestone_count": milestone_count or "Auto-calculated",
            "include_buffer": include_buffer,
            "message": f"Timeline created for '{project_name}' starting {start_date}",
            "note": "Detailed timeline with milestones provided in conversation response"
        }

    async def _assess_risks_handler(
        self,
        user_id: str,
        project_description: str,
        project_type: str,
        risk_categories: Optional[List[str]] = None,
        risk_tolerance: str = "medium",
        include_mitigation: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Identify and assess project risks.

        The LLM performs risk analysis through the conversation.
        """
        logger.info(
            f"Assessing risks: type={project_type}, categories={risk_categories}, "
            f"tolerance={risk_tolerance}, mitigation={include_mitigation}"
        )

        return {
            "success": True,
            "project_type": project_type,
            "risk_categories": risk_categories or ["all categories"],
            "risk_tolerance": risk_tolerance,
            "include_mitigation": include_mitigation,
            "message": f"Risk assessment completed for {project_type} project",
            "note": "Detailed risk analysis with mitigation strategies provided in conversation response"
        }

    async def _allocate_resources_handler(
        self,
        user_id: str,
        project_name: str,
        tasks: List[Dict[str, Any]],
        available_resources: Optional[Dict[str, Any]] = None,
        optimization_goal: str = "balanced",
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Plan resource allocation for tasks.

        The LLM performs resource planning through the conversation.
        """
        logger.info(
            f"Allocating resources: project='{project_name}', tasks={len(tasks)}, "
            f"optimization={optimization_goal}"
        )

        return {
            "success": True,
            "project_name": project_name,
            "task_count": len(tasks),
            "available_resources": available_resources or "Not specified",
            "optimization_goal": optimization_goal,
            "message": f"Resource allocation plan created for {len(tasks)} tasks",
            "note": "Detailed resource allocation provided in conversation response"
        }

    async def _analyze_dependencies_handler(
        self,
        user_id: str,
        tasks: List[Dict[str, Any]],
        identify_critical_path: bool = True,
        suggest_optimizations: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Analyze task dependencies and critical path.

        The LLM performs dependency analysis through the conversation.
        """
        logger.info(
            f"Analyzing dependencies: tasks={len(tasks)}, "
            f"critical_path={identify_critical_path}, optimize={suggest_optimizations}"
        )

        return {
            "success": True,
            "task_count": len(tasks),
            "identify_critical_path": identify_critical_path,
            "suggest_optimizations": suggest_optimizations,
            "message": f"Dependency analysis completed for {len(tasks)} tasks",
            "note": "Dependency graph and critical path analysis provided in conversation response"
        }

    async def _create_roadmap_handler(
        self,
        user_id: str,
        initiative_name: str,
        vision: str,
        time_horizon: str,
        strategic_themes: Optional[List[str]] = None,
        key_initiatives: Optional[List[Dict[str, Any]]] = None,
        roadmap_format: str = "quarters",
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Create strategic roadmap.

        The LLM generates the roadmap through the conversation.
        """
        logger.info(
            f"Creating roadmap: initiative='{initiative_name}', horizon={time_horizon}, "
            f"themes={len(strategic_themes) if strategic_themes else 0}, "
            f"initiatives={len(key_initiatives) if key_initiatives else 0}, format={roadmap_format}"
        )

        return {
            "success": True,
            "initiative_name": initiative_name,
            "vision": vision,
            "time_horizon": time_horizon,
            "strategic_themes": strategic_themes or [],
            "key_initiatives_count": len(key_initiatives) if key_initiatives else 0,
            "roadmap_format": roadmap_format,
            "message": f"Strategic roadmap created for '{initiative_name}' with {time_horizon} horizon",
            "note": "Detailed roadmap provided in conversation response"
        }

    async def _evaluate_feasibility_handler(
        self,
        user_id: str,
        project_description: str,
        objectives: List[str],
        constraints: Optional[Dict[str, Any]] = None,
        evaluation_criteria: Optional[List[str]] = None,
        provide_alternatives: bool = True,
        db: Any = None
    ) -> Dict[str, Any]:
        """
        Assess project feasibility.

        The LLM performs feasibility analysis through the conversation.
        """
        logger.info(
            f"Evaluating feasibility: objectives={len(objectives)}, "
            f"constraints={bool(constraints)}, criteria={evaluation_criteria}, "
            f"alternatives={provide_alternatives}"
        )

        return {
            "success": True,
            "objectives_count": len(objectives),
            "constraints": constraints or {},
            "evaluation_criteria": evaluation_criteria or ["all criteria"],
            "provide_alternatives": provide_alternatives,
            "message": "Feasibility analysis completed",
            "note": "Detailed feasibility assessment with recommendations provided in conversation response"
        }

    # ============================================================================
    # Customization Methods
    # ============================================================================

    def get_greeting_message(self) -> str:
        """Custom greeting for Planning Agent."""
        return (
            "👋 Hello! I'm your Planning & Strategy Agent.\n\n"
            "I can help you:\n"
            "• 📋 Create comprehensive project plans\n"
            "• 🔨 Break down goals into actionable tasks\n"
            "• 📅 Develop realistic timelines and schedules\n"
            "• ⚠️ Identify and mitigate project risks\n"
            "• 👥 Plan resource allocation\n"
            "• 🗺️ Create strategic roadmaps\n"
            "• ✅ Assess project feasibility\n\n"
            "What would you like to plan today?"
        )

    def get_recommended_model(self) -> str:
        """
        Recommend the best model for planning tasks.

        Planning requires strategic thinking and analysis.
        """
        return "gpt-4-turbo-preview"  # Best for strategic thinking

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate Planning Agent configuration.
        """
        issues = []

        valid_horizons = ["1_week", "1_month", "3_months", "6_months", "1_year", "2_years", "3_years", "5_years"]
        if self.default_planning_horizon not in valid_horizons:
            issues.append(f"Invalid planning horizon: {self.default_planning_horizon}")

        valid_granularities = ["high_level", "moderate", "detailed"]
        if self.granularity not in valid_granularities:
            issues.append(f"Invalid granularity: {self.granularity}")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "configuration": {
                "planning_horizon": self.default_planning_horizon,
                "risk_assessment": self.include_risk_assessment,
                "resource_planning": self.include_resource_planning,
                "granularity": self.granularity
            }
        }


# ============================================================================
# Convenience Export
# ============================================================================

__all__ = ["PlanningAgent"]

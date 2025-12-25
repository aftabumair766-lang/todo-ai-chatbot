"""
Universal Agent System - Integration & Workflow Examples

This file demonstrates how to use the 10 universal agents together in real-world workflows.

**Available Agents:**
CORE (5): Writing, Research, Planning, QA, Template
TESTING (5): Software, Content, Legal, Academic, Business

**Example Workflows:**
1. Book Writing Workflow
2. Constitution Drafting Workflow
3. Software Development Workflow
4. Academic Research Workflow
5. Business Planning Workflow
"""

from backend.agents.reusable import ReusableAgent

# Core Agents
from backend.agents.universal.adapters.writing_adapter import WritingAgent
from backend.agents.universal.adapters.research_adapter import ResearchAgent
from backend.agents.universal.adapters.planning_adapter import PlanningAgent
from backend.agents.universal.adapters.qa_adapter import QAAgent
from backend.agents.universal.adapters.template_adapter import TemplateAgent

# Testing Agents
from backend.agents.universal.testing.software_testing_adapter import SoftwareTestingAgent
from backend.agents.universal.testing.content_testing_adapter import ContentTestingAgent
from backend.agents.universal.testing.legal_testing_adapter import LegalTestingAgent
from backend.agents.universal.testing.academic_testing_adapter import AcademicTestingAgent
from backend.agents.universal.testing.business_testing_adapter import BusinessTestingAgent


# ==============================================================================
# WORKFLOW 1: Book Writing (Research → Plan → Write → Review → Format → Test)
# ==============================================================================

async def book_writing_workflow():
    """
    Complete book writing workflow using 5 agents.

    Agents used: Research, Planning, Writing, QA, Template, Content Testing
    """

    # Initialize agents
    research_agent = ReusableAgent(adapter=ResearchAgent())
    planning_agent = ReusableAgent(adapter=PlanningAgent())
    writing_agent = ReusableAgent(adapter=WritingAgent())
    qa_agent = ReusableAgent(adapter=QAAgent())
    template_agent = ReusableAgent(adapter=TemplateAgent())
    content_tester = ReusableAgent(adapter=ContentTestingAgent())

    user_id = "author_1"
    conversation_history = []

    # Step 1: Research the topic
    print("📚 Step 1: Researching AI Ethics...")
    research_result = await research_agent.process_message(
        user_id=user_id,
        message="Research the history and key debates in AI ethics from 2010-2024",
        conversation_history=conversation_history,
        db=None
    )

    # Step 2: Create book plan
    print("\n📋 Step 2: Creating book outline and timeline...")
    planning_result = await planning_agent.process_message(
        user_id=user_id,
        message="Create a detailed plan for writing a 300-page book on AI Ethics over 6 months, with 12 chapters",
        conversation_history=conversation_history,
        db=None
    )

    # Step 3: Write chapter
    print("\n✍️ Step 3: Writing Chapter 1...")
    writing_result = await writing_agent.process_message(
        user_id=user_id,
        message="Write Chapter 1: Introduction to AI Ethics (3000 words) covering the definition, importance, and key stakeholders",
        conversation_history=conversation_history,
        db=None
    )

    # Step 4: Quality review
    print("\n🔍 Step 4: Reviewing chapter quality...")
    qa_result = await qa_agent.process_message(
        user_id=user_id,
        message="Review this chapter for grammar, clarity, consistency, and readability",
        conversation_history=conversation_history,
        db=None
    )

    # Step 5: Apply template and format
    print("\n📄 Step 5: Applying book template...")
    template_result = await template_agent.process_message(
        user_id=user_id,
        message="Apply professional book chapter template with proper formatting",
        conversation_history=conversation_history,
        db=None
    )

    # Step 6: Test content quality
    print("\n✅ Step 6: Testing content for publication...")
    test_result = await content_tester.process_message(
        user_id=user_id,
        message="Test this chapter for readability (target: general audience), engagement, and structure",
        conversation_history=conversation_history,
        db=None
    )

    print("\n✨ Book writing workflow complete!")
    print("Agents used: Research → Planning → Writing → QA → Template → Content Testing")


# ==============================================================================
# WORKFLOW 2: Constitution Drafting (Research → Plan → Write → Review → Test)
# ==============================================================================

async def constitution_drafting_workflow():
    """
    Complete constitution drafting workflow using 6 agents.

    Agents used: Research, Planning, Writing, QA, Template, Legal Testing
    """

    # Initialize agents
    research_agent = ReusableAgent(adapter=ResearchAgent())
    planning_agent = ReusableAgent(adapter=PlanningAgent())
    writing_agent = ReusableAgent(adapter=WritingAgent())
    qa_agent = ReusableAgent(adapter=QAAgent())
    template_agent = ReusableAgent(adapter=TemplateAgent())
    legal_tester = ReusableAgent(adapter=LegalTestingAgent())

    user_id = "lawyer_1"

    # Step 1: Research constitutional frameworks
    print("⚖️ Step 1: Researching constitutional frameworks...")
    await research_agent.process_message(
        user_id=user_id,
        message="Research modern constitutional frameworks from US, Canada, Germany, and South Africa",
        conversation_history=[],
        db=None
    )

    # Step 2: Plan constitution structure
    print("\n📋 Step 2: Planning constitution structure...")
    await planning_agent.process_message(
        user_id=user_id,
        message="Create a detailed plan for drafting a constitution with 10 articles covering fundamental rights, government structure, and amendments",
        conversation_history=[],
        db=None
    )

    # Step 3: Write preamble and Article 1
    print("\n✍️ Step 3: Drafting preamble and Article 1 (Fundamental Rights)...")
    await writing_agent.process_message(
        user_id=user_id,
        message="Write the preamble and Article 1 on Fundamental Rights in formal legal language",
        conversation_history=[],
        db=None
    )

    # Step 4: Review for consistency
    print("\n🔍 Step 4: Reviewing for legal language precision...")
    await qa_agent.process_message(
        user_id=user_id,
        message="Review for legal language precision, consistency, and completeness",
        conversation_history=[],
        db=None
    )

    # Step 5: Apply legal document template
    print("\n📄 Step 5: Applying legal document template...")
    await template_agent.process_message(
        user_id=user_id,
        message="Apply legal document template with proper article numbering and formatting",
        conversation_history=[],
        db=None
    )

    # Step 6: Legal testing
    print("\n✅ Step 6: Testing for legal compliance...")
    await legal_tester.process_message(
        user_id=user_id,
        message="Test this constitution for legal validity, completeness, and enforceability",
        conversation_history=[],
        db=None
    )

    print("\n✨ Constitution drafting workflow complete!")


# ==============================================================================
# WORKFLOW 3: Software Development (Plan → Write → Review → Test → Document)
# ==============================================================================

async def software_development_workflow():
    """
    Complete software development workflow using 5 agents.

    Agents used: Planning, Writing (code), QA (code review), Software Testing, Template (docs)
    """

    # Initialize agents
    planning_agent = ReusableAgent(adapter=PlanningAgent())
    writing_agent = ReusableAgent(adapter=WritingAgent())
    qa_agent = ReusableAgent(adapter=QAAgent())
    software_tester = ReusableAgent(adapter=SoftwareTestingAgent())
    template_agent = ReusableAgent(adapter=TemplateAgent())

    user_id = "dev_1"

    # Step 1: Plan the feature
    print("💻 Step 1: Planning authentication feature...")
    await planning_agent.process_message(
        user_id=user_id,
        message="Create a detailed plan for implementing user authentication with JWT tokens, including task breakdown",
        conversation_history=[],
        db=None
    )

    # Step 2: Write code (using Writing agent for structure)
    print("\n✍️ Step 2: Writing authentication code...")
    await writing_agent.process_message(
        user_id=user_id,
        message="Write the authentication module with login, logout, token refresh functions",
        conversation_history=[],
        db=None
    )

    # Step 3: Code review (QA)
    print("\n🔍 Step 3: Reviewing code quality...")
    await qa_agent.process_message(
        user_id=user_id,
        message="Review this code for clarity, consistency, and completeness",
        conversation_history=[],
        db=None
    )

    # Step 4: Software testing
    print("\n✅ Step 4: Testing code quality, security, and performance...")
    await software_tester.process_message(
        user_id=user_id,
        message="Test this authentication code for security vulnerabilities, code quality, and best practices",
        conversation_history=[],
        db=None
    )

    # Step 5: Generate documentation
    print("\n📄 Step 5: Generating API documentation...")
    await template_agent.process_message(
        user_id=user_id,
        message="Generate API documentation for this authentication module",
        conversation_history=[],
        db=None
    )

    print("\n✨ Software development workflow complete!")


# ==============================================================================
# WORKFLOW 4: Academic Research (Research → Plan → Write → Review → Test)
# ==============================================================================

async def academic_research_workflow():
    """
    Complete academic research workflow using 6 agents.

    Agents used: Research, Planning, Writing, QA, Template, Academic Testing
    """

    # Initialize agents
    research_agent = ReusableAgent(adapter=ResearchAgent())
    planning_agent = ReusableAgent(adapter=PlanningAgent())
    writing_agent = ReusableAgent(adapter=WritingAgent())
    qa_agent = ReusableAgent(adapter=QAAgent())
    template_agent = ReusableAgent(adapter=TemplateAgent())
    academic_tester = ReusableAgent(adapter=AcademicTestingAgent())

    user_id = "researcher_1"

    # Step 1: Literature review
    print("🔬 Step 1: Conducting literature review...")
    await research_agent.process_message(
        user_id=user_id,
        message="Research machine learning applications in healthcare from 2020-2024, focusing on peer-reviewed journals",
        conversation_history=[],
        db=None
    )

    # Step 2: Plan research methodology
    print("\n📋 Step 2: Planning research methodology...")
    await planning_agent.process_message(
        user_id=user_id,
        message="Create a detailed research methodology plan for a systematic review of ML in healthcare",
        conversation_history=[],
        db=None
    )

    # Step 3: Write paper
    print("\n✍️ Step 3: Writing methodology section...")
    await writing_agent.process_message(
        user_id=user_id,
        message="Write the Methodology section for this systematic review in academic style",
        conversation_history=[],
        db=None
    )

    # Step 4: Review academic writing
    print("\n🔍 Step 4: Reviewing academic writing quality...")
    await qa_agent.process_message(
        user_id=user_id,
        message="Review for academic tone, clarity, and citation consistency (APA style)",
        conversation_history=[],
        db=None
    )

    # Step 5: Apply academic template
    print("\n📄 Step 5: Applying academic paper template...")
    await template_agent.process_message(
        user_id=user_id,
        message="Apply academic paper template with proper section formatting",
        conversation_history=[],
        db=None
    )

    # Step 6: Academic peer review
    print("\n✅ Step 6: Peer review for publication readiness...")
    await academic_tester.process_message(
        user_id=user_id,
        message="Test this paper for methodology rigor, citation quality, and journal publication readiness",
        conversation_history=[],
        db=None
    )

    print("\n✨ Academic research workflow complete!")


# ==============================================================================
# WORKFLOW 5: Business Planning (Research → Plan → Write → Review → Test)
# ==============================================================================

async def business_planning_workflow():
    """
    Complete business planning workflow using 6 agents.

    Agents used: Research, Planning, Writing, QA, Template, Business Testing
    """

    # Initialize agents
    research_agent = ReusableAgent(adapter=ResearchAgent())
    planning_agent = ReusableAgent(adapter=PlanningAgent())
    writing_agent = ReusableAgent(adapter=WritingAgent())
    qa_agent = ReusableAgent(adapter=QAAgent())
    template_agent = ReusableAgent(adapter=TemplateAgent())
    business_tester = ReusableAgent(adapter=BusinessTestingAgent())

    user_id = "entrepreneur_1"

    # Step 1: Market research
    print("💼 Step 1: Conducting market research...")
    await research_agent.process_message(
        user_id=user_id,
        message="Research the SaaS market for project management tools, including market size, trends, and key competitors",
        conversation_history=[],
        db=None
    )

    # Step 2: Business planning
    print("\n📋 Step 2: Creating business plan structure...")
    await planning_agent.process_message(
        user_id=user_id,
        message="Create a detailed business plan outline with financial projections for a project management SaaS startup",
        conversation_history=[],
        db=None
    )

    # Step 3: Write business plan
    print("\n✍️ Step 3: Writing executive summary and market analysis...")
    await writing_agent.process_message(
        user_id=user_id,
        message="Write the Executive Summary and Market Analysis sections of the business plan",
        conversation_history=[],
        db=None
    )

    # Step 4: Review quality
    print("\n🔍 Step 4: Reviewing business plan quality...")
    await qa_agent.process_message(
        user_id=user_id,
        message="Review for clarity, professionalism, and consistency",
        conversation_history=[],
        db=None
    )

    # Step 5: Apply business template
    print("\n📄 Step 5: Applying business plan template...")
    await template_agent.process_message(
        user_id=user_id,
        message="Apply professional business plan template with proper formatting",
        conversation_history=[],
        db=None
    )

    # Step 6: Business validation
    print("\n✅ Step 6: Testing for investor readiness...")
    await business_tester.process_message(
        user_id=user_id,
        message="Test this business plan for financial realism, market analysis depth, and investor readiness",
        conversation_history=[],
        db=None
    )

    print("\n✨ Business planning workflow complete!")


# ==============================================================================
# MAIN - Run Example Workflows
# ==============================================================================

async def main():
    """Run all example workflows."""

    print("="*80)
    print("UNIVERSAL AGENT SYSTEM - INTEGRATION EXAMPLES")
    print("="*80)
    print("\n10 Agents Available:")
    print("  CORE (5): Writing, Research, Planning, QA, Template")
    print("  TESTING (5): Software, Content, Legal, Academic, Business")
    print("\n" + "="*80 + "\n")

    # Uncomment the workflow you want to run:

    # await book_writing_workflow()
    # await constitution_drafting_workflow()
    # await software_development_workflow()
    # await academic_research_workflow()
    await business_planning_workflow()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

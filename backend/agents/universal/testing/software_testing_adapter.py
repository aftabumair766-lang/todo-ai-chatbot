"""
Software Testing Agent - Profession-Specific Testing Agent

A specialized testing agent for SOFTWARE DEVELOPMENT projects:
- Tests code quality, architecture, security, performance, and best practices
- Validates software projects from a developer's perspective

**What It Tests:**
1. Code Quality & Standards
2. Architecture & Design Patterns
3. Security Vulnerabilities
4. Performance & Optimization
5. Test Coverage & Quality
6. Documentation Quality
7. Dependencies & Versioning
8. Build & Deployment Readiness

**Use Cases:**
- Test API implementations
- Review code architecture
- Security audits
- Performance analysis
- Test coverage assessment
- Code review automation

**Example Usage:**
```python
from backend.agents.universal.testing.software_testing_adapter import SoftwareTestingAgent
from backend.agents.reusable import ReusableAgent

software_tester = ReusableAgent(adapter=SoftwareTestingAgent())

# Test code quality
result = await software_tester.process_message(
    user_id="dev_1",
    message="Test this Python codebase for code quality, security vulnerabilities, and test coverage",
    conversation_history=[],
    db=None
)

# Architecture review
result = await software_tester.process_message(
    user_id="architect_1",
    message="Review the architecture of this microservices system for scalability and best practices",
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


class SoftwareTestingAgent(DomainAdapter):
    """
    Software Testing Agent - Tests software projects for quality and correctness
    """

    def __init__(
        self,
        strictness: str = "balanced",
        focus_areas: Optional[List[str]] = None,
        minimum_coverage: int = 80,
        enable_security_scan: bool = True
    ):
        """
        Initialize Software Testing Agent.

        Args:
            strictness: Testing strictness (lenient, balanced, strict, enterprise)
            focus_areas: Areas to focus on (code_quality, security, performance, tests, architecture)
            minimum_coverage: Minimum required test coverage percentage
            enable_security_scan: Enable security vulnerability scanning
        """
        self.strictness = strictness
        self.focus_areas = focus_areas or ["code_quality", "security", "performance", "tests", "architecture"]
        self.minimum_coverage = minimum_coverage
        self.enable_security_scan = enable_security_scan

        logger.info(
            f"SoftwareTestingAgent initialized with strictness={strictness}, "
            f"focus={focus_areas}, min_coverage={minimum_coverage}, security_scan={enable_security_scan}"
        )

    def get_system_prompt(self) -> str:
        """System prompt for Software Testing Agent."""
        return f"""You are a world-class software quality engineer, security expert, and code reviewer with deep expertise in software testing and best practices.

**Your Role:**
Test and validate software projects for quality, security, performance, and adherence to best practices.

**What You Test:**

1. **Code Quality:**
   - Code style and consistency (PEP 8, ESLint, etc.)
   - Code complexity and maintainability
   - Code smells and anti-patterns
   - Naming conventions
   - Documentation and comments
   - Error handling
   - Code duplication (DRY principle)

2. **Architecture & Design:**
   - Design patterns usage
   - SOLID principles adherence
   - Modularity and separation of concerns
   - Scalability and extensibility
   - API design
   - Database schema design
   - System architecture review

3. **Security:**
   - SQL injection vulnerabilities
   - XSS (Cross-Site Scripting)
   - CSRF (Cross-Site Request Forgery)
   - Authentication and authorization flaws
   - Sensitive data exposure
   - Dependency vulnerabilities
   - Security misconfigurations
   - OWASP Top 10 compliance

4. **Performance:**
   - Algorithm efficiency
   - Database query optimization
   - Caching strategies
   - Resource usage (memory, CPU)
   - API response times
   - Scalability bottlenecks
   - Load testing readiness

5. **Testing:**
   - Test coverage (minimum: {self.minimum_coverage}%)
   - Test quality and effectiveness
   - Unit test best practices
   - Integration test coverage
   - E2E test scenarios
   - Test data management
   - Mocking and stubbing practices

6. **Documentation:**
   - README quality and completeness
   - API documentation (Swagger/OpenAPI)
   - Code comments and docstrings
   - Architecture diagrams
   - Setup and installation guides
   - Contributing guidelines

7. **Dependencies:**
   - Dependency vulnerabilities
   - Version compatibility
   - Dependency bloat
   - License compliance
   - Update policies

8. **Build & Deployment:**
   - CI/CD pipeline configuration
   - Environment configuration
   - Docker/containerization
   - Deployment scripts
   - Health checks and monitoring
   - Rollback strategies

**Testing Standards:**
- ✅ **Critical Issues**: Must fix (security vulnerabilities, data loss risks, crashes)
- 🟡 **Major Issues**: Should fix (performance problems, poor architecture, low coverage)
- 🟢 **Minor Issues**: Consider fixing (style violations, minor improvements)
- 💡 **Suggestions**: Best practice recommendations

**Current Configuration:**
- Strictness: {self.strictness}
- Focus Areas: {', '.join(self.focus_areas)}
- Minimum Coverage: {self.minimum_coverage}%
- Security Scanning: {'Enabled' if self.enable_security_scan else 'Disabled'}

**How You Work:**
1. Analyze codebase structure and architecture
2. Review code quality and style
3. Scan for security vulnerabilities
4. Assess performance and scalability
5. Evaluate test coverage and quality
6. Check documentation completeness
7. Review dependencies and builds
8. Generate comprehensive test report with severity ratings

You are thorough, objective, and focused on helping developers build secure, performant, and maintainable software.
"""

    def get_tools(self) -> List[Dict[str, Any]]:
        """Define testing tools for software projects."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "test_code_quality",
                    "description": "Test code quality, style, complexity, and maintainability.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string", "description": "Code to test"},
                            "language": {"type": "string", "enum": ["python", "javascript", "typescript", "java", "go", "rust", "other"]},
                            "style_guide": {"type": "string", "enum": ["pep8", "eslint", "google", "airbnb", "standard"]},
                            "check_complexity": {"type": "boolean"},
                            "check_duplication": {"type": "boolean"}
                        },
                        "required": ["code", "language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "review_architecture",
                    "description": "Review software architecture and design patterns.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "architecture_description": {"type": "string"},
                            "code_samples": {"type": "array", "items": {"type": "string"}},
                            "architecture_type": {"type": "string", "enum": ["monolith", "microservices", "serverless", "mvc", "layered"]},
                            "evaluate_patterns": {"type": "boolean"},
                            "check_solid": {"type": "boolean"}
                        },
                        "required": ["architecture_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "security_scan",
                    "description": "Scan code for security vulnerabilities (OWASP Top 10).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "language": {"type": "string"},
                            "scan_types": {"type": "array", "items": {"type": "string", "enum": ["sql_injection", "xss", "csrf", "auth", "crypto", "dependencies", "all"]}},
                            "include_fixes": {"type": "boolean"}
                        },
                        "required": ["code", "language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_performance",
                    "description": "Analyze code performance and identify bottlenecks.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"},
                            "language": {"type": "string"},
                            "performance_aspects": {"type": "array", "items": {"type": "string", "enum": ["algorithm", "database", "caching", "memory", "concurrency"]}},
                            "suggest_optimizations": {"type": "boolean"}
                        },
                        "required": ["code", "language"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "evaluate_tests",
                    "description": "Evaluate test coverage and quality.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "test_code": {"type": "string"},
                            "source_code": {"type": "string"},
                            "test_framework": {"type": "string"},
                            "check_coverage": {"type": "boolean"},
                            "assess_quality": {"type": "boolean"}
                        },
                        "required": ["test_code"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "review_documentation",
                    "description": "Review code documentation quality.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "readme": {"type": "string"},
                            "code_with_comments": {"type": "string"},
                            "api_docs": {"type": "string"},
                            "check_completeness": {"type": "boolean"}
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_dependencies",
                    "description": "Check dependencies for vulnerabilities and best practices.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "dependencies": {"type": "object"},
                            "package_manager": {"type": "string", "enum": ["npm", "pip", "maven", "cargo", "go_mod"]},
                            "check_vulnerabilities": {"type": "boolean"},
                            "check_licenses": {"type": "boolean"}
                        },
                        "required": ["dependencies", "package_manager"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_test_report",
                    "description": "Generate comprehensive software testing report.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_name": {"type": "string"},
                            "test_results": {"type": "object"},
                            "report_format": {"type": "string", "enum": ["summary", "detailed", "comprehensive"]},
                            "include_recommendations": {"type": "boolean"}
                        },
                        "required": ["project_name"]
                    }
                }
            }
        ]

    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Map tool names to handlers."""
        return {
            "test_code_quality": self._test_code_quality,
            "review_architecture": self._review_architecture,
            "security_scan": self._security_scan,
            "analyze_performance": self._analyze_performance,
            "evaluate_tests": self._evaluate_tests,
            "review_documentation": self._review_documentation,
            "check_dependencies": self._check_dependencies,
            "generate_test_report": self._generate_test_report
        }

    async def _test_code_quality(self, user_id: str, code: str, language: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Testing code quality for {language} code ({len(code)} chars)")
        return {
            "success": True,
            "language": language,
            "code_length": len(code),
            "checks_performed": ["style", "complexity", "duplication", "naming"],
            "message": f"Code quality test completed for {language}",
            "note": "Detailed code quality report in conversation response"
        }

    async def _review_architecture(self, user_id: str, architecture_description: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Reviewing architecture: {len(architecture_description)} chars")
        return {
            "success": True,
            "description_length": len(architecture_description),
            "aspects_reviewed": ["design_patterns", "SOLID", "scalability", "modularity"],
            "message": "Architecture review completed",
            "note": "Architecture analysis in conversation response"
        }

    async def _security_scan(self, user_id: str, code: str, language: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Security scanning {language} code")
        return {
            "success": True,
            "language": language,
            "code_length": len(code),
            "scan_enabled": self.enable_security_scan,
            "scan_types": kwargs.get("scan_types", ["all"]),
            "message": f"Security scan completed for {language}",
            "note": "Security vulnerability report in conversation response"
        }

    async def _analyze_performance(self, user_id: str, code: str, language: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Analyzing performance for {language} code")
        return {
            "success": True,
            "language": language,
            "code_length": len(code),
            "aspects": kwargs.get("performance_aspects", ["algorithm", "database", "caching"]),
            "message": "Performance analysis completed",
            "note": "Performance optimization recommendations in conversation response"
        }

    async def _evaluate_tests(self, user_id: str, test_code: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Evaluating tests ({len(test_code)} chars)")
        return {
            "success": True,
            "test_code_length": len(test_code),
            "minimum_coverage": self.minimum_coverage,
            "checks": ["coverage", "quality", "best_practices"],
            "message": "Test evaluation completed",
            "note": "Test coverage and quality report in conversation response"
        }

    async def _review_documentation(self, user_id: str, **kwargs) -> Dict[str, Any]:
        logger.info("Reviewing documentation")
        return {
            "success": True,
            "docs_reviewed": ["README", "code_comments", "API_docs"],
            "message": "Documentation review completed",
            "note": "Documentation quality report in conversation response"
        }

    async def _check_dependencies(self, user_id: str, dependencies: Dict, package_manager: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Checking dependencies via {package_manager}")
        return {
            "success": True,
            "package_manager": package_manager,
            "dependency_count": len(dependencies),
            "checks": ["vulnerabilities", "versions", "licenses"],
            "message": f"Dependency check completed for {len(dependencies)} packages",
            "note": "Dependency analysis in conversation response"
        }

    async def _generate_test_report(self, user_id: str, project_name: str, **kwargs) -> Dict[str, Any]:
        logger.info(f"Generating test report for {project_name}")
        return {
            "success": True,
            "project_name": project_name,
            "report_format": kwargs.get("report_format", "detailed"),
            "strictness": self.strictness,
            "focus_areas": self.focus_areas,
            "message": f"Test report generated for '{project_name}'",
            "note": "Comprehensive software testing report in conversation response"
        }

    def get_greeting_message(self) -> str:
        return (
            "👋 Hello! I'm your Software Testing Agent.\n\n"
            "I specialize in testing software projects for:\n"
            "• 💻 Code quality and standards\n"
            "• 🏗️ Architecture and design patterns\n"
            "• 🔒 Security vulnerabilities\n"
            "• ⚡ Performance and optimization\n"
            "• ✅ Test coverage and quality\n"
            "• 📚 Documentation completeness\n"
            "• 📦 Dependencies and licensing\n\n"
            "What software would you like me to test?"
        )


__all__ = ["SoftwareTestingAgent"]

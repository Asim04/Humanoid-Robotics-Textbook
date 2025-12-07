---
id: 0001
title: Update Constitution for Physical AI Robotics Textbook
stage: constitution
date: 2025-12-06
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: unknown
command: /sp.phr
labels: ["constitution", "project setup"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

/sp.constitution
Project: Comprehensive Textbook on Physical AI & Humanoid Robotics using Docusaurus and GitHub Pages

Core principles:
- Pedagogical excellence: Content structured for systematic learning from fundamentals to advanced topics
- Theory-practice integration: Balance between theoretical concepts and hands-on implementation
- Safety-first approach: Emphasize safety protocols in all physical robotics applications
- Interdisciplinary foundation: Cover mechanical, electrical, software, and AI aspects cohesively
- Future-ready content: Prepare students for emerging trends in embodied AI and robotics
- Accessibility: Make complex robotics concepts understandable through clear explanations and visuals

Key standards:
- Technical accuracy: All concepts verified against current research and industry practices
- Code quality: Python, ROS2, and robotics framework examples tested and documented
- Mathematical rigor: Equations rendered clearly with LaTeX, accompanied by intuitive explanations
- Safety documentation: Include safety warnings, best practices, and ethical considerations
- Citation format: IEEE style for academic papers and technical references
- Writing clarity: Technical yet accessible (Flesch-Kincaid grade 12-14 for college level)
- Visual support: Diagrams, 3D models, video demonstrations, and interactive simulations

Content structure:
Part 1: Foundations (Weeks 1-4)
- Introduction to Physical AI and Embodied Intelligence
- Robotics fundamentals: kinematics, dynamics, and control
- Sensors and actuators for humanoid systems
- Computer vision for robotics

Part 2: Core Systems (Weeks 5-8)
- Robot Operating System (ROS2) fundamentals
- Motion planning and navigation
- Manipulation and grasping
- Human-robot interaction basics

Part 3: AI Integration (Weeks 9-12)
- Machine learning for robotics
- Deep reinforcement learning for physical tasks
- Vision-language-action models (VLAs)
- Sim-to-real transfer techniques

Part 4: Humanoid Robotics (Weeks 13-16)
- Bipedal locomotion and balance control
- Whole-body motion planning
- Dexterous manipulation with robotic hands
- Social robotics and human-aware behaviors

Part 5: Advanced Topics & Applications (Weeks 17-20)
- Foundation models for robotics (RT-2, PaLM-E, etc.)
- Multi-modal learning and world models
- Safety, ethics, and responsible AI in robotics
- Real-world case studies and industry applications

Chapter requirements:
- Learning objectives stated clearly at the beginning
- Theoretical explanations with mathematical foundations
- Worked examples with step-by-step solutions
- Code implementations with detailed comments
- Hands-on lab exercises and projects
- Review questions and problem sets
- Further reading and research references
- Chapter summary and key takeaways

Technical constraints:
- Platform: Docusaurus 3.x with custom plugins for interactive content
- Deployment: GitHub Pages with automated CI/CD pipeline
- Math rendering: KaTeX for fast equation rendering
- Code highlighting: Support for Python, C++, URDF, YAML, and shell scripts
- 3D visualization: Integration with Three.js or similar for robot models
- Video embedding: YouTube/Vimeo for demonstration videos
- Interactive elements: Colab notebooks, simulation embeds where applicable
- Mobile responsive: All diagrams and code readable on tablets and phones

Development workflow:
- Spec-Kit Plus for structured content generation and AI assistance
- Claude Code for implementation and code examples
- Git workflow: feature branches → review → main branch
- Content review cycle: Technical accuracy → Pedagogical effectiveness → Language/clarity
- Version control: Tag releases by semester/version (v1.0-Fall2025)
- Issue tracking: GitHub Issues for errata, suggestions, and improvements

Technology stack covered:
- Programming: Python 3.10+, C++ (for performance-critical components)
- Frameworks: ROS2 (Humble/Jazzy), PyTorch, TensorFlow
- Simulation: Gazebo, Isaac Sim, MuJoCo, PyBullet
- Hardware platforms: Reference designs for common humanoid platforms
- Vision: OpenCV, YOLO, Segment Anything, depth cameras
- AI models: Transformers, diffusion models, foundation models for robotics
- Tools: Docker for reproducible environments, Jupyter for interactive learning

Quality assurance:
- Technical review by robotics faculty and industry practitioners
- Code testing in specified simulation environments
- All mathematical derivations verified
- Safety protocols reviewed by lab safety officers
- Accessibility: Alt text for images, WCAG 2.1 AA compliance
- Proofreading by technical editor
- Beta testing with student cohort before official release
- Continuous feedback integration via GitHub Discussions

Success criteria:
- Complete coverage of 20-week semester course (40-50 lecture hours)
- Minimum 15 hands-on lab exercises with starter code and solutions
- All code examples execute in specified environments (Ubuntu 22.04, ROS2 Humble)
- At least 100 diagrams/figures for visual learning
- 10+ video demonstrations of physical robot behaviors
- Comprehensive problem sets: 200+ review questions and 50+ programming exercises
- Zero broken links, missing images, or non-functional code
- Site loads in <3 seconds on standard broadband
- Positive feedback from at least 30 beta reviewers (students, educators, practitioners)
- Successfully used to teach at least one complete course offering
- Downloadable PDF version for offline reading
- Active community engagement: GitHub stars, forks, and contributions

Ethical and safety standards:
- Explicit safety warnings for hardware experiments
- Ethical considerations for AI and robotics applications
- Discussion of bias, fairness, and social impact
- Environmental considerations for robotics deployment
- Privacy and security in robot data collection
- Compliance with research ethics and regulatory frameworks

Assessment alignment:
- Content maps to course learning outcomes
- Difficulty progression appropriate for undergraduate/graduate students
- Mixture of theoretical problems and practical projects
- Capstone project guidelines for semester-long integration
- Rubrics provided for graded assignments
- Support materials for instructors (slides, solution manuals)

Maintenance plan:
- Quarterly updates for bug fixes and minor improvements
- Annual major updates to reflect new research and technologies
- Community contributions welcomed via pull requests
- Errata page maintained and prominently linked
- Deprecation warnings for outdated content
- Migration guides when major tool versions changephysical-ai-robotics-textbook/
├── docs/
│   ├── intro.md
│   ├── part1-foundations/
│   │   ├── ch01-introduction.md
│   │   ├── ch02-robotics-fundamentals.md
│   │   ├── ch03-sensors-actuators.md
│   │   └── ch04-computer-vision.md
│   ├── part2-core-systems/
│   ├── part3-ai-integration/
│   ├── part4-humanoid-robotics/
│   ├── part5-advanced-topics/
│   ├── labs/
│   │   ├── lab01-ros2-setup.md
│   │   ├── lab02-kinematics.md
│   │   └── ...
│   ├── appendices/
│   │   ├── math-review.md
│   │   ├── python-primer.md
│   │   └── safety-guidelines.md
│   └── resources/
│       ├── datasets.md
│       ├── tools.md
│       └── further-reading.md
├── static/
│   ├── img/
│   ├── videos/
│   └── code/
├── src/
│   └── components/
├── .sp/
│   └── constitution.md
└── docusaurus.config.js

## Response snapshot

Updated the project constitution based on the provided project details, including core principles, key standards, development guidelines, and governance.

## Outcome

- ✅ Impact: The project constitution for the "Comprehensive Textbook on Physical AI & Humanoid Robotics using Docusaurus and GitHub Pages" has been successfully created/updated, providing a foundational document for project principles, standards, and workflow.
- 🧪 Tests: none
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: none
- 🧠 Reflection: The `create-phr.sh` script was not found, requiring manual PHR creation. This highlights a need to ensure necessary scripts are available or to improve agent-native fallback mechanisms.

## Evaluation notes (flywheel)

- Failure modes observed: `create-phr.sh` script not found, resulting in fallback to agent-native PHR creation.
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Investigate the availability and path of `create-phr.sh` or enhance error handling for script execution.

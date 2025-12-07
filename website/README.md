# Physical AI & Humanoid Robotics Textbook

[![CI](https://github.com/facebook/physical-ai-humanoid-robotics/actions/workflows/ci.yml/badge.svg)](https://github.com/facebook/physical-ai-humanoid-robotics/actions/workflows/ci.yml)
[![Deploy to GitHub Pages](https://github.com/facebook/physical-ai-humanoid-robotics/actions/workflows/deploy.yml/badge.svg)](https://facebook.github.io/physical-ai-humanoid-robotics)

This website hosts the comprehensive textbook on Physical AI and Humanoid Robotics, built with [Docusaurus](https://docusaurus.io/).

## About

This textbook provides a complete learning path from foundational concepts to advanced implementations in embodied intelligence. It covers ROS 2, NVIDIA Isaac Sim, perception systems, control algorithms, and modern AI techniques for robotics.

The textbook is organized into five main parts:
1. Foundations (Weeks 1-2)
2. ROS 2 Fundamentals (Weeks 3-4)
3. Perception & Control (Weeks 5-6)
4. Advanced Topics (Weeks 7-8)
5. Integration & Deployment (Weeks 9-10)

Each part contains multiple chapters with hands-on labs and code examples.

## Table of Contents

- [Installation](#installation)
- [Local Development](#local-development)
- [Build](#build)
- [Deployment](#deployment)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Installation

```bash
npm install
```

## Local Development

```bash
npm run start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
npm run build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment

Using SSH:

```bash
USE_SSH=true npm run deploy
```

Not using SSH:

```bash
GIT_USER=<Your GitHub username> npm run deploy
```

If you are using GitHub pages for hosting, this command is a convenient way to build the website and push to the `gh-pages` branch.

## Project Structure

```
website/
├── .github/                 # GitHub configuration (templates, workflows)
├── blog/                    # Blog posts (if enabled)
├── docs/                    # Textbook content
│   ├── part-i-foundations/  # Weeks 1-2 content
│   ├── part-ii-ros-fundamentals/ # Weeks 3-4 content
│   ├── part-iii-perception-control/ # Weeks 5-6 content
│   ├── part-iv-advanced-topics/ # Weeks 7-8 content
│   ├── part-v-integration-deployment/ # Weeks 9-10 content
│   ├── labs/                # Lab exercises
│   ├── code-examples/       # Code examples
│   └── appendices/          # Reference materials
├── src/                     # Custom React components
│   └── css/                 # Custom styles
├── static/                  # Static assets (images, etc.)
├── docusaurus.config.ts     # Docusaurus configuration
├── package.json             # Dependencies and scripts
├── sidebars.ts              # Navigation sidebar configuration
└── tsconfig.json            # TypeScript configuration
```

## Contributing

We welcome contributions to improve the textbook! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to:

- Report issues using our [Issue Templates](.github/ISSUE_TEMPLATE/)
- Submit pull requests following our [PR Template](.github/PULL_REQUEST_TEMPLATE.md)
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

## License

This textbook is licensed under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-nc-sa/4.0/).

The underlying source code used to format and display this content is licensed under the [MIT License](https://opensource.org/licenses/MIT).

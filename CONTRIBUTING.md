# Contributing to OpenMC Username Sniper

Thank you for your interest in contributing to the OpenMC Username Sniper project! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Node.js 16.x or newer
- Python 3.6 or newer
- npm or yarn
- Git

### Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/Minecraft-Sniper-Application.git
   cd Minecraft-Sniper-Application
   ```

3. Install dependencies and set up the development environment:
   ```bash
   npm run setup
   ```

4. Start the development server:
   ```bash
   # In one terminal
   npm run dev
   
   # In another terminal
   npm start
   ```

## Project Structure

- `src/main/` - Electron main process code
- `src/renderer/` - React frontend code
- `src/python/` - Python script adapters
- `assets/` - Application icons and resources

## Development Workflow

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and test thoroughly
3. Commit your changes following the [Conventional Commits](https://www.conventionalcommits.org/) format:
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve issue with authentication"
   ```

4. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a Pull Request on GitHub

## Testing

Before submitting a Pull Request, please run tests to ensure your changes don't break existing functionality:

1. Review the test plan in TEST-PLAN.md
2. Run automated tests:
   ```bash
   npm test
   ```

3. Manually test the functionality you've changed
4. For UI changes, test on different platforms if possible

## Code Style and Guidelines

- Follow the existing code style and patterns
- Use meaningful variable and function names
- Write comments for complex code sections
- Keep functions small and focused on a single task
- Use TypeScript type annotations where appropriate

## Building and Packaging

To build the application for your platform:

```bash
npm run make
```

To build for a specific platform (if supported by your OS):

```bash
npm run make -- --platform=win32
npm run make -- --platform=darwin
npm run make -- --platform=linux
```

## Release Process

1. Version numbers follow [Semantic Versioning](https://semver.org/)
2. Releases are created by tagging the main branch:
   ```bash
   git tag -a v1.0.0 -m "Version 1.0.0"
   git push origin v1.0.0
   ```

3. GitHub Actions will automatically build and create installers for all platforms
4. Release notes should be added to the GitHub release

## Questions and Support

If you have questions or need help, please:

1. Check the existing issues on GitHub
2. Open a new issue if your question hasn't been addressed
3. Tag the issue with "question" or "help wanted"

We appreciate your contributions! 
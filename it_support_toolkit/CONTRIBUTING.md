# Contributing to IT Support Toolkit

Thanks for your interest in contributing! 🚀

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/toolskitmasaul.git
   cd toolskitmasaul/it_support_toolkit
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run from source** to verify:
   ```bash
   python main.py
   ```

## Development Guidelines

### Code Style
- Follow [PEP 8](https://peps.python.org/pep-0008/).
- Use type hints where practical.
- Keep methods short and focused — single responsibility principle.
- Use `TaskWorker` (from `utils/background_tasks.py`) for any blocking I/O to keep the UI responsive.

### Architecture
```
core/     → Data & logic layer (no PyQt imports)
ui/       → Presentation layer (PyQt6 widgets)
utils/    → Shared utilities (config, logging, permissions)
```

### Adding a New Page
1. Create `ui/pages/your_page.py` — subclass `QWidget`
2. Register in `ui/pages/__init__.py`
3. Add to `MainWindow.PAGE_CLASSES` and `nav_items` in `ui/app.py`
4. Style with object names in `ui/styles.qss` and `ui/styles_light.qss`

### Adding a Core Module
1. Create `core/your_module.py`
2. Keep it importable without PyQt — pure Python only
3. Expose static methods or class methods for easy calling

### Before Submitting
- [ ] Code runs without errors on Windows 10/11
- [ ] Both dark and light themes render correctly
- [ ] Admin-dependent features degrade gracefully without admin
- [ ] New features use `TaskWorker` for background work
- [ ] No new external dependencies without discussion

### Pull Request Process
1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make changes with clear commit messages
3. Push and open a PR against `main`
4. Describe **what** you changed and **why**
5. Link any related issues

## Questions?
Open a [GitHub Discussion](https://github.com/YOUR_USERNAME/toolskitmasaul/discussions) or file an issue.

# Contributing to VARSYS Kitchen Dashboard

Thank you for your interest in contributing to VARSYS Kitchen Dashboard! We welcome contributions from the community and are grateful for your help in making this project better.

## 🤝 How to Contribute

### Reporting Bugs

Before creating bug reports, please check the [issue tracker](https://github.com/your-username/VARSYS-Kitchen-Dashboard/issues) to see if the issue has already been reported.

When creating a bug report, please include:

- **Clear title and description**
- **Steps to reproduce** the issue
- **Expected behavior** vs **actual behavior**
- **Screenshots** if applicable
- **Environment details** (OS, Python version, etc.)
- **Application version**

### Suggesting Features

We welcome feature suggestions! Please:

1. Check if the feature has already been suggested
2. Create a detailed issue describing:
   - The problem the feature would solve
   - How you envision the feature working
   - Any alternative solutions you've considered

### Code Contributions

#### Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/VARSYS-Kitchen-Dashboard.git
   cd VARSYS-Kitchen-Dashboard
   ```
3. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

#### Development Workflow

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. **Make your changes**
3. **Test your changes:**
   ```bash
   python kitchen_app.py
   ```
4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```
5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Create a Pull Request**

#### Code Style Guidelines

- **Follow PEP 8** for Python code style
- **Use meaningful variable and function names**
- **Add docstrings** to functions and classes
- **Comment complex logic**
- **Keep functions focused** and reasonably sized

#### Commit Message Guidelines

Use clear and descriptive commit messages:

- **Add:** for new features
- **Fix:** for bug fixes
- **Update:** for updates to existing features
- **Remove:** for removing code/features
- **Refactor:** for code refactoring

Examples:
```
Add: inventory low stock alert system
Fix: expense calculation error in budget module
Update: improve dashboard chart performance
```

## 🧪 Testing

Before submitting a pull request:

1. **Test the application** thoroughly
2. **Verify all features** work as expected
3. **Check for any console errors**
4. **Test on different screen sizes** if UI changes are involved

## 📝 Documentation

When contributing:

- **Update documentation** if you change functionality
- **Add comments** for complex code
- **Update README.md** if needed
- **Include examples** for new features

## 🎯 Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- **Bug fixes** and stability improvements
- **Performance optimizations**
- **UI/UX improvements**
- **Test coverage** expansion

### Medium Priority
- **New features** for kitchen management
- **Integration** with external services
- **Mobile responsiveness** improvements
- **Accessibility** enhancements

### Low Priority
- **Code refactoring**
- **Documentation** improvements
- **Localization** support
- **Theme** customization

## 🔧 Development Setup

### Prerequisites

- **Python 3.8+**
- **Git**
- **Code editor** (VS Code recommended)

### Recommended Tools

- **Python extension** for VS Code
- **GitLens** for Git integration
- **Pylint** for code linting
- **Black** for code formatting

### Project Structure

```
VARSYS-Kitchen-Dashboard/
├── kitchen_app.py              # Main application entry point
├── version.py                  # Version management
├── update_checker.py           # Auto-update functionality
├── modules/                    # Core application modules
│   ├── inventory_fixed.py      # Inventory management
│   ├── sales.py               # Sales tracking
│   ├── budget.py              # Budget management
│   └── ...                    # Other modules
├── utils/                      # Utility functions
├── data/                       # Data storage (CSV files)
├── assets/                     # Images, icons, resources
├── requirements.txt            # Python dependencies
└── setup_cx_freeze.py         # Build configuration
```

## 🚀 Release Process

1. **Version bump** in `version.py`
2. **Update CHANGELOG.md**
3. **Create release** on GitHub
4. **Upload executable** to release
5. **Update download links**

## 📞 Getting Help

If you need help with contributing:

- **Check the documentation** in the Wiki
- **Ask questions** in GitHub Discussions
- **Join our community** (links in README)
- **Contact maintainers** through issues

## 🏆 Recognition

Contributors will be:

- **Listed in CONTRIBUTORS.md**
- **Mentioned in release notes**
- **Credited in the application**

## 📋 Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Commit messages are clear
- [ ] No merge conflicts
- [ ] Feature is tested thoroughly
- [ ] Screenshots included for UI changes

## 🎉 Thank You!

Your contributions help make VARSYS Kitchen Dashboard better for everyone. We appreciate your time and effort in improving this project!

---

**Happy Coding! 🍳**

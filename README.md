# DataGuard-QA

![CI](https://github.com/bszilard26/DataGuard-QA/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Overview

**DataGuard-QA** is an end-to-end test automation framework built in Python to demonstrate professional QA practices across:

- ✅ UI automation (Selenium)
- ✅ API testing (requests)
- ✅ ETL/data validation (SQLite)
- ✅ Containerized execution (Docker)
- ✅ Reporting (Allure)
- ✅ CI/CD integration (GitHub Actions)

This project simulates real-world testing layers in a modular, DevOps-friendly structure — tailored for QA roles in data-heavy and enterprise environments.

---

## 📦 Tech Stack

| Area     | Tools Used                              |
|----------|------------------------------------------|
| UI       | Selenium, WebDriverManager, Pytest       |
| API      | requests, Pytest                         |
| ETL/DB   | SQLite, SQLAlchemy (optional)            |
| CI/CD    | GitHub Actions, Docker, Docker Compose   |
| Reports  | Allure, allure-pytest plugin             |

---

## 🧪 Test Coverage

| Test Type | Description |
|-----------|-------------|
| **UI**    | Automates login flow using Selenium against [saucedemo.com](https://www.saucedemo.com) |
| **API**   | Validates REST endpoints from [jsonplaceholder.typicode.com](https://jsonplaceholder.typicode.com) |
| **ETL**   | Verifies data integrity post-transformation using SQLite queries |

---

## 🚀 Getting Started

```bash
# Clone and navigate
git clone git@github.com:bszilard26/DataGuard-QA.git
cd DataGuard-QA

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# View report (requires Allure CLI)
allure serve reports/allure-results


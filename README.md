# DataGuard-QA

![CI](https://github.com/bszilard26/DataGuard-QA/actions/workflows/ci.yml/badge.svg)
![Version](https://img.shields.io/badge/version-1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Overview

**DataGuard-QA** is an end-to-end test automation framework built in Python to demonstrate enterprise-level QA practices across:

- ✅ UI automation (Selenium + POM)
- ✅ API testing (requests, Pytest)
- ✅ ETL/data validation (SQLite-based pipelines)
- ✅ Containerized execution (Docker)
- ✅ Reporting (Allure)
- ✅ CI/CD integration (GitHub Actions)

This project simulates realistic, full-stack QA responsibilities in a modular and DevOps-aligned structure. It's designed for showcasing data-aware automation testing — combining reliability, reusability, and test observability.

---

## 📦 Tech Stack

| Area     | Tools Used                              |
|----------|------------------------------------------|
| UI       | Selenium, WebDriverManager, Pytest       |
| API      | requests, Pytest                         |
| ETL/DB   | SQLite, Python (OOP-based validation)    |
| CI/CD    | GitHub Actions, Docker, Docker Compose   |
| Reports  | Allure, allure-pytest plugin             |

---

## 🧪 Test Coverage

| Test Type | Description |
|-----------|-------------|
| **UI**    | Automates login flow using Selenium against [saucedemo.com](https://www.saucedemo.com), structured using Page Object Model |
| **API**   | Verifies REST endpoints using `requests` library with assertions on status codes and response bodies |
| **ETL**   | Validates data post-transformation with checks like row count comparison, null validation, data type enforcement, duplicate detection, and logical mapping (e.g., full name → first/last name split) |

---

## 🧠 ETL Validation Scenarios

Implemented validations in `data_validator.py`:

- 🔢 **Row Count Match** — Verifies staging vs. target counts
- 🚫 **Null Check** — Ensures critical fields like `email` are populated
- 🧬 **Uniqueness** — Ensures `id` column is de-duplicated
- 🧠 **Business Logic** — Confirms correct parsing of `full_name` into `first_name`, `last_name`
- 🧪 **Column Type Integrity** — Asserts expected types (e.g., `age: int`, `email: str`)
- ♻️ **Reusable Class** — All validations abstracted via OOP utility `DataValidator` with connection lifecycle management

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

# Build and run tests in container
docker build -t dataguard-qa .
docker run --rm dataguard-qa

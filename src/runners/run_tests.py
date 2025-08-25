#!/usr/bin/env python3
"""
Test runner script for Jakarta Maps Analyzer
This script provides convenient ways to run different types of tests.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle the output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(command)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            cwd=Path(__file__).parent,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        return False
    except FileNotFoundError:
        print(f"Command not found: {command[0]}")
        print("Please ensure pytest is installed: pip install -r requirements-test.txt")
        return False


def install_dependencies():
    """Install test dependencies."""
    print("Installing test dependencies...")
    command = [sys.executable, "-m", "pip", "install", "-r", "requirements-test.txt"]
    return run_command(command, "Installing test dependencies")


def run_unit_tests():
    """Run unit tests only."""
    command = ["python", "-m", "pytest", "-m", "unit", "-v"]
    return run_command(command, "Unit tests")


def run_integration_tests():
    """Run integration tests only."""
    command = ["python", "-m", "pytest", "-m", "integration", "-v"]
    return run_command(command, "Integration tests")


def run_all_tests():
    """Run all tests."""
    command = ["python", "-m", "pytest", "-v"]
    return run_command(command, "All tests")


def run_coverage_tests():
    """Run tests with coverage report."""
    command = ["python", "-m", "pytest", "--cov=main", "--cov-report=term-missing", "--cov-report=html", "-v"]
    return run_command(command, "Tests with coverage")


def run_quick_tests():
    """Run quick tests (excluding slow tests)."""
    command = ["python", "-m", "pytest", "-m", "not slow", "-v"]
    return run_command(command, "Quick tests (excluding slow tests)")


def run_security_tests():
    """Run security-focused tests."""
    command = ["python", "-m", "pytest", "-k", "security or sanitiz or validat", "-v"]
    return run_command(command, "Security-focused tests")


def run_linting():
    """Run code linting (if flake8 is available)."""
    try:
        command = ["python", "-m", "flake8", "main.py", "tests/"]
        return run_command(command, "Code linting")
    except:
        print("Flake8 not available. Skipping linting.")
        return True


def check_test_structure():
    """Check that test structure is correct."""
    print("\nChecking test structure...")
    
    required_files = [
        "tests/__init__.py",
        "tests/test_config.py",
        "tests/test_validation.py",
        "tests/test_api_integration.py",
        "tests/test_data_processing.py",
        "tests/test_csv_processing.py",
        "tests/test_error_handling.py",
        "tests/fixtures/test_queries.csv",
        "pytest.ini",
        "requirements-test.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("All required test files are present.")
        return True


def main():
    """Main function to handle command line arguments."""
    parser = argparse.ArgumentParser(
        description="Test runner for Jakarta Maps Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Types:
  unit        Run unit tests only
  integration Run integration tests only
  all         Run all tests (default)
  coverage    Run tests with coverage report
  quick       Run quick tests (exclude slow tests)
  security    Run security-focused tests
  
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py unit              # Run unit tests only
  python run_tests.py coverage          # Run with coverage
  python run_tests.py --install         # Install dependencies first
  python run_tests.py --check           # Check test structure
        """
    )
    
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["unit", "integration", "all", "coverage", "quick", "security"],
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install test dependencies before running tests"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check test structure before running tests"
    )
    
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run code linting"
    )
    
    args = parser.parse_args()
    
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    success = True
    
    # Install dependencies if requested
    if args.install:
        success = install_dependencies() and success
    
    # Check test structure if requested
    if args.check:
        success = check_test_structure() and success
    
    # Run linting if requested
    if args.lint:
        success = run_linting() and success
    
    # Run the requested tests
    if success:
        test_functions = {
            "unit": run_unit_tests,
            "integration": run_integration_tests,
            "all": run_all_tests,
            "coverage": run_coverage_tests,
            "quick": run_quick_tests,
            "security": run_security_tests
        }
        
        success = test_functions[args.test_type]() and success
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✅ All operations completed successfully!")
    else:
        print("❌ Some operations failed. Check the output above.")
    print(f"{'='*60}")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
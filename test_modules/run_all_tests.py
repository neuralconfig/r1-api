#!/usr/bin/env python3
"""
Run all RUCKUS One API module tests.

This script runs all the test scripts for the RUCKUS One API modules
and summarizes the results.

Usage:
    python run_all_tests.py
"""

import os
import sys
import importlib
import logging
from typing import Dict, Any, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_test_module(module_name: str) -> Tuple[bool, Dict[str, bool]]:
    """
    Run a single test module and return its results.
    
    Args:
        module_name: Name of the test module to run
        
    Returns:
        Tuple of (overall_result, test_results)
    """
    logger.info(f"Running test module: {module_name}")
    
    try:
        # Import the module dynamically
        module = importlib.import_module(f"test_modules.{module_name}")
        
        # Run the tests
        test_results = {}
        overall_result = module.run_tests()
        
        # For modules with a more detailed result structure
        if hasattr(module, 'results') and isinstance(module.results, dict):
            test_results = module.results
        
        return overall_result, test_results
    
    except Exception as e:
        logger.error(f"Error running test module {module_name}: {e}")
        return False, {}

def run_all_tests() -> Dict[str, Any]:
    """
    Run all test modules and collect results.
    
    Returns:
        Dictionary of results by module
    """
    # List of test modules to run (excluding __init__ and this file)
    test_modules = [
        'test_venues',
        'test_access_points',
        'test_switches',
        'test_wlans',
        'test_vlans'
    ]
    
    # Run each test module and collect results
    results = {}
    all_passed = True
    
    for module_name in test_modules:
        module_passed, module_results = run_test_module(module_name)
        results[module_name] = {
            'overall': module_passed,
            'tests': module_results
        }
        if not module_passed:
            all_passed = False
    
    # Print summary
    print("\n" + "=" * 80)
    print("OVERALL TEST RESULTS")
    print("=" * 80)
    
    for module_name, module_results in results.items():
        status = "PASS" if module_results['overall'] else "FAIL"
        print(f"{module_name}: {status}")
    
    print("=" * 80)
    print(f"OVERALL: {'PASS' if all_passed else 'FAIL'}")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    run_all_tests()
    
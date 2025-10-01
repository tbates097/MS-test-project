# Aerotech DLL Integration Test Project

This is a minimal test project to demonstrate an issue with loading and using Aerotech DLLs in Python via pythonnet.

## Environment
- Windows 10
- Python (version will be printed by test script)
- pythonnet
- Aerotech Automation1 DLLs (v2.11.0.3126)

## Issue Description
When attempting to use the Aerotech DLLs through pythonnet, we encounter issues with .NET assembly loading and type resolution. Specifically:

1. Initial DLL loading appears to work
2. Basic type imports seem to work
3. When trying to use certain functionality (like `CalculateParameters`), we get type loading errors related to System.IO.Path

## Test Script
The `test_aerotech.py` script attempts to:
1. Load the minimal required Aerotech assemblies
2. Import and use basic types
3. Read an MCD file
4. Print basic information about the MCD

This represents the simplest possible use case of the Aerotech libraries.

## Running the Test
1. Ensure pythonnet is installed: `pip install pythonnet`
2. Run the test script: `python test_aerotech.py`

## Expected Output
The script should be able to:
- Load the Aerotech DLL
- Read an MCD file
- Display basic information about the MCD

## Actual Output
(This will be filled in after running the test) 
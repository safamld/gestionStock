#!/bin/bash

echo "========================================="
echo "Test Login Flow"
echo "========================================="

# Test 1: Get login page (should return 200)
echo -e "\n1. Testing GET /login/"
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:8000/login/

# Test 2: Get CSRF token (simulate)
echo -e "\n2. Testing login attempt (need valid credentials)"
echo "Note: For actual test, use browser to test with admin/admin or correct credentials"

echo -e "\n========================================="
echo "Access via browser:"
echo "URL: http://localhost:8000/login/"
echo "========================================="

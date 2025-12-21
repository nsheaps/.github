#!/bin/bash
# Test workflow files for syntax errors

set -e

cd "$(dirname "$0")/.."

echo "Testing workflow syntax..."

# Test each workflow file
for workflow in .github/workflows/*.yml ansible/templates/workflows/*.yml; do
    if [ -f "$workflow" ]; then
        echo "Testing: $workflow"
        
        # Basic YAML syntax check using Python
        python3 -c "
import yaml
import sys

try:
    with open('$workflow', 'r') as f:
        yaml.safe_load(f)
    print('  ✓ Valid YAML')
except yaml.YAMLError as e:
    print(f'  ✗ Invalid YAML: {e}')
    sys.exit(1)
"
    fi
done

echo ""
echo "✓ All workflow files have valid syntax"

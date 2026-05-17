#!/bin/bash
# Inject memory into session context
MEMORY_FILE="$(dirname "$0")/memory.md"
if [ -f "$MEMORY_FILE" ]; then
    echo "=== ПАМЯТЬ ИЗ ПРЕДЫДУЩИХ СЕССИЙ ==="
    cat "$MEMORY_FILE"
    echo "==================================="
fi

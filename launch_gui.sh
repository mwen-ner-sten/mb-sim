#!/bin/bash
#
# GUI Launcher for MB-Sim Modbus Simulator (Shell Script)
#
# This script provides an easy way to launch the GUI without needing to set PYTHONPATH.
# Run this script from the project root directory.
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the current directory (project root)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_PATH="$PROJECT_ROOT/src"

echo -e "${BLUE}🚀 Launching MB-Sim GUI${NC}"
echo -e "${BLUE}📁 Project root: $PROJECT_ROOT${NC}"
echo -e "${BLUE}📁 Source path: $SRC_PATH${NC}"
echo -e "${BLUE}🎯 Command: python -m mb_sim.gui${NC}"

echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo -e "   • Press Ctrl+C to exit the GUI"
echo -e "   • The GUI will show device and register management"
echo -e "   • Make sure no other Modbus server is running on port 1502"
echo -e "${YELLOW}=================================================${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found. Please install Python 3.11+${NC}"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

echo -e "${GREEN}Using Python command: $PYTHON_CMD${NC}"

# Launch the GUI
exec "$PYTHON_CMD" -m mb_sim.gui
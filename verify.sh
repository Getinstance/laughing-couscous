#!/bin/bash

# Tech Challenge Fase 4 - Verification Script
# This script verifies all required files are in place

echo "================================================================"
echo "Tech Challenge Fase 4 - Project Verification"
echo "================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL=0
FOUND=0

# Function to check file
check_file() {
    local file=$1
    local description=$2
    
    TOTAL=$((TOTAL + 1))
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $description"
        echo "   File: $file"
        FOUND=$((FOUND + 1))
    else
        echo -e "${RED}✗${NC} $description"
        echo "   File: $file"
    fi
    echo ""
}

# Function to check directory
check_dir() {
    local dir=$1
    local description=$2
    
    TOTAL=$((TOTAL + 1))
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $description"
        echo "   Directory: $dir"
        FOUND=$((FOUND + 1))
    else
        echo -e "${RED}✗${NC} $description"
        echo "   Directory: $dir"
    fi
    echo ""
}

# Main Project Files
echo -e "${YELLOW}=== Core Project Files ===${NC}"
check_file "requirements.txt" "Python Dependencies"
check_file "README.md" "Main Documentation"
check_file "IMPLEMENTATION_SUMMARY.md" "Implementation Summary"
check_file ".gitignore" "Git Ignore File"

# Jupyter Notebook
echo -e "${YELLOW}=== Jupyter Notebook ===${NC}"
check_file "notebooks/fase-4-lstm-model.ipynb" "LSTM Training Notebook"

# Source Code
echo -e "${YELLOW}=== Source Code ===${NC}"
check_dir "src" "Source Code Directory"
check_dir "src/data" "Data Module"
check_dir "src/models" "Models Module"
check_dir "src/api" "API Module"

check_file "src/__init__.py" "src Package Init"
check_file "src/data/__init__.py" "Data Package Init"
check_file "src/data/data_collector.py" "Data Collector Module"
check_file "src/models/__init__.py" "Models Package Init"
check_file "src/models/lstm_model.py" "LSTM Model Module"
check_file "src/api/__init__.py" "API Package Init"
check_file "src/api/app.py" "FastAPI Application"
check_file "src/api/monitoring.py" "Monitoring Module"

# Docker
echo -e "${YELLOW}=== Docker Configuration ===${NC}"
check_file "Dockerfile" "Dockerfile"
check_file "docker-compose.yml" "Docker Compose"
check_file ".dockerignore" "Docker Ignore"

# Documentation
echo -e "${YELLOW}=== Documentation ===${NC}"
check_dir "docs" "Documentation Directory"
check_file "docs/API.md" "API Documentation"
check_file "docs/DEPLOYMENT.md" "Deployment Guide"
check_file "docs/QUICKSTART.md" "Quick Start Guide"
check_file "docs/DELIVERABLES.md" "Deliverables List"

# Models Directory (may not exist until notebook is run)
echo -e "${YELLOW}=== Models Directory ===${NC}"
if [ -d "models" ]; then
    echo -e "${GREEN}✓${NC} Models Directory Exists"
    echo "   Directory: models"
    
    if [ -f "models/lstm_model.h5" ]; then
        echo -e "${GREEN}✓${NC} Trained Model Found"
        size=$(ls -lh models/lstm_model.h5 | awk '{print $5}')
        echo "   File: models/lstm_model.h5 (Size: $size)"
    else
        echo -e "${YELLOW}⚠${NC} Trained Model Not Found (run notebook to generate)"
    fi
    
    if [ -f "models/scaler.pkl" ]; then
        echo -e "${GREEN}✓${NC} Scaler Found"
    fi
    
    if [ -f "models/model_info.json" ]; then
        echo -e "${GREEN}✓${NC} Model Info Found"
    fi
else
    echo -e "${YELLOW}⚠${NC} Models Directory Not Found (will be created by notebook)"
fi

echo ""
echo "================================================================"
echo -e "Verification Result: ${GREEN}$FOUND / $TOTAL${NC} items found"
echo "================================================================"

if [ "$FOUND" -eq "$TOTAL" ]; then
    echo -e "${GREEN}✓ All required files are present!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run the notebook to train the model (if needed):"
    echo "   jupyter notebook notebooks/fase-4-lstm-model.ipynb"
    echo ""
    echo "2. Start the API:"
    echo "   Option A (Local): python -m uvicorn src.api.app:app --reload"
    echo "   Option B (Docker): docker-compose up -d"
    echo ""
    echo "3. Access the API:"
    echo "   http://localhost:8000/docs"
    exit 0
else
    echo -e "${RED}✗ Some files are missing!${NC}"
    echo ""
    echo "Please ensure all files are created before proceeding."
    exit 1
fi

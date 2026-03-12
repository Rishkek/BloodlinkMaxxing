#!/bin/bash
# Quick Start Script for Healo Health Dashboard

echo "================================"
echo "Healo Health Dashboard - Quick Start"
echo "================================"
echo ""

# Check if running on Windows
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "Detected Windows environment"
    
    # Start Flask Backend
    echo ""
    echo "1. Starting Flask Backend..."
    echo "   Command: python app.py"
    echo ""
    echo "   Make sure to run this in PowerShell/CMD from:"
    echo "   C:\Users\rishi\PycharmProjects\Healo"
    echo ""
    
    # Instructions for Frontend
    echo "2. In a NEW terminal window, start the React Frontend..."
    echo "   Commands:"
    echo "   cd health-frontend"
    echo "   npm run dev"
    echo ""
    
    echo "3. Open your browser and navigate to:"
    echo "   http://localhost:5173"
    echo ""
    
    echo "================================"
    echo "Expected Behavior:"
    echo "- Map should load with Leaflet tiles"
    echo "- Green checkmarks (✔) = Hospitals in database"
    echo "- Blue icons (🏥) = Mock/demo hospitals"
    echo "- Red icons (🚑) = Ambulances"
    echo "================================"
else
    echo "This is a Windows-based project. Please run manually:"
    echo ""
    echo "Terminal 1 (Backend):"
    echo "  cd C:\\Users\\rishi\\PycharmProjects\\Healo"
    echo "  python app.py"
    echo ""
    echo "Terminal 2 (Frontend):"
    echo "  cd C:\\Users\\rishi\\PycharmProjects\\Healo\\health-frontend"
    echo "  npm run dev"
    echo ""
    echo "Then open: http://localhost:5173"
fi

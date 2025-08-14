#!/bin/bash

echo "🚀 RTX Innovations - macOS Build Script"
echo "=========================================="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18+ first.${NC}"
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.js version 18+ is required. Current version: $(node -v)${NC}"
    echo "   Please update Node.js to version 18 or higher."
    exit 1
fi

echo -e "${GREEN}✅ Node.js version: $(node -v)${NC}"
echo -e "${GREEN}✅ npm version: $(npm -v)${NC}"
echo

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ This script must be run on macOS to build for macOS.${NC}"
    echo "   Current OS: $OSTYPE"
    echo "   Please run this script on a Mac computer."
    exit 1
fi

echo -e "${BLUE}🍎 Detected macOS system${NC}"
echo

# Check for Xcode Command Line Tools
if ! xcode-select -p &> /dev/null; then
    echo -e "${YELLOW}⚠️  Xcode Command Line Tools not found.${NC}"
    echo "   Installing Xcode Command Line Tools..."
    xcode-select --install
    
    echo -e "${YELLOW}⏳ Please complete the Xcode installation in the popup window.${NC}"
    echo "   After installation completes, run this script again."
    exit 1
fi

echo -e "${GREEN}✅ Xcode Command Line Tools found${NC}"
echo

# Install dependencies
echo -e "${BLUE}📦 Installing dependencies...${NC}"
npm install

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"
echo

# Build the application
echo -e "${BLUE}🔨 Building application...${NC}"
npm run build

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Application built successfully!${NC}"
echo

# Build macOS executable
echo -e "${BLUE}🍎 Building macOS executable...${NC}"
npm run build-mac

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ macOS build failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ macOS executable built successfully!${NC}"
echo

# Check output
if [ -d "dist-builds/mac" ]; then
    echo -e "${GREEN}🎉 Build completed successfully!${NC}"
    echo
    echo -e "${BLUE}📱 macOS app location:${NC} dist-builds/mac/"
    echo -e "${BLUE}📦 DMG file location:${NC} dist-builds/"
    echo
    echo -e "${GREEN}🚀 You can now distribute the .dmg file to macOS users!${NC}"
    echo -e "${GREEN}💡 Users just need to double-click the .dmg file to install.${NC}"
    echo
    echo -e "${YELLOW}📋 Next steps:${NC}"
    echo "   1. Test the app on macOS"
    echo "   2. Share the .dmg file with users"
    echo "   3. Users install by dragging to Applications folder"
    echo
    echo -e "${BLUE}🔍 Files created:${NC}"
    ls -la dist-builds/
else
    echo -e "${RED}❌ Build output not found${NC}"
    exit 1
fi 
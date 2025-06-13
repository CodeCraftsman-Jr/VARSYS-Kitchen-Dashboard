#!/bin/bash

# VARSYS Kitchen Dashboard - Release Manager (Shell Script)
# Works on Linux, macOS, and Git Bash on Windows

show_help() {
    echo "VARSYS Kitchen Dashboard - Release Manager"
    echo "========================================="
    echo ""
    echo "Usage: ./release.sh [command] [options]"
    echo ""
    echo "Commands:"
    echo "  current           - Show current version"
    echo "  patch             - Increment patch version (1.0.3 -> 1.0.4)"
    echo "  minor             - Increment minor version (1.0.3 -> 1.1.0)"
    echo "  major             - Increment major version (1.0.3 -> 2.0.0)"
    echo "  set [version]     - Set specific version (e.g., 1.2.0)"
    echo "  build             - Build application only"
    echo "  release [version] - Prepare release with notes"
    echo "  full [version]    - Complete release process"
    echo "  clean             - Clean build directories"
    echo "  menu              - Show interactive menu"
    echo "  help              - Show this help"
    echo ""
    echo "Examples:"
    echo "  ./release.sh current"
    echo "  ./release.sh patch"
    echo "  ./release.sh set 1.1.0"
    echo "  ./release.sh full 1.1.0"
    echo "  ./release.sh menu"
    echo ""
}

show_success() {
    echo "✅ $1"
}

show_error() {
    echo "❌ $1"
}

show_info() {
    echo "ℹ️  $1"
}

run_python_script() {
    local script="$1"
    shift
    local args="$@"
    
    if python "$script" $args; then
        return 0
    else
        return 1
    fi
}

# Check if Python is available
if ! command -v python &> /dev/null; then
    show_error "Python is not installed or not in PATH"
    echo "Please install Python 3.x and try again"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "update_version.py" ] || [ ! -f "release_automation.py" ]; then
    show_error "Required files not found in current directory"
    echo "Please run this script from the VARSYS_COOKSUITE directory"
    echo "Expected files: update_version.py, release_automation.py"
    exit 1
fi

# Main script logic
case "${1:-help}" in
    "current")
        show_info "Getting current version..."
        run_python_script "update_version.py" "current"
        ;;
    
    "patch")
        show_info "Incrementing patch version..."
        if run_python_script "update_version.py" "increment" "patch"; then
            show_success "Patch version incremented successfully"
        else
            show_error "Failed to increment patch version"
        fi
        ;;
    
    "minor")
        show_info "Incrementing minor version..."
        if run_python_script "update_version.py" "increment" "minor"; then
            show_success "Minor version incremented successfully"
        else
            show_error "Failed to increment minor version"
        fi
        ;;
    
    "major")
        show_info "Incrementing major version..."
        if run_python_script "update_version.py" "increment" "major"; then
            show_success "Major version incremented successfully"
        else
            show_error "Failed to increment major version"
        fi
        ;;
    
    "set")
        if [ -z "$2" ]; then
            show_error "Version number required"
            echo "Usage: ./release.sh set 1.2.0"
            exit 1
        fi
        show_info "Setting version to $2..."
        if run_python_script "update_version.py" "set" "$2"; then
            show_success "Version set to $2 successfully"
        else
            show_error "Failed to set version"
        fi
        ;;
    
    "build")
        show_info "Building application..."
        if run_python_script "release_automation.py" "build"; then
            show_success "Application built successfully"
        else
            show_error "Build failed"
        fi
        ;;
    
    "release")
        if [ -z "$2" ]; then
            show_error "Version number required"
            echo "Usage: ./release.sh release 1.2.0"
            exit 1
        fi
        show_info "Preparing release $2..."
        if run_python_script "update_version.py" "release" "$2"; then
            show_success "Release $2 prepared successfully"
        else
            show_error "Failed to prepare release"
        fi
        ;;
    
    "full")
        if [ -z "$2" ]; then
            show_error "Version number required"
            echo "Usage: ./release.sh full 1.2.0"
            exit 1
        fi
        show_info "Starting full release process for version $2..."
        if run_python_script "release_automation.py" "full" "$2"; then
            show_success "Full release process completed successfully"
            echo ""
            echo "🎉 Release v$2 is ready!"
            echo ""
            echo "Next steps:"
            echo "1. Test the release package in the 'releases' folder"
            echo "2. Update release notes if needed"
            echo "3. Commit and push changes to GitHub"
            echo "4. Create GitHub release with the package"
        else
            show_error "Full release process failed"
        fi
        ;;
    
    "clean")
        show_info "Cleaning build directories..."
        if run_python_script "release_automation.py" "clean"; then
            show_success "Build directories cleaned successfully"
        else
            show_error "Failed to clean build directories"
        fi
        ;;
    
    "menu")
        show_info "Starting interactive menu..."
        python "release_manager.py"
        ;;
    
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    
    *)
        show_error "Invalid command: $1"
        echo "Use './release.sh help' for available commands"
        exit 1
        ;;
esac

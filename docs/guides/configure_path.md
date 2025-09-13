# How to Configure PATH for Java and GCC

## Current Status
- **Java**: Installed at `C:\Program Files\Java\jre1.8.0_461\bin\`
- **GCC/Clang**: Installation needs to be completed

## Method 1: Temporary (Current Session Only)

### For Java:
```bash
export PATH="/c/Program Files/Java/jre1.8.0_461/bin:$PATH"
```

### For GCC (after installing MinGW-w64):
```bash
# First, let's install MinGW-w64 properly:
choco install mingw -y

# Or download from: https://www.mingw-w64.org/downloads/
# Install to C:\mingw64

# Then add to PATH:
export PATH="/c/mingw64/bin:$PATH"
```

## Method 2: Permanent (System-wide)

### Windows GUI Method:
1. Press `Windows + X` and select "System"
2. Click "Advanced system settings"
3. Click "Environment Variables"
4. Under "System variables", find and select "Path", then click "Edit"
5. Click "New" and add:
   - `C:\Program Files\Java\jre1.8.0_461\bin`
   - `C:\mingw64\bin` (after installing MinGW)
6. Click "OK" to save

### PowerShell Method (Run as Administrator):
```powershell
# Add Java to PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\Program Files\Java\jre1.8.0_461\bin", [EnvironmentVariableTarget]::Machine)

# Add MinGW to PATH (after installation)
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";C:\mingw64\bin", [EnvironmentVariableTarget]::Machine)
```

## Method 3: Create Aliases (Immediate Use)

Add these to your `.bashrc` or `.bash_profile`:
```bash
# Java alias
alias java='"/c/Program Files/Java/jre1.8.0_461/bin/java"'
alias javac='"/c/Program Files/Java/jre1.8.0_461/bin/javac"'

# After installing MinGW:
alias gcc='/c/mingw64/bin/gcc'
alias g++='/c/mingw64/bin/g++'
```

## Recommended: Install MinGW-w64 Properly

Since the LLVM-MinGW didn't configure properly, I recommend:

```bash
# Using Chocolatey (recommended)
choco install mingw -y

# Or using MSYS2
# Download from: https://www.msys2.org/
# Then install gcc with: pacman -S mingw-w64-x86_64-gcc
```

## Verify Installation

After configuring PATH:
```bash
# Test Java
java -version

# Test GCC (after installing)
gcc --version
```

## Note
- Changes to PATH in Windows GUI require restarting your terminal
- The `export` command only affects the current session
- For permanent changes in Git Bash, edit `~/.bashrc` or `~/.bash_profile`
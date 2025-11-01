# yt-dlp PowerPC Compatibility Fork

This is a modified version of yt-dlp designed to run on PowerPC Mac OS X 10.4 Tiger and 10.5 Leopard systems with Python 3.5.

## Changes Made

### Python Version Compatibility
- Reduced minimum Python requirement from 3.10 to 3.5
- Replaced `typing.Self` usage with string literals for Python 3.5 compatibility
- Updated version classifiers in `pyproject.toml`

### TLS/SSL Support
- Added `ppc_ssl.py` module for enhanced TLS support on PowerPC systems
- Automatic detection and use of bundled OpenSSL 1.1.1w when system SSL is insufficient
- Support for TLS 1.2+ on systems that normally only support older protocols

## Installation

### Prerequisites
1. Python 3.5 (available through TigerBrew for PowerPC systems)
2. Xcode development tools
3. TigerBrew package manager (optional, for easier OpenSSL installation)

### Option 1: With Bundled OpenSSL (Recommended)
```bash
# Build bundled OpenSSL for better TLS support
python3 setup_ppc_tls.py

# Install yt-dlp
pip3 install -e .
```

### Option 2: Use System SSL (Limited TLS support)
```bash
# Install directly
pip3 install -e .
```

## TLS Support Details

### System Requirements
- **Tiger (10.4)**: Requires bundled OpenSSL for modern TLS
- **Leopard (10.5)**: May work with system SSL, bundled recommended

### Bundled OpenSSL Features
- OpenSSL 1.1.1w with PowerPC optimizations
- TLS 1.2 and 1.3 support
- Modern cipher suites
- Based on TigerBrew's proven OpenSSL formula

## Usage

Usage is identical to standard yt-dlp:

```bash
# Download a video
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID"

# List available formats
yt-dlp -F "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Limitations

### Known Issues
1. Some extractors may not work due to Python 3.5 limitations
2. Modern crypto algorithms may not be available without bundled OpenSSL
3. Performance may be slower on PowerPC hardware
4. Some dependencies may not be available for Python 3.5

### Compatibility Notes
- Tested on PowerPC G4/G5 systems
- Requires at least 512MB RAM (1GB recommended)
- Internet connection required for video downloads

## Building OpenSSL

The `setup_ppc_tls.py` script automatically:
1. Downloads OpenSSL 1.1.1w source
2. Configures for PowerPC architecture
3. Builds with Tiger/Leopard compatibility flags
4. Installs to `bundled_openssl/` directory

Manual build flags used:
```bash
./config darwin-ppc-cc \
    --prefix=./bundled_openssl \
    --openssldir=./bundled_openssl/ssl \
    no-ssl3 no-zlib shared \
    no-async -fno-common  # Tiger-specific flags
```

## Contributing

This is an experimental compatibility fork. For the main yt-dlp project, visit:
https://github.com/yt-dlp/yt-dlp

PowerPC-specific issues should be reported separately from the main project.

## Credits

- Original yt-dlp team for the excellent foundation
- TigerBrew project for OpenSSL PowerPC build configuration
- discord-lite project for inspiration on bundled TLS approach

## License

Same as yt-dlp: The Unlicense (public domain)
#!/usr/bin/env python3
"""
PowerPC TLS Setup Script for yt-dlp

This script downloads and builds OpenSSL 1.1.1w for PowerPC Mac OS X 10.4/10.5
Based on TigerBrew's OpenSSL formula configuration.
"""

import os
import subprocess
import sys
import urllib.request
import tarfile
import tempfile
import platform

OPENSSL_VERSION = "1.1.1w"
OPENSSL_URL = f"https://www.openssl.org/source/openssl-{OPENSSL_VERSION}.tar.gz"
OPENSSL_SHA256 = "cf3098950cb4d853ad95c0841f1f9c6d3dc102dccfcacd521d93925208b76ac8"

def detect_architecture():
    """Detect the current architecture"""
    machine = platform.machine().lower()
    if machine in ['powerpc', 'ppc', 'ppc64']:
        if '64' in machine:
            return 'darwin64-ppc-cc'
        else:
            return 'darwin-ppc-cc'
    elif machine in ['i386', 'x86_64']:
        return 'darwin64-x86_64-cc'
    else:
        return 'darwin64-x86_64-cc'  # fallback

def download_openssl():
    """Download OpenSSL source"""
    print(f"Downloading OpenSSL {OPENSSL_VERSION}...")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tar.gz') as tmp:
        urllib.request.urlretrieve(OPENSSL_URL, tmp.name)
        return tmp.name

def build_openssl(source_archive, install_prefix):
    """Build OpenSSL with PowerPC configuration"""
    arch = detect_architecture()
    print(f"Building OpenSSL for architecture: {arch}")
    
    with tempfile.TemporaryDirectory() as build_dir:
        # Extract source
        with tarfile.open(source_archive, 'r:gz') as tar:
            tar.extractall(build_dir)
        
        openssl_dir = os.path.join(build_dir, f"openssl-{OPENSSL_VERSION}")
        
        # Configure build
        configure_cmd = [
            './config',
            arch,
            f'--prefix={install_prefix}',
            '--openssldir=' + os.path.join(install_prefix, 'ssl'),
            'no-ssl3',
            'no-zlib',
            'shared'
        ]
        
        # Add Tiger-specific flags
        if platform.mac_ver()[0].startswith('10.4') or platform.mac_ver()[0].startswith('10.5'):
            configure_cmd.extend(['no-async', '-fno-common'])
        
        print("Configuring OpenSSL...")
        subprocess.run(configure_cmd, cwd=openssl_dir, check=True)
        
        print("Building OpenSSL...")
        subprocess.run(['make'], cwd=openssl_dir, check=True)
        
        print("Installing OpenSSL...")
        subprocess.run(['make', 'install'], cwd=openssl_dir, check=True)

def main():
    """Main setup function"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    openssl_prefix = os.path.join(script_dir, 'bundled_openssl')
    
    print("yt-dlp PowerPC TLS Setup")
    print("========================")
    
    if os.path.exists(openssl_prefix):
        print(f"OpenSSL already installed at {openssl_prefix}")
        return
    
    try:
        # Download source
        archive_path = download_openssl()
        
        # Build and install
        os.makedirs(openssl_prefix, exist_ok=True)
        build_openssl(archive_path, openssl_prefix)
        
        # Cleanup
        os.unlink(archive_path)
        
        print(f"OpenSSL {OPENSSL_VERSION} successfully installed to {openssl_prefix}")
        print("\nTo use with Python, set these environment variables:")
        print(f"export OPENSSL_ROOT_DIR={openssl_prefix}")
        print(f"export LD_LIBRARY_PATH={openssl_prefix}/lib:$LD_LIBRARY_PATH")
        print(f"export DYLD_LIBRARY_PATH={openssl_prefix}/lib:$DYLD_LIBRARY_PATH")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
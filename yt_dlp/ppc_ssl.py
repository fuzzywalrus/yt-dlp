"""
PowerPC SSL compatibility module for yt-dlp

This module provides TLS 1.2+ support on PowerPC Mac OS X 10.4/10.5
by using bundled OpenSSL 1.1.1w when system SSL is insufficient.
"""

import os
import ssl
import sys
import ctypes
import ctypes.util
from typing import Optional

# Check if we need to use bundled OpenSSL
BUNDLED_OPENSSL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'bundled_openssl')
USE_BUNDLED_SSL = False

def _check_system_tls_support():
    """Check if system SSL supports TLS 1.2+"""
    try:
        # Try to create a TLS 1.2 context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        return True
    except (AttributeError, OSError):
        return False

def _load_bundled_openssl():
    """Load bundled OpenSSL libraries"""
    global USE_BUNDLED_SSL
    
    if not os.path.exists(BUNDLED_OPENSSL_DIR):
        return False
    
    lib_dir = os.path.join(BUNDLED_OPENSSL_DIR, 'lib')
    if not os.path.exists(lib_dir):
        return False
    
    # Try to load bundled OpenSSL
    try:
        # Set library path
        if 'DYLD_LIBRARY_PATH' in os.environ:
            os.environ['DYLD_LIBRARY_PATH'] = f"{lib_dir}:{os.environ['DYLD_LIBRARY_PATH']}"
        else:
            os.environ['DYLD_LIBRARY_PATH'] = lib_dir
        
        # Load libraries
        libssl_path = os.path.join(lib_dir, 'libssl.dylib')
        libcrypto_path = os.path.join(lib_dir, 'libcrypto.dylib')
        
        if os.path.exists(libssl_path) and os.path.exists(libcrypto_path):
            ctypes.CDLL(libcrypto_path)
            ctypes.CDLL(libssl_path)
            USE_BUNDLED_SSL = True
            return True
    except Exception:
        pass
    
    return False

def create_ssl_context(verify_mode=ssl.CERT_REQUIRED):
    """Create an SSL context with TLS 1.2+ support"""
    try:
        if hasattr(ssl, 'PROTOCOL_TLS_CLIENT'):
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        else:
            # Fallback for older Python versions
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        
        context.check_hostname = False
        context.verify_mode = verify_mode
        
        # Try to set minimum TLS version
        try:
            context.minimum_version = ssl.TLSVersion.TLSv1_2
        except AttributeError:
            # TLSVersion enum not available in older Python
            try:
                context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1
            except AttributeError:
                pass
        
        # Load certificates
        try:
            context.load_default_certs()
        except AttributeError:
            # Fallback for older Python
            try:
                context.set_default_verify_paths()
            except AttributeError:
                pass
        
        return context
        
    except Exception as e:
        # If all else fails, create a basic context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = verify_mode
        return context

def patch_urllib():
    """Patch urllib to use our SSL context"""
    import urllib.request
    import urllib.parse
    
    original_build_opener = urllib.request.build_opener
    
    def patched_build_opener(*handlers):
        """Build opener with our SSL context"""
        opener = original_build_opener(*handlers)
        
        # Try to patch HTTPS handler
        for handler in opener.handlers:
            if hasattr(handler, '_context'):
                handler._context = create_ssl_context()
        
        return opener
    
    urllib.request.build_opener = patched_build_opener

# Initialize on import
if not _check_system_tls_support():
    if _load_bundled_openssl():
        print("Using bundled OpenSSL for TLS support")
    else:
        print("Warning: Limited TLS support on this system")
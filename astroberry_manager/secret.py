#!/usr/bin/env python3
# coding=utf-8

"""
This library is part of Astroberry OS and Astroberry Manager
https://github.com/astroberry-official/astroberry-os
https://github.com/astroberry-official/astroberry-manager

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Library General Public
License version 3 as published by the Free Software Foundation.
"""

import os, secrets

# Value that shipped in earlier releases. It is public, so it must never be used to sign sessions.
_RETIRED_DEFAULT = 'e55325c30acadadaae4006cf80c6439502043408f792afe57f501c2db4a0fc22'
_MIN_LENGTH = 32

def _default_path():
    base = os.getenv('XDG_CONFIG_HOME') or os.path.join(os.getenv('HOME', '/'), '.config')
    return os.path.join(base, 'astroberry-manager', 'secret_key')

def load_secret_key(path=None):
    """Return the key used to sign session cookies.

    Order: APP_KEY from the environment (unless it is the retired public default),
    then a per-installation key stored with owner-only permissions, then a new
    random key, which is stored for the next start. If the key cannot be stored
    it lasts for this process only, so sessions end at restart but are never
    signed with a guessable value.
    """
    key = os.getenv('APP_KEY')
    if key and key != _RETIRED_DEFAULT and len(key) >= _MIN_LENGTH:
        return key

    path = path or _default_path()
    try:
        with open(path, 'r') as f:
            key = f.read().strip()
        if len(key) >= _MIN_LENGTH and key != _RETIRED_DEFAULT:
            return key
    except OSError:
        pass

    key = secrets.token_hex(32)
    try:
        os.makedirs(os.path.dirname(path), mode=0o700, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(key)
    except OSError:
        pass
    return key

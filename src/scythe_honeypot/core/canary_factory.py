"""Generates realistic content for canary files - Scythe Honeypot."""

import os
import random
import string
from datetime import datetime, timedelta

from scythe_honeypot.core.canary import CanaryType


def _random_hex(length: int) -> str:
    """Random hex string."""
    return os.urandom(length).hex()


def _random_base64(length: int) -> str:
    """Random base64-like string (for fake keys)."""
    chars = string.ascii_letters + string.digits + "+/"
    return "".join(random.choices(chars, k=length))


def _format_date(days_ago: int = 0) -> str:
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")


def _generate_wallet() -> bytes:
    """
    Fake Bitcoin wallet.dat header (Berkeley DB format) + random encrypted-looking bytes.
    Real wallets start with bytes 0x00 0x05 0x31 0x62.
    """
    header = bytes([0x00, 0x05, 0x31, 0x62])  # Berkeley DB magic
    # Padding qui ressemble à du contenu chiffré
    encrypted_blob = os.urandom(random.randint(2000, 8000))
    return header + encrypted_blob


def _generate_ssh_key() -> str:
    """Fake OpenSSH private key. Format identique aux vraies."""
    # Body = ~50 lignes de base64, comme une vraie clé 4096 bits
    body_lines = []
    for _ in range(50):
        body_lines.append(_random_base64(70))
    body = "\n".join(body_lines)

    return (
        "-----BEGIN OPENSSH PRIVATE KEY-----\n"
        f"{body}\n"
        "-----END OPENSSH PRIVATE KEY-----\n"
    )


def _generate_password_file() -> str:
    """Fake credential dump - looks like a leaked password file."""
    services = [
        "admin", "root", "postgres", "mysql_root", "redis",
        "backup_user", "ftp_admin", "vpn_user", "api_key_prod",
        "stripe_key", "aws_secret", "github_token",
    ]
    lines = ["# Internal credentials - DO NOT SHARE", "# Last updated: " + _format_date(2), ""]
    for svc in services:
        # Format style "user:hash" ou "service=value"
        if random.random() < 0.5:
            lines.append(f"{svc}:{_random_hex(32)}")
        else:
            lines.append(f"{svc.upper()}={_random_base64(40)}")
    return "\n".join(lines) + "\n"


def _generate_database_dump() -> str:
    """Fake SQL dump with INSERT statements - looks like a real database export."""
    lines = [
        "-- MySQL dump",
        "-- Host: prod-db-01.internal    Database: company_main",
        f"-- Generation Time: {_format_date(1)}",
        "-- Server version: 8.0.32",
        "",
        "DROP TABLE IF EXISTS `users`;",
        "CREATE TABLE `users` (",
        "  `id` int NOT NULL AUTO_INCREMENT,",
        "  `email` varchar(255) NOT NULL,",
        "  `password_hash` varchar(255) NOT NULL,",
        "  `api_token` varchar(64) DEFAULT NULL,",
        "  PRIMARY KEY (`id`)",
        ");",
        "",
        "LOCK TABLES `users` WRITE;",
        "INSERT INTO `users` VALUES",
    ]

    # Plein de fausses lignes
    user_lines = []
    for i in range(1, 50):
        email = f"user{i}@company.com"
        pwd = _random_hex(32)
        token = _random_hex(32)
        user_lines.append(f"  ({i}, '{email}', '{pwd}', '{token}')")
    lines.append(",\n".join(user_lines) + ";")
    lines.append("UNLOCK TABLES;")

    return "\n".join(lines) + "\n"


def _generate_pdf() -> bytes:
    """Minimal but valid PDF structure with fake confidential-looking content."""
    # PDF minimaliste qui passe les readers basiques
    pdf = b"%PDF-1.4\n"
    pdf += b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    pdf += b"2 0 obj\n<< /Type /Pages /Count 1 /Kids [3 0 R] >>\nendobj\n"
    pdf += b"3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n"
    pdf += b"4 0 obj\n<< /Length 100 >>\nstream\n"
    pdf += b"BT /F1 12 Tf 100 700 Td (CONFIDENTIAL - Internal Use Only) Tj ET\n"
    pdf += b"endstream\nendobj\n"
    pdf += b"xref\n0 5\n0000000000 65535 f\n"
    pdf += b"trailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n400\n%%EOF\n"
    # Padding aléatoire pour faire grossir le fichier
    pdf += os.urandom(random.randint(5000, 20000))
    return pdf


def _generate_zip() -> bytes:
    """Fake ZIP file - just the header + random bytes (won't open but will look real to a glance)."""
    # ZIP magic bytes
    header = b"PK\x03\x04"  # ZIP local file header
    body = os.urandom(random.randint(10000, 50000))
    # End of central directory
    eocd = b"PK\x05\x06" + b"\x00" * 18
    return header + body + eocd


# Dispatch table : type → fonction de génération
_GENERATORS = {
    CanaryType.WALLET:   _generate_wallet,
    CanaryType.SSH_KEY:  _generate_ssh_key,
    CanaryType.PASSWORD: _generate_password_file,
    CanaryType.DATABASE: _generate_database_dump,
    CanaryType.PDF:      _generate_pdf,
    CanaryType.ZIP:      _generate_zip,
}


def generate_content(canary_type: CanaryType) -> bytes:
    """
    Generate realistic-looking content for a canary file.

    Returns bytes (binary or encoded text) ready to write to disk.
    """
    generator = _GENERATORS.get(canary_type)
    if generator is None:
        raise ValueError(f"No generator for type {canary_type}")

    content = generator()
    # Some generators return str, some return bytes — normalize to bytes
    if isinstance(content, str):
        return content.encode("utf-8")
    return content
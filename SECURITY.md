# Security Policy — OZPanel

## Cryptographic Release Integrity (OZV7-Fortress)
- Every official OZPanel release artifact (`oz_installer_vi`, `oz_installer_vi-arm64`, `install.sh`) is covered by `release.manifest.json` and signed with a 64-byte **Ed25519** publisher signature (`release.manifest.sig`).
- The installer verifies HTTPS transport, Ed25519 signature, monotonic anti-rollback `sequence`, file size, and SHA-256 digests before atomic installation.
- Sensitive server-side source code and private keys are **never** published to public repositories.

## Reporting a Vulnerability
If you discover a security vulnerability in OZPanel, please report it privately to **Chương Minh® Studio**:
- Email: `chuongmerchant@gmail.com`
- Please include steps to reproduce, affected version (`oz --version`), and potential impact.
- We acknowledge security reports promptly and coordinate patched releases with signed manifests.

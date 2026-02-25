# Secure Data & Identity Manager (Python) 



A desktop application designed for secure customer data management, featuring symmetric encryption, binary data (BLOB) handling, and XML serialization.

## Engineering Highlights
- **Symmetric Encryption:** Utilizes `cryptography.fernet` to ensure sensitive data (Emails) is never stored in plain text.
- **Relational Data Storage:** Implements SQLite with automatic schema generation and data integrity checks.
- **Advanced Data Types:** Handles binary image data (BLOB) for local storage within the database file.
- **Data Serialization:** Features an XML generation engine to export records into standardized machine-readable formats.

## Tech Stack
- **Python 3.x**
- **Tkinter** (GUI Framework)
- **SQLite3** (Database)
- **Pillow** (Image Processing)
- **Fernet** (Encryption)

## Security Features
- **Regex Validation:** Strict validation for emails and 10-digit phone numbers.
- **Key-Based Access:** Requires a `secret.key` file for data decryption; without it, the database is unreadable.
- **macOS Patching:** Implemented parent-window logic to prevent native NSInvalidArgumentException crashes in Tkinter.

## How to Run
1. **Install Dependencies:**
   ```bash
   pip install cryptography Pillow

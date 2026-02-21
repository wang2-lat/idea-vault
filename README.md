# idea-vault

Protect your startup ideas with timestamped proof and controlled sharing.

## Problem

Entrepreneurs want to share their product progress, technical solutions, and pricing strategies online to gain attention and feedback, but fear being copied by well-funded teams who can execute faster. Even worse, some see their business models directly copied by friends or competitors, watching helplessly as market share is stolen.

## Solution

idea-vault provides:
- **Timestamped proof**: Generate cryptographic hash proof of your idea's creation time
- **Auto-sanitization**: Automatically hide sensitive technical and pricing details
- **Trust circle**: Control who can see the full version

## Installation


## Usage

### Add a new idea

### List all ideas

### Show idea (sanitized version)

### Show full version

### Generate proof certificate

### Manage trust circle

### Generate shareable version

## How It Works

1. **Timestamped Proof**: When you add an idea, the system generates a SHA-256 hash of your content + timestamp. This proves you had the idea at that specific time.

2. **Auto-Sanitization**: Keywords like "price", "pricing", "$", "algorithm", "secret" trigger automatic redaction in the sanitized version.

3. **Trust Circle**: Manage who you trust to see full versions of your ideas.

## Data Storage

All data is stored locally in `~/.idea-vault/`:
- `ideas.json`: Your ideas with full and sanitized versions
- `trust.json`: Your trust circle
- `keys/`: Cryptographic keys (future feature)

## Security Note

This tool provides timestamped proof and basic sanitization. For legal protection, consult with an intellectual property attorney.
pip install -r requirements.txt
python main.py add --title "My Idea" --content "Full description..."
python main.py list
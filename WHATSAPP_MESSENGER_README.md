# WhatsApp Messenger - Standalone System

## Overview

The WhatsApp Messenger is a standalone application that handles WhatsApp messaging separately from the main Kitchen Dashboard application. This architecture provides better reliability, performance, and error isolation.

## Architecture

### Components

1. **Kitchen Dashboard App** - Logs messages to shared JSON file
2. **WhatsApp Message Logger** - Handles structured message logging with file locking
3. **Standalone WhatsApp Messenger** - Processes messages and sends via WhatsApp Web
4. **Shared JSON File** - Communication bridge between applications

### Benefits

- ✅ **Better Reliability** - WhatsApp issues don't crash the main application
- ✅ **Improved Performance** - Main app runs faster without WhatsApp dependencies
- ✅ **Error Isolation** - WhatsApp problems are contained in separate process
- ✅ **Message Persistence** - Messages are never lost, even if WhatsApp is down
- ✅ **Independent Scaling** - Can run messenger on different schedule or machine
- ✅ **Easier Debugging** - WhatsApp issues can be debugged separately

## Installation

### Prerequisites

- Python 3.8 or later
- PySide6 (for GUI version)
- Selenium and WebDriver Manager (for WhatsApp Web integration)

### Install Dependencies

```bash
pip install selenium webdriver-manager PySide6
```

## Usage

### Option 1: GUI Version (Recommended)

**Windows:**
```cmd
start_whatsapp_messenger.bat
```

**Linux/Mac:**
```bash
chmod +x start_whatsapp_messenger.sh
./start_whatsapp_messenger.sh
```

**Manual:**
```bash
python whatsapp_messenger_gui.py
```

### Option 2: Command Line Version

**Basic Usage:**
```bash
python whatsapp_messenger.py
```

**Show Status:**
```bash
python whatsapp_messenger.py --status
```

**Test Connection:**
```bash
python whatsapp_messenger.py --test
```

**Custom Configuration:**
```bash
python whatsapp_messenger.py --config my_config.json --messages my_messages.json
```

## Configuration

### Message File Structure

The shared `whatsapp_messages.json` file contains:

```json
{
  "messages": [
    {
      "id": "unique_message_id",
      "timestamp": "2025-06-20T14:30:00Z",
      "message_type": "low_stock|cleaning_reminder|gas_warning|packing_materials",
      "content": "Raw message content with emojis 🚨📦",
      "sanitized_content": "Sanitized message for WhatsApp [URGENT][PACKAGE]",
      "priority": "CRITICAL|HIGH|MEDIUM|LOW",
      "sent_status": "pending|sent|failed|retry",
      "retry_count": 0,
      "max_retries": 3,
      "created_by": "kitchen_app",
      "error_message": null
    }
  ],
  "last_updated": "2025-06-20T14:30:00Z",
  "version": "1.0"
}
```

### Configuration File

The `whatsapp_config.json` file contains:

```json
{
  "messenger_settings": {
    "target_group": "Abiram's Kitchen",
    "check_interval_seconds": 30,
    "max_retries": 3,
    "retry_delay_seconds": 60,
    "connection_timeout_seconds": 300,
    "message_batch_size": 5,
    "priority_order": ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
  },
  "notification_settings": {
    "low_stock_enabled": true,
    "cleaning_reminders_enabled": true,
    "packing_materials_enabled": true,
    "gas_level_warnings_enabled": true,
    "last_notification_times": {}
  }
}
```

## Message Types

### Low Stock Alerts
- **Type:** `low_stock`
- **Priority:** `HIGH` (low stock) or `CRITICAL` (out of stock)
- **Cooldown:** 2 hours
- **Triggers:** When inventory falls below reorder level

### Cleaning Reminders
- **Type:** `cleaning_reminder`
- **Priority:** `MEDIUM`
- **Cooldown:** 12 hours
- **Triggers:** When cleaning tasks are due today

### Packing Material Alerts
- **Type:** `packing_materials`
- **Priority:** `HIGH` (low stock) or `CRITICAL` (out of stock)
- **Cooldown:** 4 hours
- **Triggers:** When packing materials fall below minimum stock

### Gas Level Warnings
- **Type:** `gas_warning`
- **Priority:** `HIGH` (3 days remaining) or `CRITICAL` (1 day remaining)
- **Cooldown:** 12 hours (warning) or 6 hours (critical)
- **Triggers:** When gas cylinder is running low

## Troubleshooting

### Common Issues

**1. WhatsApp Web Connection Failed**
- Ensure Chrome browser is installed
- Check internet connection
- Try running the test connection command
- Verify WhatsApp Web is accessible in browser

**2. Target Group Not Found**
- Verify the group name "Abiram's Kitchen" exists in WhatsApp
- Check that the WhatsApp account has access to the group
- Ensure group name spelling is exact

**3. Messages Not Being Sent**
- Check the messenger status in GUI
- Verify WhatsApp Web connection
- Check message file permissions
- Review logs for error messages

**4. File Locking Issues**
- Ensure only one messenger instance is running
- Check file permissions on message and config files
- Restart the messenger if file locks persist

### Log Files

- **Messenger Logs:** `whatsapp_messenger.log`
- **Kitchen App Logs:** Check the main application logs
- **GUI Logs:** Displayed in the Logs tab of the GUI

### Debug Mode

For detailed debugging, modify the logging level in the messenger:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Integration with Kitchen Dashboard

### Enabling Integrated WhatsApp

To re-enable integrated WhatsApp in the main application:

1. Open `kitchen_app.py`
2. Change `self.WHATSAPP_ENABLED = False` to `self.WHATSAPP_ENABLED = True`
3. Restart the Kitchen Dashboard application

### Message Flow

1. **Kitchen Dashboard** detects data changes (inventory, cleaning, etc.)
2. **Message Logger** evaluates conditions and logs messages to JSON file
3. **Standalone Messenger** reads pending messages from JSON file
4. **WhatsApp Web Driver** sends messages to "Abiram's Kitchen" group
5. **Status Updates** are written back to JSON file

## Security Considerations

- Message files contain business-sensitive information
- Ensure proper file permissions on shared JSON files
- Consider encrypting message content for sensitive deployments
- WhatsApp Web session should be secured with appropriate browser settings

## Performance

- **Message Processing:** Up to 5 messages per batch
- **Check Interval:** 30 seconds (configurable)
- **Retry Logic:** Exponential backoff with maximum 3 retries
- **File Locking:** Prevents data corruption during concurrent access

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review log files for error messages
3. Test WhatsApp connection using the test command
4. Verify configuration file settings
5. Ensure all dependencies are properly installed

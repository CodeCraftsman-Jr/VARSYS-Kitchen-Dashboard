# WhatsApp Automated Notifications System

## Overview

The VARSYS Kitchen Dashboard now includes a comprehensive automated notification system that sends real-time WhatsApp messages to the 'Abiram's Kitchen' group for various kitchen management scenarios.

## Features Implemented

### 1. 📦 Low Stock Notifications
- **Trigger**: When inventory items fall below their reorder level
- **Real-time**: Notifications sent immediately when stock levels change
- **Message includes**: Item name, current quantity, reorder level, unit
- **Special handling**: Different messages for low stock vs. completely out of stock

### 2. 🧹 Cleaning Task Reminders
- **Trigger**: When cleaning tasks are due today or overdue
- **Frequency**: Daily check with 12-hour cooldown
- **Message includes**: Task name, assigned person, location, due date
- **Batch support**: Multiple tasks combined into a single message

### 3. 📦 Packing Materials Alerts
- **Trigger**: When packing materials fall below minimum stock levels
- **Real-time**: Immediate alerts when materials are used
- **Message includes**: Material name, current stock, minimum required, unit
- **Critical alerts**: Special handling for completely out-of-stock materials

### 4. ⛽ Gas Level Warnings
- **Trigger**: When gas cylinders are running low
- **Thresholds**: Warning at 3 days, Critical at 1 day remaining
- **Message includes**: Cylinder ID, days remaining, urgency level
- **Frequency**: 12-hour cooldown for warnings, 6-hour for critical alerts

## How It Works

### Automated Monitoring
- Background thread runs every 30 minutes (configurable)
- Monitors all data sources for changes
- Sends notifications based on predefined thresholds
- Includes cooldown periods to prevent spam

### Real-time Triggers
- Integrated with data update events
- Immediate notifications when critical changes occur
- Smart detection of inventory, cleaning, packing, and gas updates

### Message Format
All messages include:
- Clear emoji indicators
- Relevant details (quantities, dates, assignments)
- Timestamp
- Appropriate urgency level

## User Interface

### WhatsApp Settings Tab
Located in Settings → 📱 WhatsApp, the interface includes:

1. **Connection Status**: Shows if WhatsApp Web is connected
2. **Message Composer**: Enhanced input with character counter and templates
3. **Quick Actions**: 
   - 🔍 Find Abiram's Kitchen
   - 🎯 Send to Abiram's Kitchen
   - 📝 Quick Templates
4. **Startup Automation**: Enable/disable automatic connection
5. **Notification Testing**: 🧪 Test Notifications button
6. **Status Monitoring**: Real-time status of the notification system

### Test Interface
The test interface allows you to:
- Send sample notifications for each type
- Verify WhatsApp connection
- Check system status
- Test message delivery

## Configuration

### Notification Settings
Access via Settings → 📱 WhatsApp → ⚙️ Settings:

- **Enable/Disable**: Individual notification types
- **Check Interval**: How often to monitor (5-120 minutes)
- **Cooldown Periods**: Prevent notification spam
- **Thresholds**: Customizable alert levels

### Default Settings
- Low Stock: Enabled, 4-hour cooldown
- Cleaning Tasks: Enabled, 12-hour cooldown
- Packing Materials: Enabled, 4-hour cooldown
- Gas Warnings: Enabled, 6-12 hour cooldown
- Check Interval: 30 minutes

## Setup Instructions

### 1. Initial Setup
1. Navigate to Settings → 📱 WhatsApp
2. Click "Connect to WhatsApp Web"
3. Scan QR code in browser
4. Click "🔍 Find Abiram's Kitchen" to verify group access
5. Enable "🔄 Enable WhatsApp Automation"

### 2. Testing
1. Click "🧪 Test Notifications"
2. Test each notification type
3. Verify messages appear in 'Abiram's Kitchen' group
4. Check status indicators

### 3. Monitoring
- Green status = System active and working
- Yellow status = System active but issues detected
- Red status = System inactive or errors

## Message Examples

### Low Stock Alert
```
⚠️ LOW STOCK ALERT ⚠️

Item: Premium Oil
Current Stock: 2 liters
Reorder Level: 10 liters

📋 Please consider restocking soon.
📅 2025-06-20 14:30
```

### Cleaning Reminder
```
🧹 CLEANING TASK REMINDER 🧹

Task: Clean Kitchen Floor
Assigned to: Kitchen Staff
Location: Main Kitchen
Due Date: 2025-06-20

⏰ Please complete this task today!
📅 2025-06-20 14:30
```

### Packing Material Alert
```
📦 PACKING MATERIAL LOW STOCK 📦

Material: Food Containers
Current Stock: 5 pieces
Minimum Required: 20 pieces

⚠️ Please restock soon to avoid order delays!
📅 2025-06-20 14:30
```

### Gas Warning
```
🔥 CRITICAL GAS ALERT 🔥

Cylinder ID: CYL-001
Days Remaining: 1

🚨 URGENT: Gas will run out very soon!
🛒 Order new cylinder IMMEDIATELY!
⚠️ Kitchen operations may stop!

📅 2025-06-20 14:30
```

## Troubleshooting

### Common Issues

1. **No notifications sent**
   - Check WhatsApp Web connection
   - Verify 'Abiram's Kitchen' group exists
   - Test with 🧪 Test Notifications

2. **Too many notifications**
   - Adjust cooldown periods in settings
   - Check thresholds are appropriate
   - Disable specific notification types if needed

3. **Missing notifications**
   - Verify monitoring is active (green status)
   - Check data is being updated correctly
   - Force check with 🔄 Force Check button

### Error Messages
- "WhatsApp Web is not connected" → Reconnect to WhatsApp Web
- "Abiram's Kitchen group not found" → Verify group name and access
- "Automated notifications not available" → Check system initialization

## Technical Details

### Files Modified/Created
- `modules/whatsapp_automated_notifications.py` - Main notification system
- `modules/whatsapp_integration.py` - Enhanced UI and testing
- `kitchen_app.py` - Integration and data change triggers
- `test_whatsapp_notifications.py` - Test suite

### Integration Points
- Inventory updates trigger stock checks
- Cleaning task changes trigger reminder checks
- Packing material updates trigger alert checks
- Gas level changes trigger warning checks

### Data Sources
- `data/inventory.csv` - Inventory levels and reorder points
- `data/cleaning_maintenance.csv` - Cleaning tasks and schedules
- `data/packing_materials.csv` - Packing material stock levels
- `data/gas_tracking.csv` - Gas cylinder information

## Support

For issues or questions:
1. Check the notification status in WhatsApp settings
2. Use the test interface to verify functionality
3. Review error messages in the application logs
4. Ensure all data files are properly formatted

The system is designed to be robust and self-monitoring, with comprehensive error handling and user feedback.

#!/usr/bin/env python3
"""
Real-time Notification Streaming System
WebSocket-based real-time notification delivery and synchronization
"""

import sys
import os
import json
import asyncio
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import weakref

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    print("⚠️ websockets not available - using simulation mode")
    WEBSOCKETS_AVAILABLE = False
    WebSocketServerProtocol = object

from modules.enhanced_notification_system import get_notification_manager

class StreamingEvent(Enum):
    """Types of streaming events"""
    NOTIFICATION_CREATED = "notification_created"
    NOTIFICATION_READ = "notification_read"
    NOTIFICATION_DISMISSED = "notification_dismissed"
    NOTIFICATION_UPDATED = "notification_updated"
    CLIENT_CONNECTED = "client_connected"
    CLIENT_DISCONNECTED = "client_disconnected"
    HEARTBEAT = "heartbeat"
    SYNC_REQUEST = "sync_request"
    BULK_UPDATE = "bulk_update"

@dataclass
class StreamingClient:
    """Represents a connected streaming client"""
    client_id: str
    websocket: Optional[WebSocketServerProtocol]
    user_id: str
    device_type: str
    connected_at: datetime
    last_heartbeat: datetime
    subscriptions: Set[str]
    is_active: bool = True

@dataclass
class StreamingMessage:
    """Message structure for streaming"""
    event_type: StreamingEvent
    data: Dict[str, Any]
    timestamp: datetime
    client_id: Optional[str] = None
    broadcast: bool = False

class NotificationStreamer:
    """Real-time notification streaming server"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.clients: Dict[str, StreamingClient] = {}
        self.notification_manager = get_notification_manager()
        self.message_queue = asyncio.Queue() if WEBSOCKETS_AVAILABLE else []
        self.is_running = False
        self.server = None
        self.stats = {
            'total_connections': 0,
            'active_connections': 0,
            'messages_sent': 0,
            'messages_received': 0,
            'uptime_start': datetime.now()
        }
        
        # Event handlers
        self.event_handlers: Dict[StreamingEvent, List[Callable]] = {}
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Setup default event handlers"""
        self.add_event_handler(StreamingEvent.NOTIFICATION_CREATED, self._handle_notification_created)
        self.add_event_handler(StreamingEvent.CLIENT_CONNECTED, self._handle_client_connected)
        self.add_event_handler(StreamingEvent.CLIENT_DISCONNECTED, self._handle_client_disconnected)
        self.add_event_handler(StreamingEvent.HEARTBEAT, self._handle_heartbeat)
        self.add_event_handler(StreamingEvent.SYNC_REQUEST, self._handle_sync_request)
    
    def add_event_handler(self, event_type: StreamingEvent, handler: Callable):
        """Add event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def start_server(self):
        """Start the WebSocket server"""
        if not WEBSOCKETS_AVAILABLE:
            print("⚠️ WebSocket server not available - running in simulation mode")
            self._run_simulation()
            return
        
        try:
            self.is_running = True
            print(f"🚀 Starting notification streaming server on {self.host}:{self.port}")
            
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
                ping_interval=30,
                ping_timeout=10
            )
            
            print(f"✅ Notification streaming server started")
            
            # Start background tasks
            asyncio.create_task(self._message_processor())
            asyncio.create_task(self._heartbeat_monitor())
            asyncio.create_task(self._cleanup_task())
            
            # Keep server running
            await self.server.wait_closed()
            
        except Exception as e:
            print(f"❌ Server error: {e}")
            self.is_running = False
    
    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle new client connection"""
        client_id = str(uuid.uuid4())
        
        try:
            # Initial handshake
            await websocket.send(json.dumps({
                'type': 'connection_established',
                'client_id': client_id,
                'server_time': datetime.now().isoformat()
            }))
            
            # Wait for client info
            client_info_raw = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            client_info = json.loads(client_info_raw)
            
            # Create client record
            client = StreamingClient(
                client_id=client_id,
                websocket=websocket,
                user_id=client_info.get('user_id', 'anonymous'),
                device_type=client_info.get('device_type', 'unknown'),
                connected_at=datetime.now(),
                last_heartbeat=datetime.now(),
                subscriptions=set(client_info.get('subscriptions', []))
            )
            
            self.clients[client_id] = client
            self.stats['total_connections'] += 1
            self.stats['active_connections'] += 1
            
            # Emit connection event
            await self._emit_event(StreamingEvent.CLIENT_CONNECTED, {
                'client_id': client_id,
                'user_id': client.user_id,
                'device_type': client.device_type
            })
            
            print(f"📱 Client connected: {client_id} ({client.user_id})")
            
            # Handle client messages
            async for message in websocket:
                await self._handle_client_message(client_id, message)
                
        except websockets.exceptions.ConnectionClosed:
            print(f"📱 Client disconnected: {client_id}")
        except asyncio.TimeoutError:
            print(f"⏰ Client handshake timeout: {client_id}")
        except Exception as e:
            print(f"❌ Client error: {e}")
        finally:
            # Cleanup client
            if client_id in self.clients:
                self.clients[client_id].is_active = False
                del self.clients[client_id]
                self.stats['active_connections'] -= 1
                
                await self._emit_event(StreamingEvent.CLIENT_DISCONNECTED, {
                    'client_id': client_id
                })
    
    async def _handle_client_message(self, client_id: str, message: str):
        """Handle message from client"""
        try:
            data = json.loads(message)
            event_type = StreamingEvent(data.get('type'))
            
            self.stats['messages_received'] += 1
            
            # Update client heartbeat
            if client_id in self.clients:
                self.clients[client_id].last_heartbeat = datetime.now()
            
            # Emit event
            await self._emit_event(event_type, data.get('data', {}), client_id)
            
        except Exception as e:
            print(f"❌ Error handling client message: {e}")
    
    async def _emit_event(self, event_type: StreamingEvent, data: Dict[str, Any], 
                         client_id: Optional[str] = None, broadcast: bool = False):
        """Emit an event to handlers and clients"""
        message = StreamingMessage(
            event_type=event_type,
            data=data,
            timestamp=datetime.now(),
            client_id=client_id,
            broadcast=broadcast
        )
        
        # Handle event internally
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    await handler(message)
                except Exception as e:
                    print(f"❌ Event handler error: {e}")
        
        # Queue for client delivery
        if WEBSOCKETS_AVAILABLE:
            await self.message_queue.put(message)
        else:
            self.message_queue.append(message)
    
    async def _message_processor(self):
        """Process outgoing messages to clients"""
        while self.is_running:
            try:
                if WEBSOCKETS_AVAILABLE:
                    message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                else:
                    if self.message_queue:
                        message = self.message_queue.pop(0)
                    else:
                        await asyncio.sleep(0.1)
                        continue
                
                await self._deliver_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"❌ Message processor error: {e}")
    
    async def _deliver_message(self, message: StreamingMessage):
        """Deliver message to appropriate clients"""
        message_data = {
            'type': message.event_type.value,
            'data': message.data,
            'timestamp': message.timestamp.isoformat()
        }
        
        message_json = json.dumps(message_data)
        
        if message.broadcast:
            # Send to all clients
            for client in list(self.clients.values()):
                await self._send_to_client(client, message_json)
        elif message.client_id and message.client_id in self.clients:
            # Send to specific client
            client = self.clients[message.client_id]
            await self._send_to_client(client, message_json)
        else:
            # Send to all subscribed clients
            for client in list(self.clients.values()):
                if self._client_should_receive(client, message):
                    await self._send_to_client(client, message_json)
    
    async def _send_to_client(self, client: StreamingClient, message: str):
        """Send message to a specific client"""
        if not client.is_active or not client.websocket:
            return
        
        try:
            await client.websocket.send(message)
            self.stats['messages_sent'] += 1
        except websockets.exceptions.ConnectionClosed:
            client.is_active = False
        except Exception as e:
            print(f"❌ Error sending to client {client.client_id}: {e}")
            client.is_active = False
    
    def _client_should_receive(self, client: StreamingClient, message: StreamingMessage) -> bool:
        """Determine if client should receive message"""
        # Check subscriptions
        if message.event_type.value in client.subscriptions:
            return True
        
        # Default events all clients receive
        default_events = {
            StreamingEvent.NOTIFICATION_CREATED,
            StreamingEvent.HEARTBEAT
        }
        
        return message.event_type in default_events
    
    async def _heartbeat_monitor(self):
        """Monitor client heartbeats"""
        while self.is_running:
            try:
                current_time = datetime.now()
                timeout_threshold = current_time - timedelta(minutes=2)
                
                # Check for timed out clients
                timed_out_clients = []
                for client_id, client in self.clients.items():
                    if client.last_heartbeat < timeout_threshold:
                        timed_out_clients.append(client_id)
                
                # Remove timed out clients
                for client_id in timed_out_clients:
                    if client_id in self.clients:
                        print(f"⏰ Client timeout: {client_id}")
                        self.clients[client_id].is_active = False
                        del self.clients[client_id]
                        self.stats['active_connections'] -= 1
                
                # Send heartbeat to all clients
                await self._emit_event(StreamingEvent.HEARTBEAT, {
                    'server_time': current_time.isoformat(),
                    'active_clients': len(self.clients)
                }, broadcast=True)
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                print(f"❌ Heartbeat monitor error: {e}")
                await asyncio.sleep(30)
    
    async def _cleanup_task(self):
        """Periodic cleanup task"""
        while self.is_running:
            try:
                # Clean up inactive clients
                inactive_clients = [
                    client_id for client_id, client in self.clients.items()
                    if not client.is_active
                ]
                
                for client_id in inactive_clients:
                    if client_id in self.clients:
                        del self.clients[client_id]
                        self.stats['active_connections'] -= 1
                
                await asyncio.sleep(60)  # Cleanup every minute
                
            except Exception as e:
                print(f"❌ Cleanup task error: {e}")
                await asyncio.sleep(60)
    
    # Event handlers
    async def _handle_notification_created(self, message: StreamingMessage):
        """Handle notification created event"""
        print(f"📢 Broadcasting notification: {message.data.get('title', 'Unknown')}")
    
    async def _handle_client_connected(self, message: StreamingMessage):
        """Handle client connected event"""
        print(f"👋 Client connected: {message.data.get('user_id', 'Unknown')}")
    
    async def _handle_client_disconnected(self, message: StreamingMessage):
        """Handle client disconnected event"""
        print(f"👋 Client disconnected: {message.data.get('client_id', 'Unknown')}")
    
    async def _handle_heartbeat(self, message: StreamingMessage):
        """Handle heartbeat event"""
        # Update client heartbeat timestamp
        if message.client_id and message.client_id in self.clients:
            self.clients[message.client_id].last_heartbeat = datetime.now()
    
    async def _handle_sync_request(self, message: StreamingMessage):
        """Handle sync request from client"""
        if message.client_id and message.client_id in self.clients:
            # Send recent notifications to client
            notifications = self.notification_manager.get_notifications()
            recent_notifications = notifications[-50:]  # Last 50 notifications
            
            await self._emit_event(StreamingEvent.BULK_UPDATE, {
                'notifications': recent_notifications,
                'total_count': len(notifications)
            }, client_id=message.client_id)
    
    def _run_simulation(self):
        """Run simulation mode without WebSockets"""
        print("🎭 Running streaming simulation...")
        
        # Simulate clients
        for i in range(3):
            client_id = f"sim_client_{i+1}"
            client = StreamingClient(
                client_id=client_id,
                websocket=None,
                user_id=f"user_{i+1}",
                device_type="simulation",
                connected_at=datetime.now(),
                last_heartbeat=datetime.now(),
                subscriptions={"notification_created", "heartbeat"}
            )
            self.clients[client_id] = client
            self.stats['total_connections'] += 1
            self.stats['active_connections'] += 1
        
        print(f"📱 Simulated {len(self.clients)} clients connected")
        
        # Simulate some events
        events = [
            (StreamingEvent.NOTIFICATION_CREATED, {'title': 'Test Notification 1', 'category': 'info'}),
            (StreamingEvent.NOTIFICATION_CREATED, {'title': 'Test Notification 2', 'category': 'warning'}),
            (StreamingEvent.HEARTBEAT, {'server_time': datetime.now().isoformat()})
        ]
        
        for event_type, data in events:
            print(f"📡 Simulating event: {event_type.value}")
            self.stats['messages_sent'] += len(self.clients)
    
    def get_streaming_stats(self) -> Dict[str, Any]:
        """Get streaming statistics"""
        uptime = datetime.now() - self.stats['uptime_start']
        
        return {
            'server_status': 'running' if self.is_running else 'stopped',
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': str(uptime).split('.')[0],
            'total_connections': self.stats['total_connections'],
            'active_connections': self.stats['active_connections'],
            'messages_sent': self.stats['messages_sent'],
            'messages_received': self.stats['messages_received'],
            'connected_clients': [
                {
                    'client_id': client.client_id,
                    'user_id': client.user_id,
                    'device_type': client.device_type,
                    'connected_duration': str(datetime.now() - client.connected_at).split('.')[0]
                }
                for client in self.clients.values()
            ]
        }
    
    async def broadcast_notification(self, notification: Dict[str, Any]):
        """Broadcast a notification to all clients"""
        await self._emit_event(StreamingEvent.NOTIFICATION_CREATED, notification, broadcast=True)
    
    async def stop_server(self):
        """Stop the streaming server"""
        self.is_running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        print("🛑 Streaming server stopped")

def create_streaming_demo():
    """Create streaming demo"""
    print("📡 Real-time Notification Streaming Demo")
    print("=" * 60)
    
    streamer = NotificationStreamer()
    
    if WEBSOCKETS_AVAILABLE:
        print("🚀 WebSocket streaming available")
        
        # In a real application, you would run this in a separate thread or process
        print("💡 To test WebSocket streaming:")
        print("   1. Run this script in a separate terminal")
        print("   2. Connect clients to ws://localhost:8765")
        print("   3. Send notifications through the system")
        
        # For demo, just show the simulation
        streamer._run_simulation()
    else:
        print("🎭 Running in simulation mode")
        streamer._run_simulation()
    
    # Show statistics
    stats = streamer.get_streaming_stats()
    
    print(f"\n📊 Streaming Statistics:")
    print(f"   • Server Status: {stats['server_status']}")
    print(f"   • Active Connections: {stats['active_connections']}")
    print(f"   • Total Connections: {stats['total_connections']}")
    print(f"   • Messages Sent: {stats['messages_sent']}")
    print(f"   • Messages Received: {stats['messages_received']}")
    
    if stats['connected_clients']:
        print(f"   • Connected Clients:")
        for client in stats['connected_clients']:
            print(f"     - {client['user_id']} ({client['device_type']}) - {client['connected_duration']}")
    
    print(f"\n✅ Real-time streaming demo completed!")
    print(f"📡 Features: WebSocket streaming, real-time sync, heartbeat monitoring")
    print(f"🔄 Capabilities: Multi-client support, event broadcasting, automatic cleanup")
    
    return streamer

if __name__ == "__main__":
    create_streaming_demo()

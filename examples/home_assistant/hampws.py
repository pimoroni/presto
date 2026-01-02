import usocket as socket
import json
import urandom as random
import ubinascii as base64
import ustruct as struct
import uhashlib as hashlib
import uselect

class HAMPWS:
    GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    
    def __init__(self, host, token):
        """Initialize Home Assistant MicroPython Web Socket"""
        print("Initializing HAMPWS...")
        self.host = host.replace('http://', '').split(':')[0]
        print(f"Parsed host: {self.host}")
        self.token = token
        self.socket = None
        self.connected = False
        self.authenticated = False
        self.message_id = 1
        self.poller = None

    def _setup_poller(self):
        """Setup the socket poller"""
        self.poller = uselect.poll()
        self.poller.register(self.socket, uselect.POLLIN)

    def _generate_key(self):
        """Generate a random 16-byte key for the WebSocket handshake"""
        random_bytes = bytes(random.getrandbits(8) for _ in range(16))
        return base64.b2a_base64(random_bytes).decode().strip()
        
    def _create_accept_key(self, key):
        """Create the accept key for WebSocket handshake verification"""
        accept_key = key + self.GUID
        sha1 = hashlib.sha1(accept_key.encode())
        return base64.b2a_base64(sha1.digest()).decode().strip()
        
    def _send_frame(self, data, opcode=0x1):
        """Send a WebSocket frame"""
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        length = len(data)
        frame = bytearray()
        
        # Fin bit and opcode
        frame.append(0x80 | opcode)
        
        # Payload length and masking bit
        if length < 126:
            frame.append(0x80 | length)
        elif length < 65536:
            frame.append(0x80 | 126)
            frame.extend(struct.pack('>H', length))
        else:
            frame.append(0x80 | 127)
            frame.extend(struct.pack('>Q', length))
            
        # Masking key
        mask = bytes(random.getrandbits(8) for _ in range(4))
        frame.extend(mask)
        
        # Masked payload
        masked_data = bytearray(length)
        for i in range(length):
            masked_data[i] = data[i] ^ mask[i % 4]
            
        frame.extend(masked_data)
        total_sent = 0
        while total_sent < len(frame):
            sent = self.socket.send(frame[total_sent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += sent
        
    def _recv_frame(self, blocking=False):
        """Receive a WebSocket frame
        Args:
            blocking (bool): If True, wait for data. If False, return None if no data available
        """
        try:
            # Check if data is available (only in non-blocking mode)
            if not blocking and not self.poller.poll(0):
                return None
                
            # Read header
            header = self.socket.recv(2)
            if not header or len(header) < 2:
                return None
                
            # Parse header
            fin = (header[0] & 0x80) == 0x80
            opcode = header[0] & 0x0F
            masked = (header[1] & 0x80) == 0x80
            length = header[1] & 0x7F
            
            # Extended payload length
            if length == 126:
                length_bytes = self.socket.recv(2)
                if len(length_bytes) < 2:
                    return None
                length = struct.unpack('>H', length_bytes)[0]
            elif length == 127:
                length_bytes = self.socket.recv(8)
                if len(length_bytes) < 8:
                    return None
                length = struct.unpack('>Q', length_bytes)[0]
                
            # Masking key if present
            if masked:
                mask = self.socket.recv(4)
                if len(mask) < 4:
                    return None
                
            # Read payload
            payload = bytearray()
            remaining = length
            while remaining > 0:
                chunk = self.socket.recv(min(remaining, 4096))
                if not chunk:
                    return None
                payload.extend(chunk)
                remaining -= len(chunk)
            
            # Unmask if needed
            if masked:
                unmasked = bytearray(length)
                for i in range(length):
                    unmasked[i] = payload[i] ^ mask[i % 4]
                payload = unmasked
                
            # Handle control frames
            if opcode == 0x8:  # Close
                self.connected = False
                return None
            elif opcode == 0x9:  # Ping
                self._send_frame(payload, 0xA)  # Send Pong
                return self._recv_frame(blocking)  # Get next message
            elif opcode == 0xA:  # Pong
                return self._recv_frame(blocking)  # Get next message
                
            return payload.decode('utf-8')
            
        except Exception as e:
            print(f"Error receiving frame: {e}")
            self.connected = False
            return None
            
    def connect(self):
        """Establish WebSocket connection with Home Assistant"""
        try:
            print(f"Starting connection to {self.host}...")
            print("Creating socket...")
            self.socket = socket.socket()
            
            print("Getting address info...")
            try:
                addr_info = socket.getaddrinfo(self.host, 8123)
                print(f"Address info: {addr_info}")
                addr = addr_info[0][-1]
                print(f"Using address: {addr}")
            except Exception as e:
                print(f"Error getting address info: {e}")
                return False
                
            print("Attempting socket connection...")
            try:
                self.socket.connect(addr)
                print("Socket connected successfully")
            except Exception as e:
                print(f"Connection error: {e}")
                return False
            
            # Set up the poller after connection
            self._setup_poller()
            
            # Generate WebSocket key
            key = self._generate_key()
            
            # Send WebSocket upgrade request
            request = (
                f"GET /api/websocket HTTP/1.1\r\n"
                f"Host: {self.host}:8123\r\n"
                "Upgrade: websocket\r\n"
                "Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {key}\r\n"
                "Sec-WebSocket-Version: 13\r\n"
                "\r\n"
            )
            
            print("Sending upgrade request...")
            total_sent = 0
            request_bytes = request.encode()
            while total_sent < len(request_bytes):
                sent = self.socket.send(request_bytes[total_sent:])
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent += sent
            
            # Read response headers
            print("Reading response...")
            response = ""
            while True:
                chunk = self.socket.recv(4096)
                if not chunk:
                    print("No response received")
                    return False
                response += chunk.decode()
                if "\r\n\r\n" in response:
                    break
                    
            # Verify upgrade response
            if "HTTP/1.1 101" not in response:
                print("Invalid upgrade response:", response)
                return False
                    
            self.connected = True
            print("WebSocket connection established")
            
            # Use blocking reads during authentication
            # Wait for auth required message
            print("Waiting for auth request...")
            auth_req = self._recv_frame(blocking=True)
            if not auth_req:
                print("No auth request received")
                return False
            print("Auth request received:", auth_req)
                
            # Authenticate
            print("Sending auth message...")
            auth_msg = {
                "type": "auth",
                "access_token": self.token
            }
            self._send_frame(json.dumps(auth_msg))
            
            # Wait for auth response
            print("Waiting for auth response...")
            response = self._recv_frame(blocking=True)  # Use blocking read for auth
            if response:
                resp_data = json.loads(response)
                if resp_data.get('type') == 'auth_ok':
                    self.authenticated = True
                    print("Authentication successful")
                    return True
                print("Authentication failed:", resp_data.get('message', 'Unknown error'))
                    
            return False
            
        except Exception as e:
            print(f"Connection error: {e}")
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            self.socket = None
            self.connected = False
            return False

    def read_message(self):
        """Read next message from WebSocket, non-blocking"""
        try:
            if not self.connected:
                return None
                
            message = self._recv_frame(blocking=False)
            if message:
                return json.loads(message)
            return None
            
        except Exception as e:
            print(f"Read error: {e}")
            self.connected = False
            return None
            
    def call_service(self, domain, service, service_data=None, target=None):
        """Call a Home Assistant service
        
        Args:
            domain: Service domain (e.g. 'light')
            service: Service name (e.g. 'turn_on')
            service_data: Optional service data dictionary
            target: Optional target dictionary (e.g. {"entity_id": "light.kitchen"})
            
        Returns:
            bool: True if successful
        """
        if not self.authenticated:
            print("Not authenticated")
            return False
            
        try:
            msg = {
                "id": self.message_id,
                "type": "call_service",
                "domain": domain,
                "service": service
            }
            if service_data:
                msg["service_data"] = service_data
            if target:
                msg["target"] = target
                
            self._send_frame(json.dumps(msg))
            self.message_id += 1
            
            # Wait for result
            response = self._recv_frame()
            if response:
                resp_data = json.loads(response)
                return resp_data.get('success', False)
                
            return False
            
        except Exception as e:
            print(f"Service call error: {e}")
            return False

    def subscribe_events(self, event_type=None):
        """Subscribe to Home Assistant events
        
        Args:
            event_type: Optional event type to filter (e.g. 'state_changed')
            
        Returns:
            int: Subscription ID if successful, None if failed
        """
        if not self.authenticated:
            print("Not authenticated")
            return None
            
        try:
            msg = {
                "id": self.message_id,
                "type": "subscribe_events",
            }
            if event_type:
                msg["event_type"] = event_type
                
            self._send_frame(json.dumps(msg))
            
            # Wait for result - use blocking read for subscription response
            response = self._recv_frame(blocking=True)
            if response:
                resp_data = json.loads(response)
                if resp_data.get('success', False):
                    sub_id = self.message_id
                    self.message_id += 1
                    print(f"Successfully subscribed to events: {event_type}")
                    return sub_id
                else:
                    print(f"Failed to subscribe: {resp_data.get('error', 'Unknown error')}")
                    
            return None
            
        except Exception as e:
            print(f"Subscribe error: {e}")
            return None
            
    def subscribe_trigger(self, trigger_config):
        """Subscribe to a Home Assistant trigger
        
        Args:
            trigger_config: Trigger configuration dictionary
            
        Returns:
            int: Subscription ID if successful, None if failed
        """
        if not self.authenticated:
            print("Not authenticated")
            return None
            
        try:
            msg = {
                "id": self.message_id,
                "type": "subscribe_trigger",
                "trigger": trigger_config
            }
            self._send_frame(json.dumps(msg))
            
            # Wait for result
            response = self._recv_frame()
            if response:
                resp_data = json.loads(response)
                if resp_data.get('success'):
                    sub_id = self.message_id
                    self.message_id += 1
                    return sub_id
                    
            return None
            
        except Exception as e:
            print(f"Subscribe error: {e}")
            return None

    def get_state(self, entity_id):
        """Get the state of a Home Assistant entity
        
        Args:
            entity_id: The entity ID to get state for (e.g. 'light.kitchen')
            
        Returns:
            dict: Entity state data if successful, None if failed
        """
        if not self.authenticated:
            print("Not authenticated")
            return None
            
        try:
            # Send get_states command for specific entity
            msg_id = self.message_id
            msg = {
                "id": msg_id,
                "type": "get_states"  # Get all states, we'll filter for our entity
            }
            
            print(f"Sending state request for {entity_id}")
            self._send_frame(json.dumps(msg))
            self.message_id += 1
            
            # Wait for result with blocking read
            response = self._recv_frame(blocking=True)
            if response:
                resp_data = json.loads(response)
                print(f"Got response: {resp_data}")  # Debug output
                
                # Check that this is the response to our query
                if resp_data.get('id') == msg_id:
                    if resp_data.get('success') and resp_data.get('result'):
                        # Find our entity in the results
                        for state in resp_data['result']:
                            if state.get('entity_id') == entity_id:
                                print(f"Found state for {entity_id}: {state}")  # Debug output
                                return state
                    else:
                        print(f"Get state error: {resp_data.get('error', 'Unknown error')}")
                        
            return None
            
        except Exception as e:
            print(f"Get state error: {e}")
            return None

    def close(self):
        """Close the WebSocket connection"""
        if self.socket:
            try:
                self._send_frame("", 0x8)  # Send close frame
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False
        self.authenticated = False

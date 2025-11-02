class Memory:
    def __init__(self, start_addr, end_addr):
        self.start_addr = start_addr
        self.end_addr = end_addr
        # Initialize memory as bytes, each storing "00000000" (8-bit binary string)
        self.data = {}
        for i in range(end_addr - start_addr + 1):
            addr = start_addr + i
            self.data[addr] = "00000000"  # 8-bit binary string
    
    def __getitem__(self, addr_str):
        """Get value at address as binary string"""
        if isinstance(addr_str, str):
            addr = int(addr_str, 16)
        else:
            addr = addr_str
        
        if addr < self.start_addr or addr > self.end_addr:
            raise KeyError(f"Address {hex(addr)} out of range")
        
        return self.data[addr]
    
    def __setitem__(self, addr_str, value):
        """Set value at address (accepts string, list, or int)"""
        if isinstance(addr_str, str):
            addr = int(addr_str, 16)
        else:
            addr = addr_str
        
        if addr < self.start_addr or addr > self.end_addr:
            raise KeyError(f"Address {hex(addr)} out of range")
        
        # Convert value to 8-bit binary string
        if isinstance(value, str):
            # If it's already a binary string, pad to 8 bits
            self.data[addr] = value.zfill(8)
        elif isinstance(value, list):
            # If it's a list of bits, join and pad
            self.data[addr] = ''.join(str(bit) for bit in value).zfill(8)
        elif isinstance(value, int):
            # If it's an integer, convert to 8-bit binary
            self.data[addr] = format(value, '08b')
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
    
    def get_bytes(self, addr_str, num_bytes):
        """Get multiple consecutive bytes as binary string"""
        if isinstance(addr_str, str):
            addr = int(addr_str, 16)
        else:
            addr = addr_str
        
        result = ""
        for i in range(num_bytes):
            byte_addr = addr + i
            if byte_addr <= self.end_addr:
                result += self.data.get(byte_addr, "00000000")
            else:
                result += "00000000"
        return result
    
    def set_bytes(self, addr_str, value, num_bytes):
        """Set multiple consecutive bytes from binary string or list"""
        if isinstance(addr_str, str):
            addr = int(addr_str, 16)
        else:
            addr = addr_str
        
        # Convert value to binary string
        if isinstance(value, list):
            binary_str = ''.join(str(bit) for bit in value)
        elif isinstance(value, str):
            binary_str = value
        elif isinstance(value, int):
            binary_str = format(value, f'0{num_bytes*8}b')
        else:
            raise ValueError(f"Unsupported value type: {type(value)}")
        
        # Pad or truncate to correct length
        binary_str = binary_str.zfill(num_bytes * 8)[:num_bytes * 8]
        
        # Store each byte
        for i in range(num_bytes):
            byte_addr = addr + i
            if byte_addr <= self.end_addr:
                start_bit = i * 8
                end_bit = start_bit + 8
                self.data[byte_addr] = binary_str[start_bit:end_bit]
    
    def get_as_list(self, addr_str):
        """Get value as list of bits"""
        return list(self[addr_str])
    
    def get_as_int(self, addr_str):
        """Get value as integer"""
        return int(self[addr_str], 2)
    
    def keys(self):
        """Return all valid addresses as hex strings"""
        return [f"0x{addr:08X}" for addr in range(self.start_addr, self.end_addr + 1)]
    
    def __len__(self):
        """Return number of byte locations"""
        return self.end_addr - self.start_addr + 1
    
    def __contains__(self, addr_str):
        """Check if address is valid"""
        if isinstance(addr_str, str):
            addr = int(addr_str, 16)
        else:
            addr = addr_str
        return self.start_addr <= addr <= self.end_addr

# Create memory from 0x10010000 to 0x10010FFF
MEMORIES = Memory(0x10010000, 0x10010FFF)

# Test different value formats
# print("=== Testing Memory Operations ===")

# # Get 8-bit value (single byte)
# byte_value = MEMORIES.get_bytes("0x10010002", 1)  # Returns "10101010" (8 bits)

# # Get 16-bit value (2 bytes)
# halfword_value = MEMORIES.get_bytes("0x10010002", 2)  # Returns 16-bit string

# # Get 32-bit value (4 bytes)  
# word_value = MEMORIES.get_bytes("0x10010002", 4)  # Returns 32-bit string

# # Get 64-bit value (8 bytes)
# doubleword_value = MEMORIES.get_bytes("0x10010002", 8)  # Returns 64-bit string

# # Set as binary string
# MEMORIES["0x10010000"] = "1101010"
# print(f"Set as string: {MEMORIES['0x10010000']}")

# # Set as list
# MEMORIES["0x10010001"] = [1, 0, 1, 1, 0, 0, 1, 0]
# print(f"Set as list: {MEMORIES['0x10010001']}")

# # Set as integer
# MEMORIES["0x10010002"] = 170  # 0xAA = 10101010
# print(f"Set as int: {MEMORIES['0x10010002']}")

# # Get in different formats
# print(f"As string: {MEMORIES['0x10010000']}")
# print(f"As list: {MEMORIES.get_as_list('0x10010000')}")
# print(f"As int: {MEMORIES.get_as_int('0x10010000')}")

# # Multi-byte operations (for load/store instructions)
# print("\n=== Multi-byte Operations ===")

# # Set 4 bytes (32-bit word)
# MEMORIES.set_bytes("0x10010004", "11001100101010111111000011110000", 4)
# print(f"4-byte value: {MEMORIES.get_bytes('0x10010004', 4)}")

# # Set 2 bytes (16-bit halfword)
# MEMORIES.set_bytes("0x10010008", [1,1,0,0,1,1,0,0,1,0,1,0,1,0,1,0], 2)
# print(f"2-byte value: {MEMORIES.get_bytes('0x10010008', 2)}")

# print(f"\nTotal memory locations: {len(MEMORIES)}")


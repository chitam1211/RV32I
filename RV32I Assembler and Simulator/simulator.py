# Data structure

def registerFiles():
    return {f"x{i}": 0 for i in range(32)}

dataMemory = {}  # addr: data

# Initialize instruction memory directly from the assembler's output file
def initInstMem(input_file, output_file):
    """
    Sao chép nội dung file output.txt (mã máy 32-bit) vào InstMemory.txt
    """
    try:
        with open(input_file, "r") as infile, open(output_file, "w") as outfile:
            for line in infile:
                if line.strip():  # Bỏ qua dòng trống
                    outfile.write(line.strip() + "\n")
        print(f"Instruction memory initialized and saved to {output_file}.")
    except Exception as e:
        print(f"Error initializing instruction memory: {e}")

# Initialize data memory
def initDataMem(filename):
    dataMemory.clear()  # Xóa dữ liệu cũ
    addr = 0x10010000  # Bắt đầu từ địa chỉ 0x10010000
    with open(filename, "r") as f:
        for line in f:
            # Bỏ qua dòng trống hoặc dòng không hợp lệ
            if not line.strip() or ":" not in line:
                return

            # Phân tách tên biến và giá trị
            var, value = line.split(":")
            var = var.strip()  # Loại bỏ khoảng trắng ở hai đầu
            value = value.strip()

            # Xử lý giá trị theo định dạng (.WORD hoặc .BYTE)
            if ".WORD" in value:
                size = 4  # .WORD là 4 byte
                val = int(value.replace(".WORD", "").strip())
            elif ".BYTE" in value:
                size = 1  # .BYTE là 1 byte
                val = int(value.replace(".BYTE", "").strip())
            else:
                raise ValueError(f"Unsupported data type in line: {line.strip()}")

            # Ghi dữ liệu vào dataMemory
            for i in range(size):
                dataMemory[addr + i] = (val >> (i * 8)) & 0xFF  # Lưu từng byte
            addr += size  # Tăng địa chỉ

# Save data memory back to file
def saveDataMem(filename):
    global dataMemoryModified
    print(dataMemoryModified)
    with open(filename, "w") as f:
        addresses = sorted(dataMemory.keys())
        if not addresses:
            print("dmem dang rong")
            start_addr = 0x10010000
            for _ in range(4):
                line = f"0x{start_addr:08x}".ljust(14)
                for offset in range(0, 32, 4):
                    # Mỗi ô 4 byte ở đây là 0
                    line += "          0"  
                f.write(line + "\n")
                start_addr += 32
            return
            
            # Nếu không rỗng, thực hiện như bình thường
        if dataMemoryModified:
            start_addr = addresses[0]
            while start_addr <= addresses[-1]:
                line = f"0x{start_addr:08x}".ljust(14)
                for offset in range(0, 32, 4):
                    addr = start_addr + offset
                    value = (
                        dataMemory.get(addr, 0)
                        | (dataMemory.get(addr + 1, 0) << 8)
                        | (dataMemory.get(addr + 2, 0) << 16)
                        | (dataMemory.get(addr + 3, 0) << 24)
                    )
                    line += f"{value:>11}"
                f.write(line + "\n")
                start_addr += 32


# R-Type execution
def executeR(func3, rd, rs1, rs2, func7):
    global pc
    rd_key = f"x{rd}"
    rs1_key = f"x{rs1}"
    rs2_key = f"x{rs2}"

    print(f"Executing R-Type: func3={bin(func3)}, rd={rd_key}, rs1={rs1_key}, rs2={rs2_key}, func7={bin(func7)}")

    if func3 == 0b000:  # add/sub
        if func7 == 0b0000000:  # add
            reg[rd_key] = reg[rs1_key] + reg[rs2_key]
        elif func7 == 0b0100000:  # sub
            reg[rd_key] = reg[rs1_key] - reg[rs2_key]
    elif func3 == 0b100:  # xor
        reg[rd_key] = reg[rs1_key] ^ reg[rs2_key]
    elif func3 == 0b110:  # or
        reg[rd_key] = reg[rs1_key] | reg[rs2_key]
    elif func3 == 0b111:  # and
        reg[rd_key] = reg[rs1_key] & reg[rs2_key]
    elif func3 == 0b001:  # sll
        reg[rd_key] = reg[rs1_key] << (reg[rs2_key] & 0x1F)
    elif func3 == 0b101:  # srl/sra
        if func7 == 0b0000000:  # srl
            reg[rd_key] = (reg[rs1_key] & 0xFFFFFFFF) >> (reg[rs2_key] & 0x1F)
        elif func7 == 0b0100000:  # sra (arithmetic shift)
            reg[rd_key] = reg[rs1_key] >> (reg[rs2_key] & 0x1F)
    elif func3 == 0b010:  # slt
        reg[rd_key] = int(reg[rs1_key] < reg[rs2_key])
    elif func3 == 0b011:  # sltu
        reg[rd_key] = int((reg[rs1_key] & 0xFFFFFFFF) < (reg[rs2_key] & 0xFFFFFFFF))

# I-Type execution   
def executeI(func3, rd, rs1, imm):
    global pc
    rd_key = f"x{rd}"
    rs1_key = f"x{rs1}"

    print(f"Executing I-Type: func3={bin(func3)}, rd={rd_key}, rs1={rs1_key}, imm={imm}")

    if func3 == 0b000:  # addi
        reg[rd_key] = reg[rs1_key] + imm
    elif func3 == 0b110:  # ori
        reg[rd_key] = reg[rs1_key] | imm
    elif func3 == 0b100:  # xori
        reg[rd_key] = reg[rs1_key] ^ imm
    elif func3 == 0b111:  # andi
        reg[rd_key] = reg[rs1_key] & imm
    elif func3 == 0b001:  # slli
        reg[rd_key] = reg[rs1_key] << (imm & 0x1F)
    elif func3 == 0b101:  # srli/srai
        if imm >> 10 & 0x1:  # srai
            reg[rd_key] = reg[rs1_key] >> (imm & 0x1F)  # Arithmetic shift
        else:  # srli
            reg[rd_key] = (reg[rs1_key] & 0xFFFFFFFF) >> (imm & 0x1F)
    elif func3 == 0b010:  # slti
        reg[rd_key] = int(reg[rs1_key] < imm)
    elif func3 == 0b011:  # sltiu
        reg[rd_key] = int((reg[rs1_key] & 0xFFFFFFFF) < (imm & 0xFFFFFFFF))

dataMemoryModified = False
# S-Type execution
def executeS(func3, rs1, rs2, imm):
    global pc
    rs1_key = f"x{rs1}"
    rs2_key = f"x{rs2}"
    global dataMemoryModified
    dataMemoryModified = True
    print(f"Executing S-Type: func3={bin(func3)}, rs1={rs1_key}, rs2={rs2_key}, imm={imm}")
    print("rs1:", reg[rs1_key])
    print("rs2:", reg[rs2_key])
    if func3 == 0b010:  # sw
        addr = reg[rs1_key] + imm
        value = reg[rs2_key]
        if value > 0:
            value = value & 0xFFFFFFFF
            print("value:", value)
            for i in range(4):
                dataMemory[addr + i] = (value >> (i * 8)) & 0xFF  # Ghi từng byte
        else:
            print("value:", value)
            for i in range(4):
                dataMemory[addr + i] = value

# L-Type execution (load instructions)
def executeL(func3, rd, rs1, imm):
    global pc
    rd_key = f"x{rd}"
    rs1_key = f"x{rs1}"
    addr = reg[rs1_key] + imm

    print(f"Executing L-Type: func3={bin(func3)}, rd={rd_key}, rs1={rs1_key}, imm={imm}, addr={hex(addr)}")

    if func3 == 0b010:  # lw (load word)
        reg[rd_key] = sum((dataMemory.get(addr + i, 0) << (i * 8)) for i in range(4))
    elif func3 == 0b000:  # lb (load byte)
        reg[rd_key] = dataMemory.get(addr, 0)
        if reg[rd_key] & 0x80:  # Dấu âm (sign extension)
            reg[rd_key] -= 0x100
    elif func3 == 0b100:  # lbu (load byte unsigned)
        reg[rd_key] = dataMemory.get(addr, 0)
    elif func3 == 0b001:  # lh (load halfword)
        reg[rd_key] = sum((dataMemory.get(addr + i, 0) << (i * 8)) for i in range(2))
        if reg[rd_key] & 0x8000:  # Dấu âm (sign extension)
            reg[rd_key] -= 0x10000
    elif func3 == 0b101:  # lhu (load halfword unsigned)
        reg[rd_key] = sum((dataMemory.get(addr + i, 0) << (i * 8)) for i in range(2))

# B-Type execution
def executeB(func3, rs1, rs2, offset):
    global pc
    rs1_key = f"x{rs1}"
    rs2_key = f"x{rs2}"
    printRegisterFile()
    # In thông tin về lệnh đang thực thi và giá trị các thanh ghi
    print(f"Executing B-Type: func3={bin(func3)}, rs1={rs1_key}, rs1_value={reg[rs1_key]}, rs2={rs2_key}, rs2_value={reg[rs2_key]}, offset={offset}")
    print("rs1:", reg[rs1_key])
    print("rs2:", reg[rs2_key])

    # BEQ
    if func3 == 0b000 and reg[rs1_key] == reg[rs2_key]:  # Branch if Equal
        pc += offset
        print(f"BEQ taken: PC updated to {pc}")
        return True

    # BNE
    elif func3 == 0b001 and reg[rs1_key] != reg[rs2_key]:  # Branch if Not Equal
        pc += offset
        print(f"BNE taken: PC updated to {pc}")
        return True

    # BLT
    elif func3 == 0b100 and reg[rs1_key] < reg[rs2_key]:  # Branch if Less Than (signed)
        pc += offset
        print(f"BLT taken: PC updated to {pc}")
        return True

    # BGE
    elif func3 == 0b101 and reg[rs1_key] >= reg[rs2_key]:  # Branch if Greater or Equal (signed)
        pc += offset
        print(f"BGE taken: PC updated to {pc}")
        return True

    # BLTU
    elif func3 == 0b110 and (reg[rs1_key] & 0xFFFFFFFF) < (reg[rs2_key] & 0xFFFFFFFF):  # Branch if Less Than (unsigned)
        pc += offset
        print(f"BLTU taken: PC updated to {pc}")
        return True

    # BGEU
    elif func3 == 0b111 and (reg[rs1_key] & 0xFFFFFFFF) >= (reg[rs2_key] & 0xFFFFFFFF):  # Branch if Greater or Equal (unsigned)
        pc += offset
        print(f"BGEU taken: PC updated to {pc}")
        return True

    # Nếu không nhảy
    print("Branch not taken")
    return False

# U-Type execution
def executeU(opcode, rd, imm):
    global pc
    rd_key = f"x{rd}"

    print(f"Executing U-Type: opcode={bin(opcode)}, rd={rd_key}, imm={imm}")

    if opcode == 0b0110111:  # lui
        reg[rd_key] = imm << 12
    elif opcode == 0b0010111:  # auipc
        reg[rd_key] = pc + (imm << 12)

# J-Type execution
def executeJ(rd, offset):
    global pc
    rd_key = f"x{rd}"

    print(f"Executing J-Type: rd={rd_key}, offset={offset}")

    reg[rd_key] = pc + 4
    pc += offset
    return True

# Instruction decoder
def instDecoder(inst):
    opcode = inst & 0x7F
    rd = (inst >> 7) & 0x1F
    func3 = (inst >> 12) & 0x7
    rs1 = (inst >> 15) & 0x1F
    rs2 = (inst >> 20) & 0x1F
    func7 = (inst >> 25) & 0x7F
    
    # Xử lý immediate mở rộng dấu
    imm_i = (inst >> 20) & 0xFFF
    if imm_i & 0x800:  # Mở rộng dấu 12-bit thành 32-bit
        imm_i -= 0x1000

    imm_s = ((inst >> 25) << 5) | ((inst >> 7) & 0x1F)
    if imm_s & 0x800:  # Mở rộng dấu 12-bit thành 32-bit
        imm_s -= 0x1000

    imm_b = ((inst >> 31) << 12) | (((inst >> 7) & 0x1) << 11) | (((inst >> 25) & 0x3F) << 5) | ((inst >> 8) & 0xF) << 1
    if imm_b & 0x1000:  # Mở rộng dấu 13-bit thành 32-bit
        imm_b -= 0x2000

    imm_u = inst >> 12  # Không cần mở rộng dấu
    imm_j = ((inst >> 31) << 20) | (((inst >> 12) & 0xFF) << 12) | (((inst >> 20) & 0x1) << 11) | (((inst >> 21) & 0x3FF) << 1)
    if imm_j & 0x100000:  # Mở rộng dấu 21-bit thành 32-bit
        imm_j -= 0x200000

    print(f"Decoded Instruction: opcode={bin(opcode)}, rd={rd}, func3={bin(func3)}, rs1={rs1}, rs2={rs2}, func7={bin(func7)}, imm_i={imm_i}, imm_s={imm_s}, imm_b={imm_b}, imm_u={imm_u}, imm_j={imm_j}")

    return opcode, func3, func7, rd, rs1, rs2, imm_i, imm_s, imm_b, imm_u, imm_j


# Hàm hiển thị trạng thái của Register File
def printRegisterFile():
    print("\nRegister File:")
    for reg_name, value in reg.items():
        print(f"{reg_name}: {value}")
    print("-" * 40)

# Main function
def main():
    # Đường dẫn file
    input_inst_file = "E:\\AI accelerator\\Assembler\\output.txt"  # File mã máy đầu vào
    output_inst_file = "E:\\AI accelerator\\Assembler\\InstMemory.txt"  # File mã lệnh đầu ra
    data_file = "E:\\AI accelerator\\Assembler\\data.txt"
    data_memory_file = "E:\\AI accelerator\\Assembler\\DataMemory.txt"
    global pc, reg, InstrMem, dataMemory  # Đảm bảo các biến toàn cục có thể được sử dụng
    reg = registerFiles()  # Khởi tạo các thanh ghi
    reg["x2"] = 2147479548
    reg["x3"] = 268468224
    pc = 4194304  # Đặt giá trị ban đầu của PC
    printRegisterFile()
    # Khởi tạo bộ nhớ lệnh từ file đầu vào và lưu vào file đầu ra
    initInstMem(input_inst_file, output_inst_file)

    # Khởi tạo bộ nhớ dữ liệu từ file data.txt
    initDataMem(data_file)

    # Execute instructions
    with open(output_inst_file, "r") as inst_file:
        instructions = inst_file.readlines()

    while pc < 4194304 + len(instructions) * 4:
        inst_index = (pc - 4194304) // 4
        line = instructions[inst_index].strip()
        if not line:  # Bỏ qua dòng trống
            pc += 4
            continue

        print(f"PC={pc}, Instruction Line={line}")

        # Chuyển đổi lệnh từ chuỗi sang số nguyên
        inst = int(line, 2)

        # Giải mã lệnh
        opcode, func3, func7, rd, rs1, rs2, imm_i, imm_s, imm_b, imm_u, imm_j = instDecoder(inst)

        # Thực thi lệnh dựa trên opcode
        if opcode == 0b0110011:  # R-Type
            executeR(func3, rd, rs1, rs2, func7)
        elif opcode == 0b0010011:  # I-Type
            executeI(func3, rd, rs1, imm_i)
        elif opcode == 0b0100011:  # S-Type
            executeS(func3, rs1, rs2, imm_s)
        elif opcode == 0b0000011:  # L-Type (load)
            executeL(func3, rd, rs1, imm_i)
        elif opcode == 0b1100011:  # B-Type
            if executeB(func3, rs1, rs2, imm_b):
                continue  # Nếu nhảy, không tăng PC theo cách thông thường
        elif opcode == 0b0110111 or opcode == 0b0010111:  # U-Type
            executeU(opcode, rd, imm_u)
        elif opcode == 0b1101111:  # J-Type
            if executeJ(rd, imm_j):
                continue  # Nếu nhảy, không tăng PC theo cách thông thường
        elif opcode == 0b1100111:  # JALR (Jump and Link Register)
            rd_key = f"x{rd}"
            rs1_key = f"x{rs1}"
            target_addr = (reg[rs1_key] + imm_i) & ~1  # Tính toán địa chỉ đích và xóa bit thấp nhất

            # Lưu giá trị PC + 4 vào rd nếu rd != 0
            if rd != 0:
                reg[rd_key] = pc + 4

            # Cập nhật PC với địa chỉ đích
            pc = target_addr
            print(f"JALR executed: rd={rd_key}, rs1={rs1_key}, imm_i={imm_i}, target_addr={hex(target_addr)}, PC={hex(pc)}")

            continue  # Không tăng PC theo cách thông thường
        pc += 4

    # In ra giá trị các thanh ghi
    printRegisterFile()
    
    # Lưu bộ nhớ dữ liệu cuối cùng vào file
    saveDataMem(data_memory_file)
if __name__ == "__main__":
    main()

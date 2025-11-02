import struct
from VARIABLES import *
from MEMORIES import *
def print_register_changes(changed_registers):
    """
    Print the registers that were modified by an instruction.
    
    Args:
        changed_registers (list): List of dictionaries containing register type, name, and optional value.
    """
    if not changed_registers:
        print("No registers were modified by this instruction.")
        return
    
    print("Registers modified by the instruction:")
    for reg in changed_registers:
        reg_name = reg.get("name")  # e.g., "md", "rs1", "0x10010000"
        value = reg.get("value", "Not displayed")  # Optional value, if provided
        print(f"{reg_name}: Value = {value}")
        
        # Write register status to file
        with open(r"D:\EA+\DoAn1\ISS\status.txt", "a") as status_file:
            status_file.write(f"{reg_name}: Value = {value}\n")
def logical_right_shift(value, n):
    # Use a mask to ensure the leftmost bits are zero-filled
    mask = (1 << 32) - 1
    return (value >> n) & mask

def apply_saturation(value, bit_width=16, sign=False):
    
    if XMCSR["xmsaten"]['value'] == "0":
        # Wrap around
        return value & ((1 << bit_width) - 1)
    
    elif XMCSR["xmsaten"]['value'] == "1":
        # Saturate to max or min
        if sign:
            max_val = (1 << (bit_width - 1)) - 1    # 2^(n-1) - 1
            min_val = -(1 << (bit_width - 1))       # -2^(n-1)
        else:
            max_val = (1 << (bit_width)) - 1    # 2^(n) - 1
            min_val = -(1 << (bit_width))       # -2^(n)
        
        if value > max_val:
            return max_val
        elif value < min_val:
            return min_val
        else:
            return value
    else:
        raise ValueError("Invalid value of XMCSR['xmsaten']")

def cvt(org_val, org_type, res_type):
    res_val = 0
    if res_type == "sint8" or res_type == "uint8":
        res_val = "0".zfill(8)
    elif res_type == "sint32" or res_type == "uint32":
        res_val = "0".zfill(32)
        
    "Convert original value to integer"
    if org_type == "sint8":
        sign = int(org_val[0])
        magnitude = int(org_val[1:8], 2)
        int_num = (-1)**sign * magnitude
    
    elif org_type == "uint8":
        int_num = int(org_val, 2)
    
    elif org_type == "sint32":
        sign = org_val[0]
        magnitude = int(org_val[1:8], 2)
        int_num = (-1)**sign * magnitude
    
    elif org_type == "uint32":
        int_num = int(org_val, 2)
    elif org_type == "int":
        int_num = org_val
    else:
        raise ValueError("Invalid original type")

    "Convert integer to desired type"    
    if res_type == "sint8":
        packed = struct.pack('>i', int_num)
        bits = struct.unpack('>i', packed)[0]
        
        if bits < 0:
            res_bin = (1 << 8) + bits
        else:
            res_bin = bits
            
        res_val = str(bin(res_bin))[2:].zfill(8)
        
    elif res_type == "uint8":
        res_val = str(bin(int(int_num)))[2:].zfill(8)
    
    elif res_type == "sint32":
        packed = struct.pack('>i', int_num)
        bits = struct.unpack('>i', packed)[0]
        
        if bits < 0:
            res_bin = (1 << 32) + bits
        else:
            res_bin = bits
            
        res_val = str(bin(res_bin))[2:].zfill(32)
    
    elif res_type == "uint32":
        res_val = str(bin(int(int_num)))[2:].zfill(32)
    
    elif res_type == "int":
        res_val = int_num
    else:
        raise ValueError("Invalid result type")
    
    return res_val

def binary_to_data_Matrix(line, current_address):
    pc1 = int(current_address, 2)
    changed_registers = []
    
    func = line[0:4]
    uop = line[4:6]
    ctrl = line[6]
    func3 = line[17:20]
    opcode = line[25:32]
    print("Function:", func, "UOP:", uop, "Control:", ctrl, "Func3:", func3)
    # md = line[7:9]
    # d_size = line[9:10]
    # ms1 = line[15:17]
    # s_size = line[18:19]
    # ms2 = line[20:22]
    # imm3_ctrl = line[23:25]
    
    if MSTATUS["MS"]["value"] == "00":
        raise Exception("Matrix Extension is Off. Please enable it before using matrix instructions.")
    
    # TABLE 2: Matrix Configuration Instructions
    if func == "0000" and func3 == "000" and uop == "00":
        # mrelease
        MATRIX_REGISTER["mi"] = 0
        MATRIX_REGISTER["ki"] = 0
        MATRIX_REGISTER["ni"] = 0
        
        MSTATUS["MS"]["value"] = "01"
        changed_registers.append([{"name": "mi", "value": 0},
                                {"name": "ki", "value": 0},
                                {"name": "ni", "value": 0},
                                {"name": "MS", "value": "01"}
                                ])   
        # M: row of Matrix A, column of Matrix C
        # N: column of Matrix B, row of Matrix C
        # K: column of Matrix A, row of Matrix B, 
        
    elif func == "0001" and func3 == "000" and uop == "00":
        if ctrl == "0":
            # msettileki imm
            uimm10 = line[7:17]
            MATRIX_REGISTER["ki"] = int(uimm10, 2)
            changed_registers.append({"name": "ki", "value": int(uimm10, 2)})
        elif ctrl == "1":
            # msettilek rs1
            rs1 = line[12:17]
            MATRIX_REGISTER["ki"] = int(REGISTERS[rs1]["value"],2)
            changed_registers.append({"name": "ki", "value": REGISTERS[rs1]["value"]})
            
    elif func == "0010" and func3 == "000" and uop == "00":

        if ctrl == "0":
            # msettilemi imm
            uimm10 = line[7:17]
            MATRIX_REGISTER["mi"] = int(uimm10, 2)
            changed_registers.append({"name": "mi", "value": int(uimm10, 2)})
        else:
            # msettilem rs1
            rs1 = line[12:17]
            MATRIX_REGISTER["mi"] = int(REGISTERS[rs1]["value"],2)
            changed_registers.append({"name": "mi", "value": REGISTERS[rs1]["value"]})
            
    elif func == "0011" and func3 == "000" and uop == "00":
        
        if ctrl == "0":
            # msettileni imm
            uimm10 = line[7:17]
            MATRIX_REGISTER["ni"] = int(uimm10, 2)
            changed_registers.append({"name": "ni", "value": int(uimm10, 2)})
        else:
            # msettilen rs1
            rs1 = line[12:17]
            MATRIX_REGISTER["ni"] = REGISTERS[rs1]["value"]    
            changed_registers.append({"name": "ni", "value": REGISTERS[rs1]["value"]})

    # TABLE 3: Matrix MISC Instructions 
    elif func == "0000" and uop == "11" and func3 == "000":
        # mzero acc0
        md = line[22:25]
        md_v = int(md, 2)
        
        md_list = list(MATRIX_REGISTER[md]["value"])
        if 0 <= md_v < 4:
            md_list = f"{0:0512b}"
        elif 4 < md_v <= 7:
            md_list = f"{0:02048b}"
        
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
        
    elif func == "0001" and uop == "11" and func3 == "000":
        # mmov.mm md ms1
        ms1 = line[14:17]
        md = line[22:25]
        
        md_v = int(md, 2)
        ms1_v = int(ms1, 2)
        md_list = list(MATRIX_REGISTER[md]["value"])
        
        if md_v in range(0,4) and ms1_v in range(0,4):
            md_list = MATRIX_REGISTER[ms1]["value"]
            MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        elif md_v in range(4,8) and ms1_v in range(4,8):
            md_list = MATRIX_REGISTER[ms1]["value"]
            MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        else:
            min_len = min(TRLEN, ARLEN)
            md_list[:min_len] = MATRIX_REGISTER[ms1]["value"][:min_len]
            MATRIX_REGISTER[md]["value"] = ''.join(md_list)
                
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
    
    elif func == "0010" and uop == "11" and func3 == "000":
        # mmov<b/h/w/d>.x.m rd, ms2, rs1
        ctrl = line[6] # no need to check
        e_size = line[7:9]
        ms2 = line[9:12]
        rs1 = line[12:17]
        rd = line[20:25]
        
        index = int(REGISTERS[rs1]["value"],2)
        rd_list = list(REGISTERS[rd]["value"])
        ms2_v = int(ms2, 2)
        rs1_v = int(rs1, 2)
        if e_size == "00":  # Byte
            eew = 8
            element_per_row = 16
        elif e_size == "01":  # Halfword (16-bit)
            eew = 16
            element_per_row = 8
        elif e_size == "10":  # Word (32-bit)
            eew = 32
            element_per_row = 4
        elif e_size == "11":  # Doubleword (64-bit)
            eew = 64
            element_per_row = 2
        else:
            raise ValueError("Invalid element size")
        
        col_index = index % element_per_row
        row_index = index // element_per_row
        if ms2_v in range(0, 4):
            index = row_index * element_per_row + col_index*TRLEN
        elif ms2_v in range(4, 8):
            index = row_index * element_per_row + col_index*ARLEN
        else:
            raise ValueError("Invalid matrix register name")
        
        for i in range(index, index + 32):
            rd_list[i - index] = MATRIX_REGISTER[ms2]["value"][i]
            
        REGISTERS[rd]["value"] = ''.join(rd_list)
        changed_registers.append({"name": REGISTERS[rd]["name"], "value": REGISTERS[rd]["value"]})

    elif func == "0011" and uop == "11" and func3 == "000":
        ctrl = line[6]
        e_size = line[7:9]
        rs2 = line[7:12]
        rs1 = line[12:17]
        d_size = line[20:22]
        md = line[22:25]
        
        rs1_v = int(REGISTERS[rs1]["value"], 2)
        md_list = list(MATRIX_REGISTER[md]["value"])
        if e_size == "00":  # Byte
            #eew = 8
            element_per_row = 16
        elif e_size == "01":  # Halfword (16-bit)
            #eew = 16
            element_per_row = 8
        elif e_size == "10":  # Word (32-bit)
            #eew = 32
            element_per_row = 4
        elif e_size == "11":  # Doubleword (64-bit)
            #eew = 64
            element_per_row = 2
        else:
            raise ValueError("Invalid element size")
        
        if ctrl == 1:
            # mmov<b/h/w/d>.m.x md, rs2, rs1
            # MATRIX_REGISTER[md]["value"][row][col] = element
            row = rs1_v // element_per_row
            col = rs1_v % element_per_row
            if md in range(0, 4):
                index = row * element_per_row + col * TRLEN
            elif md in range(4, 8):
                index = row * element_per_row + col * ARLEN
            else:
                raise ValueError("Invalid matrix register name")
            
            for i in range(index, index + 32):
                md_list[i] = REGISTERS[rs2]["value"][i-index]
            
            MATRIX_REGISTER[md]["value"] = ''.join(md_list)
            changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
        elif ctrl == 0:
            #mdup.b/h/w/d md, rs1
            #does not support yet            
            changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})

    elif func == "0100" and uop == "11" and func3 == "000":
        #mpack md, ms1, ms2
        md = line[22:25]
        ms1 = line[14:17]
        ms2 = line[9:12]
        ctrl = line[7:9]
        
        md_v = int(md, 2)
        ms1_v = int(ms1, 2)
        ms2_v = int(ms2, 2)
        md_list = list(MATRIX_REGISTER[md]["value"])
        
        if md_v in range(0,4) and ms1_v in range(0,4) and ms2_v in range(0,4):
            if MATRIX_REGISTER["mi"] != 0:  # Matrix A
                if MATRIX_REGISTER["mi"] > 4:
                    raise ValueError("Matrix A has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["mi"]
            else:  # Matrix B
                if MATRIX_REGISTER["ni"] > 4:
                    raise ValueError("Matrix B has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["ni"]
            
            if ctrl == "00":
                # mpack
                for i in range(ROWNUM):
                    md_list[i*TRLEN:i*TRLEN+TRLEN/2] = MATRIX_REGISTER[ms1]["value"][i*TRLEN+TRLEN/2:i*TRLEN+TRLEN]
                    md_list[i*TRLEN+TRLEN/2:i*TRLEN+TRLEN] = MATRIX_REGISTER[ms2]["value"][i*TRLEN+TRLEN/2:i*TRLEN+TRLEN]
            elif ctrl == "10":
                # mpackhl
                for i in range(ROWNUM):
                    md_list[i*TRLEN:i*TRLEN+TRLEN/2] = MATRIX_REGISTER[ms1]["value"][i*TRLEN:i*TRLEN+TRLEN/2]
                    md_list[i*TRLEN+TRLEN/2:i*TRLEN+TRLEN] = MATRIX_REGISTER[ms2]["value"][i*TRLEN+TRLEN/2:i*TRLEN+TRLEN]
            elif ctrl == "11":
                # mpackhh
                for i in range(ROWNUM):
                    md_list[i*TRLEN:i*TRLEN+TRLEN/2] = MATRIX_REGISTER[ms1]["value"][i*TRLEN:i*TRLEN+TRLEN/2]
                    md_list[i*TRLEN+TRLEN/2:i*TRLEN+TRLEN] = MATRIX_REGISTER[ms2]["value"][i*TRLEN:i*TRLEN+TRLEN/2]

        elif md_v in range(4,8) and ms1_v in range(4,8) and ms2_v in range(4,8):
            if MATRIX_REGISTER["mi"] > 4:
                raise ValueError("Matrix C has more than 4 rows, which is not supported")
            ROWNUM = MATRIX_REGISTER["mi"]
            
            if ctrl == "00":
                # mpack
                for i in range(ROWNUM):
                    md_list[i*TRLEN:i*TRLEN+TRLEN/2] = MATRIX_REGISTER[ms1]["value"][i*TRLEN+TRLEN/2:i*TRLEN+TRLEN]
                    md_list[i*TRLEN+TRLEN/2:i*TRLEN+TRLEN] = MATRIX_REGISTER[ms2]["value"][i*TRLEN+TRLEN/2:i*TRLEN+TRLEN]
            elif ctrl == "10":
                # mpackhl
                for i in range(ROWNUM):
                    md_list[i*TRLEN:i*TRLEN+TRLEN/2] = MATRIX_REGISTER[ms1]["value"][i*TRLEN:i*TRLEN+TRLEN/2]
                    md_list[i*TRLEN+TRLEN/2:i*TRLEN+TRLEN] = MATRIX_REGISTER[ms2]["value"][i*TRLEN+TRLEN/2:i*TRLEN+TRLEN]
            elif ctrl == "11":
                # mpackhh
                for i in range(ROWNUM):
                    md_list[i*TRLEN:i*TRLEN+TRLEN/2] = MATRIX_REGISTER[ms1]["value"][i*TRLEN:i*TRLEN+TRLEN/2]
                    md_list[i*TRLEN+TRLEN/2:i*TRLEN+TRLEN] = MATRIX_REGISTER[ms2]["value"][i*TRLEN:i*TRLEN+TRLEN/2]

        else:
            raise ValueError("Matrix register do not match")
        
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
      
    elif func == "0101" and uop == "11" and func3 == "000":
    # mrslidedown
        uimm3 = int(line[6:9], 2)
        ms1 = line[14:17]
        md = line[22:25]
        
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        md_list = list(MATRIX_REGISTER[md]["value"])
        # Get actual matrix dimensions from configuration registers
        if md_v in range(0, 4) and ms1_v in range(0, 4):
            # For matrices A or B, use appropriate dimensions
            if MATRIX_REGISTER["mi"] != 0:  # Matrix A
                if MATRIX_REGISTER["mi"] > 4:
                    raise ValueError("Matrix A has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["mi"]
            else:  # Matrix B
                if MATRIX_REGISTER["ni"] > 4:
                    raise ValueError("Matrix B has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["ni"]
                
            # Limit uimm3 to actual row count
            uimm3 = uimm3 % ROWNUM
            
            md_list = list(f"{0:0512b}")
            for i in range(ROWNUM - uimm3):
                md_list[i*TRLEN:(i+1)*TRLEN] = MATRIX_REGISTER[ms1]["value"][(i+uimm3)*TRLEN:(i+1)*TRLEN]
                
        elif md_v in range(4, 8) and ms1_v in range(4, 8):
            if MATRIX_REGISTER["mi"] > 4:
                raise ValueError("Matrix C has more than 4 rows, which is not supported")
            ROWNUM = MATRIX_REGISTER["mi"]
            
            # Limit uimm3 to actual row count
            uimm3 = uimm3 % ROWNUM
            
            md_list = list(f"{0:02048b}")
            for i in range(ROWNUM - uimm3):
                md_list[i*ARLEN:(i+1)*ARLEN] = MATRIX_REGISTER[ms1]["value"][(i+uimm3)*ARLEN:(i+1)*ARLEN]
        
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
    elif func == "0110" and uop == "11" and func3 == "000":
        # mrslideup
        uimm3 = int(line[6:9], 2)
        ms1 = line[14:17]
        md = line[22:25]
        
        ms1_v = int(ms1, 2) 
        md_v = int(md, 2)
        md_list = list(MATRIX_REGISTER[md]["value"])
        if md_v in range(0,4) and ms1_v in range(0,4):
            if MATRIX_REGISTER["mi"] != 0:  # Matrix A
                if MATRIX_REGISTER["mi"] > 4:
                    raise ValueError("Matrix A has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["mi"]
            else:  # Matrix B
                if MATRIX_REGISTER["ni"] > 4:
                    raise ValueError("Matrix B has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["ni"]
            
            md_list = list(f"{0:0512b}")
            for i in range(ROWNUM - uimm3):
                md_list[i*TRLEN:(i+1)*TRLEN] = MATRIX_REGISTER[ms1]["value"][(i-uimm3)*TRLEN:(i+1)*TRLEN]
            
        elif md_v in range(4,8) and ms1_v in range(4,8):
            if MATRIX_REGISTER["mi"] > 4:
                raise ValueError("Matrix C has more than 4 rows, which is not supported")
            ROWNUM = MATRIX_REGISTER["mi"]
            
            md_list = list(f"{0:2048b}")
            for i in range(ROWNUM - uimm3):
                md_list[i*ARLEN:(i+1)*ARLEN] = MATRIX_REGISTER[ms1]["value"][(i-uimm3)*ARLEN:(i+1)*ARLEN]
        else:
            raise ValueError("Matrix register do not match")
            
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})

    elif func == "0111" and uop == "11" and func3 == "000":
        # mcslidedown<b.h.w.d>
        uimm3 = int(line[6:9], 2)
        s_size = line[12:14]
        ms1 = line[14:17]
        d_size = line[20:22]
        md = line[22:25]
        
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        if d_size != s_size:
            raise ValueError("Size mismatch")
        elif not ((0 <= md_v < 4 and 0 <= ms1_v < 4) 
                or (4 <= md_v < 8 and 4 <= ms1_v < 8)):
            raise ValueError("Matrix register do not match")
        
        if d_size == "00":  # Byte (8-bit)
            eew = 8
        elif d_size == "01":  # Halfword (16-bit)
            eew = 16
        elif d_size == "10":  # Word (32-bit)
            eew = 32
        elif d_size == "11":  # Doubleword (64-bit)
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if (0 <= md_v < 4 and 0 <= ms1_v < 4):
            if MATRIX_REGISTER["mi"] != 0:  # Matrix A
                if MATRIX_REGISTER["mi"] > 4:
                    raise ValueError("Matrix A has more than 4 rows, which is not supported")
                
                ROWNUM = MATRIX_REGISTER["mi"]
            else:  # Matrix B
                if MATRIX_REGISTER["ni"] > 4:
                    raise ValueError("Matrix B has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["ni"]
                
            if MATRIX_REGISTER["ki"] > TRLEN // eew:
                raise ValueError(f"Matrix A has more than {TRLEN//eew} columns, which is not supported")
            COLNUM = MATRIX_REGISTER["ki"]
            
            md_list = list(f"{0:0512b}")
            uimm3 = uimm3 & (COLNUM - 1)
            for i in range(0, COLNUM - uimm3 - 1):
                for j in range(ROWNUM):
                    md_list[i*eew+j*TRLEN:(i+1)*eew+j*TRLEN] = MATRIX_REGISTER[ms1]["value"][(i+uimm3)*eew+j*TRLEN:(i+uimm3+1)*eew+j*TRLEN]
            
        elif (4 <= md_v < 8 and 4 <= ms1_v < 8):
            if MATRIX_REGISTER["mi"] > 4:
                raise ValueError("Matrix C has more than 4 rows, which is not supported")
            ROWNUM = MATRIX_REGISTER["mi"]
            
            if MATRIX_REGISTER["ki"] > ARLEN // eew:
                raise ValueError(f"Matrix C has more than {ARLEN//eew} columns, which is not supported")
            COLNUM = MATRIX_REGISTER["ki"]
            
            md_list = list(f"{0:02048b}")
            uimm3 = uimm3 & (COLNUM - 1)
            for i in range(0, COLNUM - uimm3 - 1):
                for j in range(ROWNUM):
                    md_list[i*eew+j*ARLEN:(i+1)*eew+j*ARLEN] = MATRIX_REGISTER[ms1]["value"][(i+uimm3)*eew+j*ARLEN:(i+uimm3+1)*eew+j*ARLEN]
        else:
            raise ValueError("Matrix register do not match")
        
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})

    elif func == "1000" and uop == "11" and func3 == "000":
        # mcslideup<b.h.w.d>
        uimm3 = int(line[6:9], 2) & 0b11
        s_size = line[12:14]
        ms1 = line[14:17]
        d_size = line[20:22]
        md = line[22:25]
        
        ms1_v = int(ms1, 2) 
        md_v = int(md, 2)
        md_list = list(MATRIX_REGISTER[md]["value"])
        if d_size != s_size:
            raise ValueError("Size mismatch")
        
        if d_size == "00":  # Byte
            eew = 8
        elif d_size == "01":  # Halfword (16-bit)
            eew = 16
        elif d_size == "10":  # Word (32-bit)
            eew = 32
        elif d_size == "11":  # Doubleword (64-bit)
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if (0 <= md_v < 4 and 0 <= ms1_v < 4):
            if MATRIX_REGISTER["mi"] != 0:  # Matrix A
                if MATRIX_REGISTER["mi"] > 4:
                    raise ValueError("Matrix A has more than 4 rows, which is not supported")
                
                ROWNUM = MATRIX_REGISTER["mi"]
            else:  # Matrix B
                if MATRIX_REGISTER["ni"] > 4:
                    raise ValueError("Matrix B has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["ni"]
                
            if MATRIX_REGISTER["ki"] > TRLEN // eew:
                raise ValueError(f"Matrix A has more than {TRLEN//eew} columns, which is not supported")
            COLNUM = MATRIX_REGISTER["ki"]
            
            md_list = list(f"{0:0512b}")
            uimm3 = uimm3 & (COLNUM - 1)
            for i in range(uimm3, COLNUM -1):
                for j in range(ROWNUM):
                    md_list[i*eew+j*TRLEN:(i+1)*eew+j*TRLEN] = MATRIX_REGISTER[ms1]["value"][(i-uimm3)*eew+j*TRLEN:(i-uimm3+1)*eew+j*TRLEN]
            
        elif (4 <= md_v < 8 and 4 <= ms1_v < 8):
            if MATRIX_REGISTER["mi"] > 4:
                raise ValueError("Matrix C has more than 4 rows, which is not supported")
            ROWNUM = MATRIX_REGISTER["mi"]
            
            if MATRIX_REGISTER["ki"] > ARLEN // eew:
                raise ValueError(f"Matrix C has more than {ARLEN//eew} columns, which is not supported")
            COLNUM = MATRIX_REGISTER["ki"]
            
            md_list = list(f"{0:02048b}")
            uimm3 = uimm3 & (COLNUM - 1)
            for i in range(uimm3, COLNUM -1):
                for j in range(ROWNUM):
                    md_list[i*eew+j*ARLEN:(i+1)*eew+j*ARLEN] = MATRIX_REGISTER[ms1]["value"][(i-uimm3)*eew+j*ARLEN:(i-uimm3+1)*eew+j*ARLEN]
        else:
            raise ValueError("Matrix register do not match")
        
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})

    elif func == "1001" and uop == "11" and func3 == "000":
        #mrbc.mv.i md, ms1, imm
        uimm3 = int(line[6:9], 2)
        ms1 = line[14:17]
        md = line[22:25]
        
        ms1_v = int(ms1, 2) 
        md_v = int(md, 2)
        md_list = list(MATRIX_REGISTER[md]["value"])
        if md_v in range(0,4) and ms1_v in range(0,4):
            if MATRIX_REGISTER["mi"] != 0:  # Matrix A
                if MATRIX_REGISTER["mi"] > 4:
                    raise ValueError("Matrix A has more than 4 rows, which is not supported")
                
                ROWNUM = MATRIX_REGISTER["mi"]
            else:  # Matrix B
                if MATRIX_REGISTER["ni"] > 4:
                    raise ValueError("Matrix B has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["ni"]
            
            source_value = MATRIX_REGISTER[ms1]["value"][uimm3*TRLEN:(uimm3+1)*TRLEN]
            for i in range(ROWNUM):
                md_list[i*TRLEN:(i+1)*TRLEN] = source_value
        elif md_v in range(4,8) and ms1_v in range(4,8):
            if MATRIX_REGISTER["mi"] > 4:
                raise ValueError("Matrix C has more than 4 rows, which is not supported")
            ROWNUM = MATRIX_REGISTER["mi"]
            
            source_value = MATRIX_REGISTER[ms1]["value"][uimm3*ARLEN:(uimm3+1)*ARLEN]
            for i in range(ROWNUM):
                md_list[i*ARLEN:(i+1)*ARLEN] = source_value
        else:
            raise ValueError("Matrix register do not match")

        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})

    elif func == "1010" and uop == "11" and func3 == "000":
        # # mcbc<b/h/w/d> md, ms1, imm
        uimm3 = int(line[6:9], 2)
        s_size = line[12:14]
        ms1 = line[14:17]
        d_size = line[20:22]
        md = line[22:25]

        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        md_list = list(MATRIX_REGISTER[md]["value"])
        if d_size != s_size:
            raise ValueError("Size mismatch")
        
        if d_size == "00":
            eew = 8
        elif d_size == "01":
            eew = 16
        elif d_size == "10":
            eew = 32
        elif d_size == "11":
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if (md_v in range(0,4) and ms1_v in range(0,4)):
            if MATRIX_REGISTER["mi"] != 0:  # Matrix A
                if MATRIX_REGISTER["mi"] > 4:
                    raise ValueError("Matrix A has more than 4 rows, which is not supported")
                
                ROWNUM = MATRIX_REGISTER["mi"]
            else:  # Matrix B
                if MATRIX_REGISTER["ni"] > 4:
                    raise ValueError("Matrix B has more than 4 rows, which is not supported")
                ROWNUM = MATRIX_REGISTER["ni"]
                
            for i in range(ROWNUM):
                source_value = MATRIX_REGISTER[ms1]["value"][uimm3*eew+i*TRLEN:(uimm3+1)*eew+i*TRLEN]
                md_list[i*TRLEN:(i+1)*TRLEN] = source_value* TRLEN//eew
                    
        elif (md_v in range(4,8) and ms1_v in range(4,8)):
            if MATRIX_REGISTER["mi"] > 4:
                raise ValueError("Matrix C has more than 4 rows, which is not supported")
            ROWNUM = MATRIX_REGISTER["mi"]
            
            for i in range(ROWNUM):
                source_value = MATRIX_REGISTER[ms1]["value"][uimm3*eew+i*ARLEN:(uimm3+1)*eew+i*ARLEN]
                md_list[i*ARLEN:(i+1)*ARLEN] = source_value* ARLEN//eew
        
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
#=======================================#        
        # TABLE 4: Matrix Multiplication Instructions
        # If the result doesn’t fully fit in md (e.g., matrix size mismatch)
        # only the lower columns are updated — the rest are zeroed
    elif func == "0001" and uop == "01" and func3 == "000":
        # mmacc
        size_sup = line[6:9]
        ms2 = line[9:12]
        s_size = line[12:14]
        ms1 = line[14:17]
        d_size = line[20:22]
        md_ms3 = line[22:25]
        
        ms1_v = int(ms1, 2)
        ms2_v = int(ms2, 2)
        md_ms3_v = int(md_ms3, 2)
        
        if (ms1_v not in range(0, 4) 
                or ms2_v not in range(0, 4) 
                or md_ms3_v not in range(4, 8)):
                raise ValueError("Invalid matrix register name")
        
        
        md_list = list(f"{0:02048b}")
        # As integer matrix multiplication operation with non-widen or widen output is
        # uncommon in AI scenarios, the matrix instruction set does not include such
        # instructions by default.The hardware can extend the mmacc.<b/h/w/d> or
        # mmacc.<h/w/d>.<b/h/w> instructions as needed.
        
        # If xmsaten equals 1, the output should be saturated.
        # Otherwise, the mmacc operations ignore the overflow and wrap around the result .
        
        #mmacc.w.q/mmaccu.w.q/mmaccus.w.q/mmaccsu.w.q are illegal if 'mmi4i32' of xmisa register is 0.
        if size_sup == "011" and s_size == "00" and d_size == "10":
            #  mmacc.w.b
            if XMISA["mmi4i32"]["value"] == 0:
                raise ValueError("mmi4i32 extension is not supported")

            
            for i in range(MATRIX_REGISTER["mi"]):
                for j in range(MATRIX_REGISTER["ni"]):
                    c_index = i * ARLEN + j * 32
                    res_val = int(0)
                    for k in range(MATRIX_REGISTER["ki"]):
                        sum_val = int(0)
                        a_index = i * TRLEN + k * 8
                        bt_index = k * TRLEN + j * 8

                        a_val = int(cvt(MATRIX_REGISTER[ms1]["value"][a_index:a_index+8], "sint8", "int"))
                        bt_val = int(cvt(MATRIX_REGISTER[ms2]["value"][bt_index:bt_index+8], "sint8", "int"))
                        sum_val = a_val * bt_val
                        sum_val = apply_saturation(sum_val, 1, True)
                        res_val = res_val + sum_val
                        # For 8-bit x 8-bit operations, use 16-bit saturation for the product
                    res_val = str(bin(res_val))[2:]
                        
                    md_list[c_index:c_index+32] = res_val.zfill(32)
            
        elif size_sup == "000" and s_size == "00" and d_size == "10":
            #  mmaccu.w.b
            if XMISA["mmi8i32"]["value"] == 0:
                raise ValueError("mmi8i32 extension is not supported")
            
            md_list = list(MATRIX_REGISTER[md_ms3]["value"])
            for i in range(MATRIX_REGISTER["mi"]):
                for j in range(MATRIX_REGISTER["ni"]):
                    c_index = i * ARLEN + j * 32
                    res_val = int(0)
                    for k in range(MATRIX_REGISTER["ki"]):
                        sum_val = int(0)
                        a_index = i * TRLEN + k * 8
                        bt_index = k * TRLEN + j * 8

                        a_val = int(cvt(MATRIX_REGISTER[ms1]["value"][a_index:a_index+8], "sint8", "int"))
                        bt_val = int(cvt(MATRIX_REGISTER[ms2]["value"][bt_index:bt_index+8], "sint8", "int"))
                        sum_val = a_val * bt_val
                        sum_val = apply_saturation(sum_val, 1, False)
                        res_val = res_val + sum_val
                        # For 8-bit x 8-bit operations, use 16-bit saturation for the product
                    res_val = str(bin(res_val))[2:]
                        
                    md_list[c_index:c_index+32] = res_val.zfill(32)
            
        elif size_sup == "001" and s_size == "00" and d_size == "10":
            # mmaccus.w.b
            if XMISA["mmi8i32"]["value"] == 0:
                raise ValueError("mmi8i32 extension is not supported")
                       
        elif size_sup == "010" and s_size == "00" and d_size == "10":
            # mmaccsu.w.b
            if XMISA["mmi8i32"]["value"] == 0:
                raise ValueError("mmi8i32 extension is not supported")

            
        # As integer matrix multiplication operation with non-widen or widen output is
        # uncommon in AI scenarios, the matrix instruction set does not include such
        # instructions by default.The hardware can extend the mmacc.<b/h/w/d> or
        # mmacc.<h/w/d>.<b/h/w> instructions as needed
        elif size_sup == "011" and s_size == "01" and d_size == "11":
            # mmacc.d.h
            if XMISA["mmi8i32"]["value"] == 0:
                raise ValueError("mmi8i32 extension is not supported")

        elif size_sup == "000" and s_size == "01" and d_size == "11":
            # mmaccu.d.h
            if XMISA["mmi8i32"]["value"] == 0:
                raise ValueError("mmi8i32 extension is not supported")

        elif size_sup == "001" and s_size == "01" and d_size == "11":
            # mmaccus.d.h
            if XMISA["mmi8i32"]["value"] == 0:
                raise ValueError("mmi8i32 extension is not supported")

        elif size_sup == "010" and s_size == "01" and d_size == "11":
            #  mmaccsu.d.h
            if XMISA["mmi8i32"]["value"] == 0:
                raise ValueError("mmi8i32 extension is not supported")

        elif size_sup == "011" and s_size == "00" and d_size == "10":
            #  mmacc.w.bp
            if XMISA["mmi4i32"]["value"] == 0:
                raise ValueError("mmi4i32 extension is not supported")

        elif size_sup == "000" and s_size == "00" and d_size == "10":
            # mmaccu.w.bp
            if XMISA["mmi4i32"]["value"] == 0:
                raise ValueError("mmi4i32 extension is not supported")

        MATRIX_REGISTER[md_ms3]["value"] = ''.join(md_list)
        
        changed_registers.append({"name": MATRIX_REGISTER[md_ms3]["name"], "value": MATRIX_REGISTER[md_ms3]["value"]})
    # TABLE 5: Matrix Load/Store Instructions
    elif func == "0000" and uop == "01" and func3 == "000":
        # mlae<8/16/32/64> md, rs1, rs2
        # msae<8/16/32/64> ms3, rs1, rs2
        ls = line[6]
        rs2 = line[7:12]
        rs1 = line[12:17]
        d_size = line[20:22]
        md_ms3 = line[22:25]
        
        base_addr = int(REGISTERS[rs1]["value"], 2)
        row_stride = int(REGISTERS[rs2]["value"], 2)
        md_list = MATRIX_REGISTER[md_ms3]["value"]

        if d_size == "00":
            eew = 8
        elif d_size == "01":
            eew = 16
        elif d_size == "10":
            eew = 32
        elif d_size == "11":
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if MATRIX_REGISTER["mi"] > 4:
                raise ValueError("Matrix A has more than 4 rows, which is not supported")
        ROWNUM = MATRIX_REGISTER["mi"]
        if MATRIX_REGISTER["ki"] > TRLEN // eew:
            raise ValueError(f"Matrix A has more than {TRLEN//eew} columns, which is not supported")
        COLNUM = MATRIX_REGISTER["ki"]   
        
        if ls == "0":
            # mlae<8/16/32/64> md, rs1, rs2
            for i in range(ROWNUM):
                for j in range(TRLEN//eew):
                    mem_addr = base_addr + i * row_stride + j * (eew // 8)
                    value = MEMORIES.get_bytes(f"0x{mem_addr:X}", eew//8)
                    md_list[i*TRLEN + j*eew:i*TRLEN + (j+1)*eew] = value
                
            MATRIX_REGISTER[md_ms3]["value"] = ''.join(md_list)
            changed_registers.append({"name": md_ms3, "value": MATRIX_REGISTER[md_ms3]["value"]})
        elif ls == "1":
            # msae<8/16/32/64> ms3, rs1, rs2
            for i in range(ROWNUM):
                for j in range(TRLEN//eew):
                    mem_addr = base_addr + i * row_stride + j * (eew // 8)
                    value = md_list[i*TRLEN + j*eew:i*TRLEN + (j+1)*eew]
                    MEMORIES.set_bytes(f"0x{mem_addr:X}", value, eew//8)
                    
    elif func == "0001" and uop == "01" and func3 == "000":
        # mlbe<8/16/32/64> md, rs1, rs2
        # msbe<8/16/32/64> ms3, rs1,
        ls = line[6]
        rs2 = line[7:12]
        rs1 = line[12:17]
        d_size = line[20:22]
        md_ms3 = line[22:25]
        
        base_addr = int(REGISTERS[rs1]["value"], 2)
        row_stride = int(REGISTERS[rs2]["value"], 2)
        md_list = MATRIX_REGISTER[md_ms3]["value"]

        if d_size == "00":
            eew = 8
        elif d_size == "01":
            eew = 16
        elif d_size == "10":
            eew = 32
        elif d_size == "11":
            eew = 64
        else:
            raise ValueError("Invalid data size")
        

        if MATRIX_REGISTER["ni"] > 4:
            raise ValueError("Matrix B has more than 4 rows, which is not supported")
        ROWNUM = MATRIX_REGISTER["mi"]
        if MATRIX_REGISTER["ki"] > TRLEN // eew:
            raise ValueError(f"Matrix B has more than {TRLEN//eew} columns, which is not supported")
        COLNUM = MATRIX_REGISTER["ki"]        

        if ls == "0":
            # mlbe<8/16/32/64> md, rs1, rs2
            for i in range(ROWNUM):
                for j in range(TRLEN//eew):
                    mem_addr = base_addr + i * row_stride + j * (eew // 8)
                    value = MEMORIES.get_bytes(f"0x{mem_addr:X}", eew//8)
                    md_list[i*TRLEN + j*eew:i*TRLEN + (j+1)*eew] = value
                
            MATRIX_REGISTER[md_ms3]["value"] = ''.join(md_list)
            changed_registers.append({"name": md_ms3, "value": MATRIX_REGISTER[md_ms3]["value"]})
        elif ls == "1":
            # msbe<8/16/32/64> ms3, rs1, rs2
            for i in range(ROWNUM):
                for j in range(TRLEN//eew):
                    mem_addr = base_addr + i * row_stride + j * (eew // 8)
                    value = md_list[i*TRLEN + j*eew:i*TRLEN + (j+1)*eew]
                    MEMORIES.set_bytes(f"0x{mem_addr:X}", value, eew//8)
                    
    elif func == "0010" and uop == "01" and func3 == "000":
        # mlce<8/16/32/64> md, rs1, rs2
        # msce<8/16/32/64> md, rs1, rs2
        ls = line[6]
        rs2 = line[7:12]
        rs1 = line[12:17]
        d_size = line[20:22]
        md_ms3 = line[22:25]
        
        base_addr = int(REGISTERS[rs1]["value"], 2)
        row_stride = int(REGISTERS[rs2]["value"], 2)
        md_list = MATRIX_REGISTER[md_ms3]["value"]

        if d_size == "00":
            eew = 8
        elif d_size == "01":
            eew = 16
        elif d_size == "10":
            eew = 32
        elif d_size == "11":
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if md_ms3 not in range(4, 8):
            raise ValueError("Invalid matrix register for matrix C")
        
        if MATRIX_REGISTER["mi"] > 4:
            raise ValueError("Matrix C has more than 4 rows, which is not supported")      
        ROWNUM = MATRIX_REGISTER["mi"]
        if MATRIX_REGISTER["ni"] > ARLEN // eew:
            raise ValueError(f"Matrix C has more than {ARLEN//eew} columns, which is not supported")
        COLNUM = MATRIX_REGISTER["ni"]
        # Perform the matrix load
        if ls == "0":
            # mlce<8/16/32/64> md, rs1, rs2
            for i in range(ROWNUM):
                for j in range(ARLEN//eew):
                    mem_addr = base_addr + i * row_stride + j * (eew // 8)
                    value = MEMORIES.get_bytes(f"0x{mem_addr:X}", eew//8)
                    md_list[i*ARLEN + j*eew:i*ARLEN + (j+1)*eew] = value
                
            MATRIX_REGISTER[md_ms3]["value"] = ''.join(md_list)
            changed_registers.append({"name": md_ms3, "value": MATRIX_REGISTER[md_ms3]["value"]})
        elif ls == "1":
            # msce<8/16/32/64> ms3, rs1, rs2
            for i in range(ROWNUM):
                for j in range(ARLEN//eew):
                    mem_addr = base_addr + i * row_stride + j * (eew // 8)
                    value = md_list[i*ARLEN + j*eew:i*ARLEN + (j+1)*eew]
                    MEMORIES.set_bytes(f"0x{mem_addr:X}", value, eew//8)
    
    elif func == "0011" and uop == "01" and func3 == "000":
        # mlme<8/16/32/64> md, rs1, rs2
        ls = line[6]
        rs2 = line[7:12]
        rs1 = line[12:17]
        d_size = line[20:22]
        md = line[22:25]
        
        base_addr = int(REGISTERS[rs1]["value"], 2)
        row_stride = int(REGISTERS[rs2]["value"], 2)
        md_list = MATRIX_REGISTER[md]["value"]
        
        if d_size == "00":
            eew = 8
        elif d_size == "01":
            eew = 16
        elif d_size == "10":
            eew = 32
        elif d_size == "11":
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if ls == "0":
            if md in range(0, 4):
                for i in range(4):
                    for j in range(TRLEN//eew):
                        mem_addr = base_addr + i * row_stride + j * (eew // 8)
                        value = MEMORIES.get_bytes(f"0x{mem_addr:X}", eew//8)
                        md_list[i*TRLEN + j*eew:i*TRLEN + (j+1)*eew] = value
            elif md in range(4, 8):
                for i in range(4):
                    for j in range(ARLEN//eew):
                        mem_addr = base_addr + i * row_stride + j * (eew // 8)
                        value = MEMORIES.get_bytes(f"0x{mem_addr:X}", eew//8)
                        md_list[i*ARLEN + j*eew:i*ARLEN + (j+1)*eew] = value
                    
            MATRIX_REGISTER[md]["value"] = ''.join(md_list)
            changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
        elif ls == "1":
            if md in range(0, 4):
                for i in range(4):
                    for j in range(TRLEN//eew):
                        mem_addr = base_addr + i * row_stride + j * (eew // 8)
                        value = md_list[i*TRLEN + j*eew:i*TRLEN + (j+1)*eew]
                        MEMORIES.set_bytes(f"0x{mem_addr:X}", value, eew//8)
            elif md in range(4, 8):
                for i in range(4):
                    for j in range(ARLEN//eew):
                        mem_addr = base_addr + i * row_stride + j * (eew // 8)
                        value = md_list[i*ARLEN + j*eew:i*ARLEN + (j+1)*eew]
                        MEMORIES.set_bytes(f"0x{mem_addr:X}", value, eew//8)
    
    elif func == "0100" and uop == "01" and func3 == "000":
        # mlate<8/16/32/64> md, rs1, rs2
        # msate<8/16/32/64> ms3, rs1, rs2
        ls = line[6]
        rs2 = line[7:12]
        rs1 = line[12:17]
        d_size = line[20:22]
        md = line[22:25]
        
        base_addr = int(REGISTERS[rs1]["value"], 2)
        row_stride = int(REGISTERS[rs2]["value"], 2)
        md_list = MATRIX_REGISTER[md]["value"]
        
        if d_size == "00":
            eew = 8
        elif d_size == "01":
            eew = 16
        elif d_size == "10":
            eew = 32
        elif d_size == "11":
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if md not in range(0, 4):
                raise ValueError("Invalid matrix register for matrix A")
        
        if MATRIX_REGISTER["mi"] > 4:
            raise ValueError("Matrix A has more than 4 rows, which is not supported")
        ROWNUM = MATRIX_REGISTER["mi"]
        if MATRIX_REGISTER["ki"] > TRLEN // eew:
            raise ValueError(f"Matrix A has more than {TRLEN//eew} columns, which is not supported")
        COLNUM = MATRIX_REGISTER["ki"]
        
        if ls == "0":
            # mlate<8/16/32/64> md, rs1, rs2
            for i in range(ROWNUM):
                for j in range(COLNUM):
                    mem_addr = base_addr + j * row_stride + i * (eew // 8)
                    value = MEMORIES.get_bytes(f"0x{mem_addr:X}", eew//8)
                    md_list[i*TRLEN + j*eew:i*TRLEN + (j+1)*eew] = value
            
            MATRIX_REGISTER[md]["value"] = ''.join(md_list)
            changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
        elif ls == "1":
            # msate<8/16/32/64> ms3, rs1, rs2
            for i in range(ROWNUM):
                for j in range(COLNUM):
                    mem_addr = base_addr + j * row_stride + i * (eew // 8)
                    value = md_list[i*TRLEN + j*eew:i*TRLEN + (j+1)*eew]
                    MEMORIES.set_bytes(f"0x{mem_addr:X}", value, eew//8)
        
    elif func == "0101" and uop == "01" and func3 == "000":
        ls = line[6]
        rs2 = line[7:12]
        rs1 = line[12:17]
        d_size = line[20:22]
        md = line[22:25]
        
        base_addr = int(REGISTERS[rs1]["value"], 2)
        row_stride = int(REGISTERS[rs2]["value"], 2)
        md_list = MATRIX_REGISTER[md]["value"]
        
        if d_size == "00":
            eew = 8
        elif d_size == "01":
            eew = 16
        elif d_size == "10":
            eew = 32
        elif d_size == "11":
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if md not in range(0, 4):
            raise ValueError("Invalid matrix register for matrix B")
        
        if MATRIX_REGISTER["ni"] > 4:
            raise ValueError("Matrix B has more than 4 rows, which is not supported")
        ROWNUM = MATRIX_REGISTER["mi"]
        if MATRIX_REGISTER["ki"] > TRLEN // eew:
            raise ValueError(f"Matrix B has more than {TRLEN//eew} columns, which is not supported")
        COLNUM = MATRIX_REGISTER["ki"]
        
        if ls == "0":
            # mlbe<8/16/32/64> md, rs1, rs2
            for i in range(ROWNUM):
                for j in range(COLNUM):
                    mem_addr = base_addr + j * row_stride + i * (eew // 8)
                    value = MEMORIES.get_bytes(f"0x{mem_addr:X}", eew//8)
                    md_list[i*ARLEN + j*eew:i*ARLEN + (j+1)*eew] = value
            
            MATRIX_REGISTER[md]["value"] = ''.join(md_list)
            changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
        elif ls == "1":
            # msbe<8/16/32/64> ms3, rs1, rs2
            for i in range(ROWNUM):
                for j in range(COLNUM):
                    mem_addr = base_addr + j * row_stride + i * (eew // 8)
                    value = md_list[i*ARLEN + j*eew:i*ARLEN + (j+1)*eew]
                    MEMORIES.set_bytes(f"0x{mem_addr:X}", value, eew//8)
                    
    elif func == "0110" and uop == "01" and func3 == "000":
        ls = line[6]
        rs2 = line[7:12]
        rs1 = line[12:17]
        d_size = line[20:22]
        md = line[22:25]
        
        base_addr = int(REGISTERS[rs1]["value"], 2)
        row_stride = int(REGISTERS[rs2]["value"], 2)
        md_list = MATRIX_REGISTER[md]["value"]
        
        if d_size == "00":
            eew = 8
        elif d_size == "01":
            eew = 16
        elif d_size == "10":
            eew = 32
        elif d_size == "11":
            eew = 64
        else:
            raise ValueError("Invalid data size")
        
        if md not in range(4, 8):
            raise ValueError("Invalid matrix register for matrix C")
        
        if MATRIX_REGISTER["mi"] > 4:
            raise ValueError("Matrix C has more than 4 rows, which is not supported")
        ROWNUM = MATRIX_REGISTER["mi"]
        if MATRIX_REGISTER["ni"] > ARLEN // eew:
            raise ValueError(f"Matrix C has more than {ARLEN//eew} columns, which is not supported")
        COLNUM = MATRIX_REGISTER["ki"]
        
        if ls == "0":
            # mlce<8/16/32/64> md, rs1, rs2
            for i in range(ROWNUM):
                for j in range(COLNUM):
                    mem_addr = base_addr + j * row_stride + i * (eew // 8)
                    value = MEMORIES.get_bytes(f"0x{mem_addr:X}", eew//8)
                    md_list[i*ARLEN + j*eew:i*ARLEN + (j+1)*eew] = value
            
            MATRIX_REGISTER[md]["value"] = ''.join(md_list)
            changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
        elif ls == "1":
            # msce<8/16/32/64> ms3, rs1, rs2
            for i in range(ROWNUM):
                for j in range(COLNUM):
                    mem_addr = base_addr + j * row_stride + i * (eew // 8)
                    value = md_list[i*ARLEN + j*eew:i*ARLEN + (j+1)*eew]
                    MEMORIES.set_bytes(f"0x{mem_addr:X}", value, eew//8)
                    
    #TABLE 6: Matrix Element-Wise Instructions
    elif func == "0110" and uop == "00" and func3 == "001":
        ctrl = line[6:9]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        md_list = list(MATRIX_REGISTER[md]["value"])
        
        if ctrl == "001":
            # mscvtl.b.p md, ms1
            if ms1_v in range(0, 4) and md_v in range(0, 4):
                col_index = TRLEN // 4
                for i in range(4):
                    for j in range(col_index // 2):
                        org_val = MATRIX_REGISTER[ms1]["value"][i*TRLEN + (j+col_index)*4:i*TRLEN + (j+col_index+1)*4]
                        if org_val & 0x8:
                            md_list[i*TRLEN + j*8] = "1111" + org_val
                        else:
                            md_list[i*TRLEN + j*8] = "0000" + org_val
            elif ms1_v in range(4, 8) and md_v in range(4, 8):
                col_index = ARLEN // 4
                for i in range(4):
                    for j in range(col_index // 2):
                        org_val = MATRIX_REGISTER[ms1]["value"][i*ARLEN + (j+col_index)*4:i*ARLEN + (j+col_index+1)*4]
                        if org_val & 0x8:
                            md_list[i*ARLEN + j*8] = "1111" + org_val
                        else:
                            md_list[i*ARLEN + j*8] = "0000" + org_val
            else:
                raise ValueError("ms1 and md have different size")
        
        elif ctrl == "011":
            # mscvth.b.p md, ms1
            if ms1_v in range(0, 4) and md_v in range(0, 4):
                col_index = TRLEN // 4
                for i in range(4):
                    for j in range(col_index // 2):
                        org_val = MATRIX_REGISTER[ms1]["value"][i*TRLEN + (j)*4:i*TRLEN + (j+1)*4]
                        if org_val & 0x8:
                            md_list[i*TRLEN + j*8] = "1111" + org_val
                        else:
                            md_list[i*TRLEN + j*8] = "0000" + org_val
            elif ms1_v in range(4, 8) and md_v in range(4, 8):
                col_index = ARLEN // 4
                for i in range(4):
                    for j in range(col_index // 2):
                        org_val = MATRIX_REGISTER[ms1]["value"][i*ARLEN + (j)*4:i*ARLEN + (j+1)*4]
                        if org_val & 0x8:
                            md_list[i*ARLEN + j*8] = "1111" + org_val
                        else:
                            md_list[i*ARLEN + j*8] = "0000" + org_val
            else:
                raise ValueError("ms1 and md have different size")
            
        elif ctrl == "000":
            # mucvtl.b.p
            if ms1_v in range(0, 4) and md_v in range(0, 4):
                col_index = TRLEN // 4
                for i in range(4):
                    for j in range(col_index // 2):
                        org_val = MATRIX_REGISTER[ms1]["value"][i*TRLEN + (j+col_index)*4:i*TRLEN + (j+col_index+1)*4]
                        md_list[i*TRLEN + j*8] = "0000" + org_val
            elif ms1_v in range(4, 8) and md_v in range(4, 8):
                col_index = ARLEN // 4
                for i in range(4):
                    for j in range(col_index // 2):
                        org_val = MATRIX_REGISTER[ms1]["value"][i*ARLEN + (j+col_index)*4:i*ARLEN + (j+col_index+1)*4]
                        md_list[i*ARLEN + j*8] = "0000" + org_val
            else:
                raise ValueError("ms1 and md have different size")
        
        elif ctrl == "010":
            # mucvth.b.p md, ms1
            if ms1_v in range(0, 4) and md_v in range(0, 4):
                col_index = TRLEN // 4
                for i in range(4):
                    for j in range(col_index // 2):
                        org_val = MATRIX_REGISTER[ms1]["value"][i*TRLEN + (j)*4:i*TRLEN + (j+1)*4]
                        md_list[i*TRLEN + j*8] = "0000" + org_val
            elif ms1_v in range(4, 8) and md_v in range(4, 8):
                col_index = ARLEN // 4
                for i in range(4):
                    for j in range(col_index // 2):
                        org_val = MATRIX_REGISTER[ms1]["value"][i*ARLEN + (j)*4:i*ARLEN + (j+1)*4]
                        md_list[i*ARLEN + j*8] = "0000" + org_val
            else:
                raise ValueError("ms1 and md have different size")
            
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})

    elif func == "0000" and uop == "10" and func3 == "001":
        # madd
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        
        if ctrl == "111":
            # madd.w.mm md, ms2, ms1
            for i in range(4):
                for j in range(ARLEN // 32):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)

                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)

                    res_value = ms1_value + ms2_value
                    if res_value < 0 and abs(res_value) > 0xFFFFFFFF:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0xFFFFFFFF
                    elif res_value > 0 and res_value > 0x80000000:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0x7FFFFFFF
                    else:
                        if res_value & 0x80000000:
                            res_value += (1 << 32)
                    
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(res_value))[2:].zfill(32)
        else:
            # madd.w.mv.i md, ms2, ms1[imm3]
            ctrl_v = int(ctrl, 2) % 4
            for i in range(4):
                for j in range(ARLEN // 32):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)

                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)

                    res_value = ms1_value + ms2_value
                    if res_value < 0 and abs(res_value) > 0xFFFFFFFF:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0xFFFFFFFF
                    elif res_value > 0 and res_value > 0x80000000:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0x7FFFFFFF
                    else:
                        if res_value & 0x80000000:
                            res_value += (1 << 32)
                    
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(res_value))[2:].zfill(32)
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
    
    elif func == "0001" and uop == "01" and func3 == "001":
        # msub
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        
        if ctrl == "111":
            # msub.w.mm md, ms2, ms1
            for i in range(4):
                for j in range(ARLEN // 32):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)

                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)

                    res_value = ms1_value - ms2_value
                    if res_value < 0 and abs(res_value) > 0xFFFFFFFF:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0xFFFFFFFF
                    elif res_value > 0 and res_value > 0x80000000:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0x7FFFFFFF
                    else:
                        if res_value & 0x80000000:
                            res_value += (1 << 32)
                    
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(res_value))[2:].zfill(32)
        else:
            # msub.w.mv.i md, ms2, ms1[uimm3]
            ctrl_v = int(ctrl, 2) % 4
            for i in range(4):
                for j in range(ARLEN // 32):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)

                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)

                    res_value = ms1_value - ms2_value
                    if res_value < 0 and abs(res_value) > 0xFFFFFFFF:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0xFFFFFFFF
                    elif res_value > 0 and res_value > 0x80000000:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0x7FFFFFFF
                    else:
                        if res_value & 0x80000000:
                            res_value += (1 << 32)
                    
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(res_value))[2:].zfill(32)
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
        
    elif func == "0010" and uop == "01" and func3 == "001":
        # mmul
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        
        if ctrl == "111":
            # mmul.w.mm md, ms2, ms1
            for i in range(4):
                for j in range(ARLEN // 32):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)

                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)

                    res_value = ms1_value * ms2_value
                    if res_value < 0 and abs(res_value) > 0xFFFFFFFF:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0xFFFFFFFF
                    elif res_value > 0 and res_value > 0x80000000:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0x7FFFFFFF
                    else:
                        if res_value & 0x80000000:
                            res_value += (1 << 32)
                    
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(res_value))[2:].zfill(32)
        else:
            # msub.w.mv.i md, ms2, ms1[uimm3]
            ctrl_v = int(ctrl, 2) % 4
            for i in range(4):
                for j in range(ARLEN // 32):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)

                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)

                    res_value = ms1_value * ms2_value
                    if res_value < 0 and abs(res_value) > 0xFFFFFFFF:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0xFFFFFFFF
                    elif res_value > 0 and res_value > 0x80000000:
                        XMCSR["xmsat"]["value"] = "1"
                        res_value = 0x7FFFFFFF
                    else:
                        if res_value & 0x80000000:
                            res_value += (1 << 32)
                    
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(res_value))[2:].zfill(32)
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
    
    elif func == "0100" and uop == "01" and func3 == "001":
        # mmax
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        col_index = ARLEN // 32
        
        if ctrl == "111":
            # mmax.w.mm
            for i in range(4):
                for j in range(col_index):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    
                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)
                    
                    if ms1_value > ms2_value:
                        md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32]
                    else:
                        md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32]

        else:
            # mmax.w.mv.i
            ctrl_v = int(ctrl, 2) % 4
            
            for i in range(4):
                for j in range(col_index):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    
                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)
                    
                    if ms1_value > ms2_value:
                        md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32]
                    else:
                        md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32]

        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})

    elif func == "0101" and uop == "01" and func3 == "001":
        # mumax
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        col_index = ARLEN // 32
        if ctrl == "111":
            #  mumax.w.mm md, ms2, ms1
            for i in range(4):
                for j in range(col_index):
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = max(
                        str(bin(int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2))[2:].zfill(32)),
                        str(bin(int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2))[2:].zfill(32))
                    )
        else:
            # mumax.w.mv.i md, ms2, ms1[uimm3]
            ctrl_v = int(ctrl, 2) % 4
            for i in range(4):
                for j in range(col_index):
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = max(
                        str(bin(int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2))[2:].zfill(32)),
                        str(bin(int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2))[2:].zfill(32))
                    )

        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
    
    elif func == "0110" and uop == "01" and func3 == "001":
        # mmin
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        col_index = ARLEN // 32
        
        if ctrl == "111":
            # mmin.w.mm
            for i in range(4):
                for j in range(col_index):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    
                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)
                    
                    if ms1_value < ms2_value:
                        md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32]
                    else:
                        md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32]

        else:
            # mmin.w.mv.i
            ctrl_v = int(ctrl, 2) % 4
            
            for i in range(4):
                for j in range(col_index):
                    ms1_value = int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2)
                    ms2_value = int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2)
                    
                    if ms1_value & 0x80000000:
                        ms1_value -= (1 << 32)
                    if ms2_value & 0x80000000:
                        ms2_value -= (1 << 32)
                    
                    if ms1_value < ms2_value:
                        md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32]
                    else:
                        md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32]

        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})

    elif func == "0111" and uop == "01" and func3 == "001":
        # mumin
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        col_index = ARLEN // 32
        if ctrl == "111":
            #  mumin.w.mm md, ms2, ms1
            for i in range(4):
                for j in range(col_index):
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = min(
                        str(bin(int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2))[2:].zfill(32)),
                        str(bin(int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2))[2:].zfill(32))
                    )
        else:
            # mumin.w.mv.i md, ms2, ms1[uimm3]
            ctrl_v = int(ctrl, 2) % 4
            for i in range(4):
                for j in range(col_index):
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = min(
                        str(bin(int(MATRIX_REGISTER[ms2]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2))[2:].zfill(32)),
                        str(bin(int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2))[2:].zfill(32))
                    )

        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
    
    elif func == "1000" and uop == "01" and func3 == "001":
        # msrl
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        col_index = ARLEN // 32
        
        if ctrl == "111":
            # msrl.w.mm md, ms2, ms1
            for i in range(4):
                for j in range(col_index):
                    shift_number = int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2) % 32
                    org_val = int(MATRIX_REGISTER[md]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32],2) 
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(org_val >> shift_number)).zfill(32)
        else:
            # msrl.w.mv.i md, ms2, ms1[uimm3]
            ctrl_v = int(ctrl, 2) % 4
            for i in range(4):
                for j in range(col_index):
                    shift_number = int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2) % 32
                    org_val = int(MATRIX_REGISTER[md]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32],2) 
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(org_val >> shift_number)).zfill(32)
        
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
        
    elif func == "1001" and uop == "01" and func3 == "001":
        # msll
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        col_index = ARLEN // 32
        
        if ctrl == "111":
            # msll.w.mm md, ms2, ms1
            for i in range(4):
                for j in range(col_index):
                    shift_number = int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2) % 32
                    org_val = int(MATRIX_REGISTER[md]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2) 
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(org_val << shift_number)).zfill(32)
        else:
            # msll.w.mv.i md, ms2, ms1[uimm3]
            ctrl_v = int(ctrl, 2) % 4
            for i in range(4):
                for j in range(col_index):
                    shift_number = int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2) % 32
                    org_val = int(MATRIX_REGISTER[md]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2) 
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(org_val << shift_number)).zfill(32)

        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
    elif func == "1010" and uop == "01" and func3 == "001":
        # msra
        ctrl = line[6:9]
        ms2 = line[9:12]
        ms1 = line[14:17]
        md = line[22:25]
        
        ms2_v = int(ms2, 2)
        ms1_v = int(ms1, 2)
        md_v = int(md, 2)
        
        if XMISA["miew"]["value"] == 0 or XMISA["mmi8i32"]["value"] == 0:
            raise ValueError("miew or mmi8i32 extension is not supported")

        if ms1_v not in range(4, 8) or ms2_v not in range(4, 8) or md_v not in range(4, 8):
            raise ValueError("Invalid matrix register for ms1, ms2 or md")

        md_list = list(MATRIX_REGISTER[md]["value"])
        col_index = ARLEN // 32
        
        if ctrl == "111":
            # msra.w.mm md, ms2, ms1
            for i in range(4):
                for j in range(col_index):
                    shift_number = int(MATRIX_REGISTER[ms1]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2) % 32
                    org_val = int(MATRIX_REGISTER[md]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32], 2) 
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = str(bin(org_val >> shift_number)).zfill(32)
        else:
            # msra.w.mv.i md, ms2, ms1[uimm3]
            ctrl_v = int(ctrl, 2) % 4
            for i in range(4):
                for j in range(col_index):
                    shift_number = int(MATRIX_REGISTER[ms1]["value"][ctrl_v*ARLEN + j*32:ctrl_v*ARLEN + (j+1)*32], 2) % 32
                    org_val = MATRIX_REGISTER[md]["value"][i*ARLEN + j*32:i*ARLEN + (j+1)*32]
                    md_list[i*ARLEN + j*32:i*ARLEN + (j+1)*32] = org_val[32-shift_number:] + org_val[0:32-shift_number] 
    
        MATRIX_REGISTER[md]["value"] = ''.join(md_list)
        changed_registers.append({"name": MATRIX_REGISTER[md]["name"], "value": MATRIX_REGISTER[md]["value"]})
    
    MSTATUS["MS"]["value"] = "11"
    #=========================================
    print_register_changes(changed_registers)
    
    
                    
    if pc1 != int(current_address, 2):
        return current_address
    else:
        pc1 = pc1 + 4
        return bin(pc1)[2:].zfill(32)
    

def PrintMemory(output_file_path):
    with open(output_file_path, "w") as output_file:
        base_address = 0x10010000
        for i in range(0, len(MEMORIES), 8):
            output_file.write(f"0x{base_address + i * 4:08X}    ")
            for j in range(0, 32, 4):
                output_file.write(f"{MEMORIES.get_bytes(base_address + i + j, 1):08X} ")
            output_file.write("\n")

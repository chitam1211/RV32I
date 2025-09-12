# **Bước 5: Phân tách lệnh thành các trường**
from preprocess_normalize import normalize_operands
import re
from op_funct_regs import *
from label_instfmt import get_instruction_format
def parse_instruction(nlb_file, line, labels, current_address):
    """
    Phân tích lệnh và trả về mã nhị phân.
    - line: dòng lệnh cần phân tích.
    - labels: từ điển chứa nhãn và địa chỉ tương ứng.
    - current_address: địa chỉ hiện tại của lệnh, dùng cho tính toán offset.
    """
    line = normalize_operands(line)

    parts = line.split(maxsplit=1)  # Tách chỉ instruction và phần còn lại
    instruction = parts[0]
    
    if len(parts) < 2:
        if instruction == "NOP":
            return "00000000000000000000000000010011"  # NOP mã máy
        raise ValueError(f"Lệnh {instruction} không hợp lệ hoặc thiếu toán hạng.")
    
    # Xử lý toán hạng: loại bỏ khoảng trắng và kiểm tra dấu phẩy
    operands = [op.strip() for op in parts[1].split(",") if op.strip()]
    
    # Xử lý lệnh giả
    if instruction == "LI":  # Load Immediate
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng.")
    
        rd = map_register(operands[0])
        imm = int(operands[1], 0)  # Chuyển immediate từ mọi định dạng
    
        if -2048 <= imm <= 2047:  # Immediate trong khoảng 12 bit
            # LI chuyển thành ADDI rd, x0, imm
            return parse_instruction(nlb_file, f"ADDI {rd}, ZERO, {imm}", labels, current_address)
        else:
            # LI với giá trị lớn hơn 12 bit cần LUI và ADDI
            upper = (imm + (1 << 11)) >> 12  # Làm tròn giá trị upper
            lower = imm - (upper << 12)     # Lấy phần còn lại (bù 2 đúng)

            # Kiểm tra nếu lower là số âm
            if lower < 0:
                lower &= 0xFFF  # Biểu diễn lower dưới dạng bù 2 (12 bit)
        
            instructions = [
                f"LUI {rd}, {upper}",
                f"ADDI {rd}, {rd}, {lower}"
            ]
            print(current_address)
            return [parse_instruction(nlb_file, instr, labels, current_address - idx * 4) 
                for idx, instr in enumerate(instructions)]

    elif instruction == "MV":  # Move (MV rd, rs) -> ADDI rd, rs, 0
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng.")
        rd = map_register(operands[0])
        rs = map_register(operands[1])
        return parse_instruction(f"ADDI {rd}, {rs}, 0", labels, current_address)
    # Xử lý lệnh BGT
    elif instruction == "BGT":  # Branch if Greater Than
        if len(operands) != 3:
            raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng.")
        
        rs1 = map_register(operands[0])
        rs2 = map_register(operands[1])
        label = operands[2]

        # Tính toán offset
        if label not in labels:
            raise ValueError(f"Nhãn {label} không được định nghĩa.")
        # Thay thế BGT bằng BLT với thanh ghi đảo ngược
        return parse_instruction(nlb_file, f"BLT {rs2}, {rs1}, {label}", labels, current_address)
    fmt = get_instruction_format(instruction)

    # Xử lý lệnh theo định dạng
    if fmt == "R":
        if len(operands) != 3:
            raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        rd = REGISTERS[map_register(operands[0])]["binary"]
        rs1 = REGISTERS[map_register(operands[1])]["binary"]
        rs2 = REGISTERS[map_register(operands[2])]["binary"]
        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]
        funct7 = FUNCT7[instruction]
        print(f"Lệnh: {instruction} | funct7: {funct7} | rs2: {rs2} | rs1: {rs1} | funct3: {funct3} | rd: {rd} | opcode: {opcode}")
        return f"{funct7}{rs2}{rs1}{funct3}{rd}{opcode}"

    elif fmt == "I":
        if instruction == "JALR":
            # Kiểm tra số lượng toán hạng và thiết lập giá trị mặc định
            rd, rs1, imm = "X1", None, 0  # Mặc định: rd = X1 (RA), imm = 0

            if len(operands) == 3:
                # Trường hợp đầy đủ: jalr rd, rs1, imm
                rd = map_register(operands[0].strip())
                rs1 = map_register(operands[1].strip())
                imm = int(operands[2].strip(), 0)
            elif len(operands) == 2:
                if "(" in operands[1]:
                # Trường hợp: jalr rd, imm(rs1)
                    rd = map_register(operands[0].strip())
                    imm_str, rs1_str = operands[1].split("(")
                    imm = int(imm_str.strip(), 0)
                    rs1 = map_register(rs1_str.strip(" )"))
                elif operands[1].isdigit() or (operands[1][0] == '-' and operands[1][1:].isdigit()):
                    # Trường hợp: jalr rs1, imm
                    rs1 = map_register(operands[0].strip())
                    imm = int(operands[1].strip(), 0)
            elif len(operands) == 1:
                # Trường hợp: jalr rs1 (chỉ có rs1, mặc định rd = X1, imm = 0)
                rs1 = map_register(operands[0].strip())
            else:
                raise ValueError(f"Lệnh {instruction} yêu cầu từ 1 đến 3 toán hạng nhưng có {len(operands)}.")

            # Kiểm tra giá trị immediate
            if imm < -2048 or imm > 2047:
                raise ValueError(f"Giá trị immediate vượt quá phạm vi: {imm} (phải trong [-2048, 2047])")
            imm_bin = f"{imm & 0xFFF:012b}"  # Chuyển thành nhị phân 12 bit

            # Lấy mã nhị phân cho rd và rs1
            rd_bin = REGISTERS[rd]["binary"]
            rs1_bin = REGISTERS[rs1]["binary"]

            # Lấy opcode và funct3
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]

            print(f"Lệnh: {instruction} | imm_bin: {imm_bin} | rs1: {rs1_bin} | funct3: {funct3} | rd: {rd_bin} | opcode: {opcode}")
            return f"{imm_bin}{rs1_bin}{funct3}{rd_bin}{opcode}"
        elif instruction in ["LB", "LH", "LW", "LBU", "LHU"]:  # Lệnh dạng I với offset
            if len(operands) != 2:
                raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")

            rd = REGISTERS[map_register(operands[0])]["binary"]  # Đăng ký đích

            # Tách offset và base trước khi ánh xạ
            operand_pattern = r"^\s*(-?\d+)\s*\(\s*(\w+)\s*\)$"
            match = re.match(operand_pattern, operands[1])

            if not match:
                raise ValueError(f"Lệnh {instruction} có cú pháp offset(base) không hợp lệ: {operands[1]}.")

            offset, base_alias = match.groups()

            # Ánh xạ base từ alias (ví dụ: A2 -> x12)
            base_register = map_register(base_alias)
            if base_register not in REGISTERS:
                raise ValueError(f"Thanh ghi {base_alias} không hợp lệ.")

            rs1 = REGISTERS[base_register]["binary"]

            # Xử lý offset và kiểm tra phạm vi
            try:
                imm = int(offset)
            except ValueError:
                raise ValueError(f"Offset không hợp lệ: {offset} phải là một số nguyên.")

            if not -2048 <= imm <= 2047:
                raise ValueError(f"Offset {imm} vượt quá phạm vi 12 bit: -2048 đến 2047.")

            imm_bin = f"{imm & 0xFFF:012b}"  # Chuyển offset thành 12 bit

            # Lấy opcode và funct3
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]

            print(f"Lệnh: {instruction} | imm_bin: {imm_bin} | rs1: {rs1} | funct3: {funct3} | rd: {rd} | opcode: {opcode}")
            return f"{imm_bin}{rs1}{funct3}{rd}{opcode}"

        elif instruction in ["SLLI", "SRLI", "SRAI"]:  # Lệnh dịch bit
            if len(operands) != 3:
                raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        
            rd = REGISTERS[map_register(operands[0])]["binary"]  # Đăng ký đích
            rs1 = REGISTERS[map_register(operands[1])]["binary"]  # Đăng ký nguồn
            shamt = int(operands[2])  # Giá trị dịch
            shamt_bin = f"{shamt & 0x1F:05b}"  # 5 bit dịch (dành cho RV32I)
        
            if instruction == "SRAI":
                funct7 = "0100000"  # Giá trị cho SRAI
            else:
                funct7 = "0000000"  # Giá trị cho SLLI và SRLI
        
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]
            print(f"Lệnh: {instruction} | funct7: {funct7} | shamt_bin: {shamt_bin} | rs1: {rs1} | funct3: {funct3} | rd: {rd} | opcode: {opcode}")
            return f"{funct7}{shamt_bin}{rs1}{funct3}{rd}{opcode}"

        else:  # Lệnh I-format dạng hằng số
            if len(operands) != 3:
                raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
        
            rd = REGISTERS[map_register(operands[0])]["binary"]  # Đăng ký đích
            rs1 = REGISTERS[map_register(operands[1])]["binary"]  # Đăng ký nguồn
            imm = int(operands[2], 0)  # Chấp nhận cả số thập phân và hexa
            imm_bin = f"{imm & 0xFFF:012b}"  # Mask để đảm bảo chỉ 12 bit
        
            opcode = OPCODES[instruction]
            funct3 = FUNCT3[instruction]
            print(f"Lệnh: {instruction} | imm_bin: {imm_bin} | rs1: {rs1} | funct3: {funct3} | rd: {rd} | opcode: {opcode}")
            return f"{imm_bin}{rs1}{funct3}{rd}{opcode}"

    elif fmt == "S":
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")

        # Lấy rs2 từ toán hạng thứ nhất
        rs2_alias = operands[0]
        rs2 = REGISTERS[map_register(rs2_alias)]["binary"]  # Đăng ký nguồn 2

        # Phân tích offset và base từ toán hạng thứ hai
        operand_pattern = r"^\s*(-?\d+)\s*\(\s*(\w+)\s*\)$"
        match = re.match(operand_pattern, operands[1])

        if not match:
            raise ValueError(f"Lệnh {instruction} có cú pháp offset(base) không hợp lệ: {operands[1]}.")

        offset, base_alias = match.groups()

        # Ánh xạ base alias sang dạng xN
        rs1 = map_register(base_alias)
        if rs1 not in REGISTERS:
            raise ValueError(f"Thanh ghi {base_alias} không hợp lệ.")

        rs1 = REGISTERS[rs1]["binary"]  # Đăng ký base đã chuyển đổi

        # Xử lý offset và phân chia thành 7 bit cao và 5 bit thấp
        try:
            imm = int(offset)
        except ValueError:
            raise ValueError(f"Offset không hợp lệ: {offset} phải là một số nguyên.")

        if not -2048 <= imm <= 2047:
            raise ValueError(f"Offset {imm} vượt quá phạm vi 12 bit: -2048 đến 2047.")

        # Xử lý offset dưới dạng bù 2
        imm = int(offset) & 0xFFF  # Offset đảm bảo trong phạm vi 12-bit
        imm_bin = f"{imm:012b}"    # Chuyển offset thành nhị phân 12-bit
        imm_high = imm_bin[:7]     # 7 bit cao
        imm_low = imm_bin[7:]      # 5 bit thấp
        # Lấy opcode và funct3
        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]
        print(f"Lệnh: {instruction} | imm_high: {imm_high} | rs2: {rs2} | rs1: {rs1} | funct3: {funct3} | imm_low: {imm_low} | opcode: {opcode}")
        return f"{imm_high}{rs2}{rs1}{funct3}{imm_low}{opcode}"

    elif fmt == "B":
        if len(operands) != 3:
            raise ValueError(f"Lệnh {instruction} yêu cầu 3 toán hạng nhưng chỉ có {len(operands)}.")
    
        # Lấy thông tin thanh ghi rs1 và rs2
        rs1 = REGISTERS[map_register(operands[0].strip())]["binary"]
        rs2 = REGISTERS[map_register(operands[1].strip())]["binary"]

        # Lấy thông tin nhãn và tính toán offset
        label = operands[2].strip()

        # Kiểm tra nhãn có tồn tại trong labels hay không
        if label not in labels:
            raise ValueError(f"Nhãn '{label}' không tồn tại trong bảng labels: {labels}")
        # Địa chỉ mục tiêu (target address) tính bằng byte
        target_address = labels[label] * 4  # Nhân với 4 để chuyển từ dòng sang byte
        # Tìm số dòng trống (nhãn) giữa current và target
        start = min(current_address // 4, target_address // 4)  # Lấy dòng nhỏ hơn
        end = max(current_address // 4, target_address // 4)    # Lấy dòng lớn hơn
        bts = 0
        with open(nlb_file, "r") as f:
            lines = f.readlines()
            for i in range(start, end):
                if not lines[i].strip():  # Dòng trống là nhãn
                    bts += 1
        # Kiểm tra hiu
        hiu = False
        if target_address // 4 < len(lines) - 1:  # Nếu nhãn không phải dòng cuối
            next_line = lines[target_address // 4 + 1].strip()
            if next_line:  # Nếu ngay sau nhãn có lệnh
                hiu = True
        li_detected = False
        t_lines = []
        with open(nlb_file, "r") as f:
            line = f.readlines()
            t_lines = line[start:end]
        for line in t_lines:
            line = line.strip()
            if line.upper().startswith("LI"):
                li_parts = line.split(maxsplit=1)
                if len(li_parts) == 2 and li_parts[0].upper() == "LI":
                    imm_split = li_parts[1].split(",")
                    if len(imm_split) > 1:
                        imm_value = imm_split[1].strip()
                        imm_value = int(imm_value, 0)
                        if imm_value > 2047 or imm_value < -2048:
                            li_detected = True
        print(f"Li detected: {li_detected}")
        # Tính offset
        if target_address > current_address and li_detected:
            offset = (target_address - current_address)  - (bts * 4) + 8
        elif target_address > current_address and not li_detected:
            offset = (target_address - current_address)  - (bts * 4) + 4
        elif target_address < current_address and li_detected:
            offset = (target_address - current_address)  + (bts * 4) 
        else:
            offset = (target_address - current_address)  + (bts * 4) + 4
        if offset < -4096 or offset > 4095:
            raise ValueError(f"Offset {offset} vượt quá phạm vi cho phép (-2^12 đến 2^12-1).")
        # Chuyển offset thành nhị phân (13 bit)
        imm_bin = f"{offset & 0x1FFF:013b}"
        print(f"Label to find: {label} | hiu: {hiu} | bts: {bts} | current_address: {current_address} | target_address: {target_address} | offset: {offset} | imm_bin: {imm_bin}")
        if offset < 0:
            imm_bin = imm_bin[:-1] + '1'  # Thay bit cuối thành 1
        # Sắp xếp lại các bit theo định dạng B
        imm_high = imm_bin[0] + imm_bin[2:8]  # Bit [12], [10:5]
        imm_low = imm_bin[8:]                # Bit [4:1], [11]
        # Tạo mã máy theo định dạng B
        opcode = OPCODES[instruction]
        funct3 = FUNCT3[instruction]
        print(f"Lệnh: {instruction} | imm_high: {imm_high} | rs2: {rs2} | rs1: {rs1} | funct3: {funct3} | imm_low: {imm_low} | opcode: {opcode}")
        return f"{imm_high}{rs2}{rs1}{funct3}{imm_low}{opcode}"

    elif fmt == "U":
        if len(operands) != 2:
            raise ValueError(f"Lệnh {instruction} yêu cầu 2 toán hạng nhưng chỉ có {len(operands)}.")
        rd = REGISTERS[map_register(operands[0])]["binary"]
        imm = int(operands[1], 0)  # Immediate được lấy trực tiếp từ operands
        if imm >= 2**20 or imm < -(2**19):  # Kiểm tra giá trị immediate hợp lệ
            raise ValueError(f"Immediate {imm} vượt quá phạm vi 20 bit cho lệnh {instruction}.")
        imm_bin = f"{imm & 0xFFFFF:020b}"  # Mask để đảm bảo chỉ lấy 20 bit cao nhất
        opcode = OPCODES[instruction]
        print(f"Lệnh: {instruction} | imm_bin: {imm_bin} | rd: {rd} | opcode: {opcode}")
        return f"{imm_bin}{rd}{opcode}"

    elif fmt == "J":
        if len(operands) == 2:
            # Trường hợp đầy đủ: jal rd, label
            rd = REGISTERS[map_register(operands[0].strip())]["binary"]
            label_operand = operands[1].strip()
        elif len(operands) == 1:
            # Trường hợp thiếu rd: jal label (mặc định rd = RA hoặc X1)
            rd = REGISTERS[map_register("RA")]["binary"]  # RA là alias của X1
            label_operand = operands[0].strip()
        else:
            raise ValueError(f"Lệnh {instruction} yêu cầu 1 hoặc 2 toán hạng nhưng có {len(operands)}.")
        # Lấy thông tin nhãn
        label_info = labels.get(label_operand)
        if label_info is None:
            raise ValueError(f"Nhãn {label_operand} không tìm thấy.")
        target_address = label_info * 4  # Nhân với 4 để tính địa chỉ byte
        temp_file = r"E:\NCKH\risc  v assembler\temp.txt"
        # Tìm số dòng trống (nhãn) giữa current và target
        start = min(current_address // 4, target_address // 4)  # Lấy dòng nhỏ hơn
        end = max(current_address // 4, target_address // 4)    # Lấy dòng lớn hơn
        bts = 0
        with open(nlb_file, "r") as f:
            lines = f.readlines()
            for i in range(start, end):
                if not lines[i].strip():  # Dòng trống là nhãn
                    bts += 1
        li_founded = False
        temp_lines = []
        with open(nlb_file, "r") as f:
            line = f.readlines()
            temp_lines = line[start:end]
        for line in temp_lines:
            line = line.strip()
            print(line)
            if line.upper().startswith("LI"):
                li_parts = line.split(maxsplit=1)
                if len(li_parts) == 2 and li_parts[0].upper() == "LI":
                    imm_split = li_parts[1].split(",")
                    if len(imm_split) > 1:
                        imm_value = imm_split[1].strip()
                        imm_value = int(imm_value, 0)
                        if imm_value > 2047 or imm_value < -2048:
                            li_founded = True
        print(f"Li founded: {li_founded}")
        if target_address > current_address and li_founded:
            offset = (target_address - current_address)  - (bts * 4) + 8
        elif target_address > current_address and not li_founded:
            offset = (target_address - current_address)  - (bts * 4) + 4
        elif target_address <current_address and li_founded:
            offset = (target_address - current_address)  + (bts * 4) 
        else:
            offset = (target_address - current_address)  + (bts * 4) + 4
        if offset < -1048576 or offset > 1048575:
            raise ValueError(f"Offset {offset} vượt quá phạm vi cho phép (-2^20 đến 2^20-1).")
        # Chuyển đổi offset thành nhị phân (20 bit)
        if offset < 0:
        # Nếu offset âm, thực hiện bù 2 với 21 bit (giữ bit dấu đúng ở đầu)
            offset_bin = f"{(offset + (1 << 21)) & 0x1FFFFF:021b}"
        else:
        # Nếu offset dương, trực tiếp chuyển thành 21 bit nhị phân
            offset_bin = f"{offset & 0x1FFFFF:021b}"
        print(f"offset: {offset}|current_address: {current_address} | target_address: {target_address} | label_info: {label_info} | bts: {bts} | offset_bin: {offset_bin}")
        imm20 = offset_bin[0]        # Bit thứ 20 (MSB)
        imm19_12 = offset_bin[1:9]   # Bit từ 19 đến 12 (8 bit)
        imm11 = offset_bin[9]        # Bit thứ 11
        imm10_1 = offset_bin[10:20]  # Bit từ 10 đến 1 (10 bit, bao gồm index 10 đến 19)
        opcode = OPCODES[instruction]
        print(f"Lệnh: {instruction} | imm20: {imm20} | imm10_1: {imm10_1} | imm11: {imm11} | imm19_12: {imm19_12} | rd: {rd} | opcode: {opcode}")
        return f"{imm20}{imm10_1}{imm11}{imm19_12}{rd}{opcode}"
    else:
        raise ValueError(f"Định dạng lệnh {instruction} không được hỗ trợ.")

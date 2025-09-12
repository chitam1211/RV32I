# **Bước 3: Tìm bảng băm LABEL và địa chỉ tương ứng**
import re 
def find_labels(temp_file, nlb_file):
    labels = {}
    with open(temp_file, "r") as infile:
        lines = infile.readlines()

    # Mở file nlb_file để ghi
    with open(nlb_file, "w") as outfile:
        for idx, line in enumerate(lines, start = 1):
            stripped_line = line.strip()
            
            # Kiểm tra xem dòng có phải là label hay không
            if stripped_line.endswith(":"):  
                label = stripped_line.split(":")[0].strip()
                labels[label] = idx  # Lưu vị trí dòng của label
                outfile.write("\n")  # Ghi dòng trống vào file nlb_file
            else:
                outfile.write(line)  # Ghi dòng lệnh vào file nlb_file
    return labels
# **Bước 4: Xác định định dạng lệnh**
def get_instruction_format(instruction):
    r_format = ["ADD", "SUB", "SLL", "SRL", "SRA", "AND", "OR", "XOR", "SLT", "SLTU","SC.W","AMOSWAP.W","AMOADD.W","AMOXOR.W","AMOAND.W","AMOOR.W","AMOMIN.W","AMOMAX.W","AMOMINU.W","AMOMAXU.W"]
    i_format = ["ADDI", "SLTI", "SLTIU", "XORI", "ORI", "ANDI", "LB", "LH", "LW", "LBU", "LHU", "JALR","SLLI","SRLI","SRAI"]
    s_format = ["SB", "SH", "SW"]
    b_format = ["BEQ", "BNE", "BLT", "BGE", "BLTU", "BGEU"]
    u_format = ["LUI", "AUIPC"]
    j_format = ["JAL"]

    if instruction in r_format:
        return "R"
    elif instruction in i_format:
        return "I"
    elif instruction in s_format:
        return "S"
    elif instruction in b_format:
        return "B"
    elif instruction in u_format:
        return "U"
    elif instruction in j_format:
        return "J"
    else:
        return None

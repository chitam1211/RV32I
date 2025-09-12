# **Bước 6: Chuyển các trường thành chuỗi bit và lưu file**
from label_instfmt import get_instruction_format
from label_instfmt import find_labels 
from parse_instruction import parse_instruction
def assemble(nlb_file, output_file, labels):
    """
    Dịch file assembler thành mã máy và lưu vào file output.
    - temp_file: file chứa các lệnh assembler đã xử lý (file nlb, có dòng trống cho labels).
    - output_file: file đầu ra chứa mã máy dưới dạng hex.
    - labels: từ điển chứa nhãn và địa chỉ tương ứng.
    """
    with open(nlb_file, "r") as infile, open(output_file, "w") as outfile:
        lines = infile.readlines()
        pc = 4  # Program counter (địa chỉ hiện tại, tính bằng byte, bắt đầu từ 0)

        for line in lines:
            line = line.strip()
            if not line:  # Nếu dòng trống, chỉ tăng PC, không xử lý lệnh
                pc += 4
                continue
            try:
                binary_instruction = parse_instruction(nlb_file, line, labels, pc)
                if isinstance(binary_instruction, list):  # Kiểm tra nếu kết quả là danh sách
                    for instr in binary_instruction:
                        outfile.write(instr + "\n")
                    pc += 4  # Tăng PC cho mỗi lệnh
                else:  # Nếu kết quả là chuỗi
                    outfile.write(binary_instruction + "\n")
                    pc += 4  # Tăng PC sau mỗi lệnh
            except ValueError as e:
                raise ValueError(f"Lỗi khi xử lý lệnh '{line}': {e}")

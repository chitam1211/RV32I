import sys
import struct
sys.stdout.reconfigure(encoding='utf-8')
from preprocess_normalize import preprocess_file
from label_instfmt import find_labels
from assemble import assemble

def parse_data_file(data_file):
    """Đọc file data và trích xuất các biến và giá trị với các loại dữ liệu khác nhau."""
    data_memory = {}
    with open(data_file, 'r') as f:
        address = 0x10010000  # Địa chỉ bắt đầu của Data Memory
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Bỏ qua dòng trống hoặc comment
                parts = line.split()
                if len(parts) >= 3:
                    variable_name = parts[0].strip(':')
                    directive = parts[1]
                    value = parts[2]

                    if directive == '.WORD':
                        data_memory[address] = int(value)
                        address += 4  # Một từ (word) chiếm 4 byte
                    elif directive == '.BYTE':
                        data_memory[address] = int(value) & 0xFF  # Lấy giá trị 1 byte
                        address += 1  # Một byte chiếm 1 địa chỉ
                    elif directive == '.HALF':
                        data_memory[address] = int(value) & 0xFFFF  # Lấy giá trị 2 byte
                        address += 2  # Một halfword chiếm 2 byte
                    elif directive == '.FLOAT':
                        float_value = float(value)
                        # Chuyển đổi số thực thành dạng số chấm động IEEE 754 (32-bit)
                        int_representation = struct.unpack('>i', struct.pack('>f', float_value))[0]
                        data_memory[address] = int_representation
                        address += 4  # Một float chiếm 4 byte
    return data_memory

def write_data_memory_to_file(data_memory, output_file):
    """Ghi nội dung Data Memory ra file với định dạng như hình trên."""
    with open(output_file, 'w') as f:
        for address, value in data_memory.items():
            f.write(f"0x{address:08x}\t{value}\n")

def main():
    input_file = "input.txt"
    data_file = "data.txt"
    temp_file = "temp.txt"
    nlb_file = "no lb.txt"
    output_file = "output.txt"
    data_memory_file = "DataMemory.txt"

    # Xử lý file
    preprocess_file(input_file, temp_file, data_file)
    labels = find_labels(temp_file, nlb_file)
    print("Labels found:", labels)
    assemble(nlb_file, output_file, labels)

    # Xử lý Data Memory
    data_memory = parse_data_file(data_file)
    write_data_memory_to_file(data_memory, data_memory_file)

    print("------------------------------------------------------------------------------------------------------------------------")
    print("Data memory saved to", data_memory_file)
    print("Program has finished executing...")

if __name__ == "__main__":
    main()

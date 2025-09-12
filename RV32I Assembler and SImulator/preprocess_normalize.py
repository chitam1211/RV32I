import re

def preprocess_file(input_file, temp_file, data_file):
    with open(input_file, "r", encoding="utf-8") as infile, \
         open(temp_file, "w", encoding="utf-8") as text_outfile, \
         open(data_file, "w", encoding="utf-8") as data_outfile:

        lines = infile.readlines()

        text_section = []  # Lưu các dòng thuộc phần .text
        data_section = []  # Lưu các dòng thuộc phần .data
        current_section = None  # Theo dõi phần hiện tại
        line_count_for_data = 0  # Đếm số dòng cho phần .data

        for line in lines:
            original_line = line  # Giữ lại dòng gốc để xử lý dòng trống
            stripped_line = line.strip()

            # Loại bỏ chú thích (phần sau dấu #)
            if "#" in stripped_line:
                comment_index = stripped_line.find("#")
                code_part = stripped_line[:comment_index].strip()

                if not code_part:  # Dòng chỉ chứa chú thích
                    if current_section == "text":
                        text_section.append("")
                    elif current_section == "data":
                        line_count_for_data += 1
                    continue

                stripped_line = code_part

            # Xử lý dòng .globl như một phần dòng trống
            if stripped_line.startswith(".globl"):
                text_section.append("")  # Thêm dòng trống vào file lệnh
                continue

            # Bỏ qua các dòng trống
            if not stripped_line:
                if current_section == "text":
                    text_section.append("")
                elif current_section == "data":
                    line_count_for_data += 1
                continue

            # Xác định phần .text hoặc .data
            if stripped_line.startswith(".text"):
                current_section = "text"
                text_section.append("")  # Tính .text là một dòng trống
                continue
            elif stripped_line.startswith(".data"):
                current_section = "data"
                line_count_for_data += 1  # Đếm dòng .data
                continue

            # Nếu không có .data hoặc .text, coi như là phần .text
            if current_section is None:
                current_section = "text"

            # Xử lý dòng theo phần hiện tại
            if current_section == "text":
                # Kiểm tra nếu dòng có label và lệnh trên cùng một hàng
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", stripped_line):
                    label, _, instruction = stripped_line.partition(":")
                    label = label.strip().upper() + ":"  # Đảm bảo nhãn kết thúc bằng dấu ':' và viết hoa
                    instruction = instruction.strip()

                    text_section.append(label)  # Ghi nhãn vào một dòng riêng
                    if instruction:  # Nếu có lệnh sau nhãn, thêm lệnh vào dòng mới
                        text_section.append(process_text_line(instruction))
                else:
                    text_section.append(process_text_line(stripped_line))
            elif current_section == "data":
                data_section.append(process_data_line(stripped_line))
                line_count_for_data += 1

        # Ghi các dòng đã xử lý vào file .data
        data_outfile.write("\n".join(data_section))

        # Chừa số dòng trống trong file .text tương ứng với phần .data
        text_outfile.write("\n" * line_count_for_data)
        text_outfile.write("\n".join(text_section))

    print(f"Preprocessed text section written to {temp_file}")
    print(f"Preprocessed data section written to {data_file}")

def process_text_line(line):
    """
    Xử lý một dòng trong phần .text: chuẩn hóa lệnh.
    """
    # Chuyển tất cả sang viết hoa, bỏ qua các nhãn
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*:", line):
        return line  # Giữ nguyên nếu là nhãn

    line = line.upper()

    # Loại bỏ dấu phẩy thừa và chuẩn hóa toán hạng
    line = re.sub(r",{2,}", ",", line)  # Xóa dấu phẩy thừa
    line = re.sub(r",\s*,", ",", line)  # Xóa dấu phẩy không cần thiết giữa khoảng trắng

    # Chuẩn hóa toán hạng
    return normalize_operands(line)

def process_data_line(line):
    """
    Xử lý một dòng trong phần .data: chuẩn hóa định nghĩa dữ liệu.
    """
    # Chuyển tất cả sang viết hoa
    return line.upper()

def normalize_operands(line):
    """
    Chuẩn hóa toán hạng: thêm dấu phẩy giữa các toán hạng nếu thiếu.
    Ví dụ: "LI A7 1" -> "LI A7, 1"
    """
    # Tìm lệnh và toán hạng
    match = re.match(r"^(\w+)\s+(.*)$", line)
    if not match:
        return line  # Trả về dòng gốc nếu không khớp

    instruction, operands = match.groups()

    # Thêm dấu phẩy nếu giữa các toán hạng chỉ có khoảng trắng
    normalized_operands = re.sub(r"\s+", ", ", operands.strip())
    normalized_operands = re.sub(r",\s*,", ",", normalized_operands)  # Loại bỏ dấu phẩy thừa sau chuẩn hóa
    return f"{instruction} {normalized_operands}"

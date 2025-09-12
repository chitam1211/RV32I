# **Bước 7: Chạy chương trình**
import sys
sys.stdout.reconfigure(encoding='utf-8')
from preprocess_normalize import preprocess_file
from label_instfmt import find_labels
from assemble import assemble
def main():
    input_file = r"E:\AI accelerator\Assembler\input.txt"
    data_file = r"E:\AI accelerator\Assembler\predeclared_data.txt"
    temp_file = r"E:\AI accelerator\Assembler\temp.txt"
    nlb_file = r"E:\AI accelerator\Assembler\no lb.txt"
    output_file = r"E:\AI accelerator\Assembler\output.txt"
    # Xử lý file
    preprocess_file(input_file, temp_file,data_file)
    labels = find_labels(temp_file,nlb_file)
    print("Labels found:", labels)
    assemble(nlb_file, output_file, labels)
    print("------------------------------------------------------------------------------------------------------------------------")
    print("Program has finished executing...")
if __name__ == "__main__":
    main()

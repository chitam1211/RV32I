from FUNCTION import *

def Simulator(input_file_path, output_file_path):
    i = 0
    with open(input_file_path, "r", encoding="utf-8") as input_file, open(output_file_path, "w+", encoding="utf-8") as output_file:
        lines = input_file.readlines()
        print("Read lines:", len(lines))
        print("----------------------------------")
        while i < len(lines):
            print("PC:", int(PC["value"], 2))
            line = lines[i].strip()
            #binary_to_data(line, current_address)
            PC["value"] = binary_to_data_Matrix(line, PC["value"])
            i = int(PC["value"], 2)//4
            
            print("----------------------------------")
    
    # PrintMemory(output_file_path)

def main():        
    MATRIX_REGISTER["000"]["value"] = "0100101000000110"*32
    MATRIX_REGISTER["001"]["value"] = "0110000100000101"*32
    MATRIX_REGISTER["010"]["value"] = "0101000001001001"*32
    MATRIX_REGISTER["011"]["value"] = "1100001000100001"*32

    MATRIX_REGISTER["100"]["value"] = "10001000100010000010000010000001"*32
    MATRIX_REGISTER["101"]["value"] = "01000100010001000101000101000010"*32
    MATRIX_REGISTER["110"]["value"] = "00100010001000101000101000100100"*32
    MATRIX_REGISTER["111"]["value"] = "00010001000100010000010000011000"*32

    REGISTERS["00001"]["value"] = "00000000000000000000000000000001"
    REGISTERS["00010"]["value"] = "00000000000000000000000000000001"
    
    input_file_path = r"D:\EA+\DoAn1\ISS\input.txt"
    output_file_path = r"D:\EA+\DoAn1\ISS\output.txt"

    open(output_file_path, "w").close()
    
    Simulator(input_file_path, output_file_path)
    
if __name__ == "__main__":
    main()
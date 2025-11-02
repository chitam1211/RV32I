ELEN = 32
TLEN = 512
TRLEN = 128
ROWNUM = 4
COLNUM = 4
ARLEN = 128
ALEN = 512
XLEN = EEW = 32 #size of instruction

DEFAULT_VALUES = {
    "xmcsr": f"{0:04b}",
    "mtilem": f"{0:04b}",
    "mtilen": f"{0:04b}",
    "mtilek": f"{0:04b}",
    "xmisa": f"{0:016b}",
    "xtlenb": f"{0:04b}",
    "xtrlenb": f"{0:04b}",
    "xalenb": f"{0:04b}",
}

MSTATUS = {
    "SD": {
        "bit": 31,
        "description": "State Dirty - Set if FS or XS is dirty",
        "value": f"{0:01b}"
    },
    "XS": {
        "bit": (22, 17),
        "description": "Extension Status - Tracks status of extensions (e.g., matrix, vector)",
        "value": f"{0:06b}"
    },
    "FS": {
        "bit": (16, 15),
        "description": "Floating-Point Status - Tracks FPU state (Off, Initial, Clean, Dirty)",
        "value": f"{0:02b}"
    },
    "MPP": {
        "bit": 14,
        "description": "Machine Previous Privilege Mode (Only 1 bit in RV32)",
        "value": f"{0:01b}"
    },
    "MS": {
        "bit": 12,
        "description": "Matrix Extension Status (Off, Initial, Clean, Dirty)",
        "value": f"{1:02b}"
    },
    "SPP": {
        "bit": 11,
        "description": "Supervisor Previous Privilege Mode (S/U mode before trap)",
        "value": f"{0:01b}"
    },
    "MPIE": {
        "bit": 10,
        "description": "Machine Previous Interrupt Enable (Interrupts were enabled before trap)",
        "value": f"{0:01b}"
    },
    "SPIE": {
        "bit": 8,
        "description": "Supervisor Previous Interrupt Enable",
        "value": f"{0:01b}"
    },
    "UBE": {
        "bit": 7,
        "description": "User Big-Endian Mode (0 = little-endian, 1 = big-endian)",
        "value": f"{0:01b}"
    },
    "MXR": {
        "bit": 6,
        "description": "Make Executable Readable (Allows execution-only pages to be read)",
        "value": f"{0:01b}"
    },
    "SUM": {
        "bit": 5,
        "description": "Supervisor User Memory Access (Supervisor can access user memory)",
        "value": f"{0:01b}"
    },
    "MPRV": {
        "bit": 4,
        "description": "Modify Privilege for Virtual Memory (Memory accesses use MPP mode)",
        "value": f"{0:01b}"
    },
    "XS_lower": {
        "bit": (3, 2),
        "description": "Extension Status Lower Bits - Additional custom extension tracking",
        "value": f"{0:02b}"
    },
    "FS_lower": {
        "bit": (1, 0),
        "description": "Floating-Point Status Lower Bits",
        "value": f"{0:02b}"
    }
}

# Value to 1 for testing, 0 for default
XMISA = {
    "miew": {"bits": 15, "value": "1"},
    "mfew": {"bits": 14, "value": "1"},
    "mfic": {"bits": 13, "value": "1"},

    # [XLEN - 4:XLEN-10] is reserved

    "reserved": {"bits": (10, 13), "value": "0"},
    "mmf8f32": {"bits": 9, "value": "1"},
    "mmf32f64": {"bits": 8, "value": "1"},
    "mmbf16f32": {"bits": 7, "value": "1"},
    "mmf8bf16": {"bits": 6, "value": "1"},
    "mmf8f16": {"bits": 5, "value": "1"},
    "mmf64f64": {"bits": 4, "value": "1"},
    "mmf32f32": {"bits": 3, "value": "1"},
    "mmf16f16": {"bits": 2, "value": "1"},
    "mmi8i32": {"bits": 1, "value": "1"},
    "mmi4i32": {"bits": 0, "value": "1"}
}

REGISTERS = {
    f"{i:05b}": {"name": name, "value": f"{0:032b}"}
    for i, name in enumerate([
        "zero", *[f"x{j}" for j in range(1, 32)]
    ])
}
# print(REGISTERS["00001"])

MATRIX_CONTROL_REGISTERS = {
    "xmcsr": {"address": "0x802", "privilege": "URW", "description": "Matrix Control and Status Register", "value": DEFAULT_VALUES["xmcsr"]},
    "mtilem": {"address": "0x803", "privilege": "URW", "description": "Tile length in m direction", "value": DEFAULT_VALUES["mtilem"]},
    "mtilen": {"address": "0x804", "privilege": "URW", "description": "Tile length in n direction", "value": DEFAULT_VALUES["mtilen"]},
    "mtilek": {"address": "0x805", "privilege": "URW", "description": "Tile length in k direction", "value": DEFAULT_VALUES["mtilek"]},
    "xmisa": {"address": "0xcc0", "privilege": "URO", "description": "Matrix ISA Register", "value": DEFAULT_VALUES["xmisa"]},
    "xtlenb": {"address": "0xcc1", "privilege": "URO", "description": "Tile register size in bytes", "value": DEFAULT_VALUES["xtlenb"]},
    "xtrlenb": {"address": "0xcc2", "privilege": "URO", "description": "Tile register row size in bytes", "value": DEFAULT_VALUES["xtrlenb"]},
    "xalenb": {"address": "0xcc3", "privilege": "URO", "description": "Accumulation register size in bytes", "value": DEFAULT_VALUES["xalenb"]},
} #adddress không rõ vì thanh ghi 32bit nhưng aadddress cách nhau chỉ 4 bit (1 hex)

# Control Status Register fields
XMCSR = {
    "reserved": {"bit_range": (32-12), "description": "Reserved if non-zero", "value": f"{0:20b}"},
    "xmsaten": {"bit": 11, "description": "Integer and FP8 saturation mode", "value": f"{0:01b}"},
    "xmfrm": {"bit_range": (8, 10), "description": "Float-point rounding mode", "value": f"{0:03b}"},
    "xmfflags": {"bit_range": (3, 7), "description": "Float-point accrued exception flags", "value": f"{0:05b}"},
    "xmsat": {"bit": 2, "description": "Fixed-point saturation flag", "value": f"{0:01b}"},
    "xmxrm": {"bit_range": (0, 1), "description": "Fixed-point rounding mode", "value": f"{0:02b}"},
}

XMSATEN = f"{0:32b}"

XMFRM = f"{0:32b}"

PE = {
    f"PE{i}": {"address": f"0x{900 + i:03x}", "privilege": "URW", "description": f"Processing Element {i} Register", "value": f"{0:032b}"}
    for i in range(1, 17)
}

#matrix register
MATRIX_REGISTER = {
    **{
    #    f"{i:03b}": { 
    #         "name": f"tr{i}",
    #         "address": f"0x{900 + i:03x}",
    #         "description": f"Tile Register {i}",
    #         "value": [[f"0b{0:032b}" for _ in range(COLNUM)] for _ in range(ROWNUM)],
    #     } for i in range(0, 4)
    # },
        **{
        f"{i:03b}": { 
                "name": f"tr{i}",
                "address": f"0x{900 + i:03x}",
                "description": f"Tile Register {i}",
                "value": f"{0:0512b}"
            } for i in range(0, 4)
        },
        "mi": 0,
        "ni": 0,
        "ki": 0,

        **{
            f"{i:03b}": {
                "name": f"acc{i-4}",
                "address": f"0x{910 + (i-4):03x}",
                "description": f"Accumulator Register {i}",
                "value": f"{0:02048b}",
            }
            for i in range(4, 8)
        }
    }
}


PC = {
    "privilege": "URW",
    "description": "Program Counter",
    "value": f"{0:032b}"
}

MEMORIES = {
    f"0x10010{hex(i)[2:].zfill(3).upper()}": 0
    for i in range(0, 0xFFC + 4, 4)
}

CSR = {
    "xmfrm": 0x000,
    "cycle": 0xC00,
    "time": 0xC01,
    "instret": 0xC02,
    "hpmcounter3": 0xC03,
    "hpmcounter4": 0xC04,
    "hpmcounter5": 0xC05,
    "hpmcounter6": 0xC06,
    "hpmcounter7": 0xC07,
    "hpmcounter8": 0xC08,
    "hpmcounter9": 0xC09,
    "hpmcounter10": 0xC0A,
    "hpmcounter11": 0xC0B,
    "hpmcounter12": 0xC0C,
    "hpmcounter13": 0xC0D,
    "hpmcounter14": 0xC0E,
    "hpmcounter15": 0xC0F,
    "hpmcounter16": 0xC10,
    "hpmcounter17": 0xC11,
    "hpmcounter18": 0xC12,
    "hpmcounter19": 0xC13,
    "hpmcounter20": 0xC14,
    "hpmcounter21": 0xC15,
    "hpmcounter22": 0xC16,
    "hpmcounter23": 0xC17,
    "hpmcounter24": 0xC18,
    "hpmcounter25": 0xC19,
    "hpmcounter26": 0xC1A,
    "hpmcounter27": 0xC1B,
    "hpmcounter28": 0xC1C,
    "hpmcounter29": 0xC1D,
    "hpmcounter30": 0xC1E,
    "hpmcounter31": 0xC1F,
}
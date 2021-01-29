#!/usr/bin/python3
import subprocess
import time


def read_dump(addr, len):
    """Read ap1302 registers

    The sysfs interface of the ap1302 driver has a 'dump' function but it writes the hexa dump
    into the kernel log via printk() calls. So we first execute the dump and then try to find
    the response in the 'dmesg' output.

    Args:
        addr (int): address to start dump at
        len (int): no. of bytes to dump
    """
    with open("/sys/devices/platform/soc/40013000.i2c/i2c-1/1-003d/dump",
              "w") as f:
        f.write("0x%04x %i" % (addr, len))

    resp = None
    output = subprocess.run(["dmesg"], capture_output=True, text=True).stdout.splitlines()
    for line in output:
        line_start = line.find(" **** %04x:  " % (addr,))
        if line_start >= 0:
            resp = line[line_start+13:]
            # print(resp)
    return resp


def read_uint16(addr):
    """Read 16-bit ap1302 register value at given address
    """
    resp = read_dump(addr, 2)
    reg = None
    if resp:
        reg = 0
        for nums in resp.split():
            reg = (reg << 8) + int(nums, 16)
        # print("reg: 0x%04x" % reg)
    return reg


def read_reg32(addr):
    """Read 32-bit ap1302 register value at given address
    """
    resp = read_dump(addr, 4)
    reg = None
    if resp:
        reg = 0
        for nums in resp.split():
            reg = (reg << 8) + int(nums, 16)
        # print("reg: 0x%08x" % reg)
    return reg


def read_int16(addr):
    reg = read_uint16(addr)
    if reg > 32767:
        reg -= 65536
    return reg


def write_reg16(addr, val):
    """Write 16-bit ap1302 register through the sysfs interface

    Args:
        addr (int): address of register
        val (int): register value
    """
    with open("/sys/devices/platform/soc/40013000.i2c/i2c-1/1-003d/write_reg16",
              "w") as f:
        f.write("0x%04x 0x%04x" % (addr, val))


# read out ooriginal value from 0x3126
orig_3126 = read_uint16(0x3126)
print(f'orig_3126: {hex(orig_3126)}')

# write 0 to 0x3126
write_reg16(0x3126, 0)
time.sleep(1)

# write 0x001 to 0x3126 and read out 0x3124
write_reg16(0x3126, 0x0001)
tempsense_data = read_int16(0x3124)
print(f'0x3124 after 0x0001: {hex(tempsense_data)}')
time.sleep(0.5)

# write 0x021 to 0x3126 and read out 0x3124
write_reg16(0x3126, 0x0021)
tempsense_data = read_int16(0x3124)
print(f'0x3124 after 0x0021: {hex(tempsense_data)}')
time.sleep(0.5)

# write 0x011 to 0x3126 and read out 0x3124
write_reg16(0x3126, 0x0011)
tempsense_data = read_int16(0x3124)
print(f'0x3124 after 0x0011: {hex(tempsense_data)}')
time.sleep(0.2)
tempsense_data = read_int16(0x3124)
print(f'0x3124 after 0x0011: {hex(tempsense_data)}')
time.sleep(0.2)

ref60 = read_uint16(0x3128)
print(f'ref60: {ref60}')

unit = 1.443137
offset = ref60 - unit*60
print(f'offset: {offset}')

temperature = (tempsense_data - offset)/unit
print(f'temperature: {temperature}')


# write back original value
write_reg16(0x3126, orig_3126)

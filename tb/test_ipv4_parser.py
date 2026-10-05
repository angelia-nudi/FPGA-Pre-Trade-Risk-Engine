import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly


@cocotb.test()
async def test_ipv4_parser(dut):

    # 100 MHz clock
    clock = Clock(
        dut.clk,
        10,
        unit="ns"
    )

    cocotb.start_soon(clock.start())


    # -----------------------------
    # Reset
    # -----------------------------

    dut.rst_n.value = 0

    dut.rx_valid.value = 0
    dut.rx_sof.value = 0
    dut.rx_data.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.rst_n.value = 1


    # -----------------------------
    # 20-byte IPv4 header
    # -----------------------------

    ipv4_header = [

        0x45,       # Version = 4, IHL = 5
        0x00,       # DSCP / ECN

        0x00, 0x1C, # Total length

        0x12, 0x34, # Identification

        0x40, 0x00, # Flags / fragment offset

        0x40,       # TTL = 64

        0x11,       # Protocol = UDP (17)

        0x00, 0x00, # Header checksum
                    # Not validating checksum yet

        # Source IP = 192.168.1.10
        0xC0,
        0xA8,
        0x01,
        0x0A,

        # Destination IP = 192.168.1.20
        0xC0,
        0xA8,
        0x01,
        0x14
    ]


    # -----------------------------
    # Send one byte per clock
    # -----------------------------

    for index, byte in enumerate(ipv4_header):

        dut.rx_data.value = byte
        dut.rx_valid.value = 1

        if index == 0:
            dut.rx_sof.value = 1
        else:
            dut.rx_sof.value = 0

        await RisingEdge(dut.clk)


    await ReadOnly()


    # -----------------------------
    # Read RTL outputs
    # -----------------------------

    actual_version = int(dut.version.value)
    actual_ihl = int(dut.ihl.value)
    actual_protocol = int(dut.protocol.value)

    actual_src = int(dut.src_ip.value)
    actual_dst = int(dut.dst_ip.value)

    actual_valid = int(dut.header_valid.value)


    cocotb.log.info(
        f"Version        = {actual_version}"
    )

    cocotb.log.info(
        f"IHL            = {actual_ihl}"
    )

    cocotb.log.info(
        f"Protocol       = 0x{actual_protocol:02X}"
    )

    cocotb.log.info(
        f"Source IP      = 0x{actual_src:08X}"
    )

    cocotb.log.info(
        f"Destination IP = 0x{actual_dst:08X}"
    )


    # -----------------------------
    # Checks
    # -----------------------------

    assert actual_version == 4

    assert actual_ihl == 5

    assert actual_protocol == 0x11

    assert actual_src == 0xC0A8010A

    assert actual_dst == 0xC0A80114

    assert actual_valid == 1
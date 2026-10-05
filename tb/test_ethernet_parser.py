import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly


@cocotb.test()
async def test_ethernet_parser(dut):

    # ------------------------------------------------
    # Start 100 MHz clock
    # ------------------------------------------------

    clock = Clock(
        dut.clk,
        10,
        unit="ns"
    )

    cocotb.start_soon(clock.start())


    # ------------------------------------------------
    # Reset
    # ------------------------------------------------

    dut.rst_n.value = 0

    dut.rx_valid.value = 0
    dut.rx_sof.value = 0
    dut.rx_data.value = 0

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.rst_n.value = 1


    # ------------------------------------------------
    # Ethernet II header
    # ------------------------------------------------

    ethernet_header = [

        # Destination MAC
        0xAA,
        0xBB,
        0xCC,
        0xDD,
        0xEE,
        0xFF,

        # Source MAC
        0x11,
        0x22,
        0x33,
        0x44,
        0x55,
        0x66,

        # EtherType = IPv4
        0x08,
        0x00

    ]


    # ------------------------------------------------
    # Send header one byte per clock
    # ------------------------------------------------

    for index, byte in enumerate(ethernet_header):

        dut.rx_data.value = byte
        dut.rx_valid.value = 1

        # Assert SOF only for first byte
        if index == 0:
            dut.rx_sof.value = 1
        else:
            dut.rx_sof.value = 0

        await RisingEdge(dut.clk)


    # Read settled RTL values
    await ReadOnly()


    # ------------------------------------------------
    # Read parser outputs
    # ------------------------------------------------

    actual_dst = int(dut.dst_mac.value)
    actual_src = int(dut.src_mac.value)
    actual_type = int(dut.ethertype.value)
    actual_valid = int(dut.header_valid.value)


    cocotb.log.info(
        f"Destination MAC = {actual_dst:012X}"
    )

    cocotb.log.info(
        f"Source MAC      = {actual_src:012X}"
    )

    cocotb.log.info(
        f"EtherType       = 0x{actual_type:04X}"
    )


    # ------------------------------------------------
    # Expected values
    # ------------------------------------------------

    expected_dst = 0xAABBCCDDEEFF
    expected_src = 0x112233445566
    expected_type = 0x0800


    # ------------------------------------------------
    # Verify
    # ------------------------------------------------

    assert actual_dst == expected_dst
    assert actual_src == expected_src
    assert actual_type == expected_type

    assert actual_valid == 1
import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly


@cocotb.test()
async def test_udp_parser(dut):

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
    # UDP packet
    # -----------------------------

    udp_packet = [

        # Source port = 5000 = 0x1388
        0x13,
        0x88,

        # Destination port = 6000 = 0x1770
        0x17,
        0x70,

        # UDP length = 16 bytes
        0x00,
        0x10,

        # Checksum
        0x00,
        0x00,

        # Quantity = 250 = 0x000000FA
        0x00,
        0x00,
        0x00,
        0xFA,

        # Price = 40 = 0x00000028
        0x00,
        0x00,
        0x00,
        0x28
    ]


    # -----------------------------
    # Send one byte per clock
    # -----------------------------

    for index, byte in enumerate(udp_packet):

        dut.rx_data.value = byte
        dut.rx_valid.value = 1

        if index == 0:
            dut.rx_sof.value = 1
        else:
            dut.rx_sof.value = 0

        await RisingEdge(dut.clk)


    await ReadOnly()


    # -----------------------------
    # Read outputs
    # -----------------------------

    actual_src_port = int(dut.src_port.value)
    actual_dst_port = int(dut.dst_port.value)

    actual_length = int(dut.udp_length.value)

    actual_quantity = int(dut.quantity.value)
    actual_price = int(dut.price.value)

    actual_valid = int(dut.order_valid.value)


    cocotb.log.info(
        f"Source port      = {actual_src_port}"
    )

    cocotb.log.info(
        f"Destination port = {actual_dst_port}"
    )

    cocotb.log.info(
        f"UDP length       = {actual_length}"
    )

    cocotb.log.info(
        f"Quantity         = {actual_quantity}"
    )

    cocotb.log.info(
        f"Price            = {actual_price}"
    )


    # -----------------------------
    # Checks
    # -----------------------------

    assert actual_src_port == 5000
    assert actual_dst_port == 6000

    assert actual_length == 16

    assert actual_quantity == 250
    assert actual_price == 40

    assert actual_valid == 1
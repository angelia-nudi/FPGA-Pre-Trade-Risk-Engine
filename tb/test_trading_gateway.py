import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly


@cocotb.test()
async def test_trading_gateway(dut):

    # ==========================================
    # Clock
    # ==========================================

    clock = Clock(
        dut.clk,
        10,
        unit="ns"
    )

    cocotb.start_soon(clock.start())


    # ==========================================
    # Initial values
    # ==========================================

    dut.rst_n.value = 0

    dut.rx_valid.value = 0
    dut.rx_sof.value = 0
    dut.rx_data.value = 0


    # Risk limits
    dut.max_quantity.value = 200
    dut.max_price.value = 30
    dut.max_notional.value = 5000


    # ==========================================
    # Reset
    # ==========================================

    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.rst_n.value = 1


    # ==========================================
    # UDP packet
    # ==========================================

    udp_packet = [

        # Source port = 5000
        0x13,
        0x88,

        # Destination port = 6000
        0x17,
        0x70,

        # UDP length = 16
        0x00,
        0x10,

        # Checksum
        0x00,
        0x00,

        # Quantity = 250
        # 0x000000FA
        0x00,
        0x00,
        0x00,
        0xFA,

        # Price = 40
        # 0x00000028
        0x00,
        0x00,
        0x00,
        0x28
    ]


    # ==========================================
    # Send UDP packet
    # ==========================================

    for index, byte in enumerate(udp_packet):

        dut.rx_data.value = byte
        dut.rx_valid.value = 1

        if index == 0:
            dut.rx_sof.value = 1
        else:
            dut.rx_sof.value = 0

        await RisingEdge(dut.clk)


    # Stop incoming stream
    dut.rx_valid.value = 0
    dut.rx_sof.value = 0


    # ==========================================
    # IMPORTANT
    #
    # UDP parser has just generated order_valid.
    # Risk engine needs the next rising edge
    # to capture the completed order.
    # ==========================================

    await RisingEdge(dut.clk)
    await ReadOnly()


    # ==========================================
    # Read outputs
    # ==========================================

    actual_quantity = int(dut.quantity.value)
    actual_price = int(dut.price.value)

    actual_valid = int(dut.decision_valid.value)

    actual_accept = int(dut.accept.value)

    actual_reason = int(
        dut.reject_reason.value
    )

    actual_flags = int(
        dut.reject_flags.value
    )


    cocotb.log.info(
        f"Parsed quantity = {actual_quantity}"
    )

    cocotb.log.info(
        f"Parsed price    = {actual_price}"
    )

    cocotb.log.info(
        f"Decision valid  = {actual_valid}"
    )

    cocotb.log.info(
        f"Accept          = {actual_accept}"
    )

    cocotb.log.info(
        f"Reject reason   = {actual_reason:02b}"
    )

    cocotb.log.info(
        f"Reject flags    = {actual_flags:03b}"
    )


    # ==========================================
    # Checks
    # ==========================================

    assert actual_quantity == 250
    assert actual_price == 40

    assert actual_valid == 1

    assert actual_accept == 0

    # Quantity = primary reason
    assert actual_reason == 0b01

    # qty + price + notional all failed
    assert actual_flags == 0b111
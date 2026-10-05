import cocotb

from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly


@cocotb.test()
async def test_network_gateway(dut):

    # ==================================================
    # Clock
    # ==================================================

    clock = Clock(
        dut.clk,
        10,
        unit="ns"
    )

    cocotb.start_soon(clock.start())


    # ==================================================
    # Initialisation
    # ==================================================

    dut.rst_n.value = 0

    dut.rx_valid.value = 0
    dut.rx_sof.value = 0
    dut.rx_data.value = 0


    dut.max_quantity.value = 200
    dut.max_price.value = 30
    dut.max_notional.value = 5000


    # Reset for two clocks
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.rst_n.value = 1


    # ==================================================
    # COMPLETE ETHERNET FRAME
    # ==================================================

    ethernet_frame = [

        # =================================================
        # Ethernet header
        # bytes 0-13
        # =================================================

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
        0x00,


        # =================================================
        # IPv4 header
        # bytes 14-33
        # =================================================

        # Version 4 + IHL 5
        0x45,

        # DSCP / ECN
        0x00,

        # Total IP length = 36 bytes
        #
        # 20-byte IP header
        # +
        # 16-byte UDP packet
        #
        # = 0x0024
        0x00,
        0x24,

        # Identification
        0x12,
        0x34,

        # Flags / Fragment offset
        0x40,
        0x00,

        # TTL = 64
        0x40,

        # Protocol = UDP = 17 = 0x11
        0x11,

        # Header checksum
        # Ignored for now
        0x00,
        0x00,

        # Source IP = 192.168.1.10
        0xC0,
        0xA8,
        0x01,
        0x0A,

        # Destination IP = 192.168.1.20
        0xC0,
        0xA8,
        0x01,
        0x14,


        # =================================================
        # UDP header
        # bytes 34-41
        # =================================================

        # Source port = 5000 = 0x1388
        0x13,
        0x88,

        # Destination port = 6000 = 0x1770
        0x17,
        0x70,

        # UDP length = 16
        0x00,
        0x10,

        # UDP checksum
        0x00,
        0x00,


        # =================================================
        # Order payload
        # bytes 42-49
        # =================================================

        # quantity = 250 = 0x000000FA
        0x00,
        0x00,
        0x00,
        0xFA,

        # price = 40 = 0x00000028
        0x00,
        0x00,
        0x00,
        0x28

    ]


    # Make sure our frame really is 50 bytes
    assert len(ethernet_frame) == 50


    # ==================================================
    # Send continuous frame
    # ==================================================

    for index, byte in enumerate(ethernet_frame):

        dut.rx_data.value = byte
        dut.rx_valid.value = 1

        # Only first byte gets SOF
        dut.rx_sof.value = 1 if index == 0 else 0

        await RisingEdge(dut.clk)


    # End input stream
    dut.rx_valid.value = 0
    dut.rx_sof.value = 0


    # UDP parser completed order on last byte.
    #
    # Give risk engine one more rising edge to capture it.

    await RisingEdge(dut.clk)
    await ReadOnly()


    # ==================================================
    # Read parsed data
    # ==================================================

    actual_ethertype = int(
        dut.ethertype.value
    )

    actual_protocol = int(
        dut.ip_protocol.value
    )

    actual_src_port = int(
        dut.src_port.value
    )

    actual_dst_port = int(
        dut.dst_port.value
    )

    actual_quantity = int(
        dut.quantity.value
    )

    actual_price = int(
        dut.price.value
    )

    actual_valid = int(
        dut.decision_valid.value
    )

    actual_accept = int(
        dut.accept.value
    )

    actual_reason = int(
        dut.reject_reason.value
    )

    actual_flags = int(
        dut.reject_flags.value
    )


    # ==================================================
    # Print results
    # ==================================================

    cocotb.log.info(
        f"EtherType       = 0x{actual_ethertype:04X}"
    )

    cocotb.log.info(
        f"IP protocol     = 0x{actual_protocol:02X}"
    )

    cocotb.log.info(
        f"Source port     = {actual_src_port}"
    )

    cocotb.log.info(
        f"Destination port= {actual_dst_port}"
    )

    cocotb.log.info(
        f"Quantity        = {actual_quantity}"
    )

    cocotb.log.info(
        f"Price           = {actual_price}"
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


    # ==================================================
    # Verify complete pipeline
    # ==================================================

    assert actual_ethertype == 0x0800

    assert actual_protocol == 0x11

    assert actual_src_port == 5000
    assert actual_dst_port == 6000

    assert actual_quantity == 250
    assert actual_price == 40

    assert actual_valid == 1

    assert actual_accept == 0

    # Quantity is primary failure
    assert actual_reason == 0b01

    # Quantity + price + notional all fail
    assert actual_flags == 0b111
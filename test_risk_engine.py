import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly, Timer


def risk_check(quantity, price, max_quantity, max_price, max_notional):

    notional = quantity * price

    qty_fail = quantity > max_quantity
    price_fail = price > max_price
    notional_fail = notional > max_notional

    accept = not (
        qty_fail
        or price_fail
        or notional_fail
    )

    reject_flags = (
        (notional_fail << 2)
        | (price_fail << 1)
        | qty_fail
    )

    if qty_fail:
        reject_reason = 1

    elif price_fail:
        reject_reason = 2

    elif notional_fail:
        reject_reason = 3

    else:
        reject_reason = 0

    return int(accept), reject_reason, reject_flags


@cocotb.test()
async def test_risk_engine(dut):

    # Start 100 MHz clock
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Limits
    max_quantity = 200
    max_price = 30
    max_notional = 5000

    # Initial values
    dut.rst_n.value = 0
    dut.order_valid.value = 0

    dut.quantity.value = 0
    dut.price.value = 0

    dut.max_quantity.value = 200
    dut.max_price.value = 30
    dut.max_notional.value = 5000

    # Hold reset for 2 clocks
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)

    dut.rst_n.value = 1

    
    # --------------------------------------------------
    # Test cases
    # quantity, price, description
    # --------------------------------------------------

    test_cases = [
        (100, 20, "Normal valid order"),
        (250, 25, "Quantity too high"),
        (100, 31, "Price too high"),
        (200, 26, "Notional too high"),
        (200, 25, "Exactly at notional limit"),
        (200, 30, "Quantity/price valid but notional too high"),
        (250, 40, "All limits violated")
    ]

    for quantity, price, description in test_cases:

        expected_accept, expected_reason, expected_flags = risk_check(
            quantity,
            price,
            max_quantity,
            max_price,
            max_notional
        )

        # Feed order into RTL
        dut.quantity.value = quantity
        dut.price.value = price
        dut.order_valid.value = 1

        # FPGA RTL captures values on this rising edge
        await RisingEdge(dut.clk)
        await ReadOnly()
    
        actual_accept = int(dut.accept.value)
        actual_reason = int(dut.reject_reason.value)
        actual_valid = int(dut.decision_valid.value)
        actual_flags = int(dut.reject_flags.value)
        
        cocotb.log.info(
            f"{description}: "
            f"quantity={quantity}, "
            f"price={price}, "
            f"notional={quantity * price}, "
            f"expected_accept={expected_accept}, "
            f"RTL_accept={actual_accept}, "
            f"expected_reason={expected_reason:02b}, "
            f"RTL_reason={actual_reason:02b}, "
            f"expected_flags={expected_flags:03b}, "
            f"RTL_flags={actual_flags:03b}"
        )

        assert actual_valid == 1
        assert actual_accept == expected_accept
        assert actual_reason == expected_reason
        assert actual_flags == expected_flags

        # Leave the ReadOnly phase before changing DUT inputs
        await Timer(1, unit="ns")

        # Drop valid between orders
        #dut.order_valid.value = 0

        # Allow one clock cycle with no valid order
        #await RisingEdge(dut.clk)
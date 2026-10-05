import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly


def risk_check(quantity, price, max_quantity, max_price, max_notional):
    notional = quantity * price

    if quantity > max_quantity:
        print("quantity too high")
        return 0, 1
    elif price > max_price:
        print("price too high")
        return 0, 2
    elif notional > max_notional:
        print("notional too high")
        return 0,3
    else:
        print("accepted")
        return 1, 0


@cocotb.test()
async def test_risk_engine(dut):

    # Start 100 MHz clock
    clock = Clock(dut.clk, 10, unit="ns")
    cocotb.start_soon(clock.start())

    # Initial values
    dut.rst_n.value = 0
    dut.order_valid.value = 0

    dut.quantity.value = 0
    dut.price.value = 0

    dut.max_quantity.value = 200
    dut.max_price.value = 30
    dut.max_notional.value = 5000

    # Hold reset for 2 clocks
    #await RisingEdge(dut.clk)
    #await RisingEdge(dut.clk)

    dut.rst_n.value = 1

    # Test order
    quantity = 250
    price = 25

    dut.quantity.value = quantity
    dut.price.value = price
    dut.order_valid.value = 1

    expected_accept, expected_reason = risk_check(
        quantity,
        price,
        200,
        30,
        5000
    )

    # FPGA RTL captures values on this rising edge
    await RisingEdge(dut.clk)
    await ReadOnly()
    
    actual_accept = int(dut.accept.value)
    actual_reason = int(dut.reject_reason.value)
    actual_valid = int(dut.decision_valid.value)
    
    cocotb.log.info(
        f"quantity={quantity}, "
        f"price={price}, "
        f"expected={expected_accept}, "
        f"RTL={int(dut.accept.value)}"
        f"reject reason={int(dut.reject_reason.value)}"
    )

    assert actual_valid == 1
    assert actual_accept == expected_accept
    assert actual_reason == expected_reason
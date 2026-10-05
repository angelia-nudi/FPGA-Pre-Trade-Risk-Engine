from pathlib import Path
from cocotb_tools.runner import get_runner


def run():

    project_dir = Path(__file__).resolve().parent

    rtl_dir = project_dir / "RTL"
    test_dir = project_dir / "tb"

    sources = [

        rtl_dir / "udp_parser.sv",

        rtl_dir / "risk_engine.sv",

        rtl_dir / "trading_gateway_top.sv",

    ]

    print("COMPILING:")

    for source in sources:
        print(" -", source)

    runner = get_runner("icarus")

    runner.build(
        sources=sources,
        hdl_toplevel="trading_gateway_top",
        always=True,
    )

    runner.test(
        hdl_toplevel="trading_gateway_top",
        test_module="test_trading_gateway",
        test_dir=test_dir,
    )


if __name__ == "__main__":
    run()
from pathlib import Path
from cocotb_tools.runner import get_runner


def run():

    project_dir = Path(__file__).resolve().parent

    source = (
        project_dir
        / "RTL"
        / "udp_parser.sv"
    )

    test_dir = (
        project_dir
        / "tb"
    )

    print("COMPILING:", source)
    print("TEST DIRECTORY:", test_dir)

    runner = get_runner("icarus")

    runner.build(
        sources=[source],
        hdl_toplevel="udp_parser",
        always=True,
    )

    runner.test(
        hdl_toplevel="udp_parser",
        test_module="test_udp_parser",
        test_dir=test_dir,
    )


if __name__ == "__main__":
    run()
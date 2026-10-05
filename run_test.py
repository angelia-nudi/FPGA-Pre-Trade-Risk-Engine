from pathlib import Path
from cocotb_tools.runner import get_runner


def run():
    project_dir = Path(__file__).resolve().parent

    source = (
        project_dir
        /"RTL"/"risk_engine.sv"
    )

    print("COMPILING:", source)

    runner = get_runner("icarus")

    runner.build(
        sources=[source],
        hdl_toplevel="risk_engine",
        always=True,
    )

    runner.test(
        hdl_toplevel="risk_engine",
        test_module="test_risk_engine",
    )


if __name__ == "__main__":
    run()
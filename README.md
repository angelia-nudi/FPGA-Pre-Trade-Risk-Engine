# FPGA-Pre-Trade-Risk-Engine
Low-latency FPGA pre-trade risk engine using SystemVerilog, cocotb and  Java as software reference models for functional verification.

Hardware basedprototype for checking orders againts configurable pre-trade risk limits. The main SystemVerilog module evaluates order quantity, price, and notional value, which then output a registered accept/reject decision with an encoded reason and a bitmask of all violated limits.

This project also explores parsing incoming Ethernet-based order data as a step towards an integrated FPGA trading gatewat. It is a design and verification portofolio project, not a production trading system.

## Design Overview

The intended processing path is:
```text
incoming Ethernet byte stream
            |
            v
    Ethernet II parser 
            |
            v
 IPv4 / UDP decoding    (integration work)
            |
            v
        Order fields
    (quantity and price)
            |
            v
    Pre-trade risk engine
            |
            v
decision_valid / accept
reject_reason / reject_flags 
```

The risk engine can be tested independently of the packet parsers
**The diagram represents the target integrated architecture, it does not imply that every block has been validated end-to-end.**

## RTL Features

### Risk Engine (`RTL/risk_engine.sv`)
- Accepts a valid order with **32-bit quantity** and **32-bit price** fields.
- Applies configurable `max_quantity`, `max_price`, and `max_notional` limits.
- Uses a **64-bit quantity × price** calculation for notional checking.
- Produces registered `decision_valid`, `accept`, `reject_reason`, and `reject_flags` outputs.
- Evaluates each limit independently, while selecting one primary rejection reason in a fixed priority order.

An order is rejected when any of the following is true:

```text
quantity > max_quantity
price > max_price
quantity * price > max_notional
```

Values exactly equal to a configured limit **pass** that individual check.

**Primary rejection reason:**

| `reject_reason` | Meaning |
|---|---|
| `2'b00` | Accepted / no violation |
| `2'b01` | Quantity limit exceeded |
| `2'b10` | Price limit exceeded |
| `2'b11` | Notional limit exceeded |

If multiple limits fail, the primary reason has priority **quantity > price > notional**. All violations are still reported by `reject_flags`:

| Flag bit | Violation |
|---|---|
| `reject_flags[0]` | Quantity |
| `reject_flags[1]` | Price |
| `reject_flags[2]` | Notional |

For example, with `max_quantity = 200`, `max_price = 30`, and `max_notional = 5000`, an order of quantity `250` at price `40` violates all three limits. The result is `accept = 0`, `reject_reason = 2'b01`, and `reject_flags = 3'b111`.

### Ethernet parser (`RTL/ethernet_parser.sv`)

- Accepts incoming bytes through `rx_data`, qualified by `rx_valid` and `rx_sof`.
- Extracts destination MAC, source MAC, and EtherType from an Ethernet II header.
- Signals parsed header availability using `header_valid`.

UDP/IPv4 decoding and integration with the risk engine are ongoing development areas; they should not be interpreted as a fully verified end-to-end network stack.

## Verification

The RTL is simulated with **Icarus Verilog** and tested in **Python/Cocotb**.

Verified unit-level work includes:

- **Risk engine:** seven directed test scenarios covering accepted orders, limit boundaries, individual violations, and simultaneous violations; the latest recorded test run passed.
- **Ethernet parser:** a directed Ethernet II header test checking destination MAC, source MAC, and EtherType (`0x0800`); the latest recorded test run passed.

Tests exercise design behaviour in simulation. There is **no claimed FPGA deployment, timing-closure result, or measured packet-to-decision latency** at this stage.

## Getting started

### Requirements

- Python 3.11 (used during development)
- Icarus Verilog (`iverilog` available on your `PATH`)
- Cocotb 2.1.x

In a terminal at the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install cocotb==2.1.0
```

Check that Icarus Verilog is installed:

```powershell
iverilog -V
```

Run the unit tests:

```powershell
python run_test.py
python run_ethernet_test.py
```

The simulation runners compile the corresponding RTL and execute the Cocotb tests. If you already use a different Python virtual environment, activate that environment instead.

## Core project files

```text
FPGA-Pre-Trade-Risk-Engine/
├── RTL/
│   ├── risk_engine.sv
│   └── ethernet_parser.sv
├── tb/
│   └── ...                  # Cocotb test modules
├── run_test.py              # Risk-engine simulation runner
├── run_ethernet_test.py     # Ethernet-parser simulation runner
└── README.md
```

Additional parser, gateway, and reference-model files may be added as their implementation and verification are completed.

## Next steps

- Complete and verify IPv4/UDP-to-order-field decoding.
- Integrate packet parsing and the risk engine in a top-level datapath.
- Add end-to-end packet tests, malformed-input cases, and broader regression coverage.
- Add a software reference model for decision cross-checking.
- Evaluate synthesis, timing, throughput, and potential clock-domain-crossing requirements on a chosen FPGA target.

## Purpose

This project is a practical exercise in **synchronous RTL design, bit-width handling, deterministic priority logic, protocol parsing, and Cocotb-based verification**, with an emphasis on making design decisions testable and clearly documented.
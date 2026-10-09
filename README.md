# FPGA-Pre-Trade-Risk-Engine
Low-latency FPGA pre-trade risk engine using SystemVerilog, cocotb and  Java as software reference models for functional verification.

Hardware basedprototype for checking orders againts configurable pre-trade risk limits. The main SystemVerilog module evaluates order quantity, price, and notional value, which then output a registered accept/reject decision with an encoded reason and a bitmask of all violated limits.

This project also explores parsing incoming Ethernet-based order data as a step towards an integrated FPGA trading gatewat. It is a design and verification portofolio project, not a production trading system.

##Design Overview

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

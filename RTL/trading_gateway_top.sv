`timescale 1ns / 1ps

module trading_gateway_top (

    input logic clk,
    input logic rst_n,

    // Incoming UDP byte stream
    input logic       rx_valid,
    input logic       rx_sof,
    input logic [7:0] rx_data,

    // Risk limits
    input logic [31:0] max_quantity,
    input logic [31:0] max_price,
    input logic [63:0] max_notional,

    // Parsed order - useful for debugging
    output logic [31:0] quantity,
    output logic [31:0] price,

    // Final decision
    output logic        decision_valid,
    output logic        accept,
    output logic [1:0]  reject_reason,
    output logic [2:0]  reject_flags
);


    // -----------------------------------------
    // Internal connections
    // -----------------------------------------

    logic [15:0] src_port;
    logic [15:0] dst_port;
    logic [15:0] udp_length;

    logic order_valid;


    // =========================================
    // UDP parser
    // =========================================

    udp_parser udp_parser_inst (

        .clk(clk),
        .rst_n(rst_n),

        .rx_valid(rx_valid),
        .rx_sof(rx_sof),
        .rx_data(rx_data),

        .src_port(src_port),
        .dst_port(dst_port),
        .udp_length(udp_length),

        .quantity(quantity),
        .price(price),

        .order_valid(order_valid)

    );


    // =========================================
    // Risk engine
    // =========================================

    risk_engine risk_engine_inst (

        .clk(clk),
        .rst_n(rst_n),

        .order_valid(order_valid),

        .quantity(quantity),
        .price(price),

        .max_quantity(max_quantity),
        .max_price(max_price),
        .max_notional(max_notional),

        .decision_valid(decision_valid),
        .accept(accept),
        .reject_reason(reject_reason),
        .reject_flags(reject_flags)

    );


endmodule
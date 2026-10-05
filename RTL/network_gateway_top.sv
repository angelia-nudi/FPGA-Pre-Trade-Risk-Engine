`timescale 1ns / 1ps

module network_gateway_top (

    input logic clk,
    input logic rst_n,

    // Complete incoming Ethernet frame
    input logic       rx_valid,
    input logic       rx_sof,
    input logic [7:0] rx_data,

    // Risk limits
    input logic [31:0] max_quantity,
    input logic [31:0] max_price,
    input logic [63:0] max_notional,

    // Debug / parsed outputs
    output logic [15:0] ethertype,
    output logic [7:0]  ip_protocol,

    output logic [15:0] src_port,
    output logic [15:0] dst_port,

    output logic [31:0] quantity,
    output logic [31:0] price,

    // Final risk decision
    output logic       decision_valid,
    output logic       accept,
    output logic [1:0] reject_reason,
    output logic [2:0] reject_flags
);


    // ==================================================
    // Frame position tracking
    // ==================================================

    logic [5:0] frame_byte_count;
    logic       frame_active;

    logic ipv4_sof;
    logic udp_sof;


    always_ff @(posedge clk) begin

        if (!rst_n) begin

            frame_byte_count <= 6'd0;
            frame_active     <= 1'b0;

        end

        else if (rx_valid) begin

            // First byte of new Ethernet frame
            if (rx_sof) begin

                frame_active     <= 1'b1;
                frame_byte_count <= 6'd1;

            end

            else if (frame_active) begin

                // This first test frame contains 50 bytes
                if (frame_byte_count == 6'd49) begin

                    frame_byte_count <= 6'd0;
                    frame_active     <= 1'b0;

                end

                else begin

                    frame_byte_count <= frame_byte_count + 1'b1;

                end

            end

        end

    end


    // --------------------------------------------------
    // Start-of-header pulses
    // --------------------------------------------------

    // Ethernet starts at byte 0.
    // rx_sof already identifies that.

    // IPv4 starts immediately after 14-byte Ethernet header
    assign ipv4_sof =
        rx_valid &&
        frame_active &&
        (frame_byte_count == 6'd14);

    // UDP starts after:
    //
    // 14 Ethernet bytes
    // +
    // 20 IPv4 bytes
    //
    // = byte 34
    //
    // Also only start UDP if this really is IPv4 + UDP.

    assign udp_sof =
        rx_valid &&
        frame_active &&
        (frame_byte_count == 6'd34) &&
        (ethertype == 16'h0800) &&
        (ip_protocol == 8'h11);


    // ==================================================
    // Ethernet parser
    // ==================================================

    logic [47:0] dst_mac;
    logic [47:0] src_mac;
    logic        ethernet_header_valid;


    ethernet_parser ethernet_parser_inst (

        .clk(clk),
        .rst_n(rst_n),

        .rx_valid(rx_valid),
        .rx_sof(rx_sof),
        .rx_data(rx_data),

        .dst_mac(dst_mac),
        .src_mac(src_mac),
        .ethertype(ethertype),

        .header_valid(ethernet_header_valid)

    );


    // ==================================================
    // IPv4 parser
    // ==================================================

    logic [3:0]  ip_version;
    logic [3:0]  ip_ihl;

    logic [31:0] src_ip;
    logic [31:0] dst_ip;

    logic        ipv4_header_valid;


    ipv4_parser ipv4_parser_inst (

        .clk(clk),
        .rst_n(rst_n),

        .rx_valid(rx_valid),
        .rx_sof(ipv4_sof),
        .rx_data(rx_data),

        .version(ip_version),
        .ihl(ip_ihl),

        .protocol(ip_protocol),

        .src_ip(src_ip),
        .dst_ip(dst_ip),

        .header_valid(ipv4_header_valid)

    );


    // ==================================================
    // UDP parser
    // ==================================================

    logic [15:0] udp_length;
    logic        order_valid;


    udp_parser udp_parser_inst (

        .clk(clk),
        .rst_n(rst_n),

        .rx_valid(rx_valid),
        .rx_sof(udp_sof),
        .rx_data(rx_data),

        .src_port(src_port),
        .dst_port(dst_port),

        .udp_length(udp_length),

        .quantity(quantity),
        .price(price),

        .order_valid(order_valid)

    );


    // ==================================================
    // Risk engine
    // ==================================================

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
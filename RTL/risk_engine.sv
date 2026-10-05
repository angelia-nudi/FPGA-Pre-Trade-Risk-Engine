`timescale 1ns / 1ps
//////////////////////////////////////////////////////////////////////////////////
// Company: 
// Engineer: 
// 
// Create Date: 18.09.2026 14:22:55
// Design Name: 
// Module Name: risk_engine
// Project Name: 
// Target Devices: 
// Tool Versions: 
// Description: 
// 
// Dependencies: 
// 
// Revision:
// Revision 0.01 - File Created
// Additional Comments:
// 
//////////////////////////////////////////////////////////////////////////////////


module risk_engine(
    input  logic        clk,
    input  logic        rst_n,

    input  logic        order_valid,
    input  logic [31:0] quantity,
    input  logic [31:0] price,

    input  logic [31:0] max_quantity,
    input  logic [31:0] max_price,
    input  logic [63:0] max_notional,

    output logic        decision_valid,
    output logic        accept,
    output logic [1:0]  reject_reason,
    output logic [2:0]  reject_flags
);

    logic [63:0] notional;

    logic qty_fail;
    logic price_fail;
    logic notional_fail;

    logic accept_comb;
    logic [1:0] reject_reason_comb;
    logic [2:0] reject_flags_comb;


    always_comb begin

        // Calculate order notional
        notional = 64'(quantity) * 64'(price);

        // ------------------------------------------------
        // Parallel risk checks
        // ------------------------------------------------

        qty_fail =
            quantity > max_quantity;

        price_fail =
            price > max_price;

        notional_fail =
            notional > max_notional;


        // Order accepted only if ALL checks pass
        accept_comb =
            !(qty_fail ||
              price_fail ||
              notional_fail);


        // Store every violation
        reject_flags_comb[0] = qty_fail;
        reject_flags_comb[1] = price_fail;
        reject_flags_comb[2] = notional_fail;


        // Primary rejection reason
        // Priority:
        // quantity > price > notional

        if (qty_fail)
            reject_reason_comb = 2'b01;

        else if (price_fail)
            reject_reason_comb = 2'b10;

        else if (notional_fail)
            reject_reason_comb = 2'b11;

        else
            reject_reason_comb = 2'b00;

    end


    always_ff @(posedge clk) begin

        if (!rst_n) begin

            accept         <= 1'b0;
            decision_valid <= 1'b0;
            reject_reason  <= 2'b00;
            reject_flags   <= 3'b000;

        end

        else begin

            decision_valid <= order_valid;

            if (order_valid) begin

                accept        <= accept_comb;
                reject_reason <= reject_reason_comb;
                reject_flags  <= reject_flags_comb;

            end

        end

    end

endmodule

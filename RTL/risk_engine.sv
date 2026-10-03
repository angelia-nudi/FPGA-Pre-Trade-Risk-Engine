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
    input logic        clk,
    input logic        rst_n,
    
    input logic        order_valid,
    input logic [31:0] quantity,
    input logic [31:0] price,
    
    input logic [31:0] max_quantity,
    input logic [31:0] max_price,
    input logic [63:0] max_notional,
    
    output logic       decision_valid,
    output logic       accept,
    output logic [1:0] reject_reason
    );
    
    logic [63:0] notional;
    logic        accept_comb;
    logic [1:0]  reject_reason_comb;
    
always_comb begin

    notional = 64'(quantity) * 64'(price);

    if (quantity > max_quantity) begin
        accept_comb        = 1'b0;      // means decline
        reject_reason_comb = 2'b01;     // means qty too high
    end

    else if (price > max_price) begin
        accept_comb        = 1'b0;      
        reject_reason_comb = 2'b10;     // means price too high
    end

    else if (notional > max_notional) begin
        accept_comb        = 1'b0;
        reject_reason_comb = 2'b11;     // means notional too high
    end

    else begin
        accept_comb        = 1'b1;
        reject_reason_comb = 2'b00;     // means accepted
    end
end
    
always_ff @(posedge clk) begin
    if (!rst_n) begin
        accept         <= 1'b0;
        decision_valid <= 1'b0;
        reject_reason  <= 2'b00;
    end

    else begin
        decision_valid <= order_valid;

        if (order_valid) begin
            accept        <= accept_comb;
            reject_reason <= reject_reason_comb;
        end
    end
end
    
    
endmodule

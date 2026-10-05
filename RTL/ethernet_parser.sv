`timescale 1ns / 1ps
module ethernet_parser (

    input  logic        clk,
    input  logic        rst_n,

    // Incoming Ethernet byte stream
    input  logic        rx_valid,
    input  logic        rx_sof,
    input  logic [7:0]  rx_data,

    // Parsed Ethernet header
    output logic [47:0] dst_mac,
    output logic [47:0] src_mac,
    output logic [15:0] ethertype,

    output logic        header_valid
);

    logic [3:0] byte_count;
    logic       parsing;


    always_ff @(posedge clk) begin

        if (!rst_n) begin

            byte_count   <= 4'd0;
            parsing      <= 1'b0;

            dst_mac      <= 48'd0;
            src_mac      <= 48'd0;
            ethertype    <= 16'd0;

            header_valid <= 1'b0;

        end

        else begin

            // By default this is only a 1-clock pulse
            header_valid <= 1'b0;


            if (rx_valid) begin

                // ------------------------------------------------
                // First byte of new Ethernet frame
                // ------------------------------------------------

                if (rx_sof) begin

                    parsing <= 1'b1;

                    byte_count <= 4'd1;

                    // Byte 0
                    dst_mac[47:40] <= rx_data;

                end


                // ------------------------------------------------
                // Remaining Ethernet header bytes
                // ------------------------------------------------

                else if (parsing) begin

                    case (byte_count)

                        // Destination MAC
                        4'd1:
                            dst_mac[39:32] <= rx_data;

                        4'd2:
                            dst_mac[31:24] <= rx_data;

                        4'd3:
                            dst_mac[23:16] <= rx_data;

                        4'd4:
                            dst_mac[15:8] <= rx_data;

                        4'd5:
                            dst_mac[7:0] <= rx_data;


                        // Source MAC
                        4'd6:
                            src_mac[47:40] <= rx_data;

                        4'd7:
                            src_mac[39:32] <= rx_data;

                        4'd8:
                            src_mac[31:24] <= rx_data;

                        4'd9:
                            src_mac[23:16] <= rx_data;

                        4'd10:
                            src_mac[15:8] <= rx_data;

                        4'd11:
                            src_mac[7:0] <= rx_data;


                        // EtherType
                        4'd12:
                            ethertype[15:8] <= rx_data;

                        4'd13: begin

                            ethertype[7:0] <= rx_data;

                            // Ethernet header complete
                            header_valid <= 1'b1;

                            parsing <= 1'b0;

                        end

                    endcase


                    // Advance to next byte
                    if (byte_count != 4'd13)
                        byte_count <= byte_count + 1'b1;

                    else
                        byte_count <= 4'd0;

                end

            end

        end

    end

endmodule
`timescale 1ns / 1ps

module udp_parser (

    input  logic        clk,
    input  logic        rst_n,

    // Incoming UDP byte stream
    input  logic        rx_valid,
    input  logic        rx_sof,
    input  logic [7:0]  rx_data,

    // UDP header fields
    output logic [15:0] src_port,
    output logic [15:0] dst_port,
    output logic [15:0] udp_length,

    // Order payload
    output logic [31:0] quantity,
    output logic [31:0] price,

    output logic        order_valid
);

    logic [4:0] byte_count;
    logic       parsing;


    always_ff @(posedge clk) begin

        if (!rst_n) begin

            byte_count  <= 5'd0;
            parsing     <= 1'b0;

            src_port    <= 16'd0;
            dst_port    <= 16'd0;
            udp_length  <= 16'd0;

            quantity    <= 32'd0;
            price       <= 32'd0;

            order_valid <= 1'b0;

        end

        else begin

            // Pulse for one clock only
            order_valid <= 1'b0;


            if (rx_valid) begin

                // -----------------------------
                // First UDP byte
                // -----------------------------

                if (rx_sof) begin

                    parsing <= 1'b1;
                    byte_count <= 5'd1;

                    src_port[15:8] <= rx_data;

                end


                // -----------------------------
                // Remaining bytes
                // -----------------------------

                else if (parsing) begin

                    case (byte_count)

                        // Source port
                        5'd1:
                            src_port[7:0] <= rx_data;


                        // Destination port
                        5'd2:
                            dst_port[15:8] <= rx_data;

                        5'd3:
                            dst_port[7:0] <= rx_data;


                        // UDP length
                        5'd4:
                            udp_length[15:8] <= rx_data;

                        5'd5:
                            udp_length[7:0] <= rx_data;


                        // Bytes 6-7 = checksum
                        // Ignored for now


                        // Quantity bytes 8-11
                        5'd8:
                            quantity[31:24] <= rx_data;

                        5'd9:
                            quantity[23:16] <= rx_data;

                        5'd10:
                            quantity[15:8] <= rx_data;

                        5'd11:
                            quantity[7:0] <= rx_data;


                        // Price bytes 12-15
                        5'd12:
                            price[31:24] <= rx_data;

                        5'd13:
                            price[23:16] <= rx_data;

                        5'd14:
                            price[15:8] <= rx_data;

                        5'd15: begin

                            price[7:0] <= rx_data;

                            order_valid <= 1'b1;

                            parsing <= 1'b0;

                        end

                    endcase


                    if (byte_count != 5'd15)
                        byte_count <= byte_count + 1'b1;

                    else
                        byte_count <= 5'd0;

                end

            end

        end

    end

endmodule
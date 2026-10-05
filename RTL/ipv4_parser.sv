`timescale 1ns / 1ps

module ipv4_parser (

    input  logic        clk,
    input  logic        rst_n,

    // Incoming IPv4 byte stream
    input  logic        rx_valid,
    input  logic        rx_sof,
    input  logic [7:0]  rx_data,

    // Parsed fields
    output logic [3:0]  version,
    output logic [3:0]  ihl,
    output logic [7:0]  protocol,

    output logic [31:0] src_ip,
    output logic [31:0] dst_ip,

    output logic        header_valid
);

    logic [4:0] byte_count;
    logic       parsing;


    always_ff @(posedge clk) begin

        if (!rst_n) begin

            byte_count   <= 5'd0;
            parsing      <= 1'b0;

            version      <= 4'd0;
            ihl          <= 4'd0;
            protocol     <= 8'd0;

            src_ip       <= 32'd0;
            dst_ip       <= 32'd0;

            header_valid <= 1'b0;

        end

        else begin

            // Pulse for one clock only
            header_valid <= 1'b0;


            if (rx_valid) begin

                // -------------------------------------
                // First IPv4 byte
                // -------------------------------------

                if (rx_sof) begin

                    parsing <= 1'b1;

                    byte_count <= 5'd1;

                    // upper nibble = version
                    version <= rx_data[7:4];

                    // lower nibble = IHL
                    ihl <= rx_data[3:0];

                end


                // -------------------------------------
                // Remaining IPv4 bytes
                // -------------------------------------

                else if (parsing) begin

                    case (byte_count)

                        // Protocol field = byte 9
                        5'd9:
                            protocol <= rx_data;


                        // Source IP = bytes 12-15
                        5'd12:
                            src_ip[31:24] <= rx_data;

                        5'd13:
                            src_ip[23:16] <= rx_data;

                        5'd14:
                            src_ip[15:8] <= rx_data;

                        5'd15:
                            src_ip[7:0] <= rx_data;


                        // Destination IP = bytes 16-19
                        5'd16:
                            dst_ip[31:24] <= rx_data;

                        5'd17:
                            dst_ip[23:16] <= rx_data;

                        5'd18:
                            dst_ip[15:8] <= rx_data;

                        5'd19: begin

                            dst_ip[7:0] <= rx_data;

                            header_valid <= 1'b1;

                            parsing <= 1'b0;

                        end

                    endcase


                    if (byte_count != 5'd19)
                        byte_count <= byte_count + 1'b1;

                    else
                        byte_count <= 5'd0;

                end

            end

        end

    end

endmodule
module fifo_sync (
    input  logic                      clk,
    input  logic                      rst_n,
    input  logic                      wr_en,
    input  logic                      rd_en,
    input  logic [7:0] wdata,
    output logic [7:0] rdata,
    output logic                      full,
    output logic                      empty
);

    localparam int unsigned DATA_WIDTH = 8;
    localparam int unsigned DEPTH = 8;
    localparam int unsigned ADDR_WIDTH = 3;
    localparam int unsigned COUNT_WIDTH = 4;
    localparam logic [COUNT_WIDTH-1:0] DEPTH_COUNT = COUNT_WIDTH'(8);

    logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];
    logic [ADDR_WIDTH-1:0] wr_ptr_q;
    logic [ADDR_WIDTH-1:0] rd_ptr_q;
    logic [COUNT_WIDTH-1:0] count_q;
    logic do_write;
    logic do_read;

    assign full = (count_q == DEPTH_COUNT);
    assign empty = (count_q == 0);
    assign do_write = wr_en && !full;
    assign do_read = rd_en && !empty;

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            wr_ptr_q <= '0;
            rd_ptr_q <= '0;
            count_q <= '0;
            rdata <= '0;
        end else begin
            if (do_write) begin
                mem[wr_ptr_q] <= wdata;
                wr_ptr_q <= wr_ptr_q + 1'b1;
            end

            if (do_read) begin
                rdata <= mem[rd_ptr_q];
                rd_ptr_q <= rd_ptr_q + 1'b1;
            end

            case ({do_write, do_read})
                2'b10: count_q <= count_q + 1'b1;
                2'b01: count_q <= count_q - 1'b1;
                default: count_q <= count_q;
            endcase
        end
    end

endmodule

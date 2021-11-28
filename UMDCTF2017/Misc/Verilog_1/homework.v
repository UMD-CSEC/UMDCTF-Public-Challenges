module homework (
  input clk,
  input clr,
  input [7:0] d,
  output [8:0] q
);

wire [8:0] r;

assign q = r;

always @ (posedge clk or posedge clr) begin
  if (clr) begin
    r <= 1'b0;
  end

  else begin
    r[0] <=        ~d[7] &  d[6] &  d[5] & ~d[4] &  d[3] &  d[2] &  d[1] & ~d[0];
    r[1] <= r[0] & ~d[7] & ~d[6] &  d[5] &  d[4] & ~d[3] & ~d[2] & ~d[1] & ~d[0];
    r[2] <= r[1] & ~d[7] &  d[6] & ~d[5] &  d[4] &  d[3] &  d[2] &  d[1] &  d[0];
    r[3] <= r[2] & ~d[7] &  d[6] &  d[5] &  d[4] & ~d[3] & ~d[2] &  d[1] &  d[0];
    r[4] <= r[3] & ~d[7] &  d[6] & ~d[5] &  d[4] & ~d[3] & ~d[2] & ~d[1] & ~d[0];
    r[5] <= r[4] & ~d[7] & ~d[6] &  d[5] &  d[4] & ~d[3] & ~d[2] & ~d[1] &  d[0];
    r[6] <= r[5] & ~d[7] &  d[6] &  d[5] & ~d[4] & ~d[3] & ~d[2] &  d[1] &  d[0];
    r[7] <= r[6] & ~d[7] & ~d[6] &  d[5] &  d[4] & ~d[3] & ~d[2] &  d[1] &  d[0];
    r[8] <= r[7];
  end
end

endmodule

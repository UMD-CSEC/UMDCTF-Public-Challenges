defmodule Flavors do
  require Integer

  def z, do: "he who controls the spice controls the universe"

  def y(0, <<a::8>> <> _), do: a
  def y(n, <<_::8>> <> b), do: y(n - 1, b)
  def y(n), do: y(n, z())

  def a(%{in: <<>>, i: 47}) do
    ""
  end

  def a(%{i: 47}) do
    raise "oh no"
  end

  def a(%{in: <<c::8>> <> d, i: i}) when Integer.is_even(i) do
    <<Bitwise.bxor(c,y(i))::8>> <> a(%{in: d, i: i + 1})
  end

  def a(%{in: <<c::8>> <> d, i: i}) do
    a(%{in: d, i: i + 1}) <> <<Bitwise.bxor(c,y(i))::8>>
  end

  def a(%{in: <<>>}) do
    raise "oh no"
  end

  def c(w, x, y, z) do
    w * 1 + x * 2 + y * 4 + z * 8
    |> Integer.to_string(16)
  end

  def b(<<w::1, x::1, y::1, z::1, r::bitstring>>) when w == y do
    c(z, w, y, x) <> b(r)
  end

  def b(<<w::1, x::1, y::1, z::1, r::bitstring>>) do
    c(x, y, w, z) <> b(r)
  end

  def b(<<>>), do: ""

  def main do
    a(%{in: IO.gets("Flag: ") |> String.trim, i: 0})
    |> b
    |> IO.puts
  end
end

Flavors.main()

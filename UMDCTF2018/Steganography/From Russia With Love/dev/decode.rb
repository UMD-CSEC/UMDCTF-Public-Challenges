#!/usr/bin/env ruby

STDIN.read.each_char do |c|
  print c unless c.ascii_only?
end

puts

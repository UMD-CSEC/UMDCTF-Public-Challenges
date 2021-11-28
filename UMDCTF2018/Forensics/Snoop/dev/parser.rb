#!/usr/bin/env ruby
# frozen_string_literal: true

# Usage: ruby parser.rb < whatever.fpff

require "securerandom"

PNG_SIGNATURE = "\x89PNG\r\n\x1a\n".b
GIF87_SIGNATURE = "GIF87a".b
GIF89_SIGNATURE = "GIF89a".b

STDIN.binmode
data = STDIN.read

header = data[0, 24]
body = data[24, data.size - 24]

magic, version, timestamp, author, nsects = header.unpack("L3<A8<L<")

raise "bad magic" unless magic == 0xBEFEDADE
raise "bad version" unless version == 1

puts "TIMESTAMP: #{Time.at timestamp}"
puts "AUTHOR: #{author}"
puts "NSECTS: #{nsects}"

offset = 0

nsects.times do
  stype, slen = body[offset, 8].unpack("L2<")
  puts "Found a section of type #{stype}, #{slen} bytes (offset #{offset + 24})"

  svalue = case stype
           when 1, 2 then body[offset + 8, slen]
           when 3 then body[offset + 8, slen].unpack("L*<")
           when 4 then body[offset + 8, slen].unpack("Q*<")
           when 5, 6 then body[offset + 8, slen].unpack("E*")
           when 7 then body[offset + 8, slen].unpack("L<")
           when 8, 9, 10 then body[offset + 8, slen]
           else raise "unknown stype: #{stype}"
           end

  if stype == 8
    filename = "#{SecureRandom.hex(4)}.png"
    File.binwrite(filename, PNG_SIGNATURE + svalue)
    puts "\tSaved PNG as #{filename}"
  elsif stype == 9
    filename = "#{SecureRandom.hex(4)}.png"
    File.binwrite(filename, GIF87_SIGNATURE + svalue)
    puts "\tSaved GIF (87) as #{filename}"
  elsif stype == 10
    filename = "#{SecureRandom.hex(4)}.gif"
    File.binwrite(filename, GIF89_SIGNATURE + svalue)
    puts "\tSaved GIF (89) as #{filename}"
  else
    puts "\tSection value: #{svalue}"
  end

  offset += slen + 8
end

#!/usr/bin/env ruby
# frozen_string_literal: true

# Usage: ruby generator.rb > whatever.fpff

require "base64"

MAGIC = 0xBEFEDADE
VERSION = 1
TIMESTAMP = Time.now.to_i
AUTHOR = "outis" # get it?

SECTION_TYPES = {
  SECTION_ASCII: 0x1,
  SECTION_UTF8: 0x2,
  SECTION_WORDS: 0x3,
  SECTION_DWORDS: 0x4,
  SECTION_DOUBLES: 0x5,
  SECTION_COORD: 0x6,
  SECTION_REFERENCE: 0x7,
  SECTION_PNG: 0x8,
  SECTION_GIF87: 0x9,
  SECTION_GIF89: 0xA,
}.freeze

BODY = {
  "drop it like it's hot." => :SECTION_ASCII,
  File.read("snoop.gif", mode: "rb") => :SECTION_GIF89,
}.freeze

print [MAGIC, VERSION, TIMESTAMP].pack("L3<")
print [AUTHOR].pack("a8")
print [BODY.size].pack("L<")

BODY.each do |value, stype|
  svalue = case stype
           when :SECTION_ASCII, :SECTION_UTF8 then value
           when :SECTION_WORDS then value.pack("L*<")
           when :SECTION_DWORDS then value.pack("Q*<")
           when :SECTION_DOUBLES, :SECTION_COORD then value.pack("E*")
           when :SECTION_REFERENCE then [value].pack("L<")
           when :SECTION_PNG then value[8, value.bytesize - 8] # chop the magic
           when :SECTION_GIF87, :SECTION_GIF89 then value[6, value.bytesize - 6] # chop the magic
           end

  print [SECTION_TYPES[stype]].pack("L<")
  print [svalue.bytesize].pack("L<")
  print svalue
end

#!/usr/bin/env ruby

# Generator for valid Swedish personnummer: http://en.wikipedia.org/wiki/Personal_identity_number_(Sweden)
# By Henrik Nyh <http://henrik.nyh.se> 2009-01-29 under the MIT license.

require 'date'

module Personnummer

  def self.generate(date=nil, serial=nil)
    date ||= Date.new(1900+rand(100), 1+rand(12), 1+rand(28))
    serial = serial ? serial.to_s : format("%03d", rand(999)+1)  # 001-999

    date_part = date.strftime('%y%m%d')
    pnr = [date_part, serial].join
  
    digits = []
    pnr.split('').each_with_index do |n,i|
      digits << n.to_i * (2 - i % 2)
    end
    sum = digits.join.split('').inject(0) {|sum,digit| sum += digit.to_i }
    checksum = 10 - sum % 10
    checksum = 0 if checksum == 10
    "19#{date_part}#{serial}#{checksum}"
  end
  
end

if $0 == __FILE__
  for i in 0..10
    # Randomize every part
    puts Personnummer.generate
    # Use given date, randomize serial
    #puts Personnummer.generate(Date.new(1975,1,1))
    # Use given date and serial, calculate checksum
    #puts Personnummer.generate(Date.new(1975,1,1), 123)
  end  
end

require "json"

struct JSON::Any
def q(l)
got=[] of String
t=self
l.each do |i|
begin
t=t[i]
got << i.to_s
rescue e
puts "error #{i} got #{got}"
raise e
end # rescue
end # each
t
end # def
end # struct


class Session
@files=[] of String

def add(t)
@files << t
end

def s
get("s")[0]
end

def c
get("c")[0]
end

def s?
have "s"
end

def c?
have "c"
end

def have(t)
get(t).size>0
end

def get(t)
@files.select {|f| f.split(".")[0].ends_with?("_#{t}") }
end

end


class Fiddler
@sessions=Hash(Int32,Session).new
def initialize(dir=".")
Dir.children(dir).each do |c|
num=c.split("_")[0].to_i
if ! @sessions[num]?
@sessions[num]=Session.new
end
@sessions[num].add c
end
end

getter sessions

end


f=Fiddler.new
seen=[] of Time
log=Hash(Time, Array(Float64)).new
idx=0
f.sessions.keys.to_a.sort.each do |k|
o=f.sessions[k]
if ! o.c?
next
end
fc=File.read(o.c)
if ! fc.starts_with?("POST ")
next
end
if ! fc.split("\n")[0].index("/cws/graphql")
next
end
if ! fc.index("WDB_GetUsageReadsForDayAndHour")
next
end
j=JSON.parse(File.read(o.s).split("\r\n\r\n")[1].strip)
l=j.q ["data",
    "billingAccountByAuthContext",
      "serviceAgreements",
0,
          "servicePointsConnection",
            "edges",
0,
                "node",
                  "readStreams",
                    "netUsage",
0,
"reads"]
l.as_a.each do |measure|
d1,d2=measure["timeInterval"].as_s.split("/")
d1=Time.parse(d1, "%Y-%m-%dT%H:%M:%S%Z", Time::Location.local)
d2=Time.parse(d2, "%Y-%m-%dT%H:%M:%S%Z", Time::Location.local)
m=measure["measuredAmount"]["value"].as_f
day=d1.at_beginning_of_day
if ! log[day]?
log[day]=[] of Float64
end
if seen.includes?(d1)
next
end
log[day] << m
seen << d1
end # each measurement
end # each key
alias Ol=Tuple(Float64,Time)
ret=[] of Ol
log.each do |k,v|
ret << ({v.sum()/v.size,k})
end
ret.sort_by! {|i| i[1] }
ret.reverse!
ret.each do |i|
puts "#{i[0]}, #{i[1]}"
end

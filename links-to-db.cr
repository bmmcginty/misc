# read html from arg1
# convert all links from html to short links
# write converted html back to arg1
# treat any args after arg1 as a new command and execute that command
# create table links (id serial, url text unique);
require "xml"
require "../scrapers/quick.cr"

server_url="http://srv1/go"
x=XML.parse_html File.read(ARGV[0])
links=x.xpath_nodes("//a[@href]").map {|i| i["href"] }.uniq
if links.size>0
union=String.build do |sb|
links.each_with_index do |link,idx|
sb << "select $#{idx+1}"
if idx<links.size-1
sb << " union "
end # if not at end
end # each
end # sb
h=Hash(String,Int32).new
with_db do |db|
db.query(
"with tmp (url) as ( #{union} ) insert into links (url) select t.url from tmp t on conflict (url) do update set url=excluded.url returning id,url",
args: links) do |rs|
rs.each do
lid,url=rs.read.as(Int32),rs.read.as(String)
h[url]=lid
end # each row
end #rs
end # with db
x.xpath_nodes("//a[@href]").each do |i|
i["href"]="#{server_url}/#{h[i["href"]]}"
end
File.write ARGV[0],x.to_s
end
system ARGV[1], ARGV[2..-1]

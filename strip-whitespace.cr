def err(v)
#STDERR << "#{v}\n"
end

# start reading
# while newline or whitespace, continue
# if text, emit character
# if first consecutive space, and we have seen text on this line, emit
# if first or second newline, emit
# if tershiary newline, continue
# if not first consecutive space, continue
start=true
line_seen_text=false
consecutive_ws=false
new_line=2
STDIN.each_char do |c|
ws=false
nl=false
case c
when '\u00a0', ' ', '\t'
ws=true
when '\n'
nl=true
end
err "#{c.ord} "
if nl && new_line<2
err "first or second new line, emitting"
new_line+=1
STDOUT << '\n'
next
end
if ws && new_line>0
err "whitespace at beginning of line"
next
end
if ! nl && new_line>0
err "resetting consecutive space and text on line for new line text"
consecutive_ws=false
line_seen_text=false
new_line=0
end
if ! ws && ! nl
err "non-whitespace character found, clearing consecutive space and setting line_seen_text"
consecutive_ws=false
line_seen_text=true
STDOUT << c
next
end
if ws && line_seen_text && ! consecutive_ws
err "first whitespace found after reading some text"
consecutive_ws=true
STDOUT << ' '
next
end # first consecutive space
if ws && line_seen_text && consecutive_ws
next
end
end # each

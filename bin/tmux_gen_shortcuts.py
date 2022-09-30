#!/usr/bin/python

"""generate chainged key tables to allow promptless shortcuts in tmux
Feed the output of this script into .tmux.conf,
and have shortcuts that will drop text into your current window.
See ../.tmux.shortcuts.yml for examples.
Note the case-insensative "any" key. Unlike the other possible shortcut entries,
the Any shortcut will run the full command specified via value.
This allows you, to e.g. display a message or ring the terminal's bell via echo,
when an unsupported key is pressed.
"""

import os
import yaml

out = []
db = yaml.safe_load(open(os.path.expanduser(
    "~/.tmux.shortcuts.yml"), "r").read())

any_already_set = set()
for entry in db:
    table_name = entry["name"]
    any_key = [i for i in entry["shortcuts"] if i.lower() == "any"]
    any_key = any_key[0] if any_key else "any"
    any = entry["shortcuts"].pop(any_key, None)
    shortcut_names = list(entry["shortcuts"].keys())
    shortcut_names.sort(key=(lambda x: len(x)), reverse=True)
    for _shortcut in shortcut_names:
        value = entry["shortcuts"][_shortcut]
        idx = 0
        prefix = entry.get("prefix", "")
        shortcut = list(_shortcut)
        if prefix:
            shortcut.insert(0, prefix)
        idx = 0
        shortcut.insert(0, "")
        for char in shortcut:
            idx += 1
            seen = shortcut[:idx]
            remainder = shortcut[idx:]
            totbl = "tbl-%s-%s" % ("-".join(seen), remainder[0],)
            if idx == 1:
                frmtbl = "root"
            else:
                frmtbl = "tbl-%s" % ("-".join(seen),)
                if any and frmtbl != "root" and frmtbl not in any_already_set:
                    any_already_set.add(frmtbl)
                    out.append(("anykey", frmtbl, "Any", any,))
            if len(remainder) == 1:
                out.append(("key", frmtbl, remainder[0], value,))
                break
            else:
                out.append(("tbl", frmtbl, totbl, remainder[0],))

for i in out:
    if i[0] == "tbl":
        frmtbl, totbl, key = i[1:]
        print("bind-key -T %(frmtbl)s %(key)s switch-client -T%(totbl)s" % vars())
    elif i[0] == "anykey":
        frmtbl, key, val = i[1:]
        print("bind-key -T%(frmtbl)s %(key)s %(val)s" % vars())
    else:
        frmtbl, key, val = i[1:]
        print("bind-key -T%(frmtbl)s %(key)s send-keys \"%(val)s\"" % vars())

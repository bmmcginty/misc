#!/usr/bin/python

"""generate chainged key tables to allow promptless shortcuts in tmux
Feed the output of this script into .tmux.conf,
and have shortcuts that will drop text into your current window.
See ../.tmux.shortcuts.yml for examples.
"""

import os
import yaml

out = []
db = yaml.safe_load(open(os.path.expanduser(
    "~/.tmux.shortcuts.yml"), "r").read())

for entry in db:
    table_name = entry["name"]
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
            if len(remainder) == 1:
                out.append(("key", frmtbl, remainder[0], value,))
                break
            else:
                out.append(("tbl", frmtbl, totbl, remainder[0],))
for i in out:
    if i[0] == "tbl":
        frmtbl, totbl, chr = i[1:]
        print("tmux bind-key -T %(frmtbl)s %(chr)s switch-client -T%(totbl)s" % vars())
    else:
        frmtbl, chr, val = i[1:]
        print("tmux bind-key -T%(frmtbl)s %(chr)s send-keys \"%(val)s\"" % vars())

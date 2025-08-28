from dataclasses import dataclass, field
from typing import Optional
import random
import json
import unicodedata
from collections import defaultdict

LINE_NAMES = ['A', 'B', 'C']

@dataclass
class Stop:
    name: str
    id: str
    lines: list[str] = field(default_factory=list)
    connections: list[str] = field(default_factory=list)

    def __repr__(self):
        return f"{self.name}({','.join(self.lines)}) -> {','.join(self.connections)}"

stops: dict[str, Stop] = {}
lines: dict[str, list[str]] = defaultdict(lambda: [])

def normalize(s: str) -> str:
    normalized = unicodedata.normalize('NFD', s)
    ascii_str = ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')
    return ascii_str.lower().replace(' ', '_')

for line in LINE_NAMES:
    with open(line + ".txt") as f:
        prev_stop = None
        names = [i.strip() for i in f.readlines()]
        for i in range(len(names)):
            if names[i][-4:-1] == " - ":
                names[i] = names[i][:-4]
            s_n = names[i]
            s_id = normalize(s_n)
            lines[line].append(s_id)
            
            if s_id not in stops:
                stops[s_id] = Stop(s_n, s_id)
                
            stops[s_id].lines.append(line)
            # print(stops[n])
            if prev_stop:
                stops[s_id].connections.append(prev_stop.id)
                prev_stop.connections.append(s_id)
            
            prev_stop = stops[s_id]

with open("stops.json", "w") as f:
    json.dump(
        {
        "stops":{i: stops[i].__dict__ for i in stops},
        "lines": lines,
        }, 
        f, 
        ensure_ascii=False)

# ---------------- Game ----------------
# The rest of this file is an implementation of the game in python

def is_on_same_line(a: Stop, b: Stop) -> bool:
    if set(a.lines).intersection(b.lines): return True
    return False

def find_path(start: Stop, end: Stop, source: Optional[Stop] = None) -> Optional[list[Stop]]:
    if start == end:
        return [end]
    for i in start.connections:
        i = stops[i]
        if i == source:
            continue
        if not (is_on_same_line(end, i) or (is_on_same_line(start, i) and is_on_same_line(source, i) if source else True)): # No double transfers
            continue
        p = find_path(i, end, start)
        if p:
            return p + [start]

def format_path(path: list[Stop]):
    if is_on_same_line(path[0], path[-1]):
        return f"{len(path)-1} stops"
    transfer = 0
    for i in range(1, len(path)):
        if not is_on_same_line(path[0], path[i]):
            transfer = i
            break
    return f"{len(path)-transfer-1} stops + {transfer} stops"

def game():
    goal = random.choice(list(stops.values()))
    while True:
        guess = input("Guess: ")
        if guess not in stops:
            print("Not a stop")
            continue
        path = find_path(stops[guess], goal)
        if len(path) == 1:
            print("You got it!")
            break
        # print([i.name for i in path[::-1]])
        print(format_path(path))
#!/usr/local/bin/yap -L -s5000 -h20000
:- initialization(run_aleph).
run_aleph :- 
consult(aleph),
read_all(Tue_Aug_23_13-38-38_2011-1314099518.979635_),
set(search, heuristic),
set(noise, 15),
set(language, 1),
set(openlist, 25),
set(clauselength, 4),
set(mode, induce_cover),
set(eval, wracc),
set(caching, true),
induce_cover,
write_rules(Tue_Aug_23_13-38-38_2011-1314099518.979635_Rules).

%
% Convert aleph's theory into a python dictionary.
%
% Author: Anze Vavpetic, 2011 <anze.vavpetic@ijs.si>


% pretty print a definite clause
py_print_dclause(Clause):-
        ('$aleph_global'(portray_literals,set(portray_literals,true))->
                py_print_dclause(Clause,true);
                py_print_dclause(Clause,false)).
 
py_print_dclause((H:-true),Pretty):-
        !,
        py_print_dclause(H,Pretty).

py_print_dclause((H:-B),Pretty):-
        !,
	write('{"clause" : "'),
        copy_term((H:-B),(Head:-Body)),
        numbervars((Head:-Body),0,_),
        aleph_portray(Head,Pretty),
        (Pretty = true ->
                write(' if:');
                write(' :-')),
        %nl,
        '$aleph_global'(print,set(print,N)),
        py_lits(Body,Pretty,1,N),
	write('", "covered" : ['),
	arg(1,H,X),
	all(X, B, L),
	print_covered(L),
        write(']}'),
	!.


print_example(X) :- 
  atom_concat(i, ID, X),
  %orig_label(X, Label),
  %write('{"id" : '),
  write('"'),
  write(ID),
  write('"').
  %write(', "rank_or_label" : '),
  %write(Label),
  %write('}').

print_covered([X]) :- 
  !,
  print_example(X).

print_covered([H|T]) :-
  print_covered([H]),
  write(','),
  print_covered(T).

py_print_dclause((Lit),Pretty):-
        copy_term(Lit,Lit1),
        numbervars(Lit1,0,_),
        aleph_portray(Lit1,Pretty),
        write('.').


toPython(File):-
        aleph_open(File,write,Stream),
        set_output(Stream),
	assertz(curr_stream(Stream)),
	write('rules = ['),
        '$aleph_global'(rules,rules(L)),
        aleph_reverse(L,L1),
        rule_toPython(L1),
	write(']'),
        flush_output(Stream),
        set_output(user_output).

rule_toPython(Rules):-
        aleph_member(RuleId,Rules),
        '$aleph_global'(theory,theory(RuleId,_,Rule,_,_)),
        py_print_dclause(Rule),
	write(','),
	curr_stream(Stream),
	flush_output(Stream),
        fail.
rule_toPython(_).

py_lits((Lit,Lits),Pretty,LitNum,LastLit):-
        !,
        (Pretty = true ->
                Sep = ' and ';
                Sep = ', '),
        print_lit(Lit,Pretty,LitNum,LastLit,Sep,NextLit),
        py_lits(Lits,Pretty,NextLit,LastLit).
py_lits((Lit),Pretty,LitNum,_):-
        print_lit(Lit,Pretty,LitNum,LitNum,'.',_).

print_lit(Lit,Pretty,LitNum,LastLit,Sep,NextLit):-
        (LitNum = 1 -> tab(3);true),
        aleph_portray(Lit,Pretty), write(Sep),
        (LitNum=LastLit,NextLit=1; NextLit is LitNum + 1).
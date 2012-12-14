%%%
%%% User prune definition.
%%%
prune((_ :- Body)) :-
    violates(Body).

violates(Body) :-
    do_violate(Body, Body).

violate_check([X], Body) :-
    check(X, Body), !.

violate_check([H|T], Body) :-
    check(H, Body), !
    ;
    violate_check([T], Body).

check([X], [Y]) :-
    isa(X, Y), !.

check([X], [H|T]) :-
  check([X], [H]), !
  ;
  check([X], T).
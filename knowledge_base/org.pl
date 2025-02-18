% Create Ruls 
Manager(X, Y) :- boss(X, Y), ic(X).
Reportee(X, Y) :- report(X,Y), boss(X). 


% Facts
boss(Raul, Daniel).
boss(Daniel, Sebastian).



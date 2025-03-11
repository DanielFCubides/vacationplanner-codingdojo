% relationship
friend(daniel, sebastian).



% Facts about parent relationships
parent(john, bob).    % john is parent of bob
parent(john, lisa).   % john is parent of lisa
parent(mary, bob).    % mary is parent of bob
parent(mary, lisa).   % mary is parent of lisa
parent(bob, ann).     % bob is parent of ann
parent(bob, pat).     % bob is parent of pat
parent(nancy, daniel).
parent(nancy, andres).
parent(nancym, nancy).
parent(fernando, daniel).
parent(fernando, valentina).
parent(cesar, sebastian).
parent(tito, junior).
parent(aurelio, cesar).
parent(aurelio, tito).
parent(rosa, liliana).
parent(fernando, fernando).
parent(cesar, luisa).

% Rules
father(X, Y) :- parent(X, Y), male(X).
mother(X, Y) :- parent(X, Y), female(X).
sibling(X, Y) :- parent(Z, X), parent(Z, Y), X \= Y.
granchild(X,Y) :- parent(Z,X), parent(Y,Z), X \= Y. 
cousins(X,Y) :- parent(Z,X), parent(W,Y), sibling(Z,W), X \= Y.
uncle(X,Y) :- sibling(Z,X), parent(Z,Y).

% Facts about gender
male(john).
male(bob).
male(pat).
female(mary).
female(lisa).
female(ann).
female(nancy).
male(daniel).
male(andres).
female(nancym).
female(valentina).


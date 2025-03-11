# Knowledge base

We are going to explore prolog as a knowledge base programming rules.

## How to run my knowledge base with prolog

To run your file use:
```shell
swipl family.pl
```



Then you can make queries like:

```sh
?- parent(john, bob).


% Who are bob's parents?
?- parent(X, bob).


% Who are lisa's siblings?
?- sibling(lisa, X).


```

## Semantics

Understanding the Output:


true. means the query is true
false. means the query is false
Multiple answers will be shown with ; between them
Press ; to see more answers
Press . to stop searching for more answers


Exiting Prolog:

  Type halt. or press Ctrl+D



# TODO

## 1. Should a parent BFN detach when it has a detached child?

- Yes, it should.
- No, it does not have to, according to 3.

## 2. After I modified a successor, should I modify the ancestors? 

- Yes, you should, according to the semantics
- No, you do not need to, according to 3.

## 3. Can depend-on-me's have children?

- No, they acnnot (?)

## 4. How to traverse the tree and make modifications?

## 5. How to design the set-functions for a BFN with children?

- Leave functions like `set_child`
- But do not put such `set_child` functions in the `mutation_set`

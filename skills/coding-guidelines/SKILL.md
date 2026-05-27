---
name: coding-guidelines
description: Use it when the user asks you to create a design document or write code.
---

All the design you propose or all the code you will write needs to be analized before
actually implementing, to achive this review the Glosary and the Best practices sections
of this document to create simple systems.

# Glosary

## Important
The biggest problem which solution can fix other problems or the most common knowledge that
can be used to solve most of the problems.

## Complexity
Something that is dificult to undertand or you needs a lot of time to implement a simple feature.

## Symptomps of Complexity
**Amplification change** The number of changes I need to do for implementing a simple feature.
**Cognitive load** The amount of time I need to understand the code to implement a simple feature.
**Unknown unknown** The things I don't know I need to implement a simple feature.

## Deep Module
Provides a simple interface to use and provides a great functionallity by exposing the important things
in the interface and hides the unimportant things in the implementation. Also, deep modules prevent information
leakage that is when a piece of knowledge is known by mulple modules.

# Best practices

## Functions
1. Common knowledge spread among the class in different methods needs to me merged into a single one.
2. Variables spread among the class in different methods needs to be moved into a single method.
3. Functions needs to be deep.

## Comments
1. Comments for interfaces needs to highligh the important things to explain its use.
2. Implementation comments highlight the unimportant things.
3. A comment needs to help to solve cognitive load and unknown unkowns.
4. Never repeat code or vocabulary of the code on the comment.
5. Never write comments when the code is self explanatory.

## When to separate methods?
When the method encapsulate logic that is not required in the caller to understand the
whole set of instructions.

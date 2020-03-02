# Conditions and loops

There are multiple operators supported by CubeLang, that control the way the program executes. These operators include the `if` statement, various types of loops and `orient` statement.

## Conditional statement

An `if` statement allows a user to control which block of code will be executed depending on the value of a predicate.

![](./diagrams/out/if.svg)

A predicate is an arbitrary expression of boolean type. Predicates after `if` and `else-if` keywords are evaluated from top to bottom until the one evaluated to `true` is found. Then the corresponding block of code gets executed. If all predicates are evaluated to `false` the block of code denoted by `else` keyword is executed if present.

An `if` statements can be used as an expression if the `else` branch is present and the last operation inside each brunch are expressions of the same type (except for `int` and `real` values; if all such operations are expression of integer or real type and at least one of them is real, the value of the `if` expression will be implicitly converted to real). For example:

```bash
let value: color = red
let opposite: color = if value == white then
        yellow
    else-if color == yellow then
        white
    else-if color == green then
        blue
    else-if color == blue then
        green
    else-if color == red then
        orange
    else
        red
    end
# opposite is equal to orange
```

## While loop

A `while` loop continuously repeats execution of the block of code until the predicate stops evaluating to `true`.

![](./diagrams/out/while.svg)

The predicate is always evaluated before each iteration including the first one.

The following code demonstrates the usage of a `while` loop. It implements finding an index of the element in a list. The same operation is implemented by the standard library `index_of` function.

```bash
let values: list of side = list_of(front, right, back, top)
let val: side = right

let index: int = 0
while index < size(values) and values[index] != val do
    index = idnex + 1
end
let result: int = if index == size(values) then -1 else index
```

## Repeat loop

`repeat` loop is useful when a user wants to execute the block of code exact number of times.

![](./diagrams/out/repeat.svg)

An integer expression, that determines the number of iterations is evaluated only once. If a user needs an iteration index he/she should use a counter variable.

The following example demonstrates the usage of a `repeat` loop. It adds natural numbers from 1 to 10 into the list.

```bash
let array: list of int
let index: int = 1

repeat 10 times
    add_last(array, index)
    index = index + 1
end
```

The following example executes a "sexy move" on a cube exactly six times. After the execution, the cube should be in the same configuration as in the beginning.

```bash
repeat 6 times
    RUR'U'
end
```

## For loop

A for loop is used when a block of code needs to be executed for each element of the collection.

![](./diagrams/out/for.svg)

A collection must be a value of type `list` or `set`. Identifier can be either the name of the variable that has not been previously declared or the name of the existing variable of the same type as a collection's elements.

If the identifier is not an existing variable, it is automatically declared and available inside the loop body only. If identifier is an existing variable then the last value of the collection will be saved and available outside the loop.

The following example demonstrates the usage of a for loop for flattening a two-dimensional list into a set.

```bash
let grid: list of list of color = list_of( \
    list_of(red, green, blue), \
    list_of(orange, green, red))
let result: set of color

for row in grid do
    for element in row do
        add(result, element)
    end
end

# result is equal to set_of(red, green, blue, orange)
```

## Orient statement

An `orient` statement allows users to automatically change the orientation of the cube to align it with some pattern. This is a common scenario when solving a puzzle using one of the existing methods.

![](./diagrams/out/orient.svg)

![](./diagrams/out/orient-constraints.svg)

An `orient` statement is similar to the `if` statement. `orient` executes the first code block of code after the set of constraints for the orientation. For each branch, the CubeLang library will iterate through every possible orientation (if the keeping parameter is defined, then the library will iterate only through orientations that do not change the specified side) and determine if the patterns match corresponding faces. If they do the brunch will be executed, otherwise the next following brunch will be considered. `else` brunch works similarly to the `else` brunch in the `if` statement.

Consider the fragment from the [`pocket-cube`](../examples/pocket-cube) example:

```
orient top: {x-/--}, front: {x-/--}, right: {x-/--}, back: {x-/--}, keeping: top then
    R'U'RU'R'U2R
else-orient top: {-x/--}, front: {-x/--}, left: {-x/--}, back: {-x/--}, keeping: top then
    LUL'ULU2L'
else-orient back: {xx/--}, front: {xx/--}, keeping: top then
    R2U2RU2R2
else-orient front: {-x/--}, left: {xx/--}, back: {x-/--}, keeping: top then
    F RUR'U' RUR'U' F'
else-orient top: {-x/-x}, left: {xx/--}, keeping: top then
    F RUR'U' F'
else-orient top: {-x/-x}, back: {-x/--}, front: {x-/--}, keeping: top then
    RUR'U' R'FRF'
else-orient top: {x-/-x}, front: {x-/--}, right: {-x/--}, keeping: top then
    FRU'R'U'RUR'F'
end
```

In the first line of the snippet above we can see five constraints. The CubeLang library will attempt to find an orientation that will satisfy all of these constraints: the top left sticker of the top face has the same color as the top left sticker of the front face, top left sticker of the right face and top left color of the back face. The face on the top will not change. If such orientation can be found, the formula on the second line will be executed. Otherwise, the constraints on line 3 will be considered.

Patterns can also be used without variables or `keeping` constraint. For example, the same example file includes the following line:

```
orient top: {--/-Y} then noop end
```

This statement will iterate through all possible orientations of the cube until the orientation with a yellow sticker in the bottom right position of the top face is found. This initial orientation is common in the speedcubing community.


## Function declaration

Users may define functions that encapsulate commonly used operations. They can be called like any function in the standard library.

![](./diagrams/out/functions.svg)

*Note:* Variables and functions declared outside the function are not visible inside the function. All functions declared in CubeLang can be pure or only mutate collection arguments. Recursion is not possible in CubeLang. This limitation may change in the future versions of the language.

Function may return a value. The type of return value must be specified in the function signature. When the interpreter encounters the `return` statement, it stops the execution of a function and sets the specified value as its result. If no `return` statement was executed, the return type's default value is returned.

The following example shows an example function that calculates the greatest common denominator of two integers.

```bash
func gcd(a: int, b: int): int
    while a != 0 and b != 0 do
        if a > b then
            a = a - b
        else
            b = b - a
        end
    end
    return a + b
end
```

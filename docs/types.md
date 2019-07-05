# Variables and types

## Variable declaration

cubelang allows its users to create and assign variables using the following syntax:

![let variable_name[, var_name [, ...]]: type[ = initial value]](./diagrams/out/var_decl.svg)

Multiple variables may be declared using the syntax above. These variables will have the same type and initial value.

Variable name is an arbitrary string consisting of *lowercase* latin letters (`a`--`z`), underscore symbol (`_`) or an arabic digit (`0`--`9`). A variable name must not begin with a digit. A variable name also cannot be any of the following reserved words: `boolean`, `color`, `do`, `end`, `for`, `func`, `if`, `in`, `int`, `let`, `list`, `of`, `orient`, `pattern`, `real`, `repeat`, `return`, `set`, `side`, `then`, `while`.

A variable has a scope. Variable is available only after it is declared using `let` keyword. If variable is declared inside a block such as a conditional clause or a loop, it is available only within this block. If a variable is declared on the top level (outside of any block) it is available anywhere within a script after declaration.

A user may declare a variable with the same name within an inner block. Statements inside this block will reference the new variable, outside this block -- the old variable.

When declaring a variable a user must specify its type and may specify its initial value. If initial value is not specified the default value is used. cubelang supports multiple types described below.

## Integer type

```bash
let number: int = 18
```

`int` type declares arbitrary precision signed integer value. Integer literal consists of an optional minus sign (`-`) followed by one or more decimal digits (e.g. `0`, `-47`, `102`).

*Default value:* `0`.


## Real type

```bash
let value: real = 1.24
```

`real` type represents a floating point number. The following syntax is used when declaring real literal:

![[-][digit*].digit*[(e|E)(+|-)?digit*]](./diagrams/out/real.svg)

An integer value including integer literal can be implicitly converted to real type and assigned to real variable or passed to the function that expectes a real argument.

*Default value:* `0.0`.

## Boolean type

```bash
let bool_value: boolean = true
```

A value of `bool` type can be either `true` or `false`. Expressions of boolean type are used as predicates in loops and conditions.

*Default value:* `false`.

## Color type

```bash
let color_value: color = red
```

A value of  `color` type represents one of the six possible colors of the sticker on the face of a cube: `white`, `orange`, `red`, `yellow`, `green`, `blue`.

*Default value:* `white`.

## Side type

```
let side_value: side = back
```

This type represents one of the sides of the cube relatice to the current orientation. The following values are allowed: `front`, `back`, `left`, `right`, `top` and `bottom`.

*Default value:* `front`

## Pattern type

```bash
let pattern_value: pattern = {-x-/-xG/-R-}
```

Patterns are used by the `orient` operator. They are used when determining the orientation of the cube such that one of the faces would match the pattern. 

Pattern literal consists of series of symbols separated by `/` character. These symbols can be either lowercase latin letter, a first letter of the color name (`R` for `red`, `G` for `green`, etc.) or a minus (`-`) symbol. Lowercase letters represent variables: all stickers corresponding to the same variable must be of the same color. Uppercase letter determine the color of the sticker. Minuses are ignored. Pattern literal is required to describe rectangular grid of symbols.

For example, the pattern defined above requires that:

* the face of a cube has dimensions of 3x3;
* the color of the sticker in the middle of the top row is the same as the color of the middle sticker in the middle row;
* the sticker in the middle of the right column is green;
* the sticker in the middle of the bottom row is red.


## Collection types

cubelang defines two collection types: `list` and `set`.  Values of these types can hold multiple values of the same type.

A list is a sequential collection of values that can be accessed by their index. The first item in the list has the index `0`. Items in the list  can be repeat.

A set is an unordered collection of unique items. Adding an element to the set, removing the element and determining if the set contains an element is supported by this data type. If an item that is already present in the set is added the second type, nothing happens. Sets do not support indexing.

A collection is a parametric type. When declaring a variable of a collection type user must specify a type of the values in the collection:

```bash
let colors_list: list of color = list_of(red, green, blue)
let numbers_set: set of int = set_of(1, 2, 3)
let grid_of_colors: list of list of color = list_of(list_of(red, green), list_of(blue, orange))
```
List values can be accessed using the following syntax: 

```bash
list_variable[index]
```

For example, `grid_of_colors[0][1]` would evaluate to `green` and `grid_of_colors[1][0]` would evaluate to `blue`.

See the standard library reference for the list of function for manipulating lists and sets.

*Default value:* empty list or set depending on the type.

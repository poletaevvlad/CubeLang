# Operators

## Binary operators

CubeLang supports multiple binary operators listed bellow in the order of ascending precedence. cubeland is using an infix notation.

The order of computation is determined by operator precedence. It can be changed by using parenthesis or assigning part of the expression to the variable.

### `a xor b` 

*Types:* `boolean xor boolean` → `boolean` 
*Precedence:* 1

Exclusive or of the boolean operands. Evaluates to  `true` if one of the operands is `true` and the other one is `false`.


### `a or b`

*Types:* `boolean or boolean` → `boolean`
*Precedence:* 2

Logical or of the boolean operands. Evaluates to `true` if either left or right operand is `true`.


### `a and b`

*Types:* `boolean and boolean` → `boolean`
*Precedence:* 3

Logical or of the boolean operands. Evaluates to `true` if both operands are `true`.


### `a == b`

*Types:* `T == T` → `boolean` where `T` is any type
*Precedence:* 4

Evaluates to `true` if the values of operands are equal. Lists are equal if their sizes are equal and `a[i] == b[i]` for each `i`. Sets are equal if their sizes are equal and `b` contains every element in `a`.

*Note:* This operator should not be used when comparing real values.


### `a != b`

*Types:* `T != T` → `boolean` where `T` is any type
*Precedence:* 4

Evaluates to `false` if the values of operands are equal, `true` otherwise. The value returned by this operator is opposite of the value of `==` operator: `a != b` is the same as `not(a == b)`.

*Note:* This operator should not be used when comparing real values.


### `a < b`, `a > b`, `a <= b`, `a >= b`
*Types:* `real ( < | > | <= | >= ) real` → `boolean`
*Precedence:* 5

Evaluates to `true` if the value of the left operand is less than (`<`), greater than (`>`), less than or equal (`<=`), greater than or equal (`>=`) the value of the right operand.


### `a + b`, `a - b`
*Types:* `int ( + | - ) int` → `int`; `real ( + | - ) real` → `real`
*Precedence:* 6

Performs arithmetic addition (`+`) or subtraction (`-`) of operands' values. 

If both operands are integers then an integer is produced. If at least one of the operands is real then the other one is implicitly converted to real and the real value is produced.


### `a * b`
*Types:* `int * int` → `int`; `real * real` → `real`
*Precedence:* 7

Performs arithmetic multiplication of operands' values.

If both operands are integers then an integer is produced. If at least one of the operands is real then the other one is implicitly converted to real and the real value is produced.


### `a / b`
*Types:* `real / real` → `real`
*Precedence:* 7

Performs arithmetic division of operands' values. The resulting value is always real. If the integer division is needed, use `floor` function to get the whole part of the real number: `floor(a / b)`.


### `a % b`
*Types:* `int % int` → `int`
*Precedence:* 7

Evaluates the remainder of integer division.

## Unary operator

The only unary operator supported by CubeLang is unary minus:

### `-a`
*Types:* `-int` → `int`; `-real` → `real`

Evaluates the number with the same absolute value but opposite sign.

Boolean negation operation is implemented as a standard library function `not`.

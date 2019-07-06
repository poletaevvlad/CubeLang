# Standard library

## Math functions

```bash
func round(value: real): int
```
Rounds the argument to a nearest integer.

<hr>

```bash
func floor(value: real): int
```
Returns the largest integer smaler or equal to `value`.

<hr>

```bash
func ceil(value: real): int
```

Returns the smallest integer larger or equal to `value`.

<hr>

```bash
func sqrt(value: real): real
```

Returns the square root of `value`.

<hr>

```bash
func pow(a: int, b:int): int
func pow(a: real, b:real): real
```

Raises `a` to the power of `b` -- a<sup>b</sup>.

<hr>

```bash
func max(a: int, b: int): int
func max(a: real, b: real): real
func max(collection: list of int): int
func max(collection: list of real): real
func max(collection: set of int): int
func max(collection: set of real): real
```

Returns the largest argument or the largest item in the collection of numbers.

<hr>

```bash
func min(a: int, b: int): int
func min(a: real, b: real): real
func min(collection: list of int): int
func min(collection: list of real): real
func min(collection: set of int): int
func min(collection: set of real): real
```

Returns the smallest argument or the smallest item in the collection of numbers.

<hr>

```bash
func sign(value: float): int
```

Returns zero if `value` is zero, one if `value` is positive and negative one otherwise.

<hr>

```bash
func not(value: boolean): boolean
```

Returns `true` if `value` is `false`, and `false` otherwise.

## Collection functions

```bash
func size(collection: list of T): int
func size(collection: set of T): int
```
Returns a number of elements in the collection.

<hr>

```bash
func contains(collection: list of T, value: T): boolean
func contains(collection: set of T, value: T): boolean
```
Returns true if the value is present in the collection, false otherwise.

<hr>

```bash
func clear(collection: list of T, value: T)
func clear(collection: set of T, value: T)
```
Removes all values from the collection.


### Set functions

```bash
func add(collection: set of T, value: T)
```
Adds a new value to the set.

<hr>

```bash
func remove(collection: set of T, value: T): boolean
```
Removes a value from the set. Returns true if the value were present, false otherwise.

<hr>

```bash
func set_of(values: T, ...): set of T
```
Creates a new set containing all values passed as arguments to this function.


### List functions

```bash
func add_first(collection: list of T, value: T)
```
Adds an elements to the begining of a list. Its index will be 0.

<hr>

```bash
func add_last(collection: list of T, value: T)
```

Adds an element to the end of a list. Its index will be one less than the size of a list.

<hr>

```bash
func add_at(collection: list of T, index: int, value: T)
```

Adds an elements to the list at a specified location.

<hr>

```bash
func remove_first(collection: list of T): T
```

Removes and returns the first element of a list.

<hr>

```bash
func remove_last(collection: list of T): T
```

Removes and returns the last element of a list.

<hr>

```bash
func remove_at(collection: list of T, index: int): T
```

Removes and returns an element of a list at specified location.

<hr>

```bash
func new_list(size: int, value: T): list of T
```

Creates a new list of length `size` and fills it with `value`s.

<hr>

```bash
func index_of(collection: list of T, value: T): int
```

Returns index of an element in a list if it is present, or -1 otherwise.

<hr>

```bash
func list_of(values: T, ...): list of T
```

Creates a new list containing all values passed as arguments to this function.

## Runtime library functions

```bash
func push_orientation()
```

Pushes the current orientation into the stack.

<hr>

```bash
func pop_orientation()
```

Pops orientation from the stack and generates necessary rotations to bring the cube to this orientation.

<hr>

```bash
func suspend_rotations()
```

Prevent cubelang runtime from outputing rotations. This creates two new states: apparent orientation and actual orientation. All turning will be converted to the apparent orientation.

<hr>

```bash
func resume_rotations()
```

Outputs necessary turns to synchronize apparent and actual orientations. All future turns will be displayed to the user.

<hr>

```bash
func exit()
```

Terminates the program.

<hr>

```bash
func print(arg: T, ...)
```

Prints all the arguments to the standard error stream.


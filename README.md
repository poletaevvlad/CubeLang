# CubeLang

CubeLang is a strongly and statically typed domain-specific procedural programming language created for solving twisting cube puzzles like Rubik's cubes.

<hr>

## Installation

CubeLang requires Python 3.6 or newer to functions. For the information on how to install Python, please refer to the [download page](https://www.python.org/downloads/).

The easiest way to install CubeLang is by using pip. On how to install pip please refer to the [manual](https://pip.pypa.io/en/stable/installing/).

```bash
pip install CubeLang
```

After the installation, `cubelang` and `cubelang-scramble` command-line utilities will be available.

#### Development

For the development of CubeLang clone this repository and install dependencies.

```bash
git clone https://github.com/poletaevvlad/CubeLang.git
cd CubeLang
pip install lark-parser termcolor
pip install -r test_requirements.txt
```

Tests for the interpreter are located in the `test` directory, tests for the example programs are in the `test_examples` directory. CubeLang uses pytest for testing.

## Examples

There are two example programs written in CubeLang. They are located in the `examples` directory of the GitHub repository.

The results of executing example programs are shown below.

**Beginner's method** (3&times;3&times;3 cube) @ [examples/beginner](examples/beginner)


| [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_beginner_1.png)](https://www.youtube.com/watch?v=dzqH6hYKuco) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_beginner_2.png)](https://www.youtube.com/watch?v=7hDjaBIfIeU) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_beginner_3.png)](https://www.youtube.com/watch?v=-jjZ7OJNd4g) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_beginner_4.png)](https://www.youtube.com/watch?v=_PxvFn2qd5M) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_beginner_5.png)](https://www.youtube.com/watch?v=D6EbnLoh51s) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_beginner_6.png)](https://www.youtube.com/watch?v=NhziEe3avvM)
|--|--|--|--|--|--|

**Pocket cube** (2&times;2&times;2 cube) @ [examples/pocket-cube](examples/pocket-cube)

| [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_pocket_1.png)](https://www.youtube.com/watch?v=NhziEe3avvM) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_pocket_2.png)](https://www.youtube.com/watch?v=z7OPzDXNGSA) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_pocket_3.png)](https://www.youtube.com/watch?v=MO36Aj56TVw) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_pocket_4.png)](https://www.youtube.com/watch?v=ZX0P7-SvCWod5M) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_pocket_5.png)](https://www.youtube.com/watch?v=an4ovEBPumc) | [![](https://raw.githubusercontent.com/poletaevvlad/CubeLang/master/docs/images/example_pocket_6.png)](https://www.youtube.com/watch?v=Qvmfpi6yIWQ)
|--|--|--|--|--|--|

## Documentation

You can find the language documentation in the [`docs`](./docs) directory in the root of this repository.

Documentation consists of the following sections:

**Usage** @ [docs/usage.md](https://github.com/poletaevvlad/CubeLang/blob/master/docs/usage.md)<br>Describes the command line arguments for the interpreter and scrambler utility application.

**Variables and types** @ [docs/types.md](https://github.com/poletaevvlad/CubeLang/blob/master/docs/types.md) <br> Describes how to define a variable, determine it's scope. Lists data types, supported by CubeLang.

**Operators** @ [docs/operators.md](https://github.com/poletaevvlad/CubeLang/blob/master/docs/operators.md) <br> Lists binary and unary operators supported by CubeLang.

**Conditions and loops** @ [docs/statements.md](https://github.com/poletaevvlad/CubeLang/blob/master/docs/statements.md) <br> Shows the syntax of most execution controlling operators: conditions, loops, and `orient` operator.

**Cube turns and rotations** @ [docs/actions.md](https://github.com/poletaevvlad/CubeLang/blob/master/docs/actions.md) <br> Shows the syntax of cube turning and rotating commands used by the language and some of the interpreter's command line arguments.

**Indexing** @ [docs/indexing.md](https://github.com/poletaevvlad/CubeLang/blob/master/docs/indexing.md) <br> Describes how to access sticker colors of a cube.

**Standard library** @ [docs/stdlib.md](https://github.com/poletaevvlad/CubeLang/blob/master/docs/stdlib.md) <br> A reference for all functions and constants included in the standard library.

## License

This software is licensed under MIT license. Please refer to [LICENSE](https://github.com/poletaevvlad/CubeLang/blob/master/LICENSE) file of this repository for more information.

Copyright &copy; Vlad Poletaev, 2019, 2020

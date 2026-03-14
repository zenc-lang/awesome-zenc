# Awesome Zen C

Official examples, community projects, and Rosetta Code implementations for the **Zen C** programming language.

## Overview

This repository serves as the primary collection of examples for Zen C. It demonstrates the language's modern features, ergonomics, and seamless C interoperability across various domains, from simple algorithms to systems programming.

## Repository Structure

- `rosetta/`: A wide collection of [Rosetta Code](https://rosettacode.org/wiki/Category:Zen_C) implementations showcasing idiomatic Zen C solutions to common programming tasks.
- `internal/`: Internal feature demos, including networking, SIMD, graphics, and more.

## Rosetta Code

Many of the examples in this repository are extracted from the [Zen C category on Rosetta Code](https://rosettacode.org/wiki/Category:Zen_C). 

We are always looking to expand our presence there! All additions and improvements to Zen C tasks on Rosetta Code are greatly appreciated and help showcase the language's capabilities to the wider programming community.

## Some Examples

### Rosetta Code
- **[FizzBuzz](examples/rosetta/FizzBuzz.zc)**: The classic programming interview task.
- **[Fibonacci Sequence](examples/rosetta/Fibonacci_sequence.zc)**: Demonstrating recursion and iteration.
- **[Ternary Logic](examples/rosetta/Ternary_logic.zc)**: Implementing non-binary logic systems.
- **[Echo Server](examples/rosetta/Echo_server.zc)**: Simple networking implementation.
- **[Caesar Cipher](examples/rosetta/Caesar_cipher.zc)**: Basic text manipulation and pattern matching.

### Internal Demos
- **[SIMD](examples/internal/simd.zc)**: Leveraging hardware acceleration for performance.
- **[Networking](examples/internal/networking/)**: Real-world communication examples.
- **[Games](examples/internal/games/zen_craft/)**: Interactive demos built with Zen C.

To run any example, ensure you have the [Zen C compiler](https://github.com/z-libs/Zen-C) installed. Since this repository is intended to be used as a submodule at `examples/` in the Zen C root, you can run examples like this:

```bash
# From Zen-C root
zc run examples/rosetta/Hello_world_Newbie.zc
```

> [!TIP]
> You can also compile these examples to standalone executables:
> ```bash
> zc build examples/rosetta/FizzBuzz.zc -o fizzbuzz
> ./fizzbuzz
> ```

## Contributing

Found a bug or want to add a new example? Contributions are welcome! Please feel free to open a Pull Request or report an Issue.

## Related Projects

- **[Zen-C](https://github.com/z-libs/Zen-C)**: The core compiler and standard library.
- **[Zen-C-Docs](https://github.com/z-libs/Zen-C-Docs)**: Official documentation and language reference.

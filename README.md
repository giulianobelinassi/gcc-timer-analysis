# GCC Compilation Timing Analysis
An set of scripts and programs to help the analysis of GCC compilation time 
This set of tools is intended for my Master Thesis qualification

## How this works
  Currently, we compute the compilation time for each file by replacing the `gcc` driver with 
  a custom wrapper that compute both timestamps before and after the call to the real `gcc`.
  We are careful to also replace the `xgcc` and `xg++` binaries generated
  by the bootstrap process. Our wrapper produces a file that we then parse by using the `plotter.py` script.

## Dependencies:
We mainly have the following dependencies:
  * Python3
    * Numpy
    * Matplotlib
  * Bash
  * GNU Compiler Collections
    * GCC

## Usage:
Use the script `gcc_builder.sh` inside the `scripts` folder to generate the dataset. The instructions
regarding how to use it is printed by calling the script without any paramenters. Here is an example of how to use it:

```
./gcc_builder.sh ~/gcc_svn/trunk/ /tmp/test_build /tmp/time_results-1.txt 8 --disable-checking --disable-bootstrap
```

The generated dataset can be parsed and the time graphic be plotted using the `plotter.sh` script. All instructions
regarding how to use it is printed by calling it without any parameters. Here is one example of usage:

```
./plotter.py --input-file /tmp/time_results-1.txt --output-file /tmp/test.pdf --filter
```

## License
Read the file LICENSE in this folder.

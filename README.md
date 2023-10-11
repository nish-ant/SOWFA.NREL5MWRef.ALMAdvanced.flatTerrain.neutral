# SOWFA-6 WT case

A reference SOWFA-6 case using ABL and ALMAdvanced solvers.

Several modifications might be needed in the run scripts to make it suited to your environment.

## How to use

For a new case, copy the `run.U8msRough1E-3m` directory and rename it accordingly. 

Make appropriate modifications in the `userInput.json` file found in the directory and run the `run.prepare` script.

The script invokes `common/helper.prepare` which copies and modifies the ABL and ALMAdvanced solver scripts in the current run directory. 

NOTE: The [`jq`](https://jqlang.github.io/jq/) bash utility is needed to read the JSON file.

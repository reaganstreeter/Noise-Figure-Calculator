import sys
import os
# Necessary to import the compute_cascaded_nf from friis.py in the Utilities folder to the Scripts folder.
# If friis.py and noise_figure_cascde.py are located in the same folder, line 6 can be deleted and line 11 
# must be amended to "from friis import compute_cascaded_nf"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from Utilities.friis import compute_cascaded_nf

# Functional Block 1

# The first stage of the script is used to handle the input of either
# interactively enterred component data, or data parsed into the script
# via a CSV file. To this end, a user-friendly interface is established

print("=" * 50)
print("Cascaded Noise Figure Calculator")
print("=" * 50)
print()
print("Select input mode:")
print("1 - Interactive entry")
print("2 - CSV file")
print()

# The chosen data entry method is saved in the variable "mode"
# .strip() cleans the input in case the user accidentally enters a space on
# either side of their input. To continuously prompt the user for an input
# mode until a valid one is given, a while True loop is used.

while True:
    mode = input("Enter 1 or 2: ").strip()
    if mode in ("1", "2"):
        break
    print("\nInvalid selection. Please enter 1 or 2.")

# Initialise a list to store the various component data
stages = []

# If the interactive entry mode is selected, then the following
# flow is initiated
if mode == "1":
    
    # To continuously prompt the user for a valid input for the number of stages
    # in the system until a valid answer is given, another while True loop is used.
    # The difference this time is that the condition to break the loop is not one of
    # two specific values, so a try/except block is also applied.
    
    while True:
        n_input = input("\nNumber of stages: ").strip()
        try:
            n = int(n_input)
            # As this calculator is for cascaded components, it only makes sense for the
            # number of stages being calculated on to be >1.
            if n > 1:
                break
            print("Invalid input. Please enter a whole number greater than 1.")
            # ValueError is the error returned by python if the conversion of n_input by
            # int() fails to return an integer value. If this occurs, the user is prompted
            # to try again
        except ValueError:
            print("Invalid input. Please enter a whole number greater than 1.")

    print()
    # After the number of component stages is established, a for loop
    # is used to collect the component name, its gain, and noise figure in dB.
    # These are obtained via input messages and stored in respective variables,
    # after which, they are appended to the stages list which becomes a 
    # list of dictionaries
    for i in range(n):
        # Using an f-string below for ease of formatting implementation
        print(f"Stage {i + 1}:")



        while True:
            name = input("Component name: ").strip()
            try:
                if int(name) < 1:
                    print("Invalid input: component name cannot be an integer less than 1.")
                    continue
            except ValueError:
                pass
            break

        while True:
            gain_input = input("Gain (dB): ").strip()
            try:
                gain_db = float(gain_input)
                break
            except ValueError:
                print("Invalid input: the gain for a component must be a number.")
        
        while True:
            nf_input = input("Noise figure (dB): ").strip()
            try:
                nf_db = float(nf_input)
                if nf_db >= 0:
                    break
                print("Invalid input: noise figure in dB must be equal to or greater than 0.")
                continue
            except ValueError:
                print("Invalid input: noise figure input must be a number.")

        stages.append({"name": name, "gain_db": gain_db, "nf_db": nf_db})
        print()

# If the CSV file data entry mode is selected, then the following process
# is initiated
elif mode == "2":
    # The filepath of the CSV file is obtained via an input message
    # and stored as a string in the variable "filepath"
    filepath = input("\nCSV file path: ").strip()
    
    # Now, the CSV is read and converted into a pandas dataframe
    df = pd.read_csv(filepath)

    # To ensure that the CSV contains the correct and required columns,
    # a simple check is performed using a set containing the names of the
    # required columns
    required_columns = {"name", "gain_db", "nf_db"}
    if not required_columns.issubset(df.columns):
        print(f"\nError: CSV must contain columns titled as: {required_columns}")
        # sys.exit(1) is used to terminate the program in the event of the
        # above error occurring
        sys.exit(1)
    
    # Using the list "stages" created earlier, the columns of the dataframe, df, 
    # that match with "name", "gain_db", and "nf_db" are selected, disregarding
    # all other columns in the CSV (if others exist). to_dict("records") then
    # converts that selection into the list of dictionaries structure needed for
    # the remainder of the program
    stages = df[["name", "gain_db", "nf_db"]].to_dict("records")

# Functional Block 2

# The next stage of the calculator script takes the component data captured during
# the input process in Block 1, and applies it to the function created in the
# friis.py script located in the Utilities folder of this repository. To this end,
# the stages list of dictionaries is now fed into the compute_cascaded_nf function,
# yielding a dictionary that contains all critical knowledge relating to the noise
# figure calculation, including the total cascaded noise figure of the system, the
# cumulative noise figure as it increases across each stage, the individual contributions
# to the noise factor from each stage, as well as the names of the stages

results = compute_cascaded_nf(stages)

# The total gain of the system is also computed here by summing over the gain values 
# stored in the stages list of dictionaries

total_gain_db = 0

for i, name in enumerate(results["names"]):
    total_gain_db += stages[i]["gain_db"]

# Functional Block 3

# The second last stage of the calculator script takes the output of applying the stages
# list of dictionairies and uses it to print a table to the terminal to display the
# results of the calculation. 

# The total cascaded noise figure of the system is extracted using:
total_nf_db = results["cascaded_nf_db"]

# The contributions from each stage are extracted using:
stage_contributions = results["stage_contributions"]

# The cumulative noise figure as it increases across subsequent stages is extracted using:
cumulative_nf_db = results["cumulative_nf_db"]

# The stage/component names are extracted via:
component_names = results["names"]

# The percentage contribution of each stage to the noise factor is one of the results
# that is to be displayed in the terminal-printed table. To this end, the quantity is computed via:
noise_factor_total_linear = 10 ** (total_nf_db / 10)
contributions_percentage = [(term / (noise_factor_total_linear - 1)) * 100
                            for term in stage_contributions]

# For formatting the terminal-printed table, column widths are specified below:
w_stage = 6
w_name = 15
w_gain = 11
w_nf = 10
w_cumulative = 22
w_contribution = 18

# The header row for the table will contain the following column titles:
header = (
    f"{'Stage':<{w_stage}}"
    f"{'Name':<{w_name}}"
    f"{'Gain (dB)':>{w_gain}}"
    f"{'NF (dB)':>{w_nf}}"
    f"{'Cumulative NF (dB)':>{w_cumulative}}"
    f"{'Contribution (%)':>{w_contribution}}"
)

# A "separator" will be used to organise the table neatly into its various
# sections
separator = "-" * len(header)

print()
# Constructing the header row of the table:
print(separator)
print(header)
print(separator)

# Constructing the body rows of the table, where there is one row for each stage of
# the system, showing the various relevant results produced by the compute_cascaded_nf function

for i, name in enumerate(results["names"]):
    gain_db  = stages[i]["gain_db"]
    nf_db    = stages[i]["nf_db"]
    cumul_nf = results["cumulative_nf_db"][i]
    contrib  = contributions_percentage[i]
 
    print(
        f"{i + 1:<{w_stage}}"
        f"{name:<{w_name}}"
        f"{gain_db:>{w_gain}.2f}"
        f"{nf_db:>{w_nf}.2f}"
        f"{cumul_nf:>{w_cumulative}.2f}"
        f"{contrib:>{w_contribution}.1f}"
    )
 
print(separator)
print(f"\nCascaded NF: {total_nf_db:.2f} dB")
print(f"Total gain: {total_gain_db:.2f} dB\n")

# Functional Block 4

# The final functional block/stage of the script deals with plotting the results, so that a visual
# representation of the evolution of the noise figure is provided, as well as the tabulated results

# The x-tick labels are based on the stage names present in the results dictionary
stage_labels = results["names"]
x_tick_positions = range(len(stage_labels))

# Now creating two subplots

fig, (ax1, ax2) = plt.subplots(2, 1, figsize = (8, 8))

# The first plot will display the cumulative noise figure as a line graph
ax1.plot(x_tick_positions, results["cumulative_nf_db"], marker = 'o', color = "tab:blue")
ax1.set_xticks(list(x_tick_positions))
ax1.set_xticklabels(stage_labels)
ax1.set_ylabel("Cumulative NF (dB)")
ax1.set_title("Cascaded Noise Figure Evolution")
ax1.grid(True, alpha = 0.3)

# The second plot will display the per-stage percentage contribution to the noise figure as a bar chart
colours = plt.cm.tab10(np.linspace(0, 1, len(stage_labels)))

ax2.bar(x_tick_positions, contributions_percentage, color = colours)
ax2.set_xticks(list(x_tick_positions))
ax2.set_xticklabels(stage_labels)
ax2.set_ylabel("Contribution to Total NF (%)")
ax2.set_title("Per-Stage Noise Contribution")
ax2.grid(True, axis = "y", alpha = 0.3)

fig.tight_layout()

plt.show()

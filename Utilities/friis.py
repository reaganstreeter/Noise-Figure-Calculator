import numpy as np

# The compute_cascaded_nf function takes a list of dictionaries with gain
# and NF parameters in dB form and transforms them into linear units, 
# depending on if a linear flag is activated or not. The function then 
# uses the converted NF/gain parameters in the typical Friis equation 
# to compute and return the cascaded NF of the system
def compute_cascaded_nf(stages, linear=False):

    # The following parameters are used as inputs to the function: 
        # stages : list of dictionaries
            # Each dictionary must contain:
                # "name": data type of string - the component label
                # "gain_db": data type of float - the gain in dB (negative for lossy components)
                # "nf_db": data type of float - noise figure in dB
            # If linear=True, "gain_db" and "nf_db" are interpreted as linear factors 
            # and are not from dB.
        # linear : bool, optional
            # If True, values in stages are treated as linear factors rather
            # than dB. Default is False.

    # The function returns
        # A dictionary with the following keys and data types, representing the parameters below:
        # "cascaded_nf_db": float - total cascaded noise figure in dB
        # "cumulative_nf_db": list[float] - cumulative NF in dB after each stage
        # "stage_contributions": list[float] - individual Friis term for each stage (linear)
        # "names": list[str] - stage names passed through for plot labels

    # The first stage of the function converts the dB inputs to linear values
    # First a list is intialised to store the linear values
    linear_stages = []
    # A for loop runs over the entries of the input dictionary
    for stage in stages:
        # An if statement is used to check for the presence of the linear flag
        if linear:
            G = stage["gain_db"]
            F = stage["nf_db"]
        # As the default is linear = False, the else statement converts from dB to linear
        else:
            G = 10 ** (stage["gain_db"] / 10)
            F = 10 ** (stage["nf_db"] / 10)
        # The last part of the loop appends the current key-value pair to the end of 
        # the list
        linear_stages.append({"name": stage["name"], "G": G, "F": F})

    # The second stage of the function is where the real Friis formula calculation
    # takes place. The calculation begins by initialising a cumulative noise factor 
    # and gain variables
    cumulative_F = 1.0
    gain_product = 1.0
    # The cumulative noise factor and Friis terms are also collected into respective lists
    cumulative_F_list = []
    friis_terms = []

    # A for loop does the summation required by the Friis equation using the
    # linear_stages dictionary created previously
    for stage in linear_stages:
        # General form of the n-th term in the Friis equation
        term = (stage["F"] - 1) / gain_product
        # Increments the cumulative noise factor by adding the current term to it
        cumulative_F += term
        # Adds the current Friis term to the cumulative and terms lists
        friis_terms.append(term)
        cumulative_F_list.append(cumulative_F)
        # Calculates the new total system gain to the n-th stage via iterative 
        # multiplication
        gain_product *= stage["G"]

    # The third stage of the function converts cumulative noise factor list to dB
    cumulative_nf_db = []
    for f in cumulative_F_list:
        cumulative_nf_db.append(10 * np.log10(f))

    # The final stage of the function returns all the key parameters required from
    # the calculator and for plotting purposes
    return {
        "cascaded_nf_db": cumulative_nf_db[-1],
        "cumulative_nf_db": cumulative_nf_db,
        "stage_contributions": friis_terms,
        "names": [stage["name"] for stage in linear_stages],
    }
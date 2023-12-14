# We are using as reference: https://cobrapy.readthedocs.io/en/latest/building_model.html

import pandas as pd
from cobra import Model, Reaction, Metabolite, io

def get_stoich_and_met(metabolite_group):
    split = metabolite_group.split()
    if len(split) == 1:
        return 1, metabolite_group
    elif len(split) == 2:
        return float(split[0]), split[1]
    else:
        return None, None


def get_stoich_by_met(eqn_side):

    met_id_to_stoich = {}
    eqn_side = eqn_side.strip()
    metabolite_groups = eqn_side.split("+")
    for curr_met_group in metabolite_groups:
        curr_met_group = curr_met_group.strip()
        stoich, met_id = get_stoich_and_met(curr_met_group)
        if met_id is not None:
            met_id_to_stoich[met_id] = stoich
    return met_id_to_stoich


def get_left_and_right_side(rxn_string):
    """Return the left and right side of this formula.  
    The first step is to figure out how the sides of the equations are being delimited."""

    delim = None
    delims_to_try = ["<->", "<=>", "<-->", "<==>", "<--", "<==", "<-", "<=", "-->", "==>", "->", "=>"]
    for curr_delim in delims_to_try:
        if curr_delim in rxn_string:
            delim = curr_delim
            break
    if delim is None:
        raise Exception("Delimiter being left and right side of equation could not be found.")
    split_eqn = rxn_string.split(delim)
    return split_eqn[0], split_eqn[1]


def get_rxn_dict(rxn_string, met_name_to_object):
    """Create and return a reaction dictionary mapping a metabolite object to its stoichiometry in that reaction."""

    left_side, right_side = get_left_and_right_side(rxn_string)
    left_metabolite_to_stoich = get_stoich_by_met(left_side)
    right_metabolite_to_stoich = get_stoich_by_met(right_side)

    dict_met_obj_to_stoich = {}
    for met, stoich in left_metabolite_to_stoich.items():
        stoich = -1 * stoich
        met_obj = met_name_to_object[met]
        dict_met_obj_to_stoich[met_obj] = stoich

    for met, stoich in right_metabolite_to_stoich.items():
        met_obj = met_name_to_object[met]
        dict_met_obj_to_stoich[met_obj] = stoich    

    return dict_met_obj_to_stoich


def get_met_name_to_object(open_sheet):
    """Return metabolite name to a Metabolite object that has the information for that metabolite."""

    met_name_to_object = {}

    names = open_sheet["Abbreviation"]
    descrips = open_sheet["Description"]
    comps = open_sheet["Compartment"]
    formulae = open_sheet["Neutral formula"]
    
    for name, descrip, comp, formula in zip(names, descrips, comps, formulae):
        descrip = get_string_value_from_excel(descrip)
        comp = get_string_value_from_excel(comp)
        formula = get_string_value_from_excel(formula)

        met_obj = Metabolite(name, formula=formula, name=descrip, compartment=comp)
        met_name_to_object[name] = met_obj

    return met_name_to_object


def get_string_value_from_excel(string):
    """This function is for processing strings read from Excel.
    If the string is well-defined, return it.  Otherwise, return the empty string."""

    if type(string) == type(""):
        return string
    else:
        return ""


def get_cobrapy_model(excel_file, model_id=None):
    """Return cobrapy model given contents of excel file, and name model (optional)"""

    if model_id is None:
        model = Model("model")
    else:
        model = Model("model_id")

    xlsx = pd.ExcelFile(excel_file)
    rxn_sheet = pd.read_excel(xlsx, "Reaction List")
    met_sheet = pd.read_excel(xlsx, "Metabolite List")
    met_name_to_object = get_met_name_to_object(met_sheet)

    names = rxn_sheet["Abbreviation"]
    descrips = rxn_sheet["Description"]
    subsystems = rxn_sheet["Subsystem"]
    rxns = rxn_sheet["Reaction"]
    revs = rxn_sheet["Reversible"]
    lbs = rxn_sheet["Lower bound"]
    ubs = rxn_sheet["Upper bound"]
    objectives = rxn_sheet["Objective"]
    gprs = rxn_sheet["GPR"]

    reactions = []
    obj_rxn = None

    for name, descrip, rxn, subsys, rev, lb, ub, objective, gpr in \
        zip(names, descrips, rxns, subsystems, revs, lbs, ubs, objectives, gprs):
        reaction = Reaction(name)
        reaction.name = get_string_value_from_excel(descrip)
        reaction.subsystem = subsys
        reaction.lower_bound = lb
        reaction.upper_bound = ub
        reaction.gene_reaction_rule = get_string_value_from_excel(gpr)

        reaction_dict = get_rxn_dict(rxn, met_name_to_object)
        reaction.add_metabolites(reaction_dict)

        # Then, create the formula and add the reaction to the model.
        reactions.append(reaction)
        # print (reaction) 
        # input()

        # Keep track of any objective function we might have around.
        if objective == 1:
            obj_rxn = name

    model.add_reactions(reactions)
    # If an objective function has been defined, specify it here.
    model.objective = obj_rxn
    return model


if __name__ == '__main__':

    test_model_file = "sample_model.xlsx"
    cobrapy_model = get_cobrapy_model(test_model_file)
    io.write_sbml_model(cobrapy_model, "test.xml")
    solution = cobrapy_model.optimize()
    print (solution)
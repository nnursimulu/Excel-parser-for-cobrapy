import pandas as pd
from cobra import Model, Reaction, Metabolite

def get_rxn_dict(rxn, met_name_to_object):

    reaction_dict = {}
    #TODO
    # reaction.add_metabolites({
    # malACP_c: -1.0,
    # h_c: -1.0,
    # ddcaACP_c: -1.0,
    # co2_c: 1.0,
    # ACP_c: 1.0,
    # omrsACP_c: 1.0
    # })
    return reaction_dict


def get_met_name_to_object(open_sheet):
    """Return metabolite name to a Metabolite object that has the information for that metabolite."""

    met_name_to_object = {}

    names = open_sheet["Abbreviation"]
    descrips = open_sheet["Description"]
    comps = open_sheet["Compartment"]
    formulae = open_sheet["Neutral formula"]
    
    for name, descrip, comp, formula in zip(names, descrips, comps, formulae):
        met_obj = Metabolite(name, formula=formula, name=descrip, compartment=comp)
        met_name_to_object[name] = met_obj

    return met_name_to_object


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

    for name, descrip, rxn, subsys, rev, lb, ub, objective, gpr in \
        zip(names, descrips, rxns, subsystems, revs, lbs, ubs, objectives, gprs):
        reaction = Reaction(name)
        reaction.name = descrip
        reaction.subsystem = subsys
        reaction.lower_bound = lb
        reaction.upper_bound = ub
        reaction.gene_reaction_rule = gpr

        reaction_dict = get_rxn_dict(rxn, met_name_to_object) #TODO
        reaction.add_metabolites(reaction_dict)
        # Then, create the formula and add the reaction to the model.
        # https://cobrapy.readthedocs.io/en/latest/building_model.html

        reactions.append(reaction)
        if objective == 1:
            model.objective = name

    model.add_reactions(reactions)
    return model


if __name__ == '__main__':

    test_model_file = "sample_model.xlsx"
    cobrapy_model = get_cobrapy_model(test_model_file)
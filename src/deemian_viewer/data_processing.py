import pandas as pd


def setup_dataframe(data):
    if data.empty:
        return pd.DataFrame(columns=["id 1",
                 "subject 1\ninfo",
                 "id 2",
                 "subject 2\ninfo",
                 "distance",
                 "interaction\ntype",
                 "conformation"])

    data.reset_index(inplace=True, drop=True)
    data["space"] = " "
    data["dot"] = "."
    data["subject 1\ninfo"] = data["atom_name_s1"] +\
        data["space"] +\
        data["residue_name_s1"] +\
        data["space"] +\
        data["residue_number_s1"].astype(str) +\
        data["dot"] +\
        data["chain_id_s1"]
    data["subject 2\ninfo"] = data["atom_name_s2"] +\
        data["space"] +\
        data["residue_name_s2"] +\
        data["space"] +\
        data["residue_number_s2"].astype(str) +\
        data["dot"] +\
        data["chain_id_s2"]
    data = data[["atom_id_s1",
                 "subject 1\ninfo",
                 "atom_id_s2",
                 "subject 2\ninfo",
                 "distance",
                 "interaction_type",
                 "conformation"]]
    data = data.rename(columns={
        "atom_id_s1": "id 1",
        "atom_id_s2": "id 2",
        "interaction_type": "interaction\ntype"
    })
    
    return data

def get_groupby_int_type_df(df):
    groupby_int_type_df_dict = {}
    if df.empty:
        return groupby_int_type_df_dict
    data = df.groupby('interaction_type')
    if 'electrostatic_cation' in data.indices:
        cation_df = data.get_group('electrostatic_cation')
        groupby_int_type_df_dict["electrostatic_cation"] = cation_df
    if 'electrostatic_anion' in data.indices:
        anion_df = data.get_group('electrostatic_anion')
        groupby_int_type_df_dict["electrostatic_anion"] = anion_df
    
    return groupby_int_type_df_dict
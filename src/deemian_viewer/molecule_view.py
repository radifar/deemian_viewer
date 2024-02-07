import json
import os

from PySide6 import QtCore, QtWidgets
from PySide6.QtWebEngineWidgets import QWebEngineView

from deemian_viewer.data_processing import get_groupby_int_type_df

def selection_parser(sele_string):
    for sele_index, sele in enumerate(sele_string):
        if "resname" in sele:
            resname_index = sele.index("resname")
            resnames = sele[resname_index+1:]
            for i, resname in enumerate(resnames):
                resnames[i] = "[" + resname + "]"
            sele[resname_index+1:] = resnames
            sele_string[sele_index] = sele
        elif "resid_range" in sele:
            resid_range_index = sele.index("resid_range")
            resid_start, resid_stop = sele[resid_range_index+1:]
            sele_string[sele_index] = sele[:resid_range_index+1] + [resid_start + "-" + resid_stop]
    
    whole_sele = ""
    for sele in sele_string:
        selection_string = " ".join(sele).replace(
            "chain ", ":"
        ).replace(
            "resname ", ""
        ).replace(
            "resid_range", ""
        ) + " "
        whole_sele += selection_string
    
    return whole_sele

class MoleculeView(QWebEngineView):

    def __init__(self):
        super().__init__()
        # self.resize(780, 350)

        self.deemian_data = {}
        self.molselection = {}
        self.mols = {}
        self.int_subjects = []

        dirname = os.path.dirname(os.path.realpath(__file__))
        htmlpath = dirname + "/index.html"
        with open(htmlpath, 'r') as f:
            localurl = QtCore.QUrl.fromLocalFile(dirname)
            html = f.read().replace('js/', localurl.toString() + '/js/').replace('fonts/', localurl.toString() + '/fonts/')
            self.setHtml(html, localurl)
        
        self.runJS = self.page().runJavaScript
    
    def setup_stage(self):
        self.runJS('''stage.setParameters({
                        clipNear: 0,
                        clipFar: 100,
                        clipDist: 10,
                        clipMode: 'scene',
                        clipScale: 'relative',
                        fogNear: 50,
                        fogFar: 70,
                        fogMode: 'scene',
                        fogScale: 'relative',
                        cameraFov: 40,
                        cameraEyeSep: 0.3,
                        cameraType: 'perspective',
                        })''')

    @QtCore.Slot()
    def handle_tree_pair(self, value):
        name = value["name"]
        parent_name_original = value["parent"]
        parent_name = parent_name_original.replace(":","_")
        pair_index = [pair["name"] for pair in self.tree_pair_data].index(parent_name_original)

        if name == "all":
            for check_index, _ in enumerate(self.tree_pair_data[pair_index]["state"]):
                self.tree_pair_data[pair_index]["state"][check_index] = value["checked"]
        else:
            check_index = self.tree_pair_data[0]["interactions"].index(name)
            self.tree_pair_data[pair_index]["state"][check_index] = value["checked"]

        # helper class to use variable as match-case pattern
        # https://stackoverflow.com/questions/66159432/how-to-use-values-stored-in-variables-as-case-patterns
        class Parent():
            NAME = parent_name
        
        if value["checked"] is True:
            if name == "electrostatic as cation":
                self.runJS(f'as_cat_{parent_name}.setVisibility(true)')
                for unit in self.vis_res_chain_list:
                    match unit:
                        case [_, _, Parent.NAME, "electrostatic_cation"]:
                            res_chain, parent, name, int_type = unit
                            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').setVisibility(true)")
            elif name == "electrostatic as anion":
                self.runJS(f'as_an_{parent_name}.setVisibility(true)')
                for unit in self.vis_res_chain_list:
                    match unit:
                        case [_, _, Parent.NAME, "electrostatic_anion"]:
                            res_chain, parent, name, int_type = unit
                            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').setVisibility(true)")
            elif name == "all":
                self.runJS(f'as_cat_{parent_name}.setVisibility(true)')
                self.runJS(f'as_an_{parent_name}.setVisibility(true)')
                for unit in self.vis_res_chain_list:
                    match unit:
                        case [_, _, Parent.NAME, "electrostatic_cation"]:
                            res_chain, parent, name, int_type = unit
                            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').setVisibility(true)")
                        case [_, _, Parent.NAME, "electrostatic_anion"]:
                            res_chain, parent, name, int_type = unit
                            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').setVisibility(true)")

        else:
            if name == "electrostatic as cation":
                self.runJS(f'as_cat_{parent_name}.setVisibility(false)')
                for unit in self.vis_res_chain_list:
                    match unit:
                        case [_, _, Parent.NAME, "electrostatic_cation"]:
                            res_chain, parent, name, int_type = unit
                            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').setVisibility(false)")
            elif name == "electrostatic as anion":
                self.runJS(f'as_an_{parent_name}.setVisibility(false)')
                for unit in self.vis_res_chain_list:
                    match unit:
                        case [_, _, Parent.NAME, "electrostatic_anion"]:
                            res_chain, parent, name, int_type = unit
                            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').setVisibility(false)")
            elif name == "all":
                self.runJS(f'as_cat_{parent_name}.setVisibility(false)')
                self.runJS(f'as_an_{parent_name}.setVisibility(false)')
                for unit in self.vis_res_chain_list:
                    match unit:
                        case [_, _, Parent.NAME, "electrostatic_cation"]:
                            res_chain, parent, name, int_type = unit
                            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').setVisibility(false)")
                        case [_, _, Parent.NAME, "electrostatic_anion"]:
                            res_chain, parent, name, int_type = unit
                            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').setVisibility(false)")

    def handle_selection_popper(self, value):
        index = int(value["index"])
        name = self.selection_data[index]["name"] 
        if value["checked"]:
            self.runJS(f"{name}_cartoon.setVisibility(true); {name}_licorice.setVisibility(true)")
        else:
            self.runJS(f"{name}_cartoon.setVisibility(false); {name}_licorice.setVisibility(false)")

    def load_visibility_from_tree_pair(self):
        for tree_pair in self.tree_pair_data:
            parent = tree_pair["name"]
            for index, name in enumerate(tree_pair["interactions"]):
                checked = tree_pair["state"][index]
                value = dict(name=name, parent=parent, checked=checked)
                self.handle_tree_pair(value)

    def populate_tree_pair(self):
        self.runJS("window.treePair.length = 0")
        for int_subject in self.int_subjects:
            name = int_subject["name"]
            pair_data = dict(name=name,
                             interactions=['electrostatic as cation', 'electrostatic as anion'],
                             state=[True, True])
            self.tree_pair_data.append(pair_data)
        
            self.runJS(f"window.treePair.push({json.dumps(pair_data)})")

    
    def populate_tree_selection(self):
        self.runJS("window.treeSelection.length = 0")
        for name in self.molselection:
            selection_data = dict(name=name, state=True)
            self.selection_data.append(selection_data)
            self.runJS(f"window.treeSelection.push({json.dumps(selection_data)})")

    
    def build_basic_representation(self):
        for name, selection in self.molselection.items():
            molname = selection["parent"].replace(".", "_")
            sele_string = selection_parser(selection["sele_string"])

            self.runJS(f''' var traj_{molname};
                            var {name}_cartoon;
                            var {name}_licorice;
                            load_{molname}.then(function (o){{
                            // bail out if the component does not contain a structure
                            if( o.type !== "structure" ) return;
                            {name}_cartoon = o.addRepresentation( "cartoon", {{
                                sele: "{sele_string}",
                                color: "sstruc",
                                aspectRatio: 4.0,
                                scale: 1.5
                            }} );
                            {name}_licorice = o.addRepresentation( "licorice", {{
                                sele: "{sele_string} and (not protein or water or ion ))",
                                multipleBond: true
                            }} );
                            traj_{molname} = o.addTrajectory();
                            stage.autoView();
                            stage.viewerControls.zoom(0.35);
                            }} );
                            ''')
    
    def draw_interaction_shape(self, conf_num=1):
        
        for int_subject in self.int_subjects:
            subject1, subject2 = int_subject["subjects"]
            parent1 = self.molselection[subject1]["parent"].replace(".", "_")
            parent2 = self.molselection[subject2]["parent"].replace(".", "_")
            int_subject_df = self.deemian_data[int_subject["results"]]
            int_subject["groupby_int_type_df"] = get_groupby_int_type_df(int_subject_df)


            name = int_subject["name"].replace(":", "_")
            self.runJS(f'''var catshape_{name} = new NGL.Shape( "shape", {{ dashedCylinder: true, radialSegments:50}});
                          var anshape_{name} = new NGL.Shape( "shape", {{ dashedCylinder: true, radialSegments:50}})''')
            
            for int_type, int_df in int_subject["groupby_int_type_df"].items():
                for row in int_df[int_df["conformation"] == conf_num].itertuples():
                    id_1 = row[1]
                    id_2 = row[8]
                    coord_1 = list(row[7])
                    coord_2 = list(row[14])
                    res_chain_1 = (str(row[5]) + '.' + row[2], parent1, name, int_type)
                    res_chain_2 = (str(row[12]) + '.' + row[9], parent2, name, int_type)
                    if res_chain_1 not in self.vis_res_chain_list:
                        self.vis_res_chain_list.append(res_chain_1)
                    if res_chain_2 not in self.vis_res_chain_list:
                        self.vis_res_chain_list.append(res_chain_2)
                    
                    if int_type == 'electrostatic_cation':
                        self.runJS(f'''catshape_{name}.addCylinder( {coord_1}, {coord_2}, [0.53, 0.81, 0.93], 0.06, "{id_1}:{id_2} {int_type}" );''')
                    elif int_type == 'electrostatic_anion':
                        self.runJS(f'''anshape_{name}.addCylinder( {coord_1}, {coord_2}, [1, 0.08, 0.58], 0.06, "{id_1}:{id_2} {int_type}" );''')

            self.runJS(f'''var catShapeComp_{name} = stage.addComponentFromObject( catshape_{name} );
                            var anShapeComp_{name} = stage.addComponentFromObject( anshape_{name} );
                            var as_cat_{name} = catShapeComp_{name}.addRepresentation( "buffer", {{opacity: 0.6}} );
                            var as_an_{name} = anShapeComp_{name}.addRepresentation( "buffer", {{opacity: 0.6}} );
                            ''')
        
    def draw_interacting_residues(self):
        for unit in self.vis_res_chain_list:
            res_chain, parent, name, int_type = unit
            res, chain = res_chain.split(".")
            self.runJS(f"""load_{parent}.then(function (o) {{
                                    o.addRepresentation("licorice", {{
                                    multipleBond: true,
                                    name: "{res_chain+parent+name+int_type}",
                                    sele: ":{chain} and sidechainAttached and {res}"
                                    }});}})""")

    def load_deemian(self, deemian_data, dirname):
        self.runJS("stage.removeAllComponents();")
        self.vis_res_chain_list = []

        # attach deemian_data to self for case when other method require it too
        self.deemian_data = deemian_data
        self.molselection = deemian_data["deemian.json"]["selection"]
        self.int_subjects = deemian_data["deemian.json"]["measurement"]["interacting_subjects"]
        for _, selection in self.molselection.items():
            filename = selection["parent"]
            molname = filename.replace(".", "_")
            if molname not in self.mols:
                self.mols[molname] = filename
        
        for molname, filename in self.mols.items():
            if filename in deemian_data:
                content = deemian_data[filename]
            else:
                with open(dirname / filename) as f:
                    content = f.read()

            # load_ prefix allow variable started with numerical e.g. PDB ID
            self.runJS(f''' var pdbblob = new Blob([`{content}`], {{type: 'text/plain'}});
                            var load_{molname} = stage.loadFile(pdbblob,  {{ ext: "pdb", asTrajectory: true}});
                            ''')
        
        self.tree_pair_data = []
        self.selection_data = []
        self.build_basic_representation()
        self.draw_interaction_shape()
        self.draw_interacting_residues()
        self.setup_stage()
        self.populate_tree_pair()
        self.populate_tree_selection()
        self.runJS("if (document.getElementById('treeforceUpdate')) {document.getElementById('treeforceUpdate').click()}")

    def set_frame(self, num):
        conf = num - 1
        for molname, _ in self.mols.items():
            self.runJS(f'''load_{molname}.then(function (o) {{
                                traj_{molname}.trajectory.setFrame({conf});
                            }} ); ''')
        
        self.reset_interaction_shapes()
        self.reset_interacting_residues()

        self.draw_interaction_shape(conf_num=num)
        self.draw_interacting_residues()
        self.load_visibility_from_tree_pair()
    
    def reset_interacting_residues(self):
        for unit in self.vis_res_chain_list:
            res_chain, parent, name, int_type = unit
            self.runJS(f"stage.getRepresentationsByName('{res_chain+parent+name+int_type}').list[0].dispose();")

        self.vis_res_chain_list = []
    
    def reset_interaction_shapes(self):
        for int_subject in self.int_subjects:
            name = int_subject["name"].replace(":", "_")
            self.runJS(f'''  if (typeof catShapeComp_{name} !== 'undefined') {{
                                stage.removeComponent(catShapeComp_{name});
                            }};
                            if (typeof anShapeComp_{name} !== 'undefined') {{
                                stage.removeComponent(anShapeComp_{name});
                            }}; ''')

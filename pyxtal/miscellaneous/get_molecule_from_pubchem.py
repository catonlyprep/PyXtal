import pubchempy as pcp
import numpy as np
import json
from pyxtal.database.element import Element


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def read_molecule(mol, name):
    x = np.transpose([mol.record["coords"][0]["conformers"][0]["x"]])
    y = np.transpose([mol.record["coords"][0]["conformers"][0]["y"]])
    z = np.transpose([mol.record["coords"][0]["conformers"][0]["z"]])

    xyz = np.concatenate((x, y, z), axis=1)
    numbers = mol.record["atoms"]["element"]
    elements = [Element(i).short_name for i in numbers]
    volume = mol.volume_3d
    pubchemid = mol.cid
    molecule = {
        "name": name,
        "elements": elements,
        "xyz": xyz,
        "volume": volume,
        "pubchem id": pubchemid,
    }
    return molecule


names = [
    "H2O",
    "CH4",
    "NH3",
    "benzene",
    "naphthalene",
    "anthracene",
    "tetracene",
    "Pentacene",
    "coumarin",
    "resorcinol",
    "benzamide",
    "aspirin",
    "ddt",
    "lindane",
    "Glycine",
    "Glucose",
    "ROY",
]

molecules = []
molecule = {
    "name": "C60",
    "elements": ["C"] * 60,
    "xyz": np.array(
        [
            [2.2101953, 0.5866631, 2.6669504],
            [3.1076393, 0.1577008, 1.6300286],
            [1.3284430, -0.3158939, 3.2363232],
            [3.0908709, -1.1585005, 1.2014240],
            [3.1879245, -1.4574599, -0.1997005],
            [3.2214623, 1.2230966, 0.6739440],
            [3.3161210, 0.9351586, -0.6765151],
            [3.2984981, -0.4301142, -1.1204138],
            [-0.4480842, 1.3591484, 3.2081020],
            [0.4672056, 2.2949830, 2.6175264],
            [-0.0256575, 0.0764219, 3.5086259],
            [1.7727917, 1.9176584, 2.3529691],
            [2.3954623, 2.3095689, 1.1189539],
            [-0.2610195, 3.0820935, 1.6623117],
            [0.3407726, 3.4592388, 0.4745968],
            [1.6951171, 3.0692446, 0.1976623],
            [-2.1258394, -0.8458853, 2.6700963],
            [-2.5620990, 0.4855202, 2.3531715],
            [-0.8781521, -1.0461985, 3.2367302],
            [-1.7415096, 1.5679963, 2.6197333],
            [-1.6262468, 2.6357030, 1.6641811],
            [-3.2984810, 0.4301871, 1.1204208],
            [-3.1879469, 1.4573895, 0.1996030],
            [-2.3360261, 2.5813627, 0.4760912],
            [-0.5005210, -2.9797771, 1.7940308],
            [-1.7944338, -2.7729087, 1.2047891],
            [-0.0514245, -2.1328841, 2.7938830],
            [-2.5891471, -1.7225828, 1.6329715],
            [-3.3160705, -0.9350636, 0.6765268],
            [-1.6951919, -3.0692581, -0.1976564],
            [-2.3954901, -2.3096853, -1.1189862],
            [-3.2214182, -1.2231835, -0.6739581],
            [2.1758234, -2.0946263, 1.7922529],
            [1.7118619, -2.9749681, 0.7557198],
            [1.3130656, -1.6829416, 2.7943892],
            [0.3959024, -3.4051395, 0.7557638],
            [-0.3408219, -3.4591883, -0.4745610],
            [2.3360057, -2.5814499, -0.4761050],
            [1.6263757, -2.6357349, -1.6642309],
            [0.2611352, -3.0821271, -1.6622618],
            [-2.2100844, -0.5868636, -2.6670300],
            [-1.7726970, -1.9178969, -2.3530466],
            [-0.4670723, -2.2950509, -2.6175105],
            [-1.3283500, 0.3157683, -3.2362375],
            [-2.1759882, 2.0945383, -1.7923294],
            [-3.0909663, 1.1583472, -1.2015749],
            [-3.1076090, -0.1578453, -1.6301627],
            [-1.3131365, 1.6828292, -2.7943639],
            [0.5003224, 2.9799637, -1.7940203],
            [-0.3961148, 3.4052817, -0.7557272],
            [-1.7120629, 2.9749122, -0.7557988],
            [0.0512824, 2.1329478, -2.7937450],
            [2.1258630, 0.8460809, -2.6700534],
            [2.5891853, 1.7227742, -1.6329562],
            [1.7943010, 2.7730684, -1.2048262],
            [0.8781323, 1.0463514, -3.2365313],
            [0.4482452, -1.3591061, -3.2080510],
            [1.7416948, -1.5679557, -2.6197714],
            [2.5621724, -0.4853529, -2.3532026],
            [0.0257904, -0.0763567, -3.5084446],
        ]
    ),
    "volume": None,
    "pubchem id": 123591,
}

molecules.append(molecule)
for name in names:
    print(name)
    mol = pcp.get_compounds(name, "name", record_type="3d")[0]
    molecule = read_molecule(mol,name)
    molecules.append(molecule)

dicts = {"LEFCIK": 812440,
         "OFIXUX": 102393188,
        }
for key in dicts.keys():
    mol = pcp.get_compounds(dicts[key], "cid", record_type="3d")[0]
    molecule = read_molecule(mol,key)
    molecules.append(molecule)

#print(molecules)
dumped = json.dumps(molecules, cls=NumpyEncoder, indent=2)
with open("molecules.json", "w") as f:
    f.write(dumped)

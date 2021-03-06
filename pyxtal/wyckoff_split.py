import numpy as np
import pyxtal.symmetry as sym
from copy import deepcopy
from pymatgen.core.operations import SymmOp
from random import choice

class wyckoff_split:
    """
    Class for performing wyckoff split between two space groups.
    Essentially, this code is to look for the database from the
    internationally crystallographic table and find the group-subgroup
    relations

    Args:
        G: int (1-230), number of super space group
        w1: string ("4a") or integer (1)
    """


    def __init__(self, G=197, idx=None, wp1=[0, 1], group_type='t'):
        self.G = sym.Group(G)  # Group object
        if group_type == 't':
            self.wyc = self.G.get_max_t_subgroup()
        else:
            self.wyc = self.G.get_max_k_subgroup()
        id_lists = []
        for wp in wp1:
            if type(wp) == int:
                id_lists.append(wp)
            else:
                id_lists.append(sym.index_from_letter(wp[-1], self.G))
        self.wp1_indices = id_lists
        self.wp1_lists = [self.G[id] for id in id_lists] # a WP object

        # choose a random spliting option if idx is not specified
        if idx is None:
            ids = [id for id in range(len(self.wyc['subgroup']))]
            idx = choice(ids)
        #print(G, idx, len(self.wyc['subgroup']))
        H = self.wyc['subgroup'][idx]
        self.H = sym.Group(H)  # Group object

        self.parse_wp2(idx)

        if (self.G.lattice_type == self.H.lattice_type):
            self.valid_split = False
            for wps in self.wp2_lists:
                for wp in wps:
                    rotation = np.array(wp[0].as_dict()['matrix'])[:3,:3]
                    if np.linalg.matrix_rank(rotation) > 0:
                        self.valid_split = True
                        break
        else:
            self.valid_split = True

        #if self.valid_split:
        self.G1_orbits = []
        self.G2_orbits = []
        self.H_orbits = []
        for i, wp1 in enumerate(self.wp1_lists):
            self.H_orbits.append([wp2.ops for wp2 in self.wp2_lists[i]])
            if group_type == 't':
                G1_orbits, G2_orbits = self.split_t(wp1, self.wp2_lists[i])
            else:
                G1_orbits, G2_orbits = self.split_k(wp1, self.wp2_lists[i])
            self.G1_orbits.append(G1_orbits)
            self.G2_orbits.append(G2_orbits)


    def parse_wp2(self, idx):
        """
        query the wp2 and transformation matrix from the given {G, H, wp1}
        """
        #print("trans", idx)
        #print(self.wyc['transformation'])
        trans = self.wyc['transformation'][idx]
        subgroup_relations = self.wyc['relations'][idx]
        subgroup_relations = [ele for ele in reversed(subgroup_relations)] 

        self.R = np.zeros([4,4])
        self.R[:3,:3] += trans[:3,:3]
        self.R[3,3] = 1
        self.inv_R = np.linalg.inv(self.R)
        inv_t = np.dot(self.inv_R[:3,:3], trans[:,3].T)
        self.inv_R[:3,3] = -inv_t.T
        self.R[:3,3] = trans[:3,3]


        wp2_lists = []
        for wp1_index in self.wp1_indices:
            wp2_list = []
            for letter in subgroup_relations[wp1_index]:
                id = sym.index_from_letter(letter[-1], self.H)
                wp2_list.append(self.H[id])
            wp2_lists.append(wp2_list)
        self.wp2_lists = wp2_lists
        self.index=self.wyc['index'][idx]
        #import sys; sys.exit()
    
    def split_t(self, wp1, wp2_lists):
        """
        split the generators in w1 to different w2s
        """
        #print(wp1)
        # wyckoff objects
        wp1_generators_visited = []
        wp1_generators = [np.array(wp.as_dict()['matrix']) for wp in wp1]
        
        # convert them to numpy array
        for generator in wp1_generators:
            generator = np.array(generator)

        G1_orbits = []
        G2_orbits = []
        factor = max([1,np.linalg.det(self.R)])

        for wp2 in wp2_lists:
            #print(wp2)
            #import sys; sys.exit()
            # try all generators here
            for gen in wp1_generators:
                good_generator = False
                #QZ: temporary solution, Needs to be fixed later
                if gen[0,3] == 1/4 and gen[1,3] == 3/4:
                    gen[0,3] -=1
                trans_generator = np.matmul(self.inv_R, gen)
                #print(trans_generator)
                
                g1_orbits = []
                g2_orbits = []
                strs = []
                for i, wp in enumerate(wp2):
                    new_basis_orbit = np.matmul(wp.as_dict()['matrix'], trans_generator)
                    #print(wp.as_dict()['matrix'])
                    #print(new_basis_orbit)
                    #import sys; sys.exit()
                    old_basis_orbit = np.matmul(self.R, new_basis_orbit).round(3)
                    #old_basis_orbit[3,:] = [0, 0, 0, 1]
                    tmp = deepcopy(old_basis_orbit)
                    tmp[3,:] = [0, 0, 0, 1]
                    if i==0: 
                        #print("wp1", SymmOp(gen).as_xyz_string(), in_lists(tmp, wp1_generators_visited), in_lists(tmp, wp1_generators))
                        #print("sgb", SymmOp(new_basis_orbit).as_xyz_string())
                        #print("gb", SymmOp(tmp).as_xyz_string())
                        #for w in wp1_generators:
                        #    print(SymmOp(w).as_xyz_string())
                        if not in_lists(tmp, wp1_generators_visited) and in_lists(tmp, wp1_generators):
                        #if in_lists(tmp, wp1_generators):
                            good_generator = True
                            #print("good_gener")
                        else:
                            break
                    # to consider PBC
                    g1_orbits.append(old_basis_orbit)        
                    g2_orbits.append(new_basis_orbit)        
                #print(g1_orbits)
                if good_generator:
                    temp=[]
                    # remove duplicates due to peridoic boundary conditions
                    for gen in g1_orbits:
                        if not in_lists(gen, temp):
                            temp.append(gen)
                    if int(len(temp)*factor) >= len(wp2):           
                        wp1_generators_visited.extend(temp)
                        g1_orbits = [SymmOp(orbit) for orbit in g1_orbits]
                        g2_orbits = [SymmOp(orbit) for orbit in g2_orbits]
                        G1_orbits.append(g1_orbits)
                        G2_orbits.append(g2_orbits)
                        #print("adding unique generators", len(g1_orbits), len(wp2), int(len(temp)*factor))
                        break
            #print("EEEEEE", len(g1_orbits), len(wp2))
            self.check_orbits(g1_orbits, wp1, wp2, wp2_lists)

        return G1_orbits, G2_orbits
        
    def split_k(self, wp1, wp2_lists):
        """
        split the generators in w1 to different w2s
        """
        wp1_generators = [np.array(wp.as_dict()['matrix']) for wp in wp1]
    
    
        G1_orbits = []
        G2_orbits = []
#         factor = max([1, np.linalg.det(self.R)])
    
        all_g2_orbits = []
        translations = self.translation_generator()
        for translation in translations:
            for gen in wp1_generators:
                orbit=np.matmul(self.inv_R,gen)
                for i in range(3):
                    if orbit[i][3]>=0:
                        orbit[i][3]+=translation[i]
                        orbit[i][3]=orbit[i][3]%1
                    else:
                        orbit[i][3]-=translation[i]
                        orbit[i][3]=orbit[i][3]%-1
                all_g2_orbits.append(orbit)
                
        #########################################################################
        for i in range(len(wp2_lists)):
            final_G2=[]
            temp=np.array(deepcopy(all_g2_orbits))
            for j in range(len(temp)):
                temp[j][:3,3]=temp[j][:3,3]%1
            temp=temp.round(3).tolist()

            for orbit in temp:
                try_match=np.array([np.matmul(x.as_dict()['matrix'], orbit) for x in wp2_lists[i]]) 
                for j in range(len(try_match)):
                    try_match[j][:3,3]=try_match[j][:3,3]%1

                try_match=try_match.round(3).tolist()
                
                try:
                    corresponding_positions=[temp.index(x) for x in try_match]
                except:
                    continue
                for index in sorted(corresponding_positions,reverse=True):
                    final_G2.append(all_g2_orbits[index])
                    del all_g2_orbits[index]
                G2_orbits.append(final_G2)
                break

        
        for position in G2_orbits:
            final_G1=[]
            for orbit in position:
                final_G1.append(SymmOp(np.matmul(self.R,orbit).round(3)))
            G1_orbits.append(final_G1)
        

        for i, position in enumerate(G2_orbits):
            for j, orbit in enumerate(position):
                G2_orbits[i][j]=SymmOp(orbit)
        
        return G1_orbits, G2_orbits
        


    def translation_generator(self):
        """
        a function to handle the translation during lattice transformation
        """
        modulo=round(np.linalg.det(self.R[:3,:3]))
        inv_rotation=np.array(self.inv_R[:3,:3])*modulo
        subgroup_basis_vectors=(np.round(inv_rotation.transpose()).astype(int)%modulo).tolist()
    
        # remove the [0,0,0] vectors
        translations=[x for x in subgroup_basis_vectors if x!=[0,0,0]]
    
        #find the independent vectors
        if len(translations)==0:
            independent_vectors=[[0,0,0]]
        elif len(translations)==1:
            independent_vectors=translations
        elif len(translations)==2:
            norm=round(np.linalg.norm(translations[0])*np.linalg.norm(translations[1]))
            inner_product=np.inner(translations[0],translations[1])
            difference=norm-inner_product
            if difference==0.:
                independent_vectors=[translations[0]]
            else:
                independent_vectors=translations
        else:
            norms=np.round([np.linalg.norm(translations[i])*np.linalg.norm(translations[j]) for i in range(2) for j in range(i+1,3)])
            inner_products=np.array([np.inner(translations[i],translations[j]) for i in range(2) for j in range(i+1,3)])
            differences=inner_products-norms
            independent_vectors=[translations[0]]
            if differences[0]!=0. and differences[1]==0.:
                independent_vectors.append(translations[1])
            elif differences[0]==0. and differences[1]!=0.:
                independent_vectors.append(translations[2])
            elif differences[0]!=0. and differences[1]!=0. and differences[2]!=0.:
                independent_vectors.append(translations[1])
                independent_vectors.append(translations[2])
            elif differences[0]!=0. and differences[1]!=0. and differences[2]==0.:
                independent_vectors.append(translations[1])
    
        #generate all possible combinations of the independent vectors
        l=len(independent_vectors)
        independent_vectors=np.array(independent_vectors)
        possible_combos=[]
        final_translation_list=[]
    
        for i in range(self.index**l):
            possible_combos.append(np.base_repr(i,self.index,padding=l)[-l:])
        for combo in possible_combos:
            combo=np.array([int(x) for x in combo])
            vector=np.array([0.,0.,0.])
            for i,scalar in enumerate(combo):
                vector+=scalar*independent_vectors[i]
            vector=(vector%modulo/modulo).tolist()
            if vector not in final_translation_list:
                final_translation_list.append(vector)
                
        return final_translation_list

    def check_orbits(self, g1_orbits, wp1, wp2, wp2_lists):
        if len(g1_orbits) < len(wp2):
            s1 = str(wp1.multiplicity)+wp1.letter
            s2 = ""
            for wp2 in wp2_lists:
                s2 += str(wp2.multiplicity)+wp2.letter
                s2 += ', '
            g, h = self.G.number, self.H.number
            print("Error between {:d}[{:s}] -> {:d}[{:s}]".format(g, s1, h, s2))
            print(self.R)
            print(g1_orbits)
            raise ValueError("Cannot find the generator for wp2")


    def __str__(self):
        s = "Wycokff split from {:d} to {:d}\n".format(self.G.number, self.H.number)
        for i, wp1 in enumerate(self.wp1_lists):
            s += "Origin: {:d}{:s}\n".format(wp1.multiplicity, wp1.letter)
            s += "After spliting\n"
        
            for j, wp2 in enumerate(self.wp2_lists[i]):
                s += "{:d}{:s}\n".format(wp2.multiplicity, wp2.letter)
                g1s, g2s, Hs = self.G1_orbits[i][j], self.G2_orbits[i][j], self.H_orbits[i][j]
                for g1_orbit, g2_orbit, h_orbit in zip(g1s, g2s, Hs):
                    s += "{:30s} -> {:30s} -> {:30s}\n".format(g1_orbit.as_xyz_string(), \
                                                               g2_orbit.as_xyz_string(), \
                                                               h_orbit.as_xyz_string())
        return s
        
    def __repr__(self):
        return str(self)




def in_lists(mat1, mat2, eps=1e-4, PBC=True):
    if len(mat2) == 0:
        return False
    else:
        for mat in mat2:
            if np.array_equal(mat[:3,:3], mat1[:3,:3]):
                diffs = np.abs(mat[:3,3] - mat1[:3,3])
                if PBC:
                    diffs -= np.floor(diffs)
                #print("diffs", diffs)
                if (diffs*diffs).sum() < 1e-2:
                    return True
        return False

        
if __name__ == "__main__":
    sites = ['8c']
    sp = wyckoff_split(G=79, wp1=sites, idx=0, group_type='t'); print(sp)
    sp = wyckoff_split(G=79, wp1=sites, idx=0, group_type='k'); print(sp)
    sp = wyckoff_split(G=79, wp1=sites, idx=1, group_type='k'); print(sp)
    sp = wyckoff_split(G=79, wp1=sites, idx=2, group_type='k'); print(sp)
    sp = wyckoff_split(G=79, wp1=sites, idx=3, group_type='k'); print(sp)
    sp = wyckoff_split(G=79, wp1=sites, idx=4, group_type='k'); print(sp)

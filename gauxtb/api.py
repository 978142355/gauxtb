import os
import sys
import re
import numpy as np
from ase.units import *
from ase import Atoms, io

class GauXTB:
    def __init__(self, xtb_exe: str = 'xtb', name: str = '', kw: str = ''):
        self.xtb_exe = xtb_exe
        self.name, _ = os.path.splitext(name)
        self.kw = kw
        self.inputs = {}
        self.outputs = {}

    def read_ein(self):
        name = '.'.join([self.name, 'EIn'])
        lines = None
        with open(name) as fd:
            lines = fd.read().splitlines()
        os.remove(name)
        natoms, nderiv, charge, mult = np.array(lines[0].split(), int)
        xyz_text = np.array([line.split() for line in lines[1:natoms+1]])
        numbers = np.array(xyz_text[:, 0], int)
        positions = np.array(xyz_text[:, 1:4], float)*Bohr
        atoms = Atoms(numbers=numbers, positions=positions)
        self.inputs['charge'] = int(charge)
        self.inputs['spin'] = int(mult-1)
        self.inputs['atoms'] = atoms
        self.inputs['nderiv'] = int(nderiv)

    def exec_xtb(self, nderiv: int, restart: bool = False):
        deriv = ['--sp', '--grad', '--hess']
        xtb_cmd = ['%s gau_xtb.xyz' % self.xtb_exe]
        xtb_cmd.append('--chrg %d' % self.inputs['charge'])
        xtb_cmd.append('--uhf %d' % self.inputs['spin'])
        xtb_cmd.append(deriv[nderiv])
        if restart:
            xtb_cmd.append('--restart')
        else:
            xtb_cmd.append('--norestart')
        if len(self.kw) > 0:
            xtb_cmd.append(self.kw)
        xtb_cmd.append('>> xtb_std.out')
        xtb_cmd = ' '.join(xtb_cmd)
        os.system(xtb_cmd)

    def read_xtb(self, nderiv: int):
        natoms = len(self.inputs['atoms'])
        pattern = r'\$\w+\s*(.*\d+\n)'
        if nderiv == 0:
            with open('energy') as fd:
                text = fd.read()
                text = re.findall(pattern, text, re.S)[0]
                energy = float(text.split()[1])
                self.inputs['energy'] = energy
        elif nderiv == 1:
            with open('gradient') as fd:
                text = fd.read()
                text = re.findall(pattern, text, re.S)[0]
                text = text.splitlines()[natoms+1:]
                forces = np.array(' '.join(text).split(), dtype=float)
                forces = forces.reshape(natoms, 3)
                self.inputs['forces'] = forces
        elif nderiv == 2:
            with open('hessian') as fd:
                text = fd.read()
                text = re.findall(pattern, text, re.S)[0]
                hessian = np.array(text.split(), dtype=float)
                hessian = hessian.reshape(3*natoms, 3*natoms)
                self.inputs['hessian'] = hessian

    def write_eou(self, nderiv: int):
        natoms = len(self.inputs['atoms'])
        if nderiv == 0:
            pattern = ''.join(['%20.12E']*4)
            dipole = np.zeros(3)
            dipole = np.insert(dipole, 0, self.inputs['energy'])
            energy = pattern % tuple(dipole)
            self.outputs[0] = energy
        elif nderiv == 1:
            pattern = ''.join(['%20.12E']*3)
            forces = self.inputs['forces']
            forces = [pattern % tuple(force) for force in forces]
            forces = '\n'.join(forces)
            self.outputs[1] = forces
        elif nderiv == 2:
            pattern = ''.join(['%20.12E']*3)
            hessian = self.inputs['hessian']
            """
            hessian = hessian.reshape(3*natoms*natoms, 3)
            hessian = [pattern % tuple(h) for h in hessian]
            """
            index = np.tril_indices_from(hessian)
            hessian = hessian[index]
            hessian = hessian.reshape(natoms*(3*natoms+1)//2, 3)
            hessian = np.vstack([np.zeros([3*natoms+2, 3]), hessian])
            hessian = [pattern % tuple(h) for h in hessian]
            hessian = '\n'.join(hessian)
            self.outputs[2] = hessian

    def run(self):
        self.read_ein()
        io.write('gau_xtb.xyz', self.inputs['atoms'])
        nderiv = self.inputs['nderiv']
        if nderiv == 0:
            self.exec_xtb(1)
            self.read_xtb(0)
            self.write_eou(0)
        elif nderiv == 1:
            self.exec_xtb(1)
            for i in range(2):
                self.read_xtb(i)
                self.write_eou(i)
        elif nderiv == 2:
            self.exec_xtb(1)
            self.exec_xtb(2, restart=True)
            for i in range(3):
                self.read_xtb(i)
                self.write_eou(i)
        text = [self.outputs[i] for i in range(nderiv+1)]
        text = '\n'.join(text)
        name = '.'.join([self.name, 'EOu'])
        with open(name, 'w+') as fd:
            fd.write(text)


if __name__ == '__main__':
    gauxtb = GauXTB(name=sys.argv[2])
    gauxtb.run()

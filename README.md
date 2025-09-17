# gauxtb
A Gaussian-xtb interface for efficient pre-optimization and transition state searches
````markdown
# gauxtb

**gauxtb** is a Python-based tool that couples the **Gaussian** quantum chemistry package with the **xtb** program.  
It leverages the speed of xtb and the stability of Gaussian for force and frequency calculations, enabling rapid acquisition of reasonable initial structures and transition states.  
This helps reduce the computational cost compared to relying solely on traditional quantum chemistry software.

---

## Key Features
- **Hybrid Workflow**: Combine Gaussian’s robust force/frequency calculations with xtb’s efficient electronic-structure evaluation.
- **Cross-Platform**: Works on macOS, Linux, and Windows with identical commands.
- **Pre-Optimization**: Quickly obtain geometries and transition states for further high-accuracy calculations using Gaussian, ORCA, PySCF, etc.

---

## Installation
```bash
git clone [[website ](https://github.com/978142355/gauxtb)](https://github.com/978142355/gauxtb)
````

Requirements:

* Python 3.9 or higher
* Gaussian 09/16 (properly configured in your environment)
* xtb 6.7.1 or newer (configured in your environment)

---

## Usage Example

1. **Prepare Gaussian Input**
   Example `gjf` file snippet:

   ```gjf
   %chk=TS.chk
   %nproc=1
   #p opt(ts,calcfc,noeigen,nomicro) freq external='python3 runxtb.py'

   Title Card

   0 1
   ...
   ```

2. **Create `runxtb.py`**

   ```python
   from gauxtb.api import GauXTB
   import sys

   gauxtb = GauXTB(name=sys.argv[2])
   gauxtb.run()
   ```

3. **Run Calculation**

   ```bash
   g16 TS.gjf
   ```

---

## Example Application

* Transition-state search for cyclopropyl carbene isomerization
* Supports geometry optimization, gradient, and Hessian calculations via xtb within Gaussian

---

## Citation

If you use **gauxtb** in your research, please cite:

> **gauxtb** – A Gaussian-xtb interface for efficient pre-optimization and transition state searches.
> Authors: **Jian Zhao** (Liaoning Normal University, [zhaoj2333@lnnu.edu.cn](mailto:zhaoj2333@lnnu.edu.cn)) and **Dong Yang**.

---




# Ok-k-mer manuscript experiments

This repository contains the experiment workflows, legacy analysis code,
notebooks, and local results for the Ok-k-mer manuscript. 
The `okkmer` command-line package and documentation is found at this [repo](https://github.com/StephenHwang/Ok-k-mer).


## Installation
Ok-*k*-mer can be installed using pip locally. We recommend using a new conda or virtual environment for this.

Ok-*k*-mer requires Python ≥ 3.10 and [Dashing2 **v2.1.21**](https://github.com/dnbaker/dashing2/releases/tag/v2.1.21).
Dashing2 is a separate executable dependency for computing the *k*-mer Jaccard distances required by Ok-*k*-mer. 
Distance matrices computed by other tools can be imported and used by Ok-*k*-mer. 

```bash
git clone https://github.com/StephenHwang/Ok-k-mer.git
python -m pip install .
dashing2 --help
okkmer help
```


## Getting help
If you run into any issues or have any questions, reach out either through:

1. GitHub Issues
2. shwang45 [at] jhu.edu


## License
Ok-*k*-mer is licensed under the GNU General Public License version 3.  
See [LICENSE](LICENSE) for the full terms.

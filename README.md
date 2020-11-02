# Installation
### Setting Up the Environment (Preinstallation)
**For Linux Users**
For the optimal performance on Intel-based architectures, installing [Intel Math Kernel Library (MKL)](https://software.intel.com/content/www/us/en/develop/articles/intel-math-kernel-library-intel-mkl-2020-install-guide.html) is **highly** recommended. After installing, make sure `MKLROOT` is defined by running the [setvars](https://software.intel.com/content/www/us/en/develop/documentation/using-configuration-file-for-setvars-sh/top.html) script.

**Install library dependencies**
To install the `ACTIONet` dependencie on debian-based linux machines, run:

```bash
sudo apt-get install libhdf5-dev libsuitesparse-dev
```

For Mac-based systems, you can use [brew](https://brew.sh/) instead:

```bash
brew install hdf5 suite-sparse
```

### Installing ACTIONet Python Package
Use `pip` to install ACTIONet directly from this repository:
```bash
pip install git+https://github.com/shmohammadi86/ACTIONet@python-devel
```

# Running ACTIONet
**Note** If you are using `MKL`, make sure to properly [set the number of threads](https://software.intel.com/content/www/us/en/develop/documentation/mkl-macos-developer-guide/top/managing-performance-and-memory/improving-performance-with-threading/techniques-to-set-the-number-of-threads.html) used prior to running `ACTIONet`.

## Example Run
Here is a simple example to get you started:

```python
from urllib.request import urlretrieve

import ACTIONet as an
import scanpy as sc

# Download example dataset from the 10X Genomics website
urlretrieve('http://cf.10xgenomics.com/samples/cell-exp/3.0.0/pbmc_10k_v3/pbmc_10k_v3_filtered_feature_bc_matrix.h5', 'pbmc_10k_v3.h5')

# Read and filter the data
adata = sc.read_10x_h5('pbmc_10k_v3.h5')
an.pp.filter_adata(adata, min_cells_per_feature=0.01, min_features_per_cell=1000)

# Run ACTIONet
an.pp.reduce_kernel(adata)
an.run_ACTIONet(adata)

# Export results
adata.write('pbmc_10k_v3.h5ad')
```
## Visualizing results using cellxgene

The output of ACTIONet in the python implementation is internally stored as as `AnnData` object, and R `ACE` objects can be imported from/exported to `AnnData` using functions `AnnData2ACE()` and `ACE2AnnData()` functions, respectively. `AnnData` objects can be directly loaded into [cellxgene](https://github.com/chanzuckerberg/cellxgene) package, an open-source viewer for interactive single-cell data visualization. `cellxgene` can be installed as:

```bash
pip install cellxgene

```

Then to visualize the results of ACTIONet, run:
```bash
cellxgene launch pbmc_10k_v3.h5ad
```

where *pbmc_10k_v3.h5ad* is the name of the file we exported using `adata.write()` function.


# Additional tutorials
You can access ACTIONet tutorials from:
1. [ACTIONet framework at a glance (human PBMC 3k dataset)](http://compbio.mit.edu/ACTIONet/tutorials/mini_intro.html)
2. [Introduction to the ACTIONet framework (human PBMC Granja et al. dataset)](http://compbio.mit.edu/ACTIONet/tutorials/intro.html)
3. [Introduction to cluster-centric analysis using the ACTIONet framework](http://compbio.mit.edu/ACTIONet/tutorials/clustering.html)
4. [To batch correct or not to batch correct, that is the question!](http://compbio.mit.edu/ACTIONet/tutorials/batch.html)
5. [PortingData: Import/export options in the ACTIONet framework](http://compbio.mit.edu/ACTIONet/tutorials/porting_data.html)
6. [Interactive visualization, annotation, and exploration](http://compbio.mit.edu/ACTIONet/tutorials/annotation.html)
7. [Constructing cell-type/cell-state-specific networks using SCINET](http://compbio.mit.edu/ACTIONet/tutorials/scinet.html)

You can also find a [step-by-step guide](http://compbio.mit.edu/ACTIONet/tutorials/guide.html) to learning the core functionalities of the ACTIONet framework.

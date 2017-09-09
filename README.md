tohu: Create random data in a controllable way
==============================================


Quick start
-----------

(i) Create a new conda environment called `tohu` containing all necessary prerequisites.

Note: If a conda environment with this name already exists it will update the packages and even the Python version in it, so make sure this is ok before you run this command.

```
$ make update-conda-environment
```

(ii) Activate the new conda environment:

```
$ source activate tohu
```

(iii) Install tohu into new conda environment:

```
$ pip install .
```

(iv) Run the test suite to make sure everything works correctly:

```
$ make test
```


Prerequisites:
--------------

- `conda`

Use [miniconda](http://conda.pydata.org/miniconda.html) if you want a small
installation which just provides the `conda` command. Alternatively, you can
install the full [Anaconda distribution](https://www.continuum.io/downloads)
which comes pre-packaged with lots of Python modules useful for data analysis
and scientific computing.


Copyright:
----------

See [LICENSE](./LICENSE)

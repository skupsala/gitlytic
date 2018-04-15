# Gitlytic

This is my personal project for learning basic data science tools and skills.
Project holds very basic descriptive statistics and visualizations for git repo commits.

## Setting up environment and analysing projects

1. Create and activate virtualenv for gitlytic
```bash
# Create virtualenv
virtualenv -p python3 gl
# Activate virtualenv
source gl/bin/activate
```
2. Upgrade pip and install dependencies
```bash
# Upgrade pip
pip install --upgrade pip
# Install dependencies
pip install -r requirements.txt
```

3. Install cloc for snapshot analysis
```bash
# This works on Debian / Ubuntu
# For other operation systems, see http://cloc.sourceforge.net/
sudo apt-get install cloc
```

4. Create project and analyse it
```bash
# Create project with some repos
python -m gitlytic.cli.create_project --project datascience --git-repo-urls https://github.com/numpy/numpy.git https://github.com/pandas-dev/pandas.git https://github.com/scipy/scipy.git https://github.com/scikit-learn/scikit-learn.git https://github.com/matplotlib/matplotlib.git https://github.com/mwaskom/seaborn.git https://github.com/jupyter/notebook.git
# Analyse project
python -m gitlytic.cli.analyse --project datascience
```

5. Start jupyter notebook
```bash
jupyter notebook
```

6. Open notebook gitlytic -> notebooks -> project-overview.ipynb and run it


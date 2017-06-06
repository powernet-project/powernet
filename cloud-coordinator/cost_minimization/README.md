# Setup to run this algorithm locally follows

## If you don't want to use virtualenv you can skip to step 3

### 1 - Install virtualenv
```
sudo pip install virtualenv 
```

### 2 - Init the venv
``` 
use venv_* as a venv folder name - this pattern is gitignored
virtualenv 'foldername'
source 'foldername'/bin/activate
```

### 3 - Install the requirements
``` 
pip install -r requirements.txt 
```

### 3.1 - You may need to install the dependencies individually if there are conflicts

### 3.2 - After the install of matplotlib, depending on your setup, you'll need to do the following
```
cd ~/.matplotlib
touch matplotlibrc
```
#### add the following line to the file created above
```
backend: TkAgg
```

### 3.3 - Manually install MOSEK - sans AnaConda - this step is Optional
```
sudo pip install --user git+http://github.com/MOSEK/Mosek.pip
```
#### if using venv
```
sudo pip install git+http://github.com/MOSEK/Mosek.pip
```

### 3.3.1 - Add the mosek license file to the correct location
```
cd ~/
mkdir mosek (if it doesn't exist)
```
#### navigate back to the project dir
```
cp mosek.lic ~/mosek/
```

### 4 - Finally, run the project
``` 
python LoadData.py
```
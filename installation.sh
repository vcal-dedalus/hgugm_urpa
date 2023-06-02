#ensure gcc is ready for pip-install queueing-tool[plotting]
sudo apt-get install gcc
#ensure graphviz is available before pip-install pygraphviz
sudo apt install graphviz graphviz-dev

#create conda env.
conda create -n urpa python==3.9
conda activate urpa

#install scipy, desirable for queueing-tool.
pip install scipy
pip install pygraphviz
pip install queueing-tool[plotting]

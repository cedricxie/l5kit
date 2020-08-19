# Setup inside the Docker Environment

## Install Python 3.6
```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.6 python3.6-dev
```

## Install PIP
```
curl https://bootstrap.pypa.io/get-pip.py | sudo -H python3.6
```

## Install Requirements
```
cd ~/shared_dir/l5kit/l5kit
sudo -H pip3 install -r requirements.txt
#sudo python3.6 -m pip install setuptools
```

## Check Torch Version and GPU.
```
python3.6
import torch
torch.cuda.is_available()
```

## Run Jupyter Notebook
```
jupyter notebook --ip 192.168.0.12 --port=8888 examples/visualisation/visualise_data.ipynb
jupyter notebook --ip 192.168.0.12 --port=8889 examples/agent_motion_prediction/agent_motion_prediction.ipynb
```
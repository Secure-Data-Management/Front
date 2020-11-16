# Client application for mPeck Scheme

## Installation

Pre requisite: Linux system (can be also wsl, wsl2, docker)

You first need to install pypbc for that you need to follow those instruction:
```shell script
sudo su <<ROOT
sudo apt-get update
sudo apt-get install -yqq --no-install-recommends libgmp-dev curl git wget build-essential flex bison python3 python3-pip python3-dev
wget https://crypto.stanford.edu/pbc/files/pbc-0.5.14.tar.gz
tar -xvf pbc-0.5.14.tar.gz
cd pbc-0.5.14
sudo ./configure --prefix=/usr --enable-shared
make -j 4
sudo make install
sudo ldconfig
cd ..
git clone https://github.com/debatem1/pypbc
cd pypbc
(echo "#define PY_SSIZE_T_CLEAN" && cat pypbc.h) > pypbc.h.temp && mv pypbc.h.temp pypbc.h
pip3 install --upgrade setuptools wheel
pip3 install .
cd ..
rm -r pypbc pbc-0.5.14 pbc-0.5.14.tar.gz
ROOT
```

Once this is done the last line should be `Successfully installed pypbc-0.2`

If it is not make sure that you have indeed installed the required libraries without error, that you are using a recent linux version and 
that no file were conflicting with your installation process (you might want to do it line by line then)

Then you need to run `sudo pip3 install -r requirements.txt` to install the python packages needed.

Finally you need to run `python3 manage.py migrate` to make all the migrations before starting anything

# Running

You can simply type `python3 manage.py runserver 127.0.0.1:15000`

You can now open your browser at: [http://127.0.0.1:15000](127.0.0.1:15000)

You need to add a server address at the beginning, so you might want to start it also.

Once the server address has been entered you can generate your key pairs.

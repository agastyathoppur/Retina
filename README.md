The following commands must be run for this application to work-

sudo apt install pip
sudo apt install pip3
pip3 install scipy
pip3 install imutils
pip3 install argparse
pip3 install datetime
pip3 install cmake
sudo apt-get install build-essential cmake pkg-config
sudo apt-get install libx11-dev libatlas-base-dev
sudo apt-get install libgtk-3-dev libboost-python-dev
pip install dlib
pip install opencv-python
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list
sudo apt-get update
sudo apt-get install -y mongodb-org
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-database hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections
sudo systemctl start mongod
sudo systemctl enable mongod

Make sure the folder that has been extracted from the cloned github repository is named "Retina", and is placed in the Desktop directory. (Note- this application only works on machines with the linux operating system)

The blink.sh shell script file must be moved to /etc/profile.d using the following command-

sudo mv blink.sh /etc/profile.d

The user can decide how often the program starts by changing the resttime variable in the blink_detection.py file. The minimum value of this variable is 10 and the maximum value is 99.

Log out and log back into your linux profile or restart your computer to start running the program. 



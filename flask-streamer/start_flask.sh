echo export LC_ALL=C.UTF-8 >> ~/.bashrc
echo export LANG=C.UTF-8 >> ~/.bashrc

source ~/.bashrc

python3 -m flask run --host=0.0.0.0
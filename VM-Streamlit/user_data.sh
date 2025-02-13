#!/bin/bash

apt-get update && apt upgrade -y
apt-get install -y python3-pip git


git clone https://github.com/julessa/Groupe1_DataBI_Ftech.git
cd Groupe1_DataBI_Ftech
pip install streamlit pandas numpy matplotlib seaborn plotly prophet

#pip install -r requirements.txt

nohup streamlit run Streamlit.py --server.enableCORS false --server.address=0.0.0.0 > streamlit.log 2>&1 &

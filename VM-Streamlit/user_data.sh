sudo -i
apt-get update && apt upgrade -y
apt-get install -y python3-pip git

pip install streamlit
git clone https://github.com/julessa/Groupe1_DataBI_Ftech.git
cd Groupe1_DataBI_Ftech
pip install -r requirements.txt

nohup streamlit run helloworld.py --server.enableCORS false > streamlit.log 2>&1 &
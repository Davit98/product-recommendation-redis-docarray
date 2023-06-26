docker run -d --name redis-stack -p 6379:6379 redis/redis-stack-server:latest
pip install -r requirements.txt
jina auth login
streamlit run main.py
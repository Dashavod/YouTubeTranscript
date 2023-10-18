mkdir -p ~/.streamlit/
echo "[general]
email = \"dvodolazska@gmail.com\"
" > ~/.streamlit/credentials.toml
echo "[server]
headless = true
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
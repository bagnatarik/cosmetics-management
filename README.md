Before launching the app, you must install requirements
```shell
pip install -r requirements.txt
```
And then change do this:
```shell
mkdir .streamlit
touch .streamlit/secrets.toml
```
And inside `secrets.toml` you must add:
```text
[db]
dsn = "your_dsn"
user = "your_username"
password = "your_password"
```

And then:
```shell
python -m streamlit app/Home.py
```

Here is the link:
[cosmetics-streamlit](https://cosmetics-management.streamlit.app)
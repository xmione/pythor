from invoke import task

@task
def savereqts(c):
    c.run("pip freeze > requirements.txt")

@task
def hflogin(c):
    c.run("huggingface-cli login")

@task
def hfwhoami(c):
    c.run("huggingface-cli whoami")

@task
def fixtokenizer(c):
    c.run("python fix_tokenizer.py")

@task
def app(c):
    c.run("python app.py")

@task
def train(c):
    c.run("python train_model.py")

@task
def traincodet5(c):
    c.run("python train_codet5.py")

@task
def convertgpt2(c):
    c.run("python -m nbconvert --to script train_gpt2_colab.ipynb")

@task
def convertcodet5(c):
    c.run("python -m nbconvert --to script CodeT5.ipynb")

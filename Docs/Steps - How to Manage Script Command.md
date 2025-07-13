# Steps - How to Manage Script Command

## 🔧 How to Set It Up

### 1. Install invoke

```bash
pip install invoke
```

### 2. Create a tasks.py file
#### Example:

```python
from invoke import task

@task
def run(c):
    c.run("python main.py")

@task
def train(c):
    c.run("python train_model.py")

@task
def convert(c):
    c.run("python -m nbconvert --to script train_gpt2_colab.ipynb")

```

### 3. Run tasks like this
```bash
invoke run
invoke train
invoke convert
```

#### You can think of tasks.py like Python’s version of package.json scripts.

## 🧠 Bonus: Aliases and Parameters
### You can even make commands shorter or pass arguments:

```python
@task(name="t")
def train_model(c, dataset="data.csv"):
    c.run(f"python train_model.py --data {dataset}")

```
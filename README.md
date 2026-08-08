# [Kaggriculture](https://www.kaggle.com/competitions/kaggriculture)
## GitHub Workflow 
### You can't push to `main`!
Therefore, create your own branch or push to existing branch.
Then, go to [`GitHub web-app`](https://github.com/bravefe/Kaggriculture/pulls) to create pull request.
### Use [`issues`](https://github.com/bravefe/Kaggriculture/issues) as to-do list.
After you create the issue it will apear in the `project board`.
### Also, [`project board`](https://github.com/users/bravefe/projects/5/views/1) exist.
You just need to be a colaborator to edit it.
## Virtual Environment
Plese use python **3.11** if not 3.12.

Create venv
```bash
python3.11 -m venv .venv
```
activate the venv
```bash
.venv\Scripts\activate
```
Then, run this to install all the lib.
```bash
pip install -r requirements.txt
```
## Code
[`kaggriculture/code`](https://www.kaggle.com/competitions/kaggriculture/code) for more code
### Basic

[Start HERE](kaggriculture-getting-started.ipynb) 
*kaggriculture-getting-started.ipynb*
by Bovard Doerschuk-Tiberi


### More Game Rules and Env Visualization 
[HERE](kaggriculture-visualized-what-every-crop-pays.ipynb)
*kaggriculture-visualized-what-every-crop-pays.ipynb*
by Georgy Mamarin

# Action format

The bot must return an **action dictionary** on every step.

```python
actions = {
    "farmer": [],
    "hands": [],
    "market": []
}
```

The dictionary contains actions for the **farmer**, any **hired hands**, and **market transactions**.

## Action dictionary

| Key      | Description                                 |
| -------- | ------------------------------------------- |
| `farmer` | A single action performed by the farmer     |
| `hands`  | A list of actions, one for each hired hand  |
| `market` | A list of market actions executed this turn |

### Farmer and hand actions

The farmer and hired hands can perform the following actions.

#### Movement

```python
["MOVE", "NORTH"]
["MOVE", "SOUTH"]
["MOVE", "EAST"]
["MOVE", "WEST"]
```

#### Farming

```python
["PLANT", crop]
["WATER"]
["HARVEST"]
["DIG"]
```

#### Buildings and collection

```python
["BUILD_PASTURE"]
["COLLECT"]
```

#### No action

```python
["PASS"]
```

### Market actions

The market accepts a list of transactions that will be executed during the turn.

#### Hire workers

```python
["HIRE"]
```

#### Expand land

```python
["BUY_LAND"]
```

#### Buy seeds

```python
["BUY_SEED", crop, quantity]
```

#### Buy animals

```python
["BUY_ANIMAL", animal, quantity]
```

#### Buy fertilizer

```python
["BUY_FERTILIZER", quantity]
```

#### Sell items

```python
["SELL", item, quantity]
```

### Example

```python
actions = {
    "farmer": ["MOVE", "EAST"],
    "hands": [
        ["WATER"],
        ["HARVEST"]
    ],
    "market": [
        ["BUY_SEED", "CARROT", 10],
        ["SELL", "CARROT", 5]
    ]
}
```

This performs one farmer action, two hired-hand actions, and two market transactions in the same turn.



## Submission
[submission_example.py](submission/submission_example.py) 
You can submit as `.py`

[submission_example_zip](submission/submission_example_zip/main.py)
or you can also submit as `.zip` to include more file, but you do need to include `main.py` in it.

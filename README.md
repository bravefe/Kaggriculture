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

สร้าง venv
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


### More Explanation and Env Visualization 
[HERE](kaggriculture-visualized-what-every-crop-pays.ipynb)
*kaggriculture-visualized-what-every-crop-pays.ipynb*
by Georgy Mamarin

## Action

The bot returns an action dictionary each step:

```python
actions = {
    "farmer": [],
    "hands": [],
    "market": []
}
```

### Farmer / Hand Actions

* `["PASS"]`
* `["MOVE", "NORTH"]`
* `["MOVE", "SOUTH"]`
* `["MOVE", "EAST"]`
* `["MOVE", "WEST"]`
* `["PLANT", crop]`
* `["WATER"]`
* `["HARVEST"]`
* `["DIG"]`
* `["BUILD_PASTURE"]`
* `["COLLECT"]`

### Market Actions

* `["HIRE"]`
* `["BUY_LAND"]`  
* `["BUY_SEED", crop, quantity]`
* `["BUY_ANIMAL", animal, quantity]`
* `["BUY_FERTILIZER", quantity]`
* `["SELL", item, quantity]`



## Submission
[submission_example.py](submission_example.py) 
You can submit as `.py`

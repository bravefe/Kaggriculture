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

## Action format

Each turn returns a dictionary with up to three sections:

```python
{
    "farmer": ["PASS"],
    "hands": [],
    "market": []
}
```

### Structure

* `farmer`: a single action performed by the farmer.
* `hands`: a list of actions, one for each hired hand.
* `market`: a list of market transactions performed this turn.

### Farmer and hand operations

These operations can be used by both the farmer and any hired hand.

| Operation          | Format                   | Description                     |
| ------------------ | ------------------------ | ------------------------------- |
| Move north         | `["NORTH"]`              | Move one tile north             |
| Move south         | `["SOUTH"]`              | Move one tile south             |
| Move east          | `["EAST"]`               | Move one tile east              |
| Move west          | `["WEST"]`               | Move one tile west              |
| Pass               | `["PASS"]`               | Do nothing                      |
| Pick up item       | `["PICKUP", item]`       | Pick up one unit of an item     |
| Pick up multiple   | `["PICKUP", item, n]`    | Pick up `n` units               |
| Plant crop         | `["PLANT", crop]`        | Plant a crop seed               |
| Water              | `["WATER"]`              | Water the current tile          |
| Harvest            | `["HARVEST"]`            | Harvest a mature crop           |
| Fertilize          | `["FERTILIZE"]`          | Fertilize the current tile      |
| Build coop         | `["BUILD_COOP"]`         | Construct a coop                |
| Build pasture      | `["BUILD_PASTURE"]`      | Construct a pasture             |
| Dig                | `["DIG"]`                | Dig the current tile            |
| Place item         | `["PLACE", item]`        | Place one unit of an item       |
| Place multiple     | `["PLACE", item, n]`     | Place `n` units                 |
| Feed               | `["FEED"]`               | Feed animals                    |
| Collect fertilizer | `["COLLECT_FERTILIZER"]` | Collect fertilizer from animals |
| Care               | `["CARE"]`               | Care for animals                |

### Market operations

These operations are placed inside the `market` list.

| Operation   | Format                      | Description                  |
| ----------- | --------------------------- | ---------------------------- |
| Buy seeds   | `["BUY_SEED", crop, n]`     | Buy `n` crop seeds           |
| Buy product | `["BUY_PRODUCT", item, n]`  | Buy `n` units of a product   |
| Buy animal  | `["BUY_ANIMAL", animal, n]` | Buy `n` animals              |
| Sell        | `["SELL", item, n]`         | Sell `n` units of an item    |
| Hire        | `["HIRE"]`                  | Hire one additional hand     |
| Buy land    | `["BUY_LAND"]`              | Purchase additional farmland |

### Example

```python
{
    "farmer": ["PLANT", "CARROT"],
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

## Submission
[submission_example.py](submission/submission_example.py) 
You can submit as `.py`

[submission_example_zip](submission/submission_example_zip/main.py)
or you can also submit as `.zip` to include more file, but you do need to include `main.py` in it.

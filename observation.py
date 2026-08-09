from kaggle_environments import make

env = make("kaggriculture", debug=True)
agent_0 = "submission/submission_example_zip/main.py"
agent_1 = "submission/submission_example_zip/main.py"
env.run([agent_0, agent_1])

# obs = env.steps[36][0].observation
# obs = env.steps[36][1].observation

# ---------------------------------------------------------------------------
# Everything below this line builds a Flask app around the finished episode
# stored in env.steps. No data is invented: every value shown in the UI is
# read directly out of env.steps[i][player].observation.
# ---------------------------------------------------------------------------

from flask import Flask, jsonify, render_template_string

app = Flask(__name__)

TOTAL_STEPS = len(env.steps)


def to_plain(obj):
    """Recursively turn kaggle_environments Struct-like objects into plain
    dict/list/scalar Python data so it can be JSON-serialized."""
    if isinstance(obj, dict):
        return {k: to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_plain(v) for v in obj]
    if hasattr(obj, "items"):
        try:
            return {k: to_plain(v) for k, v in obj.items()}
        except Exception:
            pass
    return obj


def get_observation(step_idx, player):
    """Safely fetch env.steps[step_idx][player].observation as plain data."""
    step_idx = max(0, min(step_idx, TOTAL_STEPS - 1))
    entry = env.steps[step_idx][player]
    obs = getattr(entry, "observation", None)
    if obs is None:
        return {}
    return to_plain(obs)


def build_step_payload(step_idx):
    """Merge player-0's and player-1's observation for a given step.

    The public part (tiles/money/farmer/hands/market/town) is identical no
    matter which player observed it, so it's taken from player 0's view.
    The 'private' block (shed/seeds/inventories) only describes the
    *observing* player's own farm, so farm 0's private data comes from
    player 0's observation and farm 1's private data comes from player 1's
    observation of the same step.
    """
    obs0 = get_observation(step_idx, 0)
    obs1 = get_observation(step_idx, 1)

    farms_public = obs0.get("farms", [])
    privates = [obs0.get("private"), obs1.get("private")]

    farms = []
    for i, farm in enumerate(farms_public):
        farm = dict(farm)
        farm["private"] = privates[i] if i < len(privates) else None
        farms.append(farm)

    return {
        "step": obs0.get("step", step_idx),
        "day": obs0.get("day"),
        "hour": obs0.get("hour"),
        "remainingOverageTime": obs0.get("remainingOverageTime"),
        "farms": farms,
        "market": obs0.get("market"),
        "town": obs0.get("town"),
    }


@app.route("/api/meta")
def api_meta():
    return jsonify({"total_steps": TOTAL_STEPS})


@app.route("/api/step/<int:idx>")
def api_step(idx):
    return jsonify(build_step_payload(idx))


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Kaggriculture Replay Viewer</title>
<style>
  :root {
    --cell: 34px;
  }
  * { box-sizing: border-box; }
  body {
    font-family: -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    background: #1c1f24;
    color: #eee;
    margin: 0;
    padding: 16px 16px 90px 16px;
  }
  h1 { font-size: 18px; margin: 0 0 4px 0; }
  #status { color: #aaa; font-size: 13px; margin-bottom: 12px; }

  .top-area {
    display: flex;
    justify-content: center;
    gap: 40px;
    flex-wrap: wrap;
    align-items: flex-start;
  }

  .farm-block { display: flex; flex-direction: column; align-items: center; }
  .farm-title { font-weight: 600; margin-bottom: 6px; }

  .grid {
    position: relative;
    display: grid;
    grid-template-columns: repeat(10, var(--cell));
    grid-template-rows: repeat(10, var(--cell));
    border: 1px solid #444;
  }

  .cell {
    width: var(--cell);
    height: var(--cell);
    border: 1px solid #333;
    position: relative;
    font-size: 9px;
    background: #2a2e35;
  }
  .cell.locked { background: #000; border-color: #000; }
  .cell.empty { background: #b7f0b0; }

  .cell.coop { border: 3px solid #000; }
  .cell.pasture { border: 3px solid #7b4a24; }

  .tag {
    position: absolute;
    z-index: 10;
    font-weight: 700;
    line-height: 1;
    color: #111;
    text-shadow: 0 0 2px #fff, 0 0 2px #fff, 0 0 2px #fff;
    pointer-events: none;
  }
  .tag.tl { top: 1px; left: 1px; }
  .tag.tr { top: 1px; right: 1px; }
  .tag.center {
    top: 50%; left: 50%; transform: translate(-50%, -50%);
    font-size: 11px;
  }
  .tag.br { bottom: 1px; right: 1px; }
  .tag.bl { bottom: 1px; left: 1px; width: 6px; height: 6px; background: #333; border-radius: 1px; }

  .actor {
    position: absolute;
    border-radius: 50%;
    background: rgba(33, 118, 255, 0.55);
    border: 1px solid #1c5cd6;
    z-index: 5;
    pointer-events: none;
  }
  .actor.farmer {
    width: calc(var(--cell) * 0.85);
    height: calc(var(--cell) * 0.85);
  }
  .actor.hand {
    width: calc(var(--cell) * 0.45);
    height: calc(var(--cell) * 0.45);
  }

  .cell .tooltip {
    display: none;
    position: absolute;
    z-index: 50;
    top: 100%;
    left: 0;
    min-width: 170px;
    background: #111;
    border: 1px solid #555;
    color: #eee;
    padding: 6px 8px;
    font-size: 11px;
    white-space: pre-wrap;
    pointer-events: none;
  }
  .cell:hover .tooltip { display: block; }

  .farm-info {
    margin-top: 10px;
    width: calc(var(--cell) * 10);
    font-size: 12px;
    background: #262a31;
    border: 1px solid #3a3f47;
    border-radius: 4px;
    padding: 8px;
  }
  .farm-info h3 { margin: 0 0 6px 0; font-size: 13px; }
  .farm-info table { width: 100%; border-collapse: collapse; font-size: 11px; }
  .farm-info td { padding: 1px 4px; border-bottom: 1px solid #333; }
  .farm-info .money { font-weight: 700; color: #7CFC00; margin-bottom: 4px; }

  .side-panel {
    width: 220px;
    background: #262a31;
    border: 1px solid #3a3f47;
    border-radius: 4px;
    padding: 10px;
    font-size: 12px;
  }
  .side-panel h3 { margin: 0 0 6px 0; font-size: 13px; }
  .side-panel table { width: 100%; border-collapse: collapse; font-size: 11px; margin-bottom: 10px; }
  .side-panel td { padding: 1px 4px; border-bottom: 1px solid #333; }
  .side-panel ul { margin: 6px 0 10px 16px; padding: 0; }
  .side-panel li { margin-bottom: 4px; list-style-type: disc; }

  .legend {
    max-width: 900px;
    margin: 16px auto 0 auto;
    font-size: 11px;
    color: #aaa;
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .swatch { display: inline-block; width: 10px; height: 10px; margin-right: 4px; vertical-align: middle; }

  #controls {
    position: fixed;
    left: 0; right: 0; bottom: 0;
    background: #14161a;
    border-top: 1px solid #333;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  #controls button {
    background: #2d7dd2;
    color: #fff;
    border: none;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
  }
  #controls button:hover { background: #1f63ab; }
  #slider { flex: 1; }
  #stepLabel { min-width: 160px; text-align: right; font-size: 12px; color: #ccc; }
</style>
</head>
<body>

<h1>Kaggriculture Replay Viewer</h1>
<div id="status">Loading...</div>

<div class="top-area">
  <div class="farm-block">
    <div class="farm-title">Farm 0 (Player 0)</div>
    <div class="grid" id="grid0"></div>
    <div class="farm-info" id="info0"></div>
  </div>
  <div class="farm-block">
    <div class="farm-title">Farm 1 (Player 1)</div>
    <div class="grid" id="grid1"></div>
    <div class="farm-info" id="info1"></div>
  </div>
  <div class="side-panel" id="sidePanel"></div>
</div>

<div class="legend">
  <span><span class="swatch" style="background:#4caf50"></span>Melon</span>
  <span><span class="swatch" style="background:#ff9800"></span>Carrot</span>
  <span><span class="swatch" style="background:#f48fb1"></span>Strawberry</span>
  <span><span class="swatch" style="background:#ffeb3b"></span>Wheat</span>
  <span><span class="swatch" style="background:#f44336"></span>Tomato</span>
  <span><span class="swatch" style="background:#8d6e63"></span>Goose</span>
  <span><span class="swatch" style="background:#9e9e9e"></span>Cow</span>
  <span><span class="swatch" style="background:#f5f5f5"></span>Sheep</span>
  <span><span class="swatch" style="background:#000;border:3px solid #000"></span>Coop border</span>
  <span><span class="swatch" style="background:#2a2e35;border:3px solid #7b4a24"></span>Pasture border</span>
  <span><span class="swatch" style="background:#000"></span>Locked</span>
  <span><span class="swatch" style="background:#b7f0b0"></span>Empty tile</span>
  <span><span class="swatch" style="border-radius:50%;background:#2176ff"></span>Farmer / hand</span>
</div>

<div id="controls">
  <button id="playBtn">Play</button>
  <button id="prevBtn">&laquo; Prev</button>
  <button id="nextBtn">Next &raquo;</button>  <label for="speedSelect" style="color:#eee; font-size:12px; margin-left:8px;">Speed:</label>
  <select id="speedSelect">
    <option value="800">0.5x</option>
    <option value="400" selected>1x</option>
    <option value="200">2x</option>
    <option value="100">4x</option>
    <option value="50">8x</option>
    <option value="25">16x</option>
    <option value="10">40x</option>
    <option value="5">80x</option>
  </select>  <input type="range" id="slider" min="0" max="0" value="0" step="1">
  <div id="stepLabel">Step 0 / 0</div>
</div>

<script>
const CROP_COLOR = {MELON:'#4caf50', CARROT:'#ff9800', STRAWBERRY:'#f48fb1', WHEAT:'#ffeb3b', TOMATO:'#f44336'};
const ANIMAL_COLOR = {GOOSE:'#8d6e63', COW:'#9e9e9e', SHEEP:'#f5f5f5'};

let TOTAL_STEPS = 0;
let currentStep = 0;
let playing = false;
let playTimer = null;
let playSpeedMs = 400;
const cache = {};

function fetchStep(idx) {
  if (cache[idx]) return Promise.resolve(cache[idx]);
  return fetch('/api/step/' + idx).then(r => r.json()).then(data => {
    cache[idx] = data;
    return data;
  });
}

function fmt(v) {
  if (v === null || v === undefined) return '';
  return v;
}

function tileTooltipText(tile) {
  if (!tile || tile === 'LOCKED') return 'Locked';
  let lines = [];
  for (const k in tile) lines.push(k + ': ' + tile[k]);
  return lines.join('\\n');
}

function renderCell(tile) {
  const cell = document.createElement('div');
  cell.className = 'cell';

  if (tile === 'LOCKED') {
    cell.classList.add('locked');
    return cell;
  }
  if (tile === null || tile === undefined) {
    cell.classList.add('empty');
    return cell;
  }

  const kind = tile.kind;

  if (kind === 'PASTURE' || kind === 'COOP') {
    cell.classList.add(kind === 'COOP' ? 'coop' : 'pasture');
    if (tile.animal) {
      cell.style.background = ANIMAL_COLOR[tile.animal] || '#fff';
    }
    if (tile.pending_care_bonus !== undefined && tile.pending_care_bonus !== null && tile.pending_care_bonus !== 0) {
      const tl = document.createElement('span');
      tl.className = 'tag tl';
      tl.textContent = tile.pending_care_bonus;
      cell.appendChild(tl);
    }
    if (tile.fed_today) {
      const tr = document.createElement('span');
      tr.className = 'tag tr';
      tr.textContent = '\\u2713';
      cell.appendChild(tr);
    }
    if (tile.yield_units !== undefined && tile.yield_units !== null) {
      const c = document.createElement('span');
      c.className = 'tag center';
      c.textContent = tile.yield_units;
      cell.appendChild(c);
    }
    if (tile.consecutive_unfed !== undefined && tile.consecutive_unfed !== null) {
      const br = document.createElement('span');
      br.className = 'tag br';
      br.textContent = tile.consecutive_unfed;
      cell.appendChild(br);
    }
    if (tile.fertilizer_available) {
      const bl = document.createElement('span');
      bl.className = 'tag bl';
      cell.appendChild(bl);
    }
  } else if (kind === 'PLANT') {
    cell.style.background = CROP_COLOR[tile.crop] || '#888';
    if (tile.fertilized_until_day !== undefined && tile.fertilized_until_day !== null) {
      const tl = document.createElement('span');
      tl.className = 'tag tl';
      tl.textContent = tile.fertilized_until_day;
      cell.appendChild(tl);
    }
    if (tile.watered_today) {
      const tr = document.createElement('span');
      tr.className = 'tag tr';
      tr.textContent = '\\u2713';
      cell.appendChild(tr);
    }
    if (tile.yield_units !== undefined && tile.yield_units !== null) {
      const c = document.createElement('span');
      c.className = 'tag center';
      c.textContent = tile.yield_units;
      cell.appendChild(c);
    }
    if (tile.consecutive_unwatered !== undefined && tile.consecutive_unwatered !== null) {
      const br = document.createElement('span');
      br.className = 'tag br';
      br.textContent = tile.consecutive_unwatered;
      cell.appendChild(br);
    }
  }

  const tip = document.createElement('div');
  tip.className = 'tooltip';
  tip.textContent = tileTooltipText(tile);
  cell.appendChild(tip);

  return cell;
}

function renderGrid(gridEl, farm) {
  gridEl.innerHTML = '';
  const tiles = farm.tiles || [];
  for (let r = 0; r < tiles.length; r++) {
    for (let c = 0; c < tiles[r].length; c++) {
      const cell = renderCell(tiles[r][c]);
      gridEl.appendChild(cell);
    }
  }

  if (farm.farmer) {
    const [fx, fy] = farm.farmer;
    const row = fy;
    const col = fx;
    const el = document.createElement('div');
    el.className = 'actor farmer';
    el.style.top = (row * 34 + 34 * 0.075) + 'px';
    el.style.left = (col * 34 + 34 * 0.075) + 'px';
    gridEl.appendChild(el);
  }
  if (farm.hands) {
    for (const h of farm.hands) {
      const [hx, hy] = h;
      const row = hy;
      const col = hx;
      const el = document.createElement('div');
      el.className = 'actor hand';
      el.style.top = (row * 34 + 34 * 0.275) + 'px';
      el.style.left = (col * 34 + 34 * 0.275) + 'px';
      gridEl.appendChild(el);
    }
  }
}

function renderTable(obj) {
  if (!obj) return '<div>-</div>';
  let rows = '';
  for (const k in obj) {
    const value = Array.isArray(obj[k]) ? obj[k].join(', ') : obj[k];
    rows += '<tr><td>' + k + '</td><td>' + fmt(value) + '</td></tr>';
  }
  return '<table>' + rows + '</table>';
}

function renderArrayList(items) {
  if (!items || !items.length) return '<div>-</div>';
  return '<ul>' + items.map(item => '<li>' + fmt(item) + '</li>').join('') + '</ul>';
}

function renderFarmInfo(el, farm, label) {
  const priv = farm.private || {};
  let html = '<h3>' + label + '</h3>';
  html += '<div class="money">Money: ' + fmt(farm.money) + '</div>';
  html += '<div>Shed</div>' + renderTable(priv.shed);
  html += '<div>Seeds</div>' + renderTable(priv.seeds);
  html += '<div>Inventories</div>';
  if (priv.inventories) {
    priv.inventories.forEach((inv, i) => {
      html += '<div style="margin-bottom:4px;">#' + i + '</div>' + renderTable(inv);
    });
  }
  el.innerHTML = html;
}

function renderSidePanel(data) {
  const el = document.getElementById('sidePanel');
  const market = data.market || {};
  const town = data.town || {};
  let html = '<h3>Market</h3><table><tr><td><b>Item</b></td><td><b>Inv</b></td><td><b>Price</b></td></tr>';
  const inv = market.inventory || {};
  const prices = market.prices || {};
  const keys = new Set([...Object.keys(inv), ...Object.keys(prices)]);
  keys.forEach(k => {
    html += '<tr><td>' + k + '</td><td>' + fmt(inv[k]) + '</td><td>' + fmt(prices[k]) + '</td></tr>';
  });
  html += '</table>';
  html += '<h3>Town</h3>';
  if (Array.isArray(town.unlocked_shops)) {
    html += '<div>Unlocked shops:</div>' + renderArrayList(town.unlocked_shops);
    const otherTown = { ...town };
    delete otherTown.unlocked_shops;
    if (Object.keys(otherTown).length) {
      html += renderTable(otherTown);
    }
  } else {
    html += renderTable(town);
  }
  el.innerHTML = html;
}

async function showStep(idx) {
  idx = Math.max(0, Math.min(idx, TOTAL_STEPS - 1));
  currentStep = idx;
  const data = await fetchStep(idx);
  const farms = data.farms || [];
  if (farms[0]) {
    renderGrid(document.getElementById('grid0'), farms[0]);
    renderFarmInfo(document.getElementById('info0'), farms[0], 'Farm 0');
  }
  if (farms[1]) {
    renderGrid(document.getElementById('grid1'), farms[1]);
    renderFarmInfo(document.getElementById('info1'), farms[1], 'Farm 1');
  }
  renderSidePanel(data);
  document.getElementById('slider').value = idx;
  document.getElementById('stepLabel').textContent =
    'Step ' + idx + ' / ' + (TOTAL_STEPS - 1) + '   Day ' + fmt(data.day) + '  Hour ' + fmt(data.hour);
  document.getElementById('status').textContent = 'Episode loaded: ' + TOTAL_STEPS + ' steps.';
}

function startPlayTimer() {
  playTimer = setInterval(() => {
    if (currentStep >= TOTAL_STEPS - 1) {
      togglePlay();
      return;
    }
    showStep(currentStep + 1);
  }, playSpeedMs);
}

function togglePlay() {
  playing = !playing;
  document.getElementById('playBtn').textContent = playing ? 'Pause' : 'Play';
  if (playing) {
    startPlayTimer();
  } else {
    clearInterval(playTimer);
  }
}

function updatePlaySpeed() {
  const select = document.getElementById('speedSelect');
  playSpeedMs = parseInt(select.value, 10) || 400;
  if (playing) {
    clearInterval(playTimer);
    startPlayTimer();
  }
}

document.getElementById('playBtn').addEventListener('click', togglePlay);
document.getElementById('speedSelect').addEventListener('change', updatePlaySpeed);
document.getElementById('prevBtn').addEventListener('click', () => showStep(currentStep - 1));
document.getElementById('nextBtn').addEventListener('click', () => showStep(currentStep + 1));
document.getElementById('slider').addEventListener('input', (e) => showStep(parseInt(e.target.value, 10)));

fetch('/api/meta').then(r => r.json()).then(meta => {
  TOTAL_STEPS = meta.total_steps;
  document.getElementById('slider').max = TOTAL_STEPS - 1;
  showStep(0);
});
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
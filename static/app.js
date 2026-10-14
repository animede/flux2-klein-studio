const $ = id => document.getElementById(id);
let activeJob = null, lastSeed = null, referenceURLs = [], polling = false;

function showStatus(message, error = false) {
  $('status').textContent = message;
  $('status').classList.toggle('error', error);
}
function busy(value) {
  $('generate').disabled = value;
  $('unload').disabled = value;
  $('model').disabled = value;
  $('cancel').hidden = !value;
  $('cancel').disabled = false;
  $('progress-track').hidden = !value;
}
const modelInfo = {
  '4b': { badge: 'LOCAL · 4B', note: 'Q4 / NF4 · Apache-2.0', footer: 'FLUX.2 klein 4B · GGUF Q4 / NF4 · Apache-2.0' },
  '9b': { badge: 'LOCAL · 9B · 非商用・非本番', note: 'Q3 / NF4 · FLUX Non-Commercial License v2.1', footer: 'FLUX.2 klein 9B · GGUF Q3 / NF4 · 非商用・非本番' },
};
function updateModelInfo() {
  const key = $('model').value;
  const info = modelInfo[key];
  $('model-badge').textContent = info.badge;
  $('model-note').textContent = info.note;
  $('model-note').classList.toggle('license-warning', key === '9b');
  $('model-footer').textContent = info.footer;
  localStorage.setItem('klein-model', key);
  showStatus(key === '9b' ? '9Bを選択しました。非商用・非本番用途に限られ、追加の利用条件があります。' : '4Bを選択しました。');
}
$('model').value = localStorage.getItem('klein-model') || '4b';
$('model').addEventListener('change', updateModelInfo);
updateModelInfo();
async function loadModelAvailability() {
  const data = await request('/api/models');
  for (const option of $('model').options) {
    const available = data.models[option.value]?.available;
    option.disabled = !available;
    option.textContent = option.value === '4b'
      ? `FLUX.2 klein 4B · 軽量${available ? '' : '（未取得）'}`
      : `FLUX.2 klein 9B · 高品質${available ? '' : '（未取得）'}`;
  }
  if ($('model').selectedOptions[0].disabled) {
    const available = [...$('model').options].find(option => !option.disabled);
    if (available) $('model').value = available.value;
  }
  updateModelInfo();
}
loadModelAvailability().catch(() => showStatus('モデルの準備状態を確認できませんでした。', true));
async function request(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(typeof data.detail === 'string' ? data.detail : 'リクエストを処理できませんでした。');
  return data;
}
function preview() {
  referenceURLs.forEach(url => URL.revokeObjectURL(url));
  referenceURLs = [];
  const files = [...$('image-input').files];
  const previews = $('reference-previews');
  previews.replaceChildren();
  previews.dataset.count = files.length;
  previews.hidden = !files.length;
  $('upload-empty').hidden = !!files.length;
  $('clear-image').hidden = !files.length;
  $('reference-name').textContent = files.length
    ? `${files.length}枚選択 · ${files.map(file => file.name).join(' / ')}`
    : '画像なしの場合はテキストから生成します';
  for (const [index, file] of files.entries()) {
    const url = URL.createObjectURL(file);
    referenceURLs.push(url);
    const item = document.createElement('div');
    item.className = 'reference-item';
    const img = document.createElement('img');
    img.src = url; img.alt = `参照画像 ${index + 1}`;
    const number = document.createElement('span');
    number.textContent = index + 1;
    item.append(img, number); previews.append(item);
  }
}
$('image-input').addEventListener('change', () => {
  if ($('image-input').files.length > 8) {
    $('image-input').value = '';
    preview(); showStatus('参照画像は8枚まで選択できます。', true); return;
  }
  preview(); showStatus('参照画像を選択しました。');
});
$('clear-image').onclick = () => { $('image-input').value = ''; preview(); };
for (const event of ['dragenter', 'dragover']) $('drop-zone').addEventListener(event, () => $('drop-zone').classList.add('drag'));
for (const event of ['dragleave', 'drop']) $('drop-zone').addEventListener(event, () => $('drop-zone').classList.remove('drag'));
$('example-prompt').onclick = () => {
  $('prompt').value = 'Create a new image of the same character from the reference image, sitting by a cafe window and reading a book. Preserve the character\'s facial features, hairstyle, hair color, eye color, distinctive accessories, and art style. Change the pose and setting. Soft afternoon light.';
  $('prompt').focus();
};

async function poll(id) {
  if (polling) return;
  polling = true;
  let failures = 0;
  try {
    while (activeJob === id) {
      let job;
      try { job = await request(`/api/jobs/${id}`); failures = 0; }
      catch (error) {
        failures++;
        if (failures >= 5) throw error;
        showStatus('接続を再確認しています…');
        await new Promise(r => setTimeout(r, 2000)); continue;
      }
      showStatus(job.message, job.status === 'error');
      $('result-state').textContent = job.status.toUpperCase();
      $('progress-fill').style.width = `${job.step / 4 * 100}%`;
      if (job.status === 'done') {
        $('result-image').src = job.image_url;
        $('result-image').hidden = false;
        $('result-empty').hidden = true;
        $('result-actions').hidden = false;
        $('download').href = job.image_url;
        $('metadata').href = job.metadata_url;
        $('metadata').download = 'generation.json';
        $('metadata').hidden = false;
        lastSeed = job.seed;
        const m = job.metrics;
        const quant = job.model === '9b' ? 'GGUF Q3 / NF4 · 非商用・非本番' : 'GGUF Q4 / NF4 · Apache-2.0';
        $('metrics').textContent = `モデル：${job.model_name}\nシード：${job.seed}\n生成時間：${m.seconds}秒（読み込み込み ${m.total_seconds}秒）\nピークVRAM：割り当て ${m.peak_allocated_gib} GiB / 予約 ${m.peak_reserved_gib} GiB\nGPU：${m.gpu}\nPyTorch割り当て上限：${m.allocator_budget_gib} GiB\n4ステップ · ${quant}\n※VRAM値はPyTorch計測。ドライバー等の使用量は含みません。`;
      }
      if (['done', 'error', 'cancelled'].includes(job.status)) {
        activeJob = null; localStorage.removeItem('klein-job'); busy(false); break;
      }
      await new Promise(r => setTimeout(r, 1000));
    }
  } catch (error) {
    showStatus(`${error.message} ページを再読み込みすると進行状況を再確認できます。`, true);
    activeJob = null; busy(false);
  } finally { polling = false; }
}

$('generate-form').addEventListener('submit', async event => {
  event.preventDefault(); busy(true); $('progress-fill').style.width = '0%';
  $('result-state').textContent = 'PREPARING'; showStatus('生成をリクエストしています');
  const [width, height] = $('size').value.split(',');
  const data = new FormData();
  data.set('prompt', $('prompt').value); data.set('model', $('model').value); data.set('width', width); data.set('height', height);
  data.set('seed', $('seed').value);
  for (const file of $('image-input').files) data.append('image', file);
  try {
    const job = await request('/api/generate', { method: 'POST', body: data });
    activeJob = job.id; localStorage.setItem('klein-job', job.id); await poll(job.id);
  } catch (error) { showStatus(error.message, true); busy(false); $('result-state').textContent = 'ERROR'; }
});
$('cancel').onclick = async () => {
  if (!activeJob) return;
  $('cancel').disabled = true;
  try { const job = await request(`/api/jobs/${activeJob}/cancel`, { method: 'POST' }); showStatus(job.message); }
  catch (error) { showStatus(error.message, true); }
};
$('reuse-seed').onclick = () => { if (lastSeed !== null) $('seed').value = lastSeed; };
$('unload').onclick = async () => {
  $('unload').disabled = true;
  try { await request('/api/unload', { method: 'POST' }); showStatus('モデルを解放しました。次の生成時に再読み込みします。'); }
  catch (error) { showStatus(error.message, true); }
  finally { $('unload').disabled = false; }
};
const savedJob = localStorage.getItem('klein-job');
if (savedJob) { activeJob = savedJob; busy(true); poll(savedJob); }

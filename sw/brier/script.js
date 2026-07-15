// Brier score calculator - client-side logic
// Created 2026-07-14 by Cline

const NUM_ITEMS = 36;
const MIN_VALUE = 1;
const MAX_VALUE = 99;
const VALUE_FOR_TRUE = 1;
const VALUE_FOR_FALSE = 99;
const NORMALIZATION = 9604; // (99 - 1)^2

const itemsList = document.getElementById('items-list');
const averageValue = document.getElementById('average-value');
const answerFileInput = document.getElementById('answer-file');
const uploadStatus = document.getElementById('upload-status');

// logicalValues[i] is true, false, or null (unset) for item i
const logicalValues = new Array(NUM_ITEMS).fill(null);

function clamp(value) {
  if (Number.isNaN(value)) return null;
  if (value < MIN_VALUE) return MIN_VALUE;
  if (value > MAX_VALUE) return MAX_VALUE;
  return value;
}

function brierScore(n, isTrue) {
  const v = isTrue ? VALUE_FOR_TRUE : VALUE_FOR_FALSE;
  return (1 / NORMALIZATION) * Math.pow(n - v, 2);
}

function formatScore(score) {
  return score.toFixed(6);
}

function buildItems() {
  itemsList.innerHTML = '';
  for (let i = 0; i < NUM_ITEMS; i += 1) {
    const li = document.createElement('li');
    li.className = 'item';
    li.dataset.index = String(i);

    const indexEl = document.createElement('span');
    indexEl.className = 'item-index';
    indexEl.textContent = `Item ${i + 1}`;

    const valueEl = document.createElement('span');
    valueEl.className = 'item-value unset';
    valueEl.textContent = 'Unset';

    const inputWrapper = document.createElement('div');
    inputWrapper.className = 'item-input-wrapper';

    const input = document.createElement('input');
    input.type = 'number';
    input.min = String(MIN_VALUE);
    input.max = String(MAX_VALUE);
    input.step = '1';
    input.placeholder = '1–99';
    input.disabled = true;
    input.setAttribute('aria-label', `Predicted percentage for item ${i + 1}`);

    inputWrapper.appendChild(input);

    const scoreEl = document.createElement('span');
    scoreEl.className = 'item-score empty';
    scoreEl.textContent = '—';

    li.appendChild(indexEl);
    li.appendChild(valueEl);
    li.appendChild(inputWrapper);
    li.appendChild(scoreEl);

    input.addEventListener('input', (event) => {
      handleInputChange(i, event.target);
    });
    // Also recompute on blur to clamp values that became out-of-range via paste
    input.addEventListener('blur', (event) => {
      handleInputChange(i, event.target);
    });

    itemsList.appendChild(li);
  }
}

function updateValueBadge(itemEl, value) {
  const badge = itemEl.querySelector('.item-value');
  badge.classList.remove('true', 'false', 'unset');
  if (value === true) {
    badge.classList.add('true');
    badge.textContent = 'True';
  } else if (value === false) {
    badge.classList.add('false');
    badge.textContent = 'False';
  } else {
    badge.classList.add('unset');
    badge.textContent = 'Unset';
  }
}

function updateItemState(itemEl) {
  const index = Number(itemEl.dataset.index);
  const input = itemEl.querySelector('input[type="number"]');
  const scoreEl = itemEl.querySelector('.item-score');
  const value = logicalValues[index];

  if (value === null) {
    input.disabled = true;
    input.value = '';
    scoreEl.textContent = '—';
    scoreEl.classList.add('empty');
    return;
  }

  input.disabled = false;
  const raw = input.value === '' ? null : Number(input.value);
  if (raw === null || Number.isNaN(raw)) {
    scoreEl.textContent = '—';
    scoreEl.classList.add('empty');
    return;
  }

  const clamped = clamp(raw);
  if (clamped !== raw) {
    input.value = String(clamped);
  }
  const score = brierScore(clamped, value);
  scoreEl.textContent = formatScore(score);
  scoreEl.classList.remove('empty');
}

function handleInputChange(index, inputEl) {
  const itemEl = itemsList.querySelector(`li[data-index="${index}"]`);
  if (!itemEl) return;
  const value = logicalValues[index];
  if (value === null) return;

  const raw = inputEl.value === '' ? null : Number(inputEl.value);
  const scoreEl = itemEl.querySelector('.item-score');

  if (raw === null || Number.isNaN(raw)) {
    scoreEl.textContent = '—';
    scoreEl.classList.add('empty');
  } else {
    const clamped = clamp(raw);
    if (clamped !== raw) {
      inputEl.value = String(clamped);
    }
    const score = brierScore(clamped, value);
    scoreEl.textContent = formatScore(score);
    scoreEl.classList.remove('empty');
  }

  recomputeAverage();
}

function recomputeAverage() {
  let sum = 0;
  let count = 0;
  for (let i = 0; i < NUM_ITEMS; i += 1) {
    if (logicalValues[i] === null) continue;
    const itemEl = itemsList.querySelector(`li[data-index="${i}"]`);
    if (!itemEl) continue;
    const input = itemEl.querySelector('input[type="number"]');
    const raw = input.value === '' ? null : Number(input.value);
    if (raw === null || Number.isNaN(raw)) continue;
    const clamped = clamp(raw);
    sum += brierScore(clamped, logicalValues[i]);
    count += 1;
  }
  if (count === 0) {
    averageValue.textContent = '—';
  } else {
    averageValue.textContent = formatScore(sum / count);
  }
}

function parseAnswerFile(text) {
  // Accept T, F, true, false, TRUE, FALSE, 1, 0. Split on any non-letter/digit.
  const tokens = text
    .split(/[^A-Za-z0-9]+/)
    .map((t) => t.trim())
    .filter((t) => t.length > 0);

  return tokens.map((token) => {
    const upper = token.toUpperCase();
    if (upper === 'T' || upper === 'TRUE' || upper === '1') return true;
    if (upper === 'F' || upper === 'FALSE' || upper === '0') return false;
    return null;
  });
}

function applyLogicalValues(values) {
  for (let i = 0; i < NUM_ITEMS; i += 1) {
    logicalValues[i] = i < values.length ? values[i] : null;
    const itemEl = itemsList.querySelector(`li[data-index="${i}"]`);
    if (itemEl) {
      updateValueBadge(itemEl, logicalValues[i]);
      updateItemState(itemEl);
    }
  }
  recomputeAverage();
}

function setUploadStatus(message, kind) {
  uploadStatus.textContent = message;
  uploadStatus.classList.remove('error', 'success');
  if (kind) {
    uploadStatus.classList.add(kind);
  }
}

function handleFileUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) {
    setUploadStatus('No file selected.', 'error');
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => {
    const text = String(e.target.result || '');
    const parsed = parseAnswerFile(text);
    const valid = parsed.filter((v) => v !== null).length;
    const total = parsed.length;
    if (total === 0) {
      setUploadStatus(
        'Could not find any T/F values in the file. Please upload a file with T or F values.',
        'error'
      );
      return;
    }
    if (valid < NUM_ITEMS) {
      setUploadStatus(
        `Loaded ${valid} T/F values from "${file.name}" (${total} tokens found). The remaining ${NUM_ITEMS - valid} items will stay unset.`,
        valid > 0 ? 'success' : 'error'
      );
    } else {
      setUploadStatus(
        `Loaded ${valid} T/F values from "${file.name}". You may now enter predicted percentages.`,
        'success'
      );
    }
    applyLogicalValues(parsed);
  };
  reader.onerror = () => {
    setUploadStatus(`Failed to read "${file.name}".`, 'error');
  };
  reader.readAsText(file);
}

function init() {
  buildItems();
  recomputeAverage();
  answerFileInput.addEventListener('change', handleFileUpload);
}

init();

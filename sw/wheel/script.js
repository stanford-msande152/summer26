const svg = document.getElementById('probability-wheel');
const orangeWedge = document.getElementById('orange-wedge');
const blueWedge = document.getElementById('blue-wedge');
const dragHandle = document.getElementById('drag-handle');
const percentValue = document.getElementById('percent-value');
const angleRange = document.getElementById('angle-range');

const center = { x: 160, y: 160 };
const radius = 140;
let percent = 50;
let isDragging = false;

function angleToPoint(angleDegrees) {
  const radians = (angleDegrees - 90) * (Math.PI / 180);
  return {
    x: center.x + radius * Math.cos(radians),
    y: center.y + radius * Math.sin(radians),
  };
}

function clampPercent(value) {
  return Math.min(100, Math.max(0, value));
}

function updateWedgeDisplay(value) {
  percent = clampPercent(value);
  angleRange.value = percent;
  percentValue.textContent = `${Math.round(percent)}%`;

  const angle = (percent / 100) * 360;
  const largeArc = angle > 180 ? 1 : 0;
  const blueLargeArc = angle > 180 ? 0 : 1;
  const end = angleToPoint(angle);
  const pathOrange = [
    `M ${center.x} ${center.y}`,
    `L ${center.x} ${center.y - radius}`,
    `A ${radius} ${radius} 0 ${largeArc} 1 ${end.x} ${end.y}`,
    'Z',
  ].join(' ');

  const pathBlue = [
    `M ${center.x} ${center.y}`,
    `L ${end.x} ${end.y}`,
    `A ${radius} ${radius} 0 ${blueLargeArc} 1 ${center.x} ${center.y - radius}`,
    'Z',
  ].join(' ');

  orangeWedge.setAttribute('d', pathOrange);
  blueWedge.setAttribute('d', pathBlue);

  dragHandle.setAttribute('cx', end.x);
  dragHandle.setAttribute('cy', end.y);
}

function pointerToPercent(event) {
  const rect = svg.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  const svgX = (x / rect.width) * svg.viewBox.baseVal.width;
  const svgY = (y / rect.height) * svg.viewBox.baseVal.height;
  const dx = svgX - center.x;
  const dy = svgY - center.y;
  let angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90;
  if (angle < 0) angle += 360;
  return (angle / 360) * 100;
}

function handlePointerMove(event) {
  if (!isDragging) return;
  const newPercent = pointerToPercent(event);
  updateWedgeDisplay(newPercent);
}

function handlePointerEnd() {
  isDragging = false;
  dragHandle.style.cursor = 'grab';
}

function handlePointerStart(event) {
  event.preventDefault();
  isDragging = true;
  dragHandle.style.cursor = 'grabbing';
  document.addEventListener('pointermove', handlePointerMove);
  document.addEventListener('pointerup', handlePointerEnd, { once: true });
}

function handleRangeChange(event) {
  updateWedgeDisplay(parseFloat(event.target.value));
}

dragHandle.addEventListener('pointerdown', handlePointerStart);
angleRange.addEventListener('input', handleRangeChange);

dragHandle.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') {
    event.preventDefault();
    updateWedgeDisplay(percent - 1);
  }
  if (event.key === 'ArrowRight' || event.key === 'ArrowUp') {
    event.preventDefault();
    updateWedgeDisplay(percent + 1);
  }
  if (event.key === 'Home') {
    event.preventDefault();
    updateWedgeDisplay(0);
  }
  if (event.key === 'End') {
    event.preventDefault();
    updateWedgeDisplay(100);
  }
});

updateWedgeDisplay(percent);

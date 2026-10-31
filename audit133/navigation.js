let cardNavKeys = [];
let cardNavScope = 'filtered';
let cardDetailRequest = 0;

function ensureCardNavigation(kind, id) {
  const key = kind + '_' + id;
  if (cardNavKeys.includes(key)) return;
  const pool = getCardPool();
  const inPool = pool.some(it => it.kind === kind && String(it.id) === String(id));
  cardNavKeys = (inPool ? pool : getAllItems().filter(it => it.kind === kind))
    .map(it => it.kind + '_' + it.id);
  cardNavScope = inPool ? 'filtered' : kind;
}

function updateCardNavigation() {
  const key = document.getElementById('cardDetailBody').dataset.currentKey;
  const index = cardNavKeys.indexOf(key);
  document.querySelectorAll('[data-card-step]').forEach(btn => {
    const step = Number(btn.dataset.cardStep);
    btn.disabled = index < 0 || index + step < 0 || index + step >= cardNavKeys.length;
  });
  document.querySelectorAll('.card-position').forEach(el => {
    el.textContent = index < 0 ? '—' : `${index + 1} / ${cardNavKeys.length}`;
  });
  document.getElementById('cardNavScope').textContent =
    cardNavScope === 'v' ? '全語彙' : cardNavScope === 'g' ? '全文法' : '閲覧リスト';
}

async function navigateCard(step) {
  const key = document.getElementById('cardDetailBody').dataset.currentKey;
  const index = cardNavKeys.indexOf(key);
  if (index < 0 || index + step < 0 || index + step >= cardNavKeys.length) return false;
  const next = cardNavKeys[index + step];
  const sep = next.indexOf('_');
  const kind = next.slice(0, sep), id = next.slice(sep + 1);
  const position = getCardPool().findIndex(it => it.kind === kind && String(it.id) === id);
  if (position >= 0) {
    curPage = Math.floor(position / PAGE_SIZE) + 1;
    renderCardsList();
  }
  await openCardDetail(kind, id);
  window.scrollTo({ top: 0, behavior: 'auto' });
  return true;
}

async function advanceToNextCard(kind, id, container) {
  if (container.dataset.currentKey !== kind + '_' + id) return;
  if (!await navigateCard(1)) {
    await refreshCardView(kind, id, container);
    showToast('このリストの最後のカードです。', 'info');
  }
}

async function openCardDetail(kind, id) {
  const request = ++cardDetailRequest;
  ensureCardNavigation(kind, id);
  document.getElementById('cardListPanel').style.display = 'none';
  document.getElementById('cardDetailPanel').style.display = '';
  const body = document.getElementById('cardDetailBody');
  body.dataset.currentKey = kind + '_' + id;
  body.innerHTML = renderCardShell(kind, id, null);
  updateCardNavigation();
  try {
    const data = await getCardData(kind, id);
    if (request !== cardDetailRequest) return;
    body.innerHTML = renderCardShell(kind, id, data);
    bindChips(body);
  } catch (e) {
    if (request !== cardDetailRequest) return;
    body.innerHTML += '<div class="small" style="margin-top:10px">カードの読み込みに失敗しました。</div>';
  }
}

document.querySelectorAll('[data-card-step]').forEach(btn => {
  btn.addEventListener('click', () => navigateCard(Number(btn.dataset.cardStep)));
});

function cardBrowsingIsActive() {
  return document.getElementById('view-cards').classList.contains('active') &&
    document.getElementById('cardDetailPanel').style.display !== 'none';
}

document.addEventListener('keydown', event => {
  if (!cardBrowsingIsActive() || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
  if (event.target.closest('input,textarea,select,[contenteditable="true"]')) return;
  if (window.getSelection()?.toString()) return;
  if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
  event.preventDefault();
  navigateCard(event.key === 'ArrowRight' ? 1 : -1);
});

let cardSwipe = null;
const cardSwipeArea = document.getElementById('cardDetailBody');
cardSwipeArea.addEventListener('touchstart', event => {
  cardSwipe = null;
  if (!cardBrowsingIsActive() || event.touches.length !== 1) return;
  if (event.target.closest('button,a,input,textarea,select,.chip,[contenteditable="true"]')) return;
  if (window.getSelection()?.toString()) return;
  const touch = event.touches[0];
  cardSwipe = { x: touch.clientX, y: touch.clientY, time: Date.now(), key: cardSwipeArea.dataset.currentKey };
}, { passive: true });
cardSwipeArea.addEventListener('touchend', event => {
  const start = cardSwipe;
  cardSwipe = null;
  if (!start || event.changedTouches.length !== 1 || !cardBrowsingIsActive()) return;
  if (start.key !== cardSwipeArea.dataset.currentKey || Date.now() - start.time > 650) return;
  if (window.getSelection()?.toString()) return;
  const touch = event.changedTouches[0];
  const dx = touch.clientX - start.x, dy = touch.clientY - start.y;
  if (Math.abs(dx) >= 72 && Math.abs(dx) > Math.abs(dy) * 1.75) navigateCard(dx < 0 ? 1 : -1);
}, { passive: true });
cardSwipeArea.addEventListener('touchcancel', () => { cardSwipe = null; }, { passive: true });

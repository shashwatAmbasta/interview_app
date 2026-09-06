const authView = document.querySelector('#auth-view');
const appView = document.querySelector('#app-view');
const authForm = document.querySelector('#auth-form');
const toast = document.querySelector('#toast');
let authMode = 'login';
let interview = null;
let questionIndex = 0;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3200);
}

function setAuthMode(mode) {
  authMode = mode;
  document.querySelectorAll('.tab').forEach(tab => tab.classList.toggle('active', tab.dataset.mode === mode));
  document.querySelector('#name-field').classList.toggle('hidden', mode === 'login');
  document.querySelector('#auth-title').textContent = mode === 'login' ? 'Pick up where you left off.' : 'Make space for better questions.';
  document.querySelector('#auth-subtitle').textContent = mode === 'login' ? 'Your next good conversation is waiting.' : 'Your private interview workspace starts here.';
  document.querySelector('#auth-action').textContent = mode === 'login' ? 'Enter workspace' : 'Create workspace';
}

document.querySelectorAll('.tab').forEach(tab => tab.addEventListener('click', () => setAuthMode(tab.dataset.mode)));

authForm.addEventListener('submit', async event => {
  event.preventDefault();
  const button = authForm.querySelector('button');
  button.disabled = true;
  const payload = { email: document.querySelector('#email').value, password: document.querySelector('#password').value, name: document.querySelector('#name').value };
  try {
    const response = await fetch(`/api/auth/${authMode === 'login' ? 'login' : 'register'}`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Unable to continue');
    enterApp(data.user);
  } catch (error) { showToast(error.message); } finally { button.disabled = false; }
});

function enterApp(user) {
  authView.classList.add('hidden');
  appView.classList.remove('hidden');
  document.querySelector('#avatar').textContent = user.name.split(' ').map(part => part[0]).slice(0, 2).join('').toUpperCase();
}

document.querySelector('#logout').addEventListener('click', async () => { await fetch('/api/auth/logout', {method: 'POST'}); document.cookie = 'sift_session=; path=/; max-age=0'; location.reload(); });
const dropZone = document.querySelector('#drop-zone');
const fileInput = document.querySelector('#file-input');
document.querySelector('#browse-button').addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', () => fileInput.files[0] && upload(fileInput.files[0]));
['dragenter', 'dragover'].forEach(eventName => dropZone.addEventListener(eventName, event => { event.preventDefault(); dropZone.classList.add('dragging'); }));
['dragleave', 'drop'].forEach(eventName => dropZone.addEventListener(eventName, event => { event.preventDefault(); dropZone.classList.remove('dragging'); }));
dropZone.addEventListener('drop', event => event.dataTransfer.files[0] && upload(event.dataTransfer.files[0]));

async function upload(file) {
  const formData = new FormData();
  formData.append('file', file);
  dropZone.querySelector('h3').textContent = 'Reading your document...';
  try {
    const response = await fetch('/api/interview/start', { method: 'POST', body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || 'Could not read that document');
    interview = data; questionIndex = 0;
    document.querySelector('#upload-state').classList.add('hidden');
    document.querySelector('#interview-state').classList.remove('hidden');
    document.querySelector('#interview-title').textContent = data.filename.replace(/\.[^/.]+$/, '') || 'A conversation worth having.';
    renderQuestion();
    if (data.mode === 'demo') showToast('Demo questions loaded. Add OPENAI_API_KEY for live generation.');
  } catch (error) { dropZone.querySelector('h3').textContent = 'Drop a resume or portfolio here'; showToast(error.message); }
}

function renderQuestion() {
  const current = interview.questions[questionIndex];
  const number = String(questionIndex + 1).padStart(2, '0');
  document.querySelector('#question-type').textContent = current.difficulty.toUpperCase();
  document.querySelector('#question-index').textContent = number;
  document.querySelector('#question-count').innerHTML = `${number} <i>/</i> ${String(interview.questions.length).padStart(2, '0')}`;
  document.querySelector('#question-text').textContent = current.question;
  document.querySelector('#question-intent').textContent = current.intent;
  document.querySelector('#answer-input').value = '';
  document.querySelector('#progress-bar').style.width = `${((questionIndex + 1) / interview.questions.length) * 100}%`;
  document.querySelector('#next-button').innerHTML = questionIndex === interview.questions.length - 1 ? 'Finish session <span>→</span>' : 'Save & next <span>→</span>';
}

document.querySelector('#next-button').addEventListener('click', async () => {
  const answer = document.querySelector('#answer-input').value.trim();
  if (!answer) { showToast('Add a note before moving on.'); return; }
  await fetch(`/api/interview/${interview.id}/answer`, { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({answer}) });
  if (questionIndex === interview.questions.length - 1) { document.querySelector('#interview-state').classList.add('hidden'); document.querySelector('#complete-state').classList.remove('hidden'); return; }
  questionIndex += 1; renderQuestion();
});
document.querySelector('#new-session').addEventListener('click', () => { document.querySelector('#complete-state').classList.add('hidden'); document.querySelector('#upload-state').classList.remove('hidden'); });

(async function restore() {
  try { const response = await fetch('/api/me'); if (response.ok) enterApp(await response.json()); } catch (_) {}
})();

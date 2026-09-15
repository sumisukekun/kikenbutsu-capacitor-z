const { chromium } = require('playwright');
const path = require('path');

const FILE_URL = 'file://' + path.resolve(__dirname, '..', 'www', 'index.html');
const OUT_DIR = __dirname;

// Seed plausible-looking progress data so screenshots don't show an all-zero
// fresh-install state.
async function seedProgress(page) {
  await page.evaluate(() => {
    const today = new Date();
    const fmt = (d) => {
      const y = d.getFullYear(), m = String(d.getMonth() + 1).padStart(2, '0'), day = String(d.getDate()).padStart(2, '0');
      return `${y}-${m}-${day}`;
    };
    const dailyStats = {};
    for (let i = 0; i < 9; i++) {
      const d = new Date(today);
      d.setDate(d.getDate() - i);
      const answered = 18 + ((i * 7) % 15);
      const correct = Math.max(1, Math.round(answered * (0.68 + (i % 3) * 0.06)));
      dailyStats[fmt(d)] = { answered, correct };
    }
    const perQuestion = {};
    QUESTIONS.forEach((q, idx) => {
      const attempts = 2 + (idx % 4);
      const correct = Math.max(1, attempts - (idx % 3 === 0 ? 1 : 0));
      perQuestion[q.id] = { attempts, correct };
    });
    state.data = {
      dailyStats,
      perQuestion,
      wrongIds: QUESTIONS.slice(0, 5).map((q) => q.id),
      currentStreak: 6,
      bestStreak: 11,
      lapCount: 2,
      seenInLap: QUESTIONS.slice(0, 20).map((q) => q.id),
    };
    state.loading = false;
    render();
  });
}

async function shoot(page, name) {
  await page.screenshot({ path: path.join(OUT_DIR, name) });
  console.log('saved', name);
}

async function captureSet(browser, viewport, prefix, deviceScaleFactor) {
  const page = await browser.newPage({ viewport, deviceScaleFactor });
  await page.goto(FILE_URL, { waitUntil: 'load' });
  await page.waitForTimeout(300);
  await seedProgress(page);
  await page.waitForTimeout(200);

  // 1. Home / dashboard
  await shoot(page, `${prefix}_1_home.png`);

  // 2. Quiz question in progress
  await page.evaluate(() => {
    state.filterSet = 'all';
    state.filterSubject = 'all';
    state.filterCount = 10;
    startSession();
  });
  await page.waitForTimeout(200);
  await shoot(page, `${prefix}_2_quiz.png`);

  // 3. Answer selected -> result / explanation view
  await page.evaluate(async () => {
    const s = state.session;
    const q = s.questions[s.idx];
    s.selected = q.answer; // pick the correct choice for a clean, positive screenshot
    await submitAnswer();
  });
  await page.waitForTimeout(200);
  await shoot(page, `${prefix}_3_result.png`);

  // 4. Study calendar
  await page.evaluate(() => {
    state.view = 'calendar';
    render();
  });
  await page.waitForTimeout(200);
  await shoot(page, `${prefix}_4_calendar.png`);

  await page.close();
}

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });

  // iPhone 6.5" display — 1284x2778 physical px (portrait)
  await captureSet(browser, { width: 428, height: 926 }, 'iphone65', 3);

  // iPad 13" display — 2048x2732 physical px (portrait)
  await captureSet(browser, { width: 1024, height: 1366 }, 'ipad13', 2);

  await browser.close();
  console.log('all screenshots done');
})();

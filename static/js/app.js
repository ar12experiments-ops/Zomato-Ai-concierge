/**
 * Zomato AI Dining Concierge Frontend Logic
 * Luminous Glassmorphic Theme & Intelligent Restaurant Discovery
 */

document.addEventListener('DOMContentLoaded', () => {
  initMetadata();
  initBenchmarks();
  initPresetHandlers();
  initBudgetMatrix();
});

// Update slider visual counter
function updateRatingDisplay(val) {
  document.getElementById('rating-display').innerText = `${parseFloat(val).toFixed(1)} ★`;
}

// Fetch Metadata to populate stats and dropdowns dynamically
async function initMetadata() {
  try {
    const res = await fetch('/api/metadata');
    if (!res.ok) return;
    const data = await res.json();

    // Update Data Source Badge
    const badgeText = document.getElementById('source-badge-text');
    if (badgeText) {
      if (data.supabase_connected) {
        badgeText.innerText = 'LIVE // SUPABASE CLOUD DB ACTIVE';
      } else if (data.data_source === 'supabase') {
        badgeText.innerText = 'SUPABASE CONFIG READY // LOCAL PARQUET SYNCED';
      } else {
        badgeText.innerText = 'DATA SOURCE // LOCAL CACHED INTELLIGENCE';
      }
    }

    // Populate stats
    if (data.total_restaurants) {
      document.getElementById('stat-restaurants').innerText = Number(data.total_restaurants).toLocaleString();
    }
    if (data.total_locations) {
      document.getElementById('stat-locations').innerText = `${data.total_locations}+`;
    }
    if (data.total_cuisines) {
      document.getElementById('stat-cuisines').innerText = `${data.total_cuisines}+`;
    }

    // Populate Location Select
    if (data.locations && data.locations.length > 0) {
      const locSelect = document.getElementById('location-select');
      const currentVal = locSelect.value;
      locSelect.innerHTML = '<option value="">All Neighborhoods / City-wide</option>';
      data.locations.forEach(loc => {
        const opt = document.createElement('option');
        opt.value = loc;
        opt.textContent = loc;
        if (loc === 'Indiranagar' || loc === currentVal) opt.selected = true;
        locSelect.appendChild(opt);
      });
    }

    // Populate Cuisine Select
    if (data.cuisines && data.cuisines.length > 0) {
      const cuiSelect = document.getElementById('cuisine-select');
      cuiSelect.innerHTML = '<option value="">Any Cuisine / Flexible</option>';
      data.cuisines.forEach(cui => {
        const opt = document.createElement('option');
        opt.value = cui;
        opt.textContent = cui;
        cuiSelect.appendChild(opt);
      });
    }
  } catch (err) {
    console.warn('Metadata fetch warning:', err);
  }
}

// Fetch Initial Benchmarks / Top Picks
async function initBenchmarks() {
  const container = document.getElementById('cards-container');
  container.innerHTML = renderSkeletonCards(3);

  try {
    const res = await fetch('/api/benchmark');
    if (!res.ok) throw new Error('Failed to fetch benchmarks');
    const data = await res.json();
    renderCards(data.benchmarks || []);
  } catch (err) {
    console.warn('Benchmark fetch fallback:', err);
    container.innerHTML = `<p style="color:var(--text-secondary); text-align:center; padding:2rem;">Select preferences above and click Discover Restaurants to view recommendations.</p>`;
  }
}

// Handle Experience Presets
function initPresetHandlers() {
  const presetButtons = document.querySelectorAll('.uh-preset-chip');
  const budgetBtns = document.querySelectorAll('.uh-budget-btn');
  const budgetInput = document.getElementById('budget-input');
  const slider = document.getElementById('rating-slider');
  const cuiSelect = document.getElementById('cuisine-select');
  const vibeInput = document.getElementById('vibe-input');

  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      presetButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const preset = btn.dataset.preset;
      if (preset === 'romantic') {
        setBudget('High');
        slider.value = 4.2;
        vibeInput.value = 'Intimate candlelit seating, ambient low lighting, fine wine selection, and exquisite handmade pasta';
        selectCuisineIfAvailable('Italian');
      } else if (preset === 'fastfood') {
        setBudget('Low');
        slider.value = 4.0;
        vibeInput.value = 'Quick service, delicious regional street food, fresh savory snacks, budget friendly';
        selectCuisineIfAvailable('Fast Food');
      } else if (preset === 'family') {
        setBudget('Medium');
        slider.value = 4.0;
        vibeInput.value = 'Spacious seating, family-friendly ambiance, rich North Indian curries, aromatic biryani and buttery naans';
        selectCuisineIfAvailable('North Indian');
      } else if (preset === 'work') {
        setBudget('Medium');
        slider.value = 4.0;
        vibeInput.value = 'Quiet cafe atmosphere, single-origin espresso, high-speed WiFi, artisan croissants and toasties';
        selectCuisineIfAvailable('Cafe');
      } else if (preset === 'brewpub') {
        setBudget('High');
        slider.value = 4.3;
        vibeInput.value = 'Lively open-air rooftop microbrewery, chilled craft beers, wood-fired sourdough pizza, vibrant music';
        selectCuisineIfAvailable('Continental');
      } else {
        setBudget('Any');
        slider.value = 4.0;
        vibeInput.value = '';
      }
      updateRatingDisplay(slider.value);
    });
  });

  function setBudget(val) {
    budgetInput.value = val;
    budgetBtns.forEach(b => {
      b.classList.toggle('active', b.dataset.budget === val);
    });
  }

  function selectCuisineIfAvailable(target) {
    for (let i = 0; i < cuiSelect.options.length; i++) {
      if (cuiSelect.options[i].value.toLowerCase().includes(target.toLowerCase())) {
        cuiSelect.selectedIndex = i;
        break;
      }
    }
  }
}

// Handle Budget Matrix Buttons
function initBudgetMatrix() {
  const budgetBtns = document.querySelectorAll('.uh-budget-btn');
  const budgetInput = document.getElementById('budget-input');

  budgetBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      budgetBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      budgetInput.value = btn.dataset.budget;
    });
  });
}

// Trigger Recommendation Flow
async function triggerRecommendation() {
  const submitBtn = document.getElementById('submit-btn');
  const container = document.getElementById('cards-container');
  const summaryBox = document.getElementById('summary-container');
  const resultsTag = document.getElementById('results-tag');
  const resultsTitle = document.getElementById('results-title');

  // Collect Payload
  const location = document.getElementById('location-select').value;
  const budget = document.getElementById('budget-input').value;
  const rating = parseFloat(document.getElementById('rating-slider').value);
  const cuisine = document.getElementById('cuisine-select').value;
  const vibe = document.getElementById('vibe-input').value;

  const payload = {
    location: location || 'Bangalore',
    budget: budget,
    cuisines: cuisine ? [cuisine] : [],
    min_rating: rating,
    additional_preferences: vibe,
  };

  // UI Loading State
  submitBtn.disabled = true;
  submitBtn.innerHTML = `<span>⏳ CURATING RESTAURANT PICKS...</span>`;
  container.innerHTML = renderSkeletonCards(3);
  summaryBox.style.display = 'none';

  // Smooth scroll to results
  document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });

  try {
    const res = await fetch('/api/recommend', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: Failed to get recommendations`);
    }

    const data = await res.json();

    // Render Summary
    if (data.summary) {
      summaryBox.innerHTML = `
        <div class="uh-summary-box">
          <div class="uh-summary-heading">
            <span>✨ AI DINING SUMMARY</span>
          </div>
          <p class="uh-summary-body">${escapeHtml(data.summary)}</p>
          ${data.relaxed_filters_applied && data.relaxation_note ? `<p style="color:var(--zomato-red); font-family:var(--font-mono); font-size:0.8rem; margin-top:0.6rem; font-weight:600;">ℹ️ CONCIERGE NOTE: ${escapeHtml(data.relaxation_note)}</p>` : ''}
        </div>
      `;
      summaryBox.style.display = 'block';
    }

    resultsTag.innerText = `CURATED MATCHES // AI SELECTION`;
    resultsTitle.innerText = `TOP ${data.recommendations.length} MATCHING RESTAURANTS`;

    renderCards(data.recommendations || []);

  } catch (err) {
    console.error('Recommendation error:', err);
    container.innerHTML = `
      <div class="uh-summary-box" style="border-left-color: var(--zomato-red);">
        <div class="uh-summary-heading" style="color:var(--zomato-red);">⚠️ NOTICE</div>
        <p class="uh-summary-body">Unable to find restaurants matching all strict constraints. Please try broadening your neighborhood or budget options.</p>
      </div>
    `;
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = `<span>✨ DISCOVER RESTAURANTS WITH AI</span>`;
  }
}

// Render Restaurant Cards
function renderCards(cards) {
  const container = document.getElementById('cards-container');
  if (!cards || cards.length === 0) {
    container.innerHTML = `<p style="color:var(--text-secondary); text-align:center; padding:2rem;">No matching restaurant records found.</p>`;
    return;
  }

  container.innerHTML = cards.map(rec => {
    const cuisinesHtml = (Array.isArray(rec.cuisine) ? rec.cuisine : [rec.cuisine])
      .map(c => `<span class="uh-cuisine-tag">${escapeHtml(c)}</span>`)
      .join('');

    const tagsHtml = (Array.isArray(rec.highlight_tags) ? rec.highlight_tags : [])
      .map(t => `<span class="uh-highlight-chip">✨ ${escapeHtml(t)}</span>`)
      .join('');

    const ratingVal = Number(rec.rating || 4.0).toFixed(1);
    const costVal = Number(rec.estimated_cost_for_two || 600).toLocaleString();

    return `
      <article class="uh-card">
        <div class="uh-card-top">
          <div>
            <div class="uh-rank-spec">
              <span>#${String(rec.rank).padStart(2, '0')} // RECOMMENDED MATCH</span>
            </div>
            <h3 class="uh-card-name">${escapeHtml(rec.restaurant_name)}</h3>
            <div class="uh-card-locality">
              <span>📍</span> ${escapeHtml(rec.location)}
            </div>
          </div>
          <div style="text-align: right; flex-shrink: 0;">
            <div class="uh-rating-badge">
              ★ ${ratingVal}
            </div>
            <div class="uh-cost-tag">
              ₹${costVal} FOR TWO
            </div>
          </div>
        </div>

        <div class="uh-cuisines-row">
          ${cuisinesHtml}
        </div>

        <div class="uh-verdict-card">
          <div class="uh-verdict-tag">
            <span>💡 WHY WE RECOMMEND THIS</span>
          </div>
          <p class="uh-verdict-desc">${escapeHtml(rec.explanation)}</p>
        </div>

        <div class="uh-tags-row">
          ${tagsHtml}
        </div>
      </article>
    `;
  }).join('');
}

// Skeleton Loading Cards
function renderSkeletonCards(count) {
  return Array(count).fill(0).map(() => `
    <div class="uh-card" style="opacity: 0.6;">
      <div class="uh-skeleton" style="width: 140px; height: 20px; margin-bottom: 1rem;"></div>
      <div class="uh-skeleton" style="width: 60%; height: 32px; margin-bottom: 0.75rem;"></div>
      <div class="uh-skeleton" style="width: 40%; height: 18px; margin-bottom: 1.5rem;"></div>
      <div class="uh-skeleton" style="width: 100%; height: 75px; margin-bottom: 1rem;"></div>
      <div style="display: flex; gap: 8px;">
        <div class="uh-skeleton" style="width: 90px; height: 26px;"></div>
        <div class="uh-skeleton" style="width: 90px; height: 26px;"></div>
      </div>
    </div>
  `).join('');
}

// Utility: Escape HTML
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}


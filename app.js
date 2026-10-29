(() => {
  "use strict";

  const RECIPES = window.RECIPES || [];
  const INGREDIENTS = window.INGREDIENTS || {};
  const APP_VERSION = window.APP_VERSION || "2.1.0";
  const COUNTRIES = [
    { id: "all", name: "Все страны" },
    { id: "eg", name: "Египет" },
    { id: "lb", name: "Ливан" },
    { id: "sy", name: "Сирия" },
    { id: "tr", name: "Турция" },
    { id: "ps", name: "Палестина" },
  ];
  const STORAGE_KEY = "egypt-recipes-v1";
  let selectedCountry = "all";
  const CHECK_SVG =
    '<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M4.2 10.5l3.4 3.4L15.9 5.6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  const ALT_SVG =
    '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 7h11l-3-3M17 17H6l3 3" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  const main = document.getElementById("main");
  const toast = document.getElementById("toast");
  const ingredientModal = document.getElementById("ingredient-modal");
  const ingredientModalContent = document.getElementById("ingredient-modal-content");
  document.querySelectorAll("[data-app-version]").forEach((node) => { node.textContent = `v${APP_VERSION}`; });

  let memoryStore = {};
  let appState = readState();

  function readState() {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : {};
    } catch (error) {
      return memoryStore;
    }
  }

  function writeState() {
    memoryStore = appState;
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(appState));
    } catch (error) {
      /* localStorage may be unavailable in some file:// contexts. */
    }
  }

  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => {
      const map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      };
      return map[char];
    });
  }

  function selectedFor(recipeId, section) {
    if (!appState[recipeId]) appState[recipeId] = {};
    if (!Array.isArray(appState[recipeId][section])) appState[recipeId][section] = [];
    return appState[recipeId][section];
  }

  function isDone(recipeId, section, index) {
    return selectedFor(recipeId, section).includes(index);
  }

  function toggleMark(recipeId, section, index) {
    const selected = selectedFor(recipeId, section);
    const position = selected.indexOf(index);
    if (position >= 0) selected.splice(position, 1);
    else selected.push(index);
    writeState();
  }

  function getRecipe(id) {
    return RECIPES.find((recipe) => recipe.id === id);
  }

  function plural(number, forms) {
    const value = Math.abs(number) % 100;
    const last = value % 10;
    if (value > 10 && value < 20) return forms[2];
    if (last > 1 && last < 5) return forms[1];
    if (last === 1) return forms[0];
    return forms[2];
  }

  function countryCount(id) {
    return id === "all" ? RECIPES.length : RECIPES.filter((recipe) => recipe.country === id).length;
  }

  function countryName(id) {
    return COUNTRIES.find((country) => country.id === id)?.name || "Все кухни";
  }

  function filteredRecipes() {
    return selectedCountry === "all"
      ? RECIPES
      : RECIPES.filter((recipe) => recipe.country === selectedCountry);
  }

  function firstSentence(text) {
    const match = String(text).match(/^.*?[.!?](?=\s+[А-ЯЁA-Z«"(]|\s*$)/);
    return (match ? match[0] : String(text)).trim();
  }

  function normalizeIngredientName(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/[«».,()]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function ingredientInfoFor(name) {
    const normalized = normalizeIngredientName(name);
    if (INGREDIENTS[normalized]) return { key: normalized, info: INGREDIENTS[normalized] };
    const key = Object.keys(INGREDIENTS)
      .sort((a, b) => b.length - a.length)
      .find((candidate) => normalized.includes(candidate));
    return key ? { key, info: INGREDIENTS[key] } : null;
  }

  function getReplacement(recipeId, index) {
    return appState[recipeId]?.replacements?.[index] || null;
  }

  function setReplacement(recipeId, index, replacement) {
    if (!appState[recipeId]) appState[recipeId] = {};
    if (!appState[recipeId].replacements) appState[recipeId].replacements = {};
    if (replacement) appState[recipeId].replacements[index] = replacement;
    else delete appState[recipeId].replacements[index];
    writeState();
  }

  function openIngredientModal(key) {
    const info = INGREDIENTS[key];
    if (!info || !ingredientModal || !ingredientModalContent) return;
    const alternatives = (info.alternatives || [])
      .map(
        (alternative) => `
          <div class="modal-alt-item">
            <strong>${esc(alternative.name)}</strong>
            <span>${Number(alternative.similarity)}%</span>
          </div>`
      )
      .join("");
    ingredientModalContent.innerHTML = `
      <span class="ingredient-modal-kicker">Ингредиент</span>
      <h2 id="ingredient-modal-title">${esc(info.title)}</h2>
      <p>${esc(info.what)}</p>
      <h3>Как подготовить</h3>
      <ul>${(info.howTo || []).map((line) => `<li>${esc(line)}</li>`).join("")}</ul>
      <h3>Чем заменить</h3>
      <div class="modal-alt-list">${alternatives}</div>
    `;
    ingredientModal.hidden = false;
    document.body.classList.add("modal-open");
    ingredientModal.querySelector(".ingredient-modal-close")?.focus();
  }

  function closeIngredientModal() {
    if (!ingredientModal) return;
    ingredientModal.hidden = true;
    document.body.classList.remove("modal-open");
  }

  function dishCardsMarkup(recipes) {
    return recipes
      .map(
        (recipe) => `
          <a class="dish-card" href="#/recipe/${esc(recipe.id)}" style="--card-accent:${recipe.accent}">
            <div class="dish-media">
              <img src="${esc(recipe.photo)}" alt="${esc(recipe.title)}" loading="lazy">
              <span class="dish-index">${esc(recipe.num)}</span>
            </div>
            <div class="dish-body">
              <span class="dish-kicker">${esc(recipe.country_name)} • ${esc(recipe.meta.cook)}</span>
              <h3>${esc(recipe.title)}</h3>
              <p>${esc(recipe.tagline)}</p>
              <div class="dish-footer">
                <span>${esc(recipe.meta.portions)}</span>
                <span>PDF-гид</span>
              </div>
            </div>
          </a>`
      )
      .join("");
  }

  function countryCardsMarkup() {
    return COUNTRIES.map((country) => {
      const active = country.id === selectedCountry;
      const count = countryCount(country.id);
      return `
        <button class="country-card${active ? " is-active" : ""}" type="button" data-country="${country.id}" aria-pressed="${active}">
          <span class="country-name">${esc(country.name)}</span>
          <span class="country-meta">${count} ${plural(count, ["блюдо", "блюда", "блюд"])}</span>
          <span class="country-mark">${active ? "Выбрано" : ""}</span>
        </button>`;
    }).join("");
  }

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add("is-visible");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => {
      toast.classList.remove("is-visible");
    }, 2600);
  }

  function renderHome() {
    document.title = "Вкус Ближнего Востока — рецепты для Санкт-Петербурга";

    const visibleRecipes = filteredRecipes();
    const cards = dishCardsMarkup(visibleRecipes);
    const cuisines = new Set(RECIPES.map((recipe) => recipe.country)).size;

    main.innerHTML = `
      <section class="hero">
        <div>
          <span class="eyebrow">Ближний Восток • Санкт-Петербург</span>
          <h1>Вкус<br><em>Ближнего Востока</em><br>без лишней суеты.</h1>
          <p class="hero-lede">
            ${RECIPES.length} блюд из пяти кухонь: от египетского кошари и ливанского хумуса
            до турецкого менемена и палестинской шакшуки. Выбирайте страну, отмечайте покупки и шаги.
          </p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="#dishes">Выбрать блюдо</a>
            <span class="hero-note">Все рецепты — с покупками<br>в Петербурге и PDF-гидами.</span>
          </div>
        </div>
        <aside class="hero-card" aria-label="Коротко о подборке">
          <div>
            <span class="hc-kicker">Сегодня на кухне</span>
            <div class="hc-title">Ближний<br>Восток</div>
            <p class="hc-text">Уличная еда, домашние запеканки, дипы и супы, которые пахнут специями.</p>
          </div>
          <div class="hc-stats">
            <div><strong>${RECIPES.length}</strong><span>блюд</span></div>
            <div><strong>${cuisines}</strong><span>кухонь</span></div>
            <div><strong>3</strong><span>вкладки</span></div>
          </div>
        </aside>
      </section>

      <section class="section" id="countries" aria-labelledby="countries-title">
        <div class="section-head">
          <div>
            <span class="eyebrow">Шаг 1</span>
            <h2 id="countries-title">Выберите кухню</h2>
          </div>
          <p>Египет, Ливан, Сирия, Турция и Палестина. Все продукты — из обычных магазинов и восточных лавок Петербурга.</p>
        </div>
        <div class="country-grid" id="country-grid">${countryCardsMarkup()}</div>
      </section>

      <section class="section" id="dishes" aria-labelledby="dishes-title">
        <div class="section-head">
          <div>
            <span class="eyebrow" id="dish-section-kicker">${esc(countryName(selectedCountry))} • ${visibleRecipes.length} ${plural(visibleRecipes.length, ["блюдо", "блюда", "блюд"])}</span>
            <h2 id="dishes-title">Выберите блюдо</h2>
          </div>
          <p>Нажмите на карточку — откроется описание, ингредиенты, подготовка и готовка.</p>
        </div>
        <div class="dish-grid" id="dish-grid">${cards}</div>
      </section>
    `;
  }

  function updateCountrySelection(countryId) {
    if (!COUNTRIES.some((country) => country.id === countryId)) return;
    selectedCountry = countryId;

    document.querySelectorAll(".country-card[data-country]").forEach((card) => {
      const active = card.dataset.country === selectedCountry;
      card.classList.toggle("is-active", active);
      card.setAttribute("aria-pressed", String(active));
      const mark = card.querySelector(".country-mark");
      if (mark) mark.textContent = active ? "Выбрано" : "";
    });

    const visibleRecipes = filteredRecipes();
    const grid = document.getElementById("dish-grid");
    const kicker = document.getElementById("dish-section-kicker");
    if (grid) grid.innerHTML = dishCardsMarkup(visibleRecipes);
    if (kicker) {
      kicker.textContent = `${countryName(selectedCountry)} • ${visibleRecipes.length} ${plural(visibleRecipes.length, ["блюдо", "блюда", "блюд"])}`;
    }
    const dishes = document.getElementById("dishes");
    if (dishes) dishes.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function sectionData(recipe) {
    return [
      {
        key: "ingredients",
        kicker: "Что купить",
        title: "Ингредиенты",
        subtitle: "Нажмите на продукт, когда он куплен или уже есть дома.",
        items: recipe.ingredients.map((item, index) => ({
          index,
          title: item.name,
          amount: item.amount,
          note: item.note,
          doneLabel: "Куплено",
        })),
      },
      {
        key: "prep",
        kicker: "Что сделать заранее",
        title: "Подготовка",
        subtitle: "Помыть, нарезать, отмерить и разложить. Это экономит нервы у плиты.",
        items: recipe.prep.map((item, index) => ({
          index,
          title: item.title,
          note: item.text,
          doneLabel: "Готово",
        })),
      },
      {
        key: "steps",
        kicker: "30–100%",
        title: "Готовим",
        subtitle: "Шесть ключевых остановок. Полный гид из 11 шагов — в PDF.",
        items: recipe.stages
          .slice(3)
          .filter((_, index) => [0, 1, 2, 3, 5, 7].includes(index))
          .map((stage, index) => ({
            index,
            percent: stage.percent,
            title: stage.title,
            note: firstSentence(stage.text),
            doneLabel: "Сделано",
          })),
      },
    ];
  }

  function alternativeMenuMarkup(item, infoEntry, replacement) {
    const alternatives = infoEntry.info.alternatives || [];
    if (!alternatives.length) return "";
    return `
      <div class="alt-menu" data-alt-menu hidden>
        <span class="alt-menu-title">Заменить «${esc(item.title)}»</span>
        ${alternatives
          .map(
            (alternative, index) => `
              <button class="alt-option" type="button" data-alt-index="${index}">
                <span class="alt-name">${esc(alternative.name)}</span>
                <span class="alt-score">${Number(alternative.similarity)}%</span>
                <span class="alt-note">${esc(alternative.note || "")}</span>
              </button>`
          )
          .join("")}
        ${replacement ? '<button class="alt-reset" type="button" data-alt-reset>Вернуть оригинал</button>' : ""}
      </div>
    `;
  }

  function ingredientItemMarkup(recipe, item) {
    const done = isDone(recipe.id, "ingredients", item.index);
    const status = done ? item.doneLabel : "Отметить";
    const infoEntry = ingredientInfoFor(item.title);
    const replacement = getReplacement(recipe.id, item.index);
    const title = replacement ? replacement.name : item.title;
    const amount = replacement ? replacement.amount : item.amount;
    const note = replacement
      ? `Заменяет: ${item.title}.${replacement.note ? " " + replacement.note : ""}`
      : item.note;
    const titleMarkup =
      infoEntry && !replacement
        ? `<span class="item-info-link" data-info-link data-info-key="${esc(infoEntry.key)}" role="button" tabindex="0">${esc(title)}</span>`
        : esc(title);
    const amountMarkup = amount ? `<span class="item-amount">${esc(amount)}</span>` : "";
    const noteMarkup = note ? `<span class="item-note">${esc(note)}</span>` : "";
    const altButton =
      infoEntry && infoEntry.info.alternatives?.length
        ? `<button class="alt-toggle" type="button" data-alt-toggle aria-label="Показать альтернативы" aria-expanded="false">${ALT_SVG}</button>`
        : "";

    return `
      <div
        class="item${done ? " is-done" : ""}"
        data-toggle-item
        data-section="ingredients"
        data-index="${item.index}"
        data-done-label="${esc(item.doneLabel)}"
        ${infoEntry ? `data-info-key="${esc(infoEntry.key)}"` : ""}
        role="button"
        tabindex="0"
        aria-pressed="${done}"
      >
        <span class="item-check" aria-hidden="true">${CHECK_SVG}</span>
        <span class="item-content">
          <span class="item-title">${titleMarkup}${amountMarkup}</span>
          ${noteMarkup}
        </span>
        <span class="item-tools">
          <span class="item-status">${esc(status)}</span>
          ${altButton}
        </span>
        ${infoEntry ? alternativeMenuMarkup(item, infoEntry, replacement) : ""}
      </div>
    `;
  }

  function itemMarkup(recipe, section, item) {
    if (section.key === "ingredients") return ingredientItemMarkup(recipe, item);

    const done = isDone(recipe.id, section.key, item.index);
    const status = done ? item.doneLabel : "Отметить";
    const percent = item.percent ? `<span class="item-percent">${esc(item.percent)}</span>` : "";
    const amount = item.amount ? `<span class="item-amount">${esc(item.amount)}</span>` : "";
    const note = item.note ? `<span class="item-note">${esc(item.note)}</span>` : "";

    return `
      <button
        class="item${done ? " is-done" : ""}"
        type="button"
        data-toggle-item
        data-section="${esc(section.key)}"
        data-index="${item.index}"
        data-done-label="${esc(item.doneLabel)}"
        aria-pressed="${done}"
      >
        <span class="item-check" aria-hidden="true">${CHECK_SVG}</span>
        <span class="item-content">
          <span class="item-title">${percent}${esc(item.title)}${amount}</span>
          ${note}
        </span>
        <span class="item-tools">
          <span class="item-status">${esc(status)}</span>
        </span>
      </button>
    `;
  }

  function refreshIngredientItem(recipe, index) {
    const node = document.querySelector(`[data-toggle-item][data-section="ingredients"][data-index="${index}"]`);
    const ingredient = recipe.ingredients[index];
    if (!node || !ingredient) return;
    const wrapper = document.createElement("div");
    wrapper.innerHTML = ingredientItemMarkup(recipe, {
      index,
      title: ingredient.name,
      amount: ingredient.amount,
      note: ingredient.note,
      doneLabel: "Куплено",
    });
    node.replaceWith(wrapper.firstElementChild);
  }

  function closeAltMenus(except = null) {
    document.querySelectorAll("[data-alt-menu]").forEach((menu) => {
      if (menu !== except) {
        menu.hidden = true;
        const toggle = menu.closest("[data-toggle-item]")?.querySelector("[data-alt-toggle]");
        if (toggle) toggle.setAttribute("aria-expanded", "false");
      }
    });
  }

  function accordionMarkup(recipe, section, position) {
    const open = position === 0;
    const doneCount = section.items.filter((item) => isDone(recipe.id, section.key, item.index)).length;
    const total = section.items.length;
    const items = section.items.map((item) => itemMarkup(recipe, section, item)).join("");

    return `
      <section class="accordion${open ? " is-open" : ""}" data-section="${esc(section.key)}">
        <button
          class="accordion-trigger"
          type="button"
          data-accordion-trigger
          aria-expanded="${open}"
          aria-controls="panel-${esc(section.key)}"
        >
          <span class="acc-index">${String(position + 1).padStart(2, "0")}</span>
          <span class="acc-main">
            <span class="acc-kicker">${esc(section.kicker)}</span>
            <span class="acc-title">${esc(section.title)}</span>
          </span>
          <span class="acc-count">${doneCount}/${total}</span>
          <span class="acc-chevron" aria-hidden="true"></span>
        </button>
        <div class="accordion-panel" id="panel-${esc(section.key)}" aria-hidden="${!open}">
          <div class="item-list">${items}</div>
        </div>
      </section>
    `;
  }

  function renderDetail(id) {
    const recipe = getRecipe(id);
    if (!recipe) {
      window.location.hash = "#/";
      return;
    }

    document.title = `${recipe.title} — Вкус Ближнего Востока`;
    const sections = sectionData(recipe);
    const source = recipe.photoSource
      ? `<a href="${esc(recipe.photoSource)}" target="_blank" rel="noopener">Источник фото</a>`
      : "";

    main.innerHTML = `
      <div class="detail-page" style="--accent:${recipe.accent};--accent-dark:${recipe.accent_dark};--accent-light:${recipe.accent_light}">
        <a class="back-link" href="#/">Все блюда</a>

        <section class="detail-hero" aria-labelledby="dish-title">
          <img src="${esc(recipe.photo)}" alt="${esc(recipe.title)}">
          <div class="detail-hero-content">
            <div class="detail-kicker">
              <span class="dot" aria-hidden="true"></span>
              Блюдо ${esc(recipe.num)} • ${esc(recipe.country_name)}
            </div>
            <h1 class="detail-title" id="dish-title">${esc(recipe.title)}</h1>
            <p class="detail-subtitle">${esc(recipe.subtitle)}</p>
            <div class="detail-chips">
              <span class="chip">${esc(recipe.country_name)}</span>
              <span class="chip">${esc(recipe.meta.portions)}</span>
              <span class="chip">Подготовка: ${esc(recipe.meta.prep)}</span>
              <span class="chip">Готовка: ${esc(recipe.meta.cook)}</span>
              <span class="chip">${esc(recipe.meta.difficulty)}</span>
            </div>
            <div class="detail-actions">
              <a class="btn btn-light" href="${esc(recipe.pdfPath)}" download>Скачать PDF</a>
              <a class="btn btn-ghost" href="#ingredients-panel">К ингредиентам</a>
            </div>
            <div class="scroll-hint" aria-hidden="true">
              <span>Описание → 3 вкладки</span>
              <i></i>
            </div>
          </div>
        </section>

        <div class="detail-body">
          <div class="detail-main">
            <section class="description-card">
              <span class="eyebrow">Что это</span>
              <h2>Коротко о блюде</h2>
              <p>${esc(recipe.description)}</p>
              <div class="why-grid">
                ${recipe.why.map((item) => `<div class="why-item">${esc(item)}</div>`).join("")}
              </div>
            </section>

            <div class="steps-heading">
              <div>
                <span class="eyebrow">Три вкладки</span>
                <h2>Соберите ужин по шагам</h2>
              </div>
              <p>Нажимайте на пункты — они закрашиваются зелёным. Повторное нажатие снимает отметку.</p>
            </div>

            <div class="accordions" id="ingredients-panel">
              ${sections.map((section, index) => accordionMarkup(recipe, section, index)).join("")}
            </div>
          </div>

          <aside class="detail-side" aria-label="Прогресс и PDF">
            <div class="side-card">
              <div class="side-kicker">Твой прогресс</div>
              <div class="progress-top">
                <strong class="progress-percent">0%</strong>
                <span class="progress-copy">0 отмечено</span>
              </div>
              <div class="progress-track" role="progressbar" aria-label="Готовность блюда" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0">
                <div class="progress-fill"></div>
              </div>
              <p class="side-note">Отмечайте покупки, подготовку и шаги. Отметки сохраняются в этом браузере.</p>
              <button class="reset-btn" type="button" data-reset-recipe>Сбросить отметки</button>
            </div>

            <div class="side-card pdf-card">
              <div class="side-kicker">PDF-гид</div>
              <h3>Полный гид 0–100</h3>
              <p>Покупки в Петербурге, подготовка, 11 шагов, подача и разбор ошибок. Без воды.</p>
              <a class="btn btn-primary btn-block" href="${esc(recipe.pdfPath)}" download>Скачать PDF</a>
            </div>

            <p class="photo-credit">${esc(recipe.photo_credit)} ${source}</p>
          </aside>
        </div>
      </div>
    `;

    refreshProgress(recipe, true);
  }

  function refreshProgress(recipe, silent = false) {
    const items = Array.from(document.querySelectorAll("[data-toggle-item]"));
    const done = items.filter((item) => item.classList.contains("is-done")).length;
    const total = items.length;
    const percent = total ? Math.round((done / total) * 100) : 0;

    document.querySelectorAll(".accordion").forEach((accordion) => {
      const visible = Array.from(accordion.querySelectorAll("[data-toggle-item]"));
      const selected = visible.filter((item) => item.classList.contains("is-done")).length;
      const count = accordion.querySelector(".acc-count");
      if (count) count.textContent = `${selected}/${visible.length}`;
    });

    const percentNode = document.querySelector(".progress-percent");
    const copyNode = document.querySelector(".progress-copy");
    const fillNode = document.querySelector(".progress-fill");
    const trackNode = document.querySelector(".progress-track");
    if (percentNode) percentNode.textContent = `${percent}%`;
    if (copyNode) copyNode.textContent = `${done} из ${total} отмечено`;
    if (fillNode) fillNode.style.width = `${percent}%`;
    if (trackNode) trackNode.setAttribute("aria-valuenow", String(percent));

    const page = document.querySelector(".detail-page");
    if (page) {
      if (total > 0 && done === total) {
        if (!silent && page.dataset.completed !== "1") {
          showToast("Всё отмечено. Можно готовить.");
        }
        page.dataset.completed = "1";
      } else {
        delete page.dataset.completed;
      }
    }
  }

  function setAccordion(accordion, open) {
    accordion.classList.toggle("is-open", open);
    const trigger = accordion.querySelector("[data-accordion-trigger]");
    const panel = accordion.querySelector(".accordion-panel");
    if (trigger) trigger.setAttribute("aria-expanded", String(open));
    if (panel) panel.setAttribute("aria-hidden", String(!open));
  }

  function route() {
    const hash = window.location.hash || "#/";
    const match = hash.match(/^#\/recipe\/([^/?#]+)/);
    if (match) {
      renderDetail(decodeURIComponent(match[1]));
    } else {
      renderHome();
    }
    window.scrollTo({ top: 0, left: 0, behavior: "auto" });
  }

  document.addEventListener("click", (event) => {
    const closeModal = event.target.closest("[data-close-ingredient]");
    if (closeModal) {
      closeIngredientModal();
      return;
    }

    const infoLink = event.target.closest("[data-info-link]");
    if (infoLink) {
      event.preventDefault();
      closeAltMenus();
      openIngredientModal(infoLink.dataset.infoKey);
      return;
    }

    const altToggle = event.target.closest("[data-alt-toggle]");
    if (altToggle) {
      event.preventDefault();
      const item = altToggle.closest("[data-toggle-item]");
      const menu = item?.querySelector("[data-alt-menu]");
      if (menu) {
        const open = menu.hidden;
        closeAltMenus(menu);
        menu.hidden = !open;
        altToggle.setAttribute("aria-expanded", String(open));
      }
      return;
    }

    const altOption = event.target.closest("[data-alt-index]");
    if (altOption) {
      event.preventDefault();
      const item = altOption.closest("[data-toggle-item]");
      const recipe = getRecipe(getRecipeIdFromHash());
      if (!item || !recipe) return;
      const info = INGREDIENTS[item.dataset.infoKey];
      const alternative = info?.alternatives?.[Number(altOption.dataset.altIndex)];
      if (!alternative) return;
      setReplacement(recipe.id, Number(item.dataset.index), alternative);
      refreshIngredientItem(recipe, Number(item.dataset.index));
      showToast(`Заменено: ${alternative.name}`);
      return;
    }

    const altReset = event.target.closest("[data-alt-reset]");
    if (altReset) {
      event.preventDefault();
      const item = altReset.closest("[data-toggle-item]");
      const recipe = getRecipe(getRecipeIdFromHash());
      if (!item || !recipe) return;
      setReplacement(recipe.id, Number(item.dataset.index), null);
      refreshIngredientItem(recipe, Number(item.dataset.index));
      showToast("Возвращён исходный ингредиент.");
      return;
    }

    const trigger = event.target.closest("[data-accordion-trigger]");
    if (trigger) {
      event.preventDefault();
      const accordion = trigger.closest(".accordion");
      if (!accordion) return;
      const open = !accordion.classList.contains("is-open");
      setAccordion(accordion, open);
      return;
    }

    const item = event.target.closest("[data-toggle-item]");
    if (item) {
      event.preventDefault();
      const recipeId = getRecipeIdFromHash();
      const recipe = getRecipe(recipeId);
      if (!recipe) return;

      const section = item.dataset.section;
      const index = Number(item.dataset.index);
      const done = !item.classList.contains("is-done");
      toggleMark(recipe.id, section, index);
      item.classList.toggle("is-done", done);
      item.setAttribute("aria-pressed", String(done));
      const status = item.querySelector(".item-status");
      if (status) status.textContent = done ? item.dataset.doneLabel : "Отметить";
      refreshProgress(recipe);
      return;
    }

    const reset = event.target.closest("[data-reset-recipe]");
    if (reset) {
      event.preventDefault();
      const recipeId = getRecipeIdFromHash();
      const recipe = getRecipe(recipeId);
      if (!recipe) return;
      if (window.confirm(`Сбросить все отметки для блюда «${recipe.title}»?`)) {
        delete appState[recipe.id];
        writeState();
        renderDetail(recipe.id);
        showToast("Отметки сброшены.");
      }
      return;
    }

    const country = event.target.closest("[data-country]");
    if (country && country.dataset.country) {
      updateCountrySelection(country.dataset.country);
      return;
    }

    const accordionLink = event.target.closest('a[href="#ingredients-panel"]');
    if (accordionLink) {
      event.preventDefault();
      const accordions = document.querySelector(".accordions");
      if (accordions) accordions.scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }

    closeAltMenus();
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeIngredientModal();
      closeAltMenus();
      return;
    }

    const infoLink = event.target.closest("[data-info-link]");
    if (infoLink && (event.key === "Enter" || event.key === " ")) {
      event.preventDefault();
      openIngredientModal(infoLink.dataset.infoKey);
      return;
    }

    const item = event.target.closest("[data-toggle-item]");
    if (item && (event.key === "Enter" || event.key === " ") && !event.target.closest("button, [data-info-link]")) {
      event.preventDefault();
      item.click();
    }
  });

  function getRecipeIdFromHash() {
    const match = (window.location.hash || "").match(/^#\/recipe\/([^/?#]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  window.addEventListener("hashchange", route);
  window.addEventListener("DOMContentLoaded", route);

  if (document.readyState === "loading") {
    // DOMContentLoaded will call route.
  } else {
    route();
  }
})();

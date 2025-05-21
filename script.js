// script.js (Realmente, Realmente COMPLETO - v3 - Com todas as funções preenchidas)
document.addEventListener('DOMContentLoaded', () => {
    console.log("SCRIPT.JS: DOMContentLoaded - v3 - Funções Completas e Boas-Vindas Revisada.");
    const domContentLoadedTimestamp = Date.now();

    // --- Constantes de Tempo da Splash Screen ---
    const SPLASH_LOGO_ANIM_MAX_DELAY = 1300; 
    const SPLASH_LOGO_ANIM_DURATION = 600;
    const SPLASH_TEXT_ANIM_DELAY = 2200;
    const SPLASH_TEXT_ANIM_DURATION = 1000;
    const SPLASH_PROGRESS_BAR_START_DELAY = 2500;
    const SPLASH_PROGRESS_BAR_FILL_DURATION = 3000;
    const APPROX_TOTAL_CSS_ANIM_DURATION = Math.max(
        SPLASH_LOGO_ANIM_MAX_DELAY + SPLASH_LOGO_ANIM_DURATION,
        SPLASH_TEXT_ANIM_DELAY + SPLASH_TEXT_ANIM_DURATION,
        SPLASH_PROGRESS_BAR_START_DELAY + SPLASH_PROGRESS_BAR_FILL_DURATION
    );
    const SPLASH_MINIMUM_VISIBLE_TIME = APPROX_TOTAL_CSS_ANIM_DURATION + 1000;

    // --- Seletores de Elementos DOM ---
    const inclusiveWelcomeScreen = document.getElementById('inclusive-welcome-screen');
    const activateVoiceGuideBtn = document.getElementById('welcome-voice-yes-btn');
    const declineVoiceGuideBtn = document.getElementById('welcome-voice-no-btn');
    const mainSplashScreen = document.getElementById('accessible-splash-screen'); 

    const appContent = document.getElementById('app-content');
    const currentYearSpan = document.getElementById('current-year');
    const voiceCommandBtn = document.getElementById('voice-command-btn');
    const voiceBtnText = voiceCommandBtn ? voiceCommandBtn.querySelector('.voice-btn-text') : null;
    const voiceBtnIcon = voiceCommandBtn ? voiceCommandBtn.querySelector('i') : null;
    
    const navDashboardBtn = document.getElementById('nav-dashboard-btn');
    const navMyGamesBtn = document.getElementById('nav-my-games-btn');
    const navPoolsBtn = document.getElementById('nav-pools-btn');
    const mainNav = document.getElementById('main-nav');
    const dashboardSection = document.getElementById('dashboard-section');
    const myGamesSection = document.getElementById('my-games-section');
    const poolsSection = document.getElementById('pools-section');
    const mainSections = document.querySelectorAll('.main-section');
    
    const statsJogosGeradosSpan = document.getElementById('stats-jogos-gerados');
    const statsJogosPremiadosSpan = document.getElementById('stats-jogos-premiados');
    const statsValorPremiosSpan = document.getElementById('stats-valor-premios');
    const recentPoolsList = document.getElementById('recent-pools-list');
    const topWinnersList = document.getElementById('top-winners-list');
    
    const quickHunchLotteryTypeSelect = document.getElementById('quick-hunch-lottery-type');
    const generateQuickHunchBtn = document.getElementById('generate-quick-hunch-btn');
    const quickHunchOutputDiv = document.getElementById('quick-hunch-output');
    const quickHunchNumbersDiv = document.getElementById('quick-hunch-numbers');
    const quickHunchStrategyP = document.getElementById('quick-hunch-strategy');
    const saveQuickHunchBtn = document.getElementById('save-quick-hunch-btn');
    const checkQuickHunchBtn = document.getElementById('check-quick-hunch-btn');
    const quickHunchCheckResultDiv = document.getElementById('quick-hunch-check-result');
    
    const hotNumbersLotteryTypeSelect = document.getElementById('hot-numbers-lottery-type');
    const hotNumbersAnalyzeCountInput = document.getElementById('hot-numbers-analyze-count');
    const generateHotNumbersHunchBtn = document.getElementById('generate-hot-numbers-hunch-btn');
    const hotNumbersHunchOutputDiv = document.getElementById('hot-numbers-hunch-output');
    const hotNumbersHunchNumbersDiv = document.getElementById('hot-numbers-hunch-numbers');
    const hotNumbersHunchStrategyP = document.getElementById('hot-numbers-hunch-strategy');
    const saveHotHunchBtn = document.getElementById('save-hot-hunch-btn');
    const checkHotHunchBtn = document.getElementById('check-hot-hunch-btn');
    const hotHunchCheckResultDiv = document.getElementById('hot-hunch-check-result');
    
    const esotericLotteryTypeSelect = document.getElementById('esoteric-lottery-type');
    const birthDateInput = document.getElementById('birth-date-input');
    const generateEsotericHunchBtn = document.getElementById('generate-esoteric-hunch-btn');
    const esotericHunchCard = document.getElementById('esoteric-hunch-card');
    const esotericHunchOutputDiv = document.getElementById('esoteric-hunch-output');
    const esotericHunchNumbersDiv = document.getElementById('esoteric-hunch-numbers');
    const esotericHunchMethodP = document.getElementById('esoteric-hunch-method');
    const esotericHunchHistoryCheckDiv = document.getElementById('esoteric-hunch-history-check');
    const saveEsotericHunchBtn = document.getElementById('save-esoteric-hunch-btn');
    const checkEsotericHunchBtn = document.getElementById('check-esoteric-hunch-btn');
    
    const cosmicPromoBanner = document.getElementById('cosmic-promo-banner');
    const promoRegisterBtn = document.getElementById('promo-register-btn'); 
    const promoLoginBtn = document.getElementById('promo-login-btn');     

    const mainDisplayLotterySelect = quickHunchLotteryTypeSelect; 
    const apiResultsPre = document.getElementById('api-results'); 
    const resultsLotteryNameSpan = document.getElementById('results-lottery-name');
    const fetchResultsBtn = document.getElementById('fetch-results-btn');
    
    const loginModalBtn = document.getElementById('login-modal-btn');
    const registerModalBtn = document.getElementById('register-modal-btn');
    const logoutBtn = document.getElementById('logout-btn');
    const userInfoDiv = document.getElementById('user-info');
    const userEmailSpan = document.getElementById('user-email');
    
    const loginModal = document.getElementById('login-modal');
    const registerModal = document.getElementById('register-modal');
    const closeLoginModalBtn = document.getElementById('close-login-modal');
    const closeRegisterModalBtn = document.getElementById('close-register-modal');
    
    const loginEmailInput = document.getElementById('login-email');
    const loginPasswordInput = document.getElementById('login-password');
    const loginSubmitBtn = document.getElementById('login-submit-btn');
    const loginErrorP = document.getElementById('login-error');
    
    const registerEmailInput = document.getElementById('register-email');
    const registerPasswordInput = document.getElementById('register-password');
    const registerConfirmPasswordInput = document.getElementById('register-confirm-password');
    const registerSubmitBtn = document.getElementById('register-submit-btn');
    const registerErrorP = document.getElementById('register-error');
    
    const errorDiv = document.getElementById('global-error-msg'); 
    const confettiCanvas = document.getElementById('confetti-canvas');

    const freqStatsLotteryNameSpan = document.getElementById('freq-stats-lottery-name');
    const frequencyListContainer = document.getElementById('frequency-list-container');
    const pairFreqStatsLotteryNameSpan = document.getElementById('pair-freq-stats-lottery-name');
    const pairFrequencyListContainer = document.getElementById('pair-frequency-list-container');
    const cityStatsLotteryNameSpan = document.getElementById('city-stats-lottery-name');
    const cityListContainer = document.getElementById('city-list-container');
    const cityPrizeSumLotteryNameSpan = document.getElementById('city-prize-sum-lottery-name');
    const cityPrizeSumListContainer = document.getElementById('city-prize-sum-list-container');

    const manualProbLotteryTypeSelect = document.getElementById('manual-prob-lottery-type');
    const manualProbUserNumbersInput = document.getElementById('manual-prob-user-numbers');
    const manualCalculateProbBtn = document.getElementById('manual-calculate-prob-btn');
    const manualProbabilityResultDisplay = document.getElementById('manual-probability-result-display');
    const manualProbNumbersCountFeedback = document.getElementById('manual-prob-numbers-count-feedback');

    const savedGamesContainer = document.getElementById('saved-games-container');
    const noSavedGamesP = document.getElementById('no-saved-games');
    const filterLotteryMyGamesSelect = document.getElementById('filter-lottery-mygames');

    let splashProgressBarFill = mainSplashScreen ? mainSplashScreen.querySelector('.progress-bar-fill') : null;
    let splashProgressContainer = mainSplashScreen ? mainSplashScreen.querySelector('.progress-bar-container') : null;

    // --- Variáveis Globais ---
    let splashHiddenTimestamp = 0;
    if (currentYearSpan) currentYearSpan.textContent = new Date().getFullYear();
    let BACKEND_URL_BASE;
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:") {
        BACKEND_URL_BASE = 'http://127.0.0.1:5000';
    } else {
        BACKEND_URL_BASE = '';
    }
    let firebaseApp, firebaseAuth, firestoreDB, currentUser = null;
    let lastFetchedResults = {};
    let lastGeneratedHunch = { type: null, lottery: null, jogo: [], estrategia_metodo: '', outputDiv: null, numbersDiv: null, checkResultDiv: null, saveButton: null, checkButton: null };
    let criticalSplashTimeout;
    let firebaseInitAttempts = 0;
    const maxFirebaseInitAttempts = 10;
    const LOTTERY_CONFIG_JS = { megasena: { count: 6, color: "#209869", name: "Mega-Sena" }, lotofacil: { count: 15, color: "#930089", name: "Lotofácil" }, quina: { count: 5, color: "#260085", name: "Quina" }, lotomania: { count_sorteadas: 20, count_apostadas: 50, color: "#f78100", name: "Lotomania" } };
    const bannerConfigurations = {
        'banner-top-dashboard': [
            { imageUrl: 'images/banner1.png', altText: 'Tammy\'s Store - Comprar agora!', linkUrl: 'https://www.instagram.com/tammysstore_/', isExternal: true },
            { imageUrl: 'images/teste1.png', altText: 'LotoGenius - A Sorte Inteligente',},
            { imageUrl: 'images/teste.png', altText: 'Recursos Premium LotoGenius', linkUrl: '#esoteric-hunch-card', isExternal: false }
        ],
        'banner-bottom-dashboard': [
            { imageUrl: 'images/dream.jpg', altText: 'Anúncio Parceiro 1', linkUrl: 'https://www.parceiro1.com', isExternal: true },
            { imageUrl: 'images/genius1.png', altText: 'Anúncio Visual Lateral' }
        ]
    };

    let recognition;
    let speechSynthesis = window.speechSynthesis;
    let isListening = false;
    let voiceGuideActive = null; 
    let firstInteractionDoneForAudio = false; 
    let voiceContext = { action: null, awaiting: null, data: {} };
    let welcomeScreenTimeout; 
    let awaitingSpecificInput = false;

    // ================================================================================================
    // === DEFINIÇÕES DE FUNÇÕES COMPLETAS ===
    // ================================================================================================
    
    function showGlobalError(message) { if (errorDiv) { errorDiv.textContent = message; errorDiv.style.display = 'block'; } else { console.error("SCRIPT.JS: Global error div não encontrado:", message); } }
    function disableFirebaseFeatures() { if (loginModalBtn) loginModalBtn.disabled = true; if (registerModalBtn) registerModalBtn.disabled = true; }
    function enableFirebaseFeatures() { if (loginModalBtn) loginModalBtn.disabled = false; if (registerModalBtn) registerModalBtn.disabled = false; if(document.getElementById('global-error-msg')) document.getElementById('global-error-msg').style.display = 'none';}
    
    function setActiveSection(sectionId) { 
        if (!mainSections || mainSections.length === 0) { console.warn("SCRIPT.JS: setActiveSection - mainSections não encontrado."); return; } 
        mainSections.forEach(section => { section.classList.remove('active-section'); if (section.id === sectionId) section.classList.add('active-section'); }); 
        if (mainNav) { 
            const navButtons = mainNav.querySelectorAll('.nav-item'); 
            navButtons.forEach(btn => { btn.classList.remove('active'); if (btn.id === `nav-${sectionId.replace('-section', '')}-btn`) btn.classList.add('active'); }); 
        } 
    }

    async function fetchData(endpoint, options = {}) {
        const url = `${BACKEND_URL_BASE}/${endpoint}`;
        try {
            const response = await fetch(url, options);
            const responseText = await response.text();
            if (!response.ok) {
                let errorJson = {}; try { errorJson = JSON.parse(responseText); } catch(e) {}
                const messageDetail = errorJson.message || (errorJson.data ? errorJson.data.detalhes || errorJson.data.erro : null) || errorJson.erro || responseText.substring(0,250) || `Erro HTTP ${response.status}`;
                console.error(`SCRIPT.JS: HTTP Error ${response.status} for ${url}:`, messageDetail);
                throw { status: response.status, message: messageDetail, data: errorJson };
            }
            if (response.status === 204 || !responseText) { return {}; }
            return JSON.parse(responseText);
        } catch (error) {
            if (error.status && error.message) { throw error; }
            console.error(`SCRIPT.JS: Erro geral em fetchData para ${url}:`, error);
            throw { status: error.status || 503, message: error.message || "Erro de comunicação.", data: {} }; 
        }
    }

    function animateCounter(element, finalValueInput) {
        if (!element) { return; }
        const numericFinalValue = parseInt(finalValueInput, 10);
        if (isNaN(numericFinalValue)) { element.textContent = "N/A"; return; }
        let startValue = 0;
        const currentText = element.textContent;
        if (currentText && currentText !== '--' && currentText !== 'N/A' && currentText.trim() !== '') {
            const parsedStart = parseInt(currentText.replace(/\D/g, ''), 10);
            if (!isNaN(parsedStart)) { startValue = parsedStart; }
        }
        if (numericFinalValue === startValue && currentText !== '--' && currentText !== 'N/A' && currentText.trim() !== '') {
            element.textContent = numericFinalValue.toLocaleString('pt-BR'); return;
        }
        let duration = 1200; let startTime = null;
        function animationStep(timestamp) {
            if (!startTime) startTime = timestamp;
            const progress = Math.min((timestamp - startTime) / duration, 1);
            let currentValue = (startValue > numericFinalValue) ?
                Math.max(numericFinalValue, Math.floor(startValue - progress * (startValue - numericFinalValue))) :
                Math.min(numericFinalValue, Math.floor(startValue + progress * (numericFinalValue - startValue)));
            element.textContent = currentValue.toLocaleString('pt-BR');
            if (progress < 1) { requestAnimationFrame(animationStep); }
            else { element.textContent = numericFinalValue.toLocaleString('pt-BR'); }
        }
        requestAnimationFrame(animationStep);
    }

    async function fetchPlatformStats() {
        if (!statsJogosGeradosSpan || !statsJogosPremiadosSpan || !statsValorPremiosSpan) { return; }
        try {
            const stats = await fetchData('api/main/platform-stats');
            if (stats && typeof stats.jogos_gerados_total === 'number') { animateCounter(statsJogosGeradosSpan, stats.jogos_gerados_total); } else { statsJogosGeradosSpan.textContent = "N/A"; }
            if (stats && typeof stats.jogos_premiados_estimativa === 'number') { animateCounter(statsJogosPremiadosSpan, stats.jogos_premiados_estimativa); } else { statsJogosPremiadosSpan.textContent = "N/A"; }
            if (stats && typeof stats.valor_premios_estimativa_formatado === 'string') { statsValorPremiosSpan.textContent = stats.valor_premios_estimativa_formatado; } else { statsValorPremiosSpan.textContent = "R$ N/A"; }
        } catch (error) { statsJogosGeradosSpan.textContent = "N/A"; statsJogosPremiadosSpan.textContent = "N/A"; statsValorPremiosSpan.textContent = "R$ N/A"; console.error("SCRIPT.JS: Erro em fetchPlatformStats:", error); }
    }

    async function fetchRecentWinningPools() {
        if (!recentPoolsList) { return; }
        recentPoolsList.innerHTML = '<li><div class="spinner small-spinner"></div> Carregando...</li>';
        try {
            const pools = await fetchData('api/main/recent-winning-pools');
            recentPoolsList.innerHTML = '';
            if (pools && pools.length > 0) { pools.forEach(pool => { const li = document.createElement('li'); li.innerHTML = `<span><i class="fas fa-trophy pool-icon"></i> ${pool.name} (${pool.lottery})</span> <span class="pool-prize">${pool.prize}</span> <small>${pool.date}</small>`; recentPoolsList.appendChild(li); }); }
            else { recentPoolsList.innerHTML = '<li>Nenhum bolão premiado recentemente.</li>'; }
        } catch (error) { recentPoolsList.innerHTML = '<li>Erro ao carregar bolões.</li>'; console.error("SCRIPT.JS: Erro em fetchRecentWinningPools:", error);}
    }

    async function fetchTopWinners() {
        if (!topWinnersList) { return; }
        topWinnersList.innerHTML = '<li><div class="spinner small-spinner"></div> Carregando...</li>';
        try {
            const winners = await fetchData('api/main/top-winners');
            topWinnersList.innerHTML = '';
            if (winners && winners.length > 0) { winners.forEach((winner, index) => { const li = document.createElement('li'); li.innerHTML = `<span>${index + 1}. <i class="fas fa-user-astronaut winner-icon"></i> ${winner.nick}</span> <span class="winner-prize">${winner.prize_total}</span>`; topWinnersList.appendChild(li); }); }
            else { topWinnersList.innerHTML = '<li>Ranking de ganhadores indisponível.</li>'; }
        } catch (error) { topWinnersList.innerHTML = '<li>Erro ao carregar ranking.</li>'; console.error("SCRIPT.JS: Erro em fetchTopWinners:", error);}
    }

    async function fetchAndDisplayStatsGeneric(lotteryName, statType, container, nameSpanInCard, endpointPrefix) {
        if (!container || !nameSpanInCard || !mainDisplayLotterySelect) { if(container) container.innerHTML = '<p class="error-message">Erro interno.</p>'; return; }
        const lotteryConfigEntry = Object.values(LOTTERY_CONFIG_JS).find(config => mainDisplayLotterySelect.options[mainDisplayLotterySelect.selectedIndex]?.text.includes(config.name));
        const lotteryFriendlyName = lotteryConfigEntry ? lotteryConfigEntry.name : lotteryName.toUpperCase();
        nameSpanInCard.textContent = lotteryFriendlyName;
        container.innerHTML = '<p class="loading-stats"><div class="spinner small-spinner"></div> Carregando...</p>';
        try {
            const result = await fetchData(`api/main/stats/${endpointPrefix}/${lotteryName}`);
            container.innerHTML = '';
            if (result.erro) { container.innerHTML = `<p class="error-message">${result.erro}</p>`; return; }
            if (!result.data || result.data.length === 0) { container.innerHTML = `<p class="no-stats">Sem dados de ${statType.toLowerCase()} para ${lotteryFriendlyName}.</p>`; return; }
            const statsData = result.data;
            const maxFreq = (endpointPrefix === 'frequencia' || endpointPrefix === 'pares-frequentes') && statsData.length > 0 ? statsData[0].frequencia : 1;
            const topN = (endpointPrefix === 'frequencia') ? Math.min(statsData.length, 15) : Math.min(statsData.length, 10);
            for (let i = 0; i < topN; i++) {
                const item = statsData[i]; const itemDiv = document.createElement('div');
                if (endpointPrefix === 'frequencia') {
                    itemDiv.classList.add('frequency-item');
                    const numSpan = document.createElement('span'); numSpan.classList.add('num'); numSpan.textContent = item.numero;
                    if (LOTTERY_CONFIG_JS[lotteryName]?.color) { numSpan.style.backgroundColor = LOTTERY_CONFIG_JS[lotteryName].color; numSpan.style.borderColor = LOTTERY_CONFIG_JS[lotteryName].color; numSpan.style.color = '#fff'; }
                    const barBgDiv = document.createElement('div'); barBgDiv.classList.add('freq-bar-bg');
                    const barDiv = document.createElement('div'); barDiv.classList.add('freq-bar');
                    const barWidth = Math.max(1, (item.frequencia / maxFreq) * 100); barDiv.style.width = `${barWidth}%`;
                    if (LOTTERY_CONFIG_JS[lotteryName]?.color) { barDiv.style.background = `linear-gradient(90deg, ${LOTTERY_CONFIG_JS[lotteryName].color}99, ${LOTTERY_CONFIG_JS[lotteryName].color}cc)`; }
                    barBgDiv.appendChild(barDiv);
                    const freqSpan = document.createElement('span'); freqSpan.classList.add('freq-count'); freqSpan.textContent = `${item.frequencia}x`;
                    itemDiv.appendChild(numSpan); itemDiv.appendChild(barBgDiv); itemDiv.appendChild(freqSpan);
                } else if (endpointPrefix === 'pares-frequentes') {
                    itemDiv.classList.add('pair-frequency-item');
                    const pairNumsDiv = document.createElement('div'); pairNumsDiv.classList.add('pair-nums');
                    item.par.forEach(numStr => { const numSpan = document.createElement('span'); numSpan.classList.add('num'); numSpan.textContent = numStr; if (LOTTERY_CONFIG_JS[lotteryName]?.color) { numSpan.style.backgroundColor = LOTTERY_CONFIG_JS[lotteryName].color; numSpan.style.borderColor = LOTTERY_CONFIG_JS[lotteryName].color; numSpan.style.color = '#fff'; } pairNumsDiv.appendChild(numSpan); });
                    const barBgDiv = document.createElement('div'); barBgDiv.classList.add('freq-bar-bg');
                    const barDiv = document.createElement('div'); barDiv.classList.add('freq-bar');
                    const barWidth = Math.max(1, (item.frequencia / maxFreq) * 100); barDiv.style.width = `${barWidth}%`;
                    if (LOTTERY_CONFIG_JS[lotteryName]?.color) { barDiv.style.background = `linear-gradient(90deg, ${LOTTERY_CONFIG_JS[lotteryName].color}99, ${LOTTERY_CONFIG_JS[lotteryName].color}cc)`; }
                    barBgDiv.appendChild(barDiv);
                    const freqSpan = document.createElement('span'); freqSpan.classList.add('freq-count'); freqSpan.textContent = `${item.frequencia}x`;
                    itemDiv.appendChild(pairNumsDiv); itemDiv.appendChild(barBgDiv); itemDiv.appendChild(freqSpan);
                } else if (endpointPrefix === 'cidades-premiadas') {
                    itemDiv.classList.add('city-stats-item');
                    const nameSpan = document.createElement('span'); nameSpan.classList.add('city-name'); nameSpan.textContent = item.cidade_uf;
                    const countSpan = document.createElement('span'); countSpan.classList.add('city-prize-count'); countSpan.textContent = `${item.premios_principais} prêmio(s)`;
                    itemDiv.appendChild(nameSpan); itemDiv.appendChild(countSpan);
                } else if (endpointPrefix === 'maiores-premios-cidade') {
                    itemDiv.classList.add('city-prize-item');
                    const nameSpan = document.createElement('span'); nameSpan.classList.add('city-name'); nameSpan.textContent = item.cidade_uf;
                    const amountSpan = document.createElement('span'); amountSpan.classList.add('city-prize-amount'); amountSpan.textContent = `${item.total_ganho_principal_formatado}`;
                    if (item.total_ganho_principal_float > 1000000) { amountSpan.style.fontWeight = 'bold'; amountSpan.style.color = '#2ecc71'; }
                    itemDiv.appendChild(nameSpan); itemDiv.appendChild(amountSpan);
                }
                container.appendChild(itemDiv);
            }
        } catch (error) { container.innerHTML = `<p class="error-message">Falha ao carregar.</p>`; console.error(`SCRIPT.JS: Erro em fetchAndDisplayStatsGeneric (${statType}, ${lotteryName}):`, error); }
    }
    async function fetchAndDisplayFrequencyStats(lotteryName) { if(frequencyListContainer && freqStatsLotteryNameSpan) fetchAndDisplayStatsGeneric(lotteryName, "Frequência", frequencyListContainer, freqStatsLotteryNameSpan, "frequencia"); }
    async function fetchAndDisplayPairFrequencyStats(lotteryName) { if(pairFrequencyListContainer && pairFreqStatsLotteryNameSpan) fetchAndDisplayStatsGeneric(lotteryName, "Pares Frequentes", pairFrequencyListContainer, pairFreqStatsLotteryNameSpan, "pares-frequentes"); }
    async function fetchAndDisplayCityStats(lotteryName) { if(cityListContainer && cityStatsLotteryNameSpan) fetchAndDisplayStatsGeneric(lotteryName, "Cidades Premiadas", cityListContainer, cityStatsLotteryNameSpan, "cidades-premiadas"); }
    async function fetchAndDisplayCityPrizeSumStats(lotteryName) { if(cityPrizeSumListContainer && cityPrizeSumLotteryNameSpan) fetchAndDisplayStatsGeneric(lotteryName, "Prêmios por Cidade", cityPrizeSumListContainer, cityPrizeSumLotteryNameSpan, "maiores-premios-cidade");}
    
    let previouslyFocusedElementModal; 
    function openModal(modalElement) { 
        if (modalElement) {
            previouslyFocusedElementModal = document.activeElement; 
            modalElement.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            const firstFocusableElement = modalElement.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusableElement) firstFocusableElement.focus();
        } else { console.warn("openModal: modalElement não encontrado"); }
    }
    function closeModal(modalElement) { 
        if (modalElement) {
            modalElement.style.display = 'none';
            document.body.style.overflow = '';
            if (modalElement === loginModal && loginEmailInput && loginPasswordInput && loginErrorP) { loginEmailInput.value = ''; loginPasswordInput.value = ''; loginErrorP.textContent = ''; } 
            else if (modalElement === registerModal && registerEmailInput && registerPasswordInput && registerConfirmPasswordInput && registerErrorP) { registerEmailInput.value = ''; registerPasswordInput.value = ''; registerConfirmPasswordInput.value = ''; registerErrorP.textContent = ''; }
            if (previouslyFocusedElementModal) previouslyFocusedElementModal.focus();
        } else { console.warn("closeModal: modalElement não encontrado"); }
    }
    
    function renderBanners() {
        for (const containerId in bannerConfigurations) {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = ''; 
                const banners = bannerConfigurations[containerId];
                banners.forEach((bannerData, index) => {
                    const imgElement = document.createElement('img');
                    imgElement.src = bannerData.imageUrl;
                    imgElement.alt = bannerData.altText;
                    let bannerItemWrapper;
                    if (bannerData.linkUrl) {
                        const linkElement = document.createElement('a');
                        linkElement.href = bannerData.linkUrl;
                        if (bannerData.isExternal) {
                            linkElement.target = '_blank';
                            linkElement.rel = 'noopener noreferrer';
                        }
                        linkElement.appendChild(imgElement);
                        bannerItemWrapper = linkElement;
                    } else {
                        const divWrapper = document.createElement('div');
                        divWrapper.appendChild(imgElement);
                        bannerItemWrapper = divWrapper;
                    }
                    bannerItemWrapper.classList.add('carousel-item');
                    if (index === 0) { bannerItemWrapper.classList.add('active'); }
                    container.appendChild(bannerItemWrapper);
                });
            }
        }
    }

    function initializeCarousels() {
        const carousels = document.querySelectorAll('.carousel-ad');
        carousels.forEach(carousel => {
            const items = carousel.querySelectorAll('.carousel-item');
            if (items.length <= 1) {
                if (items.length === 1 && !items[0].classList.contains('active')) { items[0].classList.add('active');}
                const noBannerP = carousel.querySelector('p');
                if(noBannerP && items.length > 0) noBannerP.style.display = 'none';
                return; 
            }
            let currentIndex = 0;
            items.forEach((item, index) => { if (index === currentIndex) item.classList.add('active'); else item.classList.remove('active'); });
            const intervalTime = parseInt(carousel.dataset.interval, 10) || 7000; 
            setInterval(() => {
                if(items[currentIndex]) items[currentIndex].classList.remove('active');
                currentIndex = (currentIndex + 1) % items.length;
                if(items[currentIndex]) items[currentIndex].classList.add('active');
            }, intervalTime);
        });
    }
    
    // ++ FUNÇÕES DE COMANDO DE VOZ ++
    function speak(text, options = {}) { 
        if (!speechSynthesis || !text) { console.warn("Síntese de voz não disponível ou texto vazio."); return; }
        if (speechSynthesis.speaking) { speechSynthesis.cancel(); } 
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'pt-BR';
        const voices = speechSynthesis.getVoices();
        const ptBRVoice = voices.find(voice => voice.lang === 'pt-BR' || voice.lang === 'pt_BR');
        if (ptBRVoice) utterance.voice = ptBRVoice;
        utterance.pitch = 1; utterance.rate = 1; 
        
        utterance.onend = () => {
            if (options.onEndCallback && typeof options.onEndCallback === 'function') options.onEndCallback();
            if (options.shouldRelisten && voiceGuideActive && recognition && !isListening) {
                console.log("Re-escutando automaticamente após a fala (speak).");
                startListeningGeneralCommands(true); 
            }
        };
        speechSynthesis.speak(utterance);
    }
    
    const defaultRecognitionResultHandler = (event) => {
        const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
        if (voiceGuideActive) { processVoiceCommand(transcript); }
    };

    function setVoiceGuideState(isActive) {
        voiceGuideActive = isActive;
        localStorage.setItem('voiceGuideActive', isActive.toString());
        if (voiceCommandBtn) { 
            voiceCommandBtn.style.display = 'inline-flex'; 
            if (voiceBtnText && voiceBtnIcon) {
                voiceBtnText.textContent = isActive ? "Desativar Guia" : "Ativar Guia";
                voiceBtnIcon.className = isActive ? "fas fa-microphone-slash" : "fas fa-microphone";
                voiceCommandBtn.setAttribute('aria-pressed', isActive.toString());
                voiceCommandBtn.title = isActive ? "Desativar Guia de Voz" : "Ativar Guia de Voz";
            }
        } else {
             console.warn("Botão de comando de voz principal não encontrado para atualizar estado.");
        }
        console.log("Estado do Guia de Voz:", isActive);
    }

    function startListeningGeneralCommands(isContinuation = false) {
        if (recognition && voiceGuideActive && !isListening) {
            try {
                if (!isContinuation) { voiceContext = { action: null, awaiting: null, data: {} }; }
                recognition.start(); isListening = true;
                if(voiceCommandBtn) voiceCommandBtn.classList.add('listening');
                console.log('Ouvindo comando geral...');
            } catch (e) { console.error("Erro ao iniciar escuta geral:", e); isListening = false; if(voiceCommandBtn) voiceCommandBtn.classList.remove('listening'); }
        } else if (!voiceGuideActive) { speak("O guia de voz está desativado."); 
        }
    }
    
    function processVoiceCommand(command) {
        console.log("Processando comando de voz:", command);
        awaitingSpecificInput = false; 
        if (command.includes('cancelar') || command.includes('parar')) {
            speak("Ação cancelada."); voiceContext = { action: null, awaiting: null, data: {} };
            if(isListening) { recognition.abort(); } return;
        }
        if (voiceContext.action === 'login_email_input') {
            voiceContext.data.email = command.replace(/arroba/g, '@').replace(/\s/g, '').toLowerCase();
            speak(`Entendi o email como ${voiceContext.data.email}. Está correto? Diga 'sim' ou 'não'.`, { shouldRelisten: true });
            voiceContext.awaiting = 'login_email_confirmation'; awaitingSpecificInput = true; return;
        }
        if (voiceContext.action === 'login_email_input' && voiceContext.awaiting === 'login_email_confirmation') {
            if (command.includes('sim')) {
                speak("Email confirmado. Por segurança, por favor, digite sua senha no campo e pressione Entrar.");
                if(loginEmailInput) loginEmailInput.value = voiceContext.data.email;
                if(loginPasswordInput) loginPasswordInput.focus();
                voiceContext = { action: null, awaiting: null, data: {} };
            } else if (command.includes('não') || command.includes('corrigir')) {
                speak("Ok, por favor, diga seu email novamente.", { shouldRelisten: true });
                voiceContext.awaiting = null; awaitingSpecificInput = true;
            } else { speak("Não entendi. Diga 'sim' para confirmar o email, ou 'não' para corrigir.", { shouldRelisten: true }); awaitingSpecificInput = true; }
            return;
        }
        if (command.includes('login') || command.includes('entrar') || command.includes('fazer login')) {
            if (currentUser) { speak("Você já está logado."); return; }
            openModal(loginModal); speak("Tela de login aberta. Para preencher por voz, diga 'digitar email'.", { shouldRelisten: true });
            voiceContext.action = 'login_prompt_email'; awaitingSpecificInput = true; return;
        }
        if (voiceContext.action === 'login_prompt_email' && command.includes('digitar email')) {
            speak("Ok, diga seu email agora.", { shouldRelisten: true });
            voiceContext.action = 'login_capturing_email'; voiceContext.awaiting = 'email_text'; 
            awaitingSpecificInput = true; return;
        }
         if (voiceContext.action === 'login_capturing_email' && voiceContext.awaiting === 'email_text') {
            const emailAttempt = command.replace(/arroba/g, '@').replace(/\s/g, '').toLowerCase(); 
            if (loginEmailInput) loginEmailInput.value = emailAttempt;
            speak(`Email preenchido como ${emailAttempt}. Por favor, digite sua senha e pressione entrar.`);
            if (loginPasswordInput) loginPasswordInput.focus();
            voiceContext = { action: null, awaiting: null, data: {} }; 
            return;
        }
        if (command.includes('registrar') || command.includes('criar conta')) {
            if (currentUser) { speak("Você já está logado."); return; }
            openModal(registerModal); speak("Tela de registro aberta. Preencha os campos utilizando o teclado.");
            voiceContext = { action: null, awaiting: null, data: {} }; return;
        }
        if (command.includes('painel') || command.includes('início') || command.includes('tela principal')) { setActiveSection('dashboard-section'); speak("Navegando para o painel principal."); return; }
        if (command.includes('meus jogos')) {
            if (!currentUser) { speak("Você precisa estar logado. Diga 'login'.", {shouldRelisten: true}); voiceContext.action = 'awaiting_login_for_my_games'; awaitingSpecificInput = true; return;}
            setActiveSection('my-games-section'); speak("Navegando para Meus Jogos Salvos."); return;
        }
        if (voiceContext.action === 'awaiting_login_for_my_games' && command.includes('login')) {
            openModal(loginModal); speak("Tela de login aberta. Diga 'digitar email'.", {shouldRelisten: true}); voiceContext.action = 'login_prompt_email'; awaitingSpecificInput = true; return;
        }
        if (command.includes('gerar mega sena rápido') || command.includes('palpite rápido mega sena')) {
            if (quickHunchLotteryTypeSelect) quickHunchLotteryTypeSelect.value = 'megasena';
            if (generateQuickHunchBtn) { speak("Gerando palpite rápido para Mega-Sena."); generateQuickHunchBtn.click(); } return;
        }
         if (command.includes('gerar lotofácil rápido') || command.includes('palpite rápido lotofácil')) {
            if (quickHunchLotteryTypeSelect) quickHunchLotteryTypeSelect.value = 'lotofacil';
            if (generateQuickHunchBtn) { speak("Gerando palpite rápido para Lotofácil."); generateQuickHunchBtn.click(); } return;
        }
        if (command.includes('ajuda') || command.includes('comandos')) {
            speak("Comandos: 'login', 'registrar', 'painel', 'meus jogos', 'gerar mega sena rápido', 'onde estou'.", {shouldRelisten: true});
            awaitingSpecificInput = true; return;
        }
        if (command.includes('onde estou') || command.includes('descreva a tela')) {
            const activeSectionElement = document.querySelector('.main-section.active-section');
            let sectionName = "uma área desconhecida";
            if (activeSectionElement) {
                if (activeSectionElement.id === 'dashboard-section') sectionName = "o painel principal. Aqui pode gerar jogos e ver estatísticas";
                else if (activeSectionElement.id === 'my-games-section') sectionName = "a seção de Meus Jogos Salvos";
                else if (activeSectionElement.id === 'pools-section') sectionName = "a seção de Bolões";
            }
            speak(`Você está em ${sectionName}.`); return;
        }
        if(!awaitingSpecificInput && (!voiceContext.action || !voiceContext.awaiting)) { speak("Comando não reconhecido. Tente 'ajuda'."); }
    }
    
    function initializeVoiceCommands() {
        const SpeechRecognitionAPI = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognitionAPI && speechSynthesis) {
            recognition = new SpeechRecognitionAPI();
            recognition.lang = 'pt-BR'; recognition.continuous = false; recognition.interimResults = false; recognition.maxAlternatives = 1;
            recognition.onresult = defaultRecognitionResultHandler;
            recognition.onerror = (event) => {
                console.error('Erro no reconhecimento de voz:', event.error);
                isListening = false; awaitingSpecificInput = false;
                if(voiceCommandBtn) voiceCommandBtn.classList.remove('listening');
                if (event.error !== 'no-speech' && event.error !== 'aborted') { speak("Erro no reconhecimento de voz."); }
            };
            recognition.onend = () => {
                const wasAwaiting = awaitingSpecificInput;
                isListening = false; awaitingSpecificInput = false; 
                if(voiceCommandBtn) voiceCommandBtn.classList.remove('listening');
                if (voiceGuideActive && wasAwaiting && voiceContext.action && voiceContext.awaiting) {
                    setTimeout(() => startListeningGeneralCommands(true), 200); 
                }
            };
            if (voiceCommandBtn) {
                voiceCommandBtn.addEventListener('click', () => {
                    if (recognition && isListening) { recognition.abort(); return; }
                     // A lógica de ativar/desativar o guia agora é feita na tela de boas-vindas
                     // ou se o usuário clicar no botão depois da escolha inicial.
                    if (voiceGuideActive) {
                        startListeningGeneralCommands();
                    } else {
                        setVoiceGuideState(true); // Ativa se estava desativado
                        speak("Guia de voz ativado. Clique novamente para comandar.");
                        localStorage.removeItem('voiceGuideDeclined');
                        localStorage.setItem('voiceGuideChoiceMade', 'true'); // Assume que a escolha foi feita
                    }
                });
            }
             if (speechSynthesis.onvoiceschanged !== undefined) { speechSynthesis.onvoiceschanged = () => {}; }
        } else { console.warn('Web Speech API não é suportada.'); if (voiceCommandBtn) voiceCommandBtn.style.display = 'none'; }
    }

    function handleWelcomeChoice(activate) {
        clearTimeout(welcomeScreenTimeout); 
        setVoiceGuideState(activate);
        localStorage.setItem('voiceGuideChoiceMade', 'true'); 
        if (activate) {
            // speak("Guia de voz ativado."); // A fala já ocorre em setVoiceGuideState ou após a escolha
            localStorage.removeItem('voiceGuideDeclined');
        } else {
            localStorage.setItem('voiceGuideDeclined', 'true');
        }
        if (inclusiveWelcomeScreen) inclusiveWelcomeScreen.classList.add('hidden'); 
        if (mainSplashScreen) mainSplashScreen.style.display = 'flex'; 

        if (splashProgressBarFill && splashProgressContainer && mainSplashScreen && !mainSplashScreen.classList.contains('hidden')) {
            let progress = 0; const totalVisualBarTime = SPLASH_PROGRESS_BAR_START_DELAY + SPLASH_PROGRESS_BAR_FILL_DURATION; const intervalTime = Math.max(10, totalVisualBarTime / 100);
            const progressInterval = setInterval(() => { progress++; if (splashProgressContainer) splashProgressContainer.setAttribute('aria-valuenow', progress); if (progress >= 100) { clearInterval(progressInterval); } }, intervalTime);
        }
        
        criticalSplashTimeout = setTimeout(() => { 
             if (splashHiddenTimestamp === 0 && typeof effectivelyShowApp === "function") { effectivelyShowApp(); }
             if (!firebaseApp && typeof showGlobalError === "function") { showGlobalError("Falha crítica na inicialização."); if(typeof disableFirebaseFeatures === "function") disableFirebaseFeatures();}
             criticalSplashTimeout = null; 
        }, SPLASH_MINIMUM_VISIBLE_TIME + 1000); 

        if (typeof attemptFirebaseInit === "function") { setTimeout(attemptFirebaseInit, 150); } 
        else {  if (typeof effectivelyShowApp === "function") effectivelyShowApp(); if(typeof disableFirebaseFeatures === "function") disableFirebaseFeatures(); }
    }
    
    function initializeInclusiveWelcome() {
        if (localStorage.getItem('voiceGuideChoiceMade') === 'true') {
            const guideWasActive = localStorage.getItem('voiceGuideActive') === 'true';
            handleWelcomeChoice(guideWasActive); 
            return;
        }

        if (inclusiveWelcomeScreen) inclusiveWelcomeScreen.style.display = 'flex';
        if (mainSplashScreen) mainSplashScreen.style.display = 'none'; 
        if (voiceCommandBtn) voiceCommandBtn.style.display = 'none'; 

        const playInitialGreetingAndListen = () => {
            if (voiceGuideActive !== null || !inclusiveWelcomeScreen || inclusiveWelcomeScreen.classList.contains('hidden')) return;
            const greeting = "Bem-vindo ao Loto Genius AI. Esta plataforma é inclusiva. Deseja ativar o guia de voz? Diga 'Sim' ou 'Não', ou use os botões na tela.";
            speak(greeting, {
                onEndCallback: () => {
                    if (recognition && !isListening && voiceGuideActive === null) { 
                        isListening = true; awaitingSpecificInput = true;
                        recognition.onresult = (event) => { 
                            const transcript = event.results[event.results.length-1][0].transcript.trim().toLowerCase();
                            awaitingSpecificInput = false; isListening = false; recognition.onresult = defaultRecognitionResultHandler; 
                            clearTimeout(welcomeScreenTimeout); 
                            if (transcript.includes('sim')) { handleWelcomeChoice(true); }
                            else if (transcript.includes('não')) { handleWelcomeChoice(false); }
                        };
                        recognition.onerror = (event) => {console.error("Erro welcome listen:", event.error); awaitingSpecificInput = false; isListening = false; recognition.onresult = defaultRecognitionResultHandler; clearTimeout(welcomeScreenTimeout); if(voiceGuideActive === null) handleWelcomeChoice(false);};
                        recognition.onend = () => {awaitingSpecificInput = false; isListening = false; recognition.onresult = defaultRecognitionResultHandler; if (voiceGuideActive === null && welcomeScreenTimeout && typeof welcomeScreenTimeout !== 'undefined' && welcomeScreenTimeout._destroyed === false) {} };
                        try { recognition.start(); } catch (e) { console.error("Falha ao iniciar reconhecimento na saudação", e); isListening = false; awaitingSpecificInput = false;}
                    }
                }
            });
        };

        document.body.addEventListener('pointerdown', function handleFirstAudio() {
            if (!firstInteractionDoneForAudio) {
                firstInteractionDoneForAudio = true;
                let voiceCheckCount = 0;
                const checkAndPlay = () => { (speechSynthesis.getVoices().length > 0 || voiceCheckCount > 15) ? playInitialGreetingAndListen() : (voiceCheckCount++, setTimeout(checkAndPlay, 200)); };
                if (speechSynthesis.onvoiceschanged !== undefined && speechSynthesis.getVoices().length === 0) { 
                    speechSynthesis.onvoiceschanged = () => { setTimeout(checkAndPlay, 100); speechSynthesis.onvoiceschanged = null; }; 
                } else {
                    checkAndPlay(); 
                }
            }
        }, { capture: true, once: true });

        if (activateVoiceGuideBtn) activateVoiceGuideBtn.addEventListener('click', () => { clearTimeout(welcomeScreenTimeout); handleWelcomeChoice(true); });
        if (declineVoiceGuideBtn) declineVoiceGuideBtn.addEventListener('click', () => { clearTimeout(welcomeScreenTimeout); handleWelcomeChoice(false); });

        welcomeScreenTimeout = setTimeout(() => {
            if (voiceGuideActive === null && inclusiveWelcomeScreen && inclusiveWelcomeScreen.style.display !== 'none') { 
                handleWelcomeChoice(false); 
            }
        }, 20000); 
    }

    function effectivelyShowApp() {
        if (criticalSplashTimeout) { clearTimeout(criticalSplashTimeout); criticalSplashTimeout = null; }
        if (mainSplashScreen && !mainSplashScreen.classList.contains('hidden') && splashHiddenTimestamp === 0) { 
            mainSplashScreen.classList.add('hidden');
            splashHiddenTimestamp = Date.now();
        }
        if (inclusiveWelcomeScreen && !inclusiveWelcomeScreen.classList.contains('hidden')) {
            inclusiveWelcomeScreen.classList.add('hidden'); 
        }
        showAppContentNow();
    }
    
    function showAppContentNow() {
        if (appContent && appContent.style.display === 'none') { 
            appContent.style.display = 'block';
            if (typeof setActiveSection === "function") setActiveSection('dashboard-section');
            if (typeof fetchPlatformStats === "function") fetchPlatformStats();
            if (typeof fetchRecentWinningPools === "function") fetchRecentWinningPools();
            if (typeof fetchTopWinners === "function") fetchTopWinners();
            if (typeof renderBanners === "function") renderBanners();
            if (typeof initializeCarousels === "function") initializeCarousels();
            if (mainDisplayLotterySelect) {
                const initialLottery = mainDisplayLotterySelect.value;
                if (typeof fetchAndDisplayResults === "function") fetchAndDisplayResults(initialLottery);
                if (typeof fetchAndDisplayFrequencyStats === "function") fetchAndDisplayFrequencyStats(initialLottery);
                if (typeof fetchAndDisplayPairFrequencyStats === "function") fetchAndDisplayPairFrequencyStats(initialLottery);
                if (typeof fetchAndDisplayCityStats === "function") fetchAndDisplayCityStats(initialLottery);
                if (typeof fetchAndDisplayCityPrizeSumStats === "function") fetchAndDisplayCityPrizeSumStats(initialLottery);
                setTimeout(() => { if (mainDisplayLotterySelect.dispatchEvent) mainDisplayLotterySelect.dispatchEvent(new Event('change')); }, 300);
            }
        }
    }
    
    function updateLoginUI(user) {
        const navItems = document.querySelectorAll('#main-nav .nav-item');
        if (user) {
            if (loginModalBtn) loginModalBtn.style.display = 'none'; if (registerModalBtn) registerModalBtn.style.display = 'none';
            if (userInfoDiv) userInfoDiv.style.display = 'flex'; if (userEmailSpan) userEmailSpan.textContent = user.email.split('@')[0];
            if (logoutBtn) logoutBtn.style.display = 'inline-block'; if (mainNav) mainNav.style.display = 'flex';
            if (navItems && typeof setActiveSection === "function") navItems.forEach(item => item.style.display = 'flex');
            if (typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos");
            if (esotericHunchCard) esotericHunchCard.style.display = 'block'; if (cosmicPromoBanner) cosmicPromoBanner.style.display = 'none';
        } else {
            if (loginModalBtn) loginModalBtn.style.display = 'inline-block'; if (registerModalBtn) registerModalBtn.style.display = 'inline-block';
            if (userInfoDiv) userInfoDiv.style.display = 'none'; if (userEmailSpan) userEmailSpan.textContent = '';
            if (logoutBtn) logoutBtn.style.display = 'none'; if (mainNav) mainNav.style.display = 'none';
            if (navItems) navItems.forEach(item => item.style.display = 'none');
            if (savedGamesContainer) savedGamesContainer.innerHTML = ''; if (noSavedGamesP) noSavedGamesP.style.display = 'block';
            if (esotericHunchCard) esotericHunchCard.style.display = 'none'; if (cosmicPromoBanner) cosmicPromoBanner.style.display = 'block';
        }
        if (typeof updateSaveButtonVisibility === "function") { updateSaveButtonVisibility('quick'); updateSaveButtonVisibility('esoteric'); updateSaveButtonVisibility('hot'); }
    }
    
    async function generateAndDisplayQuickHunch() {
        if (!quickHunchLotteryTypeSelect || !generateQuickHunchBtn || !quickHunchOutputDiv || !quickHunchNumbersDiv || !quickHunchStrategyP) { return; }
        const lottery = quickHunchLotteryTypeSelect.value;
        generateQuickHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...'; generateQuickHunchBtn.disabled = true;
        quickHunchOutputDiv.style.display = 'block'; quickHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>'; quickHunchStrategyP.textContent = 'Gerando palpite...';
        if(saveQuickHunchBtn) saveQuickHunchBtn.style.display = 'none'; if(checkQuickHunchBtn) checkQuickHunchBtn.style.display = 'none'; if(quickHunchCheckResultDiv) quickHunchCheckResultDiv.innerHTML = '';
        try {
            const data = await fetchData(`api/main/gerar_jogo/${lottery}`);
            if (data.erro) { throw new Error(data.detalhes || data.erro);  } if (!data.jogo || !Array.isArray(data.jogo) || data.jogo.length === 0) { throw new Error("Palpite inválido.");}
            if (typeof renderGameNumbers === "function") renderGameNumbers(quickHunchNumbersDiv, data.jogo, [], [], lottery);
            quickHunchStrategyP.textContent = `Método: ${data.estrategia_usada || 'Aleatório'}`;
            lastGeneratedHunch = { type: 'quick', lottery: lottery, jogo: data.jogo, estrategia_metodo: data.estrategia_usada || 'Aleatório', outputDiv: quickHunchOutputDiv, numbersDiv: quickHunchNumbersDiv, checkResultDiv: quickHunchCheckResultDiv, saveButton: saveQuickHunchBtn, checkButton: checkQuickHunchBtn };
            if (typeof updateSaveButtonVisibility === "function") updateSaveButtonVisibility('quick'); if (checkQuickHunchBtn) checkQuickHunchBtn.style.display = 'inline-block';
        } catch (error) { console.error("SCRIPT.JS: Erro palpite rápido:", error); quickHunchNumbersDiv.innerHTML = `<p class="error-message">${error.message || 'Falha.'}</p>`; quickHunchStrategyP.textContent = 'Erro.'; lastGeneratedHunch = { type: null };
        } finally { generateQuickHunchBtn.innerHTML = '<i class="fas fa-random"></i> Gerar Palpite Rápido'; generateQuickHunchBtn.disabled = false; }
    }

    async function generateAndDisplayHotNumbersHunch() {
        if (!hotNumbersLotteryTypeSelect || !generateHotNumbersHunchBtn || !hotNumbersAnalyzeCountInput || !hotNumbersHunchOutputDiv || !hotNumbersHunchNumbersDiv || !hotNumbersHunchStrategyP) { return; }
        const lottery = hotNumbersLotteryTypeSelect.value; let analyzeCount = parseInt(hotNumbersAnalyzeCountInput.value, 10);
        if (isNaN(analyzeCount) || analyzeCount <= 0) { alert("Insira um número válido de concursos (mín. 1)."); hotNumbersAnalyzeCountInput.focus(); analyzeCount = 20; hotNumbersAnalyzeCountInput.value = analyzeCount; }
        generateHotNumbersHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...'; generateHotNumbersHunchBtn.disabled = true;
        hotNumbersHunchOutputDiv.style.display = 'block'; hotNumbersHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>'; hotNumbersHunchStrategyP.textContent = 'Analisando...';
        if(saveHotHunchBtn) saveHotHunchBtn.style.display = 'none'; if(checkHotHunchBtn) checkHotHunchBtn.style.display = 'none'; if(hotHunchCheckResultDiv) hotHunchCheckResultDiv.innerHTML = '';
        try {
            const data = await fetchData(`api/main/gerar_jogo/numeros_quentes/${lottery}?num_concursos_analisar=${analyzeCount}`);
            if (data.erro) { throw new Error(data.detalhes || data.erro); } if (!data.jogo || !Array.isArray(data.jogo) || data.jogo.length === 0) { throw new Error("Palpite inválido (quentes)."); }
            if (typeof renderGameNumbers === "function") renderGameNumbers(hotNumbersHunchNumbersDiv, data.jogo, [], [], lottery);
            hotNumbersHunchStrategyP.textContent = `Método: ${data.estrategia_usada || 'Números Quentes'}`; if (data.aviso) { hotNumbersHunchStrategyP.textContent += ` (${data.aviso})`; }
            lastGeneratedHunch = { type: 'hot', lottery: lottery, jogo: data.jogo, estrategia_metodo: data.estrategia_usada || 'Números Quentes', outputDiv: hotNumbersHunchOutputDiv, numbersDiv: hotNumbersHunchNumbersDiv, checkResultDiv: hotHunchCheckResultDiv, saveButton: saveHotHunchBtn, checkButton: checkHotHunchBtn };
            if (typeof updateSaveButtonVisibility === "function") updateSaveButtonVisibility('hot'); if (checkHotHunchBtn) checkHotHunchBtn.style.display = 'inline-block';
        } catch (error) { console.error("SCRIPT.JS: Erro palpite números quentes:", error); hotNumbersHunchNumbersDiv.innerHTML = `<p class="error-message">${error.message || 'Falha.'}</p>`; hotNumbersHunchStrategyP.textContent = 'Erro.'; lastGeneratedHunch = { type: null };
        } finally { generateHotNumbersHunchBtn.innerHTML = '<i class="fas fa-chart-line"></i> Gerar Palpite Quente'; generateHotNumbersHunchBtn.disabled = false; }
    }

    async function generateAndDisplayEsotericHunch() {
        if (!esotericLotteryTypeSelect || !birthDateInput || !generateEsotericHunchBtn || !esotericHunchOutputDiv || !esotericHunchNumbersDiv || !esotericHunchMethodP || !esotericHunchHistoryCheckDiv) { return; }
        const lotteryName = esotericLotteryTypeSelect.value; const birthDateRaw = birthDateInput.value.trim(); const birthDate = birthDateRaw.replace(/\D/g, '');
        if (!birthDate) { alert("Insira sua data de nascimento."); birthDateInput.focus(); return; } if (birthDate.length !== 8) { alert("Formato da data inválido. Use DDMMAAAA."); birthDateInput.focus(); return; }
        generateEsotericHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...'; generateEsotericHunchBtn.disabled = true;
        esotericHunchOutputDiv.style.display = 'block'; esotericHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>'; esotericHunchMethodP.textContent = 'Consultando...'; esotericHunchHistoryCheckDiv.innerHTML = '';
        if(saveEsotericHunchBtn) saveEsotericHunchBtn.style.display = 'none'; if(checkEsotericHunchBtn) checkEsotericHunchBtn.style.display = 'none';
        try {
            const requestBody = { data_nascimento: birthDate }; const data = await fetchData(`api/main/palpite-esoterico/${lotteryName}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestBody) });
            if (data.erro) { throw new Error(data.erro); } if (!data.palpite_gerado) { throw new Error("API não retornou palpite."); }
            if (typeof renderGameNumbers === "function") renderGameNumbers(esotericHunchNumbersDiv, data.palpite_gerado, [], [], lotteryName);
            esotericHunchMethodP.textContent = `Método: ${data.metodo_geracao || 'N/A'}`;
            let historyHtml = `<strong>Histórico:</strong><br>`;
            if (data.historico_desta_combinacao) { const hist = data.historico_desta_combinacao; historyHtml += `Premiada? <span style="color: ${hist.ja_foi_premiada_faixa_principal ? '#2ecc71' : '#ff4765'}; font-weight: bold;">${hist.ja_foi_premiada_faixa_principal ? 'Sim' : 'Não'}</span> (${hist.vezes_premiada_faixa_principal}x) - Valor: ${hist.valor_total_ganho_faixa_principal_formatado}`; } else { historyHtml += "Não verificado."; }
            esotericHunchHistoryCheckDiv.innerHTML = historyHtml;
            lastGeneratedHunch = { type: 'esoteric', lottery: lotteryName, jogo: data.palpite_gerado, estrategia_metodo: data.metodo_geracao || 'N/A', outputDiv: esotericHunchOutputDiv, numbersDiv: esotericHunchNumbersDiv, checkResultDiv: esotericHunchHistoryCheckDiv, saveButton: saveEsotericHunchBtn, checkButton: checkEsotericHunchBtn };
            if (typeof updateSaveButtonVisibility === "function") updateSaveButtonVisibility('esoteric'); if (checkEsotericHunchBtn) checkEsotericHunchBtn.style.display = 'inline-block';
        } catch (error) { console.error("SCRIPT.JS: Erro palpite esotérico:", error); esotericHunchNumbersDiv.innerHTML = ''; esotericHunchMethodP.textContent = ''; esotericHunchHistoryCheckDiv.innerHTML = `<p class="error-message">Falha: ${error.message || 'Erro.'}</p>`; lastGeneratedHunch = { type: null };
        } finally { generateEsotericHunchBtn.innerHTML = '<i class="fas fa-meteor"></i> Gerar Palpite Cósmico'; generateEsotericHunchBtn.disabled = false; }
    }

    function updateSaveButtonVisibility(hunchType) {
        const currentHunch = lastGeneratedHunch; let targetSaveButton = null;
        if (hunchType === 'quick') targetSaveButton = saveQuickHunchBtn;
        else if (hunchType === 'esoteric') targetSaveButton = saveEsotericHunchBtn;
        else if (hunchType === 'hot') targetSaveButton = saveHotHunchBtn;
        if (targetSaveButton) { targetSaveButton.style.display = currentUser && currentHunch.type === hunchType && currentHunch.outputDiv && currentHunch.outputDiv.style.display !== 'none' ? 'inline-block' : 'none'; }
        else if (currentHunch.type === hunchType && !targetSaveButton) { console.warn(`SCRIPT.JS: Botão Salvar para '${hunchType}' não encontrado.`); }
    }

    function setupSaveHunchButtonListeners() {
        if (saveQuickHunchBtn) saveQuickHunchBtn.addEventListener('click', () => saveLastGeneratedHunch('quick'));
        if (saveEsotericHunchBtn) saveEsotericHunchBtn.addEventListener('click', () => saveLastGeneratedHunch('esoteric'));
        if (saveHotHunchBtn) saveHotHunchBtn.addEventListener('click', () => saveLastGeneratedHunch('hot'));
    }

    function saveLastGeneratedHunch(expectedHunchType) {
        if (!firestoreDB || !currentUser || !lastGeneratedHunch.jogo || !Array.isArray(lastGeneratedHunch.jogo) || lastGeneratedHunch.jogo.length === 0 || lastGeneratedHunch.type !== expectedHunchType) {
            alert("Logue-se e gere um palpite válido deste tipo para salvar."); return;
        }
        const { lottery, jogo, estrategia_metodo } = lastGeneratedHunch;
        firestoreDB.collection('userGames').add({ userId: currentUser.uid, userEmail: currentUser.email, lottery: lottery, game: jogo, strategy: estrategia_metodo, savedAt: firebase.firestore.FieldValue.serverTimestamp(), checkedResult: null })
            .then(() => { alert("Palpite salvo!"); if (myGamesSection && myGamesSection.classList.contains('active-section') && typeof loadUserGames === "function") { loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); } })
            .catch((error) => { alert(`Erro ao salvar: ${error.message}`); console.error("SCRIPT.JS: Erro ao salvar:", error); });
    }

    function setupCheckHunchButtonListeners() {
        if (checkQuickHunchBtn && quickHunchLotteryTypeSelect) checkQuickHunchBtn.addEventListener('click', () => checkLastGeneratedHunch('quick', quickHunchLotteryTypeSelect));
        if (checkEsotericHunchBtn && esotericLotteryTypeSelect) checkEsotericHunchBtn.addEventListener('click', () => checkLastGeneratedHunch('esoteric', esotericLotteryTypeSelect));
        if (checkHotHunchBtn && hotNumbersLotteryTypeSelect) checkHotHunchBtn.addEventListener('click', () => checkLastGeneratedHunch('hot', hotNumbersLotteryTypeSelect));
    }

    async function checkLastGeneratedHunch(expectedHunchType, lotterySelectElement) {
        const currentLottery = lotterySelectElement.value; const currentHunch = lastGeneratedHunch;
        let targetCheckResultDiv = null; let targetNumbersDiv = null;
        if (expectedHunchType === 'quick') { targetCheckResultDiv = quickHunchCheckResultDiv; targetNumbersDiv = quickHunchNumbersDiv; }
        else if (expectedHunchType === 'esoteric') { targetCheckResultDiv = esotericHunchHistoryCheckDiv; targetNumbersDiv = esotericHunchNumbersDiv; }
        else if (expectedHunchType === 'hot') { targetCheckResultDiv = hotHunchCheckResultDiv; targetNumbersDiv = hotNumbersHunchNumbersDiv; }

        if (!currentHunch.jogo || !Array.isArray(currentHunch.jogo) || currentHunch.jogo.length === 0 || currentHunch.lottery !== currentLottery || currentHunch.type !== expectedHunchType || !targetCheckResultDiv || !targetNumbersDiv ) {
            if(targetCheckResultDiv) targetCheckResultDiv.innerHTML = '<span class="misses">Gere um palpite deste tipo para esta loteria primeiro.</span>'; return;
        }
        let resultsToUse = lastFetchedResults[currentLottery];
        if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) {
            targetCheckResultDiv.innerHTML = `<div class="spinner small-spinner"></div> Buscando resultados...`;
            try { resultsToUse = await fetchData(`api/main/resultados/${currentLottery}`); if(resultsToUse) resultsToUse.loteria_tipo = currentLottery; lastFetchedResults[currentLottery] = resultsToUse; }
            catch (e) { targetCheckResultDiv.innerHTML = `<span class="misses">Falha ao buscar resultados.</span>`; return; }
        }
        if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) { targetCheckResultDiv.innerHTML = `<span class="misses">Resultados oficiais indisponíveis.</span>`; return; }
        if(typeof checkGame !== "function" || typeof renderGameNumbers !== "function") { targetCheckResultDiv.innerHTML = "Erro interno."; return; }
        const result = checkGame(currentHunch.jogo, resultsToUse);
        if (expectedHunchType === 'esoteric') { console.log("Conferência p/ esotérico:", result.message); } 
        else { targetCheckResultDiv.innerHTML = `<span class="${result.hits > 0 ? 'hits' : (result.almostNumbers && result.almostNumbers.length > 0 ? 'almost-text' : 'misses')}">${result.message}</span>`; }
        renderGameNumbers(targetNumbersDiv, currentHunch.jogo, result.hitNumbers, result.almostNumbers || [], currentLottery);
    }
    
    function triggerConfetti() {
        if (!confettiCanvas) return;
        for (let i = 0; i < 100; i++) { 
            const confetti = document.createElement('div');
            confetti.classList.add('confetti');
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 70%)`;
            const duration = Math.random() * 3 + 2; 
            confetti.style.animationDuration = duration + 's';
            confetti.style.animationDelay = Math.random() * 0.5 + 's'; 
            confetti.addEventListener('animationend', () => { confetti.remove(); });
            confettiCanvas.appendChild(confetti);
        }
    }

    function checkGame(userGameNumbers, officialResults) {
        if (!userGameNumbers || !officialResults || !officialResults.numeros || !Array.isArray(officialResults.numeros)) {
            return { hits: 0, hitNumbers: [], almostNumbers: [], message: "Dados insuficientes para conferir." };
        }
        const drawnNumbers = officialResults.numeros.map(n => String(n).trim());
        const userNumbersStr = userGameNumbers.map(n => String(n).trim());
        let hits = 0; 
        let hitNumbers = [];
        userNumbersStr.forEach(num => { 
            if (drawnNumbers.includes(num)) { 
                hits++; 
                hitNumbers.push(parseInt(num,10)); 
            } 
        });
        let message = `Você acertou ${hits} número(s).`;
        if (hits > 0) {
            message += ` Acertos: ${hitNumbers.join(', ')}.`;
            const lotteryConfig = LOTTERY_CONFIG_JS[officialResults.loteria_tipo];
            const numbersToWin = lotteryConfig?.count_sorteadas || lotteryConfig?.count || 0;
            if (hits === numbersToWin && numbersToWin > 0) { 
                message += " Parabéns, você GANHOU o prêmio máximo!";
                triggerConfetti(); 
            }
        }
        return { hits: hits, hitNumbers: hitNumbers, almostNumbers: [], message: message }; 
    }

    async function loadUserGames(filterLottery = "todos") {
        if (!currentUser || !firestoreDB || !savedGamesContainer || !noSavedGamesP) return;
        savedGamesContainer.innerHTML = '<div class="spinner small-spinner"></div> Carregando...'; noSavedGamesP.style.display = 'none';
        try {
            let query = firestoreDB.collection('userGames').where('userId', '==', currentUser.uid).orderBy('savedAt', 'desc');
            if (filterLottery !== "todos") query = query.where('lottery', '==', filterLottery);
            const snapshot = await query.get(); savedGamesContainer.innerHTML = '';
            if (snapshot.empty) { noSavedGamesP.style.display = 'block'; return; }
            snapshot.forEach(doc => { const gameCard = createGameCardElement(doc.id, doc.data()); if(gameCard) savedGamesContainer.appendChild(gameCard); });
        } catch (error) { console.error("Erro jogos salvos:", error); savedGamesContainer.innerHTML = '<p class="error-message">Erro ao carregar.</p>'; }
    }

    function createGameCardElement(docId, gameData) {
        const card = document.createElement('div'); card.classList.add('card', 'game-card'); card.dataset.id = docId;
        const lotteryName = LOTTERY_CONFIG_JS[gameData.lottery]?.name || gameData.lottery.toUpperCase();
        const gameNumbersDiv = document.createElement('div'); gameNumbersDiv.classList.add('game-numbers');
        renderGameNumbers(gameNumbersDiv, gameData.game, [], [], gameData.lottery);
        const strategyP = document.createElement('p'); strategyP.classList.add('strategy-text'); strategyP.textContent = `Estratégia: ${gameData.strategy || 'N/A'}`;
        const dateP = document.createElement('p'); dateP.classList.add('game-card-info'); dateP.textContent = `Salvo em: ${gameData.savedAt ? new Date(gameData.savedAt.toDate()).toLocaleDateString() : 'N/A'}`;
        const actionsDiv = document.createElement('div'); actionsDiv.classList.add('game-card-actions');
        const deleteBtn = document.createElement('button'); deleteBtn.classList.add('action-btn', 'small-btn'); deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Excluir';
        deleteBtn.addEventListener('click', async () => { if (confirm("Excluir este jogo?")) { try { await firestoreDB.collection('userGames').doc(docId).delete(); card.remove(); if (savedGamesContainer.children.length === 0) noSavedGamesP.style.display = 'block'; } catch (e) { alert("Erro ao excluir.");}}});
        actionsDiv.appendChild(deleteBtn); card.innerHTML = `<h4>${lotteryName}</h4>`;
        card.appendChild(gameNumbersDiv); card.appendChild(strategyP); card.appendChild(dateP); card.appendChild(actionsDiv);
        return card;
    }

    function updateManualProbNumbersFeedback() {
        if (!manualProbLotteryTypeSelect || !manualProbUserNumbersInput || !manualProbNumbersCountFeedback) return;
        const selectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex];
        const expectedCount = selectedOption ? parseInt(selectedOption.dataset.count, 10) : 0;
        const numbersStr = manualProbUserNumbersInput.value;
        const userNumbersCount = numbersStr.split(/[ ,;/\t\n]+/).filter(n => n.trim() !== "" && !isNaN(n)).length;
        manualProbNumbersCountFeedback.textContent = `Números: ${userNumbersCount} de ${expectedCount}.`;
    }
    
    // --- INICIALIZAÇÃO E EVENT LISTENERS ---
    function setupAuthEventListeners() {
        if(loginSubmitBtn && loginEmailInput && loginPasswordInput && loginErrorP) {
            loginSubmitBtn.addEventListener('click', () => { 
                if (!firebaseAuth) { if(loginErrorP) loginErrorP.textContent = "Erro de inicialização."; return; }
                const email = loginEmailInput.value; const password = loginPasswordInput.value;
                loginErrorP.textContent = ""; if (!email || !password) { loginErrorP.textContent = "Preencha email e senha."; return; }
                firebaseAuth.signInWithEmailAndPassword(email, password)
                    .then(() => { if(typeof closeModal === "function") closeModal(loginModal); })
                    .catch((error) => { loginErrorP.textContent = `Erro: ${error.message}`; });
            });
        }
        if(registerSubmitBtn && registerEmailInput && registerPasswordInput && registerConfirmPasswordInput && registerErrorP) {
            registerSubmitBtn.addEventListener('click', () => { 
                if (!firebaseAuth) { if(registerErrorP) registerErrorP.textContent = "Erro de inicialização."; return; }
                const email = registerEmailInput.value; const password = registerPasswordInput.value; const confirmPassword = registerConfirmPasswordInput.value;
                registerErrorP.textContent = ""; if (!email || !password || !confirmPassword) { registerErrorP.textContent = "Preencha todos os campos."; return; }
                if (password !== confirmPassword) { registerErrorP.textContent = "As senhas não coincidem."; return; }
                if (password.length < 6) { registerErrorP.textContent = "A senha deve ter no mínimo 6 caracteres."; return; }
                firebaseAuth.createUserWithEmailAndPassword(email, password)
                    .then(() => { alert("Usuário registrado! Você já está logado."); if(typeof closeModal === "function") closeModal(registerModal); })
                    .catch((error) => { registerErrorP.textContent = `Erro: ${error.message}`; });
            });
        }
        if(logoutBtn) {
            logoutBtn.addEventListener('click', () => { if (firebaseAuth && currentUser) { firebaseAuth.signOut().then(() => {}).catch(e => alert(e.message)); } });
        }
    }
    
    function initializeFirebase() {
        if (typeof firebase !== 'undefined' && typeof firebaseConfig !== 'undefined') {
            try {
                if (firebase.apps.length === 0) { firebaseApp = firebase.initializeApp(firebaseConfig); } else { firebaseApp = firebase.app(); }
                firebaseAuth = firebase.auth(firebaseApp); firestoreDB = firebase.firestore(firebaseApp);
                if (typeof setupAuthEventListeners === "function") setupAuthEventListeners();
                
                firebaseAuth.onAuthStateChanged(user => {
                    currentUser = user;
                    if (typeof updateLoginUI === "function") updateLoginUI(user);
                    
                    // A lógica de mostrar o conteúdo AGORA é gerenciada por handleWelcomeChoice ou effectivelyShowApp
                    // Esta callback só atualiza o estado do usuário e a UI correspondente.
                    // Se a escolha de voz já foi feita e a splash principal já sumiu, podemos mostrar o conteúdo.
                    if (localStorage.getItem('voiceGuideChoiceMade') === 'true') {
                        if (splashHiddenTimestamp > 0 || (mainSplashScreen && mainSplashScreen.classList.contains('hidden')) ) {
                            if (typeof effectivelyShowApp === "function") effectivelyShowApp();
                        }
                        // Se a splash principal ainda não sumiu, o timeout dela chamará effectivelyShowApp.
                    } else if (typeof effectivelyShowApp === "function" && (!inclusiveWelcomeScreen || inclusiveWelcomeScreen.classList.contains('hidden'))) {
                        // Fallback se a tela de boas-vindas foi pulada ou escondeu e o app não carregou
                        const timeSinceDOMLoad = Date.now() - domContentLoadedTimestamp;
                        let delayToHideMainSplash = (mainSplashScreen && !mainSplashScreen.classList.contains('hidden') && splashHiddenTimestamp === 0 && timeSinceDOMLoad < SPLASH_MINIMUM_VISIBLE_TIME) ? SPLASH_MINIMUM_VISIBLE_TIME - timeSinceDOMLoad : 0;
                        setTimeout(effectivelyShowApp, delayToHideMainSplash);
                    }
                });
                if (typeof enableFirebaseFeatures === "function") enableFirebaseFeatures();
                return true;
            } catch (error) { console.error("SCRIPT.JS: CRITICAL Firebase init error:", error); if (typeof showGlobalError === "function") showGlobalError(`Erro Firebase: ${error.message}`); if (typeof disableFirebaseFeatures === "function") disableFirebaseFeatures(); return false; }
        } else { 
            console.error("SCRIPT.JS: Firebase SDK ou firebaseConfig não definidos."); 
            if (typeof effectivelyShowApp === "function") { 
                const timeSinceDOMLoad = Date.now() - domContentLoadedTimestamp;
                setTimeout(effectivelyShowApp, SPLASH_MINIMUM_VISIBLE_TIME > timeSinceDOMLoad ? SPLASH_MINIMUM_VISIBLE_TIME - timeSinceDOMLoad : 0); 
            } 
            if(typeof disableFirebaseFeatures === "function") disableFirebaseFeatures(); 
            return false; 
        }
    }

    function attemptFirebaseInit() {
        if (!initializeFirebase()) {
            firebaseInitAttempts++;
            if (firebaseInitAttempts < maxFirebaseInitAttempts) setTimeout(attemptFirebaseInit, 500);
            else { 
                if (typeof showGlobalError === "function") showGlobalError("Não foi possível carregar os serviços. Tente recarregar."); 
                if(typeof disableFirebaseFeatures === "function") disableFirebaseFeatures();
                if (typeof effectivelyShowApp === "function") { effectivelyShowApp(); }
            }
        }
    }

    function effectivelyShowApp() {
        if (criticalSplashTimeout) { clearTimeout(criticalSplashTimeout); criticalSplashTimeout = null; }
        
        // Esconde a tela de boas-vindas se ainda estiver visível
        if (inclusiveWelcomeScreen && !inclusiveWelcomeScreen.classList.contains('hidden')) {
            inclusiveWelcomeScreen.classList.add('hidden'); 
        }
        // Esconde a splash principal se ainda estiver visível
        if (mainSplashScreen && !mainSplashScreen.classList.contains('hidden') && splashHiddenTimestamp === 0) { 
            mainSplashScreen.classList.add('hidden');
            splashHiddenTimestamp = Date.now();
        }
        showAppContentNow(); // Mostra o conteúdo do aplicativo
    }
    
    function showAppContentNow() { // Esta função agora SÓ mostra o conteúdo e faz fetches
        if (appContent && appContent.style.display === 'none') { 
            appContent.style.display = 'block';
            if (typeof setActiveSection === "function") setActiveSection('dashboard-section');
            if (typeof fetchPlatformStats === "function") fetchPlatformStats();
            if (typeof fetchRecentWinningPools === "function") fetchRecentWinningPools();
            if (typeof fetchTopWinners === "function") fetchTopWinners();
            if (typeof renderBanners === "function") renderBanners();
            if (typeof initializeCarousels === "function") initializeCarousels();
            if (mainDisplayLotterySelect) {
                const initialLottery = mainDisplayLotterySelect.value;
                if (typeof fetchAndDisplayResults === "function") fetchAndDisplayResults(initialLottery);
                if (typeof fetchAndDisplayFrequencyStats === "function") fetchAndDisplayFrequencyStats(initialLottery);
                if (typeof fetchAndDisplayPairFrequencyStats === "function") fetchAndDisplayPairFrequencyStats(initialLottery);
                if (typeof fetchAndDisplayCityStats === "function") fetchAndDisplayCityStats(initialLottery);
                if (typeof fetchAndDisplayCityPrizeSumStats === "function") fetchAndDisplayCityPrizeSumStats(initialLottery);
                setTimeout(() => { if (mainDisplayLotterySelect.dispatchEvent) mainDisplayLotterySelect.dispatchEvent(new Event('change')); }, 300);
            }
        }
    }

    // --- LÓGICA DA TELA DE BOAS-VINDAS INCLUSIVA ---
    function handleWelcomeChoice(activate) {
        clearTimeout(welcomeScreenTimeout); 
        setVoiceGuideState(activate); // Define o estado global e atualiza o botão do header
        localStorage.setItem('voiceGuideChoiceMade', 'true'); 
        if (activate) {
            speak("Guia de voz ativado. A interface principal será carregada.");
            localStorage.removeItem('voiceGuideDeclined');
        } else {
            // speak("Guia de voz desativado. Carregando a interface."); // Opcional
            localStorage.setItem('voiceGuideDeclined', 'true');
        }
        if (inclusiveWelcomeScreen) inclusiveWelcomeScreen.classList.add('hidden'); 
        if (mainSplashScreen) mainSplashScreen.style.display = 'flex'; // Mostra a splash principal

        // Animação da Splash Principal
        if (splashProgressBarFill && splashProgressContainer && mainSplashScreen && !mainSplashScreen.classList.contains('hidden')) {
            let progress = 0; const totalVisualBarTime = SPLASH_PROGRESS_BAR_START_DELAY + SPLASH_PROGRESS_BAR_FILL_DURATION; const intervalTime = Math.max(10, totalVisualBarTime / 100);
            const progressInterval = setInterval(() => { progress++; if (splashProgressContainer) splashProgressContainer.setAttribute('aria-valuenow', progress); if (progress >= 100) { clearInterval(progressInterval); } }, intervalTime);
        }
        
        // Timeout para a splash principal ANTES de mostrar o conteúdo do app
        criticalSplashTimeout = setTimeout(() => { 
             if (splashHiddenTimestamp === 0 && typeof effectivelyShowApp === "function") { 
                effectivelyShowApp(); 
            } else if (typeof effectivelyShowApp === "function" && mainSplashScreen && mainSplashScreen.classList.contains('hidden') && appContent.style.display === 'none'){
                effectivelyShowApp();
            }
             if (!firebaseApp && typeof showGlobalError === "function") { showGlobalError("Falha crítica na inicialização."); if(typeof disableFirebaseFeatures === "function") disableFirebaseFeatures();}
             criticalSplashTimeout = null; 
        }, SPLASH_MINIMUM_VISIBLE_TIME + 1000); 

        // Inicia o carregamento do Firebase AGORA, após a escolha na tela de boas-vindas
        if (typeof attemptFirebaseInit === "function") { 
            setTimeout(attemptFirebaseInit, 100); // Pequeno delay para a splash aparecer
        } else {  
            if (typeof effectivelyShowApp === "function") effectivelyShowApp(); 
            if(typeof disableFirebaseFeatures === "function") disableFirebaseFeatures(); 
        }
    }
    
    function initializeInclusiveWelcome() {
        if (localStorage.getItem('voiceGuideChoiceMade') === 'true') {
            const guideWasActive = localStorage.getItem('voiceGuideActive') === 'true';
            handleWelcomeChoice(guideWasActive); 
            return;
        }

        if (inclusiveWelcomeScreen) inclusiveWelcomeScreen.style.display = 'flex';
        if (mainSplashScreen) mainSplashScreen.style.display = 'none'; 
        if (voiceCommandBtn) voiceCommandBtn.style.display = 'none'; 

        const playInitialGreetingAndListen = () => {
            if (voiceGuideActive !== null || !inclusiveWelcomeScreen || inclusiveWelcomeScreen.classList.contains('hidden')) return;
            const greeting = "Bem-vindo ao Loto Genius AI. Esta plataforma é inclusiva. Deseja ativar o guia de voz? Diga 'Sim' ou 'Não', ou use os botões na tela.";
            speak(greeting, {
                onEndCallback: () => {
                    if (recognition && !isListening && voiceGuideActive === null) { 
                        isListening = true; awaitingSpecificInput = true;
                        recognition.onresult = (event) => { 
                            const transcript = event.results[event.results.length-1][0].transcript.trim().toLowerCase();
                            awaitingSpecificInput = false; isListening = false; recognition.onresult = defaultRecognitionResultHandler; 
                            clearTimeout(welcomeScreenTimeout); 
                            if (transcript.includes('sim')) { handleWelcomeChoice(true); }
                            else if (transcript.includes('não')) { handleWelcomeChoice(false); }
                        };
                        recognition.onerror = (event) => {console.error("Erro welcome listen:", event.error); awaitingSpecificInput = false; isListening = false; recognition.onresult = defaultRecognitionResultHandler; clearTimeout(welcomeScreenTimeout); if(voiceGuideActive === null) handleWelcomeChoice(false);};
                        recognition.onend = () => {
                            isListening = false; awaitingSpecificInput = false; recognition.onresult = defaultRecognitionResultHandler; 
                            if (voiceGuideActive === null && welcomeScreenTimeout) { // Se não foi destruído pelo clearTimeout
                                // O timeout vai pegar
                            }
                        };
                        try { recognition.start(); } catch (e) { console.error("Falha ao iniciar reconhecimento na saudação", e); isListening = false; awaitingSpecificInput = false;}
                    }
                }
            });
        };

        document.body.addEventListener('pointerdown', function handleFirstAudio() {
            if (!firstInteractionDoneForAudio) {
                firstInteractionDoneForAudio = true;
                let voiceCheckCount = 0;
                const checkAndPlay = () => { (speechSynthesis.getVoices().length > 0 || voiceCheckCount > 15) ? playInitialGreetingAndListen() : (voiceCheckCount++, setTimeout(checkAndPlay, 200)); };
                if (speechSynthesis.onvoiceschanged !== undefined && speechSynthesis.getVoices().length === 0) { 
                    speechSynthesis.onvoiceschanged = () => { setTimeout(checkAndPlay, 100); speechSynthesis.onvoiceschanged = null; }; 
                } else {
                    checkAndPlay(); 
                }
            }
        }, { capture: true, once: true });

        if (activateVoiceGuideBtn) activateVoiceGuideBtn.addEventListener('click', () => { clearTimeout(welcomeScreenTimeout); handleWelcomeChoice(true); });
        if (declineVoiceGuideBtn) declineVoiceGuideBtn.addEventListener('click', () => { clearTimeout(welcomeScreenTimeout); handleWelcomeChoice(false); });

        welcomeScreenTimeout = setTimeout(() => {
            if (voiceGuideActive === null && inclusiveWelcomeScreen && inclusiveWelcomeScreen.style.display !== 'none') { 
                handleWelcomeChoice(false); 
            }
        }, 20000); 
    }


    // --- INICIALIZAÇÃO PRINCIPAL DO SCRIPT ---
    initializeVoiceCommands(); // Configura as APIs de voz e o botão do header
    initializeInclusiveWelcome(); // Mostra a tela de boas-vindas primeiro
    
    // --- EVENT LISTENERS (Configurados após todas as funções estarem definidas) ---
    if(loginModalBtn) loginModalBtn.addEventListener('click', () => openModal(loginModal));
    if(registerModalBtn) registerModalBtn.addEventListener('click', () => openModal(registerModal));
    if(closeLoginModalBtn) closeLoginModalBtn.addEventListener('click', () => closeModal(loginModal));
    if(closeRegisterModalBtn) closeRegisterModalBtn.addEventListener('click', () => closeModal(registerModal));
    window.addEventListener('click', (event) => { if (event.target === loginModal) closeModal(loginModal); if (event.target === registerModal) closeModal(registerModal); });
    if (navDashboardBtn) navDashboardBtn.addEventListener('click', () => setActiveSection('dashboard-section'));
    if (navMyGamesBtn) navMyGamesBtn.addEventListener('click', () => { setActiveSection('my-games-section'); if (currentUser && typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); });
    if (navPoolsBtn) navPoolsBtn.addEventListener('click', () => setActiveSection('pools-section'));
    
    if (mainDisplayLotterySelect) { 
        mainDisplayLotterySelect.addEventListener('change', (e) => { 
            const selectedLottery = e.target.value; 
            const selectedOption = e.target.options[e.target.selectedIndex]; 
            const lotteryFriendlyName = selectedOption ? selectedOption.text : (LOTTERY_CONFIG_JS[selectedLottery] ? LOTTERY_CONFIG_JS[selectedLottery].name : selectedLottery.toUpperCase());
            if (resultsLotteryNameSpan) resultsLotteryNameSpan.textContent = lotteryFriendlyName; 
            if(freqStatsLotteryNameSpan) freqStatsLotteryNameSpan.textContent = lotteryFriendlyName; 
            if(pairFreqStatsLotteryNameSpan) pairFreqStatsLotteryNameSpan.textContent = lotteryFriendlyName; 
            if(cityStatsLotteryNameSpan) cityStatsLotteryNameSpan.textContent = lotteryFriendlyName; 
            if(cityPrizeSumLotteryNameSpan) cityPrizeSumLotteryNameSpan.textContent = lotteryFriendlyName;
            if (typeof fetchAndDisplayResults === "function") fetchAndDisplayResults(selectedLottery); 
            if (typeof fetchAndDisplayFrequencyStats === "function") fetchAndDisplayFrequencyStats(selectedLottery); 
            if (typeof fetchAndDisplayPairFrequencyStats === "function") fetchAndDisplayPairFrequencyStats(selectedLottery); 
            if (typeof fetchAndDisplayCityStats === "function") fetchAndDisplayCityStats(selectedLottery); 
            if (typeof fetchAndDisplayCityPrizeSumStats === "function") fetchAndDisplayCityPrizeSumStats(selectedLottery);
        }); 
    }
    if (fetchResultsBtn && mainDisplayLotterySelect) { 
        fetchResultsBtn.addEventListener('click', () => { 
            const selectedLottery = mainDisplayLotterySelect.value;
            if (typeof fetchAndDisplayResults === "function") fetchAndDisplayResults(selectedLottery); 
            if (typeof fetchAndDisplayFrequencyStats === "function") fetchAndDisplayFrequencyStats(selectedLottery); 
            if (typeof fetchAndDisplayPairFrequencyStats === "function") fetchAndDisplayPairFrequencyStats(selectedLottery); 
            if (typeof fetchAndDisplayCityStats === "function") fetchAndDisplayCityStats(selectedLottery); 
            if (typeof fetchAndDisplayCityPrizeSumStats === "function") fetchAndDisplayCityPrizeSumStats(selectedLottery);
        }); 
    }
    if (generateQuickHunchBtn) generateQuickHunchBtn.addEventListener('click', generateAndDisplayQuickHunch);
    if (generateEsotericHunchBtn) generateEsotericHunchBtn.addEventListener('click', generateAndDisplayEsotericHunch);
    if (generateHotNumbersHunchBtn) generateHotNumbersHunchBtn.addEventListener('click', generateAndDisplayHotNumbersHunch);
    if (typeof setupSaveHunchButtonListeners === "function") setupSaveHunchButtonListeners();
    if (typeof setupCheckHunchButtonListeners === "function") setupCheckHunchButtonListeners();
    
    if (promoRegisterBtn) { // Verificação adicionada
        promoRegisterBtn.addEventListener('click', () => { if (typeof openModal === "function") openModal(registerModal); });
    }
    if (promoLoginBtn && typeof openModal === "function") { // Verificação mantida
        promoLoginBtn.addEventListener('click', () => openModal(loginModal));
    }
    
    if (filterLotteryMyGamesSelect) { filterLotteryMyGamesSelect.addEventListener('change', (e) => { if (currentUser && typeof loadUserGames === "function") loadUserGames(e.target.value); });}
    
    if (manualProbUserNumbersInput && manualProbLotteryTypeSelect) { 
        manualProbUserNumbersInput.addEventListener('input', updateManualProbNumbersFeedback);
        manualProbLotteryTypeSelect.addEventListener('change', () => { 
            const selectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex]; 
            if (!selectedOption || !selectedOption.dataset.count || !selectedOption.dataset.min || !selectedOption.dataset.max) return;
            manualProbUserNumbersInput.placeholder = `Ex: 01,02,... (${selectedOption.dataset.count} de ${selectedOption.dataset.min}-${selectedOption.dataset.max})`; 
            manualProbUserNumbersInput.value = ''; 
            if (typeof updateManualProbNumbersFeedback === "function") updateManualProbNumbersFeedback(); 
            if(manualProbabilityResultDisplay) manualProbabilityResultDisplay.textContent = "Aguardando seu jogo...";
        });
        const initialSelectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex];
         if (initialSelectedOption && initialSelectedOption.dataset.count && initialSelectedOption.dataset.min && initialSelectedOption.dataset.max){ 
            manualProbUserNumbersInput.placeholder = `Ex: 01,02,... (${initialSelectedOption.dataset.count} de ${initialSelectedOption.dataset.min}-${initialSelectedOption.dataset.max})`; 
         }
        if (typeof updateManualProbNumbersFeedback === "function") updateManualProbNumbersFeedback(); 
    }
    if (manualCalculateProbBtn) { 
        manualCalculateProbBtn.addEventListener('click', async () => { 
            if (!manualProbLotteryTypeSelect || !manualProbUserNumbersInput || !manualProbabilityResultDisplay || typeof fetchData !== 'function') return;
            const lotteryType = manualProbLotteryTypeSelect.value; 
            const numbersStr = manualProbUserNumbersInput.value; 
            const userNumbersRaw = numbersStr.split(/[ ,;/\t\n]+/); 
            const userNumbers = userNumbersRaw.map(n => n.trim()).filter(n => n !== "" && !isNaN(n)).map(n => parseInt(n,10));
            const selectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex]; 
            const expectedCount = parseInt(selectedOption.dataset.count, 10);
            if (userNumbers.length === 0) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Insira os números.</p>`; return; }
            if (userNumbers.length !== expectedCount) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Forneça ${expectedCount} números.</p>`; return; }
            if (new Set(userNumbers).size !== userNumbers.length) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Números repetidos.</p>`; return; }
            const minNum = parseInt(selectedOption.dataset.min, 10); const maxNum = parseInt(selectedOption.dataset.max, 10);
            for (const num of userNumbers) { if (num < minNum || num > maxNum) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Número ${num} fora do range.</p>`; return; } }
            manualProbabilityResultDisplay.innerHTML = '<div class="spinner small-spinner"></div> Calculando...';
            try {
                const resultData = await fetchData(`api/main/jogo-manual/probabilidade`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ lottery_type: lotteryType, numeros_usuario: userNumbers }) });
                if (resultData.erro) { throw new Error(resultData.erro); }
                let displayText = `Loteria: <span class="highlight">${resultData.loteria}</span>\nSeu Jogo: <span class="highlight">${resultData.jogo_usuario.join(', ')}</span>\nProbabilidade: <span class="highlight">${resultData.probabilidade_texto}</span>`;
                if (resultData.probabilidade_decimal > 0) { displayText += ` (Decimal: ${resultData.probabilidade_decimal.toExponential(4)})`; }
                if(resultData.descricao) displayText += `\n<small>${resultData.descricao}</small>`;
                manualProbabilityResultDisplay.innerHTML = displayText.replace(/\n/g,'<br>');
            } catch (error) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Erro: ${error.message}</p>`; }
        }); 
    }
    console.log("SCRIPT.JS: Final do script atingido.");
});
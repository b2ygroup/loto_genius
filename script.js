document.addEventListener('DOMContentLoaded', () => {
    const domContentLoadedTimestamp = Date.now();

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
    const navMyMysteryGamesBtn = document.getElementById('nav-my-mystery-games-btn');
    const navPoolsBtn = document.getElementById('nav-pools-btn');
    const mainNav = document.getElementById('main-nav');
    const dashboardSection = document.getElementById('dashboard-section');
    const myGamesSection = document.getElementById('my-games-section');
    const myMysteryGamesSection = document.getElementById('my-mystery-games-section');
    const poolsSection = document.getElementById('pools-section');
    const mainSections = document.querySelectorAll('.main-section');

    const statsJogosGeradosSpan = document.getElementById('stats-jogos-gerados');
    const statsJogosPremiadosSpan = document.getElementById('stats-jogos-premiados');
    const statsValorPremiosSpan = document.getElementById('stats-valor-premios');
    const recentPoolsList = document.getElementById('recent-pools-list');
    const topWinnersList = document.getElementById('top-winners-list');

    const mainLotterySelect = document.getElementById('main-lottery-select');
    const refreshAllDashboardDataBtn = document.getElementById('refresh-all-dashboard-data-btn');
    const dynamicLotteryNameInfoSpan = document.getElementById('dynamic-lottery-name-info');
    const dynamicLotteryNameHunchLoggedOutSpan = document.getElementById('dynamic-lottery-name-hunch-logged-out');
    const dynamicLotteryNameManualSpan = document.getElementById('dynamic-lottery-name-manual');
    
    const dynamicLotteryNameMysterySpan = document.getElementById('dynamic-lottery-name-mystery'); 
    const buyMysteryGameBtn = document.getElementById('buy-mystery-game-btn'); 
    const mysteryGamePriceSpan = document.getElementById('mystery-game-price'); 
    const mysteryGamePurchaseStatusDiv = document.getElementById('mystery-game-purchase-status'); 
    const myMysteryGamesContainer = document.getElementById('my-mystery-games-container');


    const hunchGeneratorsSectionLoggedOut = document.getElementById('hunch-generators-section-logged-out');
    const generateQuickHunchBtnLoggedOut = document.getElementById('generate-quick-hunch-btn-logged-out');
    const quickHunchOutputDivLoggedOut = document.getElementById('quick-hunch-output-logged-out');
    const quickHunchNumbersDivLoggedOut = document.getElementById('quick-hunch-numbers-logged-out');
    const quickHunchStrategyPLoggedOut = document.getElementById('quick-hunch-strategy-logged-out');
    const checkQuickHunchBtnLoggedOut = document.getElementById('check-quick-hunch-btn-logged-out');
    const quickHunchCheckResultDivLoggedOut = document.getElementById('quick-hunch-check-result-logged-out');

    const loggedInHunchTabsSection = document.getElementById('logged-in-hunch-tabs-section');
    const tabLinks = document.querySelectorAll('.tabs-navigation .tab-link');
    const tabPanels = document.querySelectorAll('.tabs-content .tab-panel');
    const dynamicLotteryNameHunchTabsSpan = document.getElementById('dynamic-lottery-name-hunch-tabs');

    const generateQuickHunchBtn = document.getElementById('generate-quick-hunch-btn');
    const quickHunchOutputDiv = document.getElementById('quick-hunch-output');
    const quickHunchNumbersDiv = document.getElementById('quick-hunch-numbers');
    const quickHunchStrategyP = document.getElementById('quick-hunch-strategy');
    const saveQuickHunchBtn = document.getElementById('save-quick-hunch-btn');
    const checkQuickHunchBtn = document.getElementById('check-quick-hunch-btn');
    const quickHunchCheckResultDiv = document.getElementById('quick-hunch-check-result');

    const hotNumbersAnalyzeCountInput = document.getElementById('hot-numbers-analyze-count');
    const generateHotNumbersHunchBtn = document.getElementById('generate-hot-numbers-hunch-btn');
    const hotNumbersHunchOutputDiv = document.getElementById('hot-numbers-hunch-output');
    const hotNumbersHunchNumbersDiv = document.getElementById('hot-numbers-hunch-numbers');
    const hotNumbersHunchStrategyP = document.getElementById('hot-numbers-hunch-strategy');
    const saveHotHunchBtn = document.getElementById('save-hot-hunch-btn');
    const checkHotHunchBtn = document.getElementById('check-hot-hunch-btn');
    const hotHunchCheckResultDiv = document.getElementById('hot-hunch-check-result');

    const coldNumbersAnalyzeCountInput = document.getElementById('cold-numbers-analyze-count');
    const generateColdNumbersHunchBtn = document.getElementById('generate-cold-numbers-hunch-btn');
    const coldNumbersHunchOutputDiv = document.getElementById('cold-numbers-hunch-output');
    const coldNumbersHunchNumbersDiv = document.getElementById('cold-numbers-hunch-numbers');
    const coldNumbersHunchStrategyP = document.getElementById('cold-numbers-hunch-strategy');
    const saveColdHunchBtn = document.getElementById('save-cold-hunch-btn');
    const checkColdHunchBtn = document.getElementById('check-cold-hunch-btn');
    const coldNumbersHunchCheckResultDiv = document.getElementById('cold-hunch-check-result'); 

    const esotericHunchCard = document.getElementById('esoteric-hunch-card');
    const birthDateInput = document.getElementById('birth-date-input');
    const generateEsotericHunchBtn = document.getElementById('generate-esoteric-hunch-btn');
    const esotericHunchOutputDiv = document.getElementById('esoteric-hunch-output');
    const esotericHunchNumbersDiv = document.getElementById('esoteric-hunch-numbers');
    const esotericHunchMethodP = document.getElementById('esoteric-hunch-method');
    const esotericHunchHistoryCheckDiv = document.getElementById('esoteric-hunch-history-check');
    const saveEsotericHunchBtn = document.getElementById('save-esoteric-hunch-btn');
    const checkEsotericHunchBtn = document.getElementById('check-esoteric-hunch-btn');
    
    const generateLogicHunchBtn = document.getElementById('generate-logic-hunch-btn');
    const logicHunchOutputDiv = document.getElementById('logic-hunch-output');
    const logicHunchNumbersDiv = document.getElementById('logic-hunch-numbers');
    const logicHunchStrategyP = document.getElementById('logic-hunch-strategy');
    const saveLogicHunchBtn = document.getElementById('save-logic-hunch-btn');
    const checkLogicHunchBtn = document.getElementById('check-logic-hunch-btn');
    const logicHunchCheckResultDiv = document.getElementById('logic-hunch-check-result');
    const frequencyListContainerLogicTab = document.getElementById('frequency-list-container-logic-tab');

    const cosmicPromoBanner = document.getElementById('cosmic-promo-banner');
    const promoRegisterBtn = document.getElementById('promo-register-btn');
    const promoLoginBtn = document.getElementById('promo-login-btn');

    const apiResultsPre = document.getElementById('api-results');
    
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
    const prizeNotificationModal = document.getElementById('prize-notification-modal');


    const frequencyListContainer = document.getElementById('frequency-list-container');
    const pairFrequencyListContainer = document.getElementById('pair-frequency-list-container');
    const cityListContainer = document.getElementById('city-list-container');
    const cityPrizeSumListContainer = document.getElementById('city-prize-sum-list-container');

    const manualProbUserNumbersInput = document.getElementById('manual-prob-user-numbers');
    const manualCalculateProbBtn = document.getElementById('manual-calculate-prob-btn');
    const manualProbabilityResultDisplay = document.getElementById('manual-probability-result-display');
    const manualProbNumbersCountFeedback = document.getElementById('manual-prob-numbers-count-feedback');

    const manualSaveUserNumbersInput = document.getElementById('manual-save-user-numbers');
    const manualSaveNumbersCountFeedback = document.getElementById('manual-save-numbers-count-feedback');
    const manualSaveGameBtn = document.getElementById('manual-save-game-btn');
    const manualSaveGameResultDisplay = document.getElementById('manual-save-game-result-display');

    const verifyPastGameCardTitleDynamicSpan = document.getElementById('verify-past-game-title-dynamic');
    const pastGameContestInput = document.getElementById('past-game-contest');
    const pastGameNumbersInput = document.getElementById('past-game-numbers');
    const pastGameNumbersLabel = document.getElementById('past-game-numbers-label');
    const verifyPastGameBtn = document.getElementById('verify-past-game-btn');
    const verifyPastGameResultDiv = document.getElementById('verify-past-game-result');


    const savedGamesContainer = document.getElementById('saved-games-container');
    const noSavedGamesP = document.getElementById('no-saved-games');
    const filterLotteryMyGamesSelect = document.getElementById('filter-lottery-mygames');

    const editGameModal = document.getElementById('edit-game-modal');
    const closeEditGameModalBtn = document.getElementById('close-edit-game-modal');
    const editGameDocIdInput = document.getElementById('edit-game-doc-id');
    const editGameLotteryDisplay = document.getElementById('edit-game-lottery-display');
    const editGameNumbersInput = document.getElementById('edit-game-numbers-input');
    const editGameNumbersLabel = document.getElementById('edit-game-numbers-label');
    const editGameNumbersFeedback = document.getElementById('edit-game-numbers-feedback');
    const submitEditGameBtn = document.getElementById('submit-edit-game-btn');
    const editGameErrorP = document.getElementById('edit-game-error');


    let splashProgressBarFill = mainSplashScreen ? mainSplashScreen.querySelector('.progress-bar-fill') : null;
    let splashProgressContainer = mainSplashScreen ? mainSplashScreen.querySelector('.progress-bar-container') : null;

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
    let lastGeneratedHunchLoggedOut = { type: null, lottery: null, jogo: [], estrategia_metodo: '', outputDiv: null, numbersDiv: null, checkResultDiv: null, checkButton: null };

    let criticalSplashTimeout;
    let firebaseInitAttempts = 0;
    const maxFirebaseInitAttempts = 10;
    const LOTTERY_CONFIG_JS = {
        megasena: { count: 6, count_apostadas: 6, min:1, max:60, color: "#209869", name: "Mega-Sena", count_sorteadas: 6, preco_base: 5.0 },
        lotofacil: { count: 15, count_apostadas: 15, min:1, max:25, color: "#930089", name: "Lotofácil", count_sorteadas: 15, preco_base: 3.0 },
        quina: { count: 5, count_apostadas: 5, min:1, max:80, color: "#260085", name: "Quina", count_sorteadas: 5, preco_base: 2.5 },
        lotomania: { count_sorteadas: 20, count_apostadas: 50, min:0, max:99, color: "#f78100", name: "Lotomania", preco_base: 3.0 }
    };
    const TAXA_SERVICO_MISTERIOSO = 1.50; 

    const bannerConfigurations = {
        'banner-top-dashboard': [
            { imageUrl: 'images/banner1.png', altText: 'Tammy\'s Store - Comprar agora!', linkUrl: 'https://www.instagram.com/tammysstore_/', isExternal: true },
            { imageUrl: 'images/teste1.png', altText: 'Loto Genius - A Sorte Inteligente',},
            { imageUrl: 'images/teste.png', altText: 'Recursos Premium Loto Genius', linkUrl: '#esoteric-hunch-card', isExternal: false }
        ],
        'banner-bottom-dashboard': [
            { imageUrl: 'images/dream.jpg', altText: 'Anúncio Parceiro 1', linkUrl: 'https://www.parceiro1.com', isExternal: true },
            { imageUrl: 'images/banner2.png', altText: 'Anúncio Visual Lateral' }
        ]
    };

    let recognition;
    let speechSynthesis = window.speechSynthesis;
    let isListening = false;
    let voiceGuideActive = null;
    let firstInteractionDoneForAudio = false;
    let voiceContext = { action: null, awaiting: null, data: {} };
    let awaitingSpecificInput = false;


    function showGlobalError(message) { if (errorDiv) { errorDiv.textContent = message; errorDiv.style.display = 'block'; } else { console.error("Global error div não encontrado:", message); } }
    function disableFirebaseFeatures() { if (loginModalBtn) loginModalBtn.disabled = true; if (registerModalBtn) registerModalBtn.disabled = true; }
    function enableFirebaseFeatures() { if (loginModalBtn) loginModalBtn.disabled = false; if (registerModalBtn) registerModalBtn.disabled = false; if(document.getElementById('global-error-msg')) document.getElementById('global-error-msg').style.display = 'none';}

    function setActiveSection(sectionId) {
        if (!mainSections || mainSections.length === 0) { return; }
        mainSections.forEach(section => { 
            section.classList.remove('active-section'); 
            section.style.display = 'none'; 
            if (section.id === sectionId) {
                section.classList.add('active-section'); 
                section.style.display = 'block'; 
            }
        });
        if (mainNav) {
            const navButtons = mainNav.querySelectorAll('.nav-item');
            navButtons.forEach(btn => { 
                btn.classList.remove('active'); 
                const controlsId = btn.id.replace('nav-', '').replace('-btn', '-section');
                if (controlsId === sectionId) {
                    btn.classList.add('active');
                }
            });
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
                throw { status: response.status, message: messageDetail, data: errorJson };
            }
            if (response.status === 204 || !responseText) { return {}; }
            return JSON.parse(responseText);
        } catch (error) {
            if (error.status && error.message) { throw error; }
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
            if (stats && typeof stats.jogos_gerados_total === 'number') { animateCounter(statsJogosGeradosSpan, stats.jogos_gerados_total); } 
            else { statsJogosGeradosSpan.textContent = "N/A"; }

            if (stats && typeof stats.jogos_premiados_total === 'number') { animateCounter(statsJogosPremiadosSpan, stats.jogos_premiados_total); } 
            else { statsJogosPremiadosSpan.textContent = "N/A"; }

            if (stats && typeof stats.valor_premios_total_formatado === 'string') { statsValorPremiosSpan.textContent = stats.valor_premios_total_formatado; } 
            else { statsValorPremiosSpan.textContent = "R$ N/A"; }
        } catch (error) { 
            statsJogosGeradosSpan.textContent = "N/A"; 
            statsJogosPremiadosSpan.textContent = "N/A"; 
            statsValorPremiosSpan.textContent = "R$ N/A"; 
        }
    }

    async function fetchRecentWinningPools() { 
        if (!recentPoolsList) { return; }
        recentPoolsList.innerHTML = ''; 
        recentPoolsList.innerHTML = '<li>Funcionalidade de Bolões será implementada futuramente.</li>';
    }

    async function fetchTopWinners() { 
        if (!topWinnersList) { return; }
        topWinnersList.innerHTML = '<li><div class="spinner small-spinner"></div> Carregando...</li>';
        try {
            const winners = await fetchData('api/main/top-winners'); 
            topWinnersList.innerHTML = '';
            if (winners && winners.length > 0) { 
                winners.forEach((winner, index) => { 
                    const li = document.createElement('li'); 
                    const lotteryName = winner.lottery || 'Sorte Variada';
                    const dateInfo = winner.date || 'Data Recente';
                    li.innerHTML = `<span>${index + 1}. <i class="fas fa-user-astronaut winner-icon"></i> ${winner.nick || 'Ganhador Anônimo'}</span> <span class="winner-prize">${winner.prize_total}</span> <small>${lotteryName} - ${dateInfo}</small>`; 
                    topWinnersList.appendChild(li); 
                }); 
            }
            else { topWinnersList.innerHTML = '<li>Ranking de ganhadores indisponível ou ainda não populado.</li>'; }
        } catch (error) { 
            topWinnersList.innerHTML = '<li>Erro ao carregar ranking de ganhadores.</li>';
        }
    }

    function renderGameNumbers(container, gameNumbers, hitNumbers = [], almostNumbers = [], lotteryType = '') {
        if (!container) { return; }
        container.innerHTML = '';

        if (!gameNumbers || !Array.isArray(gameNumbers) || gameNumbers.length === 0) {
            return;
        }

        const lotteryConfig = LOTTERY_CONFIG_JS[lotteryType.toLowerCase()] || {};
        const defaultColor = '#47aeff';
        const numberColor = lotteryConfig.color || defaultColor;

        gameNumbers.forEach(num => {
            const numDiv = document.createElement('div');
            numDiv.classList.add('game-number');
            numDiv.textContent = String(num).padStart(2, '0');
            numDiv.style.backgroundColor = numberColor;
            numDiv.style.borderColor = numberColor;
            numDiv.style.color = '#1a1a2e';

            if (hitNumbers.includes(parseInt(num))) {
                numDiv.classList.add('hit');
                numDiv.style.backgroundColor = '#2ecc71';
                numDiv.style.color = '#fff';
            } else if (almostNumbers.includes(parseInt(num))) {
                numDiv.classList.add('almost');
                numDiv.style.backgroundColor = '#f1c40f';
                numDiv.style.color = '#333';
            }
            numDiv.style.opacity = '0';
            numDiv.style.transform = 'scale(0.8) translateY(10px)';
            setTimeout(() => {
                numDiv.style.opacity = '1';
                numDiv.style.transform = 'scale(1) translateY(0)';
            }, Math.random() * 200 + 50);

            container.appendChild(numDiv);
        });
    }

    async function fetchAndDisplayStatsGeneric(lotteryName, statType, container, endpointPrefix) {
        if (!container || !mainLotterySelect) { if(container) container.innerHTML = '<p class="error-message">Erro interno (stats).</p>'; return; }
        
        container.innerHTML = '<p class="loading-stats"><div class="spinner small-spinner"></div> Carregando...</p>';
        try {
            const result = await fetchData(`api/main/stats/${endpointPrefix}/${lotteryName}`);
            container.innerHTML = '';
            if (result.erro) { container.innerHTML = `<p class="error-message">${result.erro}</p>`; return; }
            const selectedLotteryConfig = LOTTERY_CONFIG_JS[lotteryName.toLowerCase()];
            const lotteryFriendlyName = selectedLotteryConfig ? selectedLotteryConfig.name : lotteryName.toUpperCase();
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
        } catch (error) { container.innerHTML = `<p class="error-message">Falha ao carregar.</p>`; }
    }

    function resetHunchDisplay(elements) {
        if (elements.outputDiv) elements.outputDiv.style.display = 'none';
        if (elements.numbersDiv) elements.numbersDiv.innerHTML = '';
        if (elements.strategyP) elements.strategyP.textContent = '';
        if (elements.checkResultDiv) elements.checkResultDiv.innerHTML = '';
        if (elements.saveButton) elements.saveButton.style.display = 'none';
        if (elements.checkButton) elements.checkButton.style.display = 'none';
    }

    function updateAllDashboardData(selectedLottery) {
        const selectedLotteryKey = selectedLottery.toLowerCase();
        const selectedLotteryConfig = LOTTERY_CONFIG_JS[selectedLotteryKey];
        const lotteryFriendlyName = selectedLotteryConfig ? selectedLotteryConfig.name : selectedLottery.toUpperCase();

        if (dynamicLotteryNameInfoSpan) dynamicLotteryNameInfoSpan.textContent = lotteryFriendlyName;
        if (dynamicLotteryNameHunchLoggedOutSpan) dynamicLotteryNameHunchLoggedOutSpan.textContent = lotteryFriendlyName;
        if (dynamicLotteryNameHunchTabsSpan) dynamicLotteryNameHunchTabsSpan.textContent = lotteryFriendlyName;
        if (dynamicLotteryNameManualSpan) dynamicLotteryNameManualSpan.textContent = lotteryFriendlyName;
        
        if (verifyPastGameCardTitleDynamicSpan) { 
            verifyPastGameCardTitleDynamicSpan.textContent = lotteryFriendlyName;
        }
        if (pastGameNumbersInput && selectedLotteryConfig) { 
            const expectedCount = selectedLotteryConfig.count_sorteadas || selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count; 
            const placeholderText = `Ex: 01,... (${expectedCount} números de ${selectedLotteryConfig.min}-${selectedLotteryConfig.max})`;
            pastGameNumbersInput.placeholder = placeholderText;
            if(pastGameNumbersLabel) pastGameNumbersLabel.textContent = `Seu Jogo (${expectedCount} números separados por vírgula):`;
            pastGameNumbersInput.value = ''; 
            if(verifyPastGameResultDiv) verifyPastGameResultDiv.style.display = 'none';
        }
        
        resetHunchDisplay({ 
            outputDiv: quickHunchOutputDivLoggedOut, numbersDiv: quickHunchNumbersDivLoggedOut,
            strategyP: quickHunchStrategyPLoggedOut, checkResultDiv: quickHunchCheckResultDivLoggedOut,
            checkButton: checkQuickHunchBtnLoggedOut
        });
        lastGeneratedHunchLoggedOut = { type: null };

        resetHunchDisplay({ 
            outputDiv: quickHunchOutputDiv, numbersDiv: quickHunchNumbersDiv,
            strategyP: quickHunchStrategyP, checkResultDiv: quickHunchCheckResultDiv,
            saveButton: saveQuickHunchBtn, checkButton: checkQuickHunchBtn
        });
        resetHunchDisplay({ 
            outputDiv: hotNumbersHunchOutputDiv, numbersDiv: hotNumbersHunchNumbersDiv,
            strategyP: hotNumbersHunchStrategyP, checkResultDiv: hotHunchCheckResultDiv,
            saveButton: saveHotHunchBtn, checkButton: checkHotHunchBtn
        });
        resetHunchDisplay({ 
            outputDiv: coldNumbersHunchOutputDiv, numbersDiv: coldNumbersHunchNumbersDiv,
            strategyP: coldNumbersHunchStrategyP, checkResultDiv: coldNumbersHunchCheckResultDiv,
            saveButton: saveColdHunchBtn, checkButton: checkColdHunchBtn
        });
        resetHunchDisplay({ 
            outputDiv: esotericHunchOutputDiv, numbersDiv: esotericHunchNumbersDiv,
            strategyP: esotericHunchMethodP, checkResultDiv: esotericHunchHistoryCheckDiv,
            saveButton: saveEsotericHunchBtn, checkButton: checkEsotericHunchBtn
        });
        resetHunchDisplay({
            outputDiv: logicHunchOutputDiv, numbersDiv: logicHunchNumbersDiv,
            strategyP: logicHunchStrategyP, checkResultDiv: logicHunchCheckResultDiv,
            saveButton: saveLogicHunchBtn, checkButton: checkLogicHunchBtn
        });

        if (esotericHunchHistoryCheckDiv) { 
             esotericHunchHistoryCheckDiv.innerHTML = 'Gere um palpite cósmico para ver o histórico e conferir.';
        }
        lastGeneratedHunch = { type: null };

        if (typeof fetchAndDisplayResults === "function") fetchAndDisplayResults(selectedLottery);
        if (typeof fetchAndDisplayStatsGeneric === "function") {
            if (frequencyListContainer) fetchAndDisplayStatsGeneric(selectedLottery, "Mais Sorteados", frequencyListContainer, "frequencia");
            if (pairFrequencyListContainer) fetchAndDisplayStatsGeneric(selectedLottery, "Pares Frequentes", pairFrequencyListContainer, "pares-frequentes");
            if (cityListContainer) fetchAndDisplayStatsGeneric(selectedLottery, "Cidades Premiadas", cityListContainer, "cidades-premiadas");
            if (cityPrizeSumListContainer) fetchAndDisplayStatsGeneric(selectedLottery, "Prêmios por Cidade", cityPrizeSumListContainer, "maiores-premios-cidade");
        }
        
        if (manualProbUserNumbersInput && selectedLotteryConfig) {
             const expectedCount = selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;
             manualProbUserNumbersInput.placeholder = `Ex: 01,02,... (${expectedCount} de ${selectedLotteryConfig.min}-${selectedLotteryConfig.max})`;
             manualProbUserNumbersInput.value = '';
             if (typeof updateManualProbNumbersFeedback === "function") updateManualProbNumbersFeedback();
             if(manualProbabilityResultDisplay) manualProbabilityResultDisplay.textContent = "Aguardando seu jogo...";
        }
        if (manualSaveUserNumbersInput && selectedLotteryConfig) {
            const expectedCount = selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;
            manualSaveUserNumbersInput.placeholder = `Ex: 01,02,... (${expectedCount} de ${selectedLotteryConfig.min}-${selectedLotteryConfig.max} para ${lotteryFriendlyName})`;
            if (typeof updateManualSaveNumbersFeedback === "function") updateManualSaveNumbersFeedback();
        }

        const activeTabLink = document.querySelector('.tabs-navigation .tab-link.active');
        if (currentUser && activeTabLink && activeTabLink.getAttribute('aria-controls') === 'tab-logic') {
            if (frequencyListContainerLogicTab) {
                fetchAndDisplayStatsGeneric(selectedLottery, "Mais Sorteados (Inspiração)", frequencyListContainerLogicTab, "frequencia");
            }
        }
    }

    async function fetchAndDisplayResults(lotteryName) {
        if (!apiResultsPre) { return; }
        apiResultsPre.innerHTML = '<div class="spinner small-spinner"></div> Carregando...';
        try {
            const data = await fetchData(`api/main/resultados/${lotteryName}`);
            lastFetchedResults[lotteryName] = data;
            if (data.aviso) { apiResultsPre.textContent = data.aviso; return; }
            if (data.erro) { apiResultsPre.textContent = `Erro: ${data.erro}`; return; }
            let content = `Concurso: ${data.ultimo_concurso || 'N/A'}\n`;
            content += `Data: ${data.data || 'N/A'}\n`;
            content += `Números: ${data.numeros ? data.numeros.join(', ') : 'N/A'}\n`;
            if (data.ganhadores_principal_contagem !== undefined) { content += `Ganhadores: ${data.ganhadores_principal_contagem}\n`; }
            if (data.cidades_ganhadoras_principal && data.cidades_ganhadoras_principal.length > 0) { content += `Cidades: ${data.cidades_ganhadoras_principal.join('; ')}\n`; }
             if (data.rateio_principal_valor !== undefined && data.rateio_principal_valor !== null) {
                 content += `Rateio: ${data.rateio_principal_valor}\n`; 
            } else {
                 content += `Rateio: N/A\n`;
            }
            apiResultsPre.textContent = content;
        } catch (error) { apiResultsPre.textContent = `Falha ao buscar resultados. ${error.message || ''}`; }
    }

    let previouslyFocusedElementModal;
    function openModal(modalElement) {
        if (modalElement) {
            previouslyFocusedElementModal = document.activeElement;
            modalElement.style.display = 'flex';
            document.body.style.overflow = 'hidden';
            const firstFocusableElement = modalElement.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusableElement) firstFocusableElement.focus();
        }
    }
    function closeModal(modalElement) {
        if (modalElement) {
            modalElement.style.display = 'none';
            document.body.style.overflow = '';
            if (modalElement === loginModal && loginEmailInput && loginPasswordInput && loginErrorP) { loginEmailInput.value = ''; loginPasswordInput.value = ''; loginErrorP.textContent = ''; }
            else if (modalElement === registerModal && registerEmailInput && registerPasswordInput && registerConfirmPasswordInput && registerErrorP) { registerEmailInput.value = ''; registerPasswordInput.value = ''; registerConfirmPasswordInput.value = ''; registerErrorP.textContent = ''; }
            else if (modalElement === editGameModal && editGameDocIdInput && editGameNumbersInput && editGameErrorP) { 
                editGameDocIdInput.value = ''; 
                editGameNumbersInput.value = ''; 
                if(editGameNumbersFeedback) editGameNumbersFeedback.textContent = '';
                editGameErrorP.textContent = ''; 
            }
            else if (modalElement.id === 'contact-modal') { // Limpeza específica para o modal de contato
                 const contactInfoDisplayToClear = document.getElementById('contact-info-display');
                 if (contactInfoDisplayToClear) {
                    contactInfoDisplayToClear.innerHTML = '';
                    contactInfoDisplayToClear.style.display = 'none';
                 }
            }
            if (previouslyFocusedElementModal) previouslyFocusedElementModal.focus();
        }
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

    function speak(text, options = {}) {
        if (!speechSynthesis || !text) { return; }
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
        }
    }

    function startListeningGeneralCommands(isContinuation = false) {
        if (recognition && voiceGuideActive && !isListening) {
            try {
                if (!isContinuation) { voiceContext = { action: null, awaiting: null, data: {} }; }
                recognition.start(); isListening = true;
                if(voiceCommandBtn) voiceCommandBtn.classList.add('listening');
            } catch (e) { isListening = false; if(voiceCommandBtn) voiceCommandBtn.classList.remove('listening'); }
        } else if (!voiceGuideActive) { speak("O guia de voz está desativado.");
        }
    }

    function processVoiceCommand(command) {
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
        if (command.includes('meus jogos') || command.includes('jogos salvos')) {
            if (!currentUser) { speak("Você precisa estar logado. Diga 'login'.", {shouldRelisten: true}); voiceContext.action = 'awaiting_login_for_my_games'; awaitingSpecificInput = true; return;}
            setActiveSection('my-games-section'); speak("Navegando para Meus Jogos Salvos."); return;
        }
        if (command.includes('jogos misteriosos')) {
            if (!currentUser) { speak("Você precisa estar logado para ver seus jogos misteriosos. Diga 'login'.", {shouldRelisten: true}); voiceContext.action = 'awaiting_login_for_mystery'; awaitingSpecificInput = true; return;}
            setActiveSection('my-mystery-games-section'); speak("Navegando para Meus Jogos Misteriosos. Esta funcionalidade está em breve!"); return;
        }
        if (voiceContext.action === 'awaiting_login_for_my_games' && command.includes('login')) {
            openModal(loginModal); speak("Tela de login aberta. Diga 'digitar email'.", {shouldRelisten: true}); voiceContext.action = 'login_prompt_email'; awaitingSpecificInput = true; return;
        }
        if (voiceContext.action === 'awaiting_login_for_mystery' && command.includes('login')) { 
            openModal(loginModal); speak("Tela de login aberta. Diga 'digitar email'.", {shouldRelisten: true}); voiceContext.action = 'login_prompt_email'; awaitingSpecificInput = true; return;
        }

        if ((command.includes('gerar') || command.includes('palpite')) && (command.includes('mega sena') || command.includes('mega'))) {
             if(mainLotterySelect) mainLotterySelect.value = 'megasena';
             if (typeof updateAllDashboardData === 'function') updateAllDashboardData('megasena');
             const activeHotTabLink = document.querySelector('.tab-link[aria-controls="tab-hot"]');
             const activeAlgoTabLink = document.querySelector('.tab-link[aria-controls="tab-algorithmic"]');

             if (currentUser) {
                if (command.includes('quente') && generateHotNumbersHunchBtn && activeHotTabLink) { if(typeof setActiveTab === "function") setActiveTab(activeHotTabLink); generateHotNumbersHunchBtn.click(); speak("Gerando palpite de números quentes para Mega-Sena.");}
                else if (activeAlgoTabLink && generateQuickHunchBtn) { if(typeof setActiveTab === "function") setActiveTab(activeAlgoTabLink); generateQuickHunchBtn.click(); speak("Gerando palpite algorítmico para Mega-Sena.");}

             } else if (generateQuickHunchBtnLoggedOut) {
                 generateQuickHunchBtnLoggedOut.click(); speak("Gerando palpite rápido para Mega-Sena.");
             }
             return;
        }
        if ((command.includes('gerar') || command.includes('palpite')) && (command.includes('lotofácil') || command.includes('fácil'))) {
            if(mainLotterySelect) mainLotterySelect.value = 'lotofacil';
            if (typeof updateAllDashboardData === 'function') updateAllDashboardData('lotofacil');
            const activeHotTabLink = document.querySelector('.tab-link[aria-controls="tab-hot"]');
            const activeAlgoTabLink = document.querySelector('.tab-link[aria-controls="tab-algorithmic"]');
            if (currentUser) {
                if (command.includes('quente') && generateHotNumbersHunchBtn && activeHotTabLink) { if(typeof setActiveTab === "function") setActiveTab(activeHotTabLink); generateHotNumbersHunchBtn.click(); speak("Gerando palpite de números quentes para Lotofácil.");}
                else if (activeAlgoTabLink && generateQuickHunchBtn) { if(typeof setActiveTab === "function") setActiveTab(activeAlgoTabLink); generateQuickHunchBtn.click(); speak("Gerando palpite algorítmico para Lotofácil.");}
            } else if (generateQuickHunchBtnLoggedOut) {
                generateQuickHunchBtnLoggedOut.click(); speak("Gerando palpite rápido para Lotofácil.");
            }
            return;
        }

        if (command.includes('ajuda') || command.includes('comandos')) {
            speak("Comandos: 'login', 'registrar', 'painel', 'meus jogos', 'jogos misteriosos', 'gerar mega sena rápido', 'onde estou'.", {shouldRelisten: true});
            awaitingSpecificInput = true; return;
        }
        if (command.includes('onde estou') || command.includes('descreva a tela')) {
            const activeSectionElement = document.querySelector('.main-section.active-section');
            let sectionName = "uma área desconhecida";
            if (activeSectionElement) {
                if (activeSectionElement.id === 'dashboard-section') sectionName = "o painel principal. Aqui pode gerar jogos e ver estatísticas";
                else if (activeSectionElement.id === 'my-games-section') sectionName = "a seção de Meus Jogos Salvos";
                else if (activeSectionElement.id === 'my-mystery-games-section') sectionName = "a seção dos seus Jogos Misteriosos, que está em breve";
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
                isListening = false; awaitingSpecificInput = false;
                if(voiceCommandBtn) voiceCommandBtn.classList.remove('listening');
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
                    if (voiceGuideActive) {
                        startListeningGeneralCommands();
                    } else {
                        setVoiceGuideState(true);
                        speak("Guia de voz ativado. Clique novamente para comandar ou diga um comando.");
                    }
                });
            }
             if (speechSynthesis.onvoiceschanged !== undefined) { speechSynthesis.onvoiceschanged = () => {}; }
        } else { if (voiceCommandBtn) voiceCommandBtn.style.display = 'none'; }
    }

    function setActiveTab(clickedLinkElement) {
        if (!clickedLinkElement || !tabLinks || !tabLinks.length || !tabPanels || !tabPanels.length) {
            return;
        }
        const targetPanelId = clickedLinkElement.getAttribute('aria-controls'); 
        tabLinks.forEach(link => {
            link.classList.remove('active');
            link.setAttribute('aria-selected', 'false');
        });
        clickedLinkElement.classList.add('active');
        clickedLinkElement.setAttribute('aria-selected', 'true');
        let panelActivated = false;
        tabPanels.forEach(panel => {
            panel.classList.remove('active'); 
            if (panel.id === targetPanelId) { 
                panel.classList.add('active'); 
                panelActivated = true;
            }
        });
        if (!panelActivated) {
            console.error("Nenhum painel encontrado com o ID: ", targetPanelId);
        }
        if (targetPanelId === 'tab-logic' && mainLotterySelect && frequencyListContainerLogicTab) {
            fetchAndDisplayStatsGeneric(mainLotterySelect.value, "Mais Sorteados (Inspiração)", frequencyListContainerLogicTab, "frequencia");
        }
    }
    
    if (tabLinks.length > 0) {
        tabLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                setActiveTab(e.currentTarget);
            });
        });
    }

    function updateLoginUI(user) {
        const navItems = document.querySelectorAll('#main-nav .nav-item');
        if (user) {
            if (loginModalBtn) loginModalBtn.style.display = 'none';
            if (registerModalBtn) registerModalBtn.style.display = 'none';
            if (userInfoDiv) userInfoDiv.style.display = 'flex';
            if (userEmailSpan) userEmailSpan.textContent = user.email.split('@')[0];
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
            if (mainNav) mainNav.style.display = 'flex';
            if (navItems) navItems.forEach(item => item.style.display = 'flex');

            if (loggedInHunchTabsSection) loggedInHunchTabsSection.style.display = 'block';
            if (hunchGeneratorsSectionLoggedOut) hunchGeneratorsSectionLoggedOut.style.display = 'none';
            if (cosmicPromoBanner) cosmicPromoBanner.style.display = 'none'; 

            if (typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos");
            if (typeof loadMyMysteryGames === "function") loadMyMysteryGames(); 
            if (typeof checkForPrizesAndNotify === 'function') checkForPrizesAndNotify(user.uid);
            
            const firstTabLink = document.querySelector('.tabs-navigation .tab-link[aria-controls="tab-hot"]');
            if (firstTabLink && typeof setActiveTab === 'function') {
                setActiveTab(firstTabLink);
            }

        } else { 
            if (loginModalBtn) loginModalBtn.style.display = 'inline-block';
            if (registerModalBtn) registerModalBtn.style.display = 'inline-block';
            if (userInfoDiv) userInfoDiv.style.display = 'none';
            if (userEmailSpan) userEmailSpan.textContent = '';
            if (logoutBtn) logoutBtn.style.display = 'none';
            if (mainNav) mainNav.style.display = 'none';
            if (navItems) navItems.forEach(item => item.style.display = 'none');

            if (loggedInHunchTabsSection) loggedInHunchTabsSection.style.display = 'none';
            if (hunchGeneratorsSectionLoggedOut) hunchGeneratorsSectionLoggedOut.style.display = 'block';
            if (cosmicPromoBanner) cosmicPromoBanner.style.display = 'block';

            if (savedGamesContainer) savedGamesContainer.innerHTML = '';
            if (noSavedGamesP) noSavedGamesP.style.display = 'block';
            if (myMysteryGamesContainer) myMysteryGamesContainer.innerHTML = '<p>Faça login para ver e comprar Jogos Misteriosos (Em Breve).</p>';
        }
        if (typeof updateSaveButtonVisibility === "function") {
            updateSaveButtonVisibility('quick');
            updateSaveButtonVisibility('esoteric');
            updateSaveButtonVisibility('hot');
            updateSaveButtonVisibility('cold');
            updateSaveButtonVisibility('logic');
        }
    }

    async function generateAndDisplayQuickHunchLoggedOut() {
        if (!mainLotterySelect || !generateQuickHunchBtnLoggedOut || !quickHunchOutputDivLoggedOut || !quickHunchNumbersDivLoggedOut || !quickHunchStrategyPLoggedOut) return;
        const lottery = mainLotterySelect.value;
        generateQuickHunchBtnLoggedOut.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';
        generateQuickHunchBtnLoggedOut.disabled = true;
        quickHunchOutputDivLoggedOut.style.display = 'block';
        quickHunchNumbersDivLoggedOut.innerHTML = '<div class="spinner small-spinner"></div>';
        quickHunchStrategyPLoggedOut.textContent = 'Gerando palpite...';
        if (checkQuickHunchBtnLoggedOut) checkQuickHunchBtnLoggedOut.style.display = 'none';
        if (quickHunchCheckResultDivLoggedOut) quickHunchCheckResultDivLoggedOut.innerHTML = '';

        try {
            const data = await fetchData(`api/main/gerar_jogo/${lottery}`);
            const config = LOTTERY_CONFIG_JS[lottery.toLowerCase()];
            const expectedCount = config ? (config.count_apostadas || config.count) : 0;
            if (data.erro) throw new Error(data.detalhes || data.erro);
            if (!data.jogo || !Array.isArray(data.jogo) || (expectedCount > 0 && data.jogo.length !== expectedCount) ) {
                throw new Error(`Palpite inválido. Esperava ${expectedCount} números para ${config ? config.name : lottery}. Recebido: ${data.jogo ? data.jogo.length : 0}`);
            }
            
            renderGameNumbers(quickHunchNumbersDivLoggedOut, data.jogo, [], [], lottery);
            quickHunchStrategyPLoggedOut.textContent = `Método: ${data.estrategia_usada || 'Aleatório'}`;
            lastGeneratedHunchLoggedOut = { type: 'quick-logged-out', lottery: lottery, jogo: data.jogo, estrategia_metodo: data.estrategia_usada || 'Aleatório', outputDiv: quickHunchOutputDivLoggedOut, numbersDiv: quickHunchNumbersDivLoggedOut, checkResultDiv: quickHunchCheckResultDivLoggedOut, checkButton: checkQuickHunchBtnLoggedOut };
            if (checkQuickHunchBtnLoggedOut) checkQuickHunchBtnLoggedOut.style.display = 'inline-block';
        } catch (error) {
            quickHunchNumbersDivLoggedOut.innerHTML = `<p class="error-message">${error.message || 'Falha ao gerar palpite.'}</p>`;
            quickHunchStrategyPLoggedOut.textContent = 'Erro ao gerar.';
            lastGeneratedHunchLoggedOut = { type: null };
        } finally {
            generateQuickHunchBtnLoggedOut.innerHTML = '<i class="fas fa-random"></i> Gerar Palpite Rápido';
            generateQuickHunchBtnLoggedOut.disabled = false;
        }
    }

    async function generateAndDisplayQuickHunch() { 
        if (!mainLotterySelect || !generateQuickHunchBtn || !quickHunchOutputDiv || !quickHunchNumbersDiv || !quickHunchStrategyP) { return; }
        const lottery = mainLotterySelect.value;
        generateQuickHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...'; generateQuickHunchBtn.disabled = true;
        quickHunchOutputDiv.style.display = 'block'; quickHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>'; quickHunchStrategyP.textContent = 'Gerando palpite...';
        if(saveQuickHunchBtn) saveQuickHunchBtn.style.display = 'none'; if(checkQuickHunchBtn) checkQuickHunchBtn.style.display = 'none'; if(quickHunchCheckResultDiv) quickHunchCheckResultDiv.innerHTML = '';
        try {
            const data = await fetchData(`api/main/gerar_jogo/${lottery}`);
            const config = LOTTERY_CONFIG_JS[lottery.toLowerCase()];
            const expectedCount = config ? (config.count_apostadas || config.count) : 0;

            if (data.erro) { throw new Error(data.detalhes || data.erro);  } 
            if (!data.jogo || !Array.isArray(data.jogo) || (expectedCount > 0 && data.jogo.length !== expectedCount)) { 
                throw new Error(`Palpite inválido. Esperava ${expectedCount} números para ${config ? config.name : lottery}. Recebido: ${data.jogo ? data.jogo.length : 'nenhum'}`);
            }
            renderGameNumbers(quickHunchNumbersDiv, data.jogo, [], [], lottery);
            quickHunchStrategyP.textContent = `Método: ${data.estrategia_usada || 'Aleatório Otimizado'}`;
            lastGeneratedHunch = { type: 'quick', lottery: lottery, jogo: data.jogo, estrategia_metodo: data.estrategia_usada || 'Aleatório Otimizado', outputDiv: quickHunchOutputDiv, numbersDiv: quickHunchNumbersDiv, checkResultDiv: quickHunchCheckResultDiv, saveButton: saveQuickHunchBtn, checkButton: checkQuickHunchBtn };
            if (typeof updateSaveButtonVisibility === "function") updateSaveButtonVisibility('quick'); if (checkQuickHunchBtn) checkQuickHunchBtn.style.display = 'inline-block';
        } catch (error) {
            quickHunchNumbersDiv.innerHTML = `<p class="error-message">${error.message || 'Falha ao gerar palpite.'}</p>`;
            quickHunchStrategyP.textContent = 'Erro ao gerar.';
            lastGeneratedHunch = { type: null };
        } finally {
            generateQuickHunchBtn.innerHTML = '<i class="fas fa-random"></i> Gerar Palpite';
            generateQuickHunchBtn.disabled = false;
        }
    }

    async function generateAndDisplayHotNumbersHunch() {
        if (!mainLotterySelect || !generateHotNumbersHunchBtn || !hotNumbersAnalyzeCountInput || !hotNumbersHunchOutputDiv || !hotNumbersHunchNumbersDiv || !hotNumbersHunchStrategyP) { return; }
        const lottery = mainLotterySelect.value;
        let analyzeCount = parseInt(hotNumbersAnalyzeCountInput.value, 10);
        if (isNaN(analyzeCount) || analyzeCount <= 0) { alert("Insira um número válido de concursos (mín. 1)."); hotNumbersAnalyzeCountInput.focus(); analyzeCount = 20; hotNumbersAnalyzeCountInput.value = analyzeCount; }
        generateHotNumbersHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...'; generateHotNumbersHunchBtn.disabled = true;
        hotNumbersHunchOutputDiv.style.display = 'block'; hotNumbersHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>'; hotNumbersHunchStrategyP.textContent = 'Analisando...';
        if(saveHotHunchBtn) saveHotHunchBtn.style.display = 'none'; if(checkHotHunchBtn) checkHotHunchBtn.style.display = 'none'; if(hotHunchCheckResultDiv) hotHunchCheckResultDiv.innerHTML = '';
        try {
            const data = await fetchData(`api/main/gerar_jogo/numeros_quentes/${lottery}?num_concursos_analisar=${analyzeCount}`);
            const config = LOTTERY_CONFIG_JS[lottery.toLowerCase()];
            const expectedCount = config ? (config.count_apostadas || config.count) : 0;

            if (data.erro) { throw new Error(data.detalhes || data.erro); } 
            if (!data.jogo || !Array.isArray(data.jogo) || (expectedCount > 0 && data.jogo.length !== expectedCount)) { 
                throw new Error(`Palpite inválido (quentes). Esperava ${expectedCount} números para ${config ? config.name : lottery}. Recebido: ${data.jogo ? data.jogo.length : 'nenhum'}`);
            }
            renderGameNumbers(hotNumbersHunchNumbersDiv, data.jogo, [], [], lottery);
            hotNumbersHunchStrategyP.textContent = `Método: ${data.estrategia_usada || 'Números Quentes'}`; if (data.aviso) { hotNumbersHunchStrategyP.textContent += ` (${data.aviso})`; }
            lastGeneratedHunch = { type: 'hot', lottery: lottery, jogo: data.jogo, estrategia_metodo: data.estrategia_usada || 'Números Quentes', outputDiv: hotNumbersHunchOutputDiv, numbersDiv: hotNumbersHunchNumbersDiv, checkResultDiv: hotHunchCheckResultDiv, saveButton: saveHotHunchBtn, checkButton: checkHotHunchBtn };
            if (typeof updateSaveButtonVisibility === "function") updateSaveButtonVisibility('hot'); if (checkHotHunchBtn) checkHotHunchBtn.style.display = 'inline-block';
        } catch (error) {
            hotNumbersHunchNumbersDiv.innerHTML = `<p class="error-message">${error.message || 'Falha.'}</p>`;
            hotNumbersHunchStrategyP.textContent = 'Erro.';
            lastGeneratedHunch = { type: null };
        } finally {
            generateHotNumbersHunchBtn.innerHTML = '<i class="fas fa-chart-line"></i> Gerar Palpite Quente';
            generateHotNumbersHunchBtn.disabled = false;
        }
    }

    async function generateAndDisplayColdNumbersHunch() {
        if (!mainLotterySelect || !generateColdNumbersHunchBtn || !coldNumbersAnalyzeCountInput || !coldNumbersHunchOutputDiv || !coldNumbersHunchNumbersDiv || !coldNumbersHunchStrategyP) {
            return;
        }
        const lottery = mainLotterySelect.value;
        let analyzeCount = parseInt(coldNumbersAnalyzeCountInput.value, 10);
        if (isNaN(analyzeCount) || analyzeCount <= 0) {
            alert("Insira um número válido de concursos para análise (mínimo 1).");
            coldNumbersAnalyzeCountInput.focus();
            analyzeCount = 20;
            coldNumbersAnalyzeCountInput.value = analyzeCount;
        }

        generateColdNumbersHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';
        generateColdNumbersHunchBtn.disabled = true;
        coldNumbersHunchOutputDiv.style.display = 'block';
        coldNumbersHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>';
        coldNumbersHunchStrategyP.textContent = 'Analisando números frios...';

        if(saveColdHunchBtn) saveColdHunchBtn.style.display = 'none';
        if(checkColdHunchBtn) checkColdHunchBtn.style.display = 'none';
        if(coldNumbersHunchCheckResultDiv) coldNumbersHunchCheckResultDiv.innerHTML = '';

        try {
            const data = await fetchData(`api/main/gerar_jogo/numeros_frios/${lottery}?num_concursos_analisar=${analyzeCount}`);
            const config = LOTTERY_CONFIG_JS[lottery.toLowerCase()];
            const expectedCount = config ? (config.count_apostadas || config.count) : 0;

            if (data.erro) {
                throw new Error(data.detalhes || data.erro);
            }
            if (!data.jogo || !Array.isArray(data.jogo) || (expectedCount > 0 && data.jogo.length !== expectedCount)) {
                throw new Error(`Palpite inválido (frios). Esperava ${expectedCount} números para ${config ? config.name : lottery}. Recebido: ${data.jogo ? data.jogo.length : 'nenhum'}`);
            }
            renderGameNumbers(coldNumbersHunchNumbersDiv, data.jogo, [], [], lottery);
            coldNumbersHunchStrategyP.textContent = `Método: ${data.estrategia_usada || 'Números Frios'}`;
            if (data.aviso) {
                coldNumbersHunchStrategyP.textContent += ` (${data.aviso})`;
            }
            lastGeneratedHunch = {
                type: 'cold',
                lottery: lottery,
                jogo: data.jogo,
                estrategia_metodo: data.estrategia_usada || 'Números Frios',
                outputDiv: coldNumbersHunchOutputDiv,
                numbersDiv: coldNumbersHunchNumbersDiv,
                checkResultDiv: coldNumbersHunchCheckResultDiv,
                saveButton: saveColdHunchBtn,
                checkButton: checkColdHunchBtn
            };
            if (typeof updateSaveButtonVisibility === "function") updateSaveButtonVisibility('cold');
            if (checkColdHunchBtn) checkColdHunchBtn.style.display = 'inline-block';
        } catch (error) {
            coldNumbersHunchNumbersDiv.innerHTML = `<p class="error-message">${error.message || 'Falha ao gerar palpite de números frios.'}</p>`;
            coldNumbersHunchStrategyP.textContent = 'Erro ao gerar.';
            lastGeneratedHunch = { type: null };
        } finally {
            generateColdNumbersHunchBtn.innerHTML = '<i class="fas fa-icicles"></i> Gerar Palpite Frio';
            generateColdNumbersHunchBtn.disabled = false;
        }
    }

    async function generateAndDisplayEsotericHunch() {
        if (!mainLotterySelect || !birthDateInput || !generateEsotericHunchBtn || !esotericHunchOutputDiv || !esotericHunchNumbersDiv || !esotericHunchMethodP || !esotericHunchHistoryCheckDiv) { return; }
        const lotteryName = mainLotterySelect.value;
        const birthDateRaw = birthDateInput.value.trim(); const birthDate = birthDateRaw.replace(/\D/g, '');
        if (!birthDate) { alert("Insira sua data de nascimento."); birthDateInput.focus(); return; } if (birthDate.length !== 8) { alert("Formato da data inválido. Use DDMMAAAA."); birthDateInput.focus(); return; }
        generateEsotericHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...'; generateEsotericHunchBtn.disabled = true;
        esotericHunchOutputDiv.style.display = 'block'; esotericHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>'; esotericHunchMethodP.textContent = 'Consultando...'; 
        esotericHunchHistoryCheckDiv.innerHTML = 'Verificando histórico...';
        if(saveEsotericHunchBtn) saveEsotericHunchBtn.style.display = 'none'; if(checkEsotericHunchBtn) checkEsotericHunchBtn.style.display = 'none';
        try {
            const requestBody = { data_nascimento: birthDate }; const data = await fetchData(`api/main/palpite-esoterico/${lotteryName}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(requestBody) });
            const config = LOTTERY_CONFIG_JS[lotteryName.toLowerCase()];
            const expectedCount = config ? (config.count_apostadas || config.count) : 0;
            
            if (data.erro) { throw new Error(data.erro); } 
            if (!data.palpite_gerado || !Array.isArray(data.palpite_gerado) || (expectedCount > 0 && data.palpite_gerado.length !== expectedCount)) { 
                throw new Error(`API não retornou palpite válido. Esperava ${expectedCount} números para ${config ? config.name : lotteryName}. Recebido: ${data.palpite_gerado ? data.palpite_gerado.length : 'nenhum'}`);
            }
            renderGameNumbers(esotericHunchNumbersDiv, data.palpite_gerado, [], [], lotteryName);
            esotericHunchMethodP.textContent = `Método: ${data.metodo_geracao || 'N/A'}`;
            let historyHtml = `<strong>Histórico desta combinação:</strong><br>`;
            if (data.historico_desta_combinacao) { const hist = data.historico_desta_combinacao; historyHtml += `Premiada (principal)? <span style="color: ${hist.ja_foi_premiada_faixa_principal ? '#2ecc71' : '#ff4765'}; font-weight: bold;">${hist.ja_foi_premiada_faixa_principal ? 'Sim' : 'Não'}</span> (${hist.vezes_premiada_faixa_principal}x) <br>Valor Total Histórico (principal): ${hist.valor_total_ganho_faixa_principal_formatado}`; } else { historyHtml += "Não verificado ou nunca premiado."; }
            esotericHunchHistoryCheckDiv.innerHTML = historyHtml;
            lastGeneratedHunch = { type: 'esoteric', lottery: lotteryName, jogo: data.palpite_gerado, estrategia_metodo: data.metodo_geracao || 'N/A', outputDiv: esotericHunchOutputDiv, numbersDiv: esotericHunchNumbersDiv, checkResultDiv: esotericHunchHistoryCheckDiv, saveButton: saveEsotericHunchBtn, checkButton: checkEsotericHunchBtn };
            if (typeof updateSaveButtonVisibility === "function") updateSaveButtonVisibility('esoteric'); if (checkEsotericHunchBtn) checkEsotericHunchBtn.style.display = 'inline-block';
        } catch (error) {
            esotericHunchNumbersDiv.innerHTML = '';
            esotericHunchMethodP.textContent = '';
            esotericHunchHistoryCheckDiv.innerHTML = `<p class="error-message">Falha: ${error.message || 'Erro.'}</p>`;
            lastGeneratedHunch = { type: null };
        } finally {
            generateEsotericHunchBtn.innerHTML = '<i class="fas fa-meteor"></i> Gerar Palpite Cósmico';
            generateEsotericHunchBtn.disabled = false;
        }
    }

    async function generateAndDisplayLogicHunch() {
        if (!mainLotterySelect || !generateLogicHunchBtn || !logicHunchOutputDiv || !logicHunchNumbersDiv || !logicHunchStrategyP) { return; }
        const lottery = mainLotterySelect.value;
        generateLogicHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...'; generateLogicHunchBtn.disabled = true;
        logicHunchOutputDiv.style.display = 'block'; logicHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>'; logicHunchStrategyP.textContent = 'Gerando palpite lógico...';
        if(saveLogicHunchBtn) saveLogicHunchBtn.style.display = 'none'; if(checkLogicHunchBtn) checkLogicHunchBtn.style.display = 'none'; if(logicHunchCheckResultDiv) logicHunchCheckResultDiv.innerHTML = '';
        try {
            const data = await fetchData(`api/main/gerar_jogo/logico/${lottery}`);
            const config = LOTTERY_CONFIG_JS[lottery.toLowerCase()];
            const expectedCount = config ? (config.count_apostadas || config.count) : 0;

            if (data.erro) { throw new Error(data.detalhes || data.erro);  } 
            if (!data.jogo || !Array.isArray(data.jogo) || (expectedCount > 0 && data.jogo.length !== expectedCount)) { 
                throw new Error(`Palpite lógico inválido. Esperava ${expectedCount} números para ${config ? config.name : lottery}. Recebido: ${data.jogo ? data.jogo.length : 'nenhum'}`);
            }
            renderGameNumbers(logicHunchNumbersDiv, data.jogo, [], [], lottery);
            logicHunchStrategyP.textContent = `Método: ${data.estrategia_usada || 'Lógica Estratégica'}`;
            lastGeneratedHunch = { type: 'logic', lottery: lottery, jogo: data.jogo, estrategia_metodo: data.estrategia_usada || 'Lógica Estratégica', outputDiv: logicHunchOutputDiv, numbersDiv: logicHunchNumbersDiv, checkResultDiv: logicHunchCheckResultDiv, saveButton: saveLogicHunchBtn, checkButton: checkLogicHunchBtn };
            if (typeof updateSaveButtonVisibility === "function") updateSaveButtonVisibility('logic'); if (checkLogicHunchBtn) checkLogicHunchBtn.style.display = 'inline-block';
        } catch (error) {
            logicHunchNumbersDiv.innerHTML = `<p class="error-message">${error.message || 'Falha ao gerar palpite lógico.'}</p>`;
            logicHunchStrategyP.textContent = 'Erro ao gerar.';
            lastGeneratedHunch = { type: null };
        } finally {
            generateLogicHunchBtn.innerHTML = '<i class="fas fa-cogs"></i> Gerar Palpite Lógico';
            generateLogicHunchBtn.disabled = false;
        }
    }


    function updateSaveButtonVisibility(hunchType) {
        const currentHunch = lastGeneratedHunch; 
        let targetSaveButton = null;
        if (hunchType === 'quick') targetSaveButton = saveQuickHunchBtn;
        else if (hunchType === 'esoteric') targetSaveButton = saveEsotericHunchBtn;
        else if (hunchType === 'hot') targetSaveButton = saveHotHunchBtn;
        else if (hunchType === 'cold') targetSaveButton = saveColdHunchBtn;
        else if (hunchType === 'logic') targetSaveButton = saveLogicHunchBtn;


        if (targetSaveButton) { 
            targetSaveButton.style.display = currentUser && currentHunch.type === hunchType && currentHunch.outputDiv && currentHunch.outputDiv.style.display !== 'none' ? 'inline-block' : 'none'; 
        }
    }

    function setupSaveHunchButtonListeners() {
        if (saveQuickHunchBtn) saveQuickHunchBtn.addEventListener('click', () => saveLastGeneratedHunch('quick'));
        if (saveEsotericHunchBtn) saveEsotericHunchBtn.addEventListener('click', () => saveLastGeneratedHunch('esoteric'));
        if (saveHotHunchBtn) saveHotHunchBtn.addEventListener('click', () => saveLastGeneratedHunch('hot'));
        if (saveColdHunchBtn) saveColdHunchBtn.addEventListener('click', () => saveLastGeneratedHunch('cold'));
        if (saveLogicHunchBtn) saveLogicHunchBtn.addEventListener('click', () => saveLastGeneratedHunch('logic'));
    }

    function saveLastGeneratedHunch(expectedHunchType) {
        if (!firestoreDB || !currentUser || !lastGeneratedHunch.jogo || !Array.isArray(lastGeneratedHunch.jogo) || lastGeneratedHunch.jogo.length === 0 || lastGeneratedHunch.type !== expectedHunchType) {
            alert("Logue-se e gere um palpite válido deste tipo para salvar."); return;
        }
        const { lottery, jogo, estrategia_metodo } = lastGeneratedHunch;
        firestoreDB.collection('userGames').add({ 
            userId: currentUser.uid, 
            userEmail: currentUser.email, 
            lottery: lottery, 
            game: jogo, 
            strategy: estrategia_metodo, 
            savedAt: firebase.firestore.FieldValue.serverTimestamp(), 
            isPremiado: false, 
            faixaPremio: "Não verificado", 
            acertos: 0, 
            numerosAcertados: [], 
            ultimoConcursoVerificado: null, 
            notificacaoPendente: false 
        })
            .then(() => { 
                alert("Palpite salvo!"); 
                if (myGamesSection && myGamesSection.classList.contains('active-section') && typeof loadUserGames === "function") { 
                    loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); 
                } 
            })
            .catch((error) => { 
                alert(`Erro ao salvar: ${error.message}`); 
            });
    }

    function setupCheckHunchButtonListeners() {
        if (checkQuickHunchBtnLoggedOut && mainLotterySelect) checkQuickHunchBtnLoggedOut.addEventListener('click', () => checkLastGeneratedHunch('quick-logged-out', mainLotterySelect));
        if (checkQuickHunchBtn && mainLotterySelect) checkQuickHunchBtn.addEventListener('click', () => checkLastGeneratedHunch('quick', mainLotterySelect));
        if (checkEsotericHunchBtn && mainLotterySelect) checkEsotericHunchBtn.addEventListener('click', () => checkLastGeneratedHunch('esoteric', mainLotterySelect));
        if (checkHotHunchBtn && mainLotterySelect) checkHotHunchBtn.addEventListener('click', () => checkLastGeneratedHunch('hot', mainLotterySelect));
        if (checkColdHunchBtn && mainLotterySelect) checkColdHunchBtn.addEventListener('click', () => checkLastGeneratedHunch('cold', mainLotterySelect));
        if (checkLogicHunchBtn && mainLotterySelect) checkLogicHunchBtn.addEventListener('click', () => checkLastGeneratedHunch('logic', mainLotterySelect));
    }

    async function checkLastGeneratedHunch(expectedHunchType, lotterySelectElement) {
        const currentLottery = lotterySelectElement.value;
        let currentHunchData;
        let targetCheckResultDiv = null;
        let targetNumbersDiv = null;

        if (expectedHunchType === 'quick-logged-out') {
            currentHunchData = lastGeneratedHunchLoggedOut;
            targetCheckResultDiv = quickHunchCheckResultDivLoggedOut;
            targetNumbersDiv = quickHunchNumbersDivLoggedOut;
        } else { 
            currentHunchData = lastGeneratedHunch;
            if (expectedHunchType === 'quick') { targetCheckResultDiv = quickHunchCheckResultDiv; targetNumbersDiv = quickHunchNumbersDiv; }
            else if (expectedHunchType === 'esoteric') { targetCheckResultDiv = esotericHunchHistoryCheckDiv; targetNumbersDiv = esotericHunchNumbersDiv; }
            else if (expectedHunchType === 'hot') { targetCheckResultDiv = hotHunchCheckResultDiv; targetNumbersDiv = hotNumbersHunchNumbersDiv; }
            else if (expectedHunchType === 'cold') { targetCheckResultDiv = coldNumbersHunchCheckResultDiv; targetNumbersDiv = coldNumbersHunchNumbersDiv; }
            else if (expectedHunchType === 'logic') { targetCheckResultDiv = logicHunchCheckResultDiv; targetNumbersDiv = logicHunchNumbersDiv; }

        }

        if (!currentHunchData.jogo || !Array.isArray(currentHunchData.jogo) || currentHunchData.jogo.length === 0 || currentHunchData.lottery !== currentLottery || currentHunchData.type !== expectedHunchType || !targetCheckResultDiv || !targetNumbersDiv ) {
            if(targetCheckResultDiv) targetCheckResultDiv.innerHTML = '<span class="misses">Gere um palpite deste tipo para esta loteria primeiro.</span>'; return;
        }
        let resultsToUse = lastFetchedResults[currentLottery];
        if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) {
            if(targetCheckResultDiv) targetCheckResultDiv.innerHTML = `<div class="spinner small-spinner"></div> Buscando resultados...`;
            try { resultsToUse = await fetchData(`api/main/resultados/${currentLottery}`); if(resultsToUse) resultsToUse.loteria_tipo = currentLottery; lastFetchedResults[currentLottery] = resultsToUse; }
            catch (e) { if(targetCheckResultDiv) targetCheckResultDiv.innerHTML = `<span class="misses">Falha ao buscar resultados.</span>`; return; }
        }
        if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || !resultsToUse.numeros.length === 0) { if(targetCheckResultDiv) targetCheckResultDiv.innerHTML = `<span class="misses">Resultados oficiais indisponíveis.</span>`; return; }

        if(typeof checkGame !== "function" || typeof renderGameNumbers !== "function") {
             if(targetCheckResultDiv) targetCheckResultDiv.innerHTML = "Erro interno (checkGame ou renderGameNumbers não definida).";
             return;
        }
        const result = checkGame(currentHunchData.jogo, resultsToUse);
        
        if (expectedHunchType === 'esoteric') { 
             let conferenceHtml = `<strong>Conferência com Último Resultado:</strong><br>`;
             conferenceHtml += `Acertos: <span class="${result.hits > 0 ? 'hits' : 'misses'}">${result.hits}</span>. ${result.message}`;
             if (targetCheckResultDiv) targetCheckResultDiv.innerHTML = conferenceHtml;
        } else {
            if (targetCheckResultDiv) targetCheckResultDiv.innerHTML = `<span class="${result.hits > 0 ? 'hits' : (result.almostNumbers && result.almostNumbers.length > 0 ? 'almost-text' : 'misses')}">${result.message}</span>`;
        }
        renderGameNumbers(targetNumbersDiv, currentHunchData.jogo, result.hitNumbers, result.almostNumbers || [], currentLottery);
    }

    function triggerConfetti() {
        if (!confettiCanvas) return;
        const parent = confettiCanvas.id === 'confetti-canvas-modal' ? confettiCanvas : document.body;
        for (let i = 0; i < 100; i++) {
            const confetti = document.createElement('div');
            confetti.classList.add('confetti');
            confetti.style.left = Math.random() * 100 + 'vw';
            confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 100%, 70%)`;
            const duration = Math.random() * 3 + 2;
            confetti.style.animationDuration = duration + 's';
            confetti.style.animationDelay = Math.random() * 0.5 + 's';
            confetti.addEventListener('animationend', () => { confetti.remove(); });
            if (parent.id === 'confetti-canvas-modal' || parent.id === 'confetti-canvas') {
                 parent.appendChild(confetti);
            } else {
                 document.body.appendChild(confetti);
            }
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
            const lotteryConfig = LOTTERY_CONFIG_JS[officialResults.loteria_tipo.toLowerCase()];
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
            snapshot.forEach(doc => {
                const gameCard = createGameCardElement(doc.id, doc.data());
                if(gameCard) savedGamesContainer.appendChild(gameCard);
            });
        } catch (error) {
            savedGamesContainer.innerHTML = `<p class="error-message">Erro ao carregar jogos salvos. Detalhe: ${error.message}</p>`;
        }
    }

    function createGameCardElement(docId, gameData) {
        const card = document.createElement('div');
        card.classList.add('card', 'game-card-item');
        if (gameData.isPremiado) {
            card.classList.add('premiado');
        }
        card.dataset.id = docId;
        const lotteryName = LOTTERY_CONFIG_JS[gameData.lottery]?.name || gameData.lottery.toUpperCase();
        const gameNumbersDiv = document.createElement('div'); gameNumbersDiv.classList.add('game-numbers');
    
        renderGameNumbers(gameNumbersDiv, gameData.game, gameData.numerosAcertados || [], [], gameData.lottery);
    
        const strategyP = document.createElement('p'); strategyP.classList.add('strategy-text'); strategyP.textContent = `Estratégia: ${gameData.strategy || 'N/A'}`;
        const dateP = document.createElement('p'); dateP.classList.add('game-card-info'); 
        let savedDateString = 'N/A';
        if (gameData.savedAt && gameData.savedAt.toDate) { 
            savedDateString = new Date(gameData.savedAt.toDate()).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
        } else if (gameData.savedAt) { 
            try {
                savedDateString = new Date(gameData.savedAt).toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
            } catch (e) { }
        }
        dateP.textContent = `Salvo em: ${savedDateString}`;
        
        const verificationStatusP = document.createElement('p');
        verificationStatusP.classList.add('game-card-info', 'verification-status');
        if (gameData.ultimoConcursoVerificado) {
            if (gameData.isPremiado) {
                verificationStatusP.innerHTML = `<i class="fas fa-trophy" style="color:gold;"></i> Premiado! ${gameData.acertos || '?'} acertos (${gameData.faixaPremio || 'Verifique detalhes'}). Verificado: Conc. ${gameData.ultimoConcursoVerificado}`;
                verificationStatusP.style.color = '#2ecc71';
            } else {
                verificationStatusP.innerHTML = `<i class="fas fa-check-circle" style="color: #a2d2ff;"></i> Não premiado. ${gameData.acertos || '0'} acertos. Verificado: Conc. ${gameData.ultimoConcursoVerificado}`;
                verificationStatusP.style.color = '#a2d2ff';
            }
        } else {
            verificationStatusP.textContent = gameData.faixaPremio === "Aguardando novo concurso" ? "Ativo para próximo concurso." : "Aguardando verificação.";
            verificationStatusP.style.fontStyle = 'italic';
            verificationStatusP.style.color = gameData.faixaPremio === "Aguardando novo concurso" ? '#82e0aa' : '#8899aa';
        }
    
        const actionsDiv = document.createElement('div'); actionsDiv.classList.add('game-card-actions');
        
        const editBtn = document.createElement('button');
        editBtn.classList.add('action-btn', 'small-btn', 'edit-game-btn');
        editBtn.innerHTML = '<i class="fas fa-edit"></i> Editar';
        
        const playAgainBtn = document.createElement('button');
        playAgainBtn.classList.add('action-btn', 'small-btn', 'play-again-btn');
        playAgainBtn.innerHTML = '<i class="fas fa-redo"></i> Jogar Novamente';
            
        if (gameData.faixaPremio === "Aguardando novo concurso" && gameData.ultimoConcursoVerificado === null) {
            playAgainBtn.title = "Este jogo já está ativo e aguardando o próximo sorteio.";
            playAgainBtn.disabled = true;
            playAgainBtn.innerHTML = '<i class="fas fa-hourglass-half"></i> Aguardando';
            playAgainBtn.classList.add('awaiting-draw'); 
            
            editBtn.title = "Não é possível editar um jogo que está aguardando o próximo sorteio.";
            editBtn.addEventListener('click', () => {
                alert("Este jogo está ativo para o próximo concurso e não pode ser editado até ser conferido.");
            });
        } else {
            playAgainBtn.title = "Exclui este jogo e o joga novamente no próximo concurso";
            playAgainBtn.addEventListener('click', () => handlePlayAgain(docId, gameData, card));
            editBtn.title = "Editar os números deste jogo";
            editBtn.addEventListener('click', () => openEditGameModal(docId, gameData));
        }
    
        const deleteBtn = document.createElement('button'); deleteBtn.classList.add('action-btn', 'small-btn', 'delete-game-btn'); 
        deleteBtn.innerHTML = '<i class="fas fa-trash"></i> Excluir';
        deleteBtn.addEventListener('click', async () => { 
            if (confirm("Excluir este jogo? Esta ação não pode ser desfeita.")) { 
                try { 
                    await firestoreDB.collection('userGames').doc(docId).delete(); 
                    card.remove(); 
                    if (savedGamesContainer.children.length === 0) {
                        noSavedGamesP.style.display = 'block';
                    }
                } catch (e) { 
                    alert("Erro ao excluir o jogo: " + e.message);
                }
            }
        });
        
        actionsDiv.appendChild(editBtn);
        actionsDiv.appendChild(playAgainBtn); 
        actionsDiv.appendChild(deleteBtn);
        
        card.innerHTML = `<h4>${lotteryName}</h4>`;
        card.appendChild(gameNumbersDiv);
        card.appendChild(strategyP);
        card.appendChild(dateP);
        card.appendChild(verificationStatusP);
        card.appendChild(actionsDiv);
        return card;
    }
    
    async function handlePlayAgain(originalDocId, originalGameData, gameCardElement) {
        if (!currentUser || !firestoreDB) {
            alert("Você precisa estar logado para jogar novamente.");
            openModal(loginModal);
            return;
        }
    
        if (!confirm(`Deseja realmente jogar novamente o jogo [${originalGameData.game.join(', ')}]? O jogo salvo original será removido e um novo será criado para o próximo concurso.`)) {
            return;
        }
    
        const playAgainButtonInCard = gameCardElement.querySelector('.play-again-btn');
        if (playAgainButtonInCard) {
            playAgainButtonInCard.disabled = true;
            playAgainButtonInCard.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';
        }
        
        let originalSavedDateStr = 'data antiga';
        if (originalGameData.savedAt && originalGameData.savedAt.toDate) {
            originalSavedDateStr = new Date(originalGameData.savedAt.toDate()).toLocaleDateString('pt-BR');
        } else if (originalGameData.savedAt) {
            try { originalSavedDateStr = new Date(originalGameData.savedAt).toLocaleDateString('pt-BR'); } catch (e) {}
        }
    
        const newGameEntry = {
            userId: currentUser.uid,
            userEmail: currentUser.email,
            lottery: originalGameData.lottery,
            game: originalGameData.game, 
            strategy: `Repetição (original de ${originalSavedDateStr})`,
            savedAt: firebase.firestore.FieldValue.serverTimestamp(),
            isPremiado: false,
            faixaPremio: "Aguardando novo concurso", 
            acertos: 0,
            numerosAcertados: [],
            ultimoConcursoVerificado: null, 
            notificacaoPendente: false
        };
    
        try {
            await firestoreDB.collection('userGames').add(newGameEntry);
            await firestoreDB.collection('userGames').doc(originalDocId).delete();
            
            const lotteryFriendlyName = LOTTERY_CONFIG_JS[originalGameData.lottery]?.name || originalGameData.lottery.toUpperCase();
            alert(`Jogo [${originalGameData.game.join(', ')}] original removido e uma nova versão foi ativada para o próximo concurso da ${lotteryFriendlyName}!`);
            
            if (myGamesSection.classList.contains('active-section')) {
                loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos");
            }
        } catch (error) {
            console.error("Erro ao tentar jogar novamente:", error);
            alert(`Erro ao tentar jogar novamente: ${error.message}. O jogo original pode não ter sido removido se a cópia falhou.`);
            if (playAgainButtonInCard) { 
                playAgainButtonInCard.disabled = false;
                playAgainButtonInCard.innerHTML = '<i class="fas fa-redo"></i> Jogar Novamente';
            }
        }
    }

    function openEditGameModal(docId, gameData) {
        if (!editGameModal || !editGameDocIdInput || !editGameLotteryDisplay || !editGameNumbersInput || !editGameNumbersLabel || !editGameNumbersFeedback || !editGameErrorP) {
            console.error("Elementos do modal de edição não encontrados."); 
            return;
        }

        editGameDocIdInput.value = docId;
        const lotteryConfig = LOTTERY_CONFIG_JS[gameData.lottery.toLowerCase()];
        const lotteryName = lotteryConfig?.name || gameData.lottery.toUpperCase();
        editGameLotteryDisplay.value = lotteryName;
        editGameLotteryDisplay.dataset.lotteryKey = gameData.lottery.toLowerCase();
        editGameNumbersInput.value = gameData.game.join(', ');

        if (lotteryConfig) {
            const expectedCount = lotteryConfig.count_apostadas || lotteryConfig.count;
            editGameNumbersLabel.textContent = `Seus números (${expectedCount} de ${lotteryConfig.min}-${lotteryConfig.max}, separados por vírgula):`;
            editGameNumbersInput.placeholder = `Ex: ${Array.from({ length: expectedCount }, (_, i) => String(i + 1).padStart(2, '0')).join(',')}`;
        } else {
            editGameNumbersLabel.textContent = `Seus números (separados por vírgula):`;
            editGameNumbersInput.placeholder = `Confirme a quantidade de números para esta loteria.`;
        }
        
        updateEditGameNumbersFeedback();
        editGameErrorP.textContent = '';
        openModal(editGameModal);
    }

    function updateEditGameNumbersFeedback() {
        if (!editGameLotteryDisplay || !editGameNumbersInput || !editGameNumbersFeedback) return;
        
        const lotteryKey = editGameLotteryDisplay.dataset.lotteryKey;
        const numbersStr = editGameNumbersInput.value;
        const userNumbersCount = numbersStr.split(/[ ,;/\t\n]+/).filter(n => n.trim() !== "" && !isNaN(n)).length;
        
        const selectedLotteryConfig = LOTTERY_CONFIG_JS[lotteryKey];

        if (selectedLotteryConfig) {
             const expectedCount = selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;
             editGameNumbersFeedback.textContent = `Números: ${userNumbersCount} de ${expectedCount}.`;
        } else {
            editGameNumbersFeedback.textContent = `Números: ${userNumbersCount}. (Configuração da loteria não encontrada)`;
        }
    }

    async function handleSaveEditedGame() {
        if (!currentUser || !firestoreDB || !editGameDocIdInput.value || !editGameLotteryDisplay || !editGameNumbersInput || !editGameErrorP) {
            alert("Erro interno ou dados do formulário de edição ausentes.");
            return;
        }

        const docId = editGameDocIdInput.value;
        const lotteryKey = editGameLotteryDisplay.dataset.lotteryKey;

        if (!lotteryKey) {
            editGameErrorP.textContent = "Chave da loteria não encontrada.";
            return;
        }
        const selectedLotteryConfig = LOTTERY_CONFIG_JS[lotteryKey];
        if (!selectedLotteryConfig) {
            editGameErrorP.textContent = "Configuração da loteria não encontrada.";
            return;
        }

        const numbersStr = editGameNumbersInput.value;
        const userNumbersRaw = numbersStr.split(/[ ,;/\t\n]+/);
        const userNumbers = userNumbersRaw.map(n => n.trim()).filter(n => n !== "" && !isNaN(n)).map(n => parseInt(n, 10));
        
        const expectedCount = selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;
        editGameErrorP.textContent = '';

        if (userNumbers.length === 0) {
            editGameErrorP.textContent = 'Insira os números do seu jogo.'; return;
        }
        if (userNumbers.length !== expectedCount) {
            editGameErrorP.textContent = `Forneça ${expectedCount} números para ${selectedLotteryConfig.name}. Você forneceu ${userNumbers.length}.`; return;
        }
        if (new Set(userNumbers).size !== userNumbers.length) {
            editGameErrorP.textContent = 'Seu jogo contém números repetidos.'; return;
        }
        const minNum = selectedLotteryConfig.min; const maxNum = selectedLotteryConfig.max;
        for (const num of userNumbers) {
            if (num < minNum || num > maxNum) {
                editGameErrorP.textContent = `O número ${num} está fora do range (${minNum}-${maxNum}) para ${selectedLotteryConfig.name}.`; return;
            }
        }

        const gameDocRef = firestoreDB.collection('userGames').doc(docId);

        const updatedGameData = {
            game: userNumbers.sort((a, b) => a - b),
            savedAt: firebase.firestore.FieldValue.serverTimestamp(),
            isPremiado: false,
            faixaPremio: "Não verificado (Editado)",
            acertos: 0,
            numerosAcertados: [],
            ultimoConcursoVerificado: null,
            notificacaoPendente: false,
            strategy: "Jogo Editado Manualmente" 
        };

        submitEditGameBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
        submitEditGameBtn.disabled = true;

        try {
            await gameDocRef.update(updatedGameData);
            alert("Jogo atualizado com sucesso! Ele será verificado no próximo concurso.");
            closeModal(editGameModal);
            if (myGamesSection.classList.contains('active-section')) {
                loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos");
            }
        } catch (error) {
            console.error("Erro ao atualizar jogo:", error);
            editGameErrorP.textContent = `Erro ao salvar: ${error.message}`;
        } finally {
            submitEditGameBtn.innerHTML = 'Salvar Alterações';
            submitEditGameBtn.disabled = false;
        }
    }


    async function checkForPrizesAndNotify(userId) {
        if (!firestoreDB || !userId) return;
        try {
            const gamesRef = firestoreDB.collection('userGames');
            const querySnapshot = await gamesRef
                                    .where('userId', '==', userId)
                                    .where('isPremiado', '==', true)
                                    .where('notificacaoPendente', '==', true)
                                    .get();

            if (!querySnapshot.empty) {
                const prizeDetailsContainer = document.getElementById('prize-details-container');
                const prizeMessage = document.getElementById('prize-message');
                const confettiModalCanvas = document.getElementById('confetti-canvas-modal');
                
                if(!prizeNotificationModal || !prizeDetailsContainer || !prizeMessage) { return; }

                prizeDetailsContainer.innerHTML = '';
                let firstPrize = true;
                let gamesToUpdate = [];

                querySnapshot.forEach(doc => {
                    const gameData = doc.data();
                    const gameDetail = document.createElement('p');
                    gameDetail.style.marginBottom = "0.5em";
                    gameDetail.innerHTML = `Jogo da <strong>${LOTTERY_CONFIG_JS[gameData.lottery]?.name || gameData.lottery}</strong> (Concurso: ${gameData.ultimoConcursoVerificado || 'N/A'}) - <strong>${gameData.acertos || '?'} acertos!</strong> Faixa: ${gameData.faixaPremio || 'Não especificada'}.`;
                    prizeDetailsContainer.appendChild(gameDetail);
                    gamesToUpdate.push(doc.id);

                    if (firstPrize && currentUser) {
                        prizeMessage.textContent = `Parabéns, ${currentUser.email.split('@')[0]}! Você tem jogos premiados!`;
                        firstPrize = false;
                    }
                });

                openModal(prizeNotificationModal);
                if(typeof triggerConfetti === 'function' && confettiModalCanvas) triggerConfetti(confettiModalCanvas);
                
                const okBtn = document.getElementById('ok-prize-modal-btn');
                const closeBtnPrize = document.getElementById('close-prize-modal');
                const copyPixBtn = document.getElementById('copy-pix-key-btn');

                const handleCloseAndMarkNotified = () => {
                    closeModal(prizeNotificationModal);
                    gamesToUpdate.forEach(gameId => {
                        firestoreDB.collection('userGames').doc(gameId).update({ notificacaoPendente: false })
                            .catch(err => {});
                    });
                    if(okBtn) okBtn.removeEventListener('click', handleCloseAndMarkNotified);
                    if(closeBtnPrize) closeBtnPrize.removeEventListener('click', handleCloseAndMarkNotified);
                };

                if(okBtn) okBtn.addEventListener('click', handleCloseAndMarkNotified, { once: true });
                if(closeBtnPrize) closeBtnPrize.addEventListener('click', handleCloseAndMarkNotified, { once: true });

                if (copyPixBtn) {
                    copyPixBtn.onclick = () => {
                        const pixKeyDisplay = document.getElementById('pix-key-display');
                        if(pixKeyDisplay) {
                            const pixKey = pixKeyDisplay.textContent;
                            navigator.clipboard.writeText(pixKey).then(() => {
                                alert('Chave PIX copiada para a área de transferência!');
                            }).catch(err => {
                                alert('Não foi possível copiar a chave PIX.');
                            });
                        }
                    };
                }
            }
        } catch (error) {}
    }

    function updateManualProbNumbersFeedback() {
        if (!mainLotterySelect || !manualProbUserNumbersInput || !manualProbNumbersCountFeedback) return;
        const selectedLotteryKey = mainLotterySelect.value.toLowerCase();
        const selectedLotteryConfig = LOTTERY_CONFIG_JS[selectedLotteryKey];

        if (!selectedLotteryConfig) {
            manualProbNumbersCountFeedback.textContent = 'Selecione uma loteria válida.';
             if(manualProbUserNumbersInput) manualProbUserNumbersInput.placeholder = `Selecione uma loteria acima.`;
            return;
        }

        const expectedCount = selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;
        const numbersStr = manualProbUserNumbersInput.value;
        const userNumbersCount = numbersStr.split(/[ ,;/\t\n]+/).filter(n => n.trim() !== "" && !isNaN(n)).length;
        manualProbNumbersCountFeedback.textContent = `Números: ${userNumbersCount} de ${expectedCount}.`;
        if(manualProbUserNumbersInput) manualProbUserNumbersInput.placeholder = `Ex: 01,02,... (${expectedCount} de ${selectedLotteryConfig.min}-${selectedLotteryConfig.max})`;
    }

    function updateManualSaveNumbersFeedback() {
        if (!mainLotterySelect || !manualSaveUserNumbersInput || !manualSaveNumbersCountFeedback) return;
        const selectedLotteryKey = mainLotterySelect.value.toLowerCase();
        const selectedLotteryConfig = LOTTERY_CONFIG_JS[selectedLotteryKey];

        if (!selectedLotteryConfig) {
            manualSaveNumbersCountFeedback.textContent = 'Selecione uma loteria válida.';
             if(manualSaveUserNumbersInput) manualSaveUserNumbersInput.placeholder = `Selecione uma loteria.`;
            return;
        }
        const expectedCount = selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;
        const numbersStr = manualSaveUserNumbersInput.value;
        const userNumbersCount = numbersStr.split(/[ ,;/\t\n]+/).filter(n => n.trim() !== "" && !isNaN(n)).length;
        manualSaveNumbersCountFeedback.textContent = `Números: ${userNumbersCount} de ${expectedCount}.`;
        if(manualSaveUserNumbersInput) manualSaveUserNumbersInput.placeholder = `Ex: 01,... (${expectedCount} de ${selectedLotteryConfig.min}-${selectedLotteryConfig.max} para ${selectedLotteryConfig.name})`;
    }

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
            logoutBtn.addEventListener('click', () => {
                if (firebaseAuth && currentUser) {
                    firebaseAuth.signOut()
                        .then(() => {
                            if(typeof setActiveSection === "function") setActiveSection('dashboard-section');
                        })
                        .catch(e => {
                            alert("Erro ao sair: " + e.message);
                        });
                }
            });
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
                    if (inclusiveWelcomeScreen && inclusiveWelcomeScreen.style.display === 'none') {
                        if (splashHiddenTimestamp > 0 || (mainSplashScreen && mainSplashScreen.style.display === 'none') ) {
                             if (typeof effectivelyShowApp === "function") effectivelyShowApp();
                        }
                    }
                });
                if (typeof enableFirebaseFeatures === "function") enableFirebaseFeatures();
                return true;
            } catch (error) { if (typeof showGlobalError === "function") showGlobalError(`Erro Firebase: ${error.message}`); if (typeof disableFirebaseFeatures === "function") disableFirebaseFeatures(); return false; }
        } else {
             if (inclusiveWelcomeScreen && inclusiveWelcomeScreen.style.display === 'none') {
                if (typeof effectivelyShowApp === "function") {
                    const timeSinceDOMLoad = Date.now() - domContentLoadedTimestamp;
                    setTimeout(effectivelyShowApp, SPLASH_MINIMUM_VISIBLE_TIME > timeSinceDOMLoad ? SPLASH_MINIMUM_VISIBLE_TIME - timeSinceDOMLoad : 0);
                }
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
        if (inclusiveWelcomeScreen && inclusiveWelcomeScreen.style.display !== 'none') {
            inclusiveWelcomeScreen.style.display = 'none';
        }
        if (mainSplashScreen && mainSplashScreen.style.display !== 'none' && splashHiddenTimestamp === 0) {
            mainSplashScreen.classList.add('hidden'); 
            splashHiddenTimestamp = Date.now();
        }
        showAppContentNow();
    }

    function showAppContentNow() {
        if (appContent && appContent.style.display === 'none') {
            appContent.style.display = 'block';
            if (typeof setActiveSection === "function") setActiveSection('dashboard-section');
            if (typeof fetchPlatformStats === "function") fetchPlatformStats();
            if (typeof fetchTopWinners === "function") fetchTopWinners();
            if (typeof renderBanners === "function") renderBanners();
            if (typeof initializeCarousels === "function") initializeCarousels();
            if (mainLotterySelect) {
                 updateAllDashboardData(mainLotterySelect.value);
            }
            if (currentUser) {
                const firstTabLink = document.querySelector('.tabs-navigation .tab-link[aria-controls="tab-hot"]'); 
                if (firstTabLink && typeof setActiveTab === 'function') {
                    setActiveTab(firstTabLink);
                }
            }
        }
    }

    function handleWelcomeChoice(activate) {
        if (inclusiveWelcomeScreen) {
            inclusiveWelcomeScreen.style.display = 'none'; 
        }
        if (mainSplashScreen) {
            mainSplashScreen.style.display = 'flex';
        }

        setTimeout(() => {
            try {
                setVoiceGuideState(activate);

                if (splashProgressBarFill && splashProgressContainer && mainSplashScreen && mainSplashScreen.style.display === 'flex') {
                    let progress = 0;
                    const totalVisualBarTime = SPLASH_MINIMUM_VISIBLE_TIME - 1000;
                    const intervalTime = Math.max(10, totalVisualBarTime / 100);
                    const progressInterval = setInterval(() => {
                        progress++;
                        if (splashProgressContainer) splashProgressContainer.setAttribute('aria-valuenow', progress);
                        if (progress >= 100) {
                            clearInterval(progressInterval);
                        }
                    }, intervalTime);
                }

                if (criticalSplashTimeout) { 
                    clearTimeout(criticalSplashTimeout);
                }
                criticalSplashTimeout = setTimeout(() => {
                    if (splashHiddenTimestamp === 0 && typeof effectivelyShowApp === "function") {
                        effectivelyShowApp();
                    } else if (typeof effectivelyShowApp === "function" && mainSplashScreen && (mainSplashScreen.classList.contains('hidden') || mainSplashScreen.style.display === 'none') && appContent && appContent.style.display === 'none'){
                         effectivelyShowApp();
                    }
                    criticalSplashTimeout = null;
                }, SPLASH_MINIMUM_VISIBLE_TIME + 500);

                if (typeof attemptFirebaseInit === "function") {
                    setTimeout(attemptFirebaseInit, 100);
                } else {
                    if (typeof effectivelyShowApp === "function") effectivelyShowApp();
                    if (typeof disableFirebaseFeatures === "function") disableFirebaseFeatures();
                }
            } catch (e) {
                console.error('Erro na lógica adiada de handleWelcomeChoice:', e);
                if (typeof effectivelyShowApp === "function") {
                     setTimeout(effectivelyShowApp, 150); 
                }
            }
        }, 10);
    }

    function initializeInclusiveWelcome() {
        if (inclusiveWelcomeScreen) inclusiveWelcomeScreen.style.display = 'flex';
        if (mainSplashScreen) mainSplashScreen.style.display = 'none';
        if (voiceCommandBtn) voiceCommandBtn.style.display = 'none';

        if (activateVoiceGuideBtn) activateVoiceGuideBtn.addEventListener('click', () => { handleWelcomeChoice(true); });
        if (declineVoiceGuideBtn) declineVoiceGuideBtn.addEventListener('click', () => { handleWelcomeChoice(false); });
    }
    
    function updateMysteryGameCardUI(lotteryKey) {
    }
    
    async function handleBuyMysteryGame() {
        if (!currentUser) {
            alert("Você precisa estar logado para comprar um Jogo Misterioso.");
            openModal(loginModal);
            return;
        }
        const actualBuyButton = document.getElementById('buy-mystery-game-btn'); 
        const actualStatusDiv = document.getElementById('mystery-game-purchase-status');
        
        if (!mainLotterySelect || !actualStatusDiv || !actualBuyButton) {
            const teaserStatusDiv = document.getElementById('mystery-game-purchase-status-teaser');
            if(teaserStatusDiv) {
                teaserStatusDiv.innerHTML = `<p style="color:#f0ad4e;">Esta funcionalidade estará disponível em breve!</p>`;
                teaserStatusDiv.style.display = 'block';
            }
            return;
        }
    }

    async function loadMyMysteryGames() {
        if (!myMysteryGamesContainer) return;
        myMysteryGamesContainer.innerHTML = '<p>Funcionalidade de "Meus Jogos Misteriosos" estará disponível em breve!</p>';
    }

    function createMysteryGameCard(game) { 
        const card = document.createElement('div');
        card.classList.add('card', 'game-card-item', 'mystery-card');
        card.dataset.orderId = game.order_id;
        
        if (game.status_pagamento !== 'pago') card.classList.add('pending-payment');
        if (game.dados_premiacao && game.dados_premiacao.foi_premiado) card.classList.add('premiado');

        const lotteryConfig = LOTTERY_CONFIG_JS[game.lottery_type.toLowerCase()] || { name: game.lottery_type.toUpperCase(), color: '#ccc' };
        
        let numbersHtml = '<div class="game-numbers">';
        (game.display_numeros || []).forEach(numStr => {
            let numClass = 'game-number';
            let numStyle = `background-color: #555; border-color: #777; color: #fff;`; 
            
            if (numStr === '?') {
                numClass += ' question-mark'; 
            } else if (numStr !== '-') { 
                numStyle = `background-color: ${lotteryConfig.color}; border-color: ${lotteryConfig.color}; color: #1a1a2e;`;
                if (game.status_revelacao === 'revelado' && game.dados_premiacao && game.dados_premiacao.numeros_que_acertou && game.dados_premiacao.numeros_que_acertou.includes(parseInt(numStr))) {
                    numClass += ' hit';
                    numStyle = `background-color: #2ecc71; color: #fff;`;
                }
            }
            numbersHtml += `<div class="${numClass}" style="${numStyle}">${String(numStr).padStart(2, '0')}</div>`;
        });
        numbersHtml += '</div>';

        if (game.status_revelacao === 'selado' && game.status_pagamento === 'pago'){
             const numbersContainerForBlur = card.querySelector('.game-numbers'); 
             if(numbersContainerForBlur) numbersContainerForBlur.classList.add('sealed-numbers');
        }

        let statusPagamentoDisplay = `Pagamento: <span class="${game.status_pagamento}">${game.status_pagamento}</span>`;
         if (game.status_pagamento === 'pendente' && game.link_pagamento_simulado_frontend) { 
             statusPagamentoDisplay += ` <a href="${game.link_pagamento_simulado_frontend}" target="_blank" class="action-btn small-btn">Pagar (Sim.)</a>`;
        }

        let revelacaoHtml = '';
        if (game.status_pagamento === 'pago' && game.status_revelacao === 'selado') {
            revelacaoHtml = `<button class="action-btn small-btn reveal-mystery-game-btn" data-order-id="${game.order_id}"><i class="fas fa-eye"></i> Revelar Agora!</button>`;
        } else if (game.status_revelacao === 'revelado') {
            revelacaoHtml = `<p class="strategy-text">Estratégia Usada: ${game.estrategia_usada || 'N/A'}</p>`;
            if (game.dados_premiacao) {
                revelacaoHtml += `<p class="game-card-info">Sorteio Oficial (Conc. ${game.concurso_oficial_referencia}): ${(game.dados_premiacao.numeros_sorteados_oficialmente || []).join(', ')}</p>`;
                revelacaoHtml += `<p class="game-card-info ${game.dados_premiacao.acertos > 0 ? 'hits' : 'misses'}">Seus Acertos: ${game.dados_premiacao.acertos} (${game.dados_premiacao.faixa_premio || ''})</p>`;
            }
        }
        
        card.innerHTML = `
            <h4>${lotteryConfig.name} (Misterioso)</h4>
            <p class="game-card-info">Pedido: ${game.order_id ? game.order_id.substring(0,8) : 'N/A'}...</p>
            <p class="game-card-info">Concurso Ref.: <strong>${game.concurso_oficial_referencia || 'N/A'}</strong></p>
            ${numbersHtml}
            <p class="game-card-info status-${game.status_pagamento}">${statusPagamentoDisplay}</p>
            <p class="game-card-info">Criado em: ${game.criado_em_display || 'N/A'}</p>
            <div class="mystery-game-reveal-status" style="margin-top:0.5rem; min-height: 2.5em;" aria-live="polite">${revelacaoHtml}</div>
        `;
        return card;
    }

    function addRevealButtonListeners() { 
        document.querySelectorAll('.reveal-mystery-game-btn').forEach(button => {
            button.removeEventListener('click', handleRevealClick); 
            button.addEventListener('click', handleRevealClick);
        });
    }

    async function handleRevealClick(event) { 
        const button = event.currentTarget;
        const orderId = button.dataset.orderId;
        const cardElement = button.closest('.game-card-item');
        const revealStatusDiv = cardElement.querySelector('.mystery-game-reveal-status');

        if (!revealStatusDiv) return;
        
        revealStatusDiv.innerHTML = '<div class="spinner small-spinner"></div> Revelando...';
        button.style.display = 'none'; 

        try {
            const result = await fetchData(`/api/main/jogo-misterioso/revelar/${orderId}`, { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId: currentUser.uid }) 
            });
            
            if (result.erro) throw new Error(result.erro);

            if (result.jogo_selado === true) { 
                 revealStatusDiv.innerHTML = `<p style="color:#f39c12; font-size: 0.9em;">${result.mensagem || result.aviso}</p><button class="action-btn small-btn reveal-mystery-game-btn" data-order-id="${orderId}"><i class="fas fa-sync-alt"></i> Tentar Revelar Novamente</button>`;
                 addRevealButtonListeners(); 
                 return;
            }
            
            const updatedGameDataFromServer = { 
                order_id: orderId,
                user_id: currentUser.uid,
                lottery_type: result.loteria.toLowerCase().replace('-',''), 
                concurso_oficial_referencia: result.concurso_referencia,
                display_numeros: result.seus_numeros_apostados, 
                numeros_gerados: result.seus_numeros_apostados, 
                estrategia_usada: result.estrategia_usada,
                status_pagamento: 'pago', 
                status_revelacao: 'revelado',
                criado_em_display: cardElement.querySelector('.game-card-info') ? cardElement.querySelector('.game-card-info').textContent.replace('Criado em: ','') : 'N/A', 
                dados_premiacao: {
                    foi_premiado: result.acertos > 0, 
                    numeros_sorteados_oficialmente: result.numeros_sorteados_oficialmente,
                    acertos: result.acertos,
                    numeros_que_acertou: result.numeros_que_acertou,
                    faixa_premio: result.faixa_premio
                }
            };

            const newCard = createMysteryGameCard(updatedGameDataFromServer);
            cardElement.parentNode.replaceChild(newCard, cardElement);
            newCard.classList.add('revealed-animation');
            if (result.acertos > 0 && typeof triggerConfetti === 'function') {
                triggerConfetti();
            }

        } catch (error) {
            revealStatusDiv.innerHTML = `<p class="error-message">Erro: ${error.message}</p><button class="action-btn small-btn reveal-mystery-game-btn" data-order-id="${orderId}"><i class="fas fa-sync-alt"></i> Tentar Novamente</button>`;
            addRevealButtonListeners(); 
        }
    }
    
    initializeVoiceCommands();
    initializeInclusiveWelcome();

    if(loginModalBtn) loginModalBtn.addEventListener('click', () => openModal(loginModal));
    if(registerModalBtn) registerModalBtn.addEventListener('click', () => openModal(registerModal));
    if(closeLoginModalBtn) closeLoginModalBtn.addEventListener('click', () => closeModal(loginModal));
    if(closeRegisterModalBtn) closeRegisterModalBtn.addEventListener('click', () => closeModal(registerModal));
    if(submitEditGameBtn) submitEditGameBtn.addEventListener('click', handleSaveEditedGame);
    if(closeEditGameModalBtn) closeEditGameModalBtn.addEventListener('click', () => closeModal(editGameModal));

    window.addEventListener('click', (event) => { 
        if (event.target === loginModal) closeModal(loginModal); 
        if (event.target === registerModal) closeModal(registerModal);
        if (event.target === editGameModal) closeModal(editGameModal);
        if (event.target === prizeNotificationModal) {
            const okBtn = document.getElementById('ok-prize-modal-btn');
            if (okBtn) okBtn.click();
        }
    });

    if (navDashboardBtn) navDashboardBtn.addEventListener('click', () => setActiveSection('dashboard-section'));
    if (navMyGamesBtn) navMyGamesBtn.addEventListener('click', () => { setActiveSection('my-games-section'); if (currentUser && typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); });
    if (navMyMysteryGamesBtn) navMyMysteryGamesBtn.addEventListener('click', () => { 
        setActiveSection('my-mystery-games-section'); 
        if (typeof loadMyMysteryGames === "function") loadMyMysteryGames(); 
    });
    if (navPoolsBtn) navPoolsBtn.addEventListener('click', () => setActiveSection('pools-section'));

    if (mainLotterySelect) {
        mainLotterySelect.addEventListener('change', (e) => {
            updateAllDashboardData(e.target.value);
        });
    }
    if (refreshAllDashboardDataBtn && mainLotterySelect) {
        refreshAllDashboardDataBtn.addEventListener('click', () => {
            updateAllDashboardData(mainLotterySelect.value);
        });
    }

    if (buyMysteryGameBtn) {
        buyMysteryGameBtn.addEventListener('click', handleBuyMysteryGame); 
    }
    if (editGameNumbersInput) {
        editGameNumbersInput.addEventListener('input', updateEditGameNumbersFeedback);
    }

    if (generateQuickHunchBtnLoggedOut) generateQuickHunchBtnLoggedOut.addEventListener('click', generateAndDisplayQuickHunchLoggedOut);
    if (generateQuickHunchBtn) generateQuickHunchBtn.addEventListener('click', generateAndDisplayQuickHunch);
    if (generateEsotericHunchBtn) generateEsotericHunchBtn.addEventListener('click', generateAndDisplayEsotericHunch);
    if (generateHotNumbersHunchBtn) generateHotNumbersHunchBtn.addEventListener('click', generateAndDisplayHotNumbersHunch);
    if (generateColdNumbersHunchBtn) generateColdNumbersHunchBtn.addEventListener('click', generateAndDisplayColdNumbersHunch);
    if (generateLogicHunchBtn) generateLogicHunchBtn.addEventListener('click', generateAndDisplayLogicHunch);


    if (typeof setupSaveHunchButtonListeners === "function") setupSaveHunchButtonListeners();
    if (typeof setupCheckHunchButtonListeners === "function") setupCheckHunchButtonListeners();

    if (promoRegisterBtn) promoRegisterBtn.addEventListener('click', () => { if (typeof openModal === "function") openModal(registerModal); });
    if (promoLoginBtn && typeof openModal === "function") promoLoginBtn.addEventListener('click', () => openModal(loginModal));

    if (filterLotteryMyGamesSelect) { filterLotteryMyGamesSelect.addEventListener('change', (e) => { if (currentUser && typeof loadUserGames === "function") loadUserGames(e.target.value); });}

    if (manualProbUserNumbersInput && mainLotterySelect) {
        manualProbUserNumbersInput.addEventListener('input', updateManualProbNumbersFeedback);
        mainLotterySelect.addEventListener('change', updateManualProbNumbersFeedback);
    }

    if (manualCalculateProbBtn) {
        manualCalculateProbBtn.addEventListener('click', async () => {
            if (!mainLotterySelect || !manualProbUserNumbersInput || !manualProbabilityResultDisplay || typeof fetchData !== 'function') return;
            const lotteryType = mainLotterySelect.value;
            const selectedLotteryConfig = LOTTERY_CONFIG_JS[lotteryType.toLowerCase()];
            if(!selectedLotteryConfig) {
                manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Configuração da loteria não encontrada.</p>`;
                return;
            }

            const numbersStr = manualProbUserNumbersInput.value;
            const userNumbersRaw = numbersStr.split(/[ ,;/\t\n]+/);
            const userNumbers = userNumbersRaw.map(n => n.trim()).filter(n => n !== "" && !isNaN(n)).map(n => parseInt(n,10));

            const expectedCount = selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;
            if (userNumbers.length === 0) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Insira os números.</p>`; return; }
            if (new Set(userNumbers).size !== userNumbers.length) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Números repetidos.</p>`; return; }

            const minNum = selectedLotteryConfig.min; const maxNum = selectedLotteryConfig.max;
            for (const num of userNumbers) { if (num < minNum || num > maxNum) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Número ${num} fora do range (${minNum}-${maxNum}).</p>`; return; } }

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
    if (manualSaveUserNumbersInput && mainLotterySelect) {
        manualSaveUserNumbersInput.addEventListener('input', updateManualSaveNumbersFeedback);
        mainLotterySelect.addEventListener('change', updateManualSaveNumbersFeedback);
    }
    if (manualSaveGameBtn) {
        manualSaveGameBtn.addEventListener('click', async () => {
            if (!currentUser || !firestoreDB) {
                manualSaveGameResultDisplay.innerHTML = '<p class="error-message">Você precisa estar logado para salvar jogos.</p>';
                manualSaveGameResultDisplay.style.display = 'block';
                return;
            }

            const lotteryType = mainLotterySelect.value;
            const selectedLotteryConfig = LOTTERY_CONFIG_JS[lotteryType.toLowerCase()];
            if (!selectedLotteryConfig) {
                manualSaveGameResultDisplay.innerHTML = '<p class="error-message">Selecione uma loteria válida.</p>';
                manualSaveGameResultDisplay.style.display = 'block';
                return;
            }

            const numbersStr = manualSaveUserNumbersInput.value;
            const userNumbersRaw = numbersStr.split(/[ ,;/\t\n]+/);
            const userNumbers = userNumbersRaw.map(n => n.trim()).filter(n => n !== "" && !isNaN(n)).map(n => parseInt(n, 10));
            const expectedCount = selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;

            if (userNumbers.length === 0) {
                manualSaveGameResultDisplay.innerHTML = '<p class="error-message">Insira os números do seu jogo.</p>';
                manualSaveGameResultDisplay.style.display = 'block';
                return;
            }
            if (userNumbers.length !== expectedCount) {
                manualSaveGameResultDisplay.innerHTML = `<p class="error-message">Forneça ${expectedCount} números para ${selectedLotteryConfig.name}. Você forneceu ${userNumbers.length}.</p>`;
                manualSaveGameResultDisplay.style.display = 'block';
                return;
            }
            if (new Set(userNumbers).size !== userNumbers.length) {
                manualSaveGameResultDisplay.innerHTML = '<p class="error-message">Seu jogo contém números repetidos.</p>';
                manualSaveGameResultDisplay.style.display = 'block';
                return;
            }
            const minNum = selectedLotteryConfig.min; const maxNum = selectedLotteryConfig.max;
            for (const num of userNumbers) {
                if (num < minNum || num > maxNum) {
                    manualSaveGameResultDisplay.innerHTML = `<p class="error-message">O número ${num} está fora do range permitido (${minNum}-${maxNum}) para ${selectedLotteryConfig.name}.</p>`;
                    manualSaveGameResultDisplay.style.display = 'block';
                    return;
                }
            }

            manualSaveGameBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Salvando...';
            manualSaveGameBtn.disabled = true;

            try {
                await firestoreDB.collection('userGames').add({
                    userId: currentUser.uid,
                    userEmail: currentUser.email,
                    lottery: lotteryType,
                    game: userNumbers.sort((a, b) => a - b),
                    strategy: "Jogo Manual",
                    savedAt: firebase.firestore.FieldValue.serverTimestamp(),
                    isPremiado: false,
                    faixaPremio: "Não verificado",
                    acertos: 0,
                    numerosAcertados: [],
                    ultimoConcursoVerificado: null,
                    notificacaoPendente: false
                });
                manualSaveGameResultDisplay.innerHTML = '<p style="color:#2ecc71;">Jogo manual salvo com sucesso!</p>';
                manualSaveGameResultDisplay.style.display = 'block';
                manualSaveUserNumbersInput.value = '';
                updateManualSaveNumbersFeedback();
                if (myGamesSection && myGamesSection.classList.contains('active-section') && typeof loadUserGames === "function") {
                    loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos");
                }
            } catch (error) {
                manualSaveGameResultDisplay.innerHTML = `<p class="error-message">Erro ao salvar: ${error.message}</p>`;
                manualSaveGameResultDisplay.style.display = 'block';
            } finally {
                manualSaveGameBtn.innerHTML = '<i class="fas fa-save"></i> Salvar Jogo Manual';
                manualSaveGameBtn.disabled = false;
            }
        });
    }

    if (verifyPastGameBtn) { 
        verifyPastGameBtn.addEventListener('click', async () => {
            const lotteryType = mainLotterySelect.value; 
            const selectedLotteryConfig = LOTTERY_CONFIG_JS[lotteryType.toLowerCase()];

            if (!selectedLotteryConfig) {
                verifyPastGameResultDiv.innerHTML = '<p class="error-message">Selecione uma loteria válida primeiro.</p>';
                verifyPastGameResultDiv.style.display = 'block';
                return;
            }

            const contestNumberStr = pastGameContestInput.value.trim();
            const numbersStr = pastGameNumbersInput.value.trim();
            verifyPastGameResultDiv.style.display = 'none';
            verifyPastGameResultDiv.innerHTML = '';

            if (!contestNumberStr) {
                verifyPastGameResultDiv.innerHTML = '<p class="error-message">Informe o número do concurso.</p>';
                verifyPastGameResultDiv.style.display = 'block';
                return;
            }
            const contestNumber = parseInt(contestNumberStr);
            if (isNaN(contestNumber) || contestNumber <=0) {
                 verifyPastGameResultDiv.innerHTML = '<p class="error-message">Número do concurso inválido.</p>';
                verifyPastGameResultDiv.style.display = 'block';
                return;
            }

            const userNumbersRaw = numbersStr.split(/[ ,;/\t\n]+/);
            const userNumbers = userNumbersRaw.map(n => n.trim()).filter(n => n !== "" && !isNaN(n)).map(n => parseInt(n, 10));

            const expectedCount = selectedLotteryConfig.count_sorteadas || selectedLotteryConfig.count_apostadas || selectedLotteryConfig.count;
            if (userNumbers.length !== expectedCount) {
                verifyPastGameResultDiv.innerHTML = `<p class="error-message">Você deve fornecer ${expectedCount} números para ${selectedLotteryConfig.name}.</p>`;
                verifyPastGameResultDiv.style.display = 'block';
                return;
            }
            if (new Set(userNumbers).size !== userNumbers.length) {
                verifyPastGameResultDiv.innerHTML = `<p class="error-message">Seu jogo contém números repetidos.</p>`;
                verifyPastGameResultDiv.style.display = 'block';
                return;
            }
            const minNum = selectedLotteryConfig.min; const maxNum = selectedLotteryConfig.max;
            for (const num of userNumbers) {
                if (num < minNum || num > maxNum) {
                    verifyPastGameResultDiv.innerHTML = `<p class="error-message">O número ${num} está fora do range (${minNum}-${maxNum}) para ${selectedLotteryConfig.name}.</p>`;
                    verifyPastGameResultDiv.style.display = 'block';
                    return;
                }
            }

            verifyPastGameBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verificando...';
            verifyPastGameBtn.disabled = true;
            
            try {
                const payload = {
                    lottery: lotteryType, 
                    concurso: contestNumber,
                    numeros_usuario: userNumbers.sort((a, b) => a - b)
                };
                
                const resultData = await fetchData('api/main/verificar-jogo-passado', { 
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (resultData.erro) {
                    throw new Error(resultData.erro);
                }
                
                let htmlResult = `<h4>Resultado da Verificação</h4>`;
                htmlResult += `<p><strong>Loteria:</strong> ${resultData.loteria_nome_exibicao || selectedLotteryConfig.name}</p>`;
                htmlResult += `<p><strong>Concurso:</strong> ${resultData.concurso_verificado}</p>`;
                htmlResult += `<p><strong>Data Sorteio:</strong> ${resultData.data_sorteio_verificado || 'N/A'}</p>`;
                htmlResult += `<p><strong>Seu Jogo:</strong> ${resultData.jogo_usuario.join(', ')}</p>`;
                htmlResult += `<p><strong>Números Sorteados Oficiais:</strong> ${resultData.numeros_sorteados.join(', ')}</p>`;
                htmlResult += `<p><strong>Acertos:</strong> <span class="highlight">${resultData.acertos}</span></p>`;
                
                if (resultData.premiado) {
                    htmlResult += `<p style="color:#2ecc71; font-weight:bold; font-size:1.1em;">Parabéns! Jogo Premiado!</p>`;
                    htmlResult += `<p><strong>Faixa do Prêmio:</strong> ${resultData.faixa_premio}</p>`;
                    if (resultData.valor_premio_formatado_estimado && resultData.valor_premio_formatado_estimado !== "N/A" && resultData.valor_premio_formatado_estimado !== "R$ 0,00") {
                        htmlResult += `<p><strong>Valor do Prêmio (na época):</strong> <span class="highlight">${resultData.valor_premio_formatado_estimado}</span></p>`;
                    } else if (resultData.aviso) { 
                        htmlResult += `<p><small><i>Aviso sobre o valor: ${resultData.aviso}</i></small></p>`;
                    }
                    if (resultData.acertos === (selectedLotteryConfig.count_sorteadas || selectedLotteryConfig.count)) triggerConfetti();
                } else {
                    htmlResult += `<p style="color:#ff4765;">Jogo não premiado neste concurso.</p>`;
                }
                if(resultData.aviso && !resultData.premiado) { 
                    htmlResult += `<p><small><i>Aviso: ${resultData.aviso}</i></small></p>`;
                }
                verifyPastGameResultDiv.innerHTML = htmlResult;

            } catch (error) {
                verifyPastGameResultDiv.innerHTML = `<p class="error-message">Erro ao verificar: ${error.message}</p>`;
            } finally {
                verifyPastGameBtn.innerHTML = '<i class="fas fa-search-dollar"></i> Verificar Jogo';
                verifyPastGameBtn.disabled = false;
                verifyPastGameResultDiv.style.display = 'block';
            }
        });
    }

    // ===== LÓGICA DO ORBE E MODAL DE CONTATO (SIMPLIFICADO) =====
    const contactOrbBtn = document.getElementById('contact-orb-btn');
    const contactModal = document.getElementById('contact-modal');
    const closeContactModalBtn = document.getElementById('close-contact-modal');
    const contactOptions = document.querySelector('.contact-options');
    const contactInfoDisplay = document.getElementById('contact-info-display');

    if (contactOrbBtn && contactModal) {
        contactOrbBtn.addEventListener('click', () => openModal(contactModal));
    }
    if (closeContactModalBtn && contactModal) {
        closeContactModalBtn.addEventListener('click', () => {
            closeModal(contactModal);
            // Limpeza já é feita na função closeModal agora
        });
    }

    if (contactOptions && contactInfoDisplay) {
        contactOptions.addEventListener('click', (e) => {
            const target = e.target.closest('.contact-option-btn');
            if (!target) return;

            const type = target.dataset.type;
            contactInfoDisplay.style.display = 'flex';
            contactInfoDisplay.innerHTML = ''; // Limpa antes de adicionar novo conteúdo

            if (type === 'phone') {
                // **!! SUBSTITUA PELO SEU NÚMERO DE TELEFONE REAL !!**
                const phoneNumber = '(+55 11) 96552-0979'; 
                contactInfoDisplay.innerHTML = `
                    <span>${phoneNumber}</span>
                    <button onclick="navigator.clipboard.writeText('${phoneNumber.replace(/\D/g, '')}')">Copiar</button>
                `;
            } else if (type === 'address') {
                // **!! SUBSTITUA PELO SEU ENDEREÇO REAL !!**
                const address = 'Torre Jacarandá - Av. Marcos Penteado de Ulhoa Rodrigues, 939 - 8º Andar Alphaville, Barueri - SP, 06460-040';
                contactInfoDisplay.innerHTML = `
                    <span>${address}</span>
                `;
            } else if (type === 'website') {
                // O data-info já contém a URL completa do site
                window.open(target.dataset.info, '_blank');
                contactInfoDisplay.style.display = 'none'; // Esconde se for só um link externo
            }
        });
    }
    
    // Adiciona o listener para fechar o modal de contato também
    window.addEventListener('click', (event) => { 
        if (event.target === contactModal) { // Certifique-se que 'contactModal' está definido
             closeModal(contactModal);
             // a limpeza do modal é feita na função closeModal agora.
        }
    });

});
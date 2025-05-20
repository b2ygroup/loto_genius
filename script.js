document.addEventListener('DOMContentLoaded', () => {
    console.log("SCRIPT.JS: DOMContentLoaded event fired. Ver 10.2 (Full Frontend Integration)");
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
    const SPLASH_MINIMUM_VISIBLE_TIME = APPROX_TOTAL_CSS_ANIM_DURATION + 1000; // Total ~6.5 segundos

    // --- Seletores de Elementos ---
    const accessibleSplashScreen = document.getElementById('accessible-splash-screen');
    const splashProgressBarFill = accessibleSplashScreen ? accessibleSplashScreen.querySelector('.progress-bar-fill') : null;
    const splashProgressContainer = accessibleSplashScreen ? accessibleSplashScreen.querySelector('.progress-bar-container') : null;
    
    const appContent = document.getElementById('app-content');
    const currentYearSpan = document.getElementById('current-year');
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
    const confettiCanvas = document.getElementById('confetti-canvas');
    const lotteryTypeSelect = document.getElementById('lottery-type'); 
    const iaStrategySelect = document.getElementById('ia-strategy-select'); 
    const simulatePremiumCheckbox = document.getElementById('simulate-premium-checkbox'); // Novo
    const fetchResultsBtn = document.getElementById('fetch-results-btn');
    const generateGameBtn = document.getElementById('generate-game-btn');
    const apiResultsPre = document.getElementById('api-results');
    const resultsLotteryNameSpan = document.getElementById('results-lottery-name');
    const gameGenerationOutputDiv = document.getElementById('game-generation-output');
    const generatedGameNumbersDiv = document.getElementById('generated-game-numbers');
    const generatedGameStrategyP = document.getElementById('generated-game-strategy');
    const saveGameBtn = document.getElementById('save-game-btn');
    const checkGeneratedGameBtn = document.getElementById('check-generated-game-btn');
    const generatedGameCheckResultDiv = document.getElementById('generated-game-check-result');
    const savedGamesContainer = document.getElementById('saved-games-container');
    const noSavedGamesP = document.getElementById('no-saved-games');
    const filterLotteryMyGamesSelect = document.getElementById('filter-lottery-mygames');
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
    
    const freqStatsLotteryNameSpan = document.getElementById('freq-stats-lottery-name');
    const frequencyListContainer = document.getElementById('frequency-list-container');
    const pairFreqStatsLotteryNameSpan = document.getElementById('pair-freq-stats-lottery-name');
    const pairFrequencyListContainer = document.getElementById('pair-frequency-list-container');
    const cityStatsLotteryNameSpan = document.getElementById('city-stats-lottery-name');
    const cityListContainer = document.getElementById('city-list-container');
    const cityPrizeSumLotteryNameSpan = document.getElementById('city-prize-sum-lottery-name');
    const cityPrizeSumListContainer = document.getElementById('city-prize-sum-list-container');

    // Seletores para o card de Cálculo de Probabilidade Manual
    const manualProbLotteryTypeSelect = document.getElementById('manual-prob-lottery-type');
    const manualProbUserNumbersInput = document.getElementById('manual-prob-user-numbers');
    const manualCalculateProbBtn = document.getElementById('manual-calculate-prob-btn');
    const manualProbabilityResultDisplay = document.getElementById('manual-probability-result-display');
    const manualProbNumbersCountFeedback = document.getElementById('manual-prob-numbers-count-feedback');


    if (currentYearSpan) currentYearSpan.textContent = new Date().getFullYear();
    let BACKEND_URL_BASE;
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:") { BACKEND_URL_BASE = 'http://127.0.0.1:5000'; } else { BACKEND_URL_BASE = '';  }
    
    let firebaseApp, firebaseAuth, firestoreDB, currentUser = null;
    let lastFetchedResults = {}; let lastGeneratedGames = {};  let criticalSplashTimeout; 
    let firebaseInitAttempts = 0; const maxFirebaseInitAttempts = 10; let splashHiddenTimestamp = 0; 
    const LOTTERY_CONFIG_JS = { 
        megasena: { count: 6, color: "#209869" }, 
        lotofacil: { count: 15, color: "#930089" },
        quina: { count: 5, color: "#260085" }, 
        lotomania: { count_sorteadas: 20, count_apostadas: 50, color: "#f78100" } // Adicionado count_apostadas
    };

    function showGlobalError(message) { if (errorDiv) { errorDiv.textContent = message; errorDiv.style.display = 'block'; } else { console.error("SCRIPT.JS: Global error div not found:", message); } }
    function disableFirebaseFeatures() { if (loginModalBtn) loginModalBtn.disabled = true; if (registerModalBtn) registerModalBtn.disabled = true; }
    function enableFirebaseFeatures() { if (loginModalBtn) loginModalBtn.disabled = false; if (registerModalBtn) registerModalBtn.disabled = false; if(document.getElementById('global-error-msg')) document.getElementById('global-error-msg').style.display = 'none';}
    function setActiveSection(sectionId) { if (!mainSections || mainSections.length === 0) { return; } mainSections.forEach(section => { section.classList.remove('active-section'); if (section.id === sectionId) section.classList.add('active-section'); }); if (mainNav) { const navButtons = mainNav.querySelectorAll('.nav-item'); navButtons.forEach(btn => { btn.classList.remove('active'); if (btn.id === `nav-${sectionId.replace('-section', '')}-btn`) btn.classList.add('active'); }); } }
    
    async function fetchData(endpoint) {
        const url = `${BACKEND_URL_BASE}/api/main/${endpoint}`;
        try {
            const response = await fetch(url);
            if (!response.ok) {
                const errorText = await response.text();
                let errorJson = {};
                try { errorJson = JSON.parse(errorText); } catch(e) { /* ignora se não for JSON */ }
                console.error(`SCRIPT.JS: HTTP Error ${response.status} for ${url}:`, errorJson.detalhes || errorText);
                // Passa o objeto de erro JSON para quem chamou, se possível
                throw { status: response.status, message: errorJson.detalhes || errorJson.erro || errorText.substring(0,250), data: errorJson };
            }
            return await response.json();
        } catch (error) {
            console.error(`SCRIPT.JS: Error fetching ${url}:`, error);
            throw error; // Relança o erro para ser tratado pela função chamadora
        }
    }
        
    function animateCounter(element, finalValueInput) {
        if (!element) { return; }
        const elementId = element.id || 'ElementoSemID';
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
            let currentValue;
            if (startValue > numericFinalValue) { currentValue = Math.max(numericFinalValue, Math.floor(startValue - progress * (startValue - numericFinalValue))); }
            else { currentValue = Math.min(numericFinalValue, Math.floor(startValue + progress * (numericFinalValue - startValue))); }
            element.textContent = currentValue.toLocaleString('pt-BR');
            if (progress < 1) { requestAnimationFrame(animationStep); }
            else { element.textContent = numericFinalValue.toLocaleString('pt-BR'); }
        }
        requestAnimationFrame(animationStep);
    }

    async function fetchPlatformStats() {
        if (!statsJogosGeradosSpan || !statsJogosPremiadosSpan || !statsValorPremiosSpan) { 
            if(statsJogosGeradosSpan) statsJogosGeradosSpan.textContent = "N/A";
            if(statsJogosPremiadosSpan) statsJogosPremiadosSpan.textContent = "N/A";
            if(statsValorPremiosSpan) statsValorPremiosSpan.textContent = "R$ N/A";
            return; 
        }
        try {
            const stats = await fetchData('platform-stats');
            if (stats && typeof stats.jogos_gerados_total === 'number') { animateCounter(statsJogosGeradosSpan, stats.jogos_gerados_total); } 
            else { statsJogosGeradosSpan.textContent = "N/A"; }
            if (stats && typeof stats.jogos_premiados_estimativa === 'number') { animateCounter(statsJogosPremiadosSpan, stats.jogos_premiados_estimativa); } 
            else { statsJogosPremiadosSpan.textContent = "N/A"; }
            if (stats && typeof stats.valor_premios_estimativa_formatado === 'string') { statsValorPremiosSpan.textContent = stats.valor_premios_estimativa_formatado; } 
            else { statsValorPremiosSpan.textContent = "R$ N/A"; }
        } catch (error) {
            statsJogosGeradosSpan.textContent = "N/A"; statsJogosPremiadosSpan.textContent = "N/A"; statsValorPremiosSpan.textContent = "R$ N/A";
        }
    }
    
    async function fetchRecentWinningPools() {
        if (!recentPoolsList) return;
        recentPoolsList.innerHTML = '<li><div class="spinner small-spinner"></div> Carregando...</li>';
        try {
            const pools = await fetchData('recent-winning-pools');
            recentPoolsList.innerHTML = ''; 
            if (pools && pools.length > 0) { pools.forEach(pool => { const li = document.createElement('li'); li.innerHTML = `<span><i class="fas fa-trophy pool-icon"></i> ${pool.name} (${pool.lottery})</span> <span class="pool-prize">${pool.prize}</span> <small>${pool.date}</small>`; recentPoolsList.appendChild(li); }); }
            else { recentPoolsList.innerHTML = '<li>Nenhum bolão premiado recentemente.</li>'; }
        } catch (error) { recentPoolsList.innerHTML = '<li>Erro ao carregar bolões.</li>'; }
    }

    async function fetchTopWinners() {
        if (!topWinnersList) return;
        topWinnersList.innerHTML = '<li><div class="spinner small-spinner"></div> Carregando...</li>';
        try {
            const winners = await fetchData('top-winners');
            topWinnersList.innerHTML = ''; 
            if (winners && winners.length > 0) { winners.forEach((winner, index) => { const li = document.createElement('li'); li.innerHTML = `<span>${index + 1}. <i class="fas fa-user-astronaut winner-icon"></i> ${winner.nick}</span> <span class="winner-prize">${winner.prize_total}</span>`; topWinnersList.appendChild(li); }); }
            else { topWinnersList.innerHTML = '<li>Ranking de ganhadores indisponível.</li>'; }
        } catch (error) { topWinnersList.innerHTML = '<li>Erro ao carregar ranking.</li>'; }
    }

    async function fetchAndDisplayFrequencyStats(lotteryName) {
        if (!frequencyListContainer || !freqStatsLotteryNameSpan) { return; }
        const lotteryFriendlyName = lotteryTypeSelect.options[lotteryTypeSelect.selectedIndex].text;
        freqStatsLotteryNameSpan.textContent = lotteryFriendlyName;
        frequencyListContainer.innerHTML = '<p class="loading-stats"><div class="spinner small-spinner"></div> Carregando...</p>';
        try {
            const result = await fetchData(`stats/frequencia/${lotteryName}`);
            frequencyListContainer.innerHTML = ''; 
            if (result.erro) { frequencyListContainer.innerHTML = `<p class="error-message">${result.erro}</p>`; return; }
            if (!result.data || result.data.length === 0) { frequencyListContainer.innerHTML = `<p class="no-stats">Sem dados de frequência para ${lotteryFriendlyName}.</p>`; return; }
            const statsData = result.data; const maxFreq = statsData.length > 0 ? statsData[0].frequencia : 1; const topN = Math.min(statsData.length, 15); 
            for(let i = 0; i < topN; i++) { const item = statsData[i]; const itemDiv = document.createElement('div'); itemDiv.classList.add('frequency-item'); const numSpan = document.createElement('span'); numSpan.classList.add('num'); numSpan.textContent = item.numero; if (LOTTERY_CONFIG_JS[lotteryName]?.color) { numSpan.style.backgroundColor = LOTTERY_CONFIG_JS[lotteryName].color; numSpan.style.borderColor = LOTTERY_CONFIG_JS[lotteryName].color; numSpan.style.color = '#fff'; } const barBgDiv = document.createElement('div'); barBgDiv.classList.add('freq-bar-bg'); const barDiv = document.createElement('div'); barDiv.classList.add('freq-bar'); const barWidth = Math.max(1, (item.frequencia / maxFreq) * 100); barDiv.style.width = `${barWidth}%`; if (LOTTERY_CONFIG_JS[lotteryName]?.color) { barDiv.style.background = `linear-gradient(90deg, ${LOTTERY_CONFIG_JS[lotteryName].color}99, ${LOTTERY_CONFIG_JS[lotteryName].color}cc)`; } barBgDiv.appendChild(barDiv); const freqSpan = document.createElement('span'); freqSpan.classList.add('freq-count'); freqSpan.textContent = `${item.frequencia}x`; itemDiv.appendChild(numSpan); itemDiv.appendChild(barBgDiv); itemDiv.appendChild(freqSpan); frequencyListContainer.appendChild(itemDiv); }
        } catch (error) { frequencyListContainer.innerHTML = `<p class="error-message">Falha ao carregar estatísticas.</p>`; }
    }

    async function fetchAndDisplayPairFrequencyStats(lotteryName) {
        if (!pairFrequencyListContainer || !pairFreqStatsLotteryNameSpan) { return; }
        const lotteryFriendlyName = lotteryTypeSelect.options[lotteryTypeSelect.selectedIndex].text;
        pairFreqStatsLotteryNameSpan.textContent = lotteryFriendlyName;
        pairFrequencyListContainer.innerHTML = '<p class="loading-stats"><div class="spinner small-spinner"></div> Carregando...</p>';
        try {
            const result = await fetchData(`stats/pares-frequentes/${lotteryName}`);
            pairFrequencyListContainer.innerHTML = '';
            if (result.erro) { pairFrequencyListContainer.innerHTML = `<p class="error-message">${result.erro}</p>`; return; }
            if (!result.data || result.data.length === 0) { pairFrequencyListContainer.innerHTML = `<p class="no-stats">Sem dados de pares para ${lotteryFriendlyName}.</p>`; return; }
            const statsData = result.data; const maxFreq = statsData.length > 0 ? statsData[0].frequencia : 1; const topN = Math.min(statsData.length, 10); 
            for(let i = 0; i < topN; i++) { const item = statsData[i]; const itemDiv = document.createElement('div'); itemDiv.classList.add('pair-frequency-item'); const pairNumsDiv = document.createElement('div'); pairNumsDiv.classList.add('pair-nums'); item.par.forEach(numStr => { const numSpan = document.createElement('span'); numSpan.classList.add('num'); numSpan.textContent = numStr; if (LOTTERY_CONFIG_JS[lotteryName]?.color) { numSpan.style.backgroundColor = LOTTERY_CONFIG_JS[lotteryName].color; numSpan.style.borderColor = LOTTERY_CONFIG_JS[lotteryName].color; numSpan.style.color = '#fff'; } pairNumsDiv.appendChild(numSpan); }); const barBgDiv = document.createElement('div'); barBgDiv.classList.add('freq-bar-bg'); const barDiv = document.createElement('div'); barDiv.classList.add('freq-bar'); const barWidth = Math.max(1, (item.frequencia / maxFreq) * 100); barDiv.style.width = `${barWidth}%`; if (LOTTERY_CONFIG_JS[lotteryName]?.color) { barDiv.style.background = `linear-gradient(90deg, ${LOTTERY_CONFIG_JS[lotteryName].color}99, ${LOTTERY_CONFIG_JS[lotteryName].color}cc)`; } barBgDiv.appendChild(barDiv); const freqSpan = document.createElement('span'); freqSpan.classList.add('freq-count'); freqSpan.textContent = `${item.frequencia}x`; itemDiv.appendChild(pairNumsDiv); itemDiv.appendChild(barBgDiv); itemDiv.appendChild(freqSpan); pairFrequencyListContainer.appendChild(itemDiv); }
        } catch (error) { pairFrequencyListContainer.innerHTML = `<p class="error-message">Falha ao carregar estatísticas de pares.</p>`;}
    }

    async function fetchAndDisplayCityStats(lotteryName) {
        if (!cityListContainer || !cityStatsLotteryNameSpan) { return; }
        const lotteryFriendlyName = lotteryTypeSelect.options[lotteryTypeSelect.selectedIndex].text;
        cityStatsLotteryNameSpan.textContent = lotteryFriendlyName;
        cityListContainer.innerHTML = '<p class="loading-stats"><div class="spinner small-spinner"></div> Carregando...</p>';
        try {
            const result = await fetchData(`stats/cidades-premiadas/${lotteryName}`);
            cityListContainer.innerHTML = '';
            if (result.erro) { cityListContainer.innerHTML = `<p class="error-message">${result.erro}</p>`; return; }
            if (!result.data || result.data.length === 0) { cityListContainer.innerHTML = `<p class="no-stats">Sem dados de cidades premiadas para ${lotteryFriendlyName}.</p>`; return; }
            const statsData = result.data; const topN = Math.min(statsData.length, 10); 
            for(let i = 0; i < topN; i++) { const item = statsData[i]; const itemDiv = document.createElement('div'); itemDiv.classList.add('city-stats-item'); const nameSpan = document.createElement('span'); nameSpan.classList.add('city-name'); nameSpan.textContent = item.cidade_uf; const countSpan = document.createElement('span'); countSpan.classList.add('city-prize-count'); countSpan.textContent = `${item.premios_principais} prêmio(s)`; itemDiv.appendChild(nameSpan); itemDiv.appendChild(countSpan); cityListContainer.appendChild(itemDiv); }
        } catch (error) { cityListContainer.innerHTML = `<p class="error-message">Falha ao carregar estatísticas de cidades.</p>`;}
    }
    
    async function fetchAndDisplayCityPrizeSumStats(lotteryName) {
        if (!cityPrizeSumListContainer || !cityPrizeSumLotteryNameSpan) { return; }
        const lotteryFriendlyName = lotteryTypeSelect.options[lotteryTypeSelect.selectedIndex].text;
        cityPrizeSumLotteryNameSpan.textContent = lotteryFriendlyName;
        cityPrizeSumListContainer.innerHTML = '<p class="loading-stats"><div class="spinner small-spinner"></div> Carregando...</p>';
        try {
            const result = await fetchData(`stats/maiores-premios-cidade/${lotteryName}`);
            cityPrizeSumListContainer.innerHTML = ''; 
            if (result.erro) { cityPrizeSumListContainer.innerHTML = `<p class="error-message">${result.erro}</p>`; return; }
            if (!result.data || result.data.length === 0) { cityPrizeSumListContainer.innerHTML = `<p class="no-stats">Sem dados de prêmios por cidade para ${lotteryFriendlyName}.</p>`; return; }
            const statsData = result.data; const topN = Math.min(statsData.length, 10); 
            for(let i = 0; i < topN; i++) { const item = statsData[i]; const itemDiv = document.createElement('div'); itemDiv.classList.add('city-prize-item');  const nameSpan = document.createElement('span'); nameSpan.classList.add('city-name'); nameSpan.textContent = item.cidade_uf; const amountSpan = document.createElement('span'); amountSpan.classList.add('city-prize-amount'); amountSpan.textContent = `${item.total_ganho_principal_formatado}`; if (item.total_ganho_principal_float > 1000000) { amountSpan.style.fontWeight = 'bold'; amountSpan.style.color = '#2ecc71'; } itemDiv.appendChild(nameSpan); itemDiv.appendChild(amountSpan); cityPrizeSumListContainer.appendChild(itemDiv); }
        } catch (error) { console.error(`SCRIPT.JS: Erro ao buscar soma de prêmios por cidade para ${lotteryName}:`, error); cityPrizeSumListContainer.innerHTML = `<p class="error-message">Falha ao carregar estatísticas de prêmios por cidade.</p>`; }
    }

    function initializeCarousels() {
        const carousels = document.querySelectorAll('.carousel-ad');
        carousels.forEach(carousel => {
            const items = carousel.querySelectorAll('.carousel-item');
            if (items.length <= 1) return; 
            let currentIndex = 0;
            if (items[currentIndex]) items[currentIndex].classList.add('active');
            setInterval(() => {
                if (items[currentIndex]) items[currentIndex].classList.remove('active');
                currentIndex = (currentIndex + 1) % items.length;
                if (items[currentIndex]) items[currentIndex].classList.add('active');
            }, 5000); 
        });
    }
    function openModal(modalElement) { if (modalElement) { modalElement.style.display = 'flex'; document.body.style.overflow = 'hidden'; } }
    function closeModal(modalElement) { if (modalElement) { modalElement.style.display = 'none'; document.body.style.overflow = ''; if (modalElement === loginModal && loginEmailInput && loginPasswordInput && loginErrorP) { loginEmailInput.value = ''; loginPasswordInput.value = ''; loginErrorP.textContent = ''; } else if (modalElement === registerModal && registerEmailInput && registerPasswordInput && registerConfirmPasswordInput && registerErrorP) { registerEmailInput.value = ''; registerPasswordInput.value = ''; registerConfirmPasswordInput.value = ''; registerErrorP.textContent = ''; } } }
    
    function showAppContentNow() {
        if (accessibleSplashScreen && !accessibleSplashScreen.classList.contains('hidden')) {
            accessibleSplashScreen.classList.add('hidden');
            splashHiddenTimestamp = Date.now();
            if(splashProgressContainer) splashProgressContainer.setAttribute('aria-valuenow', '100');
        } else if (splashHiddenTimestamp > 0 && appContent && appContent.style.display !== 'none') {
            return; 
        }
        
        if (appContent && appContent.style.display === 'none') { 
            appContent.style.display = 'block';
            setActiveSection('dashboard-section');
            
            fetchPlatformStats(); 
            fetchRecentWinningPools();
            fetchTopWinners();
            
            if (lotteryTypeSelect) { 
                const initialLottery = lotteryTypeSelect.value;
                fetchAndDisplayResults(initialLottery);
                fetchAndDisplayFrequencyStats(initialLottery); 
                fetchAndDisplayPairFrequencyStats(initialLottery);
                fetchAndDisplayCityStats(initialLottery);
                fetchAndDisplayCityPrizeSumStats(initialLottery); 
                 setTimeout(() => { 
                     if (lotteryTypeSelect.dispatchEvent) lotteryTypeSelect.dispatchEvent(new Event('change'));
                 }, 200);
            }
            initializeCarousels();
        } else if (appContent && appContent.style.display !== 'none' && splashHiddenTimestamp > 0) {
            fetchPlatformStats(); 
            fetchRecentWinningPools();
            fetchTopWinners();
             if (lotteryTypeSelect) {
                const currentLottery = lotteryTypeSelect.value;
                fetchAndDisplayResults(currentLottery);
                fetchAndDisplayFrequencyStats(currentLottery); 
                fetchAndDisplayPairFrequencyStats(currentLottery);
                fetchAndDisplayCityStats(currentLottery);
                fetchAndDisplayCityPrizeSumStats(currentLottery);
            }
        }
    }
    
    function initializeFirebase() {
        if (typeof firebase !== 'undefined' && typeof firebaseConfig !== 'undefined') {
            try {
                if (firebase.apps.length === 0) { firebaseApp = firebase.initializeApp(firebaseConfig); }
                else { firebaseApp = firebase.app(); }
                firebaseAuth = firebase.auth(firebaseApp);
                firestoreDB = firebase.firestore(firebaseApp);
                firebaseAuth.onAuthStateChanged(user => {
                    currentUser = user; 
                    updateLoginUI(user);
                    if (criticalSplashTimeout) { clearTimeout(criticalSplashTimeout); criticalSplashTimeout = null; }
                    const timeSinceDOMLoad = Date.now() - domContentLoadedTimestamp;
                    let delayToHideSplash = 0;
                    if (splashHiddenTimestamp === 0) { 
                        if (timeSinceDOMLoad < SPLASH_MINIMUM_VISIBLE_TIME) {
                            delayToHideSplash = SPLASH_MINIMUM_VISIBLE_TIME - timeSinceDOMLoad;
                        }
                        setTimeout(showAppContentNow, delayToHideSplash);
                    } else { showAppContentNow();  }
                });
                enableFirebaseFeatures(); return true;
            } catch (error) { 
                console.error("SCRIPT.JS: CRITICAL Firebase init error:", error);
                showGlobalError(`Error initializing Firebase: ${error.message}.`);
                disableFirebaseFeatures(); return false; 
            }
        } else { 
            console.error("SCRIPT.JS: Firebase SDK or firebaseConfig UNDEFINED."); return false; 
        }
    }

    function attemptFirebaseInit() {
        if (initializeFirebase()) { /* Sucesso */ }
        else { 
            firebaseInitAttempts++;
            if (firebaseInitAttempts < maxFirebaseInitAttempts) {
                setTimeout(attemptFirebaseInit, 500);
            } else { 
                console.error("SCRIPT.JS: Failed to init Firebase after multiple attempts.");
                if (splashHiddenTimestamp === 0) { showAppContentNow(); } 
                showGlobalError("Could not load backend services. Please reload.");
                disableFirebaseFeatures();
            }
        }
    }

    async function fetchAndDisplayResults(lottery) { 
        if (!apiResultsPre || !resultsLotteryNameSpan || !lotteryTypeSelect) { return; }
        const selectedOption = Array.from(lotteryTypeSelect.options).find(opt => opt.value === lottery);
        const lotteryFriendlyName = selectedOption ? selectedOption.text : lottery.toUpperCase();
        resultsLotteryNameSpan.textContent = lotteryFriendlyName;
        apiResultsPre.textContent = 'Buscando...';
        try {
            const data = await fetchData(`resultados/${lottery}`);
            let displayText = "";
            if (data.erro) displayText = `Erro da API: ${data.erro}`;
            else if (data.aviso) displayText = `Aviso: ${data.aviso}\nConcurso: ${data.ultimo_concurso || 'N/A'}\nData: ${data.data || 'N/A'}\nNúmeros: ${data.numeros ? data.numeros.join(', ') : 'N/A'}`;
            else displayText = `Concurso: ${data.ultimo_concurso || 'N/A'}\nData: ${data.data || 'N/A'}\nNúmeros Sorteados: ${data.numeros ? data.numeros.join(', ') : 'N/A'}`;
            apiResultsPre.textContent = displayText;
            lastFetchedResults[lottery] = data; 
            if(lastFetchedResults[lottery]) lastFetchedResults[lottery].loteria_tipo = lottery;
        } catch (error) {
            apiResultsPre.textContent = `Falha ao buscar resultados para ${lotteryFriendlyName}: ${error.message}`;
            lastFetchedResults[lottery] = { erro: `Falha ao buscar: ${error.message}`, numeros: [] };
        }
    }

    function renderGameNumbers(container, numbersArray, highlightedNumbers = [], almostNumbers = []) {
        if (!container) { return; }
        container.innerHTML = ''; 
        if (!numbersArray || !Array.isArray(numbersArray) || numbersArray.length === 0) {
            container.textContent = "N/A"; return;
        }
        numbersArray.forEach((numInput, index) => {
            const num = parseInt(numInput, 10); 
            if (isNaN(num)) { return; }
            const numDiv = document.createElement('div');
            numDiv.classList.add('game-number');
            numDiv.style.opacity = '0';
            numDiv.style.transform = 'scale(0.5) translateY(10px)';
            numDiv.style.transition = `opacity 0.3s ease-out ${index * 0.07}s, transform 0.3s ease-out ${index * 0.07}s`;
            if (highlightedNumbers.includes(num)) numDiv.classList.add('hit');
            else if (almostNumbers.includes(num)) numDiv.classList.add('almost');
            numDiv.textContent = String(num).padStart(2, '0');
            const currentLottery = lotteryTypeSelect.value; 
            if (LOTTERY_CONFIG_JS[currentLottery] && LOTTERY_CONFIG_JS[currentLottery].color) {
                if (!numDiv.classList.contains('hit') && !numDiv.classList.contains('almost')) {
                    numDiv.style.backgroundColor = LOTTERY_CONFIG_JS[currentLottery].color;
                    numDiv.style.color = '#fff'; 
                }
            }
            container.appendChild(numDiv);
            requestAnimationFrame(() => { setTimeout(() => { numDiv.style.opacity = '1'; numDiv.style.transform = 'scale(1) translateY(0)'; }, 20); });
        });
    }

    function triggerConfetti() { if (!confettiCanvas) { return; } for (let i = 0; i < 100; i++) { const confetti = document.createElement('div'); confetti.classList.add('confetti'); confetti.style.left = Math.random() * 100 + 'vw'; const animDuration = Math.random() * 1.5 + 2.0; confetti.style.animationDuration = animDuration + 's'; confetti.style.animationDelay = (Math.random() * 0.5) + 's'; confetti.style.backgroundColor = `hsl(${Math.random() * 360}, 90%, 60%)`; const size = Math.random() * 8 + 4; confetti.style.width = size + 'px'; confetti.style.height = size * (Math.random() * 1.5 + 1) + 'px'; confetti.style.opacity = Math.random() * 0.5 + 0.5; confetti.style.transform = `rotate(${Math.random() * 360}deg)`; confettiCanvas.appendChild(confetti); setTimeout(() => { confetti.remove(); }, animDuration * 1000 + parseFloat(confetti.style.animationDelay.replace('s','')) * 1000 + 500); } }
    function checkGame(userGameNumbers, officialResults) { if (!userGameNumbers || !officialResults || !officialResults.numeros || officialResults.numeros.length === 0) { return { hits: 0, hitNumbers: [], almostNumbers: [], message: "Não foi possível conferir." }; } const officialNumbers = officialResults.numeros.map(n => parseInt(n, 10)); const userNumbers = userGameNumbers.map(n => parseInt(n, 10)); const hitNumbers = userNumbers.filter(num => officialNumbers.includes(num)); const almostNumbers = userNumbers.filter(num => !hitNumbers.includes(num) && (officialNumbers.includes(num - 1) || officialNumbers.includes(num + 1))); const hits = hitNumbers.length; let prizeMessage = ""; const lotteryType = officialResults.loteria_tipo; let isMajorPrize = false; if (lotteryType === 'megasena') { if (hits === 6) { prizeMessage = "UAU! Acertou a SENA!"; isMajorPrize = true; } else if (hits === 5) prizeMessage = "Parabéns! Acertou a QUINA!"; else if (hits === 4) prizeMessage = "Muito bom! Acertou a QUADRA!"; } else if (lotteryType === 'lotofacil') { if (hits === 15) { prizeMessage = "INCRÍVEL! 15 acertos!"; isMajorPrize = true; } else if (hits === 14) prizeMessage = "Parabéns! 14 acertos!"; else if (hits >= 11) prizeMessage = `Bom! ${hits} acertos!`; } else if (lotteryType === 'quina') { if (hits === 5) { prizeMessage = "EXCELENTE! Acertou a Quina!"; isMajorPrize = true; } else if (hits === 4) prizeMessage = "Parabéns! Acertou o Quadque!"; else if (hits === 3) prizeMessage = "Bom! Acertou o Terno!"; else if (hits === 2) prizeMessage = "Legal! Acertou o Duque!"; } else if (lotteryType === 'lotomania') { const countSorteadas = (LOTTERY_CONFIG_JS[lotteryType] && LOTTERY_CONFIG_JS[lotteryType].count_sorteadas) || 20; if (hits === countSorteadas) { prizeMessage = `FANTÁSTICO! ${hits} acertos na Lotomania!`; isMajorPrize = true; } else if (hits === 0) prizeMessage = "Curioso! 0 acertos na Lotomania também pode premiar!"; else if (hits >= 15 && hits < countSorteadas) prizeMessage = `Parabéns! ${hits} acertos na Lotomania!`; } if (isMajorPrize) triggerConfetti(); return { hits, hitNumbers, almostNumbers, message: `Você acertou ${hits} número(s). ${prizeMessage}` }; }
    function updateLoginUI(user) { const navItems = document.querySelectorAll('#main-nav .nav-item'); if (user) { if (loginModalBtn) loginModalBtn.style.display = 'none'; if (registerModalBtn) registerModalBtn.style.display = 'none'; if (userInfoDiv) userInfoDiv.style.display = 'flex'; if (userEmailSpan) userEmailSpan.textContent = user.email.split('@')[0]; if (logoutBtn) logoutBtn.style.display = 'inline-block'; if (mainNav) mainNav.style.display = 'flex'; if (navItems) navItems.forEach(item => item.style.display = 'flex'); if (gameGenerationOutputDiv && gameGenerationOutputDiv.dataset.game && saveGameBtn) saveGameBtn.style.display = 'inline-block'; if (typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); if (typeof setActiveSection === "function") setActiveSection('dashboard-section'); } else { if (loginModalBtn) loginModalBtn.style.display = 'inline-block'; if (registerModalBtn) registerModalBtn.style.display = 'inline-block'; if (userInfoDiv) userInfoDiv.style.display = 'none'; if (userEmailSpan) userEmailSpan.textContent = ''; if (logoutBtn) logoutBtn.style.display = 'none'; if (mainNav) mainNav.style.display = 'none'; if (navItems) navItems.forEach(item => item.style.display = 'none'); if (saveGameBtn) saveGameBtn.style.display = 'none'; if (savedGamesContainer) savedGamesContainer.innerHTML = ''; if (noSavedGamesP) noSavedGamesP.style.display = 'block'; if (typeof setActiveSection === "function") setActiveSection('dashboard-section'); } }
    async function loadUserGames(filterLottery = "todos") { if (!firestoreDB || !currentUser || !savedGamesContainer || !noSavedGamesP) return; savedGamesContainer.innerHTML = '<div class="spinner small-spinner"></div>'; noSavedGamesP.style.display = 'none'; let query = firestoreDB.collection('userGames').where('userId', '==', currentUser.uid).orderBy('savedAt', 'desc').limit(30); if (filterLottery !== "todos") query = query.where('lottery', '==', filterLottery); try { const querySnapshot = await query.get(); savedGamesContainer.innerHTML = '';  if (querySnapshot.empty) { noSavedGamesP.style.display = 'block'; return; } querySnapshot.forEach((doc) => { const gameData = doc.data(); const gameCard = createGameCardElement(doc.id, gameData); if(gameCard) savedGamesContainer.appendChild(gameCard); }); } catch (error) { console.error("SCRIPT.JS: Error loading games: ", error); savedGamesContainer.innerHTML = ''; noSavedGamesP.textContent = 'Erro ao carregar jogos.'; noSavedGamesP.style.display = 'block'; if (error.code === 'failed-precondition') { showGlobalError("Índice do banco de dados necessário. Verifique o console."); } } }
    function createGameCardElement(docId, gameData) { if(!gameData || !gameData.lottery || !gameData.game) return null; const card = document.createElement('div'); card.classList.add('game-card'); card.dataset.docId = docId; card.dataset.lottery = gameData.lottery; card.dataset.game = JSON.stringify(gameData.game); const title = document.createElement('h4'); title.innerHTML = `<i class="fas fa-ticket-alt"></i> ${gameData.lottery.toUpperCase()}`; const numbersDiv = document.createElement('div'); numbersDiv.classList.add('game-numbers'); renderGameNumbers(numbersDiv, gameData.game); const strategyP = document.createElement('p'); strategyP.classList.add('strategy-text'); strategyP.textContent = `Estratégia: ${gameData.strategy || 'N/A'}`; const savedAtP = document.createElement('p'); savedAtP.classList.add('game-card-info'); savedAtP.textContent = `Salvo em: ${gameData.savedAt?.toDate ? new Date(gameData.savedAt.toDate()).toLocaleString('pt-BR') : 'N/A'}`; const actionsDiv = document.createElement('div'); actionsDiv.classList.add('game-card-actions'); const checkResultDiv = document.createElement('div'); checkResultDiv.classList.add('check-result-display'); if(gameData.checkedResult) checkResultDiv.innerHTML = gameData.checkedResult; const checkBtn = document.createElement('button'); checkBtn.classList.add('action-btn', 'small-btn'); checkBtn.innerHTML = '<i class="fas fa-check-circle"></i> Conferir'; checkBtn.addEventListener('click', async () => { let resultsToUse = lastFetchedResults[gameData.lottery]; if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) { checkResultDiv.innerHTML = `<div class="spinner small-spinner"></div> Buscando resultados...`; try { resultsToUse = await fetchData(`resultados/${gameData.lottery}`); if(resultsToUse) resultsToUse.loteria_tipo = gameData.lottery; lastFetchedResults[gameData.lottery] = resultsToUse; if (lotteryTypeSelect && lotteryTypeSelect.value === gameData.lottery && apiResultsPre) { let displayText = resultsToUse.erro || resultsToUse.aviso || `Concurso: ${resultsToUse.ultimo_concurso || 'N/A'}...`; if (resultsToUse.numeros && resultsToUse.numeros.length > 0) { displayText = `Concurso: ${resultsToUse.ultimo_concurso || 'N/A'}\nData: ${resultsToUse.data || 'N/A'}\nNúmeros Sorteados: ${resultsToUse.numeros.join(', ')}`; } apiResultsPre.textContent = displayText; } } catch (e) { checkResultDiv.innerHTML = `<span class="misses">Falha ao buscar resultados.</span>`; return; } } if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) { checkResultDiv.innerHTML = `<span class="misses">Resultados oficiais indisponíveis.</span>`; return; } const result = checkGame(gameData.game, resultsToUse); checkResultDiv.innerHTML = `<span class="${result.hits > 0 ? 'hits' : (result.almostNumbers.length > 0 ? 'almost-text' : 'misses')}">${result.message}</span>`; renderGameNumbers(numbersDiv, gameData.game, result.hitNumbers, result.almostNumbers); if (firestoreDB && currentUser) firestoreDB.collection('userGames').doc(docId).update({ checkedResult: checkResultDiv.innerHTML }).catch(err => console.error("Erro ao atualizar conferência:", err)); }); const deleteBtn = document.createElement('button'); deleteBtn.classList.add('action-btn', 'small-btn', 'logout'); deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i> Excluir'; deleteBtn.addEventListener('click', async () => { if (confirm("Excluir este jogo?")) { try { if (!firestoreDB || !currentUser) { alert("Erro de autenticação."); return; } await firestoreDB.collection('userGames').doc(docId).delete(); card.remove(); if (savedGamesContainer && savedGamesContainer.children.length === 0 && noSavedGamesP) noSavedGamesP.style.display = 'block'; } catch (error) { console.error("Erro ao excluir:", error); alert("Não foi possível excluir."); } } }); actionsDiv.appendChild(checkBtn); actionsDiv.appendChild(deleteBtn); card.appendChild(title); card.appendChild(numbersDiv); card.appendChild(strategyP); card.appendChild(savedAtP); card.appendChild(actionsDiv); card.appendChild(checkResultDiv); return card; }
    
    // --- LÓGICA PARA O CARD DE CÁLCULO DE PROBABILIDADE MANUAL ---
    function updateManualProbNumbersFeedback() {
        if (!manualProbLotteryTypeSelect || !manualProbUserNumbersInput || !manualProbNumbersCountFeedback) return;
        const selectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex];
        if (!selectedOption || !selectedOption.dataset.count) {
            manualProbNumbersCountFeedback.textContent = "Selecione uma loteria."; return;
        }
        const expectedCount = parseInt(selectedOption.dataset.count, 10);
        const currentNumbersRaw = manualProbUserNumbersInput.value.split(/[ ,;/\t\n]+/);
        const currentNumbers = currentNumbersRaw.map(n => n.trim()).filter(n => n !== "" && !isNaN(n));
        manualProbNumbersCountFeedback.textContent = `Digitados: ${currentNumbers.length} de ${expectedCount} números.`;
        if (currentNumbers.length === expectedCount) { manualProbNumbersCountFeedback.style.color = '#2ecc71'; }
        else if (currentNumbers.length > expectedCount) { manualProbNumbersCountFeedback.style.color = '#ff4765'; }
        else { manualProbNumbersCountFeedback.style.color = '#f1c40f'; }
    }

    if (manualProbUserNumbersInput && manualProbLotteryTypeSelect) {
        manualProbUserNumbersInput.addEventListener('input', updateManualProbNumbersFeedback);
        manualProbLotteryTypeSelect.addEventListener('change', () => {
            const selectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex];
            if (!selectedOption || !selectedOption.dataset.count || !selectedOption.dataset.min || !selectedOption.dataset.max) return;
            manualProbUserNumbersInput.placeholder = `Ex: 01,02,... (${selectedOption.dataset.count} de ${selectedOption.dataset.min}-${selectedOption.dataset.max})`;
            manualProbUserNumbersInput.value = ''; 
            updateManualProbNumbersFeedback(); 
            if(manualProbabilityResultDisplay) manualProbabilityResultDisplay.textContent = "Aguardando seu jogo...";
        });
        const initialSelectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex];
         if (initialSelectedOption && initialSelectedOption.dataset.count && initialSelectedOption.dataset.min && initialSelectedOption.dataset.max){
            manualProbUserNumbersInput.placeholder = `Ex: 01,02,... (${initialSelectedOption.dataset.count} de ${initialSelectedOption.dataset.min}-${initialSelectedOption.dataset.max})`;
         }
        updateManualProbNumbersFeedback(); 
    }

    if (manualCalculateProbBtn && manualProbLotteryTypeSelect && manualProbUserNumbersInput && manualProbabilityResultDisplay) {
        manualCalculateProbBtn.addEventListener('click', async () => {
            const lotteryType = manualProbLotteryTypeSelect.value;
            const numbersStr = manualProbUserNumbersInput.value;
            const userNumbersRaw = numbersStr.split(/[ ,;/\t\n]+/);
            const userNumbers = userNumbersRaw.map(n => n.trim()).filter(n => n !== "" && !isNaN(n)).map(n => parseInt(n,10));
            const selectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex];
            const expectedCount = parseInt(selectedOption.dataset.count, 10);
            if (userNumbers.length === 0) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Por favor, insira os números do seu jogo.</p>`; return; }
            if (userNumbers.length !== expectedCount) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Para ${selectedOption.text.split('(')[0].trim()}, você deve fornecer exatamente ${expectedCount} números.</p>`; return; }
            if (new Set(userNumbers).size !== userNumbers.length) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Seu jogo contém números repetidos. Por favor, corrija.</p>`; return; }
            const minNum = parseInt(selectedOption.dataset.min, 10);
            const maxNum = parseInt(selectedOption.dataset.max, 10);
            for (const num of userNumbers) { if (num < minNum || num > maxNum) { manualProbabilityResultDisplay.innerHTML = `<p class="error-message">O número ${num} está fora do range permitido (${minNum}-${maxNum}) para esta loteria.</p>`; return; } }
            
            manualProbabilityResultDisplay.innerHTML = '<div class="spinner small-spinner"></div> Calculando...';
            try {
                const response = await fetch(`${BACKEND_URL_BASE}/api/main/jogo-manual/probabilidade`, {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ lottery_type: lotteryType, numeros_usuario: userNumbers })
                });
                const resultData = await response.json();
                if (!response.ok) { throw new Error(resultData.erro || `Erro HTTP ${response.status}`); }
                let displayText = `Loteria: <span class="highlight">${resultData.loteria}</span>\n`;
                displayText += `Seu Jogo: <span class="highlight">${resultData.jogo_usuario.join(', ')}</span>\n`;
                displayText += `Probabilidade (Prêmio Máximo): <span class="highlight">${resultData.probabilidade_texto}</span>\n`;
                if (resultData.probabilidade_decimal && resultData.probabilidade_decimal > 0) { displayText += `(Valor Decimal Aprox.: ${resultData.probabilidade_decimal.toExponential(4)})\n`; }
                if(resultData.descricao) displayText += `\n<small>${resultData.descricao}</small>`;
                manualProbabilityResultDisplay.innerHTML = displayText.replace(/\n/g, '<br>');
            } catch (error) {
                manualProbabilityResultDisplay.innerHTML = `<p class="error-message">Erro: ${error.message}</p>`;
            }
        });
    }

    // --- INÍCIO DA LÓGICA PRINCIPAL E EVENT LISTENERS ---
    if (splashProgressBarFill && splashProgressContainer) { let progress = 0; const totalVisualBarTime = SPLASH_PROGRESS_BAR_START_DELAY + SPLASH_PROGRESS_BAR_FILL_DURATION; const intervalTime = totalVisualBarTime / 100; const progressInterval = setInterval(() => { progress++; if (splashProgressContainer) splashProgressContainer.setAttribute('aria-valuenow', progress); if (progress >= 100) { clearInterval(progressInterval); } }, intervalTime); }
    criticalSplashTimeout = setTimeout(() => { if (splashHiddenTimestamp === 0) { showAppContentNow(); } if (!firebaseApp) { showGlobalError("Falha crítica na inicialização dos serviços."); disableFirebaseFeatures(); } criticalSplashTimeout = null; }, SPLASH_MINIMUM_VISIBLE_TIME + 1500);  
    setTimeout(attemptFirebaseInit, 100); 

    if(loginModalBtn) loginModalBtn.addEventListener('click', () => openModal(loginModal));
    if(registerModalBtn) registerModalBtn.addEventListener('click', () => openModal(registerModal));
    if(closeLoginModalBtn) closeLoginModalBtn.addEventListener('click', () => closeModal(loginModal));
    if(closeRegisterModalBtn) closeRegisterModalBtn.addEventListener('click', () => closeModal(registerModal));
    window.addEventListener('click', (event) => { if (event.target === loginModal) closeModal(loginModal); if (event.target === registerModal) closeModal(registerModal); });
    if (navDashboardBtn) navDashboardBtn.addEventListener('click', () => setActiveSection('dashboard-section'));
    if (navMyGamesBtn) navMyGamesBtn.addEventListener('click', () => { setActiveSection('my-games-section'); if (currentUser) loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); });
    if (navPoolsBtn) navPoolsBtn.addEventListener('click', () => setActiveSection('pools-section'));

    if (fetchResultsBtn && lotteryTypeSelect) {
        fetchResultsBtn.addEventListener('click', () => {
            const selectedLottery = lotteryTypeSelect.value;
            fetchAndDisplayResults(selectedLottery); fetchAndDisplayFrequencyStats(selectedLottery); 
            fetchAndDisplayPairFrequencyStats(selectedLottery); fetchAndDisplayCityStats(selectedLottery);
            fetchAndDisplayCityPrizeSumStats(selectedLottery);
        });
    }
    
    if (lotteryTypeSelect) {
        lotteryTypeSelect.addEventListener('change', () => {
            const selectedLottery = lotteryTypeSelect.value;
            if (resultsLotteryNameSpan && lotteryTypeSelect.options[lotteryTypeSelect.selectedIndex]) {
                 resultsLotteryNameSpan.textContent = lotteryTypeSelect.options[lotteryTypeSelect.selectedIndex].text;
            }
            fetchAndDisplayResults(selectedLottery); fetchAndDisplayFrequencyStats(selectedLottery); 
            fetchAndDisplayPairFrequencyStats(selectedLottery); fetchAndDisplayCityStats(selectedLottery);
            fetchAndDisplayCityPrizeSumStats(selectedLottery);
            if (lastGeneratedGames[selectedLottery] && gameGenerationOutputDiv && generatedGameNumbersDiv && generatedGameStrategyP) { gameGenerationOutputDiv.style.display = 'block'; renderGameNumbers(generatedGameNumbersDiv, lastGeneratedGames[selectedLottery].jogo); generatedGameStrategyP.textContent = `Estratégia: ${lastGeneratedGames[selectedLottery].estrategia}`; gameGenerationOutputDiv.dataset.lottery = selectedLottery; gameGenerationOutputDiv.dataset.game = JSON.stringify(lastGeneratedGames[selectedLottery].jogo); if (currentUser && saveGameBtn) saveGameBtn.style.display = 'inline-block'; if (checkGeneratedGameBtn) checkGeneratedGameBtn.style.display = 'inline-block'; if (generatedGameCheckResultDiv) generatedGameCheckResultDiv.innerHTML = lastGeneratedGames[selectedLottery].checkResult || ''; } else if (gameGenerationOutputDiv) { gameGenerationOutputDiv.style.display = 'none'; }
        });
    } 

    if (generateGameBtn && lotteryTypeSelect && iaStrategySelect) { 
        generateGameBtn.addEventListener('click', async () => {
            const lottery = lotteryTypeSelect.value;
            const strategy = iaStrategySelect.value; 
            const isPremiumUserSimulated = simulatePremiumCheckbox ? simulatePremiumCheckbox.checked : false;
            
            console.log(`SCRIPT.JS: generateGameBtn clicked for ${lottery}, Strategy: ${strategy}, Premium (simulado): ${isPremiumUserSimulated}`); 

            generateGameBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';
            generateGameBtn.disabled = true;
            if(generatedGameNumbersDiv) generatedGameNumbersDiv.innerHTML = '<div class="spinner small-spinner" role="status" aria-label="Gerando números"></div>'; 
            if(generatedGameStrategyP) generatedGameStrategyP.textContent = 'Nossa IA está preparando seu palpite...';
            if(gameGenerationOutputDiv) gameGenerationOutputDiv.style.display = 'block';
            if(saveGameBtn) saveGameBtn.style.display = 'none'; 
            if(checkGeneratedGameBtn) checkGeneratedGameBtn.style.display = 'none';
            if(generatedGameCheckResultDiv) generatedGameCheckResultDiv.innerHTML = '';
            
            try {
                const apiUrl = `gerar_jogo/${lottery}?estrategia=${strategy}&premium_user=${isPremiumUserSimulated}`;
                console.log(`SCRIPT.JS: generateGameBtn - Chamando fetchData para ${apiUrl}`); 
                const data = await fetchData(apiUrl);
                console.log(`SCRIPT.JS: generateGameBtn - Dados recebidos de ${apiUrl}:`, JSON.stringify(data, null, 2)); 

                if (data.premium_requerido) { 
                    console.warn(`SCRIPT.JS: generateGameBtn - Acesso premium requerido: ${data.detalhes}`);
                    if(generatedGameNumbersDiv) generatedGameNumbersDiv.innerHTML = `<p class="error-message" style="color: #f1c40f;">${data.detalhes || 'Recurso Premium.'}<br>Considere assinar para ter acesso!</p>`; 
                    if(generatedGameStrategyP) generatedGameStrategyP.textContent = '✨ Funcionalidade Premium ✨';
                    return; 
                }

                if (data.erro) { 
                    console.error(`SCRIPT.JS: generateGameBtn - Erro da API: ${data.detalhes || data.erro}`); 
                    throw new Error(data.detalhes || data.erro); 
                }
                if (!data.jogo || !Array.isArray(data.jogo) || data.jogo.length === 0) { 
                    console.error(`SCRIPT.JS: generateGameBtn - Jogo vazio ou inválido. Data:`, data); 
                    throw new Error("Palpite inválido retornado pela IA."); 
                }
                
                renderGameNumbers(generatedGameNumbersDiv, data.jogo); 
                
                if(generatedGameStrategyP) generatedGameStrategyP.textContent = `Estratégia IA: ${data.estrategia_usada || 'Indefinida'}`;
                lastGeneratedGames[lottery] = { jogo: data.jogo, estrategia: data.estrategia_usada || 'Indefinida', checkResult: '' };
                if(gameGenerationOutputDiv) { gameGenerationOutputDiv.dataset.lottery = lottery; gameGenerationOutputDiv.dataset.game = JSON.stringify(data.jogo); }
                if (currentUser && saveGameBtn) saveGameBtn.style.display = 'inline-block';
                if (checkGeneratedGameBtn) checkGeneratedGameBtn.style.display = 'inline-block';
            } catch (error) {
                console.error(`SCRIPT.JS: generateGameBtn - Erro:`, error);
                let displayError = 'Falha ao gerar palpite.';
                if(error && error.message) displayError = error.message;
                if(error && error.data && error.data.premium_requerido){ //Trata erro de premium vindo do throw
                    displayError = error.data.detalhes || "Esta é uma estratégia Premium! Considere assinar para ter acesso. 😉";
                     if(generatedGameNumbersDiv) generatedGameNumbersDiv.innerHTML = `<p class="error-message" style="color: #f1c40f;">${displayError}</p>`;
                     if(generatedGameStrategyP) generatedGameStrategyP.textContent = '✨ Funcionalidade Premium ✨';
                } else {
                    if(generatedGameNumbersDiv) generatedGameNumbersDiv.innerHTML = `<p class="error-message">${displayError}</p>`;
                    if(generatedGameStrategyP) generatedGameStrategyP.textContent = `Erro ao gerar.`;
                }
                lastGeneratedGames[lottery] = null;
            } finally {
                generateGameBtn.innerHTML = '<i class="fas fa-magic"></i> Gerar Palpite IA';
                generateGameBtn.disabled = false;
            }
        });
    } 
    if (checkGeneratedGameBtn && lotteryTypeSelect && gameGenerationOutputDiv && generatedGameCheckResultDiv) { checkGeneratedGameBtn.addEventListener('click', async () => { const currentLottery = lotteryTypeSelect.value; let resultsToUse = lastFetchedResults[currentLottery]; if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) { generatedGameCheckResultDiv.innerHTML = `<div class="spinner small-spinner"></div> Buscando resultados...`; try { resultsToUse = await fetchData(`resultados/${currentLottery}`); if(resultsToUse) resultsToUse.loteria_tipo = currentLottery; lastFetchedResults[currentLottery] = resultsToUse; } catch (e) { generatedGameCheckResultDiv.innerHTML = `<span class="misses">Falha ao buscar resultados.</span>`; return; } } if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) { generatedGameCheckResultDiv.innerHTML = `<span class="misses">Resultados oficiais indisponíveis.</span>`; return; } const gameData = gameGenerationOutputDiv.dataset; if (gameData && gameData.game && gameData.lottery === currentLottery) { const userGame = JSON.parse(gameData.game); const result = checkGame(userGame, resultsToUse); generatedGameCheckResultDiv.innerHTML = `<span class="${result.hits > 0 ? 'hits' : (result.almostNumbers.length > 0 ? 'almost-text' : 'misses')}">${result.message}</span>`; renderGameNumbers(generatedGameNumbersDiv, userGame, result.hitNumbers, result.almostNumbers); if(lastGeneratedGames[currentLottery]) lastGeneratedGames[currentLottery].checkResult = generatedGameCheckResultDiv.innerHTML; } else { generatedGameCheckResultDiv.innerHTML = '<span class="misses">Gere um jogo ou verifique se os resultados são da loteria correta.</span>'; } }); }
    if(loginSubmitBtn) loginSubmitBtn.addEventListener('click', () => { if (!firebaseAuth) { if(loginErrorP) loginErrorP.textContent = "Serviço indisponível."; return; } if (!loginEmailInput || !loginPasswordInput || !loginErrorP) return; const email = loginEmailInput.value; const password = loginPasswordInput.value; loginErrorP.textContent = ""; if (!email || !password) { loginErrorP.textContent = "Preencha email e senha."; return; } firebaseAuth.signInWithEmailAndPassword(email, password).then(() => closeModal(loginModal)).catch((error) => { loginErrorP.textContent = `Erro: ${error.message}`; }); });
    if(registerSubmitBtn) registerSubmitBtn.addEventListener('click', () => { if (!firebaseAuth) { if(registerErrorP) registerErrorP.textContent = "Serviço indisponível."; return; } if (!registerEmailInput || !registerPasswordInput || !registerConfirmPasswordInput || !registerErrorP) return; const email = registerEmailInput.value; const password = registerPasswordInput.value; const confirmPassword = registerConfirmPasswordInput.value; registerErrorP.textContent = ""; if (!email || !password || !confirmPassword) { registerErrorP.textContent = "Preencha todos os campos."; return; } if (password !== confirmPassword) { registerErrorP.textContent = "As senhas não coincidem."; return; } if (password.length < 6) { registerErrorP.textContent = "A senha deve ter no mínimo 6 caracteres."; return; } firebaseAuth.createUserWithEmailAndPassword(email, password).then(() => { alert("Usuário registrado! Você já está logado."); closeModal(registerModal); }).catch((error) => { registerErrorP.textContent = `Erro: ${error.message}`; }); });
    if(logoutBtn) logoutBtn.addEventListener('click', () => { if (!firebaseAuth) { alert("Serviço indisponível."); return; } firebaseAuth.signOut().catch((error) => { alert(`Erro no logout: ${error.message}`); }); });
    if(saveGameBtn) saveGameBtn.addEventListener('click', () => { if (!firestoreDB || !currentUser || !gameGenerationOutputDiv || !gameGenerationOutputDiv.dataset.game) { alert("Logue e gere um jogo para salvar."); return; } const gameDataFromDiv = gameGenerationOutputDiv.dataset; const lottery = gameDataFromDiv.lottery; const jogoArray = JSON.parse(gameDataFromDiv.game); const estrategia = lastGeneratedGames[lottery] ? lastGeneratedGames[lottery].estrategia : (generatedGameStrategyP ? generatedGameStrategyP.textContent.replace('Estratégia IA: ', '') : 'N/A'); const checkResultText = lastGeneratedGames[lottery] ? lastGeneratedGames[lottery].checkResult : (generatedGameCheckResultDiv ? generatedGameCheckResultDiv.innerHTML : null); firestoreDB.collection('userGames').add({ userId: currentUser.uid, userEmail: currentUser.email, lottery: lottery, game: jogoArray, strategy: estrategia, savedAt: firebase.firestore.FieldValue.serverTimestamp(), checkedResult: checkResultText }).then(() => { alert("Jogo salvo!"); if(myGamesSection && myGamesSection.classList.contains('active-section')) loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); }).catch((error) => { alert(`Erro ao salvar: ${error.message}`); }); });
    if (filterLotteryMyGamesSelect) filterLotteryMyGamesSelect.addEventListener('change', (e) => { if (currentUser) loadUserGames(e.target.value); });
    
    console.log("SCRIPT.JS: Final do script atingido, todos os listeners configurados.");
});
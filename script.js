// script.js (Seu código de 601 linhas + minhas atualizações integradas)
document.addEventListener('DOMContentLoaded', () => {
    console.log("SCRIPT.JS: DOMContentLoaded event fired. Ver 10.4 (Refatoração UI + Cósmicos)");
    const domContentLoadedTimestamp = Date.now(); 

    // --- Constantes de Tempo da Splash Screen --- (DO SEU CÓDIGO)
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

    // --- Seletores de Elementos (DO SEU CÓDIGO + NOVOS) ---
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
    // Seletores do Gerador Rápido (Antigo Gerador Inteligente)
    const quickHunchLotteryTypeSelect = document.getElementById('quick-hunch-lottery-type');
    const generateQuickHunchBtn = document.getElementById('generate-quick-hunch-btn');
    const quickHunchOutputDiv = document.getElementById('quick-hunch-output');
    const quickHunchNumbersDiv = document.getElementById('quick-hunch-numbers');
    const quickHunchStrategyP = document.getElementById('quick-hunch-strategy');
    const saveQuickHunchBtn = document.getElementById('save-quick-hunch-btn');
    const checkQuickHunchBtn = document.getElementById('check-quick-hunch-btn');
    const quickHunchCheckResultDiv = document.getElementById('quick-hunch-check-result');
    
    const apiResultsPre = document.getElementById('api-results');
    const resultsLotteryNameSpan = document.getElementById('results-lottery-name');
    const fetchResultsBtn = document.getElementById('fetch-results-btn'); // Certifique-se que este ID existe no HTML para o card de resultados

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
    const manualProbLotteryTypeSelect = document.getElementById('manual-prob-lottery-type');
    const manualProbUserNumbersInput = document.getElementById('manual-prob-user-numbers');
    const manualCalculateProbBtn = document.getElementById('manual-calculate-prob-btn');
    const manualProbabilityResultDisplay = document.getElementById('manual-probability-result-display');
    const manualProbNumbersCountFeedback = document.getElementById('manual-prob-numbers-count-feedback');

    // === NOVOS Seletores para Palpites Esotéricos e Banner Promocional (ADICIONADOS) ===
    const esotericLotteryTypeSelect = document.getElementById('esoteric-lottery-type');
    const birthDateInput = document.getElementById('birth-date-input');
    const generateEsotericHunchBtn = document.getElementById('generate-esoteric-hunch-btn');
    const esotericHunchCard = document.getElementById('esoteric-hunch-card'); // Para mostrar/esconder
    const esotericHunchOutputDiv = document.getElementById('esoteric-hunch-output');
    const esotericHunchNumbersDiv = document.getElementById('esoteric-hunch-numbers');
    const esotericHunchMethodP = document.getElementById('esoteric-hunch-method');
    const esotericHunchHistoryCheckDiv = document.getElementById('esoteric-hunch-history-check');
    const saveEsotericHunchBtn = document.getElementById('save-esoteric-hunch-btn');
    const checkEsotericHunchBtn = document.getElementById('check-esoteric-hunch-btn');
    
    const cosmicPromoBanner = document.getElementById('cosmic-promo-banner');
    const promoRegisterBtn = document.getElementById('promo-register-btn');
    const promoLoginBtn = document.getElementById('promo-login-btn');
    // === FIM DOS NOVOS Seletores ===
    
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
    let lastGeneratedGame = { // Alterado para um único objeto para o último jogo gerado (rápido ou esotérico)
        type: null, // 'quick' ou 'esoteric'
        lottery: null,
        jogo: [],
        estrategia: '',
        checkResult: ''
    };  
    let criticalSplashTimeout; 
    let firebaseInitAttempts = 0; 
    const maxFirebaseInitAttempts = 10; 
    const LOTTERY_CONFIG_JS = { 
        megasena: { count: 6, color: "#209869" }, 
        lotofacil: { count: 15, color: "#930089" },
        quina: { count: 5, color: "#260085" }, 
        lotomania: { count_sorteadas: 20, count_apostadas: 50, color: "#f78100" }
    };
    
    // --- Funções Utilitárias (showGlobalError, disableFirebaseFeatures, etc.) ---
    // (COLE SUAS FUNÇÕES showGlobalError, disableFirebaseFeatures, enableFirebaseFeatures, setActiveSection AQUI)
    function showGlobalError(message) { /* ... */ }
    function disableFirebaseFeatures() { /* ... */ }
    function enableFirebaseFeatures() { /* ... */ }
    function setActiveSection(sectionId) { /* ... */ }


    // --- FUNÇÃO fetchData (MODIFICADA para aceitar 'options') ---
    async function fetchData(endpoint, options = {}) {
        const url = `${BACKEND_URL_BASE}/api/main/${endpoint}`; // Seu prefixo de API
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorText = await response.text();
                let errorJson = {};
                try { errorJson = JSON.parse(errorText); } catch(e) { /* ignora */ }
                const messageDetail = errorJson.message || (errorJson.data ? errorJson.data.detalhes || errorJson.data.erro : null) || errorJson.erro || `Erro HTTP ${response.status}: ${errorText.substring(0,100)}`;
                console.error(`SCRIPT.JS: HTTP Error ${response.status} for ${url}:`, messageDetail);
                throw { status: response.status, message: messageDetail, data: errorJson };
            }
            if (response.status === 204) return {}; 
            return await response.json();
        } catch (error) {
            console.error(`SCRIPT.JS: Error fetching ${url}:`, error);
            throw error;
        }
    }
        
    // --- SUAS FUNÇÕES DE BUSCA E EXIBIÇÃO DE DADOS EXISTENTES ---
    // (animateCounter, fetchPlatformStats, fetchRecentWinningPools, fetchTopWinners, etc.)
    // Mantenha o código original dessas funções aqui, garantindo que usam a fetchData acima.
    function animateCounter(element, finalValueInput) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    async function fetchPlatformStats() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    async function fetchRecentWinningPools() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    async function fetchTopWinners() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    async function fetchAndDisplayFrequencyStats(lotteryName) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    async function fetchAndDisplayPairFrequencyStats(lotteryName) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    async function fetchAndDisplayCityStats(lotteryName) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    async function fetchAndDisplayCityPrizeSumStats(lotteryName) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function initializeCarousels() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function openModal(modalElement) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function closeModal(modalElement) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function showAppContentNow() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function initializeFirebase() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function attemptFirebaseInit() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    async function fetchAndDisplayResults(lottery) {  /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function renderGameNumbers(container, numbersArray, highlightedNumbers = [], almostNumbers = []) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function triggerConfetti() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function checkGame(userGameNumbers, officialResults) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }

    // === FUNÇÃO updateLoginUI (MODIFICADA para Palpites Cósmicos e Banner) ===
    function updateLoginUI(user) {
        const navItems = document.querySelectorAll('#main-nav .nav-item');
        if (user) {
            // UI para usuário logado (como antes)
            if (loginModalBtn) loginModalBtn.style.display = 'none';
            if (registerModalBtn) registerModalBtn.style.display = 'none';
            if (userInfoDiv) userInfoDiv.style.display = 'flex';
            if (userEmailSpan) userEmailSpan.textContent = user.email.split('@')[0];
            if (logoutBtn) logoutBtn.style.display = 'inline-block';
            if (mainNav) mainNav.style.display = 'flex';
            if (navItems) navItems.forEach(item => item.style.display = 'flex');
            // if (gameGenerationOutputDiv && gameGenerationOutputDiv.dataset.game && saveGameBtn) saveGameBtn.style.display = 'inline-block';
            if (typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos");
            if (typeof setActiveSection === "function") setActiveSection('dashboard-section');
            
            // Lógica para Palpites Cósmicos e Banner
            if (esotericHunchCard) esotericHunchCard.style.display = 'block'; // MOSTRA card esotérico
            if (cosmicPromoBanner) cosmicPromoBanner.style.display = 'none'; // ESCONDE banner promocional
        } else {
            // UI para usuário deslogado (como antes)
            if (loginModalBtn) loginModalBtn.style.display = 'inline-block';
            if (registerModalBtn) registerModalBtn.style.display = 'inline-block';
            if (userInfoDiv) userInfoDiv.style.display = 'none';
            if (userEmailSpan) userEmailSpan.textContent = '';
            if (logoutBtn) logoutBtn.style.display = 'none';
            if (mainNav) mainNav.style.display = 'none';
            if (navItems) navItems.forEach(item => item.style.display = 'none');
            // if (saveGameBtn) saveGameBtn.style.display = 'none';
            if (savedGamesContainer) savedGamesContainer.innerHTML = '';
            if (noSavedGamesP) noSavedGamesP.style.display = 'block';
            if (typeof setActiveSection === "function") setActiveSection('dashboard-section');

            // Lógica para Palpites Cósmicos e Banner
            if (esotericHunchCard) esotericHunchCard.style.display = 'none'; // ESCONDE card esotérico
            if (cosmicPromoBanner) cosmicPromoBanner.style.display = 'block'; // MOSTRA banner promocional
        }
        // Esconder botões de salvar palpites se deslogado, mostrar se logado (após um palpite ser gerado)
        if (saveQuickHunchBtn) saveQuickHunchBtn.style.display = user && quickHunchOutputDiv.style.display !== 'none' ? 'inline-block' : 'none';
        if (saveEsotericHunchBtn) saveEsotericHunchBtn.style.display = user && esotericHunchOutputDiv.style.display !== 'none' ? 'inline-block' : 'none';
    }
    // === FIM DA MODIFICAÇÃO updateLoginUI ===

    // --- SUAS FUNÇÕES DE JOGOS SALVOS E PROBABILIDADE MANUAL EXISTENTES ---
    async function loadUserGames(filterLottery = "todos") { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function createGameCardElement(docId, gameData) { /* ... (COLE SEU CÓDIGO AQUI, adapte os botões de salvar/conferir se necessário) ... */ }
    function updateManualProbNumbersFeedback() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }

    // === NOVA FUNÇÃO PARA GERAR E EXIBIR PALPITE ESOTÉRICO ===
    async function generateAndDisplayEsotericHunch() {
        if (!esotericLotteryTypeSelect || !birthDateInput || !generateEsotericHunchBtn ||
            !esotericHunchOutputDiv || !esotericHunchNumbersDiv || !esotericHunchMethodP || !esotericHunchHistoryCheckDiv) {
            console.error("SCRIPT.JS: Elementos DOM para Palpite Cósmico não encontrados.");
            return;
        }

        const lotteryName = esotericLotteryTypeSelect.value;
        const birthDateRaw = birthDateInput.value.trim();
        const birthDate = birthDateRaw.replace(/\D/g, '');

        if (!birthDate) { alert("Por favor, insira sua data de nascimento."); birthDateInput.focus(); return; }
        if (birthDate.length !== 8) { alert("Formato da data de nascimento inválido. Use DDMMAAAA."); birthDateInput.focus(); return; }
        
        generateEsotericHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando Magia...';
        generateEsotericHunchBtn.disabled = true;
        esotericHunchOutputDiv.style.display = 'block';
        esotericHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>';
        esotericHunchMethodP.textContent = 'Consultando os astros e os números...';
        esotericHunchHistoryCheckDiv.innerHTML = '';
        if(saveEsotericHunchBtn) saveEsotericHunchBtn.style.display = 'none';
        if(checkEsotericHunchBtn) checkEsotericHunchBtn.style.display = 'none';


        try {
            const requestBody = { data_nascimento: birthDate };
            const data = await fetchData(`palpite-esoterico/${lotteryName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestBody)
            });

            if (data.erro) { throw new Error(data.erro); }
            if (!data.palpite_gerado) { throw new Error("A API não retornou um palpite válido."); }

            renderGameNumbers(esotericHunchNumbersDiv, data.palpite_gerado);
            esotericHunchMethodP.textContent = `Método: ${data.metodo_geracao || 'Indefinido'}`;
            
            let historyHtml = `<strong>Histórico desta combinação:</strong><br>`;
            if (data.historico_desta_combinacao) {
                const hist = data.historico_desta_combinacao;
                historyHtml += `Já foi premiada (faixa principal)? <span style="color: ${hist.ja_foi_premiada_faixa_principal ? '#2ecc71' : '#ff4765'}; font-weight: bold;">${hist.ja_foi_premiada_faixa_principal ? 'Sim' : 'Não'}</span><br>`;
                historyHtml += `Vezes premiada: ${hist.vezes_premiada_faixa_principal}<br>`;
                historyHtml += `Valor total ganho (aprox.): ${hist.valor_total_ganho_faixa_principal_formatado}`;
            } else { historyHtml += "Não foi possível verificar o histórico."; }
            esotericHunchHistoryCheckDiv.innerHTML = historyHtml;

            // Atualiza lastGeneratedGame para o palpite esotérico
            lastGeneratedGame = { 
                type: 'esoteric', 
                lottery: lotteryName, 
                jogo: data.palpite_gerado, 
                estrategia: data.metodo_geracao || 'Indefinido', 
                checkResult: esotericHunchHistoryCheckDiv.innerHTML 
            };
            if (currentUser && saveEsotericHunchBtn) saveEsotericHunchBtn.style.display = 'inline-block';
            if (checkEsotericHunchBtn) checkEsotericHunchBtn.style.display = 'inline-block';


        } catch (error) {
            console.error("SCRIPT.JS: Erro ao gerar palpite esotérico:", error);
            esotericHunchNumbersDiv.innerHTML = '';
            esotericHunchMethodP.textContent = '';
            esotericHunchHistoryCheckDiv.innerHTML = `<p class="error-message">Falha ao gerar palpite: ${error.message || 'Erro desconhecido.'}</p>`;
            lastGeneratedGame = { type: null }; // Limpa em caso de erro
        } finally {
            generateEsotericHunchBtn.innerHTML = '<i class="fas fa-meteor"></i> Gerar Palpite Cósmico';
            generateEsotericHunchBtn.disabled = false;
        }
    }
    // === FIM DA NOVA FUNÇÃO ===

    // === FUNÇÃO PARA GERADOR RÁPIDO (ANTIGO GERADOR INTELIGENTE SIMPLIFICADO) ===
    async function generateAndDisplayQuickHunch() {
        if (!quickHunchLotteryTypeSelect || !generateQuickHunchBtn || !quickHunchOutputDiv || !quickHunchNumbersDiv || !quickHunchStrategyP) {
            console.error("SCRIPT.JS: Elementos DOM para Palpite Rápido não encontrados.");
            return;
        }
        const lottery = quickHunchLotteryTypeSelect.value;
        
        generateQuickHunchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Gerando...';
        generateQuickHunchBtn.disabled = true;
        quickHunchOutputDiv.style.display = 'block';
        quickHunchNumbersDiv.innerHTML = '<div class="spinner small-spinner"></div>';
        quickHunchStrategyP.textContent = 'Gerando um palpite aleatório rápido...';
        if(saveQuickHunchBtn) saveQuickHunchBtn.style.display = 'none';
        if(checkQuickHunchBtn) checkQuickHunchBtn.style.display = 'none';
        if(quickHunchCheckResultDiv) quickHunchCheckResultDiv.innerHTML = '';

        try {
            // O backend para gerar_jogo agora só tem a estratégia "aleatorio_rapido" (ou o que você definiu lá)
            const data = await fetchData(`gerar_jogo/${lottery}?estrategia=aleatorio_rapido`); // Força estratégia

            if (data.erro) { throw new Error(data.detalhes || data.erro);  }
            if (!data.jogo || !Array.isArray(data.jogo) || data.jogo.length === 0) {
                throw new Error("Palpite inválido retornado pela IA.");
            }
            renderGameNumbers(quickHunchNumbersDiv, data.jogo);
            quickHunchStrategyP.textContent = `Estratégia: ${data.estrategia_usada || 'Aleatório Rápido'}`;
            
            lastGeneratedGame = { 
                type: 'quick', 
                lottery: lottery, 
                jogo: data.jogo, 
                estrategia: data.estrategia_usada || 'Aleatório Rápido',
                checkResult: ''
             };
            if (currentUser && saveQuickHunchBtn) saveQuickHunchBtn.style.display = 'inline-block';
            if (checkQuickHunchBtn) checkQuickHunchBtn.style.display = 'inline-block';

        } catch (error) {
            console.error("SCRIPT.JS: Erro ao gerar palpite rápido:", error);
            quickHunchNumbersDiv.innerHTML = `<p class="error-message">${error.message || 'Falha ao gerar palpite.'}</p>`;
            quickHunchStrategyP.textContent = 'Erro ao gerar.';
            lastGeneratedGame = { type: null };
        } finally {
            generateQuickHunchBtn.innerHTML = '<i class="fas fa-random"></i> Gerar Palpite Rápido';
            generateQuickHunchBtn.disabled = false;
        }
    }
    // === FIM DA FUNÇÃO PARA GERADOR RÁPIDO ===


    // === LÓGICA PARA OS BOTÕES DE SALVAR E CONFERIR (Generalizada) ===
    function setupSaveHunchButton(buttonElement, outputDiv) {
        if (buttonElement) {
            buttonElement.addEventListener('click', () => {
                if (!firestoreDB || !currentUser || !outputDiv || !lastGeneratedGame.type || lastGeneratedGame.lottery !== outputDiv.dataset.lotteryTypeFromSelect) { // Checa se é do select correto
                    alert("Logue e gere um palpite válido para salvar.");
                    return;
                }
                const gameToSave = lastGeneratedGame.jogo;
                const lotteryToSave = lastGeneratedGame.lottery;
                const strategyToSave = lastGeneratedGame.estrategia;
                const checkResultToSave = lastGeneratedGame.checkResult;

                firestoreDB.collection('userGames').add({
                    userId: currentUser.uid, userEmail: currentUser.email,
                    lottery: lotteryToSave, game: gameToSave, strategy: strategyToSave,
                    savedAt: firebase.firestore.FieldValue.serverTimestamp(),
                    checkedResult: checkResultToSave || null
                }).then(() => {
                    alert("Palpite salvo com sucesso!");
                    if (myGamesSection && myGamesSection.classList.contains('active-section')) {
                        loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos");
                    }
                }).catch((error) => {
                    alert(`Erro ao salvar palpite: ${error.message}`);
                    console.error("SCRIPT.JS: Erro ao salvar palpite:", error);
                });
            });
        }
    }
    
    function setupCheckHunchButton(buttonElement, outputDiv, numbersDiv, checkResultDisplayDiv, lotterySelectElement) {
         if (buttonElement) {
             buttonElement.addEventListener('click', async () => {
                 const currentLottery = lotterySelectElement.value;
                 if (!lastGeneratedGame.jogo || lastGeneratedGame.lottery !== currentLottery) {
                     checkResultDisplayDiv.innerHTML = '<span class="misses">Gere um palpite para esta loteria primeiro.</span>';
                     return;
                 }

                 let resultsToUse = lastFetchedResults[currentLottery];
                 if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) {
                     checkResultDisplayDiv.innerHTML = `<div class="spinner small-spinner"></div> Buscando últimos resultados...`;
                     try {
                         resultsToUse = await fetchData(`resultados/${currentLottery}`);
                         if(resultsToUse) resultsToUse.loteria_tipo = currentLottery; // Adiciona para checkGame
                         lastFetchedResults[currentLottery] = resultsToUse;
                         // Atualiza o card de "Últimos Resultados" se for a loteria selecionada globalmente
                         if (lotteryTypeSelect && lotteryTypeSelect.value === currentLottery && apiResultsPre) {
                             let displayText = resultsToUse.erro || resultsToUse.aviso || `Concurso: ${resultsToUse.ultimo_concurso || 'N/A'}...`;
                             if (resultsToUse.numeros && resultsToUse.numeros.length > 0) {
                                 displayText = `Concurso: ${resultsToUse.ultimo_concurso || 'N/A'}\nData: ${resultsToUse.data || 'N/A'}\nNúmeros Sorteados: ${resultsToUse.numeros.join(', ')}`;
                             }
                             apiResultsPre.textContent = displayText;
                         }
                     } catch (e) {
                         checkResultDisplayDiv.innerHTML = `<span class="misses">Falha ao buscar resultados.</span>`;
                         return;
                     }
                 }
                 if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) {
                     checkResultDisplayDiv.innerHTML = `<span class="misses">Resultados oficiais indisponíveis.</span>`;
                     return;
                 }

                 const result = checkGame(lastGeneratedGame.jogo, resultsToUse);
                 checkResultDisplayDiv.innerHTML = `<span class="${result.hits > 0 ? 'hits' : (result.almostNumbers.length > 0 ? 'almost-text' : 'misses')}">${result.message}</span>`;
                 renderGameNumbers(numbersDiv, lastGeneratedGame.jogo, result.hitNumbers, result.almostNumbers);
                 lastGeneratedGame.checkResult = checkResultDisplayDiv.innerHTML;
             });
         }
    }
    // === FIM DAS FUNÇÕES DE SALVAR E CONFERIR ===


    // --- EVENT LISTENERS ---
    // (Seus event listeners existentes para modais, navegação, fetchResultsBtn, lotteryTypeSelect (agora quickHunchLotteryTypeSelect para stats),
    //  generateGameBtn (agora generateQuickHunchBtn), checkGeneratedGameBtn (agora checkQuickHunchBtn), auth, saveGameBtn (agora saveQuickHunchBtn), etc.)
    if (splashProgressBarFill && splashProgressContainer) { /* ... (splash logic) ... */ }
    criticalSplashTimeout = setTimeout(() => { /* ... (splash logic) ... */ }, SPLASH_MINIMUM_VISIBLE_TIME + 1500);  
    setTimeout(attemptFirebaseInit, 100); 

    if(loginModalBtn) loginModalBtn.addEventListener('click', () => openModal(loginModal));
    if(registerModalBtn) registerModalBtn.addEventListener('click', () => openModal(registerModal));
    if(closeLoginModalBtn) closeLoginModalBtn.addEventListener('click', () => closeModal(loginModal));
    if(closeRegisterModalBtn) closeRegisterModalBtn.addEventListener('click', () => closeModal(registerModal));
    window.addEventListener('click', (event) => { if (event.target === loginModal) closeModal(loginModal); if (event.target === registerModal) closeModal(registerModal); });
    if (navDashboardBtn) navDashboardBtn.addEventListener('click', () => setActiveSection('dashboard-section'));
    if (navMyGamesBtn) navMyGamesBtn.addEventListener('click', () => { setActiveSection('my-games-section'); if (currentUser && typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); });
    if (navPoolsBtn) navPoolsBtn.addEventListener('click', () => setActiveSection('pools-section'));
    
    // Listener para o select de loteria principal (que atualiza as estatísticas)
    // Usa quickHunchLotteryTypeSelect como o select principal para estatísticas agora, ou o antigo lotteryTypeSelect se preferir.
    // Vou assumir que o select dentro do card de "Palpite Rápido" agora também controla as estatísticas.
    const mainLotterySelectForStats = quickHunchLotteryTypeSelect || lotteryTypeSelect; // Escolha um
    if (mainLotterySelectForStats) {
        mainLotterySelectForStats.addEventListener('change', () => {
            const selectedLottery = mainLotterySelectForStats.value;
            if (resultsLotteryNameSpan && mainLotterySelectForStats.options[mainLotterySelectForStats.selectedIndex]) {
                 resultsLotteryNameSpan.textContent = mainLotterySelectForStats.options[mainLotterySelectForStats.selectedIndex].text;
            }
            fetchAndDisplayResults(selectedLottery); 
            fetchAndDisplayFrequencyStats(selectedLottery); 
            fetchAndDisplayPairFrequencyStats(selectedLottery); 
            fetchAndDisplayCityStats(selectedLottery);
            fetchAndDisplayCityPrizeSumStats(selectedLottery);
        });
    }
    if (fetchResultsBtn && mainLotterySelectForStats) { 
         fetchResultsBtn.addEventListener('click', () => {
             const selectedLottery = mainLotterySelectForStats.value;
              fetchAndDisplayResults(selectedLottery); fetchAndDisplayFrequencyStats(selectedLottery); 
              fetchAndDisplayPairFrequencyStats(selectedLottery); fetchAndDisplayCityStats(selectedLottery);
              fetchAndDisplayCityPrizeSumStats(selectedLottery);
         });
     }

    // Listener para o Gerador Rápido (antigo Gerador Inteligente)
    if (generateQuickHunchBtn && quickHunchLotteryTypeSelect) { 
        generateQuickHunchBtn.addEventListener('click', generateAndDisplayQuickHunch);
    }
    // Configura botões de salvar e conferir para o Palpite Rápido
    if (quickHunchOutputDiv && quickHunchLotteryTypeSelect) { // Para pegar o tipo de loteria do select correto
         setupSaveHunchButton(saveQuickHunchBtn, quickHunchOutputDiv);
         setupCheckHunchButton(checkQuickHunchBtn, quickHunchOutputDiv, quickHunchNumbersDiv, quickHunchCheckResultDiv, quickHunchLotteryTypeSelect);
         quickHunchOutputDiv.dataset.lotteryTypeFromSelect = quickHunchLotteryTypeSelect.id; // Ajuda a identificar o select
    }


    // Listeners de Autenticação (loginSubmitBtn, registerSubmitBtn, logoutBtn)
    if(loginSubmitBtn) loginSubmitBtn.addEventListener('click', () => { /* ... (sua lógica de login) ... */ });
    if(registerSubmitBtn) registerSubmitBtn.addEventListener('click', () => { /* ... (sua lógica de registro) ... */ });
    if(logoutBtn) logoutBtn.addEventListener('click', () => { /* ... (sua lógica de logout) ... */ });
    
    // Listener para filtro de jogos salvos
    if (filterLotteryMyGamesSelect) filterLotteryMyGamesSelect.addEventListener('change', (e) => { if (currentUser && typeof loadUserGames === "function") loadUserGames(e.target.value); });
    
    // Listeners para Probabilidade Manual
    if (manualProbUserNumbersInput && manualProbLotteryTypeSelect) { 
        manualProbUserNumbersInput.addEventListener('input', updateManualProbNumbersFeedback);
        manualProbLotteryTypeSelect.addEventListener('change', () => { /* ... (sua lógica) ... */ });
        const initialSelectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex];
        if (initialSelectedOption && initialSelectedOption.dataset.count && initialSelectedOption.dataset.min && initialSelectedOption.dataset.max){
            manualProbUserNumbersInput.placeholder = `Ex: 01,02,... (${initialSelectedOption.dataset.count} de ${initialSelectedOption.dataset.min}-${initialSelectedOption.dataset.max})`;
        }
        updateManualProbNumbersFeedback(); 
    }
    if (manualCalculateProbBtn) { manualCalculateProbBtn.addEventListener('click', async () => { /* ... (sua lógica) ... */ }); }


    // === NOVOS EVENT LISTENERS (ADICIONADOS) ===
    if (generateEsotericHunchBtn) {
        generateEsotericHunchBtn.addEventListener('click', generateAndDisplayEsotericHunch);
    }
    // Configura botões de salvar e conferir para o Palpite Esotérico
    if (esotericHunchOutputDiv && esotericLotteryTypeSelect) { // Para pegar o tipo de loteria do select correto
         setupSaveHunchButton(saveEsotericHunchBtn, esotericHunchOutputDiv);
         setupCheckHunchButton(checkEsotericHunchBtn, esotericHunchOutputDiv, esotericHunchNumbersDiv, esotericHunchHistoryCheckDiv, esotericLotteryTypeSelect);
         esotericHunchOutputDiv.dataset.lotteryTypeFromSelect = esotericLotteryTypeSelect.id; // Ajuda a identificar o select
    }

    // Listeners para os botões no banner promocional e no prompt do card esotérico
    if (promoRegisterBtn && registerModalBtn) {
        promoRegisterBtn.addEventListener('click', () => openModal(registerModal));
    }
    if (promoLoginBtn && loginModalBtn) {
        promoLoginBtn.addEventListener('click', () => openModal(loginModal));
    }
    // (Os listeners para esotericPromptRegisterBtn e esotericPromptLoginBtn já estavam na minha sugestão anterior,
    //  garanta que eles estejam aqui também se você manteve aqueles botões no HTML)
    const esotericPromptRegisterBtnInstance = document.getElementById('esoteric-prompt-register-btn'); // Re-seleciona se necessário
    const esotericPromptLoginBtnInstance = document.getElementById('esoteric-prompt-login-btn'); // Re-seleciona se necessário

    if (esotericPromptRegisterBtnInstance && registerModalBtn) {
        esotericPromptRegisterBtnInstance.addEventListener('click', () => { openModal(registerModal); });
    }
    if (esotericPromptLoginBtnInstance && loginModalBtn) {
        esotericPromptLoginBtnInstance.addEventListener('click', () => { openModal(loginModal); });
    }
    // === FIM DOS NOVOS EVENT LISTENERS ===
    
    console.log("SCRIPT.JS: Final do script atingido, todos os listeners configurados.");
});
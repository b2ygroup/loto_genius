// script.js (Seu código da resposta #40 + Minhas Refatorações da Resposta #43, revisado)
document.addEventListener('DOMContentLoaded', () => {
    console.log("SCRIPT.JS: DOMContentLoaded event fired. Ver 10.4 (Refatoração UI + Cósmicos)");
    const domContentLoadedTimestamp = Date.now(); 

    // --- Constantes de Tempo da Splash Screen (DO SEU CÓDIGO) ---
    const SPLASH_LOGO_ANIM_MAX_DELAY = 1300; 
    const SPLASH_LOGO_ANIM_DURATION = 600;  
    // ... (resto das suas constantes de splash)
    const SPLASH_MINIMUM_VISIBLE_TIME = Math.max(
        SPLASH_LOGO_ANIM_MAX_DELAY + SPLASH_LOGO_ANIM_DURATION,
        2200 + 1000, // SPLASH_TEXT_ANIM_DELAY + SPLASH_TEXT_ANIM_DURATION
        2500 + 3000  // SPLASH_PROGRESS_BAR_START_DELAY + SPLASH_PROGRESS_BAR_FILL_DURATION
    ) + 1000;


    // --- Seletores de Elementos (DO SEU CÓDIGO + NOVOS para refatoração) ---
    const accessibleSplashScreen = document.getElementById('accessible-splash-screen');
    // ... (todos os seus seletores existentes da resposta #40) ...
    const lotteryTypeSelect = document.getElementById('lottery-type'); // Este era o seletor do Gerador Inteligente
    const iaStrategySelect = document.getElementById('ia-strategy-select'); // Do Gerador Inteligente
    const generateGameBtn = document.getElementById('generate-game-btn'); // Do Gerador Inteligente
    const gameGenerationOutputDiv = document.getElementById('game-generation-output');
    const generatedGameNumbersDiv = document.getElementById('generated-game-numbers');
    const generatedGameStrategyP = document.getElementById('generated-game-strategy');
    const saveGameBtn = document.getElementById('save-game-btn'); // Do Gerador Inteligente
    const checkGeneratedGameBtn = document.getElementById('check-generated-game-btn'); // Do Gerador Inteligente
    const generatedGameCheckResultDiv = document.getElementById('generated-game-check-result');
    const simulatePremiumCheckbox = document.getElementById('simulate-premium-checkbox');


    // NOVOS Seletores para a refatoração
    const quickHunchLotteryTypeSelect = document.getElementById('quick-hunch-lottery-type');
    const generateQuickHunchBtn = document.getElementById('generate-quick-hunch-btn');
    const quickHunchOutputDiv = document.getElementById('quick-hunch-output');
    const quickHunchNumbersDiv = document.getElementById('quick-hunch-numbers');
    const quickHunchStrategyP = document.getElementById('quick-hunch-strategy');
    const saveQuickHunchBtn = document.getElementById('save-quick-hunch-btn');
    const checkQuickHunchBtn = document.getElementById('check-quick-hunch-btn');
    const quickHunchCheckResultDiv = document.getElementById('quick-hunch-check-result');
    
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
    // (O antigo `esotericRegisterPromptDiv` foi removido pois o banner e o card esotérico (apenas para logados) cuidam disso)
    
    // Certifique-se que TODOS os outros seletores do seu script original estão aqui.
    // ... (statsJogosGeradosSpan, recentPoolsList, etc. etc.)

    let splashHiddenTimestamp = 0; 
    if (document.getElementById('current-year')) document.getElementById('current-year').textContent = new Date().getFullYear();
    let BACKEND_URL_BASE;
    if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1" || window.location.protocol === "file:") { 
        BACKEND_URL_BASE = 'http://127.0.0.1:5000'; 
    } else { 
        BACKEND_URL_BASE = '';
    }
    
    let firebaseApp, firebaseAuth, firestoreDB, currentUser = null;
    let lastFetchedResults = {}; 
    let lastGeneratedHunch = { // Armazena o último palpite gerado (rápido OU esotérico)
        type: null, // 'quick' ou 'esoteric'
        lottery: null,
        jogo: [],
        estrategia_metodo: '', // Nome da estratégia ou método
        outputDiv: null, // Referência ao DIV de saída do palpite
        numbersDiv: null, // Referência ao DIV dos números
        checkResultDiv: null, // Referência ao DIV do resultado da conferência
        saveButton: null, // Referência ao botão de salvar
        checkButton: null // Referência ao botão de conferir
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

    // --- Funções Utilitárias (COPIE AS SUAS AQUI) ---
    function showGlobalError(message) { /* ... (sua implementação) ... */ }
    function disableFirebaseFeatures() { /* ... (sua implementação) ... */ }
    function enableFirebaseFeatures() { /* ... (sua implementação) ... */ }
    function setActiveSection(sectionId) { /* ... (sua implementação) ... */ }

    // --- FUNÇÃO fetchData (MODIFICADA para aceitar 'options') ---
    async function fetchData(endpoint, options = {}) {
        const url = `${BACKEND_URL_BASE}/api/main/${endpoint}`;
        console.log(`SCRIPT.JS: Fetching ${url} com options:`, options.method || 'GET');
        try {
            const response = await fetch(url, options);
            const responseText = await response.text(); // Ler como texto primeiro
            if (!response.ok) {
                let errorJson = {};
                try { errorJson = JSON.parse(responseText); } catch(e) { /* ignora */ }
                const messageDetail = errorJson.message || (errorJson.data ? errorJson.data.detalhes || errorJson.data.erro : null) || errorJson.erro || responseText.substring(0,250);
                console.error(`SCRIPT.JS: HTTP Error ${response.status} for ${url}:`, messageDetail);
                throw { status: response.status, message: messageDetail, data: errorJson };
            }
            if (response.status === 204 || !responseText) return {}; // Trata respostas vazias
            return JSON.parse(responseText); // Parsear para JSON só se tiver conteúdo
        } catch (error) {
            console.error(`SCRIPT.JS: Error fetching ${url}:`, error);
            throw error;
        }
    }
        
    // --- SUAS FUNÇÕES DE BUSCA E EXIBIÇÃO DE DADOS (COPIE AS SUAS AQUI) ---
    // (animateCounter, fetchPlatformStats, fetchRecentWinningPools, fetchTopWinners, etc.)
    function animateCounter(element, finalValueInput) { /* ... (sua implementação) ... */ }
    async function fetchPlatformStats() { /* ... (sua implementação) ... */ }
    async function fetchRecentWinningPools() { /* ... (sua implementação) ... */ }
    async function fetchTopWinners() { /* ... (sua implementação) ... */ }
    async function fetchAndDisplayFrequencyStats(lotteryName) { /* ... (sua implementação) ... */ }
    async function fetchAndDisplayPairFrequencyStats(lotteryName) { /* ... (sua implementação) ... */ }
    async function fetchAndDisplayCityStats(lotteryName) { /* ... (sua implementação) ... */ }
    async function fetchAndDisplayCityPrizeSumStats(lotteryName) { /* ... (sua implementação) ... */ }
    function initializeCarousels() { /* ... (sua implementação) ... */ }
    function openModal(modalElement) { /* ... (sua implementação) ... */ }
    function closeModal(modalElement) { /* ... (sua implementação) ... */ }
    function showAppContentNow() { /* ... (sua implementação) ... */ }
    function initializeFirebase() { /* ... (sua implementação) ... */ }
    function attemptFirebaseInit() { /* ... (sua implementação) ... */ }
    async function fetchAndDisplayResults(lottery) {  /* ... (sua implementação) ... */ }
    function renderGameNumbers(container, numbersArray, highlightedNumbers = [], almostNumbers = []) { /* ... (sua implementação) ... */ }
    function triggerConfetti() { /* ... (sua implementação) ... */ }
    function checkGame(userGameNumbers, officialResults) { /* ... (sua implementação) ... */ }

    // === FUNÇÃO updateLoginUI (MODIFICADA para Palpites Cósmicos e Banner) ===
    function updateLoginUI(user) {
        // ... (sua lógica de UI existente para login/logout) ...
        const navItems = document.querySelectorAll('#main-nav .nav-item'); 
        const mainLotterySelectForStats = quickHunchLotteryTypeSelect || lotteryTypeSelect; // Para carregar stats

        if (user) { 
            if (loginModalBtn) loginModalBtn.style.display = 'none'; 
            if (registerModalBtn) registerModalBtn.style.display = 'none'; 
            if (userInfoDiv) userInfoDiv.style.display = 'flex'; 
            if (userEmailSpan) userEmailSpan.textContent = user.email.split('@')[0]; 
            if (logoutBtn) logoutBtn.style.display = 'inline-block'; 
            if (mainNav) mainNav.style.display = 'flex'; 
            if (navItems) navItems.forEach(item => item.style.display = 'flex'); 
            
            if (typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); 
            if (typeof setActiveSection === "function") setActiveSection('dashboard-section'); 
            
            // Palpites Cósmicos e Banner
            if (esotericHunchCard) esotericHunchCard.style.display = 'block';
            if (cosmicPromoBanner) cosmicPromoBanner.style.display = 'none'; 
        } else { 
            if (loginModalBtn) loginModalBtn.style.display = 'inline-block'; 
            if (registerModalBtn) registerModalBtn.style.display = 'inline-block'; 
            if (userInfoDiv) userInfoDiv.style.display = 'none'; 
            if (userEmailSpan) userEmailSpan.textContent = ''; 
            if (logoutBtn) logoutBtn.style.display = 'none'; 
            if (mainNav) mainNav.style.display = 'none'; 
            if (navItems) navItems.forEach(item => item.style.display = 'none'); 
            if (savedGamesContainer) savedGamesContainer.innerHTML = ''; 
            if (noSavedGamesP) noSavedGamesP.style.display = 'block'; 
            if (typeof setActiveSection === "function") setActiveSection('dashboard-section');

            // Palpites Cósmicos e Banner
            if (esotericHunchCard) esotericHunchCard.style.display = 'none';
            if (cosmicPromoBanner) cosmicPromoBanner.style.display = 'block';
        }
        // Atualiza visibilidade dos botões de salvar dinamicamente
        updateSaveButtonVisibility('quick');
        updateSaveButtonVisibility('esoteric');
    }
    // === FIM DA MODIFICAÇÃO updateLoginUI ===

    // --- SUAS FUNÇÕES DE JOGOS SALVOS E PROBABILIDADE MANUAL EXISTENTES ---
    async function loadUserGames(filterLottery = "todos") { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function createGameCardElement(docId, gameData) { /* ... (COLE SEU CÓDIGO AQUI) ... */ }
    function updateManualProbNumbersFeedback() { /* ... (COLE SEU CÓDIGO AQUI) ... */ }

    // === FUNÇÃO PARA GERAR PALPITE ALEATÓRIO RÁPIDO (NOVO/REFEITO) ===
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
        quickHunchStrategyP.textContent = 'Gerando um palpite aleatório...';
        if(saveQuickHunchBtn) saveQuickHunchBtn.style.display = 'none';
        if(checkQuickHunchBtn) checkQuickHunchBtn.style.display = 'none';
        if(quickHunchCheckResultDiv) quickHunchCheckResultDiv.innerHTML = '';

        try {
            const data = await fetchData(`gerar_jogo/${lottery}`); // Chama o endpoint simplificado
            console.log(`SCRIPT.JS: Palpite Rápido - Dados recebidos:`, data);

            if (data.erro) { throw new Error(data.detalhes || data.erro);  }
            if (!data.jogo || !Array.isArray(data.jogo) || data.jogo.length === 0) {
                throw new Error("Palpite inválido retornado.");
            }
            renderGameNumbers(quickHunchNumbersDiv, data.jogo);
            quickHunchStrategyP.textContent = `Estratégia: ${data.estrategia_usada || 'Aleatório Rápido'}`;
            
            lastGeneratedHunch = { 
                type: 'quick', 
                lottery: lottery, 
                jogo: data.jogo, 
                estrategia_metodo: data.estrategia_usada || 'Aleatório Rápido',
                outputDiv: quickHunchOutputDiv,
                numbersDiv: quickHunchNumbersDiv,
                checkResultDiv: quickHunchCheckResultDiv,
                saveButton: saveQuickHunchBtn,
                checkButton: checkQuickHunchBtn
            };
            updateSaveButtonVisibility('quick'); // Mostra botão salvar se logado
            if (checkQuickHunchBtn) checkQuickHunchBtn.style.display = 'inline-block';

        } catch (error) {
            console.error("SCRIPT.JS: Erro ao gerar palpite rápido:", error);
            quickHunchNumbersDiv.innerHTML = `<p class="error-message">${error.message || 'Falha ao gerar palpite.'}</p>`;
            quickHunchStrategyP.textContent = 'Erro ao gerar.';
            lastGeneratedHunch = { type: null };
        } finally {
            generateQuickHunchBtn.innerHTML = '<i class="fas fa-random"></i> Gerar Palpite Rápido';
            generateQuickHunchBtn.disabled = false;
        }
    }
    // === FIM DA FUNÇÃO PARA GERADOR RÁPIDO ===

    // === FUNÇÃO PARA GERAR E EXIBIR PALPITE ESOTÉRICO (COMO ANTES) ===
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

            lastGeneratedHunch = { 
                type: 'esoteric', 
                lottery: lotteryName, 
                jogo: data.palpite_gerado, 
                estrategia_metodo: data.metodo_geracao || 'Indefinido',
                outputDiv: esotericHunchOutputDiv,
                numbersDiv: esotericHunchNumbersDiv,
                checkResultDiv: esotericHunchHistoryCheckDiv,
                saveButton: saveEsotericHunchBtn,
                checkButton: checkEsotericHunchBtn
            };
            updateSaveButtonVisibility('esoteric');
            if (checkEsotericHunchBtn) checkEsotericHunchBtn.style.display = 'inline-block';

        } catch (error) {
            console.error("SCRIPT.JS: Erro ao gerar palpite esotérico:", error);
            esotericHunchNumbersDiv.innerHTML = '';
            esotericHunchMethodP.textContent = '';
            esotericHunchHistoryCheckDiv.innerHTML = `<p class="error-message">Falha ao gerar palpite: ${error.message || 'Erro desconhecido.'}</p>`;
            lastGeneratedHunch = { type: null };
        } finally {
            generateEsotericHunchBtn.innerHTML = '<i class="fas fa-meteor"></i> Gerar Palpite Cósmico';
            generateEsotericHunchBtn.disabled = false;
        }
    }
    // === FIM DA FUNÇÃO PALPITE ESOTÉRICO ===

    // === FUNÇÕES DE UTILIDADE PARA BOTÕES DE SALVAR/CONFERIR ===
    function updateSaveButtonVisibility(hunchType) {
        const saveButton = (hunchType === 'quick') ? saveQuickHunchBtn : saveEsotericHunchBtn;
        const outputDiv = (hunchType === 'quick') ? quickHunchOutputDiv : esotericHunchOutputDiv;
        if (saveButton) {
            saveButton.style.display = currentUser && outputDiv.style.display !== 'none' && lastGeneratedHunch.type === hunchType ? 'inline-block' : 'none';
        }
    }
    
    function setupSaveHunchButton(buttonElement, hunchType) {
        if (buttonElement) {
            buttonElement.addEventListener('click', () => {
                if (!firestoreDB || !currentUser || !lastGeneratedHunch.jogo || lastGeneratedHunch.type !== hunchType) {
                    alert("Logue e gere um palpite válido deste tipo para salvar.");
                    return;
                }
                const gameToSave = lastGeneratedHunch.jogo;
                const lotteryToSave = lastGeneratedHunch.lottery;
                const strategyToSave = lastGeneratedHunch.estrategia_metodo;
                // A conferência não será salva aqui, será feita sob demanda em "Meus Jogos"
                firestoreDB.collection('userGames').add({
                    userId: currentUser.uid, userEmail: currentUser.email,
                    lottery: lotteryToSave, game: gameToSave, strategy: strategyToSave,
                    savedAt: firebase.firestore.FieldValue.serverTimestamp(),
                    checkedResult: null // Resultado da conferência será atualizado depois
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
    
    function setupCheckHunchButton(buttonElement, numbersDisplayDiv, checkResultDisplayDiv, lotterySelectElement, hunchType) {
         if (buttonElement) {
             buttonElement.addEventListener('click', async () => {
                 const currentLottery = lotterySelectElement.value;
                 if (!lastGeneratedHunch.jogo || lastGeneratedHunch.lottery !== currentLottery || lastGeneratedHunch.type !== hunchType) {
                     checkResultDisplayDiv.innerHTML = '<span class="misses">Gere um palpite deste tipo para esta loteria primeiro.</span>';
                     return;
                 }

                 let resultsToUse = lastFetchedResults[currentLottery];
                 if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) {
                     checkResultDisplayDiv.innerHTML = `<div class="spinner small-spinner"></div> Buscando últimos resultados...`;
                     try {
                         resultsToUse = await fetchData(`resultados/${currentLottery}`);
                         if(resultsToUse) resultsToUse.loteria_tipo = currentLottery;
                         lastFetchedResults[currentLottery] = resultsToUse;
                         // Atualiza o card de "Últimos Resultados" principal se for a mesma loteria
                         const mainLotterySelectForStats = document.getElementById('quick-hunch-lottery-type') || document.getElementById('lottery-type'); // Adapte se o ID mudou
                         if (mainLotterySelectForStats && mainLotterySelectForStats.value === currentLottery && document.getElementById('api-results')) {
                             let displayText = resultsToUse.erro || resultsToUse.aviso || `Concurso: ${resultsToUse.ultimo_concurso || 'N/A'}...`;
                             if (resultsToUse.numeros && resultsToUse.numeros.length > 0) {
                                 displayText = `Concurso: ${resultsToUse.ultimo_concurso || 'N/A'}\nData: ${resultsToUse.data || 'N/A'}\nNúmeros Sorteados: ${resultsToUse.numeros.join(', ')}`;
                             }
                             document.getElementById('api-results').textContent = displayText;
                         }
                     } catch (e) { checkResultDisplayDiv.innerHTML = `<span class="misses">Falha ao buscar resultados.</span>`; return; }
                 }
                 if (!resultsToUse || resultsToUse.erro || resultsToUse.aviso || !resultsToUse.numeros || resultsToUse.numeros.length === 0) {
                     checkResultDisplayDiv.innerHTML = `<span class="misses">Resultados oficiais indisponíveis.</span>`; return;
                 }

                 const result = checkGame(lastGeneratedHunch.jogo, resultsToUse);
                 checkResultDisplayDiv.innerHTML = `<span class="${result.hits > 0 ? 'hits' : (result.almostNumbers.length > 0 ? 'almost-text' : 'misses')}">${result.message}</span>`;
                 renderGameNumbers(numbersDisplayDiv, lastGeneratedHunch.jogo, result.hitNumbers, result.almostNumbers);
                 lastGeneratedHunch.checkResult = checkResultDisplayDiv.innerHTML;
             });
         }
    }
    // === FIM DAS FUNÇÕES DE SALVAR E CONFERIR ===

    // --- EVENT LISTENERS (Seu código existente + Novos) ---
    if (splashProgressBarFill && splashProgressContainer) { /* ... (sua lógica splash) */ }
    criticalSplashTimeout = setTimeout(() => { if (splashHiddenTimestamp === 0) { showAppContentNow(); } if (!firebaseApp) { showGlobalError("Falha crítica na inicialização dos serviços."); disableFirebaseFeatures(); } criticalSplashTimeout = null; }, SPLASH_MINIMUM_VISIBLE_TIME + 1500);  
    setTimeout(attemptFirebaseInit, 100); 

    if(loginModalBtn) loginModalBtn.addEventListener('click', () => openModal(loginModal));
    if(registerModalBtn) registerModalBtn.addEventListener('click', () => openModal(registerModal));
    if(closeLoginModalBtn) closeLoginModalBtn.addEventListener('click', () => closeModal(loginModal));
    if(closeRegisterModalBtn) closeRegisterModalBtn.addEventListener('click', () => closeModal(registerModal));
    window.addEventListener('click', (event) => { if (event.target === loginModal) closeModal(loginModal); if (event.target === registerModal) closeModal(registerModal); });
    
    if (navDashboardBtn) navDashboardBtn.addEventListener('click', () => setActiveSection('dashboard-section'));
    if (navMyGamesBtn) navMyGamesBtn.addEventListener('click', () => { setActiveSection('my-games-section'); if (currentUser && typeof loadUserGames === "function") loadUserGames(filterLotteryMyGamesSelect ? filterLotteryMyGamesSelect.value : "todos"); });
    if (navPoolsBtn) navPoolsBtn.addEventListener('click', () => setActiveSection('pools-section')); // Seção de bolões, se existir

    // Listener para o select de loteria principal (que atualiza as estatísticas e resultados)
    const mainLotterySelectForDisplay = quickHunchLotteryTypeSelect || lotteryTypeSelect; // Use o ID do seu select principal
    if (mainLotterySelectForDisplay) {
        mainLotterySelectForDisplay.addEventListener('change', (e) => {
            const selectedLottery = e.target.value;
            const selectedOptionText = e.target.options[e.target.selectedIndex].text;
            if (document.getElementById('results-lottery-name')) document.getElementById('results-lottery-name').textContent = selectedOptionText;
            
            fetchAndDisplayResults(selectedLottery); 
            fetchAndDisplayFrequencyStats(selectedLottery); 
            fetchAndDisplayPairFrequencyStats(selectedLottery); 
            fetchAndDisplayCityStats(selectedLottery);
            fetchAndDisplayCityPrizeSumStats(selectedLottery);
        });
    }
    if (fetchResultsBtn && mainLotterySelectForDisplay) { 
         fetchResultsBtn.addEventListener('click', () => {
             const selectedLottery = mainLotterySelectForDisplay.value;
             fetchAndDisplayResults(selectedLottery); fetchAndDisplayFrequencyStats(selectedLottery); 
             fetchAndDisplayPairFrequencyStats(selectedLottery); fetchAndDisplayCityStats(selectedLottery);
             fetchAndDisplayCityPrizeSumStats(selectedLottery);
         });
     }

    // Listener para o Gerador Rápido
    if (generateQuickHunchBtn) { 
        generateQuickHunchBtn.addEventListener('click', generateAndDisplayQuickHunch);
    }
    setupSaveHunchButton(saveQuickHunchBtn, 'quick');
    if (quickHunchLotteryTypeSelect) { // Passa o select correto
        setupCheckHunchButton(checkQuickHunchBtn, quickHunchNumbersDiv, quickHunchCheckResultDiv, quickHunchLotteryTypeSelect, 'quick');
    }


    // Listeners de Autenticação (COPIE OS SEUS COMPLETOS AQUI)
    if(loginSubmitBtn) loginSubmitBtn.addEventListener('click', () => { /* ... (sua lógica de login) ... */ });
    if(registerSubmitBtn) registerSubmitBtn.addEventListener('click', () => { /* ... (sua lógica de registro) ... */ });
    if(logoutBtn) logoutBtn.addEventListener('click', () => { /* ... (sua lógica de logout) ... */ });
    
    // Listener para filtro de jogos salvos (COPIE O SEU COMPLETO AQUI)
    if (filterLotteryMyGamesSelect) filterLotteryMyGamesSelect.addEventListener('change', (e) => { /* ... */ });
    
    // Listeners para Probabilidade Manual (COPIE OS SEUS COMPLETOS AQUI)
    if (manualProbUserNumbersInput && manualProbLotteryTypeSelect) { 
        manualProbUserNumbersInput.addEventListener('input', updateManualProbNumbersFeedback);
        manualProbLotteryTypeSelect.addEventListener('change', () => { /* ... */ });
        const initialSelectedOption = manualProbLotteryTypeSelect.options[manualProbLotteryTypeSelect.selectedIndex];
        if (initialSelectedOption && initialSelectedOption.dataset.count){ /* ... */ }
        updateManualProbNumbersFeedback(); 
    }
    if (manualCalculateProbBtn) { manualCalculateProbBtn.addEventListener('click', async () => { /* ... */ }); }

    // === NOVOS EVENT LISTENERS ===
    if (generateEsotericHunchBtn) {
        generateEsotericHunchBtn.addEventListener('click', generateAndDisplayEsotericHunch);
    }
    setupSaveHunchButton(saveEsotericHunchBtn, 'esoteric');
    if (esotericLotteryTypeSelect) { // Passa o select correto
         setupCheckHunchButton(checkEsotericHunchBtn, esotericHunchNumbersDiv, esotericHunchHistoryCheckDiv, esotericLotteryTypeSelect, 'esoteric');
    }
    
    if (promoRegisterBtn && registerModalBtn) {
        promoRegisterBtn.addEventListener('click', () => openModal(registerModal));
    }
    if (promoLoginBtn && loginModalBtn) {
        promoLoginBtn.addEventListener('click', () => openModal(loginModal));
    }
    // === FIM DOS NOVOS EVENT LISTENERS ===
    
    console.log("SCRIPT.JS: Final do script atingido, todos os listeners configurados.");
});
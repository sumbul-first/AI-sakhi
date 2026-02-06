/**
 * Audio and Video Player Components for AI Sakhi
 * Provides accessible media controls with pause, replay, skip functionality
 * Requirements: 1.4, 1.5, 3.4
 */

class MediaPlayer {
    constructor() {
        this.currentAudio = null;
        this.currentVideo = null;
        this.playbackHistory = [];
        this.isPlaying = false;
        this.currentTime = 0;
        this.duration = 0;
        this.playbackRate = 1.0;
        
        this.init();
    }
    
    /**
     * Initialize media player
     */
    init() {
        this.createPlayerStyles();
        this.setupEventListeners();
        console.log('Media Player initialized');
    }
    
    /**
     * Create audio player with controls
     */
    createAudioPlayer(audioUrl, options = {}) {
        const {
            title = 'Audio Content',
            transcript = '',
            autoplay = false,
            showTranscript = true,
            language = 'hi'
        } = options;
        
        const playerId = `audio-player-${Date.now()}`;
        
        const playerHTML = `
            <div class="media-player audio-player" id="${playerId}">
                <div class="player-header">
                    <h4 class="player-title">${title}</h4>
                    <div class="player-language">${this.getLanguageName(language)}</div>
                </div>
                
                <div class="audio-controls">
                    <button class="control-btn replay-btn" onclick="mediaPlayer.replayAudio('${playerId}')" 
                            aria-label="Replay audio" title="Replay">
                        ⏮️
                    </button>
                    
                    <button class="control-btn play-pause-btn" onclick="mediaPlayer.toggleAudioPlayback('${playerId}')" 
                            aria-label="Play/Pause audio" title="Play/Pause">
                        ▶️
                    </button>
                    
                    <button class="control-btn skip-btn" onclick="mediaPlayer.skipAudio('${playerId}')" 
                            aria-label="Skip audio" title="Skip">
                        ⏭️
                    </button>
                    
                    <div class="volume-control">
                        <button class="control-btn volume-btn" onclick="mediaPlayer.toggleMute('${playerId}')" 
                                aria-label="Mute/Unmute" title="Volume">
                            🔊
                        </button>
                        <input type="range" class="volume-slider" min="0" max="100" value="80" 
                               onchange="mediaPlayer.setVolume('${playerId}', this.value)"
                               aria-label="Volume control">
                    </div>
                </div>
                
                <div class="progress-container">
                    <div class="progress-bar" onclick="mediaPlayer.seekAudio(event, '${playerId}')">
                        <div class="progress-fill"></div>
                        <div class="progress-handle"></div>
                    </div>
                    <div class="time-display">
                        <span class="current-time">0:00</span>
                        <span class="duration">0:00</span>
                    </div>
                </div>
                
                <div class="playback-controls">
                    <label for="speed-${playerId}" class="speed-label">Speed:</label>
                    <select id="speed-${playerId}" class="speed-selector" 
                            onchange="mediaPlayer.setPlaybackRate('${playerId}', this.value)">
                        <option value="0.5">0.5x</option>
                        <option value="0.75">0.75x</option>
                        <option value="1.0" selected>1.0x</option>
                        <option value="1.25">1.25x</option>
                        <option value="1.5">1.5x</option>
                    </select>
                </div>
                
                ${showTranscript && transcript ? `
                    <div class="transcript-section">
                        <button class="transcript-toggle" onclick="mediaPlayer.toggleTranscript('${playerId}')"
                                aria-label="Show/Hide transcript">
                            📝 Show Transcript
                        </button>
                        <div class="transcript-content" style="display: none;">
                            <p>${transcript}</p>
                        </div>
                    </div>
                ` : ''}
                
                <audio preload="metadata" ${autoplay ? 'autoplay' : ''}>
                    <source src="${audioUrl}" type="audio/mpeg">
                    <source src="${audioUrl}" type="audio/wav">
                    <source src="${audioUrl}" type="audio/ogg">
                    Your browser does not support the audio element.
                </audio>
            </div>
        `;
        
        return { playerId, playerHTML };
    }
    
    /**
     * Create video player with controls
     */
    createVideoPlayer(videoUrl, options = {}) {
        const {
            title = 'Video Content',
            poster = '',
            subtitles = '',
            autoplay = false,
            language = 'hi',
            width = '100%',
            height = 'auto'
        } = options;
        
        const playerId = `video-player-${Date.now()}`;
        
        const playerHTML = `
            <div class="media-player video-player" id="${playerId}">
                <div class="player-header">
                    <h4 class="player-title">${title}</h4>
                    <div class="player-language">${this.getLanguageName(language)}</div>
                </div>
                
                <div class="video-container">
                    <video controls preload="metadata" ${autoplay ? 'autoplay' : ''} 
                           ${poster ? `poster="${poster}"` : ''}
                           style="width: ${width}; height: ${height};">
                        <source src="${videoUrl}" type="video/mp4">
                        <source src="${videoUrl}" type="video/webm">
                        <source src="${videoUrl}" type="video/ogg">
                        ${subtitles ? `<track kind="subtitles" src="${subtitles}" srclang="${language}" label="${this.getLanguageName(language)}" default>` : ''}
                        Your browser does not support the video element.
                    </video>
                </div>
                
                <div class="video-controls">
                    <button class="control-btn replay-btn" onclick="mediaPlayer.replayVideo('${playerId}')" 
                            aria-label="Replay video" title="Replay">
                        ⏮️
                    </button>
                    
                    <button class="control-btn play-pause-btn" onclick="mediaPlayer.toggleVideoPlayback('${playerId}')" 
                            aria-label="Play/Pause video" title="Play/Pause">
                        ▶️
                    </button>
                    
                    <button class="control-btn skip-btn" onclick="mediaPlayer.skipVideo('${playerId}')" 
                            aria-label="Skip video" title="Skip">
                        ⏭️
                    </button>
                    
                    <button class="control-btn fullscreen-btn" onclick="mediaPlayer.toggleFullscreen('${playerId}')" 
                            aria-label="Toggle fullscreen" title="Fullscreen">
                        ⛶
                    </button>
                </div>
                
                <div class="playback-controls">
                    <label for="video-speed-${playerId}" class="speed-label">Speed:</label>
                    <select id="video-speed-${playerId}" class="speed-selector" 
                            onchange="mediaPlayer.setVideoPlaybackRate('${playerId}', this.value)">
                        <option value="0.5">0.5x</option>
                        <option value="0.75">0.75x</option>
                        <option value="1.0" selected>1.0x</option>
                        <option value="1.25">1.25x</option>
                        <option value="1.5">1.5x</option>
                    </select>
                </div>
            </div>
        `;
        
        return { playerId, playerHTML };
    }
    
    /**
     * Toggle audio playback
     */
    toggleAudioPlayback(playerId) {
        const player = document.getElementById(playerId);
        const audio = player.querySelector('audio');
        const playBtn = player.querySelector('.play-pause-btn');
        
        if (audio.paused) {
            // Pause any other playing audio
            this.pauseAllMedia();
            
            audio.play().then(() => {
                playBtn.innerHTML = '⏸️';
                playBtn.setAttribute('aria-label', 'Pause audio');
                this.currentAudio = audio;
                this.isPlaying = true;
                this.updateProgress(playerId, audio);
            }).catch(error => {
                console.error('Audio playback failed:', error);
                this.showError('Audio playback failed. Please try again.');
            });
        } else {
            audio.pause();
            playBtn.innerHTML = '▶️';
            playBtn.setAttribute('aria-label', 'Play audio');
            this.isPlaying = false;
        }
    }
    
    /**
     * Toggle video playback
     */
    toggleVideoPlayback(playerId) {
        const player = document.getElementById(playerId);
        const video = player.querySelector('video');
        const playBtn = player.querySelector('.play-pause-btn');
        
        if (video.paused) {
            // Pause any other playing media
            this.pauseAllMedia();
            
            video.play().then(() => {
                playBtn.innerHTML = '⏸️';
                playBtn.setAttribute('aria-label', 'Pause video');
                this.currentVideo = video;
                this.isPlaying = true;
            }).catch(error => {
                console.error('Video playback failed:', error);
                this.showError('Video playback failed. Please try again.');
            });
        } else {
            video.pause();
            playBtn.innerHTML = '▶️';
            playBtn.setAttribute('aria-label', 'Play video');
            this.isPlaying = false;
        }
    }
    
    /**
     * Replay audio from beginning
     */
    replayAudio(playerId) {
        const player = document.getElementById(playerId);
        const audio = player.querySelector('audio');
        
        audio.currentTime = 0;
        if (!audio.paused) {
            audio.play();
        }
        
        this.addToHistory(playerId, 'replay', 'audio');
    }
    
    /**
     * Replay video from beginning
     */
    replayVideo(playerId) {
        const player = document.getElementById(playerId);
        const video = player.querySelector('video');
        
        video.currentTime = 0;
        if (!video.paused) {
            video.play();
        }
        
        this.addToHistory(playerId, 'replay', 'video');
    }
    
    /**
     * Skip audio (jump forward 10 seconds)
     */
    skipAudio(playerId) {
        const player = document.getElementById(playerId);
        const audio = player.querySelector('audio');
        
        audio.currentTime = Math.min(audio.currentTime + 10, audio.duration);
        this.addToHistory(playerId, 'skip', 'audio');
    }
    
    /**
     * Skip video (jump forward 10 seconds)
     */
    skipVideo(playerId) {
        const player = document.getElementById(playerId);
        const video = player.querySelector('video');
        
        video.currentTime = Math.min(video.currentTime + 10, video.duration);
        this.addToHistory(playerId, 'skip', 'video');
    }
    
    /**
     * Seek audio to specific position
     */
    seekAudio(event, playerId) {
        const player = document.getElementById(playerId);
        const audio = player.querySelector('audio');
        const progressBar = player.querySelector('.progress-bar');
        
        const rect = progressBar.getBoundingClientRect();
        const clickX = event.clientX - rect.left;
        const percentage = clickX / rect.width;
        
        audio.currentTime = percentage * audio.duration;
    }
    
    /**
     * Set volume
     */
    setVolume(playerId, volume) {
        const player = document.getElementById(playerId);
        const media = player.querySelector('audio, video');
        
        media.volume = volume / 100;
        
        const volumeBtn = player.querySelector('.volume-btn');
        if (volume == 0) {
            volumeBtn.innerHTML = '🔇';
        } else if (volume < 50) {
            volumeBtn.innerHTML = '🔉';
        } else {
            volumeBtn.innerHTML = '🔊';
        }
    }
    
    /**
     * Toggle mute
     */
    toggleMute(playerId) {
        const player = document.getElementById(playerId);
        const media = player.querySelector('audio, video');
        const volumeSlider = player.querySelector('.volume-slider');
        
        if (media.muted) {
            media.muted = false;
            volumeSlider.value = media.volume * 100;
            this.setVolume(playerId, volumeSlider.value);
        } else {
            media.muted = true;
            player.querySelector('.volume-btn').innerHTML = '🔇';
        }
    }
    
    /**
     * Set playback rate for audio
     */
    setPlaybackRate(playerId, rate) {
        const player = document.getElementById(playerId);
        const audio = player.querySelector('audio');
        
        audio.playbackRate = parseFloat(rate);
        this.playbackRate = parseFloat(rate);
    }
    
    /**
     * Set playback rate for video
     */
    setVideoPlaybackRate(playerId, rate) {
        const player = document.getElementById(playerId);
        const video = player.querySelector('video');
        
        video.playbackRate = parseFloat(rate);
    }
    
    /**
     * Toggle fullscreen for video
     */
    toggleFullscreen(playerId) {
        const player = document.getElementById(playerId);
        const video = player.querySelector('video');
        
        if (document.fullscreenElement) {
            document.exitFullscreen();
        } else {
            video.requestFullscreen().catch(error => {
                console.error('Fullscreen failed:', error);
            });
        }
    }
    
    /**
     * Toggle transcript visibility
     */
    toggleTranscript(playerId) {
        const player = document.getElementById(playerId);
        const transcriptContent = player.querySelector('.transcript-content');
        const transcriptToggle = player.querySelector('.transcript-toggle');
        
        if (transcriptContent.style.display === 'none') {
            transcriptContent.style.display = 'block';
            transcriptToggle.innerHTML = '📝 Hide Transcript';
        } else {
            transcriptContent.style.display = 'none';
            transcriptToggle.innerHTML = '📝 Show Transcript';
        }
    }
    
    /**
     * Update progress bar for audio
     */
    updateProgress(playerId, audio) {
        const player = document.getElementById(playerId);
        const progressFill = player.querySelector('.progress-fill');
        const currentTimeSpan = player.querySelector('.current-time');
        const durationSpan = player.querySelector('.duration');
        
        const updateInterval = setInterval(() => {
            if (audio.paused || audio.ended) {
                clearInterval(updateInterval);
                return;
            }
            
            const progress = (audio.currentTime / audio.duration) * 100;
            progressFill.style.width = `${progress}%`;
            
            currentTimeSpan.textContent = this.formatTime(audio.currentTime);
            durationSpan.textContent = this.formatTime(audio.duration);
        }, 100);
        
        // Handle audio end
        audio.addEventListener('ended', () => {
            clearInterval(updateInterval);
            const playBtn = player.querySelector('.play-pause-btn');
            playBtn.innerHTML = '▶️';
            playBtn.setAttribute('aria-label', 'Play audio');
            progressFill.style.width = '0%';
            this.isPlaying = false;
        });
    }
    
    /**
     * Pause all currently playing media
     */
    pauseAllMedia() {
        // Pause all audio elements
        document.querySelectorAll('audio').forEach(audio => {
            if (!audio.paused) {
                audio.pause();
                const player = audio.closest('.media-player');
                if (player) {
                    const playBtn = player.querySelector('.play-pause-btn');
                    playBtn.innerHTML = '▶️';
                    playBtn.setAttribute('aria-label', 'Play audio');
                }
            }
        });
        
        // Pause all video elements
        document.querySelectorAll('video').forEach(video => {
            if (!video.paused) {
                video.pause();
                const player = video.closest('.media-player');
                if (player) {
                    const playBtn = player.querySelector('.play-pause-btn');
                    playBtn.innerHTML = '▶️';
                    playBtn.setAttribute('aria-label', 'Play video');
                }
            }
        });
        
        this.isPlaying = false;
    }
    
    /**
     * Format time in MM:SS format
     */
    formatTime(seconds) {
        if (isNaN(seconds)) return '0:00';
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }
    
    /**
     * Get language name from code
     */
    getLanguageName(code) {
        const languages = {
            'hi': 'हिंदी',
            'en': 'English',
            'bn': 'বাংলা',
            'ta': 'தமிழ்',
            'te': 'తెలుగు',
            'mr': 'मराठी'
        };
        return languages[code] || 'Unknown';
    }
    
    /**
     * Add interaction to history
     */
    addToHistory(playerId, action, mediaType) {
        this.playbackHistory.push({
            playerId,
            action,
            mediaType,
            timestamp: Date.now()
        });
        
        // Keep only last 50 interactions
        if (this.playbackHistory.length > 50) {
            this.playbackHistory = this.playbackHistory.slice(-50);
        }
    }
    
    /**
     * Setup global event listeners
     */
    setupEventListeners() {
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return; // Don't interfere with form inputs
            }
            
            switch (e.key) {
                case ' ':
                    e.preventDefault();
                    if (this.currentAudio || this.currentVideo) {
                        const activePlayer = document.querySelector('.media-player audio:not([paused]), .media-player video:not([paused])');
                        if (activePlayer) {
                            const playerId = activePlayer.closest('.media-player').id;
                            if (activePlayer.tagName === 'AUDIO') {
                                this.toggleAudioPlayback(playerId);
                            } else {
                                this.toggleVideoPlayback(playerId);
                            }
                        }
                    }
                    break;
                    
                case 'ArrowLeft':
                    e.preventDefault();
                    if (this.currentAudio || this.currentVideo) {
                        const activeMedia = this.currentAudio || this.currentVideo;
                        activeMedia.currentTime = Math.max(activeMedia.currentTime - 10, 0);
                    }
                    break;
                    
                case 'ArrowRight':
                    e.preventDefault();
                    if (this.currentAudio || this.currentVideo) {
                        const activeMedia = this.currentAudio || this.currentVideo;
                        activeMedia.currentTime = Math.min(activeMedia.currentTime + 10, activeMedia.duration);
                    }
                    break;
            }
        });
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                // Optionally pause media when page is hidden
                // this.pauseAllMedia();
            }
        });
    }
    
    /**
     * Create CSS styles for media players
     */
    createPlayerStyles() {
        if (document.getElementById('media-player-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'media-player-styles';
        styles.textContent = `
            .media-player {
                background: rgba(255, 255, 255, 0.95);
                border: 2px solid #FF69B4;
                border-radius: 12px;
                padding: 20px;
                margin: 16px 0;
                box-shadow: 0 4px 12px rgba(255, 105, 180, 0.15);
                font-family: inherit;
            }
            
            .player-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid #f0f0f0;
            }
            
            .player-title {
                margin: 0;
                color: #333;
                font-size: 18px;
                font-weight: 600;
            }
            
            .player-language {
                background: rgba(255, 105, 180, 0.1);
                color: #FF69B4;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }
            
            .audio-controls, .video-controls {
                display: flex;
                align-items: center;
                gap: 12px;
                margin-bottom: 16px;
                flex-wrap: wrap;
            }
            
            .control-btn {
                background: rgba(255, 105, 180, 0.1);
                border: 2px solid #FF69B4;
                border-radius: 50%;
                width: 48px;
                height: 48px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 18px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .control-btn:hover {
                background: rgba(255, 105, 180, 0.2);
                transform: scale(1.05);
            }
            
            .control-btn:focus {
                outline: 3px solid #FF69B4;
                outline-offset: 2px;
            }
            
            .control-btn:active {
                transform: scale(0.95);
            }
            
            .volume-control {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-left: auto;
            }
            
            .volume-slider {
                width: 80px;
                height: 4px;
                background: #ddd;
                border-radius: 2px;
                outline: none;
                cursor: pointer;
            }
            
            .volume-slider::-webkit-slider-thumb {
                appearance: none;
                width: 16px;
                height: 16px;
                background: #FF69B4;
                border-radius: 50%;
                cursor: pointer;
            }
            
            .volume-slider::-moz-range-thumb {
                width: 16px;
                height: 16px;
                background: #FF69B4;
                border-radius: 50%;
                cursor: pointer;
                border: none;
            }
            
            .progress-container {
                margin-bottom: 12px;
            }
            
            .progress-bar {
                width: 100%;
                height: 6px;
                background: #e0e0e0;
                border-radius: 3px;
                cursor: pointer;
                position: relative;
                margin-bottom: 8px;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #FF69B4, #FF1493);
                border-radius: 3px;
                width: 0%;
                transition: width 0.1s ease;
            }
            
            .progress-handle {
                position: absolute;
                top: 50%;
                right: 0;
                transform: translateY(-50%);
                width: 12px;
                height: 12px;
                background: #FF69B4;
                border-radius: 50%;
                cursor: pointer;
            }
            
            .time-display {
                display: flex;
                justify-content: space-between;
                font-size: 12px;
                color: #666;
            }
            
            .playback-controls {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-bottom: 12px;
            }
            
            .speed-label {
                font-size: 14px;
                color: #333;
                font-weight: 600;
            }
            
            .speed-selector {
                padding: 4px 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                cursor: pointer;
            }
            
            .speed-selector:focus {
                outline: 2px solid #FF69B4;
                outline-offset: 1px;
            }
            
            .video-container {
                margin-bottom: 16px;
                border-radius: 8px;
                overflow: hidden;
            }
            
            .video-container video {
                width: 100%;
                height: auto;
                display: block;
            }
            
            .transcript-section {
                margin-top: 16px;
                padding-top: 16px;
                border-top: 1px solid #f0f0f0;
            }
            
            .transcript-toggle {
                background: rgba(255, 105, 180, 0.1);
                border: 1px solid #FF69B4;
                border-radius: 6px;
                padding: 8px 12px;
                cursor: pointer;
                font-size: 14px;
                color: #FF69B4;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .transcript-toggle:hover {
                background: rgba(255, 105, 180, 0.2);
            }
            
            .transcript-toggle:focus {
                outline: 2px solid #FF69B4;
                outline-offset: 2px;
            }
            
            .transcript-content {
                margin-top: 12px;
                padding: 16px;
                background: rgba(255, 105, 180, 0.05);
                border-radius: 8px;
                line-height: 1.6;
                color: #333;
            }
            
            .transcript-content p {
                margin: 0;
            }
            
            @media (max-width: 768px) {
                .media-player {
                    padding: 16px;
                }
                
                .player-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 8px;
                }
                
                .audio-controls, .video-controls {
                    justify-content: center;
                }
                
                .control-btn {
                    width: 44px;
                    height: 44px;
                    font-size: 16px;
                }
                
                .volume-control {
                    margin-left: 0;
                    margin-top: 8px;
                }
                
                .volume-slider {
                    width: 60px;
                }
            }
            
            @media (max-width: 480px) {
                .audio-controls, .video-controls {
                    gap: 8px;
                }
                
                .control-btn {
                    width: 40px;
                    height: 40px;
                    font-size: 14px;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }
    
    /**
     * Show error message
     */
    showError(message) {
        console.error(message);
        
        if (window.showMessage) {
            window.showMessage(message, 'error');
        } else {
            // Create temporary error display
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #ff4444;
                color: white;
                padding: 12px 16px;
                border-radius: 6px;
                z-index: 10000;
                font-size: 14px;
                max-width: 300px;
            `;
            errorDiv.textContent = message;
            document.body.appendChild(errorDiv);
            
            setTimeout(() => {
                document.body.removeChild(errorDiv);
            }, 5000);
        }
    }
    
    /**
     * Get playback statistics
     */
    getPlaybackStats() {
        return {
            totalInteractions: this.playbackHistory.length,
            replayCount: this.playbackHistory.filter(h => h.action === 'replay').length,
            skipCount: this.playbackHistory.filter(h => h.action === 'skip').length,
            audioInteractions: this.playbackHistory.filter(h => h.mediaType === 'audio').length,
            videoInteractions: this.playbackHistory.filter(h => h.mediaType === 'video').length,
            currentPlaybackRate: this.playbackRate,
            isCurrentlyPlaying: this.isPlaying
        };
    }
}

// Initialize media player when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.mediaPlayer = new MediaPlayer();
});

// Export for global access
window.MediaPlayer = MediaPlayer;
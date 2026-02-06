#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo for AI Sakhi Media Player Components
Tests audio and video player functionality with Flask integration
"""

from flask import Flask, render_template_string, jsonify, request
import os

app = Flask(__name__)

# Demo HTML template
DEMO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Sakhi - Media Player Demo</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/media-player.css') }}">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600;700&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Noto Sans', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h1 { color: #FF69B4; text-align: center; margin-bottom: 30px; }
        h2 { color: #333; border-bottom: 2px solid #FF69B4; padding-bottom: 8px; }
        .demo-section { margin: 30px 0; }
        .test-btn { background: #FF69B4; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; margin: 10px 5px; }
        .test-btn:hover { background: #FF1493; }
        .stats { background: #f9f9f9; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 AI Sakhi Media Player Demo 🎬</h1>
        
        <div class="demo-section">
            <h2>Audio Player Examples</h2>
            <button class="test-btn" onclick="loadAudioExample()">Load Audio Player</button>
            <button class="test-btn" onclick="loadAudioWithTranscript()">Load Audio with Transcript</button>
            <div id="audio-demo"></div>
        </div>
        
        <div class="demo-section">
            <h2>Video Player Examples</h2>
            <button class="test-btn" onclick="loadVideoExample()">Load Video Player</button>
            <div id="video-demo"></div>
        </div>
        
        <div class="demo-section">
            <h2>Multi-Language Examples</h2>
            <button class="test-btn" onclick="loadHindiContent()">Hindi Content</button>
            <button class="test-btn" onclick="loadEnglishContent()">English Content</button>
            <button class="test-btn" onclick="loadBengaliContent()">Bengali Content</button>
            <div id="multilang-demo"></div>
        </div>
        
        <div class="demo-section">
            <h2>Playback Statistics</h2>
            <button class="test-btn" onclick="showStats()">Show Stats</button>
            <div id="stats-display" class="stats" style="display: none;"></div>
        </div>
    </div>

    <script src="{{ url_for('static', filename='js/media-player.js') }}"></script>
    <script>
        function loadAudioExample() {
            const audioPlayer = window.mediaPlayer.createAudioPlayer(
                'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                {
                    title: 'Puberty Education - Body Changes',
                    language: 'hi',
                    autoplay: false,
                    showTranscript: false
                }
            );
            
            document.getElementById('audio-demo').innerHTML = audioPlayer.playerHTML;
        }
        
        function loadAudioWithTranscript() {
            const audioPlayer = window.mediaPlayer.createAudioPlayer(
                'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                {
                    title: 'Menstrual Health Guide',
                    language: 'hi',
                    transcript: 'यह ऑडियो मासिक धर्म स्वास्थ्य के बारे में महत्वपूर्ण जानकारी प्रदान करता है। इसमें स्वच्छता, उत्पादों की तुलना, और सामान्य मिथकों के बारे में बताया गया है।',
                    showTranscript: true
                }
            );
            
            document.getElementById('audio-demo').innerHTML = audioPlayer.playerHTML;
        }
        
        function loadVideoExample() {
            const videoPlayer = window.mediaPlayer.createVideoPlayer(
                'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                {
                    title: 'Safety Awareness Video',
                    language: 'en',
                    poster: 'https://via.placeholder.com/640x360/FF69B4/FFFFFF?text=Safety+Video',
                    autoplay: false
                }
            );
            
            document.getElementById('video-demo').innerHTML = videoPlayer.playerHTML;
        }
        
        function loadHindiContent() {
            const audioPlayer = window.mediaPlayer.createAudioPlayer(
                'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                {
                    title: 'गर्भावस्था मार्गदर्शन',
                    language: 'hi',
                    transcript: 'गर्भावस्था के दौरान पोषण और सुरक्षा के बारे में महत्वपूर्ण जानकारी।',
                    showTranscript: true
                }
            );
            
            document.getElementById('multilang-demo').innerHTML = audioPlayer.playerHTML;
        }
        
        function loadEnglishContent() {
            const audioPlayer = window.mediaPlayer.createAudioPlayer(
                'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                {
                    title: 'Government Health Schemes',
                    language: 'en',
                    transcript: 'Information about government health schemes and programs available for women and children.',
                    showTranscript: true
                }
            );
            
            document.getElementById('multilang-demo').innerHTML = audioPlayer.playerHTML;
        }
        
        function loadBengaliContent() {
            const audioPlayer = window.mediaPlayer.createAudioPlayer(
                'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                {
                    title: 'নিরাপত্তা সচেতনতা',
                    language: 'bn',
                    transcript: 'মহিলা ও মেয়েদের নিরাপত্তা সম্পর্কে গুরুত্বপূর্ণ তথ্য এবং সহায়তা।',
                    showTranscript: true
                }
            );
            
            document.getElementById('multilang-demo').innerHTML = audioPlayer.playerHTML;
        }
        
        function showStats() {
            const stats = window.mediaPlayer.getPlaybackStats();
            const statsHtml = `
                <h3>Playback Statistics</h3>
                <p><strong>Total Interactions:</strong> ${stats.totalInteractions}</p>
                <p><strong>Replay Count:</strong> ${stats.replayCount}</p>
                <p><strong>Skip Count:</strong> ${stats.skipCount}</p>
                <p><strong>Audio Interactions:</strong> ${stats.audioInteractions}</p>
                <p><strong>Video Interactions:</strong> ${stats.videoInteractions}</p>
                <p><strong>Current Playback Rate:</strong> ${stats.currentPlaybackRate}x</p>
                <p><strong>Currently Playing:</strong> ${stats.isCurrentlyPlaying ? 'Yes' : 'No'}</p>
            `;
            
            const statsDiv = document.getElementById('stats-display');
            statsDiv.innerHTML = statsHtml;
            statsDiv.style.display = 'block';
        }
        
        // Test keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'h' && e.ctrlKey) {
                alert('Keyboard Shortcuts:\\n\\nSpace: Play/Pause\\nLeft Arrow: Rewind 10s\\nRight Arrow: Forward 10s');
                e.preventDefault();
            }
        });
        
        console.log('Media Player Demo loaded successfully!');
        console.log('Press Ctrl+H for keyboard shortcuts help');
    </script>
</body>
</html>
'''

@app.route('/')
def demo():
    """Main demo page"""
    return render_template_string(DEMO_TEMPLATE)

@app.route('/api/media/test')
def test_media_api():
    """Test API endpoint for media functionality"""
    return jsonify({
        'status': 'success',
        'message': 'Media player API is working',
        'supported_formats': {
            'audio': ['mp3', 'wav', 'ogg'],
            'video': ['mp4', 'webm', 'ogg']
        },
        'features': [
            'Play/Pause controls',
            'Replay functionality',
            'Skip controls',
            'Volume control',
            'Playback speed adjustment',
            'Progress seeking',
            'Transcript display',
            'Multi-language support',
            'Keyboard shortcuts',
            'Accessibility features'
        ]
    })

@app.route('/api/media/content/<content_type>')
def get_media_content(content_type):
    """Get sample media content URLs"""
    content = {
        'audio': {
            'puberty': {
                'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                'title': 'Puberty Education',
                'transcript': 'Educational content about puberty and body changes.',
                'language': 'en'
            },
            'safety': {
                'url': 'https://www.soundjay.com/misc/sounds/bell-ringing-05.wav',
                'title': 'Safety Awareness',
                'transcript': 'Important safety information for women and girls.',
                'language': 'en'
            }
        },
        'video': {
            'health': {
                'url': 'https://sample-videos.com/zip/10/mp4/SampleVideo_1280x720_1mb.mp4',
                'title': 'Health Education Video',
                'poster': 'https://via.placeholder.com/640x360/FF69B4/FFFFFF?text=Health+Video',
                'language': 'en'
            }
        }
    }
    
    return jsonify(content.get(content_type, {}))

if __name__ == '__main__':
    print("🎵 Starting AI Sakhi Media Player Demo...")
    print("📱 Open http://localhost:5000 to test the media players")
    print("🎬 Features: Audio/Video players with accessibility controls")
    
    app.run(debug=True, host='0.0.0.0', port=5000)